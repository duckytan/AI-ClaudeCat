# -*- coding: utf-8 -*-
"""
OutputAdapter - 输出适配器基类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
from src.plugins.base import StateEvent


class OutputAdapter(ABC):
    """输出适配器基类"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.running = False
    
    @abstractmethod
    async def start(self):
        """启动适配器"""
        pass
    
    @abstractmethod
    async def stop(self):
        """停止适配器"""
        pass
    
    @abstractmethod
    async def send(self, event: StateEvent):
        """发送事件"""
        pass
