# -*- coding: utf-8 -*-
"""
HTTPAdapter - HTTP REST API 适配器
提供查询接口（当前状态、Token 统计）
"""

import asyncio
from typing import Optional, Dict
from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread
from src.plugins.base import StateEvent
from .base import OutputAdapter


class HTTPAdapter(OutputAdapter):
    """HTTP REST API 适配器"""
    
    def __init__(self, config: Optional[Dict] = None, middleware=None):
        super().__init__(config)
        self.host = self.config.get('host', '127.0.0.1')
        self.port = self.config.get('port', 8080)
        self.cors = self.config.get('cors', True)
        
        self.middleware = middleware
        self.current_status: Optional[StateEvent] = None
        
        # Flask 应用
        self.app = Flask(__name__)
        if self.cors:
            CORS(self.app)
        
        # 注册路由
        self._register_routes()
        
        # 服务器线程
        self.server_thread: Optional[Thread] = None
    
    def _register_routes(self):
        """注册 API 路由"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """获取当前状态"""
            if self.current_status is None:
                return jsonify({'error': 'No status available'}), 404
            
            return jsonify(self.current_status.to_dict())
        
        @self.app.route('/api/tokens', methods=['GET'])
        def get_tokens():
            """获取 Token 统计"""
            if self.middleware is None:
                return jsonify({'error': 'Middleware not available'}), 500
            
            stats = self.middleware.get_token_stats()
            return jsonify(stats)
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """健康检查"""
            return jsonify({
                'status': 'ok',
                'version': '4.0.0',
                'adapters': {
                    'websocket': True,
                    'http': True,
                }
            })
    
    async def start(self):
        """启动 HTTP 服务器"""
        if not self.enabled or self.running:
            return
        
        print(f"[HTTP] Starting on http://{self.host}:{self.port}...")
        
        # 在新线程中启动 Flask
        self.server_thread = Thread(
            target=self.app.run,
            kwargs={
                'host': self.host,
                'port': self.port,
                'debug': False,
                'use_reloader': False,
            },
            daemon=True
        )
        self.server_thread.start()
        
        self.running = True
        print(f"[HTTP] [OK] Started on http://{self.host}:{self.port}")
    
    async def stop(self):
        """停止 HTTP 服务器"""
        if not self.running:
            return
        
        print("[HTTP] Stopping...")
        # Flask 无法优雅关闭，使用 daemon 线程自动退出
        self.running = False
        print("[HTTP] [OK] Stopped")
    
    async def send(self, event: StateEvent):
        """更新当前状态"""
        self.current_status = event
