# Claude 桌面宠物开发 - 技术研究笔记

**创建日期**: 2026-02-04
**最后更新**: 2026-02-04

---

## 目录

- [一、psutil - 进程监控](#一psutil---进程监控)
- [二、watchdog - 文件系统监控](#二watchdog---文件系统监控)
- [三、Pillow - GIF 动画处理](#三pillow---gif-动画处理)
- [四、tkinter - 桌面宠物窗口](#四tkinter---桌面宠物窗口)
- [五、WebSocket - websockets 库](#五websocket---websockets-库)
- [六、Flask - HTTP 服务](#六flask---http-服务)
- [七、Redis - Pub/Sub](#七redis---pubsub)
- [八、Python 插件系统](#八python-插件系统)
- [九、Python 事件总线](#九python-事件总线)
- [十、asyncio 异步编程](#十asyncio-异步编程)
- [参考资源](#参考资源)

---

## 一、psutil - 进程监控

### 1.1 获取进程 CPU 占用率

```python
import psutil

# 方法1：通过 PID 获取进程
p = psutil.Process(pid)
cpu = p.cpu_percent(interval=1.0)  # interval=1.0 更准确

# 方法2：遍历所有进程查找特定进程
def find_procs_by_name(name):
    """返回匹配进程名的进程列表"""
    ls = []
    for p in psutil.process_iter(['name', 'exe', 'cmdline']):
        if name == p.info['name'] or \
                p.info['exe'] and os.path.basename(p.info['exe']) == name or \
                p.info['cmdline'] and p.info['cmdline'][0] == name:
            ls.append(p)
    return ls

# 使用示例
procs = find_procs_by_name('claude')
for p in procs:
    print(f"PID: {p.pid}, CPU: {p.cpu_percent(interval=1.0)}%")
```

### 1.2 获取进程内存占用

```python
# 内存百分比
mem_percent = p.memory_percent()

# 详细内存信息
mem_info = p.memory_info()
# .rss (Resident Set Size) - 实际使用的物理内存
# .vms (Virtual Memory Size) - 虚拟内存
```

### 1.3 查找 Claude Code 进程

```python
def find_claude_processes():
    """查找 Claude Code 相关进程"""
    claude_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            info = proc.info
            name = info.get('name', '').lower()
            cmdline = ' '.join(info.get('cmdline', []) or []).lower()
            
            # 匹配条件
            if any(keyword in name or keyword in cmdline
                  for keyword in ['claude', 'anthropic']):
                claude_procs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return claude_procs
```

### 1.4 注意事项

- `cpu_percent()` 第一次调用返回的是从进程启动到现在的累计值，需要 `interval` 参数才能获取准确的瞬时值
- 使用 `psutil.process_iter()` 时应捕获可能的异常

---

## 二、watchdog - 文件系统监控

### 2.1 基础用法

```python
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event)  # 打印所有事件

    def on_created(self, event):
        print(f"创建: {event.src_path}")

    def on_modified(self, event):
        print(f"修改: {event.src_path}")

    def on_deleted(self, event):
        print(f"删除: {event.src_path}")

# 使用
event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, path="~/.claude/", recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
finally:
    observer.stop()
    observer.join()
```

### 2.2 事件类型

| 事件类型 | 说明 |
|----------|------|
| `event.event_type` | 'created', 'deleted', 'modified', 'moved' |
| `event.src_path` | 文件路径 |
| `event.is_directory` | 是否是目录 |

### 2.3 Observer API

```python
from watchdog.observers import Observer

observer = Observer()

# 调度监控
observer.schedule(event_handler, path="~/.claude/", recursive=True)

# 启动和停止
observer.start()
# ... 监控中 ...
observer.stop()
observer.join()  # 等待线程结束
```

---

## 三、Pillow - GIF 动画处理

### 3.1 加载并播放 GIF

```python
from PIL import Image, ImageTk
import tkinter as tk

# 加载 GIF
def load_gif(path):
    """加载 GIF，返回帧列表"""
    frames = []
    with Image.open(path) as im:
        try:
            while True:
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(im.tell() + 1)
        except EOFError:
            pass  # 结束
    return frames

# 在 tkinter 中播放
def play_gif(label, frames, delay=100):
    """播放 GIF 动画"""
    def update_frame(idx):
        label.config(image=frames[idx])
        label.after(delay, update_frame, (idx + 1) % len(frames))
    update_frame(0)
```

### 3.2 提取所有帧

```python
from PIL import Image, ImageSequence

with Image.open("animation.gif") as im:
    for i, frame in enumerate(ImageSequence.Iterator(im)):
        frame.save(f"frame_{i}.png")
```

### 3.3 注意事项

- 使用 `ImageTk.PhotoImage` 在 tkinter 中显示
- 每一帧都要保存为 `PhotoImage` 对象，否则会被垃圾回收
- 播放完成后需要循环处理

---

## 四、tkinter - 桌面宠物窗口

### 4.1 透明置顶窗口

```python
import tkinter as tk

root = tk.Tk()

# 无边框窗口
root.overrideredirect(True)

# 窗口置顶
root.attributes('-topmost', True)

# 透明背景（指定透明色）
root.attributes('-transparentcolor', 'black')

# 设置透明度 (0.0-1.0)
root.attributes('-alpha', 0.9)

# 初始位置（右下角）
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = screen_width - 200
y = screen_height - 200
root.geometry(f"+{x}+{y}")
```

### 4.2 拖拽功能

```python
class DraggableWindow:
    def __init__(self, root):
        self.root = root
        self.label = tk.Label(root, text="拖拽我", bg='black')
        self.label.pack()
        
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0
        
        self.label.bind('<Button-1>', self.on_click)
        self.label.bind('<B1-Motion>', self.on_drag)
        self.label.bind('<ButtonRelease-1>', self.on_release)
    
    def on_click(self, event):
        self.is_dragging = True
        self.offset_x = event.x
        self.offset_y = event.y
    
    on_drag = lambda self, event: self.root.geometry(
        f"+{event.x_root - self.offset_x}+{event.y_root - self.offset_y}"
    ) if self.is_dragging else None
    
    def on_release(self, event):
        self.is_dragging = False
```

### 4.3 右键菜单

```python
def create_context_menu(root):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="关于", command=show_about)
    menu.add_separator()
    menu.add_command(label="退出", command=root.quit)
    
    def popup(event):
        menu.post(event.x_root, event.y_root)
    
    root.bind('<Button-3>', popup)  # 右键绑定
```

---

## 五、WebSocket - websockets 库

### 5.1 安装

```bash
pip install websockets
```

### 5.2 基础 WebSocket 服务器

```python
import asyncio
from websockets.asyncio.server import serve

async def echo(websocket):
    """回声服务器处理器"""
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(message)

async def main():
    async with serve(echo, "localhost", 8765) as server:
        print("Server started on ws://localhost:8765")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
```

### 5.3 广播到多个客户端

```python
import asyncio
from websockets.asyncio.server import serve, broadcast

CONNECTIONS = set()

async def handler(websocket):
    """注册客户端并处理消息"""
    CONNECTIONS.add(websocket)
    try:
        async for message in websocket:
            # 广播接收到的消息到所有客户端
            broadcast(CONNECTIONS, f"Broadcast: {message}")
    finally:
        CONNECTIONS.remove(websocket)

async def main():
    async with serve(handler, "localhost", 8765) as server:
        print(f"Broadcasting server on ws://localhost:8765")
        await server.serve_forever()
```

### 5.4 WebSocket 客户端

```python
import asyncio
from websockets.asyncio.client import connect

async def hello():
    async with connect("ws://localhost:8765") as websocket:
        await websocket.send("Hello, Server!")
        print(f">>> Sent: Hello, Server!")
        
        response = await websocket.recv()
        print(f"<<< Received: {response}")

if __name__ == "__main__":
    asyncio.run(hello())
```

### 5.5 官方文档

- https://websockets.readthedocs.io/

---

## 六、Flask - HTTP 服务

### 6.1 安装

```bash
pip install flask
```

### 6.2 基础 REST API

```python
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# 模拟数据
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify({"users": users, "count": len(users)})

@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user is None:
        abort(404, description="User not found")
    return jsonify(user)

@app.route("/api/users", methods=["POST"])
def create_user():
    if not request.json or "name" not in request.json:
        abort(400, description="Invalid request data")
    
    new_user = {
        "id": max(u["id"] for u in users) + 1,
        "name": request.json["name"],
        "email": request.json.get("email", "")
    }
    users.append(new_user)
    return jsonify(new_user), 201
```

### 6.3 Flask 直接返回字典（自动 JSON 序列化）

```python
@app.route("/api/state")
def get_state():
    return {
        "status": "running",
        "confidence": 0.85,
        "timestamp": 1700000000.123
    }
```

### 6.4 官方文档

- https://flask.palletsprojects.com/

---

## 七、Redis - Pub/Sub

### 7.1 安装

```bash
pip install redis
```

### 7.2 基础 Pub/Sub

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 发布者
def publisher():
    for i in range(10):
        r.publish('notifications', f'Message {i}')
        time.sleep(1)

# 订阅者
def subscriber():
    pubsub = r.pubsub()
    pubsub.subscribe('notifications', 'alerts')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Received: {message['data']}")
        if message['data'] == 'STOP':
            break
    
    pubsub.unsubscribe()
    pubsub.close()
```

### 7.3 异步 Redis Pub/Sub

```python
import asyncio
import redis.asyncio as aioredis

async def main():
    r = await aioredis.from_url(
        'redis://localhost:6379',
        encoding='utf-8',
        decode_responses=True
    )
    
    async with r.pubsub() as pubsub:
        await pubsub.subscribe('channel1')
        
        # 发布消息
        await r.publish('channel1', 'Hello')
        
        # 接收消息
        async for message in pubsub.listen():
            if message['type'] == 'message':
                print(f"Received: {message['data']}")
                break
    
    await r.close()

asyncio.run(main())
```

### 7.4 模式订阅

```python
# 订阅匹配模式的消息
pubsub = r.pubsub()
pubsub.psubscribe("channel:*")  # 匹配 channel:1, channel:2 等

# 异步模式订阅
await pubsub.psubscribe("channel:*")
```

### 7.5 官方文档

- https://redis-py.readthedocs.io/

---

## 八、Python 插件系统

### 8.1 抽象基类定义

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum
import time


class Status(Enum):
    """状态枚举"""
    UNKNOWN = "unknown"
    IDLE = "idle"
    RUNNING = "running"
    WORKING = "working"
    ERROR = "error"


class Plugin(ABC):
    """插件基类"""
    
    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.enabled = True
        self.running = False
        self.middleware = None
    
    @abstractmethod
    def check_available(self) -> bool:
        """检查目标是否可用"""
        pass
    
    @abstractmethod
    def detect(self) -> Dict:
        """检测状态"""
        pass
    
    def initialize(self, middleware):
        """初始化"""
        self.middleware = middleware
    
    def start(self):
        """启动"""
        self.running = True
    
    def stop(self):
        """停止"""
        self.running = False
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
```

### 8.2 动态加载插件（importlib）

```python
import importlib.util
import os


def load_plugin(plugin_name: str, plugin_dir: str) -> Plugin:
    """动态加载插件"""
    spec = importlib.util.spec_from_file_location(
        plugin_name,
        os.path.join(plugin_dir, f'{plugin_name}.py')
    )
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # 查找插件类
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and 
            issubclass(attr, Plugin) and 
            attr != Plugin):
            return attr()
    
    return None
```

### 8.3 插件发现和注册

```python
class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
    
    def register(self, plugin: Plugin):
        self.plugins[plugin.name] = plugin
        plugin.initialize(self)
        print(f"[PluginManager] 注册插件: {plugin.name}")
    
    def load_from_dir(self, plugin_dir: str):
        """从目录加载所有插件"""
        if not os.path.exists(plugin_dir):
            return
        
        for file in os.listdir(plugin_dir):
            if file.endswith('.py') and not file.startswith('_'):
                plugin_name = file[:-3]
                plugin = load_plugin(plugin_name, plugin_dir)
                if plugin:
                    self.register(plugin)
    
    def get_all_results(self) -> Dict[str, Dict]:
        """获取所有插件状态"""
        results = {}
        for name, plugin in self.plugins.items():
            if plugin.is_enabled() and plugin.check_available():
                try:
                    results[name] = plugin.detect()
                except Exception as e:
                    print(f"[PluginManager] 插件 {name} 错误: {e}")
        return results
```

---

## 九、Python 事件总线

### 9.1 简单事件总线实现

```python
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """事件基类"""
    type: str
    data: Dict[str, Any]
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self wildcard_handlers: List[Callable] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def subscribe_all(self, handler: Callable):
        """订阅所有事件（通配符）"""
        self.wildcard_handlers.append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """取消订阅"""
        if event_type in self.handlers:
            self.handlers[event_type].remove(handler)
    
    def publish(self, event: Event):
        """发布事件"""
        # 发送到特定类型处理器
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"[EventBus] Handler error: {e}")
        
        # 发送到通配符处理器
        for handler in self.wildcard_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[EventBus] Wildcard handler error: {e}")
```

### 9.2 事件总线使用示例

```python
# 创建事件总线
bus = EventBus()

# 定义事件处理器
def on_status_change(event):
    print(f"状态变化: {event.data}")

def on_any_event(event):
    print(f"收到事件: {event.type}")

# 订阅事件
bus.subscribe("status_change", on_status_change)
bus.subscribe_all(on_any_event)

# 发布事件
bus.publish(Event("status_change", {"status": "running", "confidence": 0.9}))
```

---

## 十、asyncio 异步编程

### 10.1 基础概念

```python
import asyncio


async def async_task(name, delay):
    """异步任务"""
    print(f"Task {name} started")
    await asyncio.sleep(delay)  # 非阻塞等待
    print(f"Task {name} completed")
    return result


async def main():
    # 并发执行多个任务
    tasks = [
        async_task("A", 1),
        async_task("B", 2),
        async_task("C", 3)
    ]
    
    # 等待所有任务完成
    results = await asyncio.gather(*tasks)
    print(f"All completed: {results}")


# 运行异步代码
asyncio.run(main())
```

### 10.2 定时任务

```python
import asyncio


async def periodic_task():
    """定期执行的任务"""
    count = 0
    while True:
        count += 1
        print(f"Task run: {count}")
        await asyncio.sleep(2)  # 每2秒执行一次


async def main():
    # 创建定时任务
    task = asyncio.create_task(periodic_task())
    
    # 主任务继续执行
    await asyncio.sleep(10)
    
    # 取消定时任务
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


asyncio.run(main())
```

### 10.3 与线程结合

```python
import asyncio
import threading


def blocking_task():
    """阻塞任务"""
    import time
    time.sleep(5)
    print("Blocking task completed")


async def main():
    # 在线程池中运行阻塞任务
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, blocking_task)
    print(f"Result: {result}")


asyncio.run(main())
```

---

## 参考资源

### 官方文档

| 库 | URL |
|----|-----|
| psutil | https://giampaolo.github.io/psutil/ |
| watchdog | https://pythonhosted.org/watchdog/ |
| Pillow | https://pillow.readthedocs.io/ |
| tkinter | https://tkdocs.com/ |
| websockets | https://websockets.readthedocs.io/ |
| Flask | https://flask.palletsprojects.com/ |
| redis-py | https://redis-py.readthedocs.io/ |

### 关键代码片段

| 功能 | 代码 |
|------|------|
| **psutil CPU 监控** | `p.cpu_percent(interval=1.0)` |
| **watchdog 监控** | `observer.schedule(handler, path, recursive=True)` |
| **GIF 帧提取** | `ImageSequence.Iterator(im)` |
| **透明窗口** | `root.attributes('-transparentcolor', 'black')` |
| **WebSocket 服务器** | `websockets.asyncio.server.serve()` |
| **WebSocket 广播** | `broadcast(CONNECTIONS, message)` |
| **Flask JSON API** | `return {"key": "value"}` |
| **Redis 发布** | `r.publish('channel', 'message')` |
| **Redis 订阅** | `pubsub.subscribe('channel')` |
| **动态加载插件** | `importlib.util.spec_from_file_location()` |

---

**最后更新**: 2026-02-04
