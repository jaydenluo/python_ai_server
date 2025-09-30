"""
Python AI开发框架主入口
使用注解路由系统
"""

import uvicorn
import sys
from app.framework import app, api_framework
from app.core.config.settings import config


def main():
    """主函数"""
    
    print("🚀 启动Python AI开发框架 ")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔧 路由信息: http://localhost:8000/api/v1/info")
    
    # 启动API框架
    api_framework.run(
        host=config.get("app.host", "0.0.0.0"),
        port=config.get("app.port", 8000),
        workers=config.get("app.workers", 1),
        reload=config.get("app.debug", False)
    )


if __name__ == "__main__":
    main()