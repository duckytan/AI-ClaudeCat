# AI-ClaudeCat 重构方案 - 借鉴 PixelHQ-bridge

**制定时间**: 2026-02-06  
**当前版本**: v3.1  
**目标版本**: v4.0  
**重构理由**: 采用 PixelHQ-bridge 的成熟日志监控方案替代当前不可靠的系统 API 方式

---

## 目录

1. [重构目标](#重构目标)
2. [当前问题分析](#当前问题分析)
3. [PixelHQ 核心优势](#pixelhq-核心优势)
4. [整改方案](#整改方案)
5. [新架构设计](#新架构设计)
6. [实施计划](#实施计划)
7. [迁移路径](#迁移路径)

---

## 重构目标

### 核心目标 🎯

1. **弃用不可靠的系统 API 方式**
   - ❌ 删除：CPU 阈值判断（不准确，易误判）
   - ❌ 删除：文件活动猜测（无实际数据支撑）
   - ⚠️ **保留但不实装**：窗口标题检测（`src/utils/window_detector.py`）
     - 用途：未来的自动进程发现、自动绑定功能
     - 状态：独立工具模块，暂不集成到主流程

2. **采用 PixelHQ 的成熟方案**
   - ✅ 日志文件监控（`~/.claude/projects/**/*.jsonl`）
   - ✅ JSONL 增量解析
   - ✅ 工具级状态推断（Read/Write/Bash/Task）
   - ✅ 隐私保护管道

3. **保留 AI-ClaudeCat 的架构优势**
   - ✅ 插件化架构（易扩展）
   - ✅ 中间件模式（状态融合）
   - ✅ 多输出协议（WebSocket + HTTP）
   - ✅ Python 生态（易维护）

4. **增强功能**
   - ✅ Token 使用量统计
   - ✅ Agent 派生追踪
   - ✅ 事件历史存储
   - ✅ 隐私保护选项

---

## 当前问题分析

### v3.1 存在的问题 ❌

#### 1. **窗口标题检测不可靠**

**问题代码** (`src/apps/claude_code.py:190-231`):
```python
def _detect_by_window(self):
    # 获取所有窗口
    windows = get_all_windows()  # Windows API
    
    # 匹配标题关键词
    for pattern, status, confidence in TITLE_PATTERNS:
        if re.search(pattern, title_lower):
            return status, confidence
```

**问题**:
- ❌ Claude Code 窗口标题不包含状态信息
- ❌ 窗口标题是静态的（如 "Claude Code - project-name"）
- ❌ 无法区分 idle/thinking/working
- ❌ 误匹配其他窗口（如 VSCode）
- ❌ Windows API 依赖，跨平台困难

#### 2. **CPU 阈值判断不准确**

**问题代码** (`src/plugins/process.py:60-75`):
```python
THRESHOLDS = {
    "idle": 0.5,      # < 0.5%
    "running": 3.0,   # < 3%
    "thinking": 15.0, # < 15%
    "working": 50.0,  # < 50%
}
```

**问题**:
- ❌ 阈值是猜测的，无数据支撑
- ❌ AI 思考时 CPU 可能很低（等待 API）
- ❌ 后台进程干扰（浏览器、杀毒软件）
- ❌ 多核 CPU 百分比不准确
- ❌ 无法区分 idle 和 waiting for user

#### 3. **文件活动检测无效**

**问题代码** (`src/apps/claude_code.py:242-247`):
```python
def _detect_by_file_activity(self):
    time_since_activity = time.time() - self._last_activity_time
    is_active = time_since_activity < 3.0
```

**问题**:
- ❌ `on_file_activity()` 从未被调用（无文件监控插件）
- ❌ 3 秒阈值是随意设定的
- ❌ 无法区分读操作和写操作
- ❌ 无法知道文件类型（代码/配置/日志）

#### 4. **缺少工具级信息**

**问题**:
- ❌ 只知道状态（thinking），不知道在做什么（Read file? Write code?）
- ❌ 无法实现细粒度的 UI 反馈
- ❌ 无法统计 Token 使用量
- ❌ 无法追踪 Agent 派生

#### 5. **无隐私保护**

**问题**:
- ❌ 如果暴露接口，可能泄露文件路径、命令
- ❌ 不适合公开发布或团队共享

---

## PixelHQ 核心优势

### 1. **成熟的日志监控方案** ✅

**数据源**: Claude Code 官方生成的 JSONL 日志
```
~/.claude/projects/my-app/session-abc123.jsonl
```

**每行日志示例**:
```json
{
  "type": "assistant",
  "timestamp": "2026-02-06T12:34:56.789Z",
  "message": {
    "content": [
      {
        "type": "tool_use",
        "id": "toolu_xyz",
        "name": "Read",
        "input": { "file_path": "/path/to/file.ts" }
      }
    ],
    "usage": {
      "input_tokens": 5000,
      "output_tokens": 200,
      "cache_read_input_tokens": 1000
    }
  }
}
```

**优势**:
- ✅ 官方数据，格式稳定
- ✅ 工具级细节（Read/Write/Bash/Grep/Task）
- ✅ Token 使用量
- ✅ 事件时序（started → completed）
- ✅ 无需系统 API（跨平台）
- ✅ 已验证（PixelHQ 生产使用）

### 2. **增量读取机制** ✅

**实现** (`PixelHQ-bridge/src/watcher.ts:143-160`):
```typescript
// 记录每个文件的读取位置
filePositions: Map<string, number>

// 增量读取新行
async readNewLines(filePath, startPosition) {
  const stream = createReadStream(filePath, { 
    start: startPosition  // 从上次位置继续
  });
  return lines;
}
```

**优势**:
- ✅ 低 CPU 占用（只读新增内容）
- ✅ 无重复处理（记录位置）
- ✅ 实时性高（文件一写入就触发）

### 3. **严格的隐私保护** ✅

**过滤管道** (`PixelHQ-bridge/src/adapters/claude-code.ts:193-223`):
```typescript
function extractSafeContext(toolName, input) {
  switch (toolName) {
    case 'Read':
      return toBasename(input.file_path);  // 只保留文件名
    case 'Bash':
      return input.description || null;  // 只保留描述，不要命令
    case 'Grep':
      return input.pattern || null;  // 保留模式
    default:
      return null;  // 未知工具，不输出任何上下文
  }
}
```

**白名单机制**:
- ✅ 只输出允许的字段
- ✅ 测试覆盖（`tests/pipeline.test.ts`）
- ✅ 适合公开发布

### 4. **Agent 派生追踪** ✅

**实现** (`PixelHQ-bridge/src/session.ts:110-183`):
```typescript
// 追踪 Task 工具调用（派生子 Agent）
trackTaskSpawn(sessionId, toolUseId) {
  session.pendingTaskIds.add(toolUseId);
  session.pendingSpawnQueue.push(toolUseId);
}

// 当文件系统发现新的 subagent JSONL 时
correlateAgentFile(sessionId, fileAgentId) {
  const toolUseId = session.pendingSpawnQueue.shift();
  session.agentIdMap.set(fileAgentId, toolUseId);
}
```

**优势**:
- ✅ 关联 Task 工具和子 Agent 文件
- ✅ 追踪 Agent 完成状态
- ✅ FIFO 队列匹配

### 5. **事件驱动架构** ✅

**数据流**:
```
Watcher.on('line') 
  → Parser.parseJsonlLine()
  → Adapter.claudeCodeAdapter()
  → SessionManager.emit('event')
  → WebSocketServer.broadcast()
```

**优势**:
- ✅ 单向数据流（易理解）
- ✅ 解耦合（每个模块独立）
- ✅ 易测试（单元测试每个模块）

---

## 整改方案

### 方案概述 📋

**保留**: AI-ClaudeCat 的插件化架构、中间件模式  
**替换**: 状态检测方式（系统 API → 日志监控）  
**增强**: 借鉴 PixelHQ 的隐私保护、Agent 追踪、Token 统计

---

### 核心改动

#### 1. **新增 ClaudeLogPlugin（核心插件）** ⭐

**功能**: 监控 Claude Code JSONL 日志，替代所有系统 API 检测

**实现** (`src/plugins/claude_log.py`):
```python
# -*- coding: utf-8 -*-
"""
Claude Log Plugin - 日志文件监控（借鉴 PixelHQ-bridge）

功能：
1. 监控 ~/.claude/projects/**/*.jsonl
2. 增量读取新行
3. 解析 JSONL 事件
4. 推断状态（thinking/responding/tool_use）
5. 提取工具信息（Read/Write/Bash）
6. 统计 Token 使用量
7. 追踪 Agent 派生
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from src.plugins.base import BasePlugin, PluginMetadata, PluginType, StateEvent, Status


@dataclass
class ToolUseEvent:
    """工具调用事件"""
    tool_name: str
    tool_use_id: str
    input: Dict
    timestamp: str


class ClaudeLogPlugin(BasePlugin):
    """Claude Code 日志监控插件"""
    
    def __init__(self, name: str = "claude_log", check_interval: float = 0.5):
        super().__init__(name)
        self.check_interval = check_interval
        
        # Claude Code 项目目录
        self.projects_dir = self._find_claude_projects_dir()
        
        # 文件读取位置记录（增量读取）
        self.file_positions: Dict[str, int] = {}
        
        # 追踪的会话
        self.tracked_sessions: Set[str] = set()
        
        # 当前状态
        self._current_status: Status = Status.UNKNOWN
        
        # Token 统计
        self.token_stats: Dict[str, int] = {
            'input': 0,
            'output': 0,
            'cache_read': 0,
            'cache_write': 0,
        }
        
        # 文件监控器
        self.observer: Optional[Observer] = None
        
        self._metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            author="AI-ClaudeCat",
            description="Monitor Claude Code JSONL logs (inspired by PixelHQ-bridge)",
            plugin_type=PluginType.CUSTOM,
            supported_software=["Claude Code"],
            dependencies=["watchdog"],
        )
    
    def _find_claude_projects_dir(self) -> Optional[Path]:
        """查找 Claude Code 项目目录"""
        candidates = [
            Path.home() / ".claude" / "projects",
            Path.home() / ".config" / "claude" / "projects",
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        return None
    
    def check_available(self) -> bool:
        """检查 Claude Code 是否可用（目录存在）"""
        return self.projects_dir is not None and self.projects_dir.exists()
    
    async def detect(self) -> Optional[StateEvent]:
        """检测状态（由文件变化触发）"""
        # 状态已经在 _handle_new_line() 中更新
        return None
    
    def start(self) -> None:
        """启动文件监控"""
        if not self.check_available():
            print(f"[ClaudeLogPlugin] Projects dir not found")
            return
        
        self._running = True
        
        # 扫描现有文件
        self._scan_existing_files()
        
        # 启动文件监控器
        self._start_file_watcher()
        
        print(f"[ClaudeLogPlugin] Started, watching: {self.projects_dir}")
    
    def stop(self) -> None:
        """停止监控"""
        self._running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        print(f"[ClaudeLogPlugin] Stopped")
    
    def _scan_existing_files(self):
        """扫描现有 JSONL 文件"""
        if not self.projects_dir:
            return
        
        # 查找所有 .jsonl 文件
        for jsonl_file in self.projects_dir.rglob("*.jsonl"):
            # 只追踪最近 10 分钟的文件
            import time
            mtime = jsonl_file.stat().st_mtime
            age = time.time() - mtime
            
            if age < 10 * 60:  # 10 分钟
                # 设置读取位置为文件末尾（不读取历史）
                self.file_positions[str(jsonl_file)] = jsonl_file.stat().st_size
                
                session_id = self._extract_session_id(jsonl_file)
                self.tracked_sessions.add(session_id)
    
    def _start_file_watcher(self):
        """启动文件监控器（watchdog）"""
        class LogFileHandler(FileSystemEventHandler):
            def __init__(self, plugin):
                self.plugin = plugin
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                
                if event.src_path.endswith('.jsonl'):
                    # 异步处理文件变化
                    asyncio.create_task(
                        self.plugin._handle_file_change(event.src_path)
                    )
        
        self.observer = Observer()
        self.observer.schedule(
            LogFileHandler(self),
            str(self.projects_dir),
            recursive=True
        )
        self.observer.start()
    
    async def _handle_file_change(self, file_path: str):
        """处理文件变化（增量读取）"""
        try:
            # 获取当前文件大小
            file_size = Path(file_path).stat().st_size
            
            # 获取上次读取位置
            last_position = self.file_positions.get(file_path, 0)
            
            if file_size <= last_position:
                return  # 文件没有新内容
            
            # 读取新行
            new_lines = self._read_new_lines(file_path, last_position)
            
            # 更新读取位置
            self.file_positions[file_path] = file_size
            
            # 处理每一行
            session_id = self._extract_session_id(Path(file_path))
            
            for line in new_lines:
                await self._handle_new_line(line, session_id)
        
        except Exception as e:
            print(f"[ClaudeLogPlugin] Error handling file: {e}")
    
    def _read_new_lines(self, file_path: str, start_position: int) -> List[str]:
        """增量读取新行"""
        lines = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.seek(start_position)
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"[ClaudeLogPlugin] Error reading file: {e}")
        
        return lines
    
    async def _handle_new_line(self, line: str, session_id: str):
        """处理新行（JSONL 解析 + 状态推断）"""
        try:
            # 解析 JSON
            raw = json.loads(line)
            
            event_type = raw.get('type')
            timestamp = raw.get('timestamp', '')
            
            # 根据事件类型推断状态
            if event_type == 'assistant':
                await self._handle_assistant_message(raw, session_id, timestamp)
            
            elif event_type == 'user':
                await self._handle_user_message(raw, session_id, timestamp)
            
            elif event_type == 'summary':
                # 会话总结 → 回到 idle
                self._update_status(Status.IDLE, 1.0, {
                    'method': 'log',
                    'event': 'summary',
                    'session_id': session_id
                })
        
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"[ClaudeLogPlugin] Error parsing line: {e}")
    
    async def _handle_assistant_message(self, raw: Dict, session_id: str, timestamp: str):
        """处理 assistant 消息（AI 的输出）"""
        message = raw.get('message', {})
        content = message.get('content', [])
        usage = message.get('usage', {})
        
        # 统计 Token
        self._update_tokens(usage)
        
        # 处理内容块
        for block in content:
            block_type = block.get('type')
            
            if block_type == 'thinking':
                # AI 思考
                self._update_status(Status.THINKING, 0.95, {
                    'method': 'log',
                    'event': 'thinking',
                    'session_id': session_id
                })
            
            elif block_type == 'text':
                text = block.get('text', '')
                
                if text == '(no content)':
                    # 无内容 = 思考中
                    self._update_status(Status.THINKING, 0.95, {
                        'method': 'log',
                        'event': 'thinking_no_content',
                        'session_id': session_id
                    })
                else:
                    # 有内容 = 回复中
                    self._update_status(Status.WORKING, 0.90, {
                        'method': 'log',
                        'event': 'responding',
                        'session_id': session_id,
                        'tokens': usage
                    })
            
            elif block_type == 'tool_use':
                # 工具调用
                tool_name = block.get('name', '')
                tool_use_id = block.get('id', '')
                tool_input = block.get('input', {})
                
                # 根据工具类型推断状态
                status = self._tool_to_status(tool_name)
                
                self._update_status(status, 0.95, {
                    'method': 'log',
                    'event': 'tool_use',
                    'tool': tool_name,
                    'tool_use_id': tool_use_id,
                    'context': self._extract_safe_context(tool_name, tool_input),
                    'session_id': session_id
                })
    
    async def _handle_user_message(self, raw: Dict, session_id: str, timestamp: str):
        """处理 user 消息（用户的输入 / 工具结果）"""
        user_type = raw.get('userType')
        
        if user_type == 'tool_result':
            # 工具结果 → 回到 idle
            self._update_status(Status.IDLE, 0.85, {
                'method': 'log',
                'event': 'tool_result',
                'session_id': session_id
            })
        else:
            # 用户提示词 → 等待 AI 回复
            self._update_status(Status.RUNNING, 0.90, {
                'method': 'log',
                'event': 'user_prompt',
                'session_id': session_id
            })
    
    def _tool_to_status(self, tool_name: str) -> Status:
        """工具名称 → 状态映射"""
        tool_status_map = {
            'Read': Status.WORKING,
            'Write': Status.WORKING,
            'Edit': Status.WORKING,
            'Bash': Status.EXECUTING,
            'Grep': Status.WORKING,
            'Glob': Status.WORKING,
            'WebFetch': Status.WORKING,
            'WebSearch': Status.WORKING,
            'Task': Status.WORKING,
            'TodoWrite': Status.WORKING,
            'AskUserQuestion': Status.IDLE,  # 等待用户
        }
        
        return tool_status_map.get(tool_name, Status.WORKING)
    
    def _extract_safe_context(self, tool_name: str, tool_input: Dict) -> Optional[str]:
        """提取安全的上下文信息（隐私保护）"""
        if tool_name in ['Read', 'Write', 'Edit']:
            file_path = tool_input.get('file_path', '')
            return os.path.basename(file_path)  # 只保留文件名
        
        elif tool_name == 'Bash':
            return tool_input.get('description')  # 只保留描述，不要命令
        
        elif tool_name in ['Grep', 'Glob']:
            return tool_input.get('pattern')  # 保留搜索模式
        
        elif tool_name == 'Task':
            return tool_input.get('subagent_type')  # Agent 类型
        
        elif tool_name == 'TodoWrite':
            todos = tool_input.get('todos', [])
            return f"{len(todos)} items" if todos else None
        
        else:
            return None  # 未知工具，不输出
    
    def _update_tokens(self, usage: Dict):
        """更新 Token 统计"""
        self.token_stats['input'] += usage.get('input_tokens', 0)
        self.token_stats['output'] += usage.get('output_tokens', 0)
        self.token_stats['cache_read'] += usage.get('cache_read_input_tokens', 0)
        self.token_stats['cache_write'] += usage.get('cache_creation_input_tokens', 0)
    
    def _update_status(self, status: Status, confidence: float, details: Dict):
        """更新状态并发送事件"""
        if status != self._current_status:
            self._current_status = status
            
            event = StateEvent(
                status=status,
                confidence=confidence,
                source_plugin=self.name,
                source_type=PluginType.CUSTOM,
                details=details,
                priority=10,  # 高优先级（日志是最准确的）
            )
            
            self._emit(event)
    
    def _extract_session_id(self, file_path: Path) -> str:
        """从文件路径提取会话 ID"""
        # ~/.claude/projects/<project>/<session-id>.jsonl
        return file_path.stem
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata


def create_claude_log_plugin(
    name: str = "claude_log",
    check_interval: float = 0.5,
) -> ClaudeLogPlugin:
    """创建 Claude Log 插件的便捷函数"""
    return ClaudeLogPlugin(name=name, check_interval=check_interval)
```

---

#### 2. **弃用旧插件**

**删除/归档**:
- ❌ `src/apps/claude_code.py` - 窗口+进程+文件融合检测（不可靠）
- ❌ `src/plugins/process.py` - CPU 阈值判断（不准确）
- ❌ `src/plugins/window.py` - 窗口标题检测（无效）

**保留**（作为独立工具，不实装）:
- 📦 `src/utils/window_detector.py` - 窗口检测工具（未来功能）
  - 用途：自动发现 AI 编程工具进程
  - 用途：通过窗口标题自动绑定进程
  - 用途：多实例管理（同时监控多个 AI 工具）
  - 状态：独立工具模块，暂不集成到主流程
  - 等待：未来可能的应用场景

**简化保留**（作为备用/补充）:
- ⚠️ `src/plugins/process.py` - 简化为进程存活检测（只检测 stopped 状态）

---

#### 3. **增强中间件**

**新增功能**:

##### 3.1 隐私过滤器 (`src/middleware/privacy.py`)

```python
# -*- coding: utf-8 -*-
"""
隐私过滤器 - 过滤敏感信息（借鉴 PixelHQ-bridge）
"""

import os
from typing import Dict, Any

from src.plugins.base import StateEvent


class PrivacyFilter:
    """隐私过滤器"""
    
    def __init__(self, enable: bool = True):
        self.enable = enable
    
    def filter_event(self, event: StateEvent) -> StateEvent:
        """过滤事件中的敏感信息"""
        if not self.enable:
            return event
        
        # 过滤 details
        if event.details:
            event.details = self._filter_dict(event.details)
        
        return event
    
    def _filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤字典中的敏感字段"""
        filtered = {}
        
        for key, value in data.items():
            # 过滤文件路径 → 只保留 basename
            if key in ['file_path', 'path', 'file']:
                filtered[key] = os.path.basename(str(value))
            
            # 过滤命令 → 删除
            elif key in ['command', 'cmd', 'bash_command']:
                # 不输出命令内容
                pass
            
            # 过滤内容 → 删除
            elif key in ['content', 'text', 'code', 'output']:
                # 不输出文件内容
                pass
            
            # 允许的字段 → 保留
            elif key in [
                'method', 'event', 'tool', 'tool_use_id', 'context',
                'session_id', 'status', 'confidence', 'priority',
                'tokens', 'agent_type', 'pattern', 'description'
            ]:
                filtered[key] = value
            
            # 嵌套字典 → 递归过滤
            elif isinstance(value, dict):
                filtered[key] = self._filter_dict(value)
            
            # 其他字段 → 默认保留（可配置）
            else:
                filtered[key] = value
        
        return filtered
```

##### 3.2 Token 统计器 (`src/middleware/token_stats.py`)

```python
# -*- coding: utf-8 -*-
"""
Token 统计器 - 统计 AI API 使用量
"""

from typing import Dict
from datetime import datetime

from src.plugins.base import StateEvent


class TokenStats:
    """Token 使用量统计"""
    
    def __init__(self):
        self.total: Dict[str, int] = {
            'input': 0,
            'output': 0,
            'cache_read': 0,
            'cache_write': 0,
        }
        
        self.history: List[Dict] = []
        self.start_time = datetime.now()
    
    def update(self, event: StateEvent):
        """更新统计（从事件中提取 tokens）"""
        if not event.details:
            return
        
        tokens = event.details.get('tokens')
        if not tokens:
            return
        
        # 累加
        self.total['input'] += tokens.get('input_tokens', 0)
        self.total['output'] += tokens.get('output_tokens', 0)
        self.total['cache_read'] += tokens.get('cache_read_input_tokens', 0)
        self.total['cache_write'] += tokens.get('cache_creation_input_tokens', 0)
        
        # 记录历史
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'input': tokens.get('input_tokens', 0),
            'output': tokens.get('output_tokens', 0),
        })
    
    def get_summary(self) -> Dict:
        """获取统计摘要"""
        runtime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'total': self.total,
            'runtime_seconds': runtime,
            'average_per_minute': {
                'input': self.total['input'] / (runtime / 60) if runtime > 0 else 0,
                'output': self.total['output'] / (runtime / 60) if runtime > 0 else 0,
            },
            'cache_hit_rate': (
                self.total['cache_read'] / (self.total['input'] + self.total['cache_read'])
                if (self.total['input'] + self.total['cache_read']) > 0 else 0
            ),
        }
```

---

#### 4. **增强输出适配器**

##### 4.1 历史存储适配器 (`src/adapters/history_adapter.py`)

```python
# -*- coding: utf-8 -*-
"""
历史存储适配器 - SQLite 持久化
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional

from src.adapters.base import OutputAdapter
from src.plugins.base import StateEvent


class HistoryAdapter(OutputAdapter):
    """历史记录适配器（SQLite）"""
    
    def __init__(self, db_path: str = "data/history.db"):
        super().__init__("history")
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL NOT NULL,
                source_plugin TEXT NOT NULL,
                source_type TEXT NOT NULL,
                details TEXT,
                priority INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON events(timestamp)
        ''')
        
        self.conn.commit()
    
    async def send(self, event: StateEvent):
        """保存事件到数据库"""
        if not self.conn:
            return
        
        try:
            self.conn.execute('''
                INSERT INTO events (timestamp, status, confidence, source_plugin, source_type, details, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.timestamp,
                event.status.value,
                event.confidence,
                event.source_plugin,
                event.source_type.value,
                json.dumps(event.details) if event.details else None,
                event.priority,
            ))
            
            self.conn.commit()
        
        except Exception as e:
            print(f"[HistoryAdapter] Error saving event: {e}")
    
    def query(self, start_time: str = None, end_time: str = None, limit: int = 100):
        """查询历史事件"""
        if not self.conn:
            return []
        
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(query, params)
        
        rows = cursor.fetchall()
        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'status': row[2],
                'confidence': row[3],
                'source_plugin': row[4],
                'source_type': row[5],
                'details': json.loads(row[6]) if row[6] else None,
                'priority': row[7],
            }
            for row in rows
        ]
    
    async def stop(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
```

---

#### 5. **更新主程序**

**新的 main.py** (`main.py`):
```python
# -*- coding: utf-8 -*-
"""
AI-ClaudeCat v4.0 - 主程序入口
重构：采用 PixelHQ-bridge 的日志监控方案
"""

import asyncio
import sys

from src.plugins.claude_log import create_claude_log_plugin
from src.middleware.core import Middleware
from src.middleware.privacy import PrivacyFilter
from src.middleware.token_stats import TokenStats
from src.adapters.websocket_adapter import WebSocketAdapter
from src.adapters.http_adapter import HTTPAdapter
from src.adapters.stdout_adapter import StdoutAdapter
from src.adapters.history_adapter import HistoryAdapter


async def main():
    """主函数"""
    print("=== AI-ClaudeCat v4.0 ===")
    print("Status monitoring for Claude Code\n")
    
    # 1. 创建核心插件（日志监控）
    claude_log = create_claude_log_plugin(
        name="claude_log",
        check_interval=0.5  # 0.5秒检查一次
    )
    
    # 检查可用性
    if not claude_log.check_available():
        print("❌ Claude Code not found!")
        print("Expected: ~/.claude/projects/")
        sys.exit(1)
    
    print(f"✓ Claude Code detected at {claude_log.projects_dir}")
    
    # 2. 创建输出适配器
    adapters = [
        WebSocketAdapter(port=8765),
        HTTPAdapter(port=8080),
        StdoutAdapter(),
        HistoryAdapter(db_path="data/history.db"),
    ]
    
    # 3. 创建中间件（启用隐私保护）
    middleware = Middleware(
        plugins=[claude_log],
        adapters=adapters,
    )
    
    # 启用隐私过滤
    middleware.privacy_filter = PrivacyFilter(enable=True)
    
    # 启用 Token 统计
    middleware.token_stats = TokenStats()
    
    print("✓ Middleware initialized")
    print(f"✓ WebSocket server on port 8765")
    print(f"✓ HTTP server on port 8080")
    print(f"✓ Privacy filter enabled")
    print(f"✓ History storage enabled\n")
    
    # 4. 运行中间件
    try:
        await middleware.run()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        await middleware.stop()
    
    # 5. 输出统计
    if middleware.token_stats:
        summary = middleware.token_stats.get_summary()
        print("\n=== Token Usage Summary ===")
        print(f"Input tokens:  {summary['total']['input']}")
        print(f"Output tokens: {summary['total']['output']}")
        print(f"Cache read:    {summary['total']['cache_read']}")
        print(f"Cache hit rate: {summary['cache_hit_rate']:.2%}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 新架构设计

### v4.0 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     AI-ClaudeCat v4.0                        │
│                  (借鉴 PixelHQ-bridge)                       │
└─────────────────────────────────────────────────────────────┘

数据源层
┌──────────────────────────────────────────┐
│  ~/.claude/projects/**/*.jsonl           │
│  - session-abc123.jsonl                  │
│  - session-abc123/subagents/xyz.jsonl    │
└──────────────────────────────────────────┘
           │
           ▼
监控层
┌──────────────────────────────────────────┐
│  ClaudeLogPlugin (核心插件) ⭐            │
│  - Watchdog 文件监控                      │
│  - 增量读取 (filePositions)              │
│  - JSONL 解析                            │
│  - 状态推断 (thinking/tool_use)          │
│  - Token 统计                            │
│  - Agent 追踪                            │
└──────────────────────────────────────────┘
           │ emit(StateEvent)
           ▼
中间件层
┌──────────────────────────────────────────┐
│  Middleware                              │
│  ├── EventBus (事件分发)                 │
│  ├── StateFusion (状态融合) ⚠️ 简化       │
│  ├── PrivacyFilter (隐私过滤) ⭐ 新增     │
│  └── TokenStats (Token 统计) ⭐ 新增      │
└──────────────────────────────────────────┘
           │
           ▼
输出层
┌──────────────────────────────────────────┐
│  OutputAdapters                          │
│  ├── WebSocketAdapter (ws://8765)        │
│  ├── HTTPAdapter (http://8080)           │
│  ├── StdoutAdapter (终端输出)            │
│  └── HistoryAdapter (SQLite) ⭐ 新增      │
└──────────────────────────────────────────┘
           │
           ▼
消费端
┌──────────────────────────────────────────┐
│  - 桌面宠物 GUI (Electron/Qt)            │
│  - 浏览器插件 (Chrome Extension)         │
│  - 移动端 App (React Native)             │
│  - CLI 工具                              │
└──────────────────────────────────────────┘
```

---

### 数据流

```
文件变化
    │
    ▼
Watchdog
    │ on_modified
    ▼
ClaudeLogPlugin._handle_file_change()
    │
    ├─► 增量读取新行
    ├─► 解析 JSONL
    ├─► 推断状态
    └─► emit(StateEvent)
           │
           ▼
Middleware._on_plugin_event()
           │
           ├─► PrivacyFilter.filter_event()  # 隐私过滤
           ├─► TokenStats.update()            # Token 统计
           └─► StateFusion.fuse_events()      # 状态融合（简化）
                   │
                   ▼
           for adapter in adapters:
               await adapter.send(event)
                   │
                   ├─► WebSocketAdapter → 前端
                   ├─► HTTPAdapter → REST API
                   ├─► StdoutAdapter → 终端
                   └─► HistoryAdapter → SQLite
```

---

## 实施计划

### 第一阶段：核心重构（v4.0-alpha）⏱️ 2-3 天

#### Day 1: 核心插件开发
- [ ] 创建 `src/plugins/claude_log.py`
- [ ] 实现文件监控（watchdog）
- [ ] 实现增量读取
- [ ] 实现 JSONL 解析
- [ ] 实现状态推断逻辑
- [ ] 单元测试（模拟 JSONL 日志）

#### Day 2: 中间件增强
- [ ] 创建 `src/middleware/privacy.py`
- [ ] 创建 `src/middleware/token_stats.py`
- [ ] 简化 `src/middleware/fusion.py`（单插件模式）
- [ ] 更新 `src/middleware/core.py`

#### Day 3: 输出和测试
- [ ] 创建 `src/adapters/history_adapter.py`
- [ ] 更新 `main.py`
- [ ] 集成测试（运行 Claude Code，验证监控）
- [ ] 性能测试（CPU/内存占用）

### 第二阶段：功能增强（v4.0-beta）⏱️ 1-2 天

#### Day 4: Agent 追踪
- [ ] 实现 subagent 文件关联
- [ ] 实现 Task 工具追踪
- [ ] 实现 Agent 完成事件

#### Day 5: 查询 API
- [ ] HTTP 查询接口（历史事件）
- [ ] Token 统计接口
- [ ] 实时状态接口

### 第三阶段：清理和发布（v4.0-stable）⏱️ 1 天

#### Day 6: 代码清理
- [ ] 删除/归档旧插件
  - `src/apps/claude_code.py`
  - `src/plugins/process.py`
  - `src/plugins/window.py`
- [ ] 更新文档
  - `README.md`
  - `CLAUDE.md`
  - `AGENTS.md`
- [ ] 更新配置文件
  - `config.json`
  - `requirements.txt`

---

## 迁移路径

### 兼容性策略

#### 1. **渐进式迁移**（推荐）

**阶段 1**: v4.0-alpha（双模式）
- ✅ 新增 `ClaudeLogPlugin`
- ✅ 保留旧插件（但标记为 deprecated）
- ✅ 配置开关：`config.json` 中选择模式

```json
{
  "detection_mode": "log",  // "log" | "system" | "hybrid"
  "plugins": {
    "claude_log": {
      "enabled": true,
      "priority": 10
    },
    "claude_code_legacy": {
      "enabled": false,
      "priority": 5
    }
  }
}
```

**阶段 2**: v4.0-beta
- ✅ 默认启用 `ClaudeLogPlugin`
- ⚠️ 旧插件标记为 deprecated（警告提示）

**阶段 3**: v4.0-stable
- ✅ 移除旧插件
- ✅ 只保留 `ClaudeLogPlugin`

#### 2. **直接切换**（快速）

- 直接删除旧插件
- 只使用 `ClaudeLogPlugin`
- 更新文档

---

### 配置文件示例

**新的 config.json**:
```json
{
  "version": "4.0.0",
  "description": "AI-ClaudeCat configuration (v4.0 - log-based detection)",
  
  "claude": {
    "projects_dir": "auto",
    "watch_debounce_ms": 100,
    "session_ttl_minutes": 10
  },
  
  "plugins": {
    "claude_log": {
      "enabled": true,
      "check_interval": 0.5,
      "priority": 10
    }
  },
  
  "middleware": {
    "privacy_filter": {
      "enabled": true,
      "whitelist": [
        "method", "event", "tool", "context",
        "session_id", "status", "confidence",
        "tokens", "agent_type", "pattern"
      ]
    },
    "token_stats": {
      "enabled": true
    }
  },
  
  "adapters": {
    "websocket": {
      "enabled": true,
      "port": 8765,
      "host": "127.0.0.1"
    },
    "http": {
      "enabled": true,
      "port": 8080,
      "host": "127.0.0.1",
      "cors": true
    },
    "stdout": {
      "enabled": true,
      "format": "simple"
    },
    "history": {
      "enabled": true,
      "db_path": "data/history.db",
      "max_events": 10000
    }
  }
}
```

---

## 总结

### 重构后的优势 ✅

1. **可靠性大幅提升**
   - ✅ 使用官方日志数据（格式稳定）
   - ✅ 工具级精度（Read/Write/Bash）
   - ✅ 已验证方案（PixelHQ 生产使用）

2. **功能显著增强**
   - ✅ Token 使用量统计
   - ✅ Agent 派生追踪
   - ✅ 事件历史存储
   - ✅ 隐私保护机制

3. **架构更加清晰**
   - ✅ 单一数据源（日志文件）
   - ✅ 单向数据流（易理解）
   - ✅ 模块解耦（易测试）

4. **跨平台支持**
   - ✅ 无需系统 API（文件监控是跨平台的）
   - ✅ Python 生态（watchdog 支持全平台）

### 工作量评估 ⏱️

- **核心重构**: 2-3 天
- **功能增强**: 1-2 天
- **清理发布**: 1 天
- **总计**: 4-6 天

### 风险评估 ⚠️

- **风险 1**: Claude Code 日志格式变化
  - **缓解**: PixelHQ 已验证，格式稳定
  - **应对**: 版本检测 + 兼容层

- **风险 2**: 文件监控性能
  - **缓解**: 增量读取，CPU 占用低
  - **应对**: 性能测试 + 优化

- **风险 3**: 用户习惯改变
  - **缓解**: 渐进式迁移，保留配置开关
  - **应对**: 文档说明 + 示例

---

**下一步行动**: 

1. ✅ Review 本方案
2. 📝 确认重构范围
3. 🚀 开始实施第一阶段

**预期成果**: 

一个基于 PixelHQ-bridge 成熟方案的、可靠的、功能完善的 AI-ClaudeCat v4.0！🎉
