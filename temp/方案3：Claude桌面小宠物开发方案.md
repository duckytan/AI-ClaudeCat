---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e5cac4fb0ce086a1340ab0e8aebd9fc4
    PropagateID: e5cac4fb0ce086a1340ab0e8aebd9fc4
    ReservedCode1: 30440220697c5884b69a18685abc6ce220c5b2e8396f7e8f46502f9287443233c3632b5702203461dbe66d9bbf4ac010e5644b77be414a936614c456a296bf8cc30f24aaac59
    ReservedCode2: 3046022100b9e5cb12052a01caef1df517da2e7bea205cda35e95595a27f7c06c74156d5d0022100e0d56fed46bd035dae3cab3b0a3dc43d1bb210973250177c8c37ff15c233b3ef
---

# Claude桌面小宠物开发方案

## 📋 项目概述

### 项目目标
开发一款桌面小宠物应用，实时监控Claude Code运行状态，并根据当前状态播放相应的动画效果，为开发者提供直观的状态反馈。

### 核心功能
- ✅ **实时状态监控** - 自动检测Claude Code运行状态
- ✅ **动画反馈** - 根据状态播放对应GIF动画
- ✅ **桌面宠物** - 可爱的桌面伴侣，拖拽移动
- ✅ **轻量级** - 低资源消耗，后台运行
- ✅ **易用性** - 一键启动，无需复杂配置

## 🔍 技术分析

### Claude Code状态系统分析

#### 1. Claude Code状态类型
基于技术研究，Claude Code具有以下核心状态：

| 状态类型 | 触发时机 | 可监控指标 | 动画映射 |
|---------|---------|-----------|---------|
| **会话状态** | SessionStart/End | 进程启动/退出 | 启动/关闭动画 |
| **交互状态** | UserPromptSubmit | 用户输入活动 | 思考/等待动画 |
| **执行状态** | PreToolUse/PostToolUse | 工具调用频率 | 工作/打字动画 |
| **后台任务** | BackgroundTaskActive | 后台任务状态 | 忙碌动画 |
| **错误状态** | Error/Exception | 错误日志 | 错误提示动画 |

#### 2. 状态获取机制
Claude Code状态可通过多种技术方案获取：

```
方案优先级：
1. 文件系统监控 (⭐⭐ 最推荐)
2. 进程监控      (⭐⭐⭐ 推荐)
3. 终端输出监控  (⭐⭐⭐⭐ 较复杂)
4. 网络流量监控  (⭐⭐⭐⭐⭐ 最复杂)
```

### 技术实现方案对比

#### 方案A: 文件系统监控
**技术特点:**
- **实现复杂度**: ⭐⭐ (简单)
- **可靠性**: ⭐⭐⭐⭐⭐ (极高)
- **实时性**: ⭐⭐⭐⭐ (良好)
- **跨平台**: ⭐⭐⭐⭐⭐ (完美支持)

**实现原理:**
```python
# 基于文件变更检测状态
class FileSystemMonitor:
    def __init__(self):
        self.watched_paths = [
            "~/.claude/",           # Claude主目录
            "~/.claude-code-router/", # 路由器日志
            "./.claude/"            # 项目级配置
        ]
    
    def detect_status(self, file_path, change_type):
        if "log" in file_path:
            return "active"  # 日志文件变更 = 正在工作
        elif "session" in file_path:
            return "processing"  # 会话文件 = 处理中
        elif "config" in file_path:
            return "configuring"  # 配置变更
```

**优势:**
- 监控Claude Code生成的各种日志和临时文件
- 无需修改Claude Code本身
- 错误容错能力强
- 实现简单，维护成本低

#### 方案B: 进程监控
**技术特点:**
- **实现复杂度**: ⭐⭐⭐ (中等)
- **可靠性**: ⭐⭐⭐⭐ (高)
- **实时性**: ⭐⭐⭐⭐⭐ (极佳)
- **跨平台**: ⭐⭐⭐⭐ (良好)

**实现原理:**
```python
# 基于进程活动检测状态
class ProcessMonitor:
    def get_claude_activity(self):
        processes = self.find_claude_processes()
        total_cpu = sum(p.cpu_percent() for p in processes)
        total_memory = sum(p.memory_percent() for p in processes)
        
        if total_cpu > 10:
            return "high_activity"
        elif total_cpu > 2:
            return "active"
        elif processes:
            return "running"
        else:
            return "not_running"
```

**优势:**
- 实时性强，毫秒级响应
- 状态判断准确
- 资源占用监控

#### 方案C: 终端输出监控
**技术特点:**
- **实现复杂度**: ⭐⭐⭐⭐ (复杂)
- **可靠性**: ⭐⭐⭐ (中等)
- **实时性**: ⭐⭐⭐⭐⭐ (极佳)
- **跨平台**: ⭐⭐ (一般)

**实现原理:**
```python
# 解析终端输出识别状态
class TerminalMonitor:
    def parse_output(self, output):
        claude_patterns = [
            r'PostToolUse.*',
            r'Background task.*',
            r'Session.*started',
            r'\[.*\] Processing'
        ]
        
        for pattern in claude_patterns:
            if re.search(pattern, output):
                return self.map_pattern_to_status(pattern)
```

**优势:**
- 信息最详细，能识别具体操作类型
- 实时性极佳

### 推荐方案: 混合监控策略

#### 核心思路
采用**文件系统监控为主 + 进程监控为辅**的混合策略，最大化可靠性和实时性。

```python
class HybridClaudeMonitor:
    def __init__(self):
        self.file_monitor = FileSystemMonitor()
        self.process_monitor = ProcessWatcher()
        self.status_cache = {}
        
    def get_comprehensive_status(self):
        # 优先使用文件系统信息
        file_status = self.file_monitor.get_status()
        
        # 用进程信息补充验证
        process_status = self.process_monitor.get_status()
        
        # 综合判断
        return self.fuse_status(file_status, process_status)
    
    def fuse_status(self, file_status, process_status):
        if file_status == "active" and process_status in ["active", "running"]:
            return "active"
        elif file_status == "processing":
            return "processing"
        elif process_status == "not_running":
            return "not_running"
        else:
            return process_status  # 退回到进程状态
```

## 🏗️ 系统架构设计

### 整体架构
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Claude Code    │───▶│  状态监控引擎     │───▶│   桌面宠物界面    │
│   (被监控方)     │    │  (混合策略)      │    │  (动画显示)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   配置文件       │
                       │   (用户设置)     │
                       └──────────────────┘
```

### 核心模块

#### 1. 状态监控引擎 (StatusMonitor)
```python
class StatusMonitor:
    """核心状态监控引擎"""
    
    def __init__(self):
        self.file_watcher = FileSystemWatcher()
        self.process_watcher = ProcessWatcher()
        self.status_history = []
        self.callbacks = []
        
    def start_monitoring(self):
        """启动监控"""
        self.file_watcher.start()
        self.process_watcher.start()
        
    def register_callback(self, callback):
        """注册状态变化回调"""
        self.callbacks.append(callback)
        
    def notify_status_change(self, new_status):
        """通知状态变化"""
        for callback in self.callbacks:
            try:
                callback(new_status)
            except Exception as e:
                print(f"回调执行错误: {e}")
```

#### 2. 动画控制器 (AnimationController)
```python
class AnimationController:
    """动画播放控制器"""
    
    def __init__(self):
        self.gif_player = GIFPlayer()
        self.animation_mapper = AnimationMapper()
        self.current_status = "idle"
        
    def update_status(self, new_status):
        """更新状态并切换动画"""
        if new_status != self.current_status:
            self.current_status = new_status
            animation_file = self.animation_mapper.get_animation(new_status)
            self.gif_player.play(animation_file)
```

#### 3. 桌面宠物界面 (DesktopPetGUI)
```python
class DesktopPetGUI:
    """桌面宠物主界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.animation_controller = AnimationController()
        self.status_monitor = StatusMonitor()
        
    def setup_window(self):
        """设置窗口属性"""
        # 无边框、可拖拽、置顶、透明背景
        self.root.overrideredirect(True)
        self.root.configure(bg='black')
        self.root.wm_attributes('-topmost', True)
        
    def setup_drag(self):
        """设置拖拽功能"""
        # 实现窗口拖拽逻辑
        
    def start(self):
        """启动应用"""
        self.status_monitor.register_callback(
            self.animation_controller.update_status
        )
        self.status_monitor.start_monitoring()
        self.root.mainloop()
```

## 📅 开发计划

### 阶段一: 核心功能 (1-2周)

#### Day 1-2: 环境搭建
```bash
# 项目结构
claude_pet/
├── src/
│   ├── monitor/
│   │   ├── __init__.py
│   │   ├── file_watcher.py
│   │   ├── process_watcher.py
│   │   └── status_fusion.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── pet_gui.py
│   │   └── gif_player.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── main.py
├── assets/
│   └── animations/
├── tests/
└── requirements.txt
```

**任务清单:**
- [ ] 创建项目结构
- [ ] 安装依赖包 (watchdog, psutil, tkinter, pillow)
- [ ] 设置版本控制

#### Day 3-4: 基础监控
```python
# file_watcher.py
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ClaudeFileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_activity = time.time()
        
    def on_modified(self, event):
        if not event.is_directory:
            self.handle_file_change(event.src_path, "modified")
            
    def on_created(self, event):
        if not event.is_directory:
            self.handle_file_change(event.src_path, "created")
            
    def handle_file_change(self, file_path, change_type):
        # 判断是否为Claude相关文件
        if self.is_claude_file(file_path):
            status = self.classify_file_activity(file_path, change_type)
            self.callback(status)
            
    def is_claude_file(self, file_path):
        claude_indicators = ['.claude', 'claude', 'session', 'log']
        return any(indicator in file_path.lower() for indicator in claude_indicators)
        
    def classify_file_activity(self, file_path, change_type):
        if 'log' in file_path.lower():
            return 'active'
        elif 'session' in file_path.lower():
            return 'processing'
        elif 'temp' in file_path.lower():
            return 'working'
        else:
            return 'general_activity'

class FileSystemWatcher:
    def __init__(self):
        self.observer = Observer()
        self.claude_paths = [
            os.path.expanduser("~/.claude/"),
            os.path.expanduser("~/.claude-code-router/"),
            os.path.expanduser("~/.config/claude/")
        ]
        
    def start(self, callback):
        for path in self.claude_paths:
            if os.path.exists(path):
                event_handler = ClaudeFileHandler(callback)
                self.observer.schedule(event_handler, path, recursive=True)
                
        self.observer.start()
        print(f"开始监控Claude文件: {self.claude_paths}")
```

#### Day 5-6: 进程监控
```python
# process_watcher.py
import psutil
import time

class ProcessWatcher:
    def __init__(self):
        self.last_cpu_samples = {}
        
    def find_claude_processes(self):
        """查找Claude相关进程"""
        claude_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                
                # 匹配Claude进程
                if any(keyword in name or keyword in cmdline 
                      for keyword in ['claude', 'anthropic']):
                    claude_processes.append(proc)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        return claude_processes
    
    def get_process_status(self):
        """获取进程状态"""
        processes = self.find_claude_processes()
        
        if not processes:
            return "not_running"
        
        # 计算总CPU使用率
        total_cpu = sum(p.cpu_percent() for p in processes)
        total_memory = sum(p.memory_percent() for p in processes)
        
        # 状态判断逻辑
        if total_cpu > 15:
            return "high_activity"
        elif total_cpu > 5:
            return "active"
        elif total_cpu > 1:
            return "running"
        else:
            return "idle"
    
    def start(self, callback):
        """开始监控进程状态"""
        def monitor_loop():
            while True:
                try:
                    status = self.get_process_status()
                    callback(status)
                    time.sleep(3)  # 每3秒检查一次
                except Exception as e:
                    print(f"进程监控错误: {e}")
                    time.sleep(5)
        
        import threading
        threading.Thread(target=monitor_loop, daemon=True).start()
```

#### Day 7-8: 状态融合
```python
# status_fusion.py
import time
from collections import deque

class StatusFusion:
    def __init__(self):
        self.file_status = "not_running"
        self.process_status = "not_running"
        self.status_history = deque(maxlen=10)
        self.current_status = "not_running"
        self.last_change_time = time.time()
        
    def update_file_status(self, status):
        """更新文件系统状态"""
        self.file_status = status
        self.recalculate_status()
        
    def update_process_status(self, status):
        """更新进程状态"""
        self.process_status = status
        self.recalculate_status()
        
    def recalculate_status(self):
        """重新计算综合状态"""
        # 状态优先级定义
        priority_map = {
            "not_running": 0,
            "idle": 1,
            "running": 2,
            "general_activity": 3,
            "working": 4,
            "processing": 5,
            "active": 6,
            "high_activity": 7
        }
        
        # 优先级选择
        file_priority = priority_map.get(self.file_status, 0)
        process_priority = priority_map.get(self.process_status, 0)
        
        # 选择更高优先级的状态
        if file_priority >= process_priority:
            new_status = self.file_status
        else:
            new_status = self.process_status
            
        # 添加到历史记录
        self.status_history.append({
            "status": new_status,
            "timestamp": time.time(),
            "file_status": self.file_status,
            "process_status": self.process_status
        })
        
        # 如果状态发生变化，触发通知
        if new_status != self.current_status:
            self.handle_status_change(new_status)
            
    def handle_status_change(self, new_status):
        """处理状态变化"""
        self.current_status = new_status
        self.last_change_time = time.time()
        print(f"状态变化: {new_status}")
        
        # 这里可以触发UI更新等回调
        # self.callbacks.notify(new_status)
```

### 阶段二: 用户界面 (1周)

#### Day 9-10: 基础GUI
```python
# pet_gui.py
import tkinter as tk
from tkinter import ttk
import threading
import os

class DesktopPetGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.is_dragging = False
        self.last_x = 0
        self.last_y = 0
        self.current_animation = None
        
        self.setup_window()
        self.setup_drag()
        self.create_widgets()
        
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("Claude桌面小宠物")
        self.root.geometry("150x150")
        
        # 无边框窗口设置
        self.root.overrideredirect(True)
        self.root.configure(bg='black')
        
        # 窗口置顶
        self.root.wm_attributes('-topmost', True)
        
        # 设置透明度
        self.root.wm_attributes('-alpha', 0.9)
        
        # 设置窗口位置（右下角）
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 150
        window_height = 150
        x = screen_width - window_width - 20
        y = screen_height - window_height - 50
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
    def setup_drag(self):
        """设置拖拽功能"""
        def on_motion(event):
            if self.is_dragging:
                x = self.root.winfo_pointerx() - self.last_x
                y = self.root.winfo_pointery() - self.last_y
                self.root.geometry(f"+{x}+{y}")
                
        def on_click(event):
            self.is_dragging = True
            self.last_x = event.x_root - self.root.winfo_x()
            self.last_y = event.y_root - self.root.winfo_y()
            
        def on_release(event):
            self.is_dragging = False
            
        # 绑定鼠标事件
        self.root.bind('<B1-Motion>', on_motion)
        self.root.bind('<Button-1>', on_click)
        self.root.bind('<ButtonRelease-1>', on_release)
        
    def create_widgets(self):
        """创建界面组件"""
        # 宠物显示区域
        self.pet_frame = tk.Frame(self.root, bg='black')
        self.pet_frame.pack(expand=True, fill='both')
        
        # 宠物图像标签
        self.pet_label = tk.Label(
            self.pet_frame, 
            bg='black',
            text="🐱", 
            font=('Arial', 24)
        )
        self.pet_label.pack(expand=True)
        
        # 状态文本
        self.status_label = tk.Label(
            self.pet_frame,
            text="等待连接...",
            fg='white',
            bg='black',
            font=('Arial', 8)
        )
        self.status_label.pack()
        
        # 右键菜单
        self.create_context_menu()
        
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="设置", command=self.show_settings)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="关于", command=self.show_about)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="退出", command=self.root.quit)
        
        def show_menu(event):
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
                
        self.root.bind('<Button-3>', show_menu)
        
    def show_settings(self):
        """显示设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("300x200")
        settings_window.resizable(False, False)
        
        # 监控间隔设置
        tk.Label(settings_window, text="监控间隔(秒):").pack(pady=5)
        interval_var = tk.IntVar(value=3)
        tk.Scale(settings_window, from_=1, to=10, orient=tk.HORIZONTAL, 
                variable=interval_var).pack(fill='x', padx=10)
        
        # 保存按钮
        tk.Button(settings_window, text="保存", 
                 command=lambda: self.save_settings(interval_var.get())).pack(pady=10)
                 
    def show_about(self):
        """显示关于信息"""
        about_text = """Claude桌面小宠物 v1.0
        
实时监控Claude Code状态
可爱动画反馈

开发者: [你的名字]
技术支持: Claude Code状态监控"""
        
        tk.messagebox.showinfo("关于", about_text)
        
    def save_settings(self, interval):
        """保存设置"""
        # 保存到配置文件
        print(f"保存设置: 监控间隔 {interval} 秒")
        tk.messagebox.showinfo("设置", "设置已保存!")
        
    def update_status(self, status):
        """更新状态显示"""
        status_texts = {
            "not_running": "Claude未运行",
            "idle": "等待中...",
            "running": "运行中",
            "active": "工作中",
            "processing": "处理中...",
            "high_activity": "忙碌中!"
        }
        
        text = status_texts.get(status, f"状态: {status}")
        self.status_label.config(text=text)
        
    def update_animation(self, animation_name):
        """更新动画显示"""
        # 这里会集成GIF播放功能
        print(f"切换到动画: {animation_name}")
        
    def run(self):
        """运行GUI"""
        self.root.mainloop()
```

#### Day 11-12: GIF动画播放
```python
# gif_player.py
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
import os

class GIFPlayer:
    def __init__(self, label):
        self.label = label
        self.frames = []
        self.current_frame = 0
        self.is_playing = False
        self.animation_thread = None
        self.frame_delay = 100  # 每帧持续时间(ms)
        
    def load_gif(self, gif_path):
        """加载GIF文件"""
        if not os.path.exists(gif_path):
            print(f"动画文件不存在: {gif_path}")
            return False
            
        try:
            image = Image.open(gif_path)
            self.frames = []
            
            # 提取所有帧
            try:
                while True:
                    frame = image.copy()
                    # 调整大小适应标签
                    frame = frame.resize((100, 100), Image.Resampling.LANCZOS)
                    self.frames.append(ImageTk.PhotoImage(frame))
                    image.seek(image.tell() + 1)
            except EOFError:
                pass  # 已经到最后一帧
                
            if self.frames:
                print(f"成功加载GIF: {gif_path}, {len(self.frames)} 帧")
                return True
            else:
                print(f"GIF文件为空: {gif_path}")
                return False
                
        except Exception as e:
            print(f"加载GIF失败: {e}")
            return False
    
    def play(self, gif_path):
        """播放GIF动画"""
        if self.load_gif(gif_path):
            self.is_playing = True
            self.current_frame = 0
            
            # 停止当前播放
            if self.animation_thread and self.animation_thread.is_alive():
                self.is_playing = False
                self.animation_thread.join()
                
            # 启动新播放线程
            self.animation_thread = threading.Thread(target=self._play_loop, daemon=True)
            self.animation_thread.start()
    
    def _play_loop(self):
        """播放循环"""
        while self.is_playing and self.frames:
            if self.current_frame < len(self.frames):
                frame = self.frames[self.current_frame]
                
                # 在主线程中更新UI
                self.label.after(0, self.label.config, {'image': frame})
                self.current_frame += 1
            else:
                self.current_frame = 0  # 循环播放
                
            time.sleep(self.frame_delay / 1000.0)
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
```

#### Day 13-14: 动画映射
```python
# animation_mapper.py
class AnimationMapper:
    def __init__(self):
        # 状态到动画文件的映射
        self.status_mapping = {
            "not_running": "sleeping.gif",      # 睡觉
            "idle": "idle.gif",                # 待机
            "running": "watching.gif",          # 观察
            "general_activity": "thinking.gif", # 思考
            "working": "typing.gif",           # 打字
            "processing": "processing.gif",     # 处理
            "active": "active.gif",             # 活跃
            "high_activity": "busy.gif"        # 忙碌
        }
        
        # 状态描述文本
        self.status_descriptions = {
            "not_running": "Claude未启动",
            "idle": "待机中...",
            "running": "运行中",
            "general_activity": "思考中...",
            "working": "工作中...",
            "processing": "处理中...",
            "active": "活跃中!",
            "high_activity": "非常忙碌!"
        }
        
    def get_animation_file(self, status):
        """根据状态获取动画文件名"""
        return self.status_mapping.get(status, "default.gif")
        
    def get_animation_path(self, status):
        """获取动画文件完整路径"""
        animation_dir = "assets/animations"
        animation_file = self.get_animation_file(status)
        return os.path.join(animation_dir, animation_file)
        
    def get_description(self, status):
        """获取状态描述文本"""
        return self.status_descriptions.get(status, "未知状态")
        
    def get_all_statuses(self):
        """获取所有支持的状态"""
        return list(self.status_mapping.keys())
```

### 阶段三: 整合与优化 (1周)

#### Day 15-16: 主程序整合
```python
# main.py
import tkinter as tk
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.monitor.status_fusion import StatusFusion
from src.ui.gif_player import GIFPlayer
from src.ui.animation_mapper import AnimationMapper
from src.ui.pet_gui import DesktopPetGUI

class ClaudePetApp:
    def __init__(self):
        # 初始化各个组件
        self.status_monitor = StatusFusion()
        self.animation_mapper = AnimationMapper()
        self.gif_player = None
        self.gui = None
        
    def setup_components(self):
        """设置各个组件"""
        # 创建GUI
        self.gui = DesktopPetGUI()
        
        # 创建GIF播放器
        self.gif_player = GIFPlayer(self.gui.pet_label)
        
        # 注册状态变化回调
        self.status_monitor.callbacks.append(self.on_status_change)
        
    def on_status_change(self, status):
        """状态变化回调"""
        print(f"状态变化: {status}")
        
        # 更新GUI显示
        self.gui.update_status(status)
        
        # 切换动画
        animation_path = self.animation_mapper.get_animation_path(status)
        self.gif_player.play(animation_path)
        
    def start_monitoring(self):
        """启动监控"""
        # 启动文件系统监控
        self.start_file_monitoring()
        
        # 启动进程监控
        self.start_process_monitoring()
        
    def start_file_monitoring(self):
        """启动文件系统监控"""
        from src.monitor.file_watcher import FileSystemWatcher
        
        def on_file_status_change(status):
            self.status_monitor.update_file_status(status)
            
        file_watcher = FileSystemWatcher()
        file_watcher.start(on_file_status_change)
        
    def start_process_monitoring(self):
        """启动进程监控"""
        from src.monitor.process_watcher import ProcessWatcher
        
        def on_process_status_change(status):
            self.status_monitor.update_process_status(status)
            
        process_watcher = ProcessWatcher()
        process_watcher.start(on_process_status_change)
        
    def run(self):
        """运行应用"""
        self.setup_components()
        self.start_monitoring()
        self.gui.run()

if __name__ == "__main__":
    print("启动Claude桌面小宠物...")
    app = ClaudePetApp()
    app.run()
```

#### Day 17-18: 配置管理
```python
# config/settings.py
import json
import os
from pathlib import Path

class Settings:
    def __init__(self):
        self.config_file = "config/settings.json"
        self.default_settings = {
            "monitoring": {
                "file_check_interval": 1.0,
                "process_check_interval": 3.0,
                "watch_paths": [
                    "~/.claude/",
                    "~/.claude-code-router/"
                ]
            },
            "ui": {
                "window_width": 150,
                "window_height": 150,
                "window_opacity": 0.9,
                "always_on_top": True,
                "animations_path": "assets/animations"
            },
            "animations": {
                "frame_delay": 100,
                "loop_animations": True,
                "default_animation": "idle.gif"
            },
            "logging": {
                "enable_logging": True,
                "log_level": "INFO",
                "log_file": "logs/pet.log"
            }
        }
        
    def load_settings(self):
        """加载设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # 合并默认设置
                return self.merge_settings(self.default_settings, settings)
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"加载设置失败: {e}")
            return self.default_settings.copy()
            
    def save_settings(self, settings):
        """保存设置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
            print(f"设置已保存: {self.config_file}")
        except Exception as e:
            print(f"保存设置失败: {e}")
            
    def merge_settings(self, default, user):
        """合并默认设置和用户设置"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_settings(result[key], value)
            else:
                result[key] = value
                
        return result
```

#### Day 19-20: 测试与调试
```python
# tests/test_monitor.py
import unittest
import time
import threading

class TestStatusMonitor(unittest.TestCase):
    def setUp(self):
        from src.monitor.status_fusion import StatusFusion
        self.monitor = StatusFusion()
        self.status_changes = []
        
        # 注册测试回调
        def test_callback(status):
            self.status_changes.append(status)
            
        self.monitor.register_callback(test_callback)
        
    def test_status_fusion(self):
        """测试状态融合逻辑"""
        # 初始状态
        self.assertEqual(self.monitor.current_status, "not_running")
        
        # 更新文件系统状态
        self.monitor.update_file_status("active")
        self.assertEqual(self.monitor.current_status, "active")
        
        # 更新进程状态
        self.monitor.update_process_status("running")
        # 进程状态优先级更低，应该保持active
        self.assertEqual(self.monitor.current_status, "active")
        
    def test_priority_logic(self):
        """测试优先级逻辑"""
        # 高优先级状态覆盖低优先级
        self.monitor.update_process_status("running")
        self.monitor.update_file_status("active")
        self.assertEqual(self.monitor.current_status, "active")
        
        # 更高优先级
        self.monitor.update_process_status("high_activity")
        self.assertEqual(self.monitor.current_status, "high_activity")

class TestAnimationMapper(unittest.TestCase):
    def setUp(self):
        from src.ui.animation_mapper import AnimationMapper
        self.mapper = AnimationMapper()
        
    def test_status_mapping(self):
        """测试状态映射"""
        self.assertEqual(self.mapper.get_animation_file("active"), "active.gif")
        self.assertEqual(self.mapper.get_animation_file("unknown"), "default.gif")
        
    def test_descriptions(self):
        """测试描述文本"""
        self.assertEqual(self.mapper.get_description("active"), "活跃中!")

if __name__ == "__main__":
    unittest.main()
```

## 🎨 动画资源准备

### 动画列表
需要准备的GIF动画文件：

| 状态 | 文件名 | 描述 | 建议尺寸 | 建议帧数 |
|------|--------|------|----------|----------|
| **not_running** | sleeping.gif | 睡觉动画 | 100x100px | 20-30帧 |
| **idle** | idle.gif | 待机动画 | 100x100px | 10-15帧 |
| **running** | watching.gif | 观察动画 | 100x100px | 15-20帧 |
| **thinking** | thinking.gif | 思考动画 | 100x100px | 20-25帧 |
| **working** | typing.gif | 打字动画 | 100x100px | 15-20帧 |
| **processing** | processing.gif | 处理动画 | 100x100px | 25-30帧 |
| **active** | active.gif | 活跃动画 | 100x100px | 20-25帧 |
| **busy** | busy.gif | 忙碌动画 | 100x100px | 30-40帧 |

### 动画设计要求
1. **风格统一** - 像素风格或卡通风格
2. **颜色协调** - 避免过于鲜艳的颜色
3. **动作自然** - 动画循环自然流畅
4. **文件大小** - 单个GIF不超过500KB
5. **兼容性好** - 使用标准GIF格式

### 动画制作工具推荐
- **在线工具**: 
  - [GIF Maker](https://gifmaker.me/)
  - [Ezgif](https://ezgif.com/)
  - [GIF Brewery](https://gfycat.com/apps/gif-brewery)
- **桌面软件**:
  - Adobe After Effects
  - Photoshop
  - GIMP (免费)

## 🔧 部署与打包

### 依赖管理
```python
# requirements.txt
watchdog==3.0.0
psutil==5.9.6
pillow==10.0.1
tkinter-tooltip==2.1.0

# 开发依赖
pyinstaller==6.2.0
pytest==7.4.3
black==23.9.1
```

### 打包脚本
```python
# build.py
import subprocess
import os
import shutil

def build_executable():
    """构建可执行文件"""
    
    # 清理之前的构建
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
        
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=ClaudePet",
        "--icon=assets/icon.ico",
        "--add-data=assets;assets",
        "--add-data=config;config",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")
        print(result.stdout)
        
        # 复制必要文件
        if os.path.exists("dist/ClaudePet"):
            shutil.copytree("assets", "dist/ClaudePet/assets")
            shutil.copytree("config", "dist/ClaudePet/config")
            
        print("可执行文件位置: dist/ClaudePet/")
        
    except subprocess.CalledProcessError as e:
        print("构建失败!")
        print(e.stderr)

if __name__ == "__main__":
    build_executable()
```

### 安装程序
```python
# installer.py
import os
import sys
import shutil
from pathlib import Path

def install_app():
    """安装应用"""
    
    # 获取安装目录
    if sys.platform == "win32":
        install_dir = Path(os.environ.get("APPDATA", "")) / "ClaudePet"
    elif sys.platform == "darwin":
        install_dir = Path.home() / "Applications" / "ClaudePet"
    else:
        install_dir = Path.home() / ".local" / "share" / "ClaudePet"
    
    # 创建安装目录
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制文件
    current_dir = Path(__file__).parent
    
    files_to_copy = [
        "main.py",
        "src/",
        "assets/",
        "config/",
        "requirements.txt"
    ]
    
    for file_path in files_to_copy:
        src = current_dir / file_path
        dst = install_dir / file_path
        
        if src.is_file():
            shutil.copy2(src, dst)
        elif src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
    
    # 创建桌面快捷方式 (Windows)
    if sys.platform == "win32":
        create_windows_shortcut(install_dir)
    
    print(f"应用安装完成: {install_dir}")

def create_windows_shortcut(install_dir):
    """创建Windows快捷方式"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "ClaudePet.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = str(install_dir / "main.py")
        shortcut.WorkingDirectory = str(install_dir)
        shortcut.IconLocation = str(install_dir / "assets" / "icon.ico")
        shortcut.Description = "Claude桌面小宠物"
        shortcut.save()
        
    except ImportError:
        print("Windows快捷方式创建失败 (需要pywin32)")

if __name__ == "__main__":
    install_app()
```

## ⚠️ 风险评估与应对

### 技术风险

#### 1. 跨平台兼容性
**风险**: 不同操作系统文件路径和权限差异
**影响**: 中等
**应对策略**:
- 使用`pathlib`处理路径兼容性
- 实现平台特定的监控逻辑
- 添加详细的错误日志

#### 2. Claude Code版本变更
**风险**: Claude Code更新可能改变文件结构
**影响**: 中等
**应对策略**:
- 监控多个可能的路径
- 实现容错机制
- 定期更新监控逻辑

#### 3. 资源占用过高
**风险**: 持续监控可能影响系统性能
**影响**: 高
**应对策略**:
- 实现智能监控间隔
- 优化文件监控算法
- 提供性能配置选项

#### 4. 权限问题
**风险**: 无法访问某些目录或文件
**影响**: 低
**应对策略**:
- 实现权限检测
- 提供备用监控方案
- 友好的错误提示

### 项目风险

#### 1. 开发进度延期
**风险**: 技术难度超出预期
**影响**: 高
**应对策略**:
- 采用MVP开发模式
- 优先实现核心功能
- 准备简化版本

#### 2. 用户需求变更
**风险**: 功能需求发生变化
**影响**: 中等
**应对策略**:
- 保持代码模块化
- 实现配置驱动
- 定期用户反馈

## 📈 后续优化计划

### 短期优化 (1-2个月)
- [ ] 添加更多动画状态
- [ ] 优化动画切换效果
- [ ] 实现配置界面
- [ ] 添加声音效果

### 中期扩展 (3-6个月)
- [ ] 支持多实例监控
- [ ] 添加统计功能
- [ ] 实现插件系统
- [ ] 支持自定义动画

### 长期愿景 (6个月+)
- [ ] AI驱动的智能状态识别
- [ ] 云端配置同步
- [ ] 社区分享平台
- [ ] 多语言支持

## 🎯 成功指标

### 技术指标
- **启动时间**: < 3秒
- **内存占用**: < 50MB
- **CPU使用率**: < 5%
- **响应延迟**: < 1秒

### 用户体验指标
- **易用性**: 一键启动，无需配置
- **稳定性**: 24小时连续运行无崩溃
- **兼容性**: 支持主流操作系统
- **响应性**: 状态变化实时反映

## 💡 创新亮点

### 技术创新
1. **混合监控策略** - 文件系统+进程监控结合
2. **智能状态融合** - 多数据源状态判断
3. **轻量级架构** - 最小化系统资源占用

### 用户体验创新
1. **可爱化反馈** - 动画替代枯燥的状态文本
2. **桌面伴侣** - 不仅仅是工具，更是陪伴
3. **零配置启动** - 开箱即用的体验

### 生态价值
1. **开发者工具** - 提升开发体验
2. **AI时代标志** - 展示AI与人类协作的美好未来
3. **开源贡献** - 为开发者社区提供实用工具

---

## 📝 结语

这个Claude桌面小宠物项目不仅是一个技术实现，更是对AI时代人机交互方式的探索。通过可爱的动画形式，让冷冰冰的技术状态变得生动有趣，为开发者的工作增添一份乐趣。

项目的成功关键在于：
1. **保持简单** - 专注核心功能，避免过度工程化
2. **用户至上** - 始终以用户体验为优先考虑
3. **持续迭代** - 根据用户反馈不断改进
4. **开放协作** - 拥抱开源社区的贡献

希望这份方案能够帮助你实现这个有趣的项目，让Claude Code的工作状态变得生动可爱！🎉

---

**文档版本**: v1.0  
**最后更新**: 2026-02-04  
**作者**: Claude  
**联系方式**: [你的联系方式]