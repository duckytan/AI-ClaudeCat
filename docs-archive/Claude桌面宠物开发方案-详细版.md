# Claude 桌面宠物开发方案（详细版）

> 本文档用于指导 Claude 桌面宠物项目的开发、验收和后期调整。
> 
> **核心策略**：方案三（Python + tkinter + watchdog + psutil 混合监控策略）

---

## 📋 目录

- [一、项目概述](#一项目概述)
- [二、技术架构](#二技术架构)
- [三、功能模块拆分](#三功能模块拆分)
- [四、开发任务清单](#四开发任务清单)
- [五、验收标准](#五验收标准)
- [六、风险与应对](#六风险与应对)
- [七、里程碑规划](#七里程碑规划)
- [八、后期调整指南](#八后期调整指南)

---

## 一、项目概述

### 1.1 项目目标

开发一款桌面宠物应用，实时监控 Claude Code 运行状态，并根据当前状态播放对应的动画效果，为开发者提供直观的状态反馈。

### 1.2 核心功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| **实时状态监控** | 自动检测 Claude Code 运行状态 | P0 |
| **动画反馈** | 根据状态播放对应 GIF 动画 | P0 |
| **桌面宠物** | 可爱的桌面伴侣，支持拖拽 | P0 |
| **轻量级** | 低资源消耗，后台运行 | P1 |
| **易用性** | 一键启动，无需复杂配置 | P1 |

### 1.3 技术选型

| 类别 | 选择 | 说明 |
|------|------|------|
| **语言** | Python 3.9+ | 易学易用，AI 辅助友好 |
| **GUI 框架** | tkinter | Python 内置，跨平台 |
| **进程监控** | psutil | 稳定可靠，文档完善 |
| **文件监控** | watchdog | 功能强大，支持多平台 |
| **图片处理** | Pillow | Python 图片处理标准库 |
| **配置管理** | JSON + Python | 简单易用 |

---

## 二、技术架构

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Claude 桌面宠物                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌─────────────────────┐    ┌───────────────┐  │
│  │ Claude Code │───▶│   状态监控引擎       │───▶│  桌面宠物界面  │  │
│  │ (被监控方)   │    │  (混合监控策略)      │    │  (动画显示)    │  │
│  └─────────────┘    └─────────────────────┘    └───────────────┘  │
│                            │                                        │
│                            ▼                                        │
│                   ┌──────────────────┐                              │
│                   │   状态融合器      │                              │
│                   │  (综合判断)       │                              │
│                   └──────────────────┘                              │
│                            │                                        │
│                            ▼                                        │
│                   ┌──────────────────┐                              │
│                   │   配置文件       │                              │
│                   │  (settings.json) │                              │
│                   └──────────────────┘                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块关系图

```
┌────────────────────────────────────────────────────────────┐
│                      模块依赖关系                           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌─────────────┐                          │
│                    │   main.py   │                          │
│                    │  (主入口)    │                          │
│                    └──────┬──────┘                          │
│                           │                                 │
│            ┌──────────────┼──────────────┐                  │
│            │              │              │                  │
│            ▼              ▼              ▼                  │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│   │  UI模块     │ │ 监控模块     │ │ 配置模块     │          │
│   │ pet_gui.py  │ │ monitor/     │ │ config/     │          │
│   └─────────────┘ └─────────────┘ └─────────────┘          │
│         │               │               │                   │
│         │               │               │                   │
│         ▼               ▼               ▼                   │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│   │ gif_player  │ │ file_watcher │ │ settings.py  │          │
│   │ animation_map│ │ process_watch│ │              │          │
│   └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                                 │
└────────────────────────────────────────────────────────────┘
```

### 2.3 项目目录结构

```
claude_pet/
│
├── 📁 src/                          # 源代码目录
│   │
│   ├── 📁 monitor/                  # 监控模块
│   │   ├── __init__.py
│   │   ├── base.py                 # 监控基类
│   │   ├── file_watcher.py         # 文件监控
│   │   ├── process_watcher.py      # 进程监控
│   │   └── status_fusion.py        # 状态融合
│   │
│   ├── 📁 ui/                       # UI 模块
│   │   ├── __init__.py
│   │   ├── pet_window.py           # 宠物主窗口
│   │   ├── gif_player.py           # GIF 播放
│   │   ├── animation_mapper.py     # 动画映射
│   │   └── context_menu.py         # 右键菜单
│   │
│   ├── 📁 config/                   # 配置模块
│   │   ├── __init__.py
│   │   ├── settings.py             # 配置管理
│   │   └── constants.py            # 常量定义
│   │
│   ├── 📁 utils/                   # 工具模块
│   │   ├── __init__.py
│   │   ├── logger.py              # 日志工具
│   │   └── helpers.py             # 辅助函数
│   │
│   └── main.py                     # 主程序入口
│
├── 📁 assets/                       # 资源目录
│   ├── 📁 animations/              # 动画资源
│   │   ├── idle.gif
│   │   ├── thinking.gif
│   │   ├── working.gif
│   │   ├── reading.gif
│   │   ├── writing.gif
│   │   ├── error.gif
│   │   └── celebrate.gif
│   │
│   └── 📁 icons/                   # 图标资源
│       ├── tray_icon.ico
│       └── about_icon.png
│
├── 📁 config/                       # 配置目录
│   └── settings.json               # 用户配置
│
├── 📁 logs/                         # 日志目录
│   └── pet.log
│
├── 📁 tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_monitor/
│   ├── test_ui/
│   └── test_config/
│
├── 📄 requirements.txt             # 依赖列表
├── 📄 README.md                     # 说明文档
├── 📄 CHANGELOG.md                  # 更新日志
└── 📄 .gitignore                    # Git 忽略配置
```

---

## 三、功能模块拆分

### 3.1 监控模块 (Monitor Module)

#### 3.1.1 进程监控子模块

| 功能项 | 说明 | 优先级 |
|--------|------|--------|
| **查找 Claude 进程** | 通过进程名/命令行查找 Claude Code | P0 |
| **获取 CPU 占用** | 获取单个进程的 CPU 使用率 | P0 |
| **获取内存占用** | 获取单个进程的内存使用量 | P0 |
| **获取运行时间** | 获取进程运行时长 | P1 |
| **进程状态判断** | 根据 CPU 占用判断进程状态 | P0 |
| **多实例支持** | 支持同时监控多个 Claude 实例 | P2 |

#### 3.1.2 文件监控子模块

| 功能项 | 说明 | 优先级 |
|--------|------|--------|
| **监控路径配置** | 可配置的监控路径列表 | P0 |
| **文件创建事件** | 监听文件创建事件 | P1 |
| **文件修改事件** | 监听文件修改事件 | P0 |
| **文件删除事件** | 监听文件删除事件 | P2 |
| **变更频率统计** | 统计文件变更频率 | P1 |
| **过滤规则** | 过滤无关文件变更 | P1 |

#### 3.1.3 状态融合子模块

| 功能项 | 说明 | 优先级 |
|--------|------|--------|
| **状态优先级定义** | 定义各状态的优先级顺序 | P0 |
| **多源状态融合** | 综合文件+进程状态判断 | P0 |
| **状态历史记录** | 保存最近 N 次状态变更 | P1 |
| **状态变更检测** | 检测状态变化并触发回调 | P0 |
| **置信度计算** | 计算状态判断的置信度 | P2 |

### 3.2 UI 模块 (UI Module)

#### 3.2.1 宠物窗口子模块

| 功能项 | 说明 | 优先级 |
|--------|------|--------|
| **窗口创建** | 创建无边框透明窗口 | P0 |
| **窗口置顶** | 设置窗口置顶显示 | P0 |
| **窗口拖拽** | 支持鼠标拖拽移动窗口 | P0 |
| **窗口位置保存** | 退出时保存窗口位置 | P1 |
| **窗口透明度** | 可调整窗口透明度 | P2 |
| **多显示器支持** | 支持多显示器显示 | P2 |

#### 3.2.2 GIF 播放子模块

| 功能项 | 说明 | 优先级 |
|--------|------|--------|
| **GIF 加载** | 从文件加载 GIF 动画 | P0 |
| **GIF 播放** | 播放 GIF 动画 | P0 |
| **GIF 停止** | 停止当前动画 | P0 |
| **动画切换** | 切换不同状态动画 | P0 |
| **帧率控制** | 控制动画播放速度 | P1 |
| **动画平滑切换** | 动画之间平滑过渡 | P2 |

#### 3.2.3 动画映射子模块

| 功能项 | 说明 | 优先级 |
|--------|------|--------|
| **状态→动画映射** | 定义状态到动画文件的映射 | P0 |
| **动画路径管理** | 管理动画文件路径 | P0 |
| **多动画风格** | 支持多套动画风格切换 | P2 |
| **自定义动画** | 支持用户自定义动画 | P2 |

#### 3.2.4 右键菜单子模块

| 功能项 | 说明 | 优先级 |
|--------|------|--------|
| **基础菜单** | 退出、关于等基础菜单项 | P0 |
| **设置入口** | 打开设置界面 | P1 |
| **状态查看** | 查看当前状态信息 | P1 |
| **动画预览** | 预览所有动画效果 | P2 |

### 3.3 配置模块 (Config Module)

#### 3.3.1 设置管理子模块

| 功能项 | 说明 | 优先级 |
|--------|------|-------- |
| **配置加载** | 从文件加载配置 | P0 |
| **配置保存** | 保存配置到文件 | P0 |
| **配置校验** | 校验配置有效性 | P0 |
| **默认配置** | 提供默认配置模板 | P0 |
| **配置重置** | 恢复默认配置 | P1 |

#### 3.3.2 常量定义子模块

| 功能项 | 说明 | 优先级 |
|--------|------|--------|
| **状态常量** | 定义所有状态类型 | P0 |
| **阈值常量** | 定义状态判断阈值 | P0 |
| **路径常量** | 定义默认路径 | P0 |
| **UI 常量** | 定义窗口大小、位置等 | P1 |

---

## 四、开发任务清单

### 4.1 任务总览

| 序号 | 任务名称 | 优先级 | 预估工时 | 状态 |
|------|----------|--------|----------|------|
| 1 | 项目初始化与目录结构 | P0 | 0.5h | 待开发 |
| 2 | 配置模块开发 | P0 | 1h | 待开发 |
| 3 | 常量定义 | P0 | 0.5h | 待开发 |
| 4 | 基础监控类开发 | P0 | 1h | 待开发 |
| 5 | 进程监控实现 | P0 | 1.5h | 待开发 |
| 6 | 文件监控实现 | P1 | 2h | 待开发 |
| 7 | 状态融合器开发 | P0 | 1.5h | 待开发 |
| 8 | GIF 播放组件开发 | P0 | 1h | 待开发 |
| 9 | 动画映射器开发 | P0 | 0.5h | 待开发 |
| 10 | 宠物窗口实现 | P0 | 2h | 待开发 |
| 11 | 右键菜单实现 | P0 | 1h | 待开发 |
| 12 | 主程序整合 | P0 | 1h | 待开发 |
| 13 | 基础测试用例 | P1 | 1h | 待开发 |
| 14 | 文档编写 | P1 | 1h | 待开发 |

### 4.2 详细任务说明

---

#### 任务 1：项目初始化与目录结构

**任务ID**: TASK-001
**优先级**: P0
**预估工时**: 0.5 小时

**任务描述**：
创建项目目录结构和基础文件

**输入**：
- 无

**输出**：
- [ ] 创建 `src/`、`assets/`、`config/`、`logs/`、`tests/` 目录
- [ ] 创建 `requirements.txt` 文件
- [ ] 创建 `.gitignore` 文件

**验收标准**：
- [ ] 目录结构符合设计文档
- [ ] `requirements.txt` 包含所有依赖
- [ ] `.gitignore` 正确忽略临时文件和日志

**依赖任务**：
- 无

**备注**：
- 可手动创建或使用脚本

---

#### 任务 2：配置模块开发

**任务ID**: TASK-002
**优先级**: P0
**预估工时**: 1 小时

**任务描述**：
开发配置管理模块，支持加载、保存、校验配置

**输入**：
- `config/settings.json` 配置文件模板

**输出**：
- `src/config/settings.py` - 配置管理类

**核心代码**：

```python
class Settings:
    """配置管理类"""
    
    def __init__(self):
        self.config_file = "config/settings.json"
        self.default_settings = {
            "monitor": {
                "check_interval": 2.0,
                "watch_paths": ["~/.claude/"],
                "enabled": True
            },
            "ui": {
                "window_width": 150,
                "window_height": 150,
                "opacity": 0.9,
                "always_on_top": True
            },
            "animations": {
                "frame_delay": 100,
                "default_animation": "idle.gif"
            }
        }
    
    def load(self):
        """加载配置"""
        pass
    
    def save(self):
        """保存配置"""
        pass
    
    def validate(self):
        """校验配置"""
        pass
    
    def get(self, key, default=None):
        """获取配置项"""
        pass
    
    def set(self, key, value):
        """设置配置项"""
        pass
```

**验收标准**：
- [ ] `Settings` 类能正确加载配置
- [ ] `Settings` 类能正确保存配置
- [ ] 配置缺失时使用默认值
- [ ] 单元测试覆盖率达到 80%

**依赖任务**：
- TASK-001

**备注**：
- 配置格式使用 JSON

---

#### 任务 3：常量定义

**任务ID**: TASK-003
**优先级**: P0
**预估工时**: 0.5 小时

**任务描述**：
定义项目中使用到的所有常量

**输入**：
- 无

**输出**：
- `src/config/constants.py` - 常量定义文件

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""项目常量定义"""

# ============== 状态常量 ==============
class Status:
    """状态常量"""
    NOT_RUNNING = "not_running"      # 未运行
    IDLE = "idle"                    # 空闲
    RUNNING = "running"              # 运行中
    THINKING = "thinking"            # 思考中
    WORKING = "working"              # 工作/执行中
    READING = "reading"              # 读取文件
    WRITING = "writing"             # 写入文件
    ERROR = "error"                  # 错误
    DONE = "done"                    # 完成

# ============== 阈值常量 ==============
class Thresholds:
    """状态判断阈值"""
    CPU_IDLE = 0.5                   # 空闲 CPU 阈值
    CPU_LOW = 2.0                   # 低负载阈值
    CPU_NORMAL = 10.0               # 正常负载阈值
    CPU_HIGH = 30.0                 # 高负载阈值
    
    FILE_CHANGE_QUIET = 5            # 文件变更静默阈值（秒）
    FILE_CHANGE_ACTIVE = 1          # 文件变更活跃阈值（秒）

# ============== 路径常量 ==============
class Paths:
    """路径常量"""
    CONFIG_DIR = "config/"
    ASSETS_DIR = "assets/"
    ANIMATIONS_DIR = "assets/animations/"
    ICONS_DIR = "assets/icons/"
    LOGS_DIR = "logs/"
    
    # Claude 可能的路径
    CLAUDE_PATHS = [
        "~/.claude/",
        "~/.claude-code-router/",
        "~/.config/claude/",
    ]

# ============== UI 常量 ==============
class UI:
    """UI 常量"""
    WINDOW_WIDTH = 150
    WINDOW_HEIGHT = 150
    DEFAULT_OPACITY = 0.9
    
    # 默认位置（右下角）
    DEFAULT_POSITION = "bottom_right"
```

**验收标准**：
- [ ] 常量分类清晰
- [ ] 常量命名规范
- [ ] 包含所有需要的常量
- [ ] 便于后续调整

**依赖任务**：
- 无

---

#### 任务 4：基础监控类开发

**任务ID**: TASK-004
**优先级**: P0
**预估工时**: 1 小时

**任务描述**：
开发监控模块的基类，定义统一接口

**输入**：
- 无

**输出**：
- `src/monitor/base.py` - 监控基类

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""监控基类"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable


class BaseMonitor(ABC):
    """监控基类"""
    
    def __init__(self, callback: Optional[Callable] = None):
        """
        初始化
        
        Args:
            callback: 状态变化回调函数
        """
        self.callback = callback
        self.current_status = None
        self.running = False
    
    def set_callback(self, callback: Callable):
        """
        设置回调函数
        
        Args:
            callback: 状态变化时调用的函数
        """
        self.callback = callback
    
    @abstractmethod
    def start(self):
        """
        开始监控（阻塞或非阻塞）
        """
        pass
    
    @abstractmethod
    def stop(self):
        """
        停止监控
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict:
        """
        获取当前状态
        
        Returns:
            {
                'status': str,           # 状态
                'confidence': float,     # 置信度 0-1
                'details': Dict          # 详细信息
            }
        """
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """
        检查监控是否运行中
        
        Returns:
            bool: 是否运行中
        """
        pass
```

**验收标准**：
- [ ] 抽象方法定义完整
- [ ] 接口清晰，便于实现
- [ ] 回调机制正常工作

**依赖任务**：
- TASK-003

---

#### 任务 5：进程监控实现

**任务ID**: TASK-005
**优先级**: P0
**预估工时**: 1.5 小时

**任务描述**：
实现进程监控，检测 Claude Code 的 CPU、内存使用情况

**输入**：
- `src/monitor/base.py` 基类

**输出**：
- `src/monitor/process_watcher.py` - 进程监控实现

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""进程监控模块"""

import psutil
import time
from typing import Dict, Optional, List

from .base import BaseMonitor
from ..config.constants import Status, Thresholds


class ProcessMonitor(BaseMonitor):
    """进程监控器"""
    
    def __init__(self, callback=None):
        super().__init__(callback)
        self.processes = []
        self.last_cpu_samples = {}
        self.check_interval = 2.0
    
    def find_claude_processes(self) -> List[psutil.Process]:
        """
        查找 Claude 相关进程
        
        Returns:
            List[psutil.Process]: 匹配的进程列表
        """
        claude_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                info = proc.info
                name = info.get('name', '').lower()
                cmdline = ' '.join(info.get('cmdline', []) or []).lower()
                
                # 匹配条件
                if any(keyword in name or keyword in cmdline
                      for keyword in ['claude', 'anthropic']):
                    claude_processes.append(proc)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return claude_processes
    
    def get_process_status(self) -> Dict:
        """
        获取进程状态
        
        Returns:
            Dict: 状态信息
        """
        processes = self.find_claude_processes()
        
        if not processes:
            return {
                'status': Status.NOT_RUNNING,
                'confidence': 1.0,
                'details': {
                    'process_count': 0
                }
            }
        
        # 计算总 CPU 和内存
        total_cpu = 0.0
        total_memory = 0.0
        
        for proc in processes:
            try:
                total_cpu += proc.cpu_percent()
                total_memory += proc.memory_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 判断状态
        status = self._judge_status(total_cpu, total_memory)
        
        return {
            'status': status,
            'confidence': 0.9,
            'details': {
                'process_count': len(processes),
                'cpu_percent': total_cpu,
                'memory_percent': total_memory
            }
        }
    
    def _judge_status(self, cpu: float, memory: float) -> str:
        """
        根据 CPU 和内存占用判断状态
        
        Args:
            cpu: CPU 占用百分比
            memory: 内存占用百分比
            
        Returns:
            str: 状态
        """
        if cpu < Thresholds.CPU_IDLE:
            return Status.IDLE
        elif cpu < Thresholds.CPU_LOW:
            return Status.RUNNING
        elif cpu < Thresholds.CPU_NORMAL:
            return Status.THINKING
        elif cpu < Thresholds.CPU_HIGH:
            return Status.WORKING
        else:
            return Status.WORKING
    
    def start(self):
        """启动监控"""
        self.running = True
        self._monitor_loop()
    
    def stop(self):
        """停止监控"""
        self.running = False
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            status = self.get_process_status()
            
            # 如果状态变化，触发回调
            if status['status'] != self.current_status:
                self.current_status = status['status']
                if self.callback:
                    self.callback(status)
            
            time.sleep(self.check_interval)
    
    def is_running(self) -> bool:
        """检查是否运行中"""
        return self.running
```

**验收标准**：
- [ ] 能正确识别 Claude Code 进程
- [ ] 能准确获取 CPU 占用率
- [ ] 能准确获取内存占用率
- [ ] 状态判断准确
- [ ] 支持设置检查间隔
- [ ] 单元测试覆盖率达到 80%

**依赖任务**：
- TASK-004

---

#### 任务 6：文件监控实现

**任务ID**: TASK-006
**优先级**: P1
**预估工时**: 2 小时

**任务描述**：
实现文件监控，监听 Claude 相关文件的变更

**输入**：
- `src/monitor/base.py` 基类
- 配置中的监控路径

**输出**：
- `src/monitor/file_watcher.py` - 文件监控实现

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""文件监控模块"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, Optional

from .base import BaseMonitor
from ..config.constants import Status, Paths


class FileEventHandler(FileSystemEventHandler):
    """文件事件处理器"""
    
    def __init__(self, callback):
        """
        初始化
        
        Args:
            callback: 事件回调函数
        """
        self.callback = callback
        self.last_event_time = time.time()
        self.event_count = 0
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_event(event)
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_event(event)
    
    def _handle_event(self, event):
        """处理文件事件"""
        current_time = time.time()
        
        # 过滤无关文件
        if not self._is_claude_file(event.src_path):
            return
        
        # 计算事件频率
        if current_time - self.last_event_time < 1.0:
            self.event_count += 1
        else:
            self.event_count = 1
        
        self.last_event_time = current_time
        
        # 触发回调
        if self.callback:
            self.callback({
                'type': event.event_type,
                'path': event.src_path,
                'frequency': self.event_count,
                'timestamp': current_time
            })
    
    def _is_claude_file(self, file_path: str) -> bool:
        """判断是否为 Claude 相关文件"""
        file_lower = file_path.lower()
        indicators = ['.claude', 'claude', 'session', 'log', 'tmp', 'temp']
        return any(indicator in file_lower for indicator in Indicators)


class FileMonitor(BaseMonitor):
    """文件监控器"""
    
    def __init__(self, callback=None):
        super().__init__(callback)
        self.observer = Observer()
        self.handler = None
        self.last_activity = time.time()
    
    def start(self):
        """启动文件监控"""
        self.running = True
        
        # 设置监控路径
        watch_paths = [
            os.path.expanduser(path)
            for path in Paths.CLAUDE_PATHS
            if os.path.exists(os.path.expanduser(path))
        ]
        
        # 创建事件处理器
        self.handler = FileEventHandler(self._on_file_change)
        
        # 启动观察者
        for path in watch_paths:
            self.observer.schedule(self.handler, path, recursive=True)
        
        self.observer.start()
    
    def stop(self):
        """停止文件监控"""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def _on_file_change(self, event_data: Dict):
        """文件变化回调"""
        self.last_activity = time.time()
        
        # 根据事件频率判断状态
        frequency = event_data.get('frequency', 0)
        
        if frequency > 5:
            status = Status.WORKING
        elif frequency > 1:
            status = Status.READING
        else:
            status = Status.RUNNING
        
        result = {
            'status': status,
            'confidence': 0.7,
            'details': event_data
        }
        
        if self.callback:
            self.callback(result)
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        time_since_activity = time.time() - self.last_activity
        
        if time_since_activity > Thresholds.FILE_CHANGE_QUIET:
            status = Status.IDLE
            confidence = 0.5
        elif time_since_activity > Thresholds.FILE_CHANGE_ACTIVE:
            status = Status.RUNNING
            confidence = 0.7
        else:
            status = Status.ACTIVE
            confidence = 0.9
        
        return {
            'status': status,
            'confidence': confidence,
            'details': {
                'last_activity': self.last_activity,
                'time_since_activity': time_since_activity
            }
        }
    
    def is_running(self) -> bool:
        """检查是否运行中"""
        return self.running
```

**验收标准**：
- [ ] 能监控配置路径下的文件变更
- [ ] 能过滤无关文件
- [ ] 能识别变更频率
- [ ] 状态判断合理
- [ ] 支持多路径监控
- [ ] 单元测试覆盖率达到 70%

**依赖任务**：
- TASK-004

**备注**：
- 此任务为 P1（可延后），核心功能依赖 TASK-005

---

#### 任务 7：状态融合器开发

**任务ID**: TASK-007
**优先级**: P0
**预估工时**: 1.5 小时

**任务描述**：
实现状态融合，综合多个监控源的状态

**输入**：
- `src/monitor/process_watcher.py` 进程监控
- `src/monitor/file_watcher.py` 文件监控（可选）

**输出**：
- `src/monitor/status_fusion.py` - 状态融合器

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""状态融合模块"""

from collections import deque
from typing import Dict, Optional, List
from dataclasses import dataclass

from ..config.constants import Status


@dataclass
class StatusRecord:
    """状态记录"""
    status: str
    confidence: float
    timestamp: float
    source: str  # 'process' or 'file'


class StatusFusion:
    """状态融合器"""
    
    def __init__(self):
        # 各监控源状态
        self.process_status = None
        self.file_status = None
        
        # 状态历史
        self.history = deque(maxlen=20)
        
        # 当前融合状态
        self.current_status = Status.NOT_RUNNING
        self.current_confidence = 0.0
        
        # 回调函数
        self.callbacks = []
        
        # 状态优先级（数值越大优先级越高）
        self.priority = {
            Status.NOT_RUNNING: 0,
            Status.IDLE: 1,
            Status.RUNNING: 2,
            Status.READING: 3,
            Status.WRITING: 4,
            Status.THINKING: 5,
            Status.WORKING: 6,
            Status.ERROR: 7,
            Status.DONE: 8
        }
    
    def update_process_status(self, status: Dict):
        """
        更新进程监控状态
        
        Args:
            status: 进程状态
        """
        self.process_status = status
        self._fuse_status()
    
    def update_file_status(self, status: Dict):
        """
        更新文件监控状态
        
        Args:
            status: 文件状态
        """
        self.file_status = status
        self._fuse_status()
    
    def register_callback(self, callback):
        """
        注册状态变化回调
        
        Args:
            callback: 回调函数
        """
        self.callbacks.append(callback)
    
    def _fuse_status(self):
        """融合状态"""
        # 收集所有可用状态
        candidates = []
        
        if self.process_status:
            candidates.append(self.process_status)
        
        if self.file_status:
            candidates.append(self.file_status)
        
        if not candidates:
            new_status = Status.NOT_RUNNING
            new_confidence = 1.0
        else:
            # 选择优先级最高的状态
            best = max(candidates, key=lambda x: self._calculate_weight(x))
            new_status = best['status']
            new_confidence = best['confidence']
            
            # 如果有多个源，提升置信度
            if len(candidates) > 1:
                new_confidence = min(0.95, new_confidence + 0.1)
        
        # 如果状态变化，触发回调
        if new_status != self.current_status:
            self._notify_status_change(new_status, new_confidence)
        
        # 更新当前状态
        self.current_status = new_status
        self.current_confidence = new_confidence
    
    def _calculate_weight(self, status: Dict) -> float:
        """
        计算状态权重
        
        Args:
            status: 状态字典
            
        Returns:
            float: 权重值
        """
        base_priority = self.priority.get(status['status'], 0)
        confidence = status.get('confidence', 0.5)
        
        # 综合优先级和置信度
        return base_priority * 0.7 + confidence * 0.3
    
    def _notify_status_change(self, status: str, confidence: float):
        """
        通知状态变化
        
        Args:
            status: 新状态
            confidence: 置信度
        """
        # 记录到历史
        self.history.append(StatusRecord(
            status=status,
            confidence=confidence,
            timestamp=time.time(),
            source='fusion'
        ))
        
        # 触发回调
        for callback in self.callbacks:
            try:
                callback({
                    'status': status,
                    'confidence': confidence,
                    'history': list(self.history)
                })
            except Exception as e:
                print(f"回调执行错误: {e}")
    
    def get_current_status(self) -> Dict:
        """
        获取当前融合状态
        
        Returns:
            Dict: 当前状态
        """
        return {
            'status': self.current_status,
            'confidence': self.current_confidence,
            'history': list(self.history)
        }
```

**验收标准**：
- [ ] 能正确接收各监控源的状态
- [ ] 能综合判断最终状态
- [ ] 状态变化时触发回调
- [ ] 支持置信度计算
- [ ] 状态历史记录正确
- [ ] 单元测试覆盖率达到 80%

**依赖任务**：
- TASK-005
- TASK-006（可选）

---

#### 任务 8：GIF 播放组件开发

**任务ID**: TASK-008
**优先级**: P0
**预估工时**: 1 小时

**任务描述**：
开发 GIF 动画播放组件

**输入**：
- `assets/animations/` 目录下的 GIF 文件

**输出**：
- `src/ui/gif_player.py` - GIF 播放组件

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""GIF 播放模块"""

import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
import os
from typing import Optional, Dict


class GIFPlayer:
    """GIF 播放器"""
    
    def __init__(self, label: tk.Label):
        """
        初始化
        
        Args:
            label: 显示 GIF 的标签组件
        """
        self.label = label
        self.frames = []  # GIF 帧列表
        self.current_frame = 0
        self.is_playing = False
        self.animation_thread = None
        self.frame_delay = 100  # 每帧延迟（毫秒）
        self.gif_path = None
    
    def load(self, gif_path: str) -> bool:
        """
        加载 GIF 文件
        
        Args:
            gif_path: GIF 文件路径
            
        Returns:
            bool: 是否加载成功
        """
        if not os.path.exists(gif_path):
            print(f"GIF 文件不存在: {gif_path}")
            return False
        
        try:
            self.gif_path = gif_path
            image = Image.open(gif_path)
            self.frames = []
            
            # 提取所有帧
            try:
                while True:
                    frame = image.copy()
                    # 调整大小（可选）
                    # frame = frame.resize((100, 100), Image.Resampling.LANCZOS)
                    self.frames.append(ImageTk.PhotoImage(frame))
                    image.seek(image.tell() + 1)
            except EOFError:
                pass
            
            if self.frames:
                print(f"加载 GIF 成功: {gif_path}, {len(self.frames)} 帧")
                return True
            else:
                print(f"GIF 文件为空: {gif_path}")
                return False
                
        except Exception as e:
            print(f"加载 GIF 失败: {e}")
            return False
    
    def play(self):
        """播放动画"""
        if not self.frames:
            return
        
        self.is_playing = True
        self.current_frame = 0
        
        # 停止当前播放
        if self.animation_thread and self.animation_thread.is_alive():
            self.is_playing = False
            self.animation_thread.join()
        
        # 启动新播放线程
        self.animation_thread = threading.Thread(
            target=self._play_loop,
            daemon=True
        )
        self.animation_thread.start()
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)
    
    def _play_loop(self):
        """播放循环"""
        while self.is_playing and self.frames:
            if self.current_frame < len(self.frames):
                frame = self.frames[self.current_frame]
                
                # 在主线程中更新 UI
                self.label.after(0, self.label.config, {'image': frame})
                self.current_frame += 1
            else:
                self.current_frame = 0  # 循环播放
            
            time.sleep(self.frame_delay / 1000.0)
    
    def set_frame_delay(self, delay: int):
        """
        设置帧延迟
        
        Args:
            delay: 延迟毫秒数
        """
        self.frame_delay = delay
    
    def get_frame_count(self) -> int:
        """获取帧数"""
        return len(self.frames)
```

**验收标准**：
- [ ] 能正确加载 GIF 文件
- [ ] 能正常播放动画
- [ ] 动画循环播放
- [ ] 支持播放/停止控制
- [ ] 支持帧率调整
- [ ] 不阻塞主界面

**依赖任务**：
- 无

---

#### 任务 9：动画映射器开发

**任务ID**: TASK-009
**优先级**: P0
**预估工时**: 0.5 小时

**任务描述**：
开发状态到动画文件的映射管理器

**输入**：
- `src/config/constants.py` 状态常量

**输出**：
- `src/ui/animation_mapper.py` - 动画映射器

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""动画映射模块"""

import os
from typing import Dict, Optional

from ..config.constants import Status, Paths


class AnimationMapper:
    """动画映射器"""
    
    def __init__(self, animation_dir: str = None):
        """
        初始化
        
        Args:
            animation_dir: 动画目录路径
        """
        self.animation_dir = animation_dir or Paths.ANIMATIONS_DIR
        
        # 状态到动画文件的映射
        self.status_mapping = {
            Status.NOT_RUNNING: "sleeping.gif",
            Status.IDLE: "idle.gif",
            Status.RUNNING: "running.gif",
            Status.THINKING: "thinking.gif",
            Status.READING: "reading.gif",
            Status.WRITING: "writing.gif",
            Status.WORKING: "working.gif",
            Status.ERROR: "error.gif",
            Status.DONE: "celebrate.gif"
        }
        
        # 状态描述文本
        self.status_descriptions = {
            Status.NOT_RUNNING: "Claude 未启动",
            Status.IDLE: "待机中...",
            Status.RUNNING: "运行中",
            Status.THINKING: "思考中...",
            Status.READING: "读取文件中...",
            Status.WRITING: "写入文件中...",
            Status.WORKING: "工作中...",
            Status.ERROR: "出错了",
            Status.DONE: "任务完成！"
        }
    
    def get_animation_file(self, status: str) -> str:
        """
        根据状态获取动画文件名
        
        Args:
            status: 状态
            
        Returns:
            str: 动画文件名
        """
        return self.status_mapping.get(status, "idle.gif")
    
    def get_animation_path(self, status: str) -> str:
        """
        根据状态获取动画文件完整路径
        
        Args:
            status: 状态
            
        Returns:
            str: 动画文件完整路径
        """
        animation_file = self.get_animation_file(status)
        return os.path.join(self.animation_dir, animation_file)
    
    def get_description(self, status: str) -> str:
        """
        根据状态获取描述文本
        
        Args:
            status: 状态
            
        Returns:
            str: 描述文本
        """
        return self.status_descriptions.get(status, "未知状态")
    
    def get_all_statuses(self) -> list:
        """获取所有支持的状态"""
        return list(self.status_mapping.keys())
    
    def set_animation_path(self, status: str, path: str):
        """
        自定义状态对应的动画路径
        
        Args:
            status: 状态
            path: 动画文件路径
        """
        if status in self.status_mapping:
            self.status_mapping[status] = path
    
    def check_animations(self) -> Dict[str, bool]:
        """
        检查所有动画文件是否存在
        
        Returns:
            Dict[str, bool]: 状态-是否存在映射
        """
        results = {}
        for status, animation_file in self.status_mapping.items():
            path = os.path.join(self.animation_dir, animation_file)
            results[status] = os.path.exists(path)
        return results
```

**验收标准**：
- [ ] 状态到动画映射正确
- [ ] 能获取动画文件完整路径
- [ ] 有默认动画兜底
- [ ] 支持自定义动画路径
- [ ] 能检查动画文件是否存在

**依赖任务**：
- TASK-003

---

#### 任务 10：宠物窗口实现

**任务ID**: TASK-010
**优先级**: P0
**预估工时**: 2 小时

**任务描述**：
开发桌面宠物主窗口

**输入**：
- `src/ui/gif_player.py` GIF 播放器
- `src/ui/animation_mapper.py` 动画映射器

**输出**：
- `src/ui/pet_window.py` - 宠物窗口

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""宠物窗口模块"""

import tkinter as tk
from typing import Optional, Callable

from .gif_player import GIFPlayer
from .animation_mapper import AnimationMapper
from ..config.settings import Settings


class PetWindow:
    """桌面宠物窗口"""
    
    def __init__(self, settings: Settings, on_status_change: Callable = None):
        """
        初始化
        
        Args:
            settings: 配置对象
            on_status_change: 状态变化回调
        """
        self.settings = settings
        self.on_status_change = on_status_change
        self.animation_mapper = AnimationMapper()
        
        # 创建主窗口
        self.root = tk.Tk()
        
        # 初始化 UI
        self._setup_window()
        self._create_widgets()
        self._setup_events()
        
        # 初始化 GIF 播放器
        self.gif_player = GIFPlayer(self.pet_label)
        
        # 加载默认动画
        self._load_animation("idle")
    
    def _setup_window(self):
        """设置窗口属性"""
        # 窗口标题
        self.root.title("Claude 桌面宠物")
        
        # 窗口大小
        width = self.settings.get("ui.window_width", 150)
        height = self.settings.get("ui.window_height", 150)
        self.root.geometry(f"{width}x{height}")
        
        # 无边框窗口
        self.root.overrideredirect(True)
        
        # 透明背景色
        self.root.configure(bg='black')
        
        # 窗口置顶
        if self.settings.get("ui.always_on_top", True):
            self.root.attributes('-topmost', True)
        
        # 窗口透明度
        opacity = self.settings.get("ui.opacity", 0.9)
        self.root.attributes('-alpha', opacity)
        
        # 设置透明色
        self.root.attributes('-transparentcolor', 'black')
        
        # 初始位置（右下角）
        self._move_to_corner()
    
    def _move_to_corner(self):
        """移动到屏幕角落"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        
        x = screen_width - width - 20
        y = screen_height - height - 50
        
        self.root.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """创建窗口组件"""
        # 主框架
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(expand=True, fill='both')
        
        # 宠物图像标签
        self.pet_label = tk.Label(
            self.main_frame,
            bg='black',
            image=None
        )
        self.pet_label.pack(expand=True)
        
        # 状态文本标签
        self.status_label = tk.Label(
            self.main_frame,
            text="等待连接...",
            fg='white',
            bg='black',
            font=('Arial', 8)
        )
        self.status_label.pack()
    
    def _setup_events(self):
        """设置事件绑定"""
        # 拖拽事件
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.pet_label.bind('<Button-1>', self._on_drag_start)
        self.pet_label.bind('<B1-Motion>', self._on_drag_motion)
        self.pet_label.bind('<ButtonRelease-1>', self._on_drag_stop)
    
    def _on_drag_start(self, event):
        """开始拖拽"""
        self.is_dragging = True
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()
    
    def _on_drag_motion(self, event):
        """拖拽中"""
        if self.is_dragging:
            x = event.x_root - self.drag_start_x
            y = event.y_root - self.drag_start_y
            self.root.geometry(f"+{x}+{y}")
    
    def _on_drag_stop(self, event):
        """停止拖拽"""
        self.is_dragging = False
    
    def _load_animation(self, status: str):
        """
        加载动画
        
        Args:
            status: 状态
        """
        animation_path = self.animation_mapper.get_animation_path(status)
        self.gif_player.load(animation_path)
        self.gif_player.play()
    
    def update_status(self, status: str, confidence: float = 1.0):
        """
        更新状态
        
        Args:
            status: 状态
            confidence: 置信度
        """
        # 更新动画
        self._load_animation(status)
        
        # 更新状态文本
        description = self.animation_mapper.get_description(status)
        self.status_label.config(text=description)
    
    def show(self):
        """显示窗口"""
        self.root.mainloop()
    
    def hide(self):
        """隐藏窗口"""
        self.root.withdraw()
    
    def destroy(self):
        """销毁窗口"""
        self.gif_player.stop()
        self.root.destroy()
```

**验收标准**：
- [ ] 窗口无边框、置顶、透明
- [ ] 窗口可拖拽移动
- [ ] 窗口位置保存在配置中
- [ ] 正确显示 GIF 动画
- [ ] 正确更新状态文本
- [ ] 右键菜单可用

**依赖任务**：
- TASK-002
- TASK-008
- TASK-009

---

#### 任务 11：右键菜单实现

**任务ID**: TASK-011
**优先级**: P0
**预估工时**: 1 小时

**任务描述**：
实现右键菜单功能

**输入**：
- `src/ui/pet_window.py` 宠物窗口

**输出**：
- `src/ui/context_menu.py` - 右键菜单

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""右键菜单模块"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional


class ContextMenu:
    """右键菜单"""
    
    def __init__(self, parent, callbacks: dict = None):
        """
        初始化
        
        Args:
            parent: 父窗口
            callbacks: 回调函数字典
        """
        self.parent = parent
        self.callbacks = callbacks or {}
        
        # 创建菜单
        self.menu = tk.Menu(parent, tearoff=0)
        self._build_menu()
    
    def _build_menu(self):
        """构建菜单"""
        # 状态查看
        self.menu.add_command(
            label="当前状态",
            command=self._on_show_status
        )
        
        self.menu.add_separator()
        
        # 打开设置
        self.menu.add_command(
            label="设置...",
            command=self._on_open_settings
        )
        
        self.menu.add_separator()
        
        # 关于
        self.menu.add_command(
            label="关于",
            command=self._on_show_about
        )
        
        self.menu.add_separator()
        
        # 退出
        self.menu.add_command(
            label="退出",
            command=self._on_quit
        )
    
    def popup(self, x, y):
        """
        显示菜单
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        self.menu.post(x, y)
    
    def _on_show_status(self):
        """显示状态"""
        callback = self.callbacks.get('show_status')
        if callback:
            callback()
    
    def _on_open_settings(self):
        """打开设置"""
        callback = self.callbacks.get('open_settings')
        if callback:
            callback()
    
    def _on_show_about(self):
        """显示关于"""
        messagebox.showinfo(
            "关于",
            "Claude 桌面宠物 v1.0\n\n"
            "实时监控 Claude Code 状态\n"
            "可爱动画反馈\n\n"
            "开发者：Claude"
        )
    
    def _on_quit(self):
        """退出"""
        callback = self.callbacks.get('quit')
        if callback:
            callback()
```

**验收标准**：
- [ ] 右键能弹出菜单
- [ ] 菜单项功能正常
- [ ] 关于弹窗显示正确
- [ ] 退出能正确关闭程序

**依赖任务**：
- 无

---

#### 任务 12：主程序整合

**任务ID**: TASK-012
**优先级**: P0
**预估工时**: 1 小时

**任务描述**：
整合所有模块，创建主程序入口

**输入**：
- 所有已完成模块

**输出**：
- `src/main.py` - 主程序入口

**核心代码**：

```python
# -*- coding: utf-8 -*-
"""主程序入口"""

import sys
import os
import signal

from config.settings import Settings
from monitor.process_watcher import ProcessMonitor
from monitor.status_fusion import StatusFusion
from ui.pet_window import PetWindow


class ClaudePetApp:
    """桌面宠物应用"""
    
    def __init__(self):
        # 加载配置
        self.settings = Settings()
        self.settings.load()
        
        # 初始化状态融合器
        self.status_fusion = StatusFusion()
        self.status_fusion.register_callback(self._on_status_change)
        
        # 初始化进程监控
        self.process_monitor = ProcessMonitor(
            callback=self.status_fusion.update_process_status
        )
        
        # 初始化窗口
        self.pet_window = PetWindow(
            settings=self.settings,
            on_status_change=self._on_window_status_change
        )
        
        # 设置退出处理
        self._setup_exit_handlers()
    
    def _setup_exit_handlers(self):
        """设置退出处理"""
        signal.signal(signal.SIGINT, self._on_exit)
        signal.signal(signal.SIGTERM, self._on_exit)
    
    def _on_exit(self, signum, frame):
        """退出处理"""
        self.stop()
        sys.exit(0)
    
    def _on_status_change(self, status: dict):
        """
        状态变化回调
        
        Args:
            status: 状态信息
        """
        # 更新窗口显示
        self.pet_window.update_status(
            status['status'],
            status['confidence']
        )
    
    def _on_window_status_change(self, status: str):
        """
        窗口状态变化回调
        
        Args:
            status: 状态
        """
        # 可以在这里添加额外的处理逻辑
        pass
    
    def start(self):
        """启动应用"""
        print("启动 Claude 桌面宠物...")
        
        # 启动进程监控
        self.process_monitor.start()
        
        # 显示窗口
        self.pet_window.show()
    
    def stop(self):
        """停止应用"""
        print("正在关闭...")
        
        # 停止监控
        self.process_monitor.stop()
        
        # 保存配置
        self.settings.save()
        
        # 销毁窗口
        self.pet_window.destroy()
        
        print("再见！")


def main():
    """主函数"""
    app = ClaudePetApp()
    app.start()


if __name__ == "__main__":
    main()
```

**验收标准**：
- [ ] 程序能正常启动
- [ ] 进程监控正常工作
- [ ] 窗口正常显示
- [ ] 状态能正确更新
- [ ] 程序能正常退出
- [ ] 配置能正确保存/加载

**依赖任务**：
- TASK-002
- TASK-005
- TASK-007
- TASK-010

---

#### 任务 13：基础测试用例

**任务ID**: TASK-013
**优先级**: P1
**预估工时**: 1 小时

**任务描述**：
编写基础测试用例

**输入**：
- 所有已完成模块

**输出**：
- `tests/` 目录下的测试文件

**验收标准**：
- [ ] 配置模块测试通过
- [ ] 进程监控测试通过
- [ ] 状态融合测试通过
- [ ] GIF 播放测试通过
- [ ] 整体测试覆盖率 > 60%

**依赖任务**：
- TASK-002, TASK-005, TASK-007, TASK-008

---

#### 任务 14：文档编写

**任务ID**: TASK-014
**优先级**: P1
**预估工时**: 1 小时

**任务描述**：
编写项目文档

**输入**：
- 所有已完成代码

**输出**：
- `README.md` - 项目说明文档
- `CHANGELOG.md` - 更新日志

**验收标准**：
- [ ] README 包含安装说明
- [ ] README 包含使用说明
- [ ] README 包含配置说明
- [ ] 代码注释完整
- [ ] API 文档完整

**依赖任务**：
- 所有 P0 任务完成

---

## 五、验收标准

### 5.1 功能验收

| 功能 | 验收条件 | 验收方法 |
|------|----------|----------|
| 进程检测 | 能识别 Claude Code 进程 | 手动测试 |
| CPU 监控 | 显示 CPU 占用率 | 手动测试 |
| 动画播放 | 状态变化时切换动画 | 手动测试 |
| 窗口拖拽 | 能拖拽窗口 | 手动测试 |
| 右键菜单 | 菜单功能正常 | 手动测试 |
| 配置保存 | 重启后配置保留 | 手动测试 |

### 5.2 性能验收

| 指标 | 目标值 | 验收方法 |
|------|--------|----------|
| 启动时间 | < 3 秒 | 计时测试 |
| 内存占用 | < 100 MB | 任务管理器查看 |
| CPU 占用 | < 5% | 任务管理器查看 |
| 响应延迟 | < 1 秒 | 手动测试 |

### 5.3 稳定性验收

| 场景 | 预期结果 | 验收方法 |
|------|----------|----------|
| Claude 未运行 | 显示待机动画 | 手动测试 |
| Claude 启动 | 自动检测并显示 | 手动测试 |
| Claude 关闭 | 自动切换待机 | 手动测试 |
| 长时间运行（24h） | 无崩溃 | 长期测试 |

---

## 六、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Claude 进程名变化 | 无法检测 | 支持多种进程名匹配 |
| 文件监控路径不存在 | 功能失效 | 检查路径是否存在 |
| GIF 文件损坏 | 动画异常 | 添加异常处理 |
| 跨平台问题 | 某些功能不可用 | 条件判断，优雅降级 |

---

## 七、里程碑规划

| 里程碑 | 包含任务 | 目标 | 预计时间 |
|--------|----------|------|----------|
| M1 基础框架 | TASK-001~004 | 目录结构和基础类 | 第 1 天 |
| M2 监控模块 | TASK-005~007 | 状态监控功能 | 第 2-3 天 |
| M3 UI 模块 | TASK-008~011 | 界面显示功能 | 第 4-5 天 |
| M4 整合测试 | TASK-012~014 | 完整功能测试 | 第 6-7 天 |

---

## 八、后期调整指南

### 8.1 添加新状态

1. 在 `src/config/constants.py` 中添加状态常量
2. 在 `src/ui/animation_mapper.py` 中添加状态映射
3. 在 `src/monitor/status_fusion.py` 中添加优先级
4. 准备对应的 GIF 动画文件

### 8.2 修改状态阈值

修改 `src/config/constants.py` 中的 `Thresholds` 类：

```python
class Thresholds:
    CPU_IDLE = 0.5       # 修改这里
    CPU_LOW = 2.0        # 修改这里
    # ...
```

### 8.3 添加新动画

1. 将 GIF 文件放入 `assets/animations/` 目录
2. 修改 `src/ui/animation_mapper.py` 中的映射

### 8.4 添加新监控源

1. 继承 `src/monitor/base.py` 中的 `BaseMonitor` 类
2. 实现所有抽象方法
3. 在 `src/main.py` 中注册新监控器

---

**文档版本**: v1.0
**创建日期**: 2026-02-04
**最后更新**: 2026-02-04
**作者**: Claude

---

## 附录 A：依赖版本要求

```
psutil>=5.9.0
Pillow>=9.0.0
watchdog>=3.0.0
```

## 附录 B：状态流转图

```
                    ┌──────────────┐
                    │ NOT_RUNNING  │◄─────────┐
                    └──────┬───────┘          │
                           │                  │
                    ┌──────▼───────┐          │
           ┌────────┤    IDLE     │────────┐ │
           │        └──────┬───────┘        │ │
           │               │                │ │
    ┌──────▼───────┐ ┌──────▼───────┐ ┌──────▼───────┐
    │   RUNNING    │ │   THINKING   │ │   WORKING    │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │               │                │
           │        ┌──────▼───────┐        │
           │        │   READING    │        │
           │        │   WRITING   │───────┘
           │        └──────────────┘
           │
    ┌──────▼───────┐
    │     DONE     │──────┐
    └──────────────┘      │
                          │
    ┌──────────────┐      │
    │    ERROR     │──────┘
    └──────────────┘
```

## 附录 C：常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python src/main.py

# 运行测试
python -m pytest tests/

# 代码格式化
black src/ tests/
```
