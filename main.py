# -*- coding: utf-8 -*-
"""
AI-ClaudeCat v4.0 - 主程序入口
"""

import asyncio
import json
import signal
import sys
from pathlib import Path

# 导入核心模块
from src.plugins import ClaudeLogPlugin
from src.middleware import Middleware
from src.adapters import WebSocketAdapter, HTTPAdapter, StdoutAdapter


class Application:
    """应用主类"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        
        # 创建中间件
        self.middleware = Middleware(self.config)
        
        # 创建插件
        self.plugins = []
        self._create_plugins()
        
        # 创建适配器
        self.adapters = []
        self._create_adapters()
        
        # 注册插件和适配器
        for plugin in self.plugins:
            self.middleware.register_plugin(plugin)
        
        for adapter in self.adapters:
            self.middleware.register_adapter(adapter)
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            print(f"WARNING: Config file not found: {self.config_path}")
            print("Using default configuration...")
            return self._get_default_config()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"[OK] Loaded config: {self.config_path}")
            return config
        
        except Exception as e:
            print(f"[ERROR] Error loading config: {e}")
            print("Using default configuration...")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """默认配置"""
        return {
            "version": "4.0.0",
            "claude": {
                "projects_dir": "auto"
            },
            "plugins": {
                "claude_log": {
                    "enabled": True
                }
            },
            "middleware": {
                "privacy_filter": {
                    "enabled": True,
                    "level": "internal",
                    "dev_mode": False
                },
                "token_stats": {
                    "enabled": True
                }
            },
            "adapters": {
                "websocket": {
                    "enabled": True,
                    "host": "127.0.0.1",
                    "port": 8765
                },
                "http": {
                    "enabled": True,
                    "host": "127.0.0.1",
                    "port": 8080,
                    "cors": True
                },
                "stdout": {
                    "enabled": True,
                    "format": "simple"
                }
            }
        }
    
    def _create_plugins(self):
        """创建插件"""
        plugins_config = self.config.get('plugins', {})
        
        # ClaudeLogPlugin
        claude_log_config = plugins_config.get('claude_log', {})
        if claude_log_config.get('enabled', True):
            # 合并 Claude 配置
            claude_config = self.config.get('claude', {})
            plugin_config = {**claude_log_config, **claude_config}
            
            plugin = ClaudeLogPlugin(plugin_config)
            self.plugins.append(plugin)
    
    def _create_adapters(self):
        """创建适配器"""
        adapters_config = self.config.get('adapters', {})
        
        # WebSocket
        ws_config = adapters_config.get('websocket', {})
        if ws_config.get('enabled', True):
            adapter = WebSocketAdapter(ws_config)
            self.adapters.append(adapter)
        
        # HTTP
        http_config = adapters_config.get('http', {})
        if http_config.get('enabled', True):
            adapter = HTTPAdapter(http_config, middleware=self.middleware)
            self.adapters.append(adapter)
        
        # Stdout
        stdout_config = adapters_config.get('stdout', {})
        if stdout_config.get('enabled', True):
            adapter = StdoutAdapter(stdout_config)
            self.adapters.append(adapter)
    
    async def run(self):
        """运行应用"""
        print("=" * 60)
        print("AI-ClaudeCat v4.0")
        print("=" * 60)
        
        # 启动中间件
        await self.middleware.start()
        
        print("\n[OK] Application started successfully!")
        print("\nServices:")
        print(f"   - WebSocket: ws://127.0.0.1:8765")
        print(f"   - HTTP API:  http://127.0.0.1:8080")
        print("\nAPI Endpoints:")
        print(f"   - GET /api/status  - Current status")
        print(f"   - GET /api/tokens  - Token statistics")
        print(f"   - GET /api/health  - Health check")
        print("\nPress Ctrl+C to stop")
        print("=" * 60)
        
        # 保持运行
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
            await self.middleware.stop()
            print("\n[OK] Application stopped")


def main():
    """主函数"""
    # 创建应用
    app = Application()
    
    # 运行应用
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)


if __name__ == '__main__':
    main()
