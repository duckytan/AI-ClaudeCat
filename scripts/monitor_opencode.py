# OpenCode 状态监控器

import psutil
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ============== 配置 ==============
OPENCODE_PATHS = [
    os.path.expanduser("~/.claude/"),
    os.path.expanduser("~/.claude-code-router/"),
    os.path.expanduser("~/.config/claude/"),
    os.path.expanduser("~/.local/share/opencode/"),
]

OPENCODE_PROCESS_NAMES = [
    "opencode-cli.exe",
    "OpenCode.exe",
    "msedgewebview2.exe",  # Electron 渲染进程
]

THRESHOLDS = {
    "idle": 1.0,
    "light": 5.0,
    "medium": 20.0,
    "heavy": 50.0,
}


# ============== 进程监控 ==============
class OpenCodeProcessMonitor:
    """OpenCode 进程监控器"""

    def __init__(self):
        self.last_cpu_samples = {}

    def find_opencode_processes(self):
        """查找 OpenCode 相关进程"""
        processes = []

        for proc in psutil.process_iter(
            ["pid", "name", "cmdline", "cpu_percent", "memory_info"]
        ):
            try:
                info = proc.info
                name = info.get("name", "") or ""
                cmdline = info.get("cmdline") or []

                # 检查是否是 OpenCode 相关进程
                if any(pn in name for pn in OPENCODE_PROCESS_NAMES):
                    processes.append(
                        {
                            "pid": info.get("pid"),
                            "name": name,
                            "cmdline": cmdline[:2],
                            "cpu": 0,  # 稍后获取
                            "memory": info.get("memory_info", {}).rss / 1024 / 1024
                            if info.get("memory_info")
                            else 0,
                        }
                    )

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes

    def get_cpu_usage(self):
        """获取总 CPU 占用"""
        procs = self.find_opencode_processes()

        if not procs:
            return 0.0, [], {}

        total_cpu = 0.0
        proc_details = []

        for p in procs:
            try:
                proc = psutil.Process(p["pid"])
                cpu = proc.cpu_percent(interval=0.3)
                p["cpu"] = cpu
                total_cpu += cpu
                proc_details.append(p)
            except:
                pass

        return total_cpu, procs, proc_details

    def get_status(self):
        """获取状态"""
        cpu, all_procs, proc_details = self.get_cpu_usage()

        if not all_procs:
            return "not_running", 0.0, {"processes": [], "message": "OpenCode 未运行"}

        # 计算状态
        if cpu < THRESHOLDS["idle"]:
            status = "idle"
        elif cpu < THRESHOLDS["light"]:
            status = "light"
        elif cpu < THRESHOLDS["medium"]:
            status = "medium"
        else:
            status = "heavy"

        # 收集详细信息
        proc_info = []
        for p in proc_details[:3]:  # 只取前3个
            proc_info.append(
                {"name": p["name"], "cpu": p["cpu"], "memory": p["memory"]}
            )

        return status, cpu, {"processes": proc_info, "total_processes": len(all_procs)}


# ============== 文件监控 ==============
class OpenCodeFileMonitor:
    """OpenCode 文件监控器"""

    def __init__(self):
        self.event_count = 0
        self.observer = None
        self.handler = None

    def start(self, callback=None):
        """启动监控"""
        self.handler = FileEventHandler(callback)
        self.observer = Observer()

        for path in OPENCODE_PATHS:
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                self.observer.schedule(self.handler, expanded, recursive=True)

        self.observer.start()
        print(f"[FileMonitor] 启动，监控 {len(OPENCODE_PATHS)} 个路径")

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def get_activity(self):
        """获取活动级别"""
        activity = self.event_count
        self.event_count = 0

        if activity == 0:
            return "none"
        elif activity < 3:
            return "low"
        elif activity < 10:
            return "medium"
        else:
            return "high"


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.event_count = 0

    def on_any_event(self, event):
        if event.is_directory:
            return

        self.event_count += 1
        if self.callback:
            self.callback({"event_count": self.event_count})


# ============== 主监控 ==============
class OpenCodeMonitor:
    """OpenCode 综合监控器"""

    def __init__(self):
        self.process_monitor = OpenCodeProcessMonitor()
        self.file_monitor = OpenCodeFileMonitor()

    def start(self, file_callback=None):
        self.file_monitor.start(file_callback)

    def stop(self):
        self.file_monitor.stop()

    def get_status(self):
        """获取综合状态"""
        # 进程状态
        proc_status, proc_cpu, proc_info = self.process_monitor.get_status()

        # 文件活动
        file_activity = self.file_monitor.get_activity()

        # 综合判断
        if proc_status == "not_running":
            status = "not_running"
            confidence = 1.0
        elif file_activity == "none" and proc_cpu < THRESHOLDS["idle"]:
            status = "idle"
            confidence = 0.9
        elif file_activity == "none":
            status = "idle" if proc_cpu < THRESHOLDS["light"] else proc_status
            confidence = 0.7
        else:
            status = proc_status
            confidence = 0.8

        return {
            "status": status,
            "confidence": confidence,
            "cpu": proc_cpu,
            "file_activity": file_activity,
            "processes": proc_info,
        }


# ============== 测试 ==============
def main():
    print("=" * 60)
    print("  OpenCode 状态监控")
    print("=" * 60)

    monitor = OpenCodeMonitor()
    monitor.start()

    try:
        while True:
            result = monitor.get_status()

            status_names = {
                "not_running": "Not Running",
                "idle": "Idle",
                "light": "Light Activity",
                "medium": "Medium Activity",
                "heavy": "Heavy Activity",
            }

            status = status_names.get(result["status"], result["status"])
            cpu = result["cpu"]
            file_act = result["file_activity"]

            print(
                f"\r{status:20} | CPU: {cpu:5.1f}% | File: {file_act:6} | Procs: {len(result['processes'])}    ",
                end="",
                flush=True,
            )

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nBye!")
    finally:
        monitor.stop()


if __name__ == "__main__":
    main()
