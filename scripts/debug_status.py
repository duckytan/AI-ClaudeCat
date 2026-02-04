# Claude 状态监控调试版

import psutil
import os

print("=" * 60)
print("  Claude Status Debug")
print("=" * 60)

# 1. 测试进程查找
print("\n[1] 测试进程查找...")
found_processes = []

for proc in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        info = proc.info
        name = info.get("name", "") or ""
        cmdline = info.get("cmdline") or []

        name_lower = name.lower()
        cmdline_str = " ".join(cmdline).lower() if cmdline else ""

        # 打印所有进程名（调试用）
        if "python" in name_lower or "code" in name_lower or "terminal" in name_lower:
            print(f"  发现进程: {name}")
            print(f"    PID: {info.get('pid')}")
            print(f"    Cmdline: {cmdline[:2] if cmdline else []}")

        # 检查是否 Claude 相关
        if any(kw in name_lower or kw in cmdline_str for kw in ["claude", "anthropic"]):
            found_processes.append(proc)
            print(f"  [MATCH] {name} (PID: {info.get('pid')})")

    except Exception as e:
        pass

print(f"\n找到 {len(found_processes)} 个 Claude 相关进程")

# 2. 测试 CPU 占用
if found_processes:
    print("\n[2] 测试 CPU 占用...")
    for p in found_processes:
        try:
            cpu = p.cpu_percent(interval=1.0)
            print(f"  PID {p.pid}: CPU = {cpu}%")
        except Exception as e:
            print(f"  错误: {e}")

# 3. 测试窗口标题
print("\n[3] 测试窗口标题...")
try:
    import pygetwindow

    all_windows = pygetwindow.getAllTitles()
    print(f"  发现 {len(all_windows)} 个窗口")

    for title in all_windows:
        if any(
            kw in title.lower()
            for kw in ["claude", "code", "terminal", "cmd", "powershell"]
        ):
            print(f"  [?] {title}")

            # 分析标题关键词
            title_lower = title.lower()
            if "thinking" in title_lower:
                print("     → 包含 'thinking' → thinking")
            if "reading" in title_lower or "read" in title_lower:
                print("     → 包含 'reading' → reading")
            if "edit" in title_lower or "write" in title_lower:
                print("     → 包含 'edit/write' → writing")
            if "bash" in title_lower or "cmd" in title_lower:
                print("     → 包含 'bash/cmd' → executing")
            if "done" in title_lower or "complete" in title_lower:
                print("     → 包含 'done' → done")
            if "error" in title_lower or "fail" in title_lower:
                print("     → 包含 'error' → error")

except ImportError:
    print("  pygetwindow 未安装")
except Exception as e:
    print(f"  错误: {e}")

# 4. 测试文件路径
print("\n[4] 测试监控路径...")
paths = [
    os.path.expanduser("~/.claude/"),
    os.path.expanduser("~/.claude-code-router/"),
    os.path.expanduser("~/.config/claude/"),
]

for path in paths:
    expanded = os.path.expanduser(path)
    exists = os.path.exists(expanded)
    print(f"  {path}: {'存在' if exists else '不存在'}")
    if exists:
        try:
            files = os.listdir(expanded)
            print(f"    文件: {files[:5]}...")
        except:
            print(f"    无法列出文件")

print("\n" + "=" * 60)
print(" 调试完成")
print("=" * 60)
