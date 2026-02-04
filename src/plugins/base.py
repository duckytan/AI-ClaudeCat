# -*- coding: utf-8 -*-
"""
插件基类 - v3.1 插件化架构

提供所有插件的抽象基类接口。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable
import uuid


class PluginType(Enum):
    """插件类型枚举"""

    PROCESS = "process"  # 进程监控
    WINDOW = "window"  # 窗口监控
    FILE = "file"  # 文件监控
    HTTP = "http"  # HTTP API 监控
    CUSTOM = "custom"  # 自定义逻辑


class Status(Enum):
    """AI 工具状态枚举"""

    UNKNOWN = "unknown"  # 未知状态
    IDLE = "idle"  # 待机/空闲
    RUNNING = "running"  # 运行中
    THINKING = "thinking"  # 思考中
    WORKING = "working"  # 工作/忙碌
    EXECUTING = "executing"  # 执行命令
    ERROR = "error"  # 错误
    STOPPED = "stopped"  # 已停止


@dataclass
class PluginMetadata:
    """插件元信息"""

    name: str  # 插件名称
    version: str  # 插件版本
    author: str  # 作者
    description: str  # 描述
    plugin_type: PluginType  # 插件类型
    supported_software: List[str]  # 支持的软件列表
    dependencies: List[str] = field(default_factory=list)  # 依赖项


@dataclass
class StateEvent:
    """状态事件 - 插件检测到的状态变更"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    # 状态信息
    status: Status = Status.UNKNOWN
    previous_status: Optional[Status] = None
    confidence: float = 0.0  # 0.0 - 1.0

    # 来源信息
    source_plugin: str = ""  # 来源插件名称
    source_type: PluginType = PluginType.CUSTOM

    # 详细信息
    details: Dict[str, Any] = field(default_factory=dict)

    # 优先级 (用于多插件融合)
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "previous_status": self.previous_status.value
            if self.previous_status
            else None,
            "confidence": self.confidence,
            "source_plugin": self.source_plugin,
            "source_type": self.source_type.value,
            "details": self.details,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateEvent":
        """从字典创建"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        previous_status = data.get("previous_status")
        if previous_status and isinstance(previous_status, str):
            previous_status = Status(previous_status)

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=timestamp or datetime.now(),
            status=Status(data.get("status", "unknown")),
            previous_status=previous_status,
            confidence=data.get("confidence", 0.0),
            source_plugin=data.get("source_plugin", ""),
            source_type=PluginType(data.get("source_type", "custom")),
            details=data.get("details", {}),
            priority=data.get("priority", 0),
        )


class EventCallback(Protocol):
    """事件回调协议"""

    def __call__(self, event: StateEvent) -> None: ...


class BasePlugin(ABC):
    """插件基类 - 所有插件必须继承此类"""

    def __init__(self, name: str):
        """
        Args:
            name: 插件名称
        """
        self.name = name
        self._callbacks: List[EventCallback] = []
        self._running = False
        self._metadata: Optional[PluginMetadata] = None

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """获取插件元信息 (必须实现)"""
        ...

    def register_callback(self, callback: EventCallback) -> None:
        """注册状态事件回调"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback: EventCallback) -> None:
        """取消注册回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _emit(self, event: StateEvent) -> None:
        """触发所有回调"""
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"[Plugin:{self.name}] Callback error: {e}")

    @abstractmethod
    def check_available(self) -> bool:
        """
        检查目标软件是否可用
        Returns:
            bool: True 表示目标软件正在运行，可以进行检测
        """

    @abstractmethod
    async def detect(self) -> Optional[StateEvent]:
        """
        检测当前状态
        Returns:
            Optional[StateEvent]: 检测到的状态事件，如果没有变化返回 None
        """

    def on_event(self, event: StateEvent) -> None:
        """
        接收其他插件事件 (可选实现)
        Args:
            event: 其他插件发出的状态事件
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """启动插件 (开始监控)"""

    @abstractmethod
    def stop(self) -> None:
        """停止插件 (停止监控)"""

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running

    def get_status(self) -> Dict[str, Any]:
        """获取插件状态信息"""
        return {
            "name": self.name,
            "running": self._running,
            "metadata": self.metadata.__dict__ if self.metadata else None,
        }


class PluginRegistry:
    """插件注册表 - 管理所有已注册的插件"""

    _instance: Optional["PluginRegistry"] = None
    _plugins: Dict[str, BasePlugin]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._plugins = {}
        return cls._instance

    def register(self, plugin: BasePlugin) -> None:
        """注册插件"""
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin '{plugin.name}' already registered")
        self._plugins[plugin.name] = plugin

    def unregister(self, plugin_name: str) -> None:
        """取消注册插件"""
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]

    def get(self, plugin_name: str) -> Optional[BasePlugin]:
        """获取插件"""
        return self._plugins.get(plugin_name)

    def list_all(self) -> List[BasePlugin]:
        """列出所有插件"""
        return list(self._plugins.values())

    def list_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:
        """按类型列出插件"""
        return [
            p for p in self._plugins.values() if p.metadata.plugin_type == plugin_type
        ]
