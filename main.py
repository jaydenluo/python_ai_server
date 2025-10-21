"""
Python AI开发框架主入口
使用注解路由系统
"""

import uvicorn
import sys
import io

# 设置标准输出编码为 UTF-8（解决 Windows emoji 显示问题）
# 并禁用缓冲以确保日志实时显示
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

from app.framework import app, api_framework
from app.core.config.settings import config


def main():
    """主函数"""
    # 清理临时标志文件（用于控制 reload 模式下的日志重复）
    import os
    import tempfile
    flag_files = [
        os.path.join(tempfile.gettempdir(), 'python_ai_framework_init.flag'),
        os.path.join(tempfile.gettempdir(), 'python_ai_framework_scan.flag'),
    ]
    for flag_file in flag_files:
        try:
            if os.path.exists(flag_file):
                os.remove(flag_file)
        except:
            pass
    
    # 启动API框架（启动信息会在 startup 事件中统一显示）
    api_framework.run(
        host=config.get("app.host", "0.0.0.0"),
        port=config.get("app.port", 8000),
        workers=config.get("app.workers", 1),
        reload=config.get("app.debug", False)
    )


if __name__ == "__main__":
    main()