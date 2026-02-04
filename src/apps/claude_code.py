# -*- coding: utf-8 -*-
"""
Claude Code 插件 - 多方式状态检测

检测方式（优先级从高到低）：
1. 窗口标题 - 实时状态（thinking/writing/executing/error）
2. 进程存在性 - 存活检测（running/stopped）
3. 文件活动 - 辅助判断（idle/working）
"""

import asyncio
import re
import sys
import os

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


class ClaudeCodePlugin(BasePlugin):
    """Claude Code 多方式状态检测插件"""

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
        self._activity_threshold = 3.0  # 3秒内有活动视为非空闲

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

        # 方式 1：窗口标题检测（最高优先级）
        title_status, title_confidence, title_details = self._detect_by_window()

        # 方式 2：进程存在性检测
        process_status, process_confidence, process_count = self._detect_by_process()

        # 融合判断
        if title_status != Status.UNKNOWN:
            # 窗口标题检测到状态，使用窗口标题
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
            # 进程存在但无窗口标题，使用进程状态 + 文件活动辅助
            file_status, file_active = self._detect_by_file_activity()

            if file_active:
                # 有文件活动，视为 working
                final_status = Status.WORKING
                final_confidence = 0.75
            else:
                # 无文件活动，根据进程状态判断
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
        """通过窗口标题检测状态"""
        try:
            import pygetwindow

            # 获取所有窗口标题
            all_titles = pygetwindow.getAllTitles()

            # 查找 Claude 相关窗口
            for title in all_titles:
                title_lower = title.lower()

                # 检查是否包含 Claude 关键词
                if any(kw in title_lower for kw in ["claude", "anthropic", "ollama"]):
                    # 匹配状态模式
                    for pattern, status, confidence in self.TITLE_PATTERNS:
                        if re.search(pattern, title_lower, re.IGNORECASE):
                            return status, confidence, {"window_title": title}

            return Status.UNKNOWN, 0.0, {}

        except ImportError:
            # pygetwindow 未安装，跳过窗口检测
            return Status.UNKNOWN, 0.0, {"error": "pygetwindow not installed"}
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
        import time

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

                # 匹配 Claude Code 特征
                if any(
                    kw in name_lower or kw in cmdline_str for kw in self.PROCESS_NAMES
                ):
                    processes.append(proc)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes if processes else None

    def _get_cpu_usage(self, processes: List[psutil.Process]) -> float:
        """计算总 CPU 占用"""
        total_cpu = 0.0

        for p in processes:
            try:
                total_cpu += p.cpu_percent(interval=0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return total_cpu

    def start(self) -> None:
        """启动监控"""
        self._running = True
        print(f"[ClaudeCodePlugin:{self.name}] Started (multi-mode detection)")

    def stop(self) -> None:
        """停止监控"""
        self._running = False
        print(f"[ClaudeCodePlugin:{self.name}] Stopped")

    def on_file_activity(self) -> None:
        """接收文件活动事件（外部调用）"""
        import time

        self._last_activity_time = time.time()


def create_claude_code_plugin(
    name: str = "claude_code",
    check_interval: float = 2.0,
) -> ClaudeCodePlugin:
    """创建 Claude Code 插件的便捷函数"""
    return ClaudeCodePlugin(name=name, check_interval=check_interval)
