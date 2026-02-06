# -*- coding: utf-8 -*-
"""
Claude Code 进程监控插件
检测 Claude Code 的启动和退出
"""

import asyncio
import time
from typing import Optional, Callable
from ..base import BasePlugin, StateEvent, Status
from ..utils.process_monitor import ClaudeProcessMonitor, ProcessEvent

class ClaudeProcessPlugin(BasePlugin):
    """Claude Code 进程监控插件"""
    
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.monitor = ClaudeProcessMonitor()
        self.check_interval = config.get('check_interval', 1.0) if config else 1.0
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    @property
    def metadata(self):
        from ..base import PluginMetadata, PluginType
        return PluginMetadata(
            name="claude_process",
            version="1.0.0",
            author="AI-ClaudeCat",
            plugin_type=PluginType.SYSTEM,
            supported_software=["Claude Code"],
            dependencies=["psutil"]
        )
    
    async def start(self) -> bool:
        """启动监控"""
        try:
            self._running = True
            self._task = asyncio.create_task(self._monitor_loop())
            
            # 检查当前是否已运行
            if self.monitor.is_claude_running():
                await self._emit(StateEvent(
                    status=Status.RUNNING,
                    confidence=0.95,
                    details={
                        'event': 'process_detected',
                        'processes': self.monitor.get_running_processes(),
                        'message': 'Claude Code 进程已在运行'
                    }
                ))
            
            return True
        except Exception as e:
            print(f"[{self.metadata.name}] 启动失败: {e}")
            return False
    
    async def stop(self) -> bool:
        """停止监控"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        return True
    
    async def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                events = self.monitor.check_events()
                for event in events:
                    await self._handle_process_event(event)
                
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[{self.metadata.name}] 监控错误: {e}")
                await asyncio.sleep(1.0)
    
    async def _handle_process_event(self, event: ProcessEvent):
        """处理进程事件"""
        if event.event_type == 'start':
            print(f"[{self.metadata.name}] 🚀 Claude Code 启动 (PID: {event.pid})")
            await self._emit(StateEvent(
                status=Status.RUNNING,
                confidence=0.95,
                details={
                    'event': 'process_start',
                    'pid': event.pid,
                    'command_line': event.command_line,
                    'timestamp': event.timestamp,
                    'message': f'Claude Code 进程启动 (PID: {event.pid})'
                }
            ))
        
        elif event.event_type == 'exit':
            print(f"[{self.metadata.name}] 🛑 Claude Code 退出 (PID: {event.pid})")
            await self._emit(StateEvent(
                status=Status.STOPPED,
                confidence=0.95,
                details={
                    'event': 'process_exit',
                    'pid': event.pid,
                    'timestamp': event.timestamp,
                    'message': f'Claude Code 进程退出 (PID: {event.pid})'
                }
            ))
            
            # 检查是否还有其他 Claude 进程在运行
            await asyncio.sleep(0.5)  # 给进程一点时间完全退出
            if not self.monitor.is_claude_running():
                await self._emit(StateEvent(
                    status=Status.IDLE,
                    confidence=0.95,
                    details={
                        'event': 'all_processes_exited',
                        'message': '所有 Claude Code 进程已退出'
                    }
                ))