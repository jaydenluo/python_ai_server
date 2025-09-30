"""
中间件系统示例
展示中间件的工作原理和使用方法
"""

from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    auth_required, admin_required, rate_limit, cache
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


@api_controller(prefix="/demo")
class MiddlewareDemoController(ResourceController):
    """中间件演示控制器"""
    
    def __init__(self):
        super().__init__(None)
    
    # 1. 公开路由 - 无需任何中间件
    @get("/public")
    async def public_route(self, request: Request) -> Response:
        """公开路由 - 任何人都可以访问"""
        return self._create_response(
            self.success_response(
                data={"message": "This is a public route"},
                message="公开路由访问成功"
            )
        )
    
    # 2. 需要认证 - 只要求登录
    @get("/profile", middleware=["auth"])
    async def profile(self, request: Request) -> Response:
        """用户资料 - 需要登录"""
        user = request.user
        return self._create_response(
            self.success_response(
                data={
                    "user_id": user.get("id"),
                    "username": user.get("username"),
                    "email": user.get("email")
                },
                message="获取用户资料成功"
            )
        )
    
    # 3. 需要管理员权限 - 登录 + 管理员权限
    @get("/admin", middleware=["auth", "admin"])
    async def admin_route(self, request: Request) -> Response:
        """管理员路由 - 需要登录 + 管理员权限"""
        user = request.user
        return self._create_response(
            self.success_response(
                data={
                    "message": "Admin access granted",
                    "user": user.get("username"),
                    "roles": user.get("roles", [])
                },
                message="管理员访问成功"
            )
        )
    
    # 4. 需要特定权限 - 登录 + 特定权限
    @get("/reports", middleware=["auth", "view_reports"])
    async def reports(self, request: Request) -> Response:
        """报告路由 - 需要登录 + 查看报告权限"""
        return self._create_response(
            self.success_response(
                data={"reports": []},
                message="获取报告成功"
            )
        )
    
    # 5. 需要多个权限 - 登录 + 多个权限
    @get("/sensitive", middleware=["auth", "admin", "sensitive_access"])
    async def sensitive(self, request: Request) -> Response:
        """敏感数据路由 - 需要登录 + 管理员权限 + 敏感数据权限"""
        return self._create_response(
            self.success_response(
                data={"sensitive_data": "confidential"},
                message="获取敏感数据成功"
            )
        )
    
    # 6. 带限流的路由 - 登录 + 限流
    @get("/limited", middleware=["auth"])
    @rate_limit(requests_per_minute=10)
    async def limited_route(self, request: Request) -> Response:
        """限流路由 - 需要登录 + 限流控制"""
        return self._create_response(
            self.success_response(
                data={"message": "Limited access"},
                message="限流路由访问成功"
            )
        )
    
    # 7. 带缓存的路由 - 登录 + 缓存
    @get("/cached", middleware=["auth"])
    @cache(ttl=300)
    async def cached_route(self, request: Request) -> Response:
        """缓存路由 - 需要登录 + 缓存"""
        return self._create_response(
            self.success_response(
                data={"cached_data": "expensive_operation_result"},
                message="缓存路由访问成功"
            )
        )


@api_controller(prefix="/admin", middleware=["auth", "admin"])
class AdminController(ResourceController):
    """管理员控制器 - 所有路由都需要管理员权限"""
    
    def __init__(self):
        super().__init__(None)
    
    # 所有路由自动应用 auth + admin 中间件
    @get("/dashboard")
    async def dashboard(self, request: Request) -> Response:
        """管理面板"""
        return self._create_response(
            self.success_response(
                data={
                    "users_count": 100,
                    "orders_count": 500,
                    "revenue": 10000
                },
                message="获取管理面板数据成功"
            )
        )
    
    @get("/users")
    async def users(self, request: Request) -> Response:
        """用户管理"""
        return self._create_response(
            self.success_response(
                data={"users": []},
                message="获取用户列表成功"
            )
        )
    
    @post("/bulk-action", middleware=["auth", "admin", "bulk_operations"])
    async def bulk_action(self, request: Request) -> Response:
        """批量操作 - 需要额外的批量操作权限"""
        return self._create_response(
            self.success_response(
                data={"processed": 100},
                message="批量操作成功"
            )
        )


@api_controller(prefix="/finance")
class FinanceController(ResourceController):
    """财务控制器 - 演示角色权限"""
    
    def __init__(self):
        super().__init__(None)
    
    # 需要财务权限
    @get("/reports", middleware=["auth", "finance_access"])
    async def reports(self, request: Request) -> Response:
        """财务报告"""
        return self._create_response(
            self.success_response(
                data={"reports": []},
                message="获取财务报告成功"
            )
        )
    
    # 需要财务经理权限
    @get("/budget", middleware=["auth", "finance_manager"])
    async def budget(self, request: Request) -> Response:
        """预算管理"""
        return self._create_response(
            self.success_response(
                data={"budget": "data"},
                message="获取预算信息成功"
            )
        )
    
    # 需要财务总监权限
    @post("/approve", middleware=["auth", "finance_director"])
    async def approve(self, request: Request) -> Response:
        """审批功能"""
        return self._create_response(
            self.success_response(
                message="审批成功"
            )
        )


def demo_middleware_system():
    """演示中间件系统"""
    print("🛡️ 中间件系统演示")
    print("=" * 60)
    
    print("\n📋 中间件类型说明:")
    print("-" * 60)
    print("1. auth - 认证中间件：验证用户是否已登录")
    print("2. admin - 管理员中间件：验证用户是否有管理员权限")
    print("3. 自定义权限 - 验证用户是否有特定权限")
    print("4. 角色中间件 - 验证用户是否有特定角色")
    
    print("\n🔗 中间件组合示例:")
    print("-" * 60)
    print("# 只要求登录")
    print("@get('/profile', middleware=['auth'])")
    print("async def profile(self, request): pass")
    print()
    print("# 要求登录 + 管理员权限")
    print("@get('/admin', middleware=['auth', 'admin'])")
    print("async def admin(self, request): pass")
    print()
    print("# 要求登录 + 特定权限")
    print("@get('/reports', middleware=['auth', 'view_reports'])")
    print("async def reports(self, request): pass")
    print()
    print("# 要求登录 + 多个权限")
    print("@get('/sensitive', middleware=['auth', 'admin', 'sensitive_access'])")
    print("async def sensitive(self, request): pass")
    
    print("\n🎯 中间件执行顺序:")
    print("-" * 60)
    print("请求 → 全局中间件 → 控制器中间件 → 方法中间件 → 业务逻辑")
    print()
    print("示例：GET /api/v1/admin/dashboard")
    print("1. LoggingMiddleware - 记录请求日志")
    print("2. RateLimitMiddleware - 检查限流")
    print("3. AuthMiddleware - 验证用户身份")
    print("4. AdminMiddleware - 验证管理员权限")
    print("5. 执行业务逻辑")
    
    print("\n🚨 错误处理:")
    print("-" * 60)
    print("401 Unauthorized - 未认证或令牌无效")
    print("403 Forbidden - 权限不足或角色不符")
    print("429 Too Many Requests - 限流触发")
    
    print("\n💡 最佳实践:")
    print("-" * 60)
    print("✅ 最小权限原则 - 只授予必要的权限")
    print("✅ 权限分离 - 区分认证和授权")
    print("✅ 合理组合 - 避免过度使用中间件")
    print("✅ 错误处理 - 提供清晰的错误信息")
    print("✅ 性能考虑 - 避免不必要的中间件")
    
    print("\n🔧 自定义中间件:")
    print("-" * 60)
    print("class CustomMiddleware(Middleware):")
    print("    async def handle(self, request, next_handler):")
    print("        # 自定义逻辑")
    print("        return await next_handler()")
    
    print("\n📊 中间件统计:")
    print("-" * 60)
    print("• 认证中间件：验证用户身份")
    print("• 权限中间件：验证用户权限")
    print("• 角色中间件：验证用户角色")
    print("• 限流中间件：控制请求频率")
    print("• 缓存中间件：提高响应速度")
    print("• 日志中间件：记录请求信息")


if __name__ == "__main__":
    demo_middleware_system()