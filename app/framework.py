"""
Python AI开发框架主入口
集成注解路由系统
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.core.config.settings import config
from app.api.docs.openapi_generator import OpenAPIGenerator
from app.core.routing.route_registry import init_auto_registry, get_auto_registry
from app.core.middleware.auth import AuthMiddleware
from app.core.middleware.logging import LoggingMiddleware
from app.core.middleware.rate_limit import RateLimitMiddleware


class APIFramework:
    """API框架 - 支持注解路由"""
    
    def __init__(self):
        self.app = FastAPI(
            title=config.get("app.name", "Python AI Framework API"),
            description="A Python AI development framework with annotation-based routing inspired by Laravel and RuoYi.",
            version=config.get("app.version", "2.0.0"),
            openapi_url="/openapi.json",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # 设置中间件
        self._setup_middleware()
        
        # 初始化路由注册
        self._init_routes()
        
        # 设置文档
        self._setup_documentation()
    
    def _setup_middleware(self):
        """设置中间件"""
        # CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.get("cors.allow_origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # 信任主机中间件
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=config.get("app.allowed_hosts", ["*"])
        )
        
        # 自定义中间件
        self.app.add_middleware(AuthMiddleware)
        self.app.add_middleware(LoggingMiddleware)
        self.app.add_middleware(RateLimitMiddleware)
    
    def _init_routes(self):
        """初始化路由"""
        # 初始化自动路由注册
        init_auto_registry()
        
        # 基础健康检查路由
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "version": "2.0.0"}
        
        # API信息路由
        @self.app.get("/api/info")
        async def api_info():
            return {
                "name": "Python AI Framework API",
                "version": "2.0.0",
                "description": "A Python AI development framework with annotation-based routing",
                "status": "active",
                "features": [
                    "Annotation-based routing",
                    "Smart middleware system",
                    "RBAC permission control",
                    "AI model integration"
                ]
            }
        
        # 路由信息路由
        @self.app.get("/api/v1/info")
        async def route_info():
            registry = get_auto_registry()
            routes = registry.get_all_routes()
            return {
                "total_routes": len(routes),
                "routes": [
                    {
                        "name": route.name,
                        "method": route.method.value,
                        "path": route.path,
                        "prefix": route.prefix,
                        "version": route.version,
                        "middleware": route.middleware
                    }
                    for route in routes
                ]
            }
    
    def _setup_documentation(self):
        """设置API文档"""
        # 自定义OpenAPI文档
        openapi_generator = OpenAPIGenerator()
        openapi_generator.setup_documentation(self.app)
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, 
            workers: int = 1, reload: bool = False):
        """运行API框架"""
        uvicorn.run(
            "app.framework:api_framework.app",
            host=host,
            port=port,
            workers=workers,
            reload=reload
        )


# 创建API框架实例
api_framework = APIFramework()
app = api_framework.app