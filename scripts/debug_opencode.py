# Claude/OpenCode 状态监控调试版

import psutil
import os

print("=" * 60)
print("  OpenCode/Claude Status Debug")
print("=" * 60)

# 1. 查找 OpenCode 相关进程
print("\n[1] 查找 OpenCode 进程...")
opencode_procs = []

for proc in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        info = proc.info
        name = info.get("name", "") or ""
        cmdline = info.get("cmdline") or []

        name_lower = name.lower()
        cmdline_str = " ".join(cmdline).lower() if cmdline else ""

        # OpenCode 关键词
        if any(
            kw in name_lower or kw in cmdline_str for kw in ["opencode", "opencode-cli"]
        ):
            opencode_procs.append(
                {
                    "name": name,
                    "pid": info.get("pid"),
                    "cmdline": cmdline[:3] if cmdline else [],
                }
            )
            print(f"  [OPENCODE] {name} (PID: {info.get('pid')})")

    except Exception as e:
        pass

print(f"\n找到 {len(opencode_procs)} 个 OpenCode 进程")

# 2. 如果没找到，查找 Claude Code
if not opencode_procs:
    print("\n[2] 没找到 OpenCode，查找 Claude Code...")
    claude_procs = []

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            info = proc.info
            name = info.get("name", "") or ""
            cmdline = info.get("cmdline") or []

            name_lower = name.lower()
            cmdline_str = " ".join(cmdline).lower() if cmdline else ""

            if any(
                kw in name_lower or kw in cmdline_str
                for kw in ["claude", "anthropic", "bash", "wsl"]
            ):
                claude_procs.append(
                    {
                        "name": name,
                        "pid": info.get("pid"),
                        "cmdline": cmdline[:3] if cmdline else [],
                    }
                )
                print(f"  [CLAUDE] {name} (PID: {info.get('pid')})")

        except Exception as e:
            pass

    print(f"\n找到 {len(claude_procs)} 个 Claude 相关进程")

# 3. 查找窗口标题
print("\n[3] 查找窗口标题...")
try:
    import pygetwindow

    all_windows = pygetwindow.getAllTitles()

    # OpenCode 相关窗口
    opencode_windows = [w for w in all_windows if "opencode" in w.lower()]
    claude_windows = [
        w for w in all_windows if "claude" in w.lower() or "ai-claude" in w.lower()
    ]

    print(f"\nOpenCode 窗口 ({len(opencode_windows)}):")
    for w in opencode_windows[:5]:
        print(f"  - {w}")
        analyze_title(w)

    print(f"\nClaude 窗口 ({len(claude_windows)}):")
    for w in claude_windows[:5]:
        print(f"  - {w}")
        analyze_title(w)

except Exception as e:
    print(f"  错误: {e}")


# 4. 分析窗口标题
def analyze_title(title):
    """分析窗口标题，推断状态"""
    title_lower = title.lower()

    # 关键词检测
    patterns = {
        "Thinking": ["think", "思考", "analyz"],
        "Reading": ["read", "load", "open"],
        "Writing": ["edit", "write", "save", "modif"],
        "Executing": ["bash", "cmd", "npm", "pip", "python", "run", "exec"],
        "Done": ["done", "complete", "success", "完成"],
        "Error": ["error", "fail", "exception", "错误", "失败"],
    }

    for status, keywords in patterns.items():
        for kw in keywords:
            if kw in title_lower:
                print(f"    → {status} (关键词: {kw})")
                return

    print(f"    → Running/Idle")


# 5. 列出所有进程的详细信息
print("\n[4] OpenCode 进程详情...")
if opencode_procs:
    for p in opencode_procs[:5]:
        print(f"\n  进程: {p['name']} (PID: {p['pid']})")
        print(f"  命令行: {p['cmdline']}")

        try:
            proc = psutil.Process(p["pid"])
            cpu = proc.cpu_percent(interval=0.5)
            mem = proc.memory_info().rss / 1024 / 1024
            print(f"  CPU: {cpu}%")
            print(f"  内存: {mem:.1f} MB")
        except Exception as e:
            print(f"  无法获取信息: {e}")

print("\n" + "=" * 60)
