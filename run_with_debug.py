# -*- coding: utf-8 -*-
"""运行主程序（带调试输出）"""

import sys
import os

# 确保使用 UTF-8 编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 导入主程序
from main import main

if __name__ == '__main__':
    print("="*80)
    print("AI-ClaudeCat v4.0 - Debug Mode")
    print("="*80)
    print("\nThis version includes detailed debug output.")
    print("You should see [DEBUG] messages when events are detected.")
    print("\nPress Ctrl+C to stop\n")
    print("="*80)
    
    main()
