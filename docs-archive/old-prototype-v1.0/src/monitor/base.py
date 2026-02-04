# -*- coding: utf-8 -*-
"""
状态监控器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    """状态枚举"""

    NOT_RUNNING = "not_running"
    IDLE = "idle"
    RUNNING = "running"
    READING = "reading"
    WRITING = "writing"
    THINKING = "thinking"
    EXECUTING = "executing"
    WORKING = "working"
    ERROR = "error"
    DONE = "done"


@dataclass
class MonitorResult:
    """监控结果"""

    status: Status
    confidence: float  # 0.0 - 1.0
    details: Dict
    source: str  # 来源标识


class BaseMonitor(ABC):
    """监控器基类"""

    def __init__(self, callback: Optional[Callable] = None):
        """
        Args:
            callback: 状态变化回调函数 (status: MonitorResult)
        """
        self.callback = callback
        self.current_result: Optional[MonitorResult] = None
        self.running = False

    def set_callback(self, callback: Callable):
        """设置回调函数"""
        self.callback = callback

    @abstractmethod
    def start(self):
        """开始监控"""
        pass

    @abstractmethod
    def stop(self):
        """停止监控"""
        pass

    @abstractmethod
    def get_result(self) -> MonitorResult:
        """获取当前监控结果"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查监控器是否可用"""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """检查是否正在运行"""
        pass

    def _notify(self, result: MonitorResult):
        """触发回调通知"""
        # 检查状态是否变化
        if self.current_result is None or self.current_result.status != result.status:
            self.current_result = result
            if self.callback:
                try:
                    self.callback(result)
                except Exception as e:
                    print(f"[ERROR] Monitor callback error: {e}")
