#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查服务器状态"""

import requests
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 检查docs页面
print("检查 /docs...")
try:
    response = requests.get("http://localhost:8000/docs", timeout=5)
    print(f"状态码: {response.status_code}")
    print(f"内容长度: {len(response.text)}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 检查openapi.json
print("\n检查 /openapi.json...")
try:
    response = requests.get("http://localhost:8000/openapi.json", timeout=5)
    print(f"状态码: {response.status_code}")
    import json
    data = response.json()
    print(f"API路径数量: {len(data.get('paths', {}))}")
    print("API路径列表:")
    for path in sorted(data.get('paths', {}).keys()):
        methods = list(data['paths'][path].keys())
        print(f"  {path}: {', '.join(methods)}")
except Exception as e:
    print(f"❌ 失败: {e}")

