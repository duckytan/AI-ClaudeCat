# -*- coding: utf-8 -*-
"""
Claude Code 插件 - 监控 Claude Code 进程状态

通过进程 CPU 占用检测 Claude Code 的工作状态：
- idle: CPU < 0.5% (待机)
- running: CPU < 3% (运行中)
- thinking: CPU < 15% (思考中)
- working: CPU >= 15% (工作中)
"""

import asyncio
import psutil
from typing import List, Optional

from .base import (
    BasePlugin,
    PluginMetadata,
    PluginType,
    StateEvent,
    Status,
)


class ClaudeCodePlugin(BasePlugin):
    """Claude Code 进程监控插件"""

    # 状态阈值配置 (CPU 百分比)
    THRESHOLDS = {
        "idle": 0.5,  # CPU < 0.5% 视为空闲
        "running": 3.0,  # CPU < 3% 视为运行中
        "thinking": 15.0,  # CPU < 15% 视为思考中
        "working": 50.0,  # CPU < 50% 视为工作中
    }

    # Claude Code 进程特征
    PROCESS_NAMES = ["claude", "anthropic"]

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
        self._last_cpu_percent: float = 0.0

        self._metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            author="AI-ClaudeCat",
            description="Monitor Claude Code process status via CPU usage",
            plugin_type=PluginType.PROCESS,
            supported_software=["Claude Code", "Claude"],
            dependencies=["psutil"],
        )

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def check_available(self) -> bool:
        """检查 Claude Code 进程是否存在"""
        return self._find_claude_processes() is not None

    async def detect(self) -> Optional[StateEvent]:
        """检测 Claude Code 状态"""
        processes = self._find_claude_processes()

        if not processes:
            status = Status.STOPPED
            confidence = 1.0
            details = {"process_count": 0}
        else:
            # 计算总 CPU 占用
            cpu_percent = self._get_cpu_usage(processes)
            process_count = len(processes)

            # 判断状态
            status = self._judge_status(cpu_percent)
            confidence = self._calculate_confidence(status, cpu_percent, process_count)

            details = {
                "process_count": process_count,
                "cpu_percent": round(cpu_percent, 2),
            }

            self._last_cpu_percent = cpu_percent

        # 只有状态变化才返回事件
        if status != self._last_status:
            self._last_status = status

            event = StateEvent(
                status=status,
                confidence=confidence,
                source_plugin=self.name,
                source_type=PluginType.PROCESS,
                details=details,
                priority=1,
            )

            self._emit(event)
            return event

        return None

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

    def _judge_status(self, cpu_percent: float) -> Status:
        """根据 CPU 占用判断状态"""
        if cpu_percent < self.THRESHOLDS["idle"]:
            return Status.IDLE
        elif cpu_percent < self.THRESHOLDS["running"]:
            return Status.RUNNING
        elif cpu_percent < self.THRESHOLDS["thinking"]:
            return Status.THINKING
        elif cpu_percent < self.THRESHOLDS["working"]:
            return Status.WORKING
        else:
            return Status.WORKING

    def _calculate_confidence(
        self, status: Status, cpu_percent: float, process_count: int
    ) -> float:
        """计算置信度"""
        if status == Status.STOPPED:
            return 1.0
        elif status == Status.IDLE:
            return 0.9
        elif status == Status.RUNNING:
            return 0.7
        elif status == Status.THINKING:
            return 0.8
        elif status == Status.WORKING:
            return 0.85
        return 0.5

    def start(self) -> None:
        """启动监控"""
        self._running = True
        print(f"[ClaudeCodePlugin:{self.name}] Started")

    def stop(self) -> None:
        """停止监控"""
        self._running = False
        print(f"[ClaudeCodePlugin:{self.name}] Stopped")


def create_claude_code_plugin(
    name: str = "claude_code",
    check_interval: float = 2.0,
) -> ClaudeCodePlugin:
    """创建 Claude Code 插件的便捷函数"""
    return ClaudeCodePlugin(name=name, check_interval=check_interval)
