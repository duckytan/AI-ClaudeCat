# -*- coding: utf-8 -*-
"""
BasePlugin - 插件基类
定义插件接口、状态事件和枚举类型
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json


class Status(Enum):
    """AI 状态枚举（8 种状态）"""
    UNKNOWN = "unknown"      # 未知状态
    IDLE = "idle"            # 空闲（等待用户输入）
    RUNNING = "running"      # 运行中（AI 接收到提示词）
    THINKING = "thinking"    # 思考中（AI 内部推理）
    WORKING = "working"      # 工作中（读/写文件、搜索）
    EXECUTING = "executing"  # 执行中（运行 Bash 命令）
    ERROR = "error"          # 错误（工具调用失败）
    STOPPED = "stopped"      # 停止（进程关闭）


class PluginType(Enum):
    """插件类型"""
    SYSTEM = "system"        # 系统插件（CPU、内存）
    WINDOW = "window"        # 窗口插件（窗口标题、进程）
    FILE = "file"            # 文件插件（日志监控）
    NETWORK = "network"      # 网络插件（API 调用）
    CUSTOM = "custom"        # 自定义插件


@dataclass
class PluginMetadata:
    """插件元信息"""
    name: str                           # 插件名称
    version: str                        # 版本号
    author: str                         # 作者
    plugin_type: PluginType            # 插件类型
    supported_software: List[str]      # 支持的软件
    dependencies: List[str] = field(default_factory=list)  # 依赖
    description: str = ""              # 描述


@dataclass
class StateEvent:
    """
    状态事件（可序列化）
    
    核心字段：
    - status: 状态枚举
    - confidence: 置信度（0.0-1.0）
    - source: 来源插件
    - timestamp: 时间戳
    - details: 详细信息（JSON 可序列化）
    """
    status: Status
    confidence: float
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典（JSON 可序列化）"""
        data = asdict(self)
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StateEvent':
        """从字典重建对象"""
        data['status'] = Status(data['status'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class BasePlugin(ABC):
    """
    插件基类
    
    所有插件必须继承此类，并实现以下方法：
    - detect(): 检测状态
    - start(): 启动插件
    - stop(): 停止插件
    - metadata: 元信息属性
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.callbacks: List[Callable[[StateEvent], None]] = []
        self.enabled = self.config.get('enabled', True)
        self.priority = self.config.get('priority', 5)
        self.running = False
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """插件元信息"""
        pass
    
    @abstractmethod
    async def detect(self) -> Optional[StateEvent]:
        """
        检测状态（异步）
        
        Returns:
            StateEvent 或 None（无变化）
        """
        pass
    
    @abstractmethod
    async def start(self):
        """启动插件"""
        pass
    
    @abstractmethod
    async def stop(self):
        """停止插件"""
        pass
    
    def register_callback(self, callback: Callable[[StateEvent], None]):
        """注册事件回调"""
        self.callbacks.append(callback)
    
    def _emit(self, event: StateEvent):
        """发送事件到所有回调"""
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"[{self.metadata.name}] Callback error: {e}")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} enabled={self.enabled} priority={self.priority}>"
