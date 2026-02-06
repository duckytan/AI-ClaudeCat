# -*- coding: utf-8 -*-
"""
进程监控工具
检测 Claude Code 进程的启动和退出
"""

import psutil
import time
from typing import Optional, Dict, Set
from dataclasses import dataclass

@dataclass
class ProcessEvent:
    """进程事件"""
    event_type: str  # 'start', 'exit'
    process_name: str
    pid: int
    timestamp: float
    command_line: Optional[str] = None

class ClaudeProcessMonitor:
    """Claude Code 进程监控器"""
    
    def __init__(self):
        self.running_pids: Set[int] = set()
        self.last_check_time = time.time()
        self._initialize_running_processes()
    
    def _initialize_running_processes(self):
        """初始化当前运行的 Claude 进程"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if self._is_claude_process(proc):
                    self.running_pids.add(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def _is_claude_process(self, proc) -> bool:
        """判断是否是 Claude Code 进程"""
        try:
            name = proc.info.get('name', '').lower()
            cmdline = proc.info.get('cmdline', [])
            
            # 检查进程名
            if name in ['claude', 'claude.exe']:
                return True
            
            # 检查命令行参数
            if cmdline and any('claude' in str(arg).lower() for arg in cmdline):
                return True
                
            return False
        except:
            return False
    
    def check_events(self) -> list[ProcessEvent]:
        """检查进程事件"""
        events = []
        current_pids = set()
        current_time = time.time()
        
        # 检查当前运行的进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if self._is_claude_process(proc):
                    pid = proc.info['pid']
                    current_pids.add(pid)
                    
                    # 检查新启动的进程
                    if pid not in self.running_pids:
                        events.append(ProcessEvent(
                            event_type='start',
                            process_name=proc.info.get('name', 'claude'),
                            pid=pid,
                            timestamp=current_time,
                            command_line=' '.join(proc.info.get('cmdline', []))
                        ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # 检查已退出的进程
        for pid in self.running_pids - current_pids:
            events.append(ProcessEvent(
                event_type='exit',
                process_name='claude',
                pid=pid,
                timestamp=current_time
            ))
        
        # 更新运行中的进程集合
        self.running_pids = current_pids
        self.last_check_time = current_time
        
        return events
    
    def is_claude_running(self) -> bool:
        """检查 Claude Code 是否正在运行"""
        return len(self.running_pids) > 0
    
    def get_running_processes(self) -> list[Dict]:
        """获取当前运行的 Claude 进程信息"""
        processes = []
        for pid in self.running_pids:
            try:
                proc = psutil.Process(pid)
                processes.append({
                    'pid': pid,
                    'name': proc.name(),
                    'cmdline': proc.cmdline(),
                    'create_time': proc.create_time(),
                    'status': proc.status()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes