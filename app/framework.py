"""
Python AI开发框架主入口
集成注解路由系统
"""

import sys
import io

# 设置UTF-8输出（必须在最开始，避免Windows emoji错误）
if sys.platform == 'win32' and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.core.config.settings import config
from app.core.docs.openapi_generator import OpenAPIGenerator
from app.core.routing.route_registry import init_fastapi_registry as init_auto_registry, get_fastapi_registry as get_auto_registry
from app.core.middleware.fastapi_auth import FastAPIAuthMiddleware
from app.core.middleware.fastapi_logging import FastAPILoggingMiddleware
from app.core.middleware.fastapi_rate_limit import FastAPIRateLimitMiddleware
from app.core.database.migrations import migrate, migration_status
from app.core.database import init_database


def _should_suppress_init_logs() -> bool:
    """
    判断是否应该抑制初始化日志（避免 reload 模式重复）
    
    在 reload 模式下：
    - 主进程第1次加载时：创建标志文件，返回 True（抑制日志）
    - 工作进程第2次加载时：检测到标志文件存在，返回 False（显示日志）
    
    在非 reload 模式下：
    - 直接返回 False（显示日志）
    """
    import os
    import tempfile
    
    # 使用临时文件作为标志
    flag_file = os.path.join(tempfile.gettempdir(), 'python_ai_framework_init.flag')
    
    # 如果标志文件存在，说明是工作进程（第2次加载），应该显示日志
    if os.path.exists(flag_file):
        return False  # 不抑制，显示日志
    else:
        # 第1次加载，创建标志文件
        try:
            with open(flag_file, 'w') as f:
                f.write('1')
        except:
            pass
        return True  # 抑制日志


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
        
        # 注册启动事件（在初始化时注册）
        self._register_startup_event()
        
        # 初始化数据库和迁移
        self._init_database()
        
        # 设置中间件
        self._setup_middleware()
        
        # 初始化路由注册
        self._init_routes()
        
        # 设置文档
        self._setup_documentation()
        
        # 添加根路由
        self._add_welcome_route()
    
    def _add_welcome_route(self):
        """添加欢迎路由"""
        @self.app.get("/", tags=["System"])
        async def welcome():
            """欢迎页面"""
            return {
                "message": "Welcome to Python AI Framework",
                "version": config.get("app.version", "2.0.0"),
                "docs": "/docs",
                "api_info": "/api/info",
                "health": "/health"
            }
    
    def _register_startup_event(self):
        """注册启动完成事件"""
        # 使用装饰器注册 startup 事件
        @self.app.on_event("startup")
        async def startup_complete():
            """启动完成后显示友好信息"""
            import asyncio
            import sys
            
            # 等待一小段时间确保 uvicorn 的启动信息已经打印
            await asyncio.sleep(0.3)
            
            # 从环境变量或全局状态读取配置
            import os
            port = os.environ.get('_APP_PORT', '8000')
            local_ip = os.environ.get('_APP_LOCAL_IP', '127.0.0.1')
            
            # 强制刷新输出
            startup_msg = f"""
{"="*70}
🎉 服务已正常启动，等待访问
{"="*70}
📡 本地访问: http://localhost:{port}
{f"📡 局域网访问: http://{local_ip}:{port}" if local_ip and local_ip != '127.0.0.1' else ""}
📖 API 文档: http://localhost:{port}/docs
📖 ReDoc 文档: http://localhost:{port}/redoc
{"="*70}
💡 按 Ctrl+C 停止服务器

"""
            print(startup_msg, flush=True)
    
    def _init_database(self):
        """初始化数据库和迁移"""
        # 只在工作进程中打印日志（避免 reload 模式重复）
        should_log = not _should_suppress_init_logs()
        
        try:
            # 获取数据库配置
            db_config = config.get_database_config()
            
            # 初始化数据库连接（静默）
            db_manager = init_database()
            
            # 测试连接
            if not db_manager.test_connection():
                # 连接失败时才显示详细信息
                if should_log:
                    print(f"❌ 数据库连接失败 ({db_config.type.value}://{db_config.host}:{db_config.port}/{db_config.database})")
                self._print_database_troubleshooting(db_config)
                return
            
            # 连接成功 - 简洁提示（只在工作进程打印）
            if should_log:
                print("✅ 数据库连接成功")
            
            # 检查是否需要自动迁移
            auto_migrate = db_config.auto_migrate
            if auto_migrate:
                print("🔄 执行数据库迁移...")
                migrate()
                print("✅ 数据库迁移完成")
                
        except Exception as e:
            print(f"⚠️  数据库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            self._print_database_troubleshooting(config.get_database_config())
    
    def _get_database_info(self, db_config):
        """获取数据库配置信息（隐藏敏感信息）"""
        if db_config.type.value == "sqlite":
            return f"SQLite: {db_config.sqlite_path}"
        else:
            return f"{db_config.type.value}://{db_config.host}:{db_config.port}/{db_config.database}"
    
    def _print_database_troubleshooting(self, db_config):
        """打印数据库故障排除指南"""
        print("\n" + "="*60)
        print("🔧 数据库连接故障排除指南")
        print("="*60)
        
        if db_config.type.value == "sqlite":
            print("\n📁 SQLite 数据库问题:")
            print(f"   当前配置: {db_config.sqlite_path}")
            print("   可能原因:")
            print("   1. 文件路径不存在或无法访问")
            print("   2. 权限不足")
            print("   3. 磁盘空间不足")
            print("\n   解决方案:")
            print("   1. 检查文件路径是否正确")
            print("   2. 确保有写入权限")
            print("   3. 检查磁盘空间")
            print(f"   4. 手动创建目录: mkdir -p {db_config.sqlite_path.rsplit('/', 1)[0] if '/' in db_config.sqlite_path else '.'}")
            
        elif db_config.type.value == "postgresql":
            print("\n🐘 PostgreSQL 数据库问题:")
            print(f"   当前配置: {db_config.host}:{db_config.port}/{db_config.database}")
            print(f"   用户名: {db_config.username}")
            print(f"   密码: {db_config.password}")
            
        elif db_config.type.value == "mysql":
            print("\n🐬 MySQL 数据库问题:")
            print(f"   当前配置: {db_config.host}:{db_config.port}/{db_config.database}")
            print(f"   用户名: {db_config.username}")
            print(f"   密码: {db_config.password}")
            
        elif db_config.type.value == "mongodb":
            print("\n🍃 MongoDB 数据库问题:")
            print(f"   当前配置: {db_config.host}:{db_config.port}/{db_config.database}")
            print(f"   用户名: {db_config.username}")
            print(f"   密码: {db_config.password}")
        
        print("\n📝 配置文件修改:")
        print("   编辑 config.yaml 文件:")
        print("   ```yaml")
        if db_config.type.value == "sqlite":
            print("   database:")
            print("     type: sqlite")
            print("     sqlite_path: ./database.db  # 修改为正确的路径")
        else:
            print("   database:")
            print(f"     type: {db_config.type.value}")
            print(f"     host: {db_config.host}")
            print(f"     port: {db_config.port}")
            print(f"     database: {db_config.database}")
            print(f"     username: {db_config.username}")
            print("     password: your_password_here")
        print("   ```")
        
        print("\n🔧 环境变量设置:")
        print("   如果使用环境变量覆盖密码:")
        print("   ```bash")
        print("   export DB_PASSWORD=your_secure_password")
        print("   ```")
        
        print("\n📚 更多帮助:")
        print("   - 查看配置示例: config.example.yaml")
        print("   - 查看文档: README.md")
        print("   - 运行示例: python examples/database_config_examples.py")
        print("="*60)
    
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
        
        # FastAPI 兼容的自定义中间件
        self.app.add_middleware(
            FastAPIAuthMiddleware,
            secret_key=config.get("auth.secret_key", "your-secret-key-here"),
            algorithm=config.get("auth.algorithm", "HS256"),
            token_expire_hours=config.get("auth.token_expire_hours", 24)
        )
        
        self.app.add_middleware(
            FastAPILoggingMiddleware,
            logger_name=config.get("logging.logger_name", "fastapi"),
            log_level=config.get("logging.level", "INFO")
        )
        
        self.app.add_middleware(
            FastAPIRateLimitMiddleware,
            requests_per_minute=config.get("rate_limit.requests_per_minute", 60),
            requests_per_hour=config.get("rate_limit.requests_per_hour", 1000),
            requests_per_day=config.get("rate_limit.requests_per_day", 10000),
            burst_limit=config.get("rate_limit.burst_limit", 100)
        )
    
    def _init_routes(self):
        """初始化路由"""
        # 初始化自动路由注册（基于装饰器的控制器）
        registry = init_auto_registry(self.app)
        registry.register_from_decorators()  # 注册所有装饰器路由
        
        # 手动注册标准 FastAPI 路由（来自 app/api/v1）
        self._register_fastapi_routes()
        
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
            routes = registry.get_route_info()
            return {
                "total_routes": len(routes),
                "routes": routes
            }
    
    def _register_fastapi_routes(self):
        """注册标准 FastAPI 路由（旧版兼容）"""
        # 新版使用装饰器自动注册，不需要手动注册
        # 如果需要兼容旧的 app/api/v1 路由，可以取消注释下面的代码
        # try:
        #     from app.api.v1 import api_router
        #     self.app.include_router(api_router, prefix="/api/v1")
        #     print("✅ 注册标准 API 路由: /api/v1")
        # except Exception as e:
        #     print(f"⚠️  注册标准 API 路由失败: {e}")
        pass
    
    def _setup_documentation(self):
        """设置API文档"""
        # 自定义OpenAPI文档
        openapi_generator = OpenAPIGenerator()
        # 生成文档（如果需要的话可以保存到文件）
        # openapi_generator.save_documentation("docs/openapi.json")
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, 
            workers: int = 1, reload: bool = False):
        """运行API框架"""
        from app.core.config.settings import config
        import socket
        import os
        
        # 获取本机实际IP地址
        def get_local_ip():
            try:
                # 创建一个UDP socket来获取本机IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                return local_ip
            except:
                return "127.0.0.1"
        
        # 通过环境变量传递配置（因为 uvicorn reload 会重新加载模块）
        os.environ['_APP_PORT'] = str(port)
        os.environ['_APP_LOCAL_IP'] = get_local_ip()
        
        uvicorn.run(
            "app.framework:api_framework.app",
            host=host,
            port=port,
            workers=workers,
            reload=reload,
            timeout_keep_alive=config.get("app.timeout_keep_alive", 300),
            timeout_graceful_shutdown=config.get("app.timeout_graceful_shutdown", 30),
            limit_concurrency=config.get("app.limit_concurrency", 1000),
            limit_max_requests=config.get("app.limit_max_requests", 10000)
        )


# 创建API框架实例
api_framework = APIFramework()
app = api_framework.app