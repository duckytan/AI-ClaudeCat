# -*- coding: utf-8 -*-
"""
Claude Code 插件 - 多方式状态检测

检测方式（优先级从高到低）：
1. 窗口标题（进程关联）- 实时状态
2. 进程存在性 - 存活检测
3. 文件活动 - 辅助判断
"""

import asyncio
import ctypes
import re
import sys
import os
import time

# 添加父目录到路径，支持独立运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psutil
from typing import Dict, List, Optional, Tuple

from src.plugins.base import (
    BasePlugin,
    PluginMetadata,
    PluginType,
    StateEvent,
    Status,
)


# Windows API 获取窗口进程 PID
def get_window_pid(hwnd: int) -> Optional[int]:
    """获取窗口对应的进程 PID"""
    try:
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value
    except:
        return None


def get_all_windows() -> List[Dict]:
    """获取所有窗口信息"""
    windows = []

    def enum_callback(hwnd, _):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            title_len = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if title_len > 0:
                title = ctypes.create_unicode_buffer(title_len + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, title, title_len + 1)
                pid = get_window_pid(hwnd)
                if pid:
                    windows.append(
                        {
                            "hwnd": hwnd,
                            "title": title.value,
                            "pid": pid,
                        }
                    )
        return True

    try:
        ctypes.windll.user32.EnumWindows(
            ctypes.WINFUNCTYPE(
                ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_ulong)
            )(enum_callback),
            0,
        )
    except:
        pass

    return windows


class ClaudeCodePlugin(BasePlugin):
    """Claude Code 多方式状态检测插件"""

    _metadata: PluginMetadata  # 实例变量

    # 窗口标题关键词匹配（优先级从高到低）
    TITLE_PATTERNS = [
        # 错误状态 - 最高优先级
        (r"error|错误|failed|失败", Status.ERROR, 0.95),
        # 执行状态
        (r"executing|执行|run|运行|bash|cmd", Status.EXECUTING, 0.90),
        # 工作状态
        (r"writing|写入|write|edit|编辑|save|保存", Status.WORKING, 0.85),
        # 思考状态
        (r"thinking|思考|analyzing|分析|processing|处理", Status.THINKING, 0.80),
    ]

    # Claude Code 进程特征
    PROCESS_NAMES = ["claude", "anthropic", "ollama"]

    def __init__(
        self,
        name: str = "claude_code",
        check_interval: float = 2.0,
    ):
        """
        Args:
            name: 插件名称
            check_interval: 检查间隔（秒）
        """
        super().__init__(name)
        self.check_interval = check_interval
        self._last_status: Optional[Status] = None

        # 文件活动检测
        self._last_activity_time = 0.0
        self._activity_threshold = 3.0

        self._metadata = PluginMetadata(
            name=name,
            version="2.0.0",
            author="AI-ClaudeCat",
            description="Monitor Claude Code via process + window title + file activity",
            plugin_type=PluginType.CUSTOM,
            supported_software=["Claude Code", "Claude"],
            dependencies=["psutil"],
        )

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def check_available(self) -> bool:
        """检查 Claude Code 是否可用（进程存在）"""
        return self._find_claude_processes() is not None

    async def detect(self) -> Optional[StateEvent]:
        """检测 Claude Code 状态（多方式融合）"""

        # 方式 1：窗口标题检测（通过进程 PID 关联）
        title_status, title_confidence, title_details = self._detect_by_window()

        # 方式 2：进程存在性检测
        process_status, process_confidence, process_count = self._detect_by_process()

        # 融合判断
        if title_status != Status.UNKNOWN:
            # 窗口标题检测到状态
            final_status = title_status
            final_confidence = title_confidence
            details = {"method": "window", "process_count": process_count}
            details.update(title_details)
        elif process_status == Status.STOPPED:
            # 进程不存在
            final_status = Status.STOPPED
            final_confidence = 1.0
            details = {"method": "process", "process_count": 0}
        else:
            # 进程存在但无窗口标题
            file_status, file_active = self._detect_by_file_activity()

            if file_active:
                final_status = Status.WORKING
                final_confidence = 0.75
            else:
                final_status = Status.RUNNING
                final_confidence = 0.70

            details = {
                "method": "process",
                "process_count": process_count,
                "file_active": file_active,
            }

        # 只有状态变化才返回事件
        if final_status != self._last_status:
            self._last_status = final_status

            event = StateEvent(
                status=final_status,
                confidence=final_confidence,
                source_plugin=self.name,
                source_type=PluginType.CUSTOM,
                details=details,
                priority=2,
            )

            self._emit(event)
            return event

        return None

    def _detect_by_window(self) -> Tuple[Status, float, Dict]:
        """通过窗口标题检测（进程 PID 关联）"""
        try:
            # 1. 获取 Claude Code 进程的 PID 列表
            claude_pids = set()
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    info = proc.info
                    name = info.get("name", "").lower()
                    cmdline = " ".join(info.get("cmdline") or []).lower()

                    if any(kw in name or kw in cmdline for kw in self.PROCESS_NAMES):
                        claude_pids.add(info["pid"])
                except:
                    pass

            if not claude_pids:
                return Status.UNKNOWN, 0.0, {"error": "no claude process"}

            # 2. 获取所有窗口，找到 PID 匹配的窗口
            windows = get_all_windows()

            for win in windows:
                if win["pid"] in claude_pids:
                    # 找到 Claude 相关的窗口
                    title_lower = win["title"].lower()

                    for pattern, status, confidence in self.TITLE_PATTERNS:
                        if re.search(pattern, title_lower, re.IGNORECASE):
                            return (
                                status,
                                confidence,
                                {
                                    "window_title": win["title"],
                                    "window_pid": win["pid"],
                                },
                            )

            return Status.UNKNOWN, 0.0, {"windows_found": len(windows)}

        except Exception as e:
            return Status.UNKNOWN, 0.0, {"error": str(e)}

    def _detect_by_process(self) -> Tuple[Status, float, int]:
        """通过进程存在性检测状态"""
        processes = self._find_claude_processes()

        if not processes:
            return Status.STOPPED, 1.0, 0

        return Status.RUNNING, 0.7, len(processes)

    def _detect_by_file_activity(self) -> Tuple[Status, bool]:
        """通过文件活动检测状态"""
        time_since_activity = time.time() - self._last_activity_time
        is_active = time_since_activity < self._activity_threshold

        return Status.WORKING if is_active else Status.IDLE, is_active

    def _find_claude_processes(self) -> Optional[List[psutil.Process]]:
        """查找 Claude Code 相关进程"""
        processes = []

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                info = proc.info
                name = info.get("name", "") or ""
                cmdline = info.get("cmdline") or []

                name_lower = name.lower()
                cmdline_str = " ".join(cmdline).lower()

                if any(
                    kw in name_lower or kw in cmdline_str for kw in self.PROCESS_NAMES
                ):
                    processes.append(proc)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes if processes else None

    def start(self) -> None:
        """启动监控"""
        self._running = True
        print(f"[ClaudeCodePlugin:{self.name}] Started (multi-mode detection)")

    def stop(self) -> None:
        """停止监控"""
        self._running = False
        print(f"[ClaudeCodePlugin:{self.name}] Stopped")

    def on_file_activity(self) -> None:
        """接收文件活动事件"""
        self._last_activity_time = time.time()


def create_claude_code_plugin(
    name: str = "claude_code",
    check_interval: float = 2.0,
) -> ClaudeCodePlugin:
    """创建 Claude Code 插件的便捷函数"""
    return ClaudeCodePlugin(name=name, check_interval=check_interval)
