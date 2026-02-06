# -*- coding: utf-8 -*-
"""
SessionManager - 会话管理器

功能：
- 追踪会话生命周期
- 超时检测
- 会话统计
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, Callable
import asyncio


@dataclass
class Session:
    """会话信息"""
    id: str
    project: str
    start_time: datetime
    last_activity: datetime
    agents: Set[str] = field(default_factory=set)
    status: str = 'active'  # active, idle, ended
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> timedelta:
        """会话持续时间"""
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    @property
    def idle_time(self) -> timedelta:
        """空闲时间"""
        return datetime.now() - self.last_activity
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'project': self.project,
            'start_time': self.start_time.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'agents': list(self.agents),
            'status': self.status,
            'duration_seconds': self.duration.total_seconds(),
            'idle_seconds': self.idle_time.total_seconds() if self.status == 'active' else 0
        }


class SessionManager:
    """会话管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # 会话超时（分钟）
        self.timeout_minutes = self.config.get('timeout_minutes', 10)
        
        # 活动会话
        self.sessions: Dict[str, Session] = {}
        
        # 回调函数
        self.callbacks: Dict[str, list] = {
            'session_start': [],
            'session_end': [],
            'session_idle': [],
            'session_active': []
        }
        
        # 后台任务
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """启动会话管理器"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        print("[SessionManager] Started")
    
    async def stop(self):
        """停止会话管理器"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        print("[SessionManager] Stopped")
    
    def on_session_start(self, session_id: str, project: str):
        """会话开始"""
        if session_id in self.sessions:
            # 会话已存在，更新活动时间
            self.on_session_activity(session_id)
            return
        
        session = Session(
            id=session_id,
            project=project,
            start_time=datetime.now(),
            last_activity=datetime.now()
        )
        self.sessions[session_id] = session
        
        self._emit('session_start', session.to_dict())
    
    def on_session_activity(self, session_id: str):
        """会话活动"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        was_idle = session.status == 'idle'
        session.last_activity = datetime.now()
        session.status = 'active'
        
        if was_idle:
            self._emit('session_active', session.to_dict())
    
    def on_session_end(self, session_id: str):
        """会话结束"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        session.status = 'ended'
        session.end_time = datetime.now()
        
        self._emit('session_end', session.to_dict())
        
        # 延迟删除（保留 1 小时）
        asyncio.create_task(self._delayed_remove(session_id, hours=1))
    
    def add_agent(self, session_id: str, agent_id: str):
        """添加 Agent"""
        session = self.sessions.get(session_id)
        if session:
            session.agents.add(agent_id)
            self.on_session_activity(session_id)
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def get_active_sessions(self) -> Dict[str, Session]:
        """获取活动会话"""
        return {
            sid: s for sid, s in self.sessions.items()
            if s.status == 'active'
        }
    
    def register_callback(self, event: str, callback: Callable):
        """注册回调"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _emit(self, event: str, data: Dict):
        """触发回调"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(event, data)
            except Exception as e:
                print(f"[SessionManager] Callback error: {e}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                self._check_timeouts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[SessionManager] Cleanup error: {e}")
    
    def _check_timeouts(self):
        """检查超时会话"""
        timeout = timedelta(minutes=self.timeout_minutes)
        now = datetime.now()
        
        for session_id, session in list(self.sessions.items()):
            if session.status != 'active':
                continue
            
            idle_time = now - session.last_activity
            
            if idle_time > timeout:
                # 会话超时 → idle
                session.status = 'idle'
                self._emit('session_idle', session.to_dict())
            elif idle_time > timeout * 2:
                # 超过 2 倍超时 → ended
                self.on_session_end(session_id)
    
    async def _delayed_remove(self, session_id: str, hours: int = 1):
        """延迟删除会话"""
        await asyncio.sleep(hours * 3600)
        if session_id in self.sessions:
            del self.sessions[session_id]
