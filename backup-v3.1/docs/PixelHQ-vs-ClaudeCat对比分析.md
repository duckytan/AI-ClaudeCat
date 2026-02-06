# PixelHQ-bridge vs AI-ClaudeCat 状态获取方法对比分析

**分析时间**: 2026-02-06  
**对比版本**: PixelHQ-bridge (v1.x) vs AI-ClaudeCat (v3.1)

---

## 目录
1. [核心差异总览](#核心差异总览)
2. [PixelHQ-bridge 状态获取方法](#pixelhq-bridge-状态获取方法)
3. [AI-ClaudeCat 状态获取方法](#ai-claudecat-状态获取方法)
4. [对比分析](#对比分析)
5. [优劣势对比](#优劣势对比)
6. [改进建议](#改进建议)

---

## 核心差异总览

| 维度 | PixelHQ-bridge | AI-ClaudeCat |
|------|----------------|--------------|
| **检测方式** | 文件监控（JSONL 日志） | 多方式融合（进程+窗口+文件） |
| **数据源** | Claude Code 会话日志 | 系统 API（进程、窗口、CPU） |
| **粒度** | 工具级（Read/Write/Bash/Task） | 状态级（idle/running/thinking/working） |
| **实时性** | 准实时（依赖文件写入） | 高实时（2秒轮询） |
| **语言** | TypeScript/Node.js | Python |
| **架构** | 事件驱动 + 管道模式 | 插件化 + 中间件模式 |
| **隐私处理** | 严格过滤（只保留元数据） | 无隐私处理（本地监控） |
| **输出协议** | WebSocket（iOS App） | WebSocket + HTTP + 标准输出 |

---

## PixelHQ-bridge 状态获取方法

### 1. 核心原理：**日志文件监控**

PixelHQ-bridge 通过监控 Claude Code 生成的 **JSONL 会话日志** 来获取状态。

#### 1.1 监控目标
```
~/.claude/projects/<project>/<session-id>.jsonl
~/.claude/projects/<project>/<session-id>/subagents/<agent-id>.jsonl
```

每个 Claude Code 会话都会生成一个 JSONL 文件，实时追加每一步操作。

#### 1.2 技术实现

**文件监控器 (Watcher)**  
`src/watcher.ts` - SessionWatcher 类

```typescript
// 使用 chokidar 监控 JSONL 文件变化
watch([
  join(config.projectsDir, '*', '*.jsonl'),           // 主会话
  join(config.projectsDir, '*', '*', 'subagents', '*.jsonl'), // 子 Agent
], {
  persistent: true,
  awaitWriteFinish: {
    stabilityThreshold: 100,  // 文件稳定 100ms 后触发
  },
});

// 增量读取新行
async readNewLines(filePath, startPosition) {
  const stream = createReadStream(filePath, { 
    start: startPosition,  // 从上次读取的位置继续
  });
  // 逐行解析 JSONL
}
```

**关键点**:
- **增量读取**: 记录每个文件的读取位置 (`filePositions: Map<string, number>`)
- **文件稳定性**: 等待 100ms 确保文件写入完成（`awaitWriteFinish`）
- **会话追踪**: 只追踪最近 10 分钟内的会话（`recencyThreshold = 10 * 60 * 1000`）

---

### 2. JSONL 日志解析

**解析器 (Parser)**  
`src/parser.ts` + `src/adapters/claude-code.ts`

#### 2.1 JSONL 事件类型

Claude Code 生成的日志包含以下事件类型：

```typescript
type RawJsonlEvent = {
  type: 'assistant' | 'user' | 'summary' | 'system' | 'progress';
  timestamp?: string;
  message?: {
    content: Array<ContentBlock>;  // 消息内容块
    usage?: { input_tokens, output_tokens, ... };  // Token 使用量
  };
  userType?: 'tool_result';  // 用户消息子类型
};

type ContentBlock =
  | { type: 'thinking', thinking: string }       // AI 思考
  | { type: 'text', text: string }               // 文本回复
  | { type: 'tool_use', id, name, input }        // 工具调用
  | { type: 'tool_result', tool_use_id, content, is_error };  // 工具结果
```

#### 2.2 状态推断逻辑

**核心算法**: 根据消息块类型推断状态

```typescript
// src/adapters/claude-code.ts - handleAssistant()
for (const block of message.content) {
  switch (block.type) {
    case 'thinking':
      // AI 正在思考
      events.push(createActivityEvent(sessionId, agentId, timestamp, 'thinking'));
      break;

    case 'text':
      if (block.text === '(no content)') {
        // 空内容 = 思考中
        events.push(createActivityEvent(sessionId, agentId, timestamp, 'thinking'));
      } else {
        // 有内容 = 正在回复
        events.push(createActivityEvent(sessionId, agentId, timestamp, 'responding', tokens));
      }
      break;

    case 'tool_use':
      // 工具调用 = 正在执行操作
      events.push(buildToolStartedEvent(sessionId, agentId, timestamp, block));
      
      if (block.name === 'Task') {
        // 特殊工具：Task = 派生子 Agent
        events.push(createAgentEvent(sessionId, block.id, timestamp, 'spawned', ...));
      }
      if (block.name === 'AskUserQuestion') {
        // 特殊工具：问用户 = 等待中
        events.push(createActivityEvent(sessionId, agentId, timestamp, 'waiting'));
      }
      break;
  }
}

// 工具结果处理
if (raw.userType === 'tool_result') {
  const isError = block.is_error || block.content.includes('Error');
  events.push(createToolEvent(sessionId, agentId, timestamp, {
    status: isError ? 'error' : 'completed',
  }));
}
```

#### 2.3 工具分类映射

PixelHQ 将 Claude Code 的工具映射到业务类别：

```typescript
// src/config.ts - TOOL_TO_CATEGORY
{
  Read:            { category: 'file_read',    detail: 'read' },
  Write:           { category: 'file_write',   detail: 'write' },
  Edit:            { category: 'file_write',   detail: 'edit' },
  Bash:            { category: 'terminal',     detail: 'bash' },
  Grep:            { category: 'search',       detail: 'grep' },
  Glob:            { category: 'search',       detail: 'glob' },
  WebFetch:        { category: 'search',       detail: 'web_fetch' },
  WebSearch:       { category: 'search',       detail: 'web_search' },
  Task:            { category: 'spawn_agent',  detail: 'task' },
  TodoWrite:       { category: 'plan',         detail: 'todo' },
  AskUserQuestion: { category: 'communicate',  detail: 'ask_user' },
  NotebookEdit:    { category: 'notebook',     detail: 'notebook' },
}
```

---

### 3. 隐私过滤管道

**严格的隐私保护**（这是 PixelHQ 的核心特性）

#### 3.1 过滤规则

**允许输出的数据**（白名单）：
- 事件类型（`tool`, `activity`, `agent`, `session`）
- 工具类别（`file_read`, `terminal`, `search`）
- 状态（`started`, `completed`, `error`）
- 文件名（**仅 basename**，`/Users/you/project/src/auth.ts` → `auth.ts`）
- 模式（Grep/Glob 的搜索模式）
- Bash 描述（仅 `description` 字段，**不是命令本身**）
- Token 计数（数字）
- 时间戳、UUID

**完全过滤的数据**（黑名单）：
- ❌ 文件内容（Read 工具的 result）
- ❌ 代码内容（Write/Edit 的 old_str/new_str）
- ❌ Bash 命令（只保留用户提供的 description）
- ❌ AI 的思考文本（thinking 块）
- ❌ AI 的回复文本（text 块）
- ❌ 用户的 prompt
- ❌ 工具输出结果
- ❌ 完整路径（只保留 basename）
- ❌ URL（WebFetch）
- ❌ 搜索查询（WebSearch）
- ❌ 错误详细消息（只保留 severity）

#### 3.2 实现

```typescript
// src/adapters/claude-code.ts - extractSafeContext()
function extractSafeContext(toolName: string, input: Record<string, unknown>): string | null {
  switch (toolName) {
    case 'Read':
    case 'Write':
    case 'Edit':
      return toBasename(input.file_path);  // 只保留文件名

    case 'Bash':
      return input.description || null;  // 只保留描述，不要命令

    case 'Grep':
    case 'Glob':
      return input.pattern || null;  // 保留搜索模式

    case 'Task':
      return input.subagent_type || null;  // Agent 类型

    case 'TodoWrite':
      return `${input.todos.length} items`;  // 只保留数量

    default:
      return null;  // 未知工具，不输出任何上下文
  }
}

// 路径过滤工具
function toBasename(path: string): string {
  return path.split('/').pop();  // /a/b/c.txt → c.txt
}
```

---

### 4. 事件输出格式

PixelHQ 输出的事件格式：

#### 4.1 Activity 事件
```json
{
  "type": "activity",
  "sessionId": "abc-123",
  "agentId": "optional",
  "action": "thinking" | "responding" | "waiting" | "user_prompt",
  "timestamp": "2026-02-06T12:34:56.789Z",
  "tokens": {
    "input": 5000,
    "output": 200,
    "cacheRead": 1000,
    "cacheWrite": 500
  }
}
```

#### 4.2 Tool 事件
```json
{
  "type": "tool",
  "sessionId": "abc-123",
  "agentId": "optional",
  "tool": "file_read",
  "detail": "read",
  "status": "started" | "completed" | "error",
  "toolUseId": "toolu_xyz",
  "context": "auth.ts",  // 仅 basename
  "timestamp": "2026-02-06T12:34:56.789Z"
}
```

#### 4.3 Agent 事件
```json
{
  "type": "agent",
  "sessionId": "abc-123",
  "agentId": "toolu_xyz",
  "action": "spawned" | "completed" | "error",
  "agentRole": "explore" | "bash" | "general",
  "timestamp": "2026-02-06T12:34:56.789Z"
}
```

---

### 5. Session 管理

**会话追踪** (`src/session.ts`)

```typescript
class SessionManager {
  sessions: Map<string, SessionInfo>;
  
  // 自动清理过期会话
  _reapStaleSessions() {
    for (const [sessionId, info] of this.sessions) {
      const age = Date.now() - info.lastEventAt.getTime();
      if (age > 2 * 60 * 1000) {  // 2分钟无活动
        this.removeSession(sessionId);  // 发送 session.ended 事件
      }
    }
  }
  
  // Agent 关联追踪（FIFO 队列）
  correlateAgentFile(sessionId: string, fileAgentId: string) {
    // 当文件系统发现新的 subagent JSONL 时
    // 关联到最近的 Task 工具调用
    const toolUseId = session.pendingSpawnQueue.shift();
    session.agentIdMap.set(fileAgentId, toolUseId);
  }
}
```

**关键特性**:
- **自动过期**: 2 分钟无活动自动清理会话
- **Agent 关联**: 通过 FIFO 队列关联 Task 工具调用和 subagent 文件
- **状态持久化**: 会话信息保存在内存（重启会丢失）

---

## AI-ClaudeCat 状态获取方法

### 1. 核心原理：**多方式融合检测**

AI-ClaudeCat 通过 **进程监控 + 窗口监控 + 文件活动** 三种方式融合判断状态。

### 2. 检测方式详解

#### 2.1 方式 1：窗口标题检测（最高优先级）

**实现** (`src/apps/claude_code.py`)

```python
def _detect_by_window(self) -> Tuple[Status, float, Dict]:
    """通过窗口标题检测（进程 PID 关联）"""
    
    # 1. 获取 Claude Code 进程的 PID 列表
    claude_pids = set()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if any(kw in proc.name().lower() for kw in ['claude', 'anthropic', 'ollama']):
            claude_pids.add(proc.pid)
    
    # 2. 枚举所有窗口，找 PID 匹配的
    for win in get_all_windows():  # Windows API
        if win['pid'] in claude_pids:
            title_lower = win['title'].lower()
            
            # 3. 窗口标题模式匹配（优先级从高到低）
            for pattern, status, confidence in TITLE_PATTERNS:
                if re.search(pattern, title_lower):
                    return (status, confidence, {
                        'window_title': win['title'],
                        'window_pid': win['pid']
                    })
```

**标题匹配规则**:
```python
TITLE_PATTERNS = [
    # 错误状态 - 最高优先级
    (r"error|错误|failed|失败", Status.ERROR, 0.95),
    # 执行状态
    (r"executing|执行|run|运行|bash|cmd", Status.EXECUTING, 0.90),
    # 工作状态
    (r"writing|写入|write|edit|编辑|save|保存", Status.WORKING, 0.85),
    # 思考状态
    (r"thinking|思考|analyzing|分析|processing|处理", Status.THINKING, 0.80),
]
```

**关键点**:
- **进程关联**: 先找 Claude 进程的 PID，再找对应的窗口（避免误匹配）
- **模式匹配**: 支持中英文关键词
- **置信度**: 越精确的匹配，置信度越高

---

#### 2.2 方式 2：进程监控（基础检测）

**实现** (`src/plugins/process.py`)

```python
class ProcessPlugin(BasePlugin):
    """通用进程监控插件（CPU 百分比推断状态）"""
    
    async def detect(self) -> Optional[StateEvent]:
        proc = psutil.Process(self.pid)
        
        # 获取 CPU 使用率
        cpu_percent = proc.cpu_percent(interval=0.1)
        
        # 根据阈值判断状态
        if cpu_percent < 0.5:
            status = Status.IDLE
        elif cpu_percent < 3.0:
            status = Status.RUNNING
        elif cpu_percent < 15.0:
            status = Status.THINKING
        elif cpu_percent < 50.0:
            status = Status.WORKING
        else:
            status = Status.EXECUTING
        
        return StateEvent(
            status=status,
            confidence=self._calculate_confidence(cpu_percent),
            source_plugin=self.name,
            source_type=PluginType.PROCESS,
        )
```

**CPU 阈值**:
```python
THRESHOLDS = {
    "idle": 0.5,      # < 0.5%
    "running": 3.0,   # < 3%
    "thinking": 15.0, # < 15%
    "working": 50.0,  # < 50%
    "executing": 100, # >= 50%
}
```

**关键点**:
- **实时监控**: 0.1秒间隔采样 CPU
- **阈值判断**: 固定阈值（简单但有效）
- **通用性**: 适用于任何进程

---

#### 2.3 方式 3：文件活动检测（辅助判断）

**实现** (`src/apps/claude_code.py`)

```python
def _detect_by_file_activity(self) -> Tuple[Status, bool]:
    """通过文件活动检测状态"""
    time_since_activity = time.time() - self._last_activity_time
    is_active = time_since_activity < 3.0  # 3秒内有活动
    
    return Status.WORKING if is_active else Status.IDLE, is_active

def on_file_activity(self):
    """接收文件活动事件（由文件监控插件触发）"""
    self._last_activity_time = time.time()
```

**关键点**:
- **被动接收**: 由其他插件（如文件监控插件）触发
- **时间窗口**: 3 秒内有活动 = 正在工作
- **辅助判断**: 仅在无窗口标题时使用

---

### 3. 状态融合算法

**融合逻辑** (`src/apps/claude_code.py` - `detect()`)

```python
async def detect(self) -> Optional[StateEvent]:
    # 方式 1：窗口标题检测
    title_status, title_confidence, title_details = self._detect_by_window()
    
    # 方式 2：进程存在性检测
    process_status, process_confidence, process_count = self._detect_by_process()
    
    # 融合判断（优先级：窗口 > 进程 > 文件）
    if title_status != Status.UNKNOWN:
        # 窗口标题检测到状态 → 直接使用
        final_status = title_status
        final_confidence = title_confidence
        details = {'method': 'window', ...}
    
    elif process_status == Status.STOPPED:
        # 进程不存在 → 停止状态
        final_status = Status.STOPPED
        final_confidence = 1.0
        details = {'method': 'process', 'process_count': 0}
    
    else:
        # 进程存在但无窗口标题 → 使用文件活动
        file_status, file_active = self._detect_by_file_activity()
        
        if file_active:
            final_status = Status.WORKING
            final_confidence = 0.75
        else:
            final_status = Status.RUNNING
            final_confidence = 0.70
        
        details = {'method': 'process', 'file_active': file_active}
    
    # 只有状态变化才返回事件
    if final_status != self._last_status:
        self._last_status = final_status
        return StateEvent(...)
```

**融合策略**:
1. **窗口标题优先**: 最精确的状态信息（来自 UI）
2. **进程存在性**: 基础判断（存活/停止）
3. **文件活动**: 辅助判断（最近有操作 = 工作中）
4. **置信度递减**: 窗口 (0.95) > 进程 (0.70) > 文件 (0.75)

---

### 4. 插件化架构

**插件体系** (`src/plugins/base.py`)

```python
class BasePlugin(ABC):
    """插件基类"""
    
    @abstractmethod
    async def detect(self) -> Optional[StateEvent]:
        """检测状态（异步）"""
        pass
    
    def register_callback(self, callback: Callable[[StateEvent], None]):
        """注册回调（发布事件）"""
        self._callbacks.append(callback)
    
    def _emit(self, event: StateEvent):
        """触发所有回调"""
        for callback in self._callbacks:
            callback(event)
```

**插件类型**:
- `ProcessPlugin`: 通用进程监控（CPU）
- `WindowPlugin`: 通用窗口监控（标题）
- `ClaudeCodePlugin`: Claude Code 专用（多方式融合）
- 可扩展：`OpenCodePlugin`, `CursorPlugin`, ...

---

### 5. 中间件和输出

**中间件** (`src/middleware/core.py`)

```python
class Middleware:
    """插件管理 + 状态融合 + 输出分发"""
    
    async def run(self):
        # 1. 注册插件
        for plugin in self.plugins:
            plugin.register_callback(self._on_plugin_event)
        
        # 2. 启动插件
        for plugin in self.plugins:
            plugin.start()
            asyncio.create_task(self._poll_plugin(plugin))
        
        # 3. 轮询检测
        async def _poll_plugin(plugin):
            while self._running:
                event = await plugin.detect()
                if event:
                    await self._process_event(event)
                await asyncio.sleep(plugin.check_interval)
    
    async def _process_event(self, event: StateEvent):
        # 状态融合
        fused_event = self.fusion.fuse_events([event])
        
        # 输出到所有适配器
        for adapter in self.adapters:
            await adapter.send(fused_event)
```

**输出适配器**:
- `WebSocketAdapter`: ws://127.0.0.1:8765 (实时推送)
- `HTTPAdapter`: http://127.0.0.1:8080/api/status (REST API)
- `StdoutAdapter`: 标准输出（调试）

---

## 对比分析

### 1. 检测方式对比

| 维度 | PixelHQ-bridge | AI-ClaudeCat |
|------|----------------|--------------|
| **数据源** | 日志文件（JSONL） | 系统 API（进程、窗口） |
| **检测精度** | ⭐⭐⭐⭐⭐ 极高（工具级） | ⭐⭐⭐⭐ 高（状态级） |
| **实时性** | ⭐⭐⭐ 准实时（依赖写入） | ⭐⭐⭐⭐⭐ 高实时（2秒轮询） |
| **系统侵入性** | ⭐⭐⭐⭐⭐ 无侵入（只读文件） | ⭐⭐⭐ 中等（系统 API 调用） |
| **依赖性** | ⭐⭐⭐ 强依赖日志格式 | ⭐⭐⭐⭐ 弱依赖（通用 API） |
| **可扩展性** | ⭐⭐ 低（需适配器） | ⭐⭐⭐⭐⭐ 高（插件化） |

---

### 2. 信息粒度对比

#### PixelHQ-bridge 提供的信息

✅ **工具级细节**:
- 具体工具名称（Read, Write, Bash, Grep, ...）
- 工具参数（文件名、模式、描述）
- 工具状态（started, completed, error）
- Agent 派生（Task 工具）
- Token 使用量（input/output/cache）

✅ **事件时序**:
- 每个工具调用的开始和结束
- 思考、回复、等待的明确边界
- 会话的开始和结束

❌ **缺少的信息**:
- 无 CPU/内存使用率
- 无窗口状态
- 无文件内容（隐私保护）

#### AI-ClaudeCat 提供的信息

✅ **系统级状态**:
- 进程存活状态
- CPU 使用率
- 窗口标题
- 文件活动时间

✅ **融合状态**:
- idle / running / thinking / working / executing / error / stopped
- 置信度（0.0 - 1.0）
- 检测方法（window / process / file）

❌ **缺少的信息**:
- 无具体工具调用信息
- 无 Token 使用量
- 无事件时序

---

### 3. 架构对比

#### PixelHQ-bridge 架构（事件驱动 + 管道）

```
文件系统
    ↓
 Watcher（chokidar）
    ↓ emit('line')
 Parser（JSONL 解析）
    ↓
 Adapter（隐私过滤）
    ↓
SessionManager（会话追踪）
    ↓ emit('event')
WebSocketServer（广播）
    ↓
 iOS App
```

**特点**:
- ✅ 单向数据流（文件 → 输出）
- ✅ 严格的隐私管道（Adapter 白名单）
- ✅ 轻量级（事件驱动）
- ❌ 强依赖日志格式
- ❌ 扩展需要新 Adapter

#### AI-ClaudeCat 架构（插件化 + 中间件）

```
系统 API（psutil, Windows API）
    ↓
 Plugins（独立检测）
 ├── ProcessPlugin
 ├── WindowPlugin
 └── ClaudeCodePlugin
    ↓ callback(StateEvent)
Middleware（插件管理）
    ├── EventBus（事件分发）
    └── StateFusion（状态融合）
    ↓
OutputAdapters（多协议输出）
 ├── WebSocketAdapter
 ├── HTTPAdapter
 └── StdoutAdapter
    ↓
 前端 / CLI / 日志
```

**特点**:
- ✅ 插件化（易扩展）
- ✅ 多输出协议（WebSocket + HTTP）
- ✅ 状态融合算法
- ✅ 异步高性能
- ❌ 无隐私保护（本地监控）
- ❌ 粒度较粗（状态级）

---

## 优劣势对比

### PixelHQ-bridge 优势 ⭐

1. **精确的工具级信息**
   - 知道 AI 正在执行哪个具体操作（Read/Write/Bash/...）
   - 可以实现细粒度的 UI 动画（文件操作 → 走向文件柜）

2. **严格的隐私保护**
   - 生产级隐私过滤管道
   - 单元测试覆盖（`tests/pipeline.test.ts`）
   - 适合公开发布（npm 包）

3. **无系统侵入**
   - 只读文件监控，无需系统 API
   - 跨平台兼容性强（Node.js）

4. **事件时序完整**
   - 工具的 started → completed 配对
   - 可以计算每个操作的耗时

5. **Token 使用量**
   - 可以统计 API 成本
   - 展示 cache 命中率

### PixelHQ-bridge 劣势 ❌

1. **强依赖日志格式**
   - Claude Code 日志格式变化会破坏解析
   - 需要为每个 AI 工具编写 Adapter

2. **实时性受限**
   - 依赖文件系统写入（可能有延迟）
   - 100ms 稳定等待时间

3. **扩展性差**
   - 新增 AI 工具需要新 Adapter
   - 每个 Adapter 需要学习日志格式

4. **无系统状态**
   - 不知道 CPU/内存使用情况
   - 不知道进程是否崩溃

---

### AI-ClaudeCat 优势 ⭐

1. **高实时性**
   - 2 秒轮询，延迟 < 10ms
   - 无需等待文件写入

2. **系统级监控**
   - CPU/内存/窗口/进程全方位监控
   - 可以检测崩溃/卡死

3. **插件化架构**
   - 易扩展（新增插件）
   - 插件独立（解耦合）
   - 支持第三方插件

4. **多输出协议**
   - WebSocket（实时推送）
   - HTTP（REST API）
   - Stdout（调试）

5. **状态融合算法**
   - 多数据源综合判断
   - 置信度评估
   - 优先级投票

### AI-ClaudeCat 劣势 ❌

1. **粒度较粗**
   - 只知道状态（thinking/working），不知道具体工具
   - 无法实现细粒度 UI 动画

2. **无隐私保护**
   - 本地监控，未考虑隐私过滤
   - 不适合公开发布

3. **平台限制**
   - 窗口 API 依赖 Windows（`ctypes.windll`）
   - 跨平台需要适配

4. **无事件时序**
   - 只有状态快照，无操作历史
   - 无法计算操作耗时

5. **无 Token 统计**
   - 不知道 API 使用量

---

## 改进建议

### 对 PixelHQ-bridge 的建议

#### 1. 增加系统级监控（补充粗粒度状态）

**问题**: 当日志文件无更新时，无法判断进程是否崩溃。

**建议**: 增加进程心跳检测

```typescript
// src/health-checker.ts
class HealthChecker {
  async checkClaudeCodeHealth(): Promise<boolean> {
    // 检查进程是否存在
    const isRunning = await this.isProcessRunning('claude');
    
    // 检查文件是否长时间无更新
    const lastUpdate = this.getLastFileUpdate();
    const staleDuration = Date.now() - lastUpdate;
    
    if (isRunning && staleDuration > 5 * 60 * 1000) {
      // 进程存在但 5 分钟无更新 → 可能卡死
      return false;
    }
    
    return isRunning;
  }
}
```

#### 2. 支持多 AI 工具的通用检测

**问题**: 每个 AI 工具需要新 Adapter，成本高。

**建议**: 设计通用的日志格式适配层

```typescript
// src/adapters/universal.ts
interface UniversalLogFormat {
  timestamp: string;
  type: 'tool' | 'thought' | 'response';
  tool?: { name: string; args: Record<string, any>; };
  status?: 'started' | 'completed' | 'error';
}

class UniversalAdapter {
  // 各 AI 工具的日志 → 统一格式
  normalize(rawLog: any, sourceType: 'claude-code' | 'cursor' | 'codex'): UniversalLogFormat {
    switch (sourceType) {
      case 'claude-code': return this.fromClaudeCode(rawLog);
      case 'cursor': return this.fromCursor(rawLog);
      // ...
    }
  }
}
```

#### 3. 增加配置文件热加载

**问题**: 修改配置需要重启服务。

**建议**: 监控 `config.json` 变化

```typescript
// src/config.ts
watch('config.json', () => {
  this.reloadConfig();
  this.emit('config-changed', newConfig);
});
```

---

### 对 AI-ClaudeCat 的建议

#### 1. 增加日志监控插件（提升粒度）

**问题**: 只知道状态，不知道具体操作。

**建议**: 增加 `ClaudeLogPlugin` 读取 JSONL 日志

```python
# src/plugins/claude_log.py
class ClaudeLogPlugin(BasePlugin):
    """监控 Claude Code JSONL 日志"""
    
    async def detect(self) -> Optional[StateEvent]:
        # 增量读取 ~/.claude/projects/**/*.jsonl
        new_lines = self._read_new_lines()
        
        for line in new_lines:
            event = self._parse_jsonl(line)
            if event.get('type') == 'tool_use':
                tool_name = event['name']
                return StateEvent(
                    status=self._tool_to_status(tool_name),
                    confidence=0.95,
                    details={'tool': tool_name, 'method': 'log'},
                )
```

**好处**:
- ✅ 获得工具级信息（Read/Write/Bash）
- ✅ 结合窗口监控，提升置信度
- ✅ 保持插件化架构

#### 2. 增加隐私保护层

**问题**: 无隐私过滤，不适合公开发布。

**建议**: 增加 `PrivacyFilter` 模块

```python
# src/middleware/privacy.py
class PrivacyFilter:
    """隐私过滤器"""
    
    def filter_event(self, event: StateEvent) -> StateEvent:
        # 过滤文件路径 → 仅保留 basename
        if 'file_path' in event.details:
            event.details['file_path'] = os.path.basename(event.details['file_path'])
        
        # 过滤命令 → 仅保留描述
        if 'command' in event.details:
            del event.details['command']
        
        return event
```

#### 3. 增加跨平台支持

**问题**: 窗口 API 依赖 Windows。

**建议**: 使用跨平台库或条件编译

```python
# src/plugins/window.py
if sys.platform == 'win32':
    from .window_win32 import WindowPluginWin32 as WindowPlugin
elif sys.platform == 'darwin':
    from .window_macos import WindowPluginMacOS as WindowPlugin
elif sys.platform.startswith('linux'):
    from .window_x11 import WindowPluginX11 as WindowPlugin
```

#### 4. 增加事件历史存储

**问题**: 无历史记录，只有当前状态。

**建议**: 增加 `HistoryAdapter`

```python
# src/adapters/history_adapter.py
class HistoryAdapter(OutputAdapter):
    """历史记录适配器"""
    
    async def send(self, event: StateEvent):
        # 保存到 SQLite
        self.db.execute('''
            INSERT INTO events (timestamp, status, confidence, details)
            VALUES (?, ?, ?, ?)
        ''', (event.timestamp, event.status, event.confidence, json.dumps(event.details)))
        
        # 提供查询 API
        # GET /api/history?start=...&end=...
```

#### 5. 增加 Token 统计插件

**问题**: 无 API 使用量统计。

**建议**: 从日志中提取 Token 信息

```python
# src/plugins/token_tracker.py
class TokenTrackerPlugin(BasePlugin):
    """Token 使用量统计"""
    
    async def detect(self) -> Optional[StateEvent]:
        # 从 JSONL 日志中提取 usage 字段
        usage = self._parse_usage_from_log()
        
        return StateEvent(
            status=Status.RUNNING,
            confidence=1.0,
            details={
                'tokens': {
                    'input': usage['input_tokens'],
                    'output': usage['output_tokens'],
                    'cache_read': usage['cache_read_input_tokens'],
                }
            }
        )
```

---

## 总结

### PixelHQ-bridge 适用场景

✅ **最佳场景**:
- iOS App（Pixel Office）动画驱动
- 需要精确工具级信息
- 需要严格隐私保护
- 公开发布的 npm 包

❌ **不适合**:
- 需要高实时性（< 100ms 延迟）
- 需要系统级监控（CPU/内存）
- 需要快速支持新 AI 工具

---

### AI-ClaudeCat 适用场景

✅ **最佳场景**:
- 桌面宠物应用（本地监控）
- 需要高实时性（< 10ms）
- 需要系统级信息（CPU/窗口）
- 需要插件化扩展

❌ **不适合**:
- 需要工具级细节（Read/Write/Bash）
- 需要隐私保护（公开发布）
- 需要跨平台支持（当前仅 Windows）

---

### 融合方案建议 🎯

**最佳实践**: 结合两者优势

```python
# AI-ClaudeCat v3.2 架构
Plugins:
  ├── ProcessPlugin       # CPU 监控（ClaudeCat 原有）
  ├── WindowPlugin        # 窗口监控（ClaudeCat 原有）
  ├── ClaudeLogPlugin     # 日志监控（学习 PixelHQ）⭐ 新增
  └── TokenTrackerPlugin  # Token 统计（学习 PixelHQ）⭐ 新增

Middleware:
  ├── StateFusion         # 融合算法（ClaudeCat 原有）
  └── PrivacyFilter       # 隐私过滤（学习 PixelHQ）⭐ 新增

Adapters:
  ├── WebSocketAdapter    # WebSocket（ClaudeCat 原有）
  ├── HTTPAdapter         # HTTP API（ClaudeCat 原有）
  └── HistoryAdapter      # 历史存储 ⭐ 新增
```

**融合后的能力**:
- ✅ 高实时性（2秒轮询）+ 工具级精度（日志解析）
- ✅ 系统级监控（CPU/窗口）+ 操作级细节（Read/Write/Bash）
- ✅ 插件化架构（易扩展）+ 隐私保护（生产级）
- ✅ 多输出协议（WebSocket/HTTP）+ 历史查询（SQLite）

---

**文档版本**: v1.0  
**作者**: AI Assistant  
**最后更新**: 2026-02-06
