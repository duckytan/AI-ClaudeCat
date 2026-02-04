# Claude 状态监控 - 改进调试版

import psutil
import os

print("=" * 60)
print("  Claude Status Debug (Enhanced)")
print("=" * 60)

# 1. 查找所有可能相关的进程
print("\n[1] 查找所有可能进程...")

# 扩大搜索范围
keywords = [
    "claude",
    "anthropic",
    "opencode",
    "code",
    "terminal",
    "cmd",
    "powershell",
    "bash",
    "wsl",
]

all_matching = []

for proc in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        info = proc.info
        name = info.get("name", "") or ""
        cmdline = info.get("cmdline") or []

        name_lower = name.lower()
        cmdline_str = " ".join(cmdline).lower() if cmdline else ""

        for kw in keywords:
            if kw in name_lower or kw in cmdline_str:
                all_matching.append(
                    {
                        "name": name,
                        "pid": info.get("pid"),
                        "cmdline": cmdline[:3] if cmdline else [],
                        "matched": kw,
                    }
                )
                print(f"  [MATCH] {name} (PID: {info.get('pid')}) - matched '{kw}'")
                break

    except Exception as e:
        pass

print(f"\n找到 {len(all_matching)} 个可能相关进程")

# 2. 查找窗口
print("\n[2] 查找窗口...")
try:
    import pygetwindow

    all_windows = pygetwindow.getAllTitles()
    print(f"  发现 {len(all_windows)} 个窗口")

    claude_windows = []
    for title in all_windows:
        # 打印所有窗口
        print(f"    - {title}")

        if any(
            kw in title.lower() for kw in ["ai-claude", "claude", "test2", "opencode"]
        ):
            claude_windows.append(title)

    print(f"\n可能相关的窗口: {claude_windows}")

except Exception as e:
    print(f"  错误: {e}")

# 3. 让用户选择
print("\n[3] 请选择监控目标:")
print("  A) 列出所有 Claude 相关进程")
print("  B) 列出所有窗口标题")
print("  C) 测试特定进程")
print("  D) 退出")

# 4. 分析 Claude Code 实际运行方式
print("\n[4] 快速检测...")
print("  检查 Claude Code 是如何运行的...")

# 检查是否是 OpenCode
if any(
    "opencode" in m["name"].lower() or "opencode" in str(m["cmdline"])
    for m in all_matching
):
    print("  ⚠️ 检测到 OpenCode 正在运行")
    print("     Claude Code 可能作为 OpenCode 的一部分运行")

# 检查是否是命令行运行
if any(
    m["name"] in ["cmd.exe", "powershell.exe", "bash.exe", "wsl.exe"]
    for m in all_matching
):
    print("  ⚠️ 检测到终端进程")
    print("     Claude Code 可能在终端中运行")

print("\n" + "=" * 60)
print(" 建议:")
print("  1. 确认 Claude Code 的运行方式（独立程序/终端/WSL）")
print("  2. 如果在终端中运行，需要监控终端标题")
print("  3. 如果是 OpenCode，需要匹配 'opencode' 关键词")
print("=" * 60)
