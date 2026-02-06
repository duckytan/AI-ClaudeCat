# -*- coding: utf-8 -*-
"""
Middleware - 中间件核心
管理插件、事件总线、状态融合、隐私过滤、Token 统计
"""

import asyncio
from typing import List, Dict, Optional
from src.plugins.base import BasePlugin, StateEvent
from .event_bus import EventBus
from .fusion import StateFusion
from .privacy import PrivacyFilter
from .token_stats import TokenStats


class Middleware:
    """中间件核心"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # 插件管理
        self.plugins: List[BasePlugin] = []
        
        # 事件总线
        self.event_bus = EventBus()
        
        # 状态融合
        fusion_config = config.get('middleware', {}).get('fusion', {})
        self.fusion = StateFusion(fusion_config)
        
        # 隐私过滤
        privacy_config = config.get('middleware', {}).get('privacy_filter', {})
        self.privacy_filter = PrivacyFilter(privacy_config)
        
        # Token 统计
        token_config = config.get('middleware', {}).get('token_stats', {})
        self.token_stats = TokenStats(token_config)
        
        # 输出适配器
        self.adapters: List = []
    
    def register_plugin(self, plugin: BasePlugin):
        """注册插件"""
        self.plugins.append(plugin)
        
        # 注册插件回调
        plugin.register_callback(self._on_plugin_event)
        
        print(f"[Middleware] Registered plugin: {plugin.metadata.name}")
    
    def register_adapter(self, adapter):
        """注册输出适配器"""
        self.adapters.append(adapter)
        print(f"[Middleware] Registered adapter: {adapter.__class__.__name__}")
    
    async def start(self):
        """启动中间件"""
        print("[Middleware] Starting...")
        
        # 启动所有插件
        for plugin in self.plugins:
            if plugin.enabled:
                await plugin.start()
        
        # 启动所有适配器
        for adapter in self.adapters:
            await adapter.start()
        
        print("[Middleware] [OK] Started")
    
    async def stop(self):
        """停止中间件"""
        print("[Middleware] Stopping...")
        
        # 停止所有插件
        for plugin in self.plugins:
            await plugin.stop()
        
        # 停止所有适配器
        for adapter in self.adapters:
            await adapter.stop()
        
        print("[Middleware] [OK] Stopped")
    
    def _on_plugin_event(self, event: StateEvent):
        """处理插件事件（同步回调）"""
        # 异步处理
        asyncio.create_task(self._process_event(event))
    
    async def _process_event(self, event: StateEvent):
        """处理事件（异步）"""
        try:
            # 1. 隐私过滤
            filtered_event = self.privacy_filter.filter_event(event)
            
            # 2. Token 统计
            self.token_stats.update(filtered_event)
            
            # 3. 状态融合
            fused_event = self.fusion.fuse_events([filtered_event])
            
            if fused_event is None:
                return
            
            # 4. 发布到事件总线
            self.event_bus.publish(fused_event)
            
            # 5. 输出到所有适配器
            for adapter in self.adapters:
                await adapter.send(fused_event)
        
        except Exception as e:
            print(f"[Middleware] Error processing event: {e}")
    
    def get_token_stats(self) -> Dict:
        """获取 Token 统计"""
        return self.token_stats.get_stats()
    
    def get_current_status(self) -> Optional[StateEvent]:
        """获取当前状态"""
        return self.fusion.get_last_event()
