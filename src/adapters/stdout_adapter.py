# -*- coding: utf-8 -*-
"""
StdoutAdapter - 标准输出适配器
用于调试和日志记录
"""

from typing import Optional, Dict
from src.plugins.base import StateEvent
from .base import OutputAdapter


class StdoutAdapter(OutputAdapter):
    """标准输出适配器"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.format = self.config.get('format', 'simple')
    
    async def start(self):
        """启动适配器"""
        if not self.enabled:
            return
        
        print("[Stdout] [OK] Started")
        self.running = True
    
    async def stop(self):
        """停止适配器"""
        print("[Stdout] [OK] Stopped")
        self.running = False
    
    async def send(self, event: StateEvent):
        """输出事件"""
        if not self.running:
            return
        
        if self.format == 'simple':
            self._print_simple(event)
        elif self.format == 'detailed':
            self._print_detailed(event)
        else:
            self._print_json(event)
    
    def _print_simple(self, event: StateEvent):
        """简单格式"""
        status = event.status.value.upper()
        source = event.source
        confidence = int(event.confidence * 100)
        timestamp = event.timestamp.strftime('%H:%M:%S')
        
        print(f"[{timestamp}] [{status}] {source} ({confidence}%)")
    
    def _print_detailed(self, event: StateEvent):
        """详细格式"""
        status = event.status.value.upper()
        source = event.source
        confidence = int(event.confidence * 100)
        timestamp = event.timestamp.strftime('%H:%M:%S')
        
        details_str = ', '.join(f"{k}={v}" for k, v in event.details.items() if k != 'tokens')
        
        print(f"[{timestamp}] [{status}] {source} ({confidence}%) - {details_str}")
    
    def _print_json(self, event: StateEvent):
        """JSON 格式"""
        print(event.to_json())
