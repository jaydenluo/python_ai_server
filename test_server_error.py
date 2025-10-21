#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试服务器错误"""
import subprocess
import sys
import io
import time
import requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

print("启动服务器并捕获错误...")
print("="*70)

process = subprocess.Popen(
    [sys.executable, 'main.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    bufsize=1
)

error_found = False

try:
    for line in iter(process.stdout.readline, ''):
        if line:
            print(line, end='', flush=True)
            
            # 检测错误
            if 'error' in line.lower() or 'exception' in line.lower() or 'traceback' in line.lower():
                error_found = True
            
            # 启动完成后测试API
            if "Application startup complete" in line:
                print("\n" + "="*70)
                print("等待2秒后测试API...")
                time.sleep(2)
                
                # 测试健康检查
                try:
                    print("\n测试: GET /health")
                    resp = requests.get('http://localhost:8000/health', timeout=5)
                    print(f"状态码: {resp.status_code}")
                    print(f"响应: {resp.text}")
                except Exception as e:
                    print(f"❌ 错误: {e}")
                
                # 测试根路径
                try:
                    print("\n测试: GET /")
                    resp = requests.get('http://localhost:8000/', timeout=5)
                    print(f"状态码: {resp.status_code}")
                    print(f"响应: {resp.text[:200]}")
                except Exception as e:
                    print(f"❌ 错误: {e}")
                
                print("\n" + "="*70)
                break
                
except KeyboardInterrupt:
    pass
finally:
    # 继续读取剩余输出（可能有错误信息）
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line, end='', flush=True)
            if not line:
                break
    except:
        pass
    
    process.terminate()
    process.wait()

if error_found:
    print("\n⚠️  检测到错误信息，请查看上方日志")

