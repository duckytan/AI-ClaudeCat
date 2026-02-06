# -*- coding: utf-8 -*-
"""
文件监控器
"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, Optional, Callable
from dataclasses import dataclass

from .base import BaseMonitor, MonitorResult, Status


# Claude 相关路径
CLAUDE_PATHS = [
    os.path.expanduser("~/.claude/"),
    os.path.expanduser("~/.claude-code-router/"),
    os.path.expanduser("~/.config/claude/"),
]

# 阈值配置
THRESHOLDS = {
    "quiet": 5.0,  # 秒内无活动 = 安静
    "active": 1.0,  # 1秒内有活动 = 活跃
}

# 权重配置
WEIGHT = 0.3  # 文件监控在融合中的权重


class FileEventHandler(FileSystemEventHandler):
    """文件事件处理器"""

    def __init__(self, callback: Optional[Callable] = None):
        super().__init__()
        self.callback = callback
        self.last_event_time = 0
        self.event_count = 0
        self.events = []  # 记录最近的事件

    def on_any_event(self, event):
        if event.is_directory:
            return

        # 检查是否为 Claude 相关文件
        if not self._is_claude_file(event.src_path):
            return

        current_time = time.time()

        # 1秒内的事件合并计算
        if current_time - self.last_event_time > 1.0:
            self.event_count = 1
        else:
            self.event_count += 1

        self.last_event_time = current_time

        # 记录事件
        self.events.append(
            {"type": event.event_type, "path": event.src_path, "time": current_time}
        )

        # 只保留最近10个事件
        if len(self.events) > 10:
            self.events = self.events[-10:]

        # 触发回调
        if self.callback:
            try:
                self.callback(
                    {
                        "event_count": self.event_count,
                        "last_event": event.event_type,
                        "path": event.src_path,
                    }
                )
            except Exception as e:
                print(f"[ERROR] File event callback error: {e}")

    def _is_claude_file(self, path: str) -> bool:
        """判断是否为 Claude 相关文件"""
        path_lower = path.lower()
        indicators = [".claude", "claude", "session", "log", "tmp", "temp"]
        return any(ind in path_lower for ind in indicators)


class FileMonitor(BaseMonitor):
    """文件监控器"""

    def __init__(self, callback=None):
        super().__init__(callback)
        self.observer: Optional[Observer] = None
        self.handler: Optional[FileEventHandler] = None
        self._running = False
        self.event_count = 0
        self.last_activity_time = time.time()

    def start(self):
        """开始监控"""
        self.observer = Observer()
        self.handler = FileEventHandler(self._on_event)

        for path in CLAUDE_PATHS:
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                self.observer.schedule(self.handler, expanded, recursive=True)

        self.observer.start()
        self._running = True
        print(f"[FileMonitor] Started (watching {len(CLAUDE_PATHS)} paths)")

    def stop(self):
        """停止监控"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self._running = False
        print("[FileMonitor] Stopped")

    def is_available(self) -> bool:
        """检查是否可用"""
        for path in CLAUDE_PATHS:
            if os.path.exists(os.path.expanduser(path)):
                return True
        return False

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running

    def get_result(self) -> MonitorResult:
        """获取监控结果"""
        # 计算活动级别
        activity = self._get_activity_level()
        event_count = self.event_count

        # 重置计数器
        self.event_count = 0

        # 判断状态
        status = self._judge_status(activity, event_count)
        confidence = self._calculate_confidence(activity, event_count)

        details = {
            "activity": activity,
            "event_count": event_count,
            "last_activity": time.time() - self.last_activity_time,
        }

        result = MonitorResult(
            status=status, confidence=confidence, details=details, source="file"
        )

        self._notify(result)
        return result

    def _on_event(self, event_data: Dict):
        """事件回调"""
        self.event_count = event_data.get("event_count", 1)
        self.last_activity_time = time.time()

    def _get_activity_level(self) -> str:
        """获取活动级别"""
        time_since = time.time() - self.last_activity_time

        if time_since > THRESHOLDS["quiet"]:
            return "none"
        elif self.event_count < 3:
            return "low"
        elif self.event_count < 10:
            return "medium"
        else:
            return "high"

    def _judge_status(self, activity: str, event_count: int) -> Status:
        """根据活动判断状态"""
        if activity == "none":
            return Status.IDLE
        elif activity == "low":
            return Status.RUNNING
        elif activity == "medium":
            return Status.THINKING
        else:  # high
            return Status.WORKING

    def _calculate_confidence(self, activity: str, event_count: int) -> float:
        """计算置信度"""
        if activity == "none":
            return 0.5
        elif activity == "low":
            return 0.6
        elif activity == "medium":
            return 0.7
        else:  # high
            return 0.8

    def get_weight(self) -> float:
        """获取权重"""
        return WEIGHT


# 便捷函数
def create_file_monitor(callback=None) -> FileMonitor:
    """创建文件监控器"""
    return FileMonitor(callback)
