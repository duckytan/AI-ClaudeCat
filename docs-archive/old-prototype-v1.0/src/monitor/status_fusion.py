# -*- coding: utf-8 -*-
"""
状态融合器
综合多个监控源的输出版断最终状态
"""

import time
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass, field
from collections import deque

from .base import BaseMonitor, MonitorResult, Status


@dataclass
class FusionResult:
    """融合结果"""

    status: Status
    confidence: float
    sources: Dict[str, MonitorResult]  # 各监控源的结果
    vote_details: Dict  # 投票详情


class StatusFusion:
    """状态融合器"""

    def __init__(self):
        self.monitors: List[BaseMonitor] = []
        self.callbacks: List[Callable] = []

        # 状态历史（用于平滑处理）
        self.history = deque(maxlen=10)
        self.last_result: Optional[FusionResult] = None

        # 优先级（数值越大优先级越高）
        self.priority = {
            Status.NOT_RUNNING: 0,
            Status.IDLE: 1,
            Status.RUNNING: 2,
            Status.READING: 3,
            Status.WRITING: 4,
            Status.THINKING: 5,
            Status.EXECUTING: 6,
            Status.WORKING: 7,
            Status.ERROR: 8,
            Status.DONE: 9,
        }

        # 投票权重
        self.weights = {}

    def add_monitor(self, monitor: BaseMonitor):
        """添加监控器"""
        self.monitors.append(monitor)
        self.weights[monitor] = monitor.get_weight()

    def remove_monitor(self, monitor: BaseMonitor):
        """移除监控器"""
        if monitor in self.monitors:
            self.monitors.remove(monitor)
            del self.weights[monitor]

    def register_callback(self, callback: Callable):
        """注册状态变化回调"""
        self.callbacks.append(callback)

    def get_result(self) -> FusionResult:
        """获取融合后的状态"""
        # 获取所有监控源的结果
        source_results = {}
        for monitor in self.monitors:
            if monitor.is_available() and monitor.is_running():
                result = monitor.get_result()
                source_results[monitor.__class__.__name__] = result

        if not source_results:
            # 没有可用监控源
            result = FusionResult(
                status=Status.IDLE,
                confidence=0.0,
                sources={},
                vote_details={"error": "no monitors available"},
            )
            self._notify(result)
            return result

        # 加权投票
        vote_result = self._weighted_vote(source_results)

        # 获取投票结果中的状态（可能是 Status 枚举或字典）
        if isinstance(vote_result["status"], Status):
            voted_status = vote_result["status"]
        else:
            voted_status = Status.IDLE

        # 添加到历史
        self.history.append(vote_result)

        # 平滑处理
        smoothed = self._smooth(vote_result)

        # 计算最终置信度
        final_confidence = self._calculate_final_confidence(source_results, vote_result)

        result = FusionResult(
            status=smoothed,
            confidence=final_confidence,
            sources=source_results,
            vote_details=vote_result,
        )

        self.last_result = result
        self._notify(result)

        return result

    def _weighted_vote(self, source_results: Dict[str, MonitorResult]) -> Dict:
        """
        加权投票

        Returns:
            {
                'status': 最终状态,
                'votes': {状态: 加权票数},
                'details': 详情
            }
        """
        votes = {}

        for name, result in source_results.items():
            weight = self.weights.get(name, 0.5)
            weighted_score = result.confidence * weight

            if result.status not in votes:
                votes[result.status] = 0.0
            votes[result.status] += weighted_score

        # 选择最高票数
        if not votes:
            return {"status": Status.IDLE, "votes": {}, "reason": "no votes"}

        # 选择得分最高的状态（得分相同则选优先级高的）
        best_status = max(votes.keys(), key=lambda s: (votes[s], self.priority[s]))
        best_score = votes[best_status]

        # 检查是否有竞争状态（票数接近）
        runners_up = [
            (s, score)
            for s, score in votes.items()
            if s != best_status and score >= best_score * 0.8
        ]

        return {
            "status": best_status,
            "votes": votes,
            "runners_up": runners_up,
            "reason": "weighted vote",
        }

    def _smooth(self, vote_result: Dict) -> Status:
        """
        平滑处理

        如果当前投票结果与最近历史不一致，考虑使用历史结果
        """
        if not self.history:
            return vote_result["status"]

        # 获取最近3个结果
        recent = list(self.history)[-3:]

        # 统计历史中的常见状态
        status_counts = {}
        for item in recent:
            status = item["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        # 如果投票结果不在历史主流中，考虑使用历史
        if (
            vote_result["status"] not in status_counts
            or status_counts[vote_result["status"]] == 1
        ):
            # 检查历史主流
            most_common = max(status_counts.keys(), key=lambda s: status_counts[s])
            if status_counts[most_common] >= 2:
                return most_common

        return vote_result["status"]

    def _calculate_final_confidence(
        self, source_results: Dict, vote_result: Dict
    ) -> float:
        """计算最终置信度"""
        if not source_results:
            return 0.0

        # 基本置信度 = 投票胜出者的票数 / 总票数
        total_votes = sum(vote_result["votes"].values())
        if total_votes == 0:
            return 0.0

        winner_votes = vote_result["votes"].get(vote_result["status"], 0)
        base_confidence = winner_votes / total_votes

        # 一致性调整
        consistency = self._calculate_consistency(source_results)

        # 活跃度调整
        activity = self._calculate_activity(source_results)

        # 最终置信度
        final = base_confidence * 0.6 + consistency * 0.3 + activity * 0.1

        return min(0.99, final)

    def _calculate_consistency(self, source_results: Dict) -> float:
        """计算各监控源的一致性"""
        if len(source_results) <= 1:
            return 1.0

        statuses = [r.status for r in source_results.values()]

        # 统计状态分布
        from collections import Counter

        counts = Counter(statuses)

        # 一致性 = 最常见状态的占比
        most_common = counts.most_common(1)[0][1]
        return most_common / len(statuses)

    def _calculate_activity(self, source_results: Dict) -> float:
        """计算活跃度"""
        if not source_results:
            return 0.0

        # 检查是否有监控源报告了高活动状态
        high_activity = [Status.ERROR, Status.DONE, Status.WORKING]

        for result in source_results.values():
            if result.status in high_activity:
                return 1.0

        return 0.5

    def _notify(self, result: FusionResult):
        """通知状态变化"""
        # 检查是否真的变化了
        if self.last_result is None or self.last_result.status != result.status:
            for callback in self.callbacks:
                try:
                    callback(result)
                except Exception as e:
                    print(f"[ERROR] Fusion callback error: {e}")

    def get_status_description(self, status: Status) -> str:
        """获取状态描述"""
        descriptions = {
            Status.NOT_RUNNING: "Not Running",
            Status.IDLE: "Idle",
            Status.RUNNING: "Running",
            Status.READING: "Reading",
            Status.WRITING: "Writing",
            Status.THINKING: "Thinking",
            Status.EXECUTING: "Executing",
            Status.WORKING: "Working",
            Status.ERROR: "Error",
            Status.DONE: "Done",
        }
        return descriptions.get(status, "Unknown")

    def get_history(self) -> List[Dict]:
        """获取状态历史"""
        return list(self.history)


# 便捷函数
def create_fusion() -> StatusFusion:
    """创建状态融合器"""
    return StatusFusion()
