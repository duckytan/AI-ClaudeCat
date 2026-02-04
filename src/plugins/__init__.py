# -*- coding: utf-8 -*-
"""
插件模块 - v3.1 插件化架构
"""

from .base import (
    BasePlugin,
    PluginMetadata,
    PluginRegistry,
    PluginType,
    StateEvent,
    Status,
)

from .claude_code import ClaudeCodePlugin, create_claude_code_plugin

__all__ = [
    "BasePlugin",
    "PluginMetadata",
    "PluginRegistry",
    "PluginType",
    "StateEvent",
    "Status",
    "ClaudeCodePlugin",
    "create_claude_code_plugin",
]
