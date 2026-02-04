# -*- coding: utf-8 -*-
"""
具体软件插件目录

存放针对特定软件的监控插件：
- Claude Code: claude_code.py
- OpenCode: opencode.py
"""

from .claude_code import ClaudeCodePlugin, create_claude_code_plugin

__all__ = [
    "ClaudeCodePlugin",
    "create_claude_code_plugin",
]
