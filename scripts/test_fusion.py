# -*- coding: utf-8 -*-
"""
综合状态监控系统测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.monitor import (
    create_process_monitor,
    create_file_monitor,
    create_window_monitor,
    create_fusion,
    Status,
)


def on_status_change(result):
    """状态变化回调"""
    fusion = create_fusion()
    desc = fusion.get_status_description(result.status)
    print(f"\n[STATUS CHANGED] {desc} (confidence: {result.confidence:.0%})")
    print(f"  Sources: {', '.join(result.sources.keys())}")


def main():
    print("=" * 60)
    print("  Claude Status Monitor - 综合监控系统测试")
    print("=" * 60)

    # 创建监控器
    process_monitor = create_process_monitor()
    file_monitor = create_file_monitor()
    window_monitor = create_window_monitor()

    # 创建融合器
    fusion = create_fusion()
    fusion.register_callback(on_status_change)

    # 添加监控器
    fusion.add_monitor(process_monitor)
    fusion.add_monitor(file_monitor)
    fusion.add_monitor(window_monitor)

    # 启动监控
    print("\n[INFO] 启动监控...")
    process_monitor.start()
    file_monitor.start()
    window_monitor.start()

    print("\n[INFO] 开始获取状态 (Ctrl+C 退出)")
    print("-" * 60)

    try:
        while True:
            result = fusion.get_result()

            desc = fusion.get_status_description(result.status)

            # 显示各监控源状态
            source_info = []
            for name, src_result in result.sources.items():
                src_desc = fusion.get_status_description(src_result.status)
                source_info.append(f"{name.split('Monitor')[0]}:{src_desc}")

            # 显示
            print(
                f"\r{desc:15} | Conf: {result.confidence:.0%} | {' | '.join(source_info):30}   ",
                end="",
                flush=True,
            )

            import time

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n[BYE] 退出测试")
    finally:
        # 停止监控
        process_monitor.stop()
        file_monitor.stop()
        window_monitor.stop()


if __name__ == "__main__":
    main()
