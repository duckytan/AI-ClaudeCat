# -*- coding: utf-8 -*-
"""
WebSocketAdapter - WebSocket 实时推送适配器
"""

import asyncio
import websockets
from typing import Set, Optional, Dict
from src.plugins.base import StateEvent
from .base import OutputAdapter


class WebSocketAdapter(OutputAdapter):
    """WebSocket 实时推送适配器"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.host = self.config.get('host', '127.0.0.1')
        self.port = self.config.get('port', 8765)
        
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server: Optional[websockets.WebSocketServer] = None
    
    async def start(self):
        """启动 WebSocket 服务器"""
        if not self.enabled or self.running:
            return
        
        print(f"[WebSocket] Starting on ws://{self.host}:{self.port}...")
        
        try:
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port
            )
            self.running = True
            print(f"[WebSocket] [OK] Started on ws://{self.host}:{self.port}")
        
        except Exception as e:
            print(f"[WebSocket] [ERROR] Failed to start: {e}")
    
    async def stop(self):
        """停止 WebSocket 服务器"""
        if not self.running:
            return
        
        print("[WebSocket] Stopping...")
        
        # 关闭所有客户端
        for client in self.clients:
            await client.close()
        
        # 关闭服务器
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        self.running = False
        print("[WebSocket] [OK] Stopped")
    
    async def send(self, event: StateEvent):
        """广播事件到所有客户端"""
        if not self.running or not self.clients:
            return
        
        message = event.to_json()
        
        # 广播到所有客户端
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                print(f"[WebSocket] Error sending to client: {e}")
                disconnected_clients.add(client)
        
        # 移除断开的客户端
        self.clients -= disconnected_clients
    
    async def _handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """处理客户端连接"""
        print(f"[WebSocket] Client connected: {websocket.remote_address}")
        
        # 添加到客户端集合
        self.clients.add(websocket)
        
        try:
            # 保持连接（等待客户端消息）
            async for message in websocket:
                # 暂不处理客户端消息
                pass
        
        except websockets.exceptions.ConnectionClosed:
            pass
        
        finally:
            # 移除客户端
            self.clients.discard(websocket)
            print(f"[WebSocket] Client disconnected: {websocket.remote_address}")
