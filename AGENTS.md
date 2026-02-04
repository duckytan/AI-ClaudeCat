# 项目知识库

**生成时间**: 2026-02-04 19:55  
**提交**: a06ff6f (docs: archive v1.0 prototype with experience summary)  
**分支**: main

---

## 概述

AI-ClaudeCat 是一款 v3.1 桌面宠物应用，通过插件化架构监控 AI 编程工具（Claude Code、OpenCode、Cursor）的运行状态，并通过中间件（WebSocket/HTTP/Redis）输出状态。

---

## 目录结构

```
AI-ClaudeCat/
├── AGENTS.md                           # 本文件 ⭐
├── CLAUDE.md                           # 主项目文档（中文）
├── docs/                               # 架构文档
│   ├── 完整架构设计.md                 # v3.0 总体架构
│   ├── 插件化架构详细设计.md           # v3.1 插件设计
│   └── research_notes.md               # 技术研究笔记
├── scripts/                            # 工具/调试脚本
├── src/
│   ├── plugins/                        # 插件实现
│   │   ├── base.py                    # BasePlugin、StateEvent、Status
│   │   └── process.py                 # ProcessPlugin（CPU 监控）
│   ├── middleware/                     # 待实现
│   │   ├── core.py
│   │   ├── event_bus.py
│   │   └── fusion.py
│   └── adapters/                       # 输出适配器（待实现）
│       ├── websocket.py
│       ├── http.py
│       └── redis.py
└── docs-archive/old-prototype-v1.0/   # 已归档 v1.0 原型 + 经验总结
```

---

## WHERE TO LOOK（查找指南）

| Task | Location | Notes |
|------|----------|-------|
| Plugin development | `src/plugins/` | Extend BasePlugin |
| Core interfaces | `src/plugins/base.py` | BasePlugin、StateEvent、PluginMetadata |
| Process monitoring | `src/plugins/process.py` | ProcessPlugin with CPU thresholds |
| Architecture docs | `docs/插件化架构详细设计.md` | Complete v3.1 spec |
| Migration notes | `docs-archive/old-prototype-v1.0/EXPERIENCE_SUMMARY.md` | v1.0 lessons |
| Debug scripts | `scripts/` | test_fusion.py、monitor_opencode.py |

---

## CODE MAP（代码地图）

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `BasePlugin` | ABC | base.py | 2 | Plugin interface |
| `ProcessPlugin` | Class | process.py | 1 | CPU monitoring |
| `StateEvent` | Dataclass | base.py | 2 | Status event with serialization |
| `Status` | Enum | base.py | 3 | State enum (unknown/idle/running/thinking/working/executing/error/stopped) |
| `PluginType` | Enum | base.py | 2 | Plugin classification |
| `PluginMetadata` | Dataclass | base.py | 1 | Plugin info |
| `PluginRegistry` | Class | base.py | 0 | Plugin singleton registry |

---

## CONVENTIONS（规范）

### Python
- **Encoding**: `# -*- coding: utf-8 -*-` mandatory header
- **Type hints**: Full typing (Dict, List, Optional, Protocol)
- **Async**: Use `async def` and `await` (see process.py)
- **Dataclasses**: `@dataclass` for data containers
- **Enums**: Use Enum for type-safe constants

### File Headers
```python
# -*- coding: utf-8 -*-
"""
[Module name] - [Brief description]
"""
```

### Comments
- Chinese comments throughout (project language)
- Class/docstring in Chinese
- Code comments in English or Chinese

### Linting
- **Tool**: ruff (configured, `.ruff_cache/` exists)
- **No config file**: pyproject.toml not yet created

---

## ANTI-PATTERNS (THIS PROJECT)

1. **No `as any` or type suppression** - Never use `as any`, `@ts-ignore`
2. **No empty catch blocks** - `except Exception as e: pass` forbidden
3. **No commit without explicit request** - Never auto-commit
4. **No speculative code** - Don't guess about unread files
5. **No breaking state on failure** - Always leave code working

---

## UNIQUE STYLES（独特风格）

### Event-Driven Architecture（事件驱动架构）
```python
# Plugins emit StateEvent via callbacks
plugin.register_callback(callback)
plugin._emit(event)  # Internal emit to all callbacks
```

### Serializable Events（可序列化事件）
```python
event.to_dict()  # {"status": "running", "confidence": 0.85, ...}
StateEvent.from_dict(data)  # Reconstruction
```

### Status Thresholds (CPU %)（状态阈值）
```python
THRESHOLDS = {
    "idle": 0.5,      # < 0.5%
    "running": 3.0,   # < 3%
    "thinking": 15.0, # < 15%
    "working": 50.0,   # < 50%
}
```

### Plugin Metadata Pattern（插件元信息模式）
```python
class ProcessPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.name,
            version="1.0.0",
            plugin_type=PluginType.PROCESS,
            ...
        )
```

---

## COMMANDS（命令）

```bash
# 运行状态测试
python scripts/test_fusion.py

# 测试 OpenCode 监控
python scripts/monitor_opencode.py

# 查看迁移经验总结
cat docs-archive/old-prototype-v1.0/EXPERIENCE_SUMMARY.md
```

---

## NOTES

- **Language**: Chinese documentation, English code/comments
- **State**: v3.1 core implementation in progress (plugins done, middleware pending)
- **No dependencies yet**: requirements.txt not created (new project)
- **v1.0 archived**: Old prototype in `docs-archive/old-prototype-v1.0/` with experience summary
- **Plugin discovery**: Uses `PluginRegistry` singleton for plugin management
