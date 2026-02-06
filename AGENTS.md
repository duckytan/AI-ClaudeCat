# AI-ClaudeCat 项目知识库

**生成时间**: 2026-02-06  
**版本**: v4.0.0  
**状态**: 🚀 重构中（采用日志监控方案）  
**分支**: main

---

## 概述

AI-ClaudeCat 是一款 v4.0 桌面宠物应用，通过**监控 Claude Code 的官方 JSONL 日志文件**，实时追踪 AI 的运行状态、工具调用和 Token 使用情况，并通过中间件输出到多种协议（WebSocket/HTTP/SQLite）。

**核心方案**: 借鉴 [PixelHQ-bridge](https://github.com/example/pixelhq-bridge)，采用成熟的日志监控方案，替代 v3.1 的不可靠系统 API 检测。

---

## 目录结构

```
AI-ClaudeCat/
├── AGENTS.md ⭐                        # 本文件
├── README.md                           # 项目总览
├── CLAUDE.md ⭐                        # 项目详细文档
├── QUICKSTART.md                       # 快速开始指南
├── CONFIG.md                           # 配置说明
├── main.py ⭐                          # 主程序入口
├── config.json                         # 配置文件
├── requirements.txt                    # 依赖清单
│
├── docs/                               # 文档
│   └── research_notes.md               # 技术研究笔记
│
├── src/                               # 源代码
│   ├── plugins/                        # 插件实现 ⭐
│   │   ├── base.py                    # BasePlugin、StateEvent、Status
│   │   └── claude_log.py ⭐           # ClaudeLogPlugin（核心）
│   │
│   ├── middleware/ ⭐                  # 中间件核心
│   │   ├── core.py                    # Middleware 主逻辑
│   │   ├── event_bus.py               # EventBus 事件分发
│   │   ├── fusion.py                  # StateFusion 状态融合
│   │   ├── privacy.py ⭐              # PrivacyFilter 隐私过滤
│   │   └── token_stats.py ⭐          # TokenStats Token 统计
│   │
│   ├── adapters/ ⭐                    # 输出适配器
│   │   ├── base.py                    # OutputAdapter 基类
│   │   ├── websocket_adapter.py       # WebSocket 实时推送
│   │   ├── http_adapter.py            # HTTP REST API
│   │   ├── stdout_adapter.py          # 标准输出调试
│   │   └── history_adapter.py ⭐      # SQLite 历史存储
│   │
│   └── utils/                          # 工具模块
│       ├── window_detector.py          # 窗口检测（保留，暂不实装）
│       └── README.md                   # 工具说明
│
├── data/                               # 数据目录
│   └── history.db                      # 事件历史数据库
│
└── backup-v3.1/                       # v3.1 备份
    ├── src/                           # 旧插件代码
    │   ├── claude_code.py             # 旧融合检测插件
    │   ├── process.py                 # CPU 阈值检测
    │   └── window.py                  # 窗口标题检测
    ├── docs/                          # 旧文档
    │   ├── 完整架构设计.md             # v3.0 架构
    │   ├── 插件化架构详细设计.md       # v3.1 插件设计
    │   ├── PixelHQ-vs-ClaudeCat对比分析.md
    │   ├── 重构方案-借鉴PixelHQ.md
    │   └── 重构任务清单.md
    ├── Desktop-Pixel-Pet/             # 其他项目备份
    └── PixelHQ-bridge/                # 参考项目备份
```

---

## WHERE TO LOOK（查找指南）

| Task | Location | Notes |
|------|----------|-------|
| **启动应用** | `python main.py` | 主程序入口 |
| **配置应用** | `config.json` | 配置文件 |
| **项目文档** | `CLAUDE.md` | 完整项目文档 |
| **快速开始** | `QUICKSTART.md` | 新手指南 |
| **核心插件** | `src/plugins/claude_log.py` ⭐ | 日志监控插件 |
| **插件基类** | `src/plugins/base.py` | BasePlugin、StateEvent、Status |
| **中间件核心** | `src/middleware/core.py` | 插件管理、事件总线、融合 |
| **隐私过滤** | `src/middleware/privacy.py` ⭐ | 白名单过滤 |
| **Token 统计** | `src/middleware/token_stats.py` ⭐ | 使用量统计 |
| **输出适配器** | `src/adapters/` | WebSocket, HTTP, Stdout, History |
| **工具模块** | `src/utils/window_detector.py` | 窗口检测（保留，暂不实装）|
| **旧代码备份** | `backup-v3.1/` | v3.1 代码和文档 |
| **依赖安装** | `pip install -r requirements.txt` | watchdog, websockets, flask |

---

## CODE MAP（代码地图）

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `BasePlugin` | ABC | base.py | 1 | 插件基类 |
| `ClaudeLogPlugin` ⭐ | Class | claude_log.py | 1 | 日志监控插件（核心）|
| `Middleware` | Class | middleware/core.py | 1 | 中间件核心 |
| `EventBus` | Class | middleware/event_bus.py | 1 | 事件分发 |
| `StateFusion` | Class | middleware/fusion.py | 1 | 状态融合 |
| `PrivacyFilter` ⭐ | Class | middleware/privacy.py | 1 | 隐私过滤器 |
| `TokenStats` ⭐ | Class | middleware/token_stats.py | 1 | Token 统计器 |
| `OutputAdapter` | ABC | adapters/base.py | 4 | 适配器基类 |
| `WebSocketAdapter` | Class | adapters/websocket_adapter.py | 1 | WebSocket 推送 |
| `HTTPAdapter` | Class | adapters/http_adapter.py | 1 | HTTP REST API |
| `HistoryAdapter` ⭐ | Class | adapters/history_adapter.py | 1 | SQLite 存储 |
| `StateEvent` | Dataclass | base.py | 10+ | 状态事件（可序列化）|
| `Status` | Enum | base.py | 10+ | 状态枚举（8 种状态）|
| `PluginType` | Enum | base.py | 5 | 插件类型 |
| `PluginMetadata` | Dataclass | base.py | 5 | 插件元信息 |
| `WindowDetector` | Class | utils/window_detector.py | 0 | 窗口检测工具（保留）|

---

## CONVENTIONS（规范）

### Python

#### 编码规范
```python
# 文件头（必须）
# -*- coding: utf-8 -*-
"""
[模块名称] - [简要描述]
"""

# 导入顺序
import standard_library  # 标准库
import third_party       # 第三方库
from src.module import X # 项目模块
```

#### 类型注解
```python
from typing import Dict, List, Optional, Protocol

def function(param: str) -> Optional[Dict]:
    pass
```

#### 异步编程
```python
async def detect(self) -> Optional[StateEvent]:
    await asyncio.sleep(1)
    return event
```

#### 数据类
```python
from dataclasses import dataclass, field

@dataclass
class StateEvent:
    status: Status
    confidence: float
    details: Dict = field(default_factory=dict)
```

#### 枚举
```python
from enum import Enum

class Status(Enum):
    IDLE = "idle"
    WORKING = "working"
```

### 注释

- **文档字符串**: 使用中文
- **代码注释**: 中英文均可
- **关键逻辑**: 必须注释

```python
class ClaudeLogPlugin(BasePlugin):
    """
    Claude Code 日志监控插件
    
    功能：
    1. 监控 ~/.claude/projects/**/*.jsonl
    2. 增量读取新行
    3. 解析 JSONL 事件
    4. 推断状态（thinking/tool_use）
    """
    
    def _read_new_lines(self, file_path: str, start: int) -> List[str]:
        """
        增量读取新行
        
        Args:
            file_path: 文件路径
            start: 起始位置
        
        Returns:
            新增的行列表
        """
        # 实现...
```

### Linting

- **工具**: ruff（已配置）
- **配置**: 待创建 `pyproject.toml`

---

## ANTI-PATTERNS（反模式）

本项目禁止的代码模式：

1. **❌ 类型抑制** - 不使用 `# type: ignore`、`as any`
2. **❌ 空异常捕获** - 禁止 `except Exception: pass`
3. **❌ 自动提交** - 除非用户明确要求，否则不提交代码
4. **❌ 猜测代码** - 不要猜测未读取文件的内容
5. **❌ 破坏性修改** - 失败时必须保持代码可运行
6. **❌ 硬编码路径** - 使用配置或自动检测
7. **❌ 随意设定阈值** - 必须有数据支撑或参考
8. **❌ 重复代码** - 提取公共逻辑到工具函数

---

## UNIQUE STYLES（独特风格）

### 1. 事件驱动架构

```python
# 插件通过回调发送事件
plugin.register_callback(callback)
plugin._emit(event)  # 内部发送到所有回调

# 中间件监听插件事件
def _on_plugin_event(self, event: StateEvent):
    # 处理事件
    for adapter in self.adapters:
        await adapter.send(event)
```

### 2. 可序列化事件

```python
# 转换为字典（JSON）
event_dict = event.to_dict()
# {"status": "working", "confidence": 0.95, ...}

# 从字典重建
event = StateEvent.from_dict(event_dict)
```

### 3. 增量读取机制

```python
# 记录每个文件的读取位置
self.file_positions: Dict[str, int] = {}

# 增量读取
last_position = self.file_positions.get(file_path, 0)
new_lines = self._read_new_lines(file_path, last_position)
self.file_positions[file_path] = current_size
```

### 4. 状态推断映射

```python
# 工具名称 → 状态映射
tool_status_map = {
    'Read': Status.WORKING,
    'Write': Status.WORKING,
    'Bash': Status.EXECUTING,
    'Task': Status.WORKING,
}

status = tool_status_map.get(tool_name, Status.WORKING)
```

### 5. 隐私保护白名单

```python
# 只输出允许的字段
whitelist = [
    'method', 'event', 'tool', 'context',
    'session_id', 'status', 'confidence',
    'tokens', 'agent_type', 'pattern'
]

# 过滤敏感信息
if key in ['command', 'content', 'output']:
    # 不输出
    pass
elif key == 'file_path':
    # 只保留文件名
    filtered[key] = os.path.basename(value)
```

### 6. 插件元信息模式

```python
@property
def metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="claude_log",
        version="1.0.0",
        author="AI-ClaudeCat",
        plugin_type=PluginType.CUSTOM,
        supported_software=["Claude Code"],
        dependencies=["watchdog"],
    )
```

---

## v4.0 核心改动

### ✅ 新增

1. **ClaudeLogPlugin** (`src/plugins/claude_log.py`)
   - 监控 `~/.claude/projects/**/*.jsonl`
   - 增量读取（`file_positions`）
   - JSONL 解析（`json.loads`）
   - 状态推断（`_tool_to_status`）
   - Token 统计（`_update_tokens`）

2. **PrivacyFilter** (`src/middleware/privacy.py`)
   - 白名单过滤（只输出元数据）
   - 文件路径 → 文件名
   - 命令/内容 → 不输出

3. **TokenStats** (`src/middleware/token_stats.py`)
   - Token 累计统计
   - 缓存命中率
   - 平均每分钟使用量

4. **HistoryAdapter** (`src/adapters/history_adapter.py`)
   - SQLite 数据库存储
   - 时间范围查询
   - 统计分析接口

### ❌ 移除（归档到 `backup-v3.1/`）

1. **WindowPlugin** (`src/plugins/window.py`)
   - 窗口标题检测（无效，窗口标题不包含状态）
   - **保留为工具**: `src/utils/window_detector.py`（未来可能用于自动发现进程）

2. **ProcessPlugin** (`src/plugins/process.py`)
   - CPU 阈值判断（不准确，易误判）

3. **ClaudeCodePlugin** (`src/apps/claude_code.py`)
   - 多方式融合检测（窗口+进程+文件，不可靠）

### 📝 更新

1. **Middleware** (`src/middleware/core.py`)
   - 集成 `PrivacyFilter`
   - 集成 `TokenStats`
   - 简化 `StateFusion`（单插件模式）

2. **Config** (`config.json`)
   - 新增 `claude` 配置项
   - 新增 `privacy_filter` 配置
   - 新增 `token_stats` 配置

3. **Dependencies** (`requirements.txt`)
   - 新增 `watchdog`（文件监控）

---

## 数据流

### v4.0 完整数据流

```
Claude Code 写入日志
    │
    ▼
~/.claude/projects/my-app/session-abc123.jsonl
    │
    ▼
Watchdog 监控文件变化
    │ on_modified(event)
    ▼
ClaudeLogPlugin._handle_file_change()
    │
    ├─► 获取文件大小
    ├─► 获取上次读取位置（file_positions）
    ├─► 增量读取新行
    └─► 更新读取位置
           │
           ▼
    for line in new_lines:
        _handle_new_line(line)
           │
           ├─► json.loads(line)  # 解析 JSON
           ├─► 检查事件类型（assistant/user/summary）
           ├─► 提取工具调用（tool_use）
           ├─► 推断状态（_tool_to_status）
           ├─► 提取安全上下文（_extract_safe_context）
           ├─► 更新 Token 统计（_update_tokens）
           └─► _update_status() → emit(StateEvent)
                   │
                   ▼
Middleware._on_plugin_event(event)
                   │
                   ├─► PrivacyFilter.filter_event(event)
                   ├─► TokenStats.update(event)
                   └─► StateFusion.fuse_events([event])
                           │
                           ▼
                   for adapter in adapters:
                       await adapter.send(event)
                           │
                           ├─► WebSocketAdapter → 广播到所有客户端
                           ├─► HTTPAdapter → 更新当前状态缓存
                           ├─► StdoutAdapter → 打印到终端
                           └─► HistoryAdapter → 插入 SQLite
```

---

## Status 枚举（8 种状态）

```python
class Status(Enum):
    UNKNOWN = "unknown"      # 未知状态
    IDLE = "idle"            # 空闲（等待用户输入）
    RUNNING = "running"      # 运行中（AI 接收到提示词）
    THINKING = "thinking"    # 思考中（AI 内部推理）
    WORKING = "working"      # 工作中（读/写文件、搜索）
    EXECUTING = "executing"  # 执行中（运行 Bash 命令）
    ERROR = "error"          # 错误（工具调用失败）
    STOPPED = "stopped"      # 停止（进程关闭）
```

### 状态转换

```
UNKNOWN → RUNNING → THINKING → WORKING → IDLE
                         ↓
                    EXECUTING → IDLE
                         ↓
                      ERROR → IDLE
```

---

## 工具映射表

| 工具名称 | 状态 | 描述 |
|---------|------|------|
| `thinking` | THINKING | AI 思考中 |
| `text` | WORKING | AI 回复文本 |
| `Read` | WORKING | 读取文件 |
| `Write` | WORKING | 写入文件 |
| `Edit` | WORKING | 编辑文件 |
| `Bash` | EXECUTING | 执行命令 |
| `Grep` | WORKING | 搜索代码 |
| `Glob` | WORKING | 文件匹配 |
| `WebFetch` | WORKING | 网络请求 |
| `WebSearch` | WORKING | 网络搜索 |
| `Task` | WORKING | 派生子 Agent |
| `TodoWrite` | WORKING | 写入待办事项 |
| `AskUserQuestion` | IDLE | 等待用户输入 |

---

## 配置示例

### 最小配置

```json
{
  "version": "4.0.0",
  "claude": {
    "projects_dir": "auto"
  }
}
```

### 完整配置

```json
{
  "version": "4.0.0",
  "description": "AI-ClaudeCat configuration (v4.0)",
  
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

## 依赖清单

```
watchdog>=3.0.0       # 文件监控
websockets>=12.0      # WebSocket 服务器
flask>=3.0.0          # HTTP 服务器
flask-cors>=4.0.0     # CORS 支持
psutil>=5.9.0         # 进程监控（可选）
```

---

## 快速命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py

# 测试 WebSocket
# （在浏览器控制台）
ws = new WebSocket('ws://127.0.0.1:8765');
ws.onmessage = (e) => console.log(JSON.parse(e.data));

# 查询当前状态
curl http://127.0.0.1:8080/api/status

# 查询历史事件
curl http://127.0.0.1:8080/api/history?limit=10

# 查询 Token 统计
curl http://127.0.0.1:8080/api/tokens
```

---

## NOTES

- **语言**: 中文文档，中英文代码/注释
- **状态**: 🚀 v4.0 重构中
- **依赖**: requirements.txt（watchdog, websockets, flask, flask-cors）
- **v3.1 已归档**: 旧代码在 `backup-v3.1/` 目录
- **插件发现**: 使用 `PluginRegistry` 单例管理插件
- **运行**: `python main.py` 启动应用
- **API**: WebSocket (ws://127.0.0.1:8765), HTTP (http://127.0.0.1:8080)
- **数据库**: SQLite (`data/history.db`)

---

## 参考资料

- [PixelHQ-bridge](https://github.com/example/pixelhq-bridge) - 日志监控方案参考
- [Claude Code 官方文档](https://docs.anthropic.com/claude/code) - Claude Code 使用指南
- [Watchdog 文档](https://python-watchdog.readthedocs.io/) - 文件监控库
- [WebSocket 协议](https://datatracker.ietf.org/doc/html/rfc6455) - WebSocket 标准

---

**最后更新**: 2026-02-06  
**版本**: v4.0.0  
**分支**: main
