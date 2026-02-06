# -*- coding: utf-8 -*-
"""
窗口监控插件 - 基于窗口标题/文本监控状态
"""

import asyncio
import ctypes
import re
from typing import Dict, List, Optional, Pattern, Tuple

from .base import (
    BasePlugin,
    PluginMetadata,
    PluginType,
    StateEvent,
    Status,
)


def get_all_windows() -> List[Dict]:
    """
    获取所有可见窗口信息

    Returns:
        窗口列表: [{"hwnd": int, "title": str, "pid": int}, ...]
    """
    windows = []

    def enum_callback(hwnd, _):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            title_len = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if title_len > 0:
                title = ctypes.create_unicode_buffer(title_len + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, title, title_len + 1)

                # 获取窗口进程 PID
                pid = ctypes.c_ulong()
                ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

                windows.append(
                    {
                        "hwnd": hwnd,
                        "title": title.value,
                        "pid": pid.value,
                    }
                )
        return True

    try:
        ctypes.windll.user32.EnumWindows(
            ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_ulong))(
                enum_callback
            ),
            0,
        )
    except Exception as e:
        print(f"[WindowPlugin] Error enumerating windows: {e}")

    return windows


class WindowPlugin(BasePlugin):
    """窗口监控插件 - 通过窗口标题/文本检测状态"""

    def __init__(
        self,
        name: str,
        window_titles: List[str],
        status_patterns: Optional[Dict[Status, List[str]]] = None,
        check_interval: float = 2.0,
    ):
        """
        Args:
            name: 插件名称
            window_titles: 窗口标题关键词列表（用于匹配窗口）
            status_patterns: 状态匹配模式 {状态: [正则表达式列表]}
            check_interval: 检查间隔（秒）
        """
        super().__init__(name)
        self.window_titles = [title.lower() for title in window_titles]
        self.check_interval = check_interval
        self._last_status: Optional[Status] = None

        # 状态匹配模式（默认）
        self.status_patterns = status_patterns or {
            Status.ERROR: [r"error|错误|failed|失败|exception"],
            Status.EXECUTING: [r"executing|执行|bash|cmd|npm|pip|running"],
            Status.WORKING: [r"writing|写入|write|edit|编辑|save|保存"],
            Status.THINKING: [r"thinking|思考|analyzing|分析|processing|处理"],
        }

        self._metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            author="AI-ClaudeCat",
            description=f"Monitor window title for {', '.join(window_titles)}",
            plugin_type=PluginType.WINDOW,
            supported_software=window_titles,
        )

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def check_available(self) -> bool:
        """检查目标窗口是否存在"""
        return self._find_matching_windows() is not None

    async def detect(self) -> Optional[StateEvent]:
        """检测窗口状态"""
        matched_windows = self._find_matching_windows()

        if not matched_windows:
            status = Status.STOPPED
            confidence = 1.0
            details = {"matched_windows": 0}
        else:
            # 分析第一个匹配的窗口标题
            primary_window = matched_windows[0]
            status = self._analyze_title(primary_window["title"])
            confidence = self._calculate_confidence(status)

            details = {
                "matched_windows": len(matched_windows),
                "primary_window": primary_window["title"],
            }

        # 只有状态变化才返回事件
        if status != self._last_status:
            self._last_status = status

            event = StateEvent(
                status=status,
                confidence=confidence,
                source_plugin=self.name,
                source_type=PluginType.WINDOW,
                details=details,
                priority=2,  # 窗口监控优先级
            )

            self._emit(event)
            return event

        return None

    def _find_matching_windows(self) -> Optional[List[Dict]]:
        """查找匹配的窗口"""
        all_windows = get_all_windows()
        matched = []

        for window in all_windows:
            title_lower = window["title"].lower()
            # 检查是否包含关键词
            if any(keyword in title_lower for keyword in self.window_titles):
                matched.append(window)

        return matched if matched else None

    def _analyze_title(self, title: str) -> Status:
        """
        分析窗口标题推断状态

        Args:
            title: 窗口标题

        Returns:
            推断的状态
        """
        title_lower = title.lower()

        # 按优先级检查（错误 > 执行 > 工作 > 思考）
        priority_order = [
            Status.ERROR,
            Status.EXECUTING,
            Status.WORKING,
            Status.THINKING,
        ]

        for status in priority_order:
            patterns = self.status_patterns.get(status, [])
            for pattern in patterns:
                if re.search(pattern, title_lower, re.IGNORECASE):
                    return status

        # 默认运行中
        return Status.RUNNING

    def _calculate_confidence(self, status: Status) -> float:
        """计算置信度"""
        confidence_map = {
            Status.ERROR: 0.95,
            Status.EXECUTING: 0.90,
            Status.WORKING: 0.85,
            Status.THINKING: 0.80,
            Status.RUNNING: 0.70,
            Status.STOPPED: 1.0,
        }
        return confidence_map.get(status, 0.5)

    def start(self) -> None:
        """启动监控"""
        self._running = True
        print(f"[WindowPlugin:{self.name}] Started")

    def stop(self) -> None:
        """停止监控"""
        self._running = False
        print(f"[WindowPlugin:{self.name}] Stopped")


def create_window_plugin(
    name: str,
    window_titles: List[str],
    status_patterns: Optional[Dict[Status, List[str]]] = None,
    check_interval: float = 2.0,
) -> WindowPlugin:
    """创建窗口监控插件的便捷函数"""
    return WindowPlugin(
        name=name,
        window_titles=window_titles,
        status_patterns=status_patterns,
        check_interval=check_interval,
    )
