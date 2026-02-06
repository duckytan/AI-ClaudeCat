# -*- coding: utf-8 -*-
"""
Adapters - 输出适配器系统
"""

from .base import OutputAdapter
from .websocket_adapter import WebSocketAdapter
from .http_adapter import HTTPAdapter
from .stdout_adapter import StdoutAdapter

__all__ = [
    'OutputAdapter',
    'WebSocketAdapter',
    'HTTPAdapter',
    'StdoutAdapter',
]
