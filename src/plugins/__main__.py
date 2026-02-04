# -*- coding: utf-8 -*-
"""
插件独立运行入口

支持直接运行插件进行测试和调试。

用法：
    python -m src.plugins.claude_code         # 运行 Claude Code 插件
    python -m src.plugins.claude_code --once  # 运行一次
    python -m src.plugins.process              # 运行通用进程插件
    python -m src.plugins.process --help       # 显示帮助
"""

import argparse
import asyncio
import sys
from datetime import datetime
from typing import Optional


def create_plugin(name: str, **kwargs):
    """根据名称创建插件实例"""
    # 具体软件插件 (从 plugins/ 目录加载)
    if name == "claude_code":
        try:
            from plugins.claude_code import ClaudeCodePlugin, create_claude_code_plugin

            return create_claude_code_plugin(**kwargs)
        except ImportError:
            raise ImportError("请确保 plugins/ 目录存在且包含 claude_code.py")

    # 框架插件 (从 src/plugins/ 目录加载)
    elif name == "process":
        from .process import ProcessPlugin, create_process_plugin

        return create_process_plugin(name=name, **kwargs)

    else:
        raise ValueError(f"Unknown plugin: {name}")


def print_status(event) -> None:
    """打印状态事件"""
    timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    status_zh = {
        "unknown": "未知",
        "idle": "空闲",
        "running": "运行中",
        "thinking": "思考中",
        "working": "工作中",
        "executing": "执行命令",
        "error": "错误",
        "stopped": "已停止",
    }.get(event.status.value, event.status.value)

    # 构建输出
    details_parts = []
    if "cpu_percent" in event.details:
        details_parts.append(f"cpu: {event.details['cpu_percent']}%")
    if "process_count" in event.details:
        details_parts.append(f"进程: {event.details['process_count']}")

    details_str = f" - {', '.join(details_parts)}" if details_parts else ""

    print(
        f"[{timestamp}] {status_zh} (confidence: {event.confidence:.0%}){details_str}"
    )


async def run_plugin(
    name: str,
    interval: float,
    once: bool,
    **plugin_kwargs,
) -> None:
    """
    运行插件

    Args:
        name: 插件名称
        interval: 检测间隔（秒）
        once: 只运行一次
        plugin_kwargs: 插件额外参数
    """
    plugin = create_plugin(name, **plugin_kwargs)

    print(f"=" * 60)
    print(f"  AI-ClaudeCat Plugin - {plugin.metadata.name}")
    print(f"=" * 60)
    print(f"  Version: {plugin.metadata.version}")
    print(f"  Author: {plugin.metadata.author}")
    print(f"  Description: {plugin.metadata.description}")
    print(f"  Interval: {interval}s")
    print(f"=" * 60)
    print()

    # 检查可用性
    if not plugin.check_available():
        print(
            f"[ERROR] 目标软件不可用，请确保 {plugin.metadata.supported_software} 正在运行"
        )
        return

    # 注册回调
    plugin.register_callback(print_status)

    # 启动
    plugin.start()

    try:
        if once:
            # 只运行一次检测
            event = await plugin.detect()
            if event:
                print_status(event)
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 状态无变化")
        else:
            # 持续运行
            print("按 Ctrl+C 停止...")
            print()
            while plugin.is_running:
                event = await plugin.detect()
                if event:
                    print_status(event)
                await asyncio.sleep(interval)
    except KeyboardInterrupt:
        print("\n收到停止信号...")
    finally:
        plugin.stop()
        print(f"\n[Plugin] 已停止")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="AI-ClaudeCat Plugin - 独立运行插件进行测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m src.plugins.claude_code              # 运行 Claude Code 插件（默认）
  python -m src.plugins.claude_code --interval 1.0  # 每秒检测
  python -m src.plugins.claude_code --once       # 只检测一次
  python -m src.plugins.process --process-names node  # 监控 node 进程
        """,
    )

    parser.add_argument(
        "plugin",
        nargs="?",
        default="claude_code",
        choices=["claude_code", "process"],
        help="插件名称 (默认: claude_code)",
    )

    parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=2.0,
        help="检测间隔（秒，默认: 2.0）",
    )

    parser.add_argument(
        "--once",
        "-o",
        action="store_true",
        help="只检测一次，不持续运行",
    )

    parser.add_argument(
        "--process-names",
        "-p",
        type=str,
        default=None,
        help="进程名称列表，逗号分隔（仅 process 插件）",
    )

    args = parser.parse_args()

    # 构建插件参数
    plugin_kwargs = {"check_interval": args.interval}

    if args.plugin == "process" and args.process_names:
        plugin_kwargs["process_names"] = args.process_names.split(",")

    # 运行插件
    try:
        asyncio.run(
            run_plugin(
                name=args.plugin,
                interval=args.interval,
                once=args.once,
                **plugin_kwargs,
            )
        )
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
