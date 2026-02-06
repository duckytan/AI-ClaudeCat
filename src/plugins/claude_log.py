# -*- coding: utf-8 -*-
"""
ClaudeLogPlugin - Claude Code 日志监控插件

功能：
1. 监控 ~/.claude/projects/**/*.jsonl
2. 增量读取新行
3. 解析 JSONL 事件
4. 推断状态（thinking/tool_use）
5. 提取 Token 统计
"""

import os
import json
import glob
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .base import BasePlugin, StateEvent, Status, PluginType, PluginMetadata


class ClaudeLogPlugin(BasePlugin):
    """Claude Code 日志监控插件"""
    
    # 工具名称 → 状态映射
    TOOL_STATUS_MAP = {
        'thinking': Status.THINKING,
        'text': Status.WORKING,
        'Read': Status.WORKING,
        'Write': Status.WORKING,
        'Edit': Status.WORKING,
        'Bash': Status.EXECUTING,
        'Grep': Status.WORKING,
        'Glob': Status.WORKING,
        'WebFetch': Status.WORKING,
        'WebSearch': Status.WORKING,
        'Task': Status.WORKING,
        'TodoWrite': Status.WORKING,
        'Skill': Status.WORKING,            # Skill 工具
        'AskUserQuestion': Status.IDLE,     # 等待用户输入
        'TaskOutput': Status.WORKING,       # 任务输出
        'ListMcpResourcesTool': Status.WORKING,  # MCP 资源列表
    }
    
    # MCP 工具模式匹配（所有 MCP 工具都以 mcp__ 开头）
    MCP_TOOL_PREFIX = 'mcp__'
    
    # 可忽略的错误类型（临时性错误，无需用户关注）
    IGNORABLE_ERRORS = {
        'overloaded_error',          # 服务器过载（502）
        'rate_limit_error',          # 速率限制（429）
        'timeout_error',             # 超时
        'connection_error',          # 连接错误
        'service_unavailable',       # 服务不可用（503）
    }
    
    # 需要关注的重大错误
    CRITICAL_ERRORS = {
        'invalid_request_error',     # 请求格式错误
        'authentication_error',      # 认证失败
        'permission_error',          # 权限不足
        'not_found_error',           # 资源不存在
        'api_error',                 # API 内部错误
    }
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        # 日志目录
        projects_dir = config.get('projects_dir', 'auto') if config else 'auto'
        if projects_dir == 'auto':
            self.projects_dir = Path.home() / '.claude' / 'projects'
        else:
            self.projects_dir = Path(projects_dir)
        
        # 子 Agent 支持
        self.track_subagents = config.get('track_subagents', True) if config else True
        
        # 错误过滤配置
        self.show_all_errors = config.get('show_all_errors', False) if config else False
        
        # 增量读取位置记录
        self.file_positions: Dict[str, int] = {}
        
        # 当前会话和 Agent
        self.current_session: Optional[str] = None
        self.current_agent: Optional[str] = None
        self.last_status = Status.UNKNOWN
        
        # 会话 → Agent 映射
        self.active_agents: Dict[str, Set[str]] = {}
        # Agent → 类型映射
        self.agent_types: Dict[str, str] = {}
        
        # Token 统计
        self.token_stats: Dict[str, int] = {
            'input': 0,
            'output': 0,
            'cache_write': 0,
            'cache_read': 0,
        }
        
        # 文件监控
        self.observer: Optional[Observer] = None
        self.monitored_files: Set[str] = set()
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="claude_log",
            version="1.0.0",
            author="AI-ClaudeCat",
            plugin_type=PluginType.FILE,
            supported_software=["Claude Code"],
            dependencies=["watchdog"],
            description="Claude Code 日志监控插件（JSONL 增量读取）"
        )
    
    async def start(self):
        """启动插件"""
        if self.running:
            return
        
        print(f"[{self.metadata.name}] Starting...")
        
        # 检查日志目录
        if not self.projects_dir.exists():
            print(f"[{self.metadata.name}] WARNING: Projects directory not found: {self.projects_dir}")
            return
        
        # 扫描现有日志文件
        await self._scan_existing_logs()
        
        # 启动文件监控
        self._start_file_watcher()
        
        self.running = True
        print(f"[{self.metadata.name}] [OK] Started, monitoring: {self.projects_dir}")
    
    async def stop(self):
        """停止插件"""
        if not self.running:
            return
        
        print(f"[{self.metadata.name}] Stopping...")
        
        # 停止文件监控
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.running = False
        print(f"[{self.metadata.name}] [OK] Stopped")
    
    async def detect(self) -> Optional[StateEvent]:
        """
        检测状态（由文件监控触发，不主动轮询）
        """
        # 此方法不主动调用，由 _handle_new_line() 触发事件
        return None
    
    async def _scan_existing_logs(self):
        """扫描现有日志文件"""
        pattern = str(self.projects_dir / '**' / '*.jsonl')
        log_files = glob.glob(pattern, recursive=True)
        
        if not log_files:
            print(f"[{self.metadata.name}] No JSONL logs found")
            return
        
        # 获取最新的日志文件
        latest_file = max(log_files, key=os.path.getmtime)
        
        print(f"[{self.metadata.name}] Found {len(log_files)} logs, latest: {latest_file}")
        
        # 初始化所有文件的读取位置（而不是只读取最新的）
        for file_path in log_files:
            try:
                # 记录当前文件大小，后续只处理新增内容
                self.file_positions[file_path] = os.path.getsize(file_path)
            except OSError:
                pass
        
        print(f"[{self.metadata.name}] Initialized {len(self.file_positions)} file positions")
        
        # 读取最新文件的最后几行（初始化状态）
        await self._read_full_file(latest_file)
    
    async def _read_full_file(self, file_path: str):
        """完整读取文件（初始化时）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 记录读取位置
            self.file_positions[file_path] = os.path.getsize(file_path)
            
            # 解析最后几行，确定当前状态
            for line in lines[-10:]:  # 只看最后 10 行
                await self._handle_new_line(line, file_path)
        
        except Exception as e:
            print(f"[{self.metadata.name}] Error reading file {file_path}: {e}")
    
    def _start_file_watcher(self):
        """启动文件监控"""
        event_handler = LogFileHandler(self)
        # 保存当前事件循环引用 - 在 async 上下文中获取
        try:
            event_handler.loop = asyncio.get_running_loop()
            print(f"[{self.metadata.name}] [OK] Event loop acquired")
        except RuntimeError:
            print(f"[{self.metadata.name}] ERROR: No running event loop!")
            return
        
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.projects_dir), recursive=True)
        self.observer.start()
        
        print(f"[{self.metadata.name}] [WATCH] Directory: {self.projects_dir}")
        print(f"[{self.metadata.name}] [WATCH] Monitoring *.jsonl files recursively...")
    
    async def _handle_file_change(self, file_path: str):
        """处理文件变化"""
        if not file_path.endswith('.jsonl'):
            return
        
        # 获取文件大小
        try:
            current_size = os.path.getsize(file_path)
        except OSError:
            return
        
        # 获取上次读取位置
        last_position = self.file_positions.get(file_path, 0)
        
        print(f"[{self.metadata.name}] [INFO] File: {Path(file_path).name} - Size: {current_size} bytes (was: {last_position})")
        
        if current_size <= last_position:
            print(f"[{self.metadata.name}] [SKIP] No new content")
            return  # 文件未增长
        
        # 增量读取新行
        new_lines = self._read_new_lines(file_path, last_position)
        print(f"[{self.metadata.name}] [READ] {len(new_lines)} new lines")
        
        # 更新位置
        self.file_positions[file_path] = current_size
        
        # 处理新行
        for line in new_lines:
            await self._handle_new_line(line, file_path)
    
    def _read_new_lines(self, file_path: str, start: int) -> List[str]:
        """增量读取新行"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.seek(start)
                lines = f.readlines()
            return lines
        except Exception as e:
            print(f"[{self.metadata.name}] Error reading new lines: {e}")
            return []
    
    async def _handle_new_line(self, line: str, file_path: str):
        """处理新行"""
        line = line.strip()
        if not line:
            return
        
        try:
            # 解析 JSON
            event = json.loads(line)
            
            # 提取事件类型
            event_type = event.get('type')
            
            if event_type == 'assistant':
                # AI 回复事件
                await self._handle_assistant_event(event, file_path)
            
            elif event_type == 'user':
                # 用户输入事件
                await self._handle_user_event(event, file_path)
            
            elif event_type == 'summary':
                # 会话总结事件
                await self._handle_summary_event(event)
            
            elif event_type == 'progress':
                # MCP 工具进度事件
                await self._handle_progress_event(event)
            
            elif event_type == 'system':
                # 系统事件
                subtype = event.get('subtype', 'unknown')
                
                # 回合结束事件（任务完成）
                if subtype == 'turn_duration':
                    duration_ms = event.get('durationMs', 0)
                    print(f"[{self.metadata.name}] [COMPLETE] Turn finished ({duration_ms}ms)")
                    await self._update_status(
                        Status.IDLE,
                        confidence=0.95,
                        details={
                            'event': 'turn_complete',
                            'duration_ms': duration_ms
                        }
                    )
                    return
                
                # API 错误事件
                elif subtype == 'api_error':
                    error_info = event.get('error', {}).get('error', {})
                    error_type = error_info.get('type', 'unknown')
                    error_message = error_info.get('message', 'Unknown error')
                    
                    # 过滤临时性错误
                    if not self.show_all_errors and error_type in self.IGNORABLE_ERRORS:
                        # 只打印警告，不触发 ERROR 状态
                        print(f"[{self.metadata.name}] [WARNING] {error_type}: {error_message} (已自动忽略)")
                        # 保持之前的状态（THINKING/WORKING），不切换到 ERROR
                        return
                    
                    # 重大错误才触发 ERROR 状态
                    if error_type in self.CRITICAL_ERRORS or self.show_all_errors:
                        await self._update_status(
                            Status.ERROR,
                            confidence=0.95,
                            details={
                                'event': 'api_error',
                                'error_type': error_type,
                                'error': error_message
                            }
                        )
                
                # 本地命令执行事件
                elif subtype == 'local_command':
                    command = event.get('command', 'unknown')
                    print(f"[{self.metadata.name}] [EXECUTING] Local command: {command}")
                    await self._update_status(
                        Status.EXECUTING,
                        confidence=0.90,
                        details={
                            'event': 'local_command',
                            'command': os.path.basename(command) if command else 'unknown'
                        }
                    )
            
            elif event_type == 'file-history-snapshot':
                # 文件历史快照（会话开始）
                print(f"[{self.metadata.name}] [DEBUG] File history snapshot")
                await self._update_status(
                    Status.IDLE,
                    confidence=0.90,
                    details={
                        'event': 'session_start',
                        'message_id': event.get('messageId', 'unknown')
                    }
                )
        
        except json.JSONDecodeError:
            pass  # 忽略非 JSON 行
        except Exception as e:
            print(f"[{self.metadata.name}] Error handling line: {e}")
    
    async def _handle_assistant_event(self, event: Dict, file_path: str):
        """处理 AI 回复事件"""
        message = event.get('message', {})
        content = message.get('content', [])
        stop_reason = message.get('stop_reason')
        
        # 检查是否是回合结束（等待用户输入）
        if stop_reason == 'end_turn':
            print(f"[{self.metadata.name}] [IDLE] Waiting for user input (stop_reason: end_turn)")
            await self._update_status(
                Status.IDLE,
                confidence=0.95,
                details={
                    'event': 'end_turn',
                    'file': os.path.basename(file_path)
                }
            )
            return
        
        elif stop_reason == 'stop_sequence':
            print(f"[{self.metadata.name}] [IDLE] Waiting for user input (stop_reason: stop_sequence)")
            await self._update_status(
                Status.IDLE,
                confidence=0.90,
                details={
                    'event': 'stop_sequence',
                    'file': os.path.basename(file_path)
                }
            )
            return
        
        for block in content:
            block_type = block.get('type')
            
            if block_type == 'thinking':
                # AI 思考中
                await self._update_status(
                    Status.THINKING,
                    confidence=0.95,
                    details={
                        'event': 'thinking',
                        'file': os.path.basename(file_path)
                    }
                )
            
            elif block_type == 'tool_use':
                # 工具调用
                tool_name = block.get('name', '')
                tool_input = block.get('input', {})
                
                # 检查是否是 MCP 工具
                is_mcp_tool = tool_name.startswith(self.MCP_TOOL_PREFIX)
                
                if is_mcp_tool:
                    # 解析 MCP 工具：mcp__server-name__tool-name
                    parts = tool_name.split('__')
                    if len(parts) >= 3:
                        server_name = parts[1]
                        actual_tool = parts[2]
                    else:
                        server_name = 'unknown'
                        actual_tool = tool_name
                    
                    print(f"[{self.metadata.name}] [MCP] Tool: {actual_tool} (server: {server_name})")
                
                # 推断状态
                status = self.TOOL_STATUS_MAP.get(tool_name, Status.WORKING)
                
                # 提取安全上下文
                safe_context = self._extract_safe_context(tool_name, tool_input)
                
                # 添加 MCP 信息
                details = {
                    'event': 'tool_use',
                    'tool': tool_name,
                    'context': safe_context,
                    'file': os.path.basename(file_path)
                }
                
                if is_mcp_tool:
                    details['mcp'] = {
                        'server': server_name,
                        'tool': actual_tool
                    }
                
                await self._update_status(
                    status,
                    confidence=0.9,
                    details=details
                )
            
            elif block_type == 'text':
                # 文本回复
                await self._update_status(
                    Status.WORKING,
                    confidence=0.8,
                    details={
                        'event': 'text',
                        'file': os.path.basename(file_path)
                    }
                )
        
        # 更新 Token 统计
        usage = message.get('usage', {})
        self._update_tokens(usage)
        
        # 如果有 usage 数据，说明这是最终回复（包含 token 统计）
        # 且没有工具调用，可能是在等待用户输入
        if usage and not any(block.get('type') == 'tool_use' for block in content):
            # 检查是否包含问题（通常以 "？" 或 "?" 结尾）
            has_question = False
            for block in content:
                if block.get('type') == 'text':
                    text = block.get('text', '')
                    if '？' in text or '?' in text:
                        has_question = True
                        break
            
            if has_question:
                print(f"[{self.metadata.name}] [IDLE] Likely waiting for user (question detected)")
                await self._update_status(
                    Status.IDLE,
                    confidence=0.85,
                    details={
                        'event': 'question_asked',
                        'file': os.path.basename(file_path)
                    }
                )
    
    async def _handle_progress_event(self, event: Dict):
        """
        处理 MCP 工具进度事件
        
        进度事件格式：
        {
            "type": "progress",
            "data": {
                "type": "mcp_progress",
                "status": "started" | "completed",
                "serverName": "open-websearch",
                "toolName": "search",
                "elapsedTimeMs": 42324  // only in completed
            }
        }
        """
        data = event.get('data', {})
        if data.get('type') != 'mcp_progress':
            return
        
        status = data.get('status')
        server_name = data.get('serverName', 'unknown')
        tool_name = data.get('toolName', 'unknown')
        elapsed_ms = data.get('elapsedTimeMs', 0)
        
        if status == 'started':
            print(f"[{self.metadata.name}] [MCP] Started: {tool_name} (server: {server_name})")
            await self._update_status(
                Status.WORKING,
                confidence=0.85,
                details={
                    'event': 'mcp_progress',
                    'status': 'started',
                    'mcp': {
                        'server': server_name,
                        'tool': tool_name
                    }
                }
            )
        
        elif status == 'completed':
            print(f"[{self.metadata.name}] [MCP] Completed: {tool_name} ({elapsed_ms}ms)")
            await self._update_status(
                Status.WORKING,
                confidence=0.80,
                details={
                    'event': 'mcp_progress',
                    'status': 'completed',
                    'elapsed_ms': elapsed_ms,
                    'mcp': {
                        'server': server_name,
                        'tool': tool_name
                    }
                }
            )
    
    async def _handle_user_event(self, event: Dict, file_path: str):
        """处理用户输入事件"""
        message = event.get('message', {})
        content = message.get('content', [])
        
        await self._update_status(
            Status.RUNNING,
            confidence=0.95,
            details={
                'event': 'user_input',
                'file': os.path.basename(file_path)
            }
        )
    
    async def _handle_summary_event(self, event: Dict):
        """处理会话总结事件"""
        # 更新 Token 统计
        usage = event.get('usage', {})
        self._update_tokens(usage)
        
        # Summary 事件通常表示会话结束，进入 IDLE
        print(f"[{self.metadata.name}] [SUMMARY] Session completed")
        await self._update_status(
            Status.IDLE,
            confidence=0.85,
            details={
                'event': 'summary',
                'total_tokens': usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            }
        )
    
    def _parse_file_path(self, file_path: str) -> Dict[str, any]:
        """
        解析文件路径，提取项目、会话、Agent 信息
        
        路径格式：
        - 主 Agent: projects/my-app/session-abc123.jsonl
        - 子 Agent: projects/my-app/session-abc123/subagents/agent-def456.jsonl
        
        Args:
            file_path: JSONL 文件路径
        
        Returns:
            {
                'project': 'my-app',
                'session_id': 'session-abc123',
                'agent_id': 'agent-def456' or None,
                'is_subagent': True/False
            }
        """
        path = Path(file_path)
        
        # 检查是否是子 Agent（路径中包含 subagents）
        is_subagent = 'subagents' in path.parts
        
        if is_subagent:
            # 路径: projects/my-app/session-abc123/subagents/agent-def456.jsonl
            agent_id = path.stem  # agent-def456
            session_dir = path.parent.parent  # session-abc123 目录
            session_id = session_dir.name
            project = session_dir.parent.name
        else:
            # 路径: projects/my-app/session-abc123.jsonl
            agent_id = None
            session_id = path.stem  # session-abc123
            project = path.parent.name
        
        return {
            'project': project,
            'session_id': session_id,
            'agent_id': agent_id,
            'is_subagent': is_subagent
        }
    
    def _tool_to_status(self, tool_name: str) -> Status:
        """
        工具名称映射到状态
        
        Args:
            tool_name: 工具名称（如 'Read', 'Write', 'Bash'）
        
        Returns:
            对应的状态枚举
        """
        return self.TOOL_STATUS_MAP.get(tool_name, Status.WORKING)
    
    def _extract_safe_context(self, tool_name: str, tool_input: Dict) -> Dict:
        """提取安全上下文（隐私保护）"""
        safe_context = {}
        
        # 只提取元数据，不提取内容
        if 'file_path' in tool_input:
            safe_context['file'] = os.basename(tool_input['file_path'])
        
        if 'pattern' in tool_input:
            safe_context['pattern'] = tool_input['pattern']
        
        if 'method' in tool_input:
            safe_context['method'] = tool_input['method']
        
        return safe_context
    
    def _update_tokens(self, usage: Dict):
        """更新 Token 统计"""
        if not usage:
            return
        
        self.token_stats['input'] += usage.get('input_tokens', 0)
        self.token_stats['output'] += usage.get('output_tokens', 0)
        self.token_stats['cache_write'] += usage.get('cache_creation_input_tokens', 0)
        self.token_stats['cache_read'] += usage.get('cache_read_input_tokens', 0)
    
    async def _update_status(self, status: Status, confidence: float, details: Dict):
        """更新状态并发送事件"""
        if status == self.last_status:
            return  # 状态未变化
        
        self.last_status = status
        
        # 添加 Token 统计
        details['tokens'] = self.token_stats.copy()
        
        # 创建事件
        event = StateEvent(
            status=status,
            confidence=confidence,
            source=self.metadata.name,
            details=details
        )
        
        # 发送事件
        self._emit(event)


class LogFileHandler(FileSystemEventHandler):
    """文件系统事件处理器"""
    
    def __init__(self, plugin: ClaudeLogPlugin):
        self.plugin = plugin
        self.loop = None
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        # 调试输出
        if event.src_path.endswith('.jsonl'):
            print(f"[Watchdog] [CHANGE] File changed: {event.src_path}")
        
        # 从其他线程提交到事件循环
        if self.loop is None:
            print(f"[Watchdog] [WARNING] No event loop!")
            return
        
        # 线程安全地调度协程
        asyncio.run_coroutine_threadsafe(
            self.plugin._handle_file_change(event.src_path),
            self.loop
        )
