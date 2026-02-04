# 插件框架 - v3.1

**目录**: `src/plugins/`  
**用途**: 插件框架代码（基类、通用插件）

---

## 目录结构

```
src/plugins/                    # 插件框架
├── AGENTS.md                  # 本文件
├── __init__.py                # 模块导出
├── __main__.py                # 独立运行入口
├── base.py                    # 插件基类 + 接口
├── process.py                 # 通用进程监控插件
└── window.py                  # 窗口监控插件（待实现）

plugins/                       # 具体软件插件（根目录）
├── __init__.py
├── claude_code.py             # Claude Code 插件 ✅
└── opencode.py                # OpenCode 插件（待实现）
```

---

## WHERE TO LOOK（查找指南）

| 任务 | 文件 | 说明 |
|------|------|------|
| 插件基类 | `src/plugins/base.py` | BasePlugin ABC |
| 通用进程插件 | `src/plugins/process.py` | 可复用的进程监控 |
| Claude Code 插件 | `plugins/claude_code.py` | 具体软件实现 |

---

## CONVENTIONS（规范）

### 新插件模板
```python
# -*- coding: utf-8 -*-
"""
[插件名称] - [简要描述]
"""

from src.plugins.base import BasePlugin, PluginMetadata, PluginType, StateEvent, Status

class MyPlugin(BasePlugin):
    """我的自定义插件"""

    THRESHOLDS = {...}  # 定义阈值

    def __init__(self, name: str):
        super().__init__(name)
        self._metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            author="AI-ClaudeCat",
            description="...",
            plugin_type=PluginType.CUSTOM,
            supported_software=[...],
        )

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def check_available(self) -> bool:
        ...

    async def detect(self) -> StateEvent | None:
        ...

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False
```

### 必需方法
| 方法 | 必需 | 返回值 |
|------|------|--------|
| `metadata` | ✅ | PluginMetadata |
| `check_available()` | ✅ | bool |
| `detect()` | ✅ | StateEvent \| None |
| `start()` | ✅ | None |
| `stop()` | ✅ | None |

---

## 独立运行

插件支持独立运行，方便开发和测试。

### 运行命令

```bash
# 运行 Claude Code 插件（从 plugins/ 目录加载）
python -m src.plugins.claude_code

# 运行一次并退出
python -m src.plugins.claude_code --once

# 指定检测间隔（秒）
python -m src.plugins.claude_code --interval 1.0

# 运行通用进程监控插件
python -m src.plugins.process --process-names node,python

# 显示帮助
python -m src.plugins.claude_code --help
```

### 运行效果

```
============================================================
  AI-ClaudeCat Plugin - claude_code
============================================================
  Version: 1.0.0
  Author: AI-ClaudeCat
  Description: Monitor Claude Code process status via CPU usage
  Interval: 2.0s
============================================================

按 Ctrl+C 停止...

[2024-01-01 12:00:00] 空闲 (confidence: 90%) - cpu: 0.3%, 进程: 4
[2024-01-01 12:00:02] 思考中 (confidence: 80%) - cpu: 8.5%, 进程: 4
...
```

---

## 插件清单

### 框架插件 (src/plugins/)

| 插件 | 文件 | 说明 | 状态 |
|------|------|------|------|
| ProcessPlugin | process.py | 通用进程监控 | ✅ 已完成 |
| WindowPlugin | window.py | 窗口监控 | ⏳ 待实现 |

### 具体软件插件 (plugins/)

| 插件 | 文件 | 支持软件 | 状态 |
|------|------|----------|------|
| ClaudeCodePlugin | claude_code.py | Claude Code | ✅ 已完成 |
| OpenCodePlugin | opencode.py | OpenCode | ⏳ 待实现 |
