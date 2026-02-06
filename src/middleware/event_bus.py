# -*- coding: utf-8 -*-
"""
EventBus - 事件总线
简单的订阅/发布模式
"""

from typing import Callable, List, Dict
from src.plugins.base import StateEvent


class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.subscribers: List[Callable[[StateEvent], None]] = []
    
    def subscribe(self, callback: Callable[[StateEvent], None]):
        """订阅事件"""
        self.subscribers.append(callback)
    
    def publish(self, event: StateEvent):
        """发布事件"""
        for callback in self.subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"[EventBus] Subscriber error: {e}")
    
    def clear(self):
        """清空订阅者"""
        self.subscribers.clear()
