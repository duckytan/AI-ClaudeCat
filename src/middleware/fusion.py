# -*- coding: utf-8 -*-
"""
StateFusion - 状态融合
在多插件场景下，融合不同来源的状态信息
当前版本（v4.0）：单插件模式，直接透传
"""

from typing import List, Optional
from src.plugins.base import StateEvent, Status


class StateFusion:
    """状态融合器"""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.last_event: Optional[StateEvent] = None
    
    def fuse_events(self, events: List[StateEvent]) -> Optional[StateEvent]:
        """
        融合多个事件
        
        当前策略：
        - 单插件模式：直接返回第一个事件
        - 未来扩展：支持多插件加权融合
        """
        if not events:
            return None
        
        # v4.0：单插件模式，直接透传
        event = events[0]
        self.last_event = event
        return event
    
    def get_last_event(self) -> Optional[StateEvent]:
        """获取最后一个事件"""
        return self.last_event
