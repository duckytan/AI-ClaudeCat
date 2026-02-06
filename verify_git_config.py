#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 Git 配置
"""

import subprocess
import os
from pathlib import Path

def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def main():
    print("=" * 60)
    print("Git 配置验证")
    print("=" * 60)
    print()
    
    # 1. 检查 .gitignore 是否存在
    print("1. 检查 .gitignore 文件...")
    if Path('.gitignore').exists():
        print("   [OK] .gitignore 存在")
    else:
        print("   [ERROR] .gitignore 不存在！")
        return
    
    # 2. 检查 .gitattributes 是否存在
    print("\n2. 检查 .gitattributes 文件...")
    if Path('.gitattributes').exists():
        print("   [OK] .gitattributes 存在")
    else:
        print("   [WARNING] .gitattributes 不存在")
    
    # 3. 验证 "参考项目/" 被忽略
    print("\n3. 验证 '参考项目/' 被忽略...")
    output, code = run_command('git check-ignore "参考项目/"')
    if code == 0:
        print("   [OK] '参考项目/' 已被 .gitignore 忽略")
        print(f"   规则: {output}")
    else:
        print("   [ERROR] '参考项目/' 未被忽略！")
    
    # 4. 检查 __pycache__ 是否被忽略
    print("\n4. 验证 Python 缓存被忽略...")
    output, code = run_command('git check-ignore __pycache__')
    if code == 0:
        print("   [OK] __pycache__ 已被忽略")
    else:
        print("   [WARNING] __pycache__ 未被忽略")
    
    # 5. 检查数据库文件是否被忽略
    print("\n5. 验证数据库文件被忽略...")
    output, code = run_command('git check-ignore data/history.db')
    if code == 0:
        print("   [OK] data/history.db 已被忽略")
    else:
        print("   [WARNING] data/history.db 未被忽略")
    
    # 6. 列出未追踪的文件（前 10 个）
    print("\n6. 未追踪的文件（前 10 个）:")
    output, code = run_command('git ls-files --others --exclude-standard')
    if output:
        files = output.split('\n')[:10]
        for f in files:
            print(f"   - {f}")
        if len(output.split('\n')) > 10:
            print(f"   ... 还有 {len(output.split('\n')) - 10} 个文件")
    else:
        print("   (无未追踪文件)")
    
    # 7. 检查是否有应该被忽略的文件
    print("\n7. 检查常见问题...")
    issues = []
    
    # 检查是否有 .pyc 文件
    output, _ = run_command('git ls-files "*.pyc"')
    if output:
        issues.append("发现 .pyc 文件被追踪")
    
    # 检查是否有 __pycache__
    output, _ = run_command('git ls-files "*__pycache__*"')
    if output:
        issues.append("发现 __pycache__ 被追踪")
    
    # 检查是否有数据库文件
    output, _ = run_command('git ls-files "data/*.db"')
    if output:
        issues.append("发现数据库文件被追踪")
    
    if issues:
        print("   [WARNING] 发现问题:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n   建议运行:")
        print("   git rm -r --cached .")
        print("   git add .")
        print("   git commit -m 'chore: 清理不必要的文件'")
    else:
        print("   [OK] 未发现问题")
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
