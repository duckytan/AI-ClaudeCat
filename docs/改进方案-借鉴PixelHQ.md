# AI-ClaudeCat 改进方案 - 借鉴 PixelHQ-bridge

**文档版本**: v1.0  
**创建时间**: 2026-02-06  
**作者**: AI Assistant  

---

## 概述

基于 [PixelHQ-bridge](../参考项目/PixelHQ-bridge) 的成熟实现，我们可以在以下四个方面改进 AI-ClaudeCat：

1. ✅ **子 Agent 支持** - 监控 `subagents/*.jsonl`
2. ✅ **测试覆盖** - 添加隐私过滤测试
3. ✅ **会话管理** - 追踪会话生命周期
4. ✅ **更细粒度事件** - 一个 JSONL 产生多个事件

---

## 1. 子 Agent 支持 🤖

### 背景

Claude Code 从某个版本开始支持**子 Agent**（通过 `Task` 工具调用）。当主 Agent 派生子 Agent 时，会创建新的日志文件：

```
~/.claude/projects/my-app/
├── session-abc123.jsonl              # 主 Agent
└── session-abc123/                   # 子 Agent 目录
    └── subagents/
        ├── agent-def456.jsonl        # 子 Agent 1
        └── agent-ghi789.jsonl        # 子 Agent 2
```

### PixelHQ 的实现

#### 文件路径解析

```typescript
// PixelHQ-bridge/src/watcher.ts
parseFilePath(filePath: string): ParsedFilePath {
  const fileName = basename(filePath, '.jsonl');
  const dirPath = dirname(filePath);
  
  const isSubagent = dirPath.includes('/subagents');
  
  let sessionId: string;
  let agentId: string | null = null;
  let project: string;
  
  if (isSubagent) {
    agentId = fileName;                              // agent-def456
    const subagentsDir = dirname(dirPath);           // session-abc123
    sessionId = basename(subagentsDir);              // session-abc123
    project = basename(dirname(subagentsDir));       // my-app
  } else {
    sessionId = fileName;                            // session-abc123
    project = basename(dirPath);                     // my-app
  }
  
  return { sessionId, agentId, project };
}
```

#### 监控规则

```typescript
// PixelHQ-bridge/src/watcher.ts
const patterns = [
  join(config.projectsDir, '*', '*.jsonl'),           // 主 Agent
  join(config.projectsDir, '*', '*', 'subagents', '*.jsonl'),  // 子 Agent
];

watch(patterns, {
  awaitWriteFinish: { stabilityThreshold: 100 },
  usePolling: false
});
```

#### 事件生成

```typescript
// PixelHQ-bridge/src/adapters/claude-code.ts
if (block.name === 'Task') {
  events.push(
    createAgentEvent(
      sessionId,
      block.id,
      timestamp,
      'spawned',  // 子 Agent 被派生
      block.input?.subagent_type || 'general'
    )
  );
}
```

---

### 我们的改进方案

#### 修改 `ClaudeLogPlugin`

```python
# src/plugins/claude_log.py

class ClaudeLogPlugin(BasePlugin):
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        # 新增：支持子 Agent
        self.track_subagents = config.get('track_subagents', True) if config else True
        
        # 会话 ID → Agent ID 映射
        self.active_agents: Dict[str, Set[str]] = {}
        # Agent ID → 类型映射
        self.agent_types: Dict[str, str] = {}
    
    async def start(self):
        """启动监控"""
        # 监控主 Agent 日志
        main_pattern = str(self.projects_dir / '*' / '*.jsonl')
        
        # 监控子 Agent 日志
        if self.track_subagents:
            sub_pattern = str(self.projects_dir / '*' / '*' / 'subagents' / '*.jsonl')
            # 注册两个模式
            self.observer.schedule(
                self._file_handler,
                str(self.projects_dir),
                recursive=True
            )
    
    def _parse_file_path(self, file_path: str) -> Dict[str, str]:
        """
        解析文件路径，提取项目、会话、Agent 信息
        
        Returns:
            {
                'project': 'my-app',
                'session_id': 'session-abc123',
                'agent_id': 'agent-def456' or None,
                'is_subagent': True/False
            }
        """
        path = Path(file_path)
        
        # 检查是否是子 Agent
        is_subagent = 'subagents' in path.parts
        
        if is_subagent:
            # 路径: projects/my-app/session-abc123/subagents/agent-def456.jsonl
            agent_id = path.stem
            session_dir = path.parent.parent
            session_id = session_dir.name
            project = session_dir.parent.name
        else:
            # 路径: projects/my-app/session-abc123.jsonl
            agent_id = None
            session_id = path.stem
            project = path.parent.name
        
        return {
            'project': project,
            'session_id': session_id,
            'agent_id': agent_id,
            'is_subagent': is_subagent
        }
    
    async def _handle_new_line(self, line: str, file_path: str):
        """处理新日志行"""
        try:
            event = json.loads(line)
            path_info = self._parse_file_path(file_path)
            
            # 更新当前会话和 Agent
            self.current_session = path_info['session_id']
            current_agent = path_info['agent_id']
            
            # 检查是否是 Task 工具（派生子 Agent）
            if event.get('method') == 'content_block_start':
                block = event.get('params', {}).get('block', {})
                
                if block.get('name') == 'Task':
                    # 提取子 Agent 类型
                    subagent_type = block.get('input', {}).get('subagent_name', 'general')
                    
                    # 记录子 Agent
                    if self.current_session not in self.active_agents:
                        self.active_agents[self.current_session] = set()
                    
                    agent_id = block.get('id', '')
                    self.active_agents[self.current_session].add(agent_id)
                    self.agent_types[agent_id] = subagent_type
                    
                    # 发送 Agent 派生事件
                    await self._update_status(
                        Status.WORKING,
                        confidence=0.95,
                        details={
                            'event': 'agent_spawned',
                            'agent_type': subagent_type,
                            'agent_id': agent_id,
                            'session_id': self.current_session,
                            'is_subagent': True
                        }
                    )
            
            # 原有的事件处理逻辑...
            # 但增加 agent_id 和 is_subagent 信息
            
        except json.JSONDecodeError:
            pass
```

#### 配置文件更新

```json
{
  "plugins": {
    "claude_log": {
      "enabled": true,
      "check_interval": 0.5,
      "priority": 10,
      "show_all_errors": false,
      "track_subagents": true
    }
  }
}
```

#### 输出示例

```
[14:23:15] [WORKING] claude_log (95%) - Task 工具调用
[14:23:16] [WORKING] claude_log (95%) - Agent 派生: code-explorer
[14:23:18] [WORKING] claude_log (90%) - [子Agent] code-explorer 搜索代码
[14:23:22] [WORKING] claude_log (90%) - [子Agent] code-explorer 完成
[14:23:23] [WORKING] claude_log (90%) - 主 Agent 继续工作
```

---

## 2. 测试覆盖 🧪

### 背景

当前项目**缺少测试**，这会导致：
- 隐私过滤逻辑可能失效
- 重构时容易引入 bug
- 难以验证新功能

### PixelHQ 的实现

```typescript
// PixelHQ-bridge/tests/privacy.test.ts
describe('Privacy Filter', () => {
  it('should redact file paths', () => {
    const event = {
      tool: 'Write',
      file: '/Users/john/secret/password.txt',
      content: 'my-password-123'
    };
    
    const filtered = privacyFilter(event);
    
    expect(filtered.file).toBeUndefined();
    expect(filtered.content).toBeUndefined();
    expect(filtered.tool).toBe('Write');
  });
  
  it('should preserve metadata', () => {
    const event = {
      method: 'content_block_start',
      tool: 'Read',
      session_id: 'abc123',
      file: '/path/to/file.txt'
    };
    
    const filtered = privacyFilter(event);
    
    expect(filtered.method).toBe('content_block_start');
    expect(filtered.tool).toBe('Read');
    expect(filtered.session_id).toBe('abc123');
    expect(filtered.file).toBeUndefined();
  });
});
```

---

### 我们的改进方案

#### 创建测试文件

```python
# tests/test_privacy_filter.py
import pytest
from src.middleware.privacy import PrivacyFilter
from src.plugins.base import StateEvent, Status

class TestPrivacyFilter:
    """隐私过滤器测试"""
    
    @pytest.fixture
    def filter(self):
        """创建过滤器实例"""
        config = {
            'whitelist': [
                'method', 'event', 'tool', 'context',
                'session_id', 'status', 'confidence',
                'tokens', 'agent_type', 'pattern'
            ]
        }
        return PrivacyFilter(config)
    
    def test_filter_sensitive_content(self, filter):
        """测试过滤敏感内容"""
        event = StateEvent(
            status=Status.WORKING,
            source='test',
            confidence=0.95,
            details={
                'tool': 'Write',
                'file_path': '/Users/john/secret/password.txt',
                'content': 'my-password-123',
                'command': 'rm -rf /',
                'method': 'content_block_start'
            }
        )
        
        filtered = filter.filter_event(event)
        
        # 应该保留的字段
        assert filtered.details['method'] == 'content_block_start'
        assert filtered.details['tool'] == 'Write'
        
        # 应该过滤的字段
        assert 'content' not in filtered.details
        assert 'command' not in filtered.details
    
    def test_preserve_metadata(self, filter):
        """测试保留元数据"""
        event = StateEvent(
            status=Status.WORKING,
            source='test',
            confidence=0.95,
            details={
                'method': 'content_block_start',
                'tool': 'Read',
                'session_id': 'abc123',
                'tokens': {'input': 100, 'output': 50}
            }
        )
        
        filtered = filter.filter_event(event)
        
        assert filtered.details['method'] == 'content_block_start'
        assert filtered.details['tool'] == 'Read'
        assert filtered.details['session_id'] == 'abc123'
        assert filtered.details['tokens'] == {'input': 100, 'output': 50}
    
    def test_redact_file_path(self, filter):
        """测试文件路径脱敏"""
        event = StateEvent(
            status=Status.WORKING,
            source='test',
            confidence=0.95,
            details={
                'file_path': '/Users/john/projects/my-app/src/main.py',
                'tool': 'Read'
            }
        )
        
        filtered = filter.filter_event(event)
        
        # file_path 应该只保留文件名
        assert filtered.details['file_path'] == 'main.py'
    
    def test_disable_filter(self):
        """测试禁用过滤器"""
        filter = PrivacyFilter({'enabled': False})
        
        event = StateEvent(
            status=Status.WORKING,
            source='test',
            confidence=0.95,
            details={
                'content': 'sensitive data',
                'command': 'rm -rf /'
            }
        )
        
        filtered = filter.filter_event(event)
        
        # 禁用时应该原样返回
        assert filtered.details['content'] == 'sensitive data'
        assert filtered.details['command'] == 'rm -rf /'

# tests/test_token_stats.py
import pytest
from src.middleware.token_stats import TokenStats
from src.plugins.base import StateEvent, Status

class TestTokenStats:
    """Token 统计测试"""
    
    @pytest.fixture
    def stats(self):
        """创建统计器实例"""
        return TokenStats({'enabled': True})
    
    def test_update_tokens(self, stats):
        """测试 Token 更新"""
        event = StateEvent(
            status=Status.WORKING,
            source='test',
            confidence=0.95,
            details={
                'tokens': {
                    'input': 100,
                    'output': 50,
                    'cache_read': 200
                }
            }
        )
        
        stats.update(event)
        
        assert stats.total_tokens['input'] == 100
        assert stats.total_tokens['output'] == 50
        assert stats.total_tokens['cache_read'] == 200
    
    def test_cache_hit_rate(self, stats):
        """测试缓存命中率"""
        # 第一次请求（无缓存）
        event1 = StateEvent(
            status=Status.WORKING,
            source='test',
            confidence=0.95,
            details={'tokens': {'input': 1000}}
        )
        stats.update(event1)
        
        # 第二次请求（有缓存）
        event2 = StateEvent(
            status=Status.WORKING,
            source='test',
            confidence=0.95,
            details={'tokens': {'cache_read': 800, 'input': 200}}
        )
        stats.update(event2)
        
        rate = stats.get_cache_hit_rate()
        assert rate == 0.8  # 800 / (800 + 200)
    
    def test_cost_savings(self, stats):
        """测试成本节省"""
        event = StateEvent(
            status=Status.WORKING,
            source='test',
            confidence=0.95,
            details={
                'tokens': {
                    'input': 1000,
                    'cache_read': 5000
                }
            }
        )
        stats.update(event)
        
        savings = stats.get_cost_savings()
        assert savings > 0  # 应该有成本节省

# tests/test_claude_log_plugin.py
import pytest
import json
from pathlib import Path
from src.plugins.claude_log import ClaudeLogPlugin
from src.plugins.base import Status

class TestClaudeLogPlugin:
    """Claude 日志插件测试"""
    
    @pytest.fixture
    def plugin(self, tmp_path):
        """创建插件实例（使用临时目录）"""
        config = {
            'projects_dir': str(tmp_path),
            'track_subagents': True
        }
        return ClaudeLogPlugin(config)
    
    def test_parse_main_agent_path(self, plugin):
        """测试主 Agent 路径解析"""
        file_path = '/home/user/.claude/projects/my-app/session-abc123.jsonl'
        
        info = plugin._parse_file_path(file_path)
        
        assert info['project'] == 'my-app'
        assert info['session_id'] == 'session-abc123'
        assert info['agent_id'] is None
        assert info['is_subagent'] is False
    
    def test_parse_subagent_path(self, plugin):
        """测试子 Agent 路径解析"""
        file_path = '/home/user/.claude/projects/my-app/session-abc123/subagents/agent-def456.jsonl'
        
        info = plugin._parse_file_path(file_path)
        
        assert info['project'] == 'my-app'
        assert info['session_id'] == 'session-abc123'
        assert info['agent_id'] == 'agent-def456'
        assert info['is_subagent'] is True
    
    @pytest.mark.asyncio
    async def test_detect_agent_spawn(self, plugin, tmp_path):
        """测试检测 Agent 派生"""
        # 创建测试日志文件
        log_file = tmp_path / 'my-app' / 'session-abc123.jsonl'
        log_file.parent.mkdir(parents=True)
        
        # 写入 Task 工具调用
        event = {
            'method': 'content_block_start',
            'params': {
                'block': {
                    'name': 'Task',
                    'id': 'block-123',
                    'input': {
                        'subagent_name': 'code-explorer'
                    }
                }
            }
        }
        log_file.write_text(json.dumps(event) + '\n')
        
        # 启动插件
        await plugin.start()
        
        # 等待检测
        import asyncio
        await asyncio.sleep(0.2)
        
        # 验证
        assert 'session-abc123' in plugin.active_agents
        assert 'block-123' in plugin.active_agents['session-abc123']
        assert plugin.agent_types['block-123'] == 'code-explorer'
```

#### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_privacy_filter.py -v

# 代码覆盖率
pip install pytest-cov
pytest tests/ --cov=src --cov-report=html
```

---

## 3. 会话管理 📊

### 背景

当前实现只追踪**当前会话**，没有维护会话生命周期：
- 会话何时开始？
- 会话何时结束？
- 多个会话如何切换？

### PixelHQ 的实现

```typescript
// PixelHQ-bridge/src/watcher.ts
class SessionManager {
  private sessions: Map<string, Session> = new Map();
  
  onSessionStart(sessionId: string, project: string) {
    this.sessions.set(sessionId, {
      id: sessionId,
      project,
      startTime: Date.now(),
      lastActivity: Date.now(),
      agents: new Set(),
      status: 'active'
    });
    
    emitEvent('session_start', { sessionId, project });
  }
  
  onSessionActivity(sessionId: string) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.lastActivity = Date.now();
    }
  }
  
  onSessionEnd(sessionId: string) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.status = 'ended';
      session.endTime = Date.now();
      
      emitEvent('session_end', {
        sessionId,
        duration: session.endTime - session.startTime,
        agents: session.agents.size
      });
    }
  }
  
  // 定期检查超时会话
  checkTimeouts() {
    const timeout = 10 * 60 * 1000; // 10 分钟
    const now = Date.now();
    
    for (const [sessionId, session] of this.sessions) {
      if (session.status === 'active' && 
          now - session.lastActivity > timeout) {
        this.onSessionEnd(sessionId);
      }
    }
  }
}
```

---

### 我们的改进方案

#### 创建会话管理器

```python
# src/middleware/session_manager.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
import asyncio

@dataclass
class Session:
    """会话信息"""
    id: str
    project: str
    start_time: datetime
    last_activity: datetime
    agents: Set[str] = field(default_factory=set)
    status: str = 'active'  # active, idle, ended
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> timedelta:
        """会话持续时间"""
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    @property
    def idle_time(self) -> timedelta:
        """空闲时间"""
        return datetime.now() - self.last_activity
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'project': self.project,
            'start_time': self.start_time.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'agents': list(self.agents),
            'status': self.status,
            'duration_seconds': self.duration.total_seconds(),
            'idle_seconds': self.idle_time.total_seconds()
        }

class SessionManager:
    """会话管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # 会话超时（分钟）
        self.timeout_minutes = self.config.get('timeout_minutes', 10)
        
        # 活动会话
        self.sessions: Dict[str, Session] = {}
        
        # 回调函数
        self.callbacks: Dict[str, list] = {
            'session_start': [],
            'session_end': [],
            'session_idle': [],
            'session_active': []
        }
        
        # 后台任务
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """启动会话管理器"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """停止会话管理器"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    def on_session_start(self, session_id: str, project: str):
        """会话开始"""
        if session_id in self.sessions:
            # 会话已存在，更新活动时间
            self.on_session_activity(session_id)
            return
        
        session = Session(
            id=session_id,
            project=project,
            start_time=datetime.now(),
            last_activity=datetime.now()
        )
        self.sessions[session_id] = session
        
        self._emit('session_start', session.to_dict())
    
    def on_session_activity(self, session_id: str):
        """会话活动"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        was_idle = session.status == 'idle'
        session.last_activity = datetime.now()
        session.status = 'active'
        
        if was_idle:
            self._emit('session_active', session.to_dict())
    
    def on_session_end(self, session_id: str):
        """会话结束"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        session.status = 'ended'
        session.end_time = datetime.now()
        
        self._emit('session_end', session.to_dict())
        
        # 延迟删除（保留 1 小时）
        asyncio.create_task(self._delayed_remove(session_id, hours=1))
    
    def add_agent(self, session_id: str, agent_id: str):
        """添加 Agent"""
        session = self.sessions.get(session_id)
        if session:
            session.agents.add(agent_id)
            self.on_session_activity(session_id)
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def get_active_sessions(self) -> Dict[str, Session]:
        """获取活动会话"""
        return {
            sid: s for sid, s in self.sessions.items()
            if s.status == 'active'
        }
    
    def register_callback(self, event: str, callback):
        """注册回调"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _emit(self, event: str, data: Dict):
        """触发回调"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(event, data)
            except Exception as e:
                print(f"[SessionManager] Callback error: {e}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                self._check_timeouts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[SessionManager] Cleanup error: {e}")
    
    def _check_timeouts(self):
        """检查超时会话"""
        timeout = timedelta(minutes=self.timeout_minutes)
        now = datetime.now()
        
        for session_id, session in list(self.sessions.items()):
            if session.status != 'active':
                continue
            
            idle_time = now - session.last_activity
            
            if idle_time > timeout:
                # 会话超时
                session.status = 'idle'
                self._emit('session_idle', session.to_dict())
            elif idle_time > timeout * 2:
                # 超过 2 倍超时，标记为结束
                self.on_session_end(session_id)
    
    async def _delayed_remove(self, session_id: str, hours: int = 1):
        """延迟删除会话"""
        await asyncio.sleep(hours * 3600)
        if session_id in self.sessions:
            del self.sessions[session_id]
```

#### 集成到中间件

```python
# src/middleware/core.py
from src.middleware.session_manager import SessionManager

class Middleware:
    def __init__(self, config: Optional[Dict] = None):
        # ... 现有代码 ...
        
        # 会话管理器
        self.session_manager = SessionManager(
            config.get('middleware', {}).get('session_manager', {})
        )
    
    async def start(self):
        """启动中间件"""
        # ... 现有代码 ...
        
        # 启动会话管理器
        await self.session_manager.start()
        
        # 注册会话事件回调
        self.session_manager.register_callback(
            'session_start',
            lambda event, data: print(f"[Middleware] Session started: {data['id']}")
        )
        self.session_manager.register_callback(
            'session_end',
            lambda event, data: print(f"[Middleware] Session ended: {data['id']} (duration: {data['duration_seconds']}s)")
        )
    
    def _on_plugin_event(self, event: StateEvent):
        """处理插件事件"""
        # ... 现有代码 ...
        
        # 更新会话管理器
        session_id = event.details.get('session_id')
        if session_id:
            project = event.details.get('project', 'unknown')
            
            # 首次活动时创建会话
            if not self.session_manager.get_session(session_id):
                self.session_manager.on_session_start(session_id, project)
            else:
                self.session_manager.on_session_activity(session_id)
            
            # 添加 Agent
            agent_id = event.details.get('agent_id')
            if agent_id:
                self.session_manager.add_agent(session_id, agent_id)
```

#### 配置文件更新

```json
{
  "middleware": {
    "session_manager": {
      "timeout_minutes": 10
    }
  }
}
```

#### 输出示例

```
[14:23:15] [Middleware] Session started: session-abc123
[14:23:18] [WORKING] claude_log (95%)
[14:23:25] [WORKING] claude_log (90%)
[14:33:15] [Middleware] Session idle: session-abc123 (10 minutes)
[14:43:15] [Middleware] Session ended: session-abc123 (duration: 1200s)
```

---

## 4. 更细粒度事件 🔬

### 背景

当前实现：**一行 JSONL → 一个事件**

PixelHQ 实现：**一行 JSONL → 多个事件**

**优势**：
- 更准确的状态追踪
- 更详细的时间线
- 更好的调试体验

### PixelHQ 的实现

```typescript
// PixelHQ-bridge/src/adapters/claude-code.ts
export function parseLogLine(line: string): Event[] {
  const data = JSON.parse(line);
  const events: Event[] = [];  // 多个事件
  
  switch (data.method) {
    case 'content_block_start':
      const block = data.params.block;
      
      // 事件 1: 内容块开始
      events.push({
        type: 'block_start',
        block_id: block.id,
        block_type: block.type
      });
      
      // 事件 2: 工具调用（如果有）
      if (block.type === 'tool_use') {
        events.push({
          type: 'tool_start',
          tool: block.name,
          tool_id: block.id
        });
        
        // 事件 3: 特殊工具事件
        if (block.name === 'Task') {
          events.push({
            type: 'agent_spawned',
            agent_type: block.input.subagent_type
          });
        }
        if (block.name === 'AskUserQuestion') {
          events.push({
            type: 'waiting_user',
            question: block.input.question
          });
        }
      }
      break;
    
    case 'content_block_delta':
      // 事件 4: 内容更新
      events.push({
        type: 'block_delta',
        content: data.params.delta.text
      });
      break;
    
    case 'content_block_stop':
      // 事件 5: 内容块结束
      events.push({
        type: 'block_stop',
        block_id: data.params.block_id
      });
      break;
  }
  
  return events;
}
```

---

### 我们的改进方案

#### 修改事件处理

```python
# src/plugins/claude_log.py

class ClaudeLogPlugin(BasePlugin):
    async def _handle_new_line(self, line: str, file_path: str):
        """处理新日志行（生成多个事件）"""
        try:
            data = json.loads(line)
            path_info = self._parse_file_path(file_path)
            
            # 生成事件列表
            events = self._parse_log_events(data, path_info)
            
            # 发送所有事件
            for event in events:
                await self._emit_event(event)
        
        except json.JSONDecodeError:
            pass
    
    def _parse_log_events(self, data: Dict, path_info: Dict) -> List[StateEvent]:
        """
        解析 JSONL，生成多个事件
        
        一行 JSONL 可能产生：
        1. 主事件（状态变化）
        2. 工具事件（工具调用）
        3. 子事件（Agent 派生、等待输入等）
        """
        events = []
        method = data.get('method', '')
        timestamp = datetime.now()
        
        # 事件 1: 方法调用（主事件）
        if method:
            events.append(StateEvent(
                status=self._method_to_status(method),
                source=self.metadata.name,
                confidence=0.9,
                timestamp=timestamp,
                details={
                    'method': method,
                    'session_id': path_info['session_id'],
                    'agent_id': path_info['agent_id'],
                    'is_subagent': path_info['is_subagent']
                }
            ))
        
        # 事件 2: 内容块事件
        if method == 'content_block_start':
            block = data.get('params', {}).get('block', {})
            block_type = block.get('type', '')
            
            # 2.1: 内容块开始
            events.append(StateEvent(
                status=Status.WORKING,
                source=self.metadata.name,
                confidence=0.85,
                timestamp=timestamp,
                details={
                    'event': 'block_start',
                    'block_id': block.get('id'),
                    'block_type': block_type,
                    **path_info
                }
            ))
            
            # 2.2: 工具调用
            if block_type == 'tool_use':
                tool_name = block.get('name', '')
                
                events.append(StateEvent(
                    status=self._tool_to_status(tool_name),
                    source=self.metadata.name,
                    confidence=0.95,
                    timestamp=timestamp,
                    details={
                        'event': 'tool_start',
                        'tool': tool_name,
                        'tool_id': block.get('id'),
                        'context': self._extract_safe_context(block),
                        **path_info
                    }
                ))
                
                # 2.3: 特殊工具事件
                if tool_name == 'Task':
                    # Agent 派生
                    events.append(StateEvent(
                        status=Status.WORKING,
                        source=self.metadata.name,
                        confidence=0.95,
                        timestamp=timestamp,
                        details={
                            'event': 'agent_spawned',
                            'agent_type': block.get('input', {}).get('subagent_name', 'general'),
                            'agent_id': block.get('id'),
                            **path_info
                        }
                    ))
                
                elif tool_name == 'AskUserQuestion':
                    # 等待用户输入
                    events.append(StateEvent(
                        status=Status.IDLE,
                        source=self.metadata.name,
                        confidence=0.98,
                        timestamp=timestamp,
                        details={
                            'event': 'waiting_user',
                            'reason': 'question',
                            **path_info
                        }
                    ))
        
        # 事件 3: 内容增量更新
        elif method == 'content_block_delta':
            delta = data.get('params', {}).get('delta', {})
            
            if 'text' in delta:
                # 文本输出
                events.append(StateEvent(
                    status=Status.WORKING,
                    source=self.metadata.name,
                    confidence=0.8,
                    timestamp=timestamp,
                    details={
                        'event': 'text_output',
                        'length': len(delta['text']),
                        **path_info
                    }
                ))
        
        # 事件 4: 内容块结束
        elif method == 'content_block_stop':
            events.append(StateEvent(
                status=Status.WORKING,
                source=self.metadata.name,
                confidence=0.85,
                timestamp=timestamp,
                details={
                    'event': 'block_stop',
                    'block_id': data.get('params', {}).get('block_id'),
                    **path_info
                }
            ))
        
        # 事件 5: Token 使用
        elif method == 'usage':
            tokens = data.get('params', {})
            self._update_tokens(tokens)
            
            events.append(StateEvent(
                status=self.last_status,  # 保持当前状态
                source=self.metadata.name,
                confidence=0.7,
                timestamp=timestamp,
                details={
                    'event': 'token_usage',
                    'tokens': {
                        'input': tokens.get('input_tokens', 0),
                        'output': tokens.get('output_tokens', 0),
                        'cache_read': tokens.get('cache_read_input_tokens', 0),
                        'cache_write': tokens.get('cache_creation_input_tokens', 0)
                    },
                    **path_info
                }
            ))
        
        # 事件 6: 错误
        elif method == 'system' and data.get('subtype') == 'api_error':
            error_info = data.get('error', {}).get('error', {})
            error_type = error_info.get('type', 'unknown')
            
            # 根据错误类型决定是否生成事件
            if error_type in self.CRITICAL_ERRORS or self.show_all_errors:
                events.append(StateEvent(
                    status=Status.ERROR,
                    source=self.metadata.name,
                    confidence=0.95,
                    timestamp=timestamp,
                    details={
                        'event': 'api_error',
                        'error_type': error_type,
                        'error': error_info.get('message', 'Unknown error'),
                        **path_info
                    }
                ))
        
        return events
    
    async def _emit_event(self, event: StateEvent):
        """发送单个事件"""
        self.last_status = event.status
        await self._emit(event)
```

#### 输出示例

**之前**（一行 → 一个事件）：
```
[14:23:15] [WORKING] claude_log (90%)
```

**现在**（一行 → 多个事件）：
```
[14:23:15.000] [WORKING] claude_log (90%) - method: content_block_start
[14:23:15.001] [WORKING] claude_log (85%) - block_start: tool_use
[14:23:15.002] [EXECUTING] claude_log (95%) - tool_start: Bash
[14:23:15.003] [WORKING] claude_log (80%) - text_output: 124 chars
[14:23:15.004] [WORKING] claude_log (85%) - block_stop: abc123
[14:23:15.005] [WORKING] claude_log (70%) - token_usage: 150 tokens
```

**优势**：
- ✅ 精确时间线（毫秒级）
- ✅ 详细事件追踪
- ✅ 更好的调试体验

---

## 总结

### 四个改进点对比

| 改进点 | 优先级 | 复杂度 | 价值 | 建议 |
|-------|--------|--------|------|------|
| **子 Agent 支持** | ⭐⭐⭐⭐ | 中 | 高 | ✅ 立即实施 |
| **测试覆盖** | ⭐⭐⭐⭐⭐ | 中 | 极高 | ✅ 立即实施 |
| **会话管理** | ⭐⭐⭐ | 中 | 中 | ⏳ 下个版本 |
| **细粒度事件** | ⭐⭐ | 高 | 中 | ⏳ 按需实施 |

### 实施建议

#### Phase 1（v4.1）- 立即实施
1. ✅ **测试覆盖**（最重要）
   - 添加 `pytest`
   - 测试隐私过滤
   - 测试 Token 统计
   - 代码覆盖率 > 80%

2. ✅ **子 Agent 支持**
   - 监控 `subagents/*.jsonl`
   - 路径解析
   - Agent 派生事件

#### Phase 2（v4.2）- 下个版本
3. ✅ **会话管理**
   - `SessionManager` 类
   - 会话生命周期
   - 超时检测

#### Phase 3（v4.3）- 按需
4. ✅ **细粒度事件**
   - 一行 JSONL → 多个事件
   - 毫秒级时间戳
   - 更详细的事件类型

---

## 下一步

需要我开始实施这些改进吗？建议顺序：
1. **测试覆盖**（最重要，保证代码质量）
2. **子 Agent 支持**（功能完整性）
3. **会话管理**（数据分析）
4. **细粒度事件**（高级特性）

你想先做哪个？
