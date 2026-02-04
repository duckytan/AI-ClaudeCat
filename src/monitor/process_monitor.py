# -*- coding: utf-8 -*-
"""
进程监控器
"""

import psutil
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

from .base import BaseMonitor, MonitorResult, Status


# 状态阈值配置
THRESHOLDS = {
    "idle": 0.5,
    "running": 3.0,
    "thinking": 15.0,
    "active": 50.0,
}

# 权重配置
WEIGHT = 0.5  # 进程监控在融合中的权重


class ProcessMonitor(BaseMonitor):
    """进程监控器"""

    def __init__(self, callback=None):
        super().__init__(callback)
        self.check_interval = 2.0
        self._running = False
        self._last_cpu = {}

    def start(self):
        """开始监控"""
        self._running = True
        print(f"[ProcessMonitor] Started (interval: {self.check_interval}s)")

    def stop(self):
        """停止监控"""
        self._running = False
        print("[ProcessMonitor] Stopped")

    def is_available(self) -> bool:
        """检查是否可用"""
        return True  # psutil 总是可用

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running

    def get_result(self) -> MonitorResult:
        """获取监控结果"""
        # 查找进程
        processes = self._find_claude_processes()

        if not processes:
            return MonitorResult(
                status=Status.NOT_RUNNING,
                confidence=1.0,
                details={"process_count": 0},
                source="process",
            )

        # 计算 CPU 占用
        cpu_percent = self._get_cpu_usage(processes)
        process_count = len(processes)

        # 判断状态
        status = self._judge_status(cpu_percent)
        confidence = self._calculate_confidence(status, cpu_percent, process_count)

        details = {
            "process_count": process_count,
            "cpu_percent": cpu_percent,
        }

        result = MonitorResult(
            status=status, confidence=confidence, details=details, source="process"
        )

        self._notify(result)
        return result

    def _find_claude_processes(self) -> List[psutil.Process]:
        """查找 Claude 相关进程"""
        processes = []

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                info = proc.info
                name = info.get("name", "") or ""
                cmdline = info.get("cmdline") or []

                name_lower = name.lower()
                cmdline_str = " ".join(cmdline).lower()

                # 匹配关键词
                keywords = ["claude", "anthropic"]
                if any(kw in name_lower or kw in cmdline_str for kw in keywords):
                    processes.append(proc)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes

    def _get_cpu_usage(self, processes: List[psutil.Process]) -> float:
        """计算总 CPU 占用"""
        total_cpu = 0.0

        for p in processes:
            try:
                total_cpu += p.cpu_percent(interval=0.3)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return total_cpu

    def _judge_status(self, cpu_percent: float) -> Status:
        """根据 CPU 占用判断状态"""
        if cpu_percent < THRESHOLDS["idle"]:
            return Status.IDLE
        elif cpu_percent < THRESHOLDS["running"]:
            return Status.RUNNING
        elif cpu_percent < THRESHOLDS["thinking"]:
            return Status.THINKING
        elif cpu_percent < THRESHOLDS["active"]:
            return Status.WORKING
        else:
            return Status.WORKING

    def _calculate_confidence(
        self, status: Status, cpu_percent: float, process_count: int
    ) -> float:
        """计算置信度"""
        # 基础置信度
        if status == Status.NOT_RUNNING:
            return 1.0
        elif status == Status.IDLE:
            return 0.9
        elif status == Status.RUNNING:
            return 0.7
        elif status == Status.THINKING:
            return 0.8
        elif status == Status.WORKING:
            return 0.85

        return 0.5  # 默认

    def get_weight(self) -> float:
        """获取权重"""
        return WEIGHT


# 便捷函数
def create_process_monitor(callback=None) -> ProcessMonitor:
    """创建进程监控器"""
    return ProcessMonitor(callback)
