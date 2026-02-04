# -*- coding: utf-8 -*-
"""
插件框架模块 - v3.1 插件化架构

提供插件基类和通用插件实现：
- base.py: 插件基类 (BasePlugin, StateEvent, PluginMetadata)
- process.py: 通用进程监控插件

具体软件插件请使用 plugins/ 目录。
"""

from .base import (
    BasePlugin,
    PluginMetadata,
    PluginRegistry,
    PluginType,
    StateEvent,
    Status,
)

from .process import ProcessPlugin, create_process_plugin

__all__ = [
    # 框架核心
    "BasePlugin",
    "PluginMetadata",
    "PluginRegistry",
    "PluginType",
    "StateEvent",
    "Status",
    # 通用插件
    "ProcessPlugin",
    "create_process_plugin",
]
