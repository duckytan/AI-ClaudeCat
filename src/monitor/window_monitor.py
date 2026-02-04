# -*- coding: utf-8 -*-
"""
窗口监控器
"""

import os
import re
from typing import Dict, Optional, Callable
from dataclasses import dataclass

from .base import BaseMonitor, MonitorResult, Status


# 关键词配置
KEYWORD_PATTERNS = {
    Status.THINKING: [
        r"thinking",
        r"思考",
        r"analyz",
        r"processing",
    ],
    Status.READING: [
        r"read",
        r"reading",
        r"打开",
        r"open",
        r"load",
    ],
    Status.WRITING: [
        r"edit",
        r"writing",
        r"write",
        r"modif",
        r"save",
        r"保存",
        r"写入",
    ],
    Status.EXECUTING: [
        r"bash",
        r"execute",
        r"run",
        r"npm ",
        r"pip ",
        r"python ",
        r"cmd",
        r"shell",
    ],
    Status.DONE: [
        r"done",
        r"complete",
        r"finished",
        r"success",
        r"完成",
        r"成功",
    ],
    Status.ERROR: [
        r"error",
        r"fail",
        r"exception",
        r"错误",
        r"失败",
        r"异常",
    ],
}

# 权重配置
WEIGHT = 0.2  # 窗口监控在融合中的权重


class WindowMonitor(BaseMonitor):
    """窗口监控器"""

    def __init__(self, callback=None):
        super().__init__(callback)
        self._running = False
        self._last_title = ""
        self._window_found = False

    def start(self):
        """开始监控"""
        self._running = True
        print("[WindowMonitor] Started")

    def stop(self):
        """停止监控"""
        self._running = False
        print("[WindowMonitor] Stopped")

    def is_available(self) -> bool:
        """检查是否可用"""
        try:
            import pygetwindow

            windows = pygetwindow.getAllTitles()
            return any("claude" in w.lower() for w in windows)
        except Exception as e:
            print(f"[WindowMonitor] Not available: {e}")
            return False

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running

    def get_result(self) -> MonitorResult:
        """获取监控结果"""
        try:
            import pygetwindow

            # 获取所有窗口
            all_windows = pygetwindow.getAllTitles()

            # 查找 Claude 窗口
            claude_windows = [w for w in all_windows if "claude" in w.lower()]

            if not claude_windows:
                return MonitorResult(
                    status=Status.NOT_RUNNING,
                    confidence=0.8,
                    details={"windows": []},
                    source="window",
                )

            # 分析最近窗口
            current_title = claude_windows[0]
            self._window_found = True

            # 关键词匹配
            status, matched_keyword = self._analyze_title(current_title)
            confidence = self._calculate_confidence(status, current_title)

            details = {
                "title": current_title,
                "windows": claude_windows,
                "matched_keyword": matched_keyword,
            }

            result = MonitorResult(
                status=status, confidence=confidence, details=details, source="window"
            )

            self._notify(result)
            return result

        except ImportError:
            print("[WindowMonitor] pygetwindow not installed")
            return MonitorResult(
                status=Status.IDLE,
                confidence=0.0,
                details={"error": "pygetwindow not installed"},
                source="window",
            )
        except Exception as e:
            print(f"[WindowMonitor] Error: {e}")
            return MonitorResult(
                status=Status.IDLE,
                confidence=0.0,
                details={"error": str(e)},
                source="window",
            )

    def _analyze_title(self, title: str) -> tuple:
        """
        分析窗口标题

        Returns:
            (status, matched_keyword)
        """
        title_lower = title.lower()

        # 按优先级检查（从高到低）
        priority_order = [
            Status.ERROR,
            Status.DONE,
            Status.EXECUTING,
            Status.WRITING,
            Status.READING,
            Status.THINKING,
        ]

        for status in priority_order:
            keywords = KEYWORD_PATTERNS.get(status, [])
            for keyword in keywords:
                if re.search(keyword, title_lower, re.IGNORECASE):
                    return status, keyword

        # 默认状态
        if "claude" in title_lower:
            return Status.RUNNING, None

        return Status.IDLE, None

    def _calculate_confidence(self, status: Status, title: str) -> float:
        """计算置信度"""
        if status == Status.ERROR or status == Status.DONE:
            return 0.95  # 这些状态很明确
        elif status == Status.EXECUTING:
            return 0.9
        elif status == Status.WRITING or status == Status.READING:
            return 0.85
        elif status == Status.THINKING:
            return 0.8
        elif status == Status.RUNNING:
            return 0.7
        else:  # IDLE
            return 0.6

    def get_weight(self) -> float:
        """获取权重"""
        return WEIGHT


# 便捷函数
def create_window_monitor(callback=None) -> WindowMonitor:
    """创建窗口监控器"""
    return WindowMonitor(callback)
