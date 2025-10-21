#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""带日志的服务器启动"""

import subprocess
import sys

# 启动服务器，将输出重定向到文件和控制台
with open('server.log', 'w', encoding='utf-8') as f:
    process = subprocess.Popen(
        [sys.executable, 'main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        bufsize=1
    )
    
    print("服务器已启动，日志输出到 server.log 和控制台")
    print("按 Ctrl+C 停止服务器")
    print("-" * 60)
    
    try:
        for line in process.stdout:
            print(line, end='')
            f.write(line)
            f.flush()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        process.terminate()
        process.wait()
        print("服务器已停止")

