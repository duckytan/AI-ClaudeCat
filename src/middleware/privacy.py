# -*- coding: utf-8 -*-
"""
PrivacyFilter - 隐私过滤器

过滤级别：
- public: 完全公开（仅状态和 Token）
- internal: 内部使用（+ 工具名称、文件名）
- full: 完整信息（开发模式，无过滤）
"""

import os
from typing import Dict, Optional
from src.plugins.base import StateEvent


class PrivacyFilter:
    """隐私过滤器"""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.level = self.config.get('level', 'internal')
        self.dev_mode = self.config.get('dev_mode', False)
        self.whitelist = self.config.get('whitelist', [])
    
    def filter_event(self, event: StateEvent) -> StateEvent:
        """
        过滤事件（返回新事件）
        
        Returns:
            过滤后的 StateEvent
        """
        if not self.enabled or self.dev_mode:
            return event  # 开发模式：不过滤
        
        # 创建过滤后的详情
        filtered_details = self._filter_details(event.details)
        
        # 创建新事件
        return StateEvent(
            status=event.status,
            confidence=event.confidence,
            source=event.source,
            timestamp=event.timestamp,
            details=filtered_details
        )
    
    def _filter_details(self, details: Dict) -> Dict:
        """过滤详情字典"""
        if self.level == 'public':
            return self._filter_public(details)
        elif self.level == 'internal':
            return self._filter_internal(details)
        else:
            return details  # full: 不过滤
    
    def _filter_public(self, details: Dict) -> Dict:
        """Public 级别：仅状态和 Token"""
        return {
            'status': details.get('status'),
            'tokens': details.get('tokens', {})
        }
    
    def _filter_internal(self, details: Dict) -> Dict:
        """Internal 级别：允许元数据，不允许内容"""
        filtered = {}
        
        for key, value in details.items():
            # 使用白名单
            if self.whitelist and key not in self.whitelist:
                continue
            
            # 敏感字段：不输出
            if key in ['command', 'content', 'output', 'input']:
                continue
            
            # 文件路径：只保留文件名
            if key == 'file_path':
                filtered['file'] = os.path.basename(value)
                continue
            
            # 其他字段：保留
            filtered[key] = value
        
        return filtered
