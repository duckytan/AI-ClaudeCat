# -*- coding: utf-8 -*-
"""
TokenStats - Token 统计器

统计指标：
- 总使用量（input + output）
- 缓存写入/读取
- 缓存命中率
- 平均每分钟使用量
"""

from typing import Dict, Optional
from datetime import datetime
from src.plugins.base import StateEvent


class TokenStats:
    """Token 统计器"""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        
        # 累计统计（使用字典以便兼容测试）
        self.total_tokens = {
            'input': 0,
            'output': 0,
            'cache_write': 0,
            'cache_read': 0
        }
        
        # 会话统计
        self.session_start: Optional[datetime] = None
        self.session_duration: float = 0.0
    
    def update(self, event: StateEvent):
        """更新统计"""
        if not self.enabled:
            return
        
        # 提取 Token 信息
        tokens = event.details.get('tokens', {})
        if not tokens:
            return
        
        # 累计统计
        self.total_tokens['input'] += tokens.get('input', 0)
        self.total_tokens['output'] += tokens.get('output', 0)
        self.total_tokens['cache_write'] += tokens.get('cache_write', 0)
        self.total_tokens['cache_read'] += tokens.get('cache_read', 0)
        
        # 会话时间
        if self.session_start is None:
            self.session_start = event.timestamp
        else:
            self.session_duration = (event.timestamp - self.session_start).total_seconds()
    
    def get_cache_hit_rate(self) -> float:
        """
        获取缓存命中率
        
        Returns:
            缓存命中率（0.0-1.0）
        """
        total_input = self.total_tokens['input'] + self.total_tokens['cache_read']
        if total_input == 0:
            return 0.0
        return self.total_tokens['cache_read'] / total_input
    
    def get_cost_savings(self) -> float:
        """
        获取缓存节省的成本（等效 tokens）
        
        cache_read 的价格是 input 的 1/10，所以：
        节省 = cache_read * (1 - 0.1) = cache_read * 0.9
        
        Returns:
            节省的等效 token 数量
        """
        return self.total_tokens['cache_read'] * 0.9
    
    def get_tokens_per_minute(self) -> float:
        """
        获取平均每分钟 Token 使用量
        
        Returns:
            tokens/min
        """
        if self.session_duration == 0:
            return 0.0
        
        total = self.total_tokens['input'] + self.total_tokens['output']
        return total / (self.session_duration / 60)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.total_tokens['input'] + self.total_tokens['output']
        
        return {
            'total': {
                'input': self.total_tokens['input'],
                'output': self.total_tokens['output'],
                'cache_write': self.total_tokens['cache_write'],
                'cache_read': self.total_tokens['cache_read'],
                'sum': total
            },
            'cache_hit_rate': round(self.get_cache_hit_rate(), 2),
            'cost_savings': round(self.get_cost_savings(), 2),
            'tokens_per_minute': round(self.get_tokens_per_minute(), 2),
            'session_duration': round(self.session_duration, 2),
        }
    
    def reset(self):
        """重置统计"""
        self.total_tokens = {
            'input': 0,
            'output': 0,
            'cache_write': 0,
            'cache_read': 0
        }
        self.session_start = None
        self.session_duration = 0.0
