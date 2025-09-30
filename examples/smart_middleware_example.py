"""
智能中间件示例
展示新的中间件默认行为
"""

from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    auth_required, admin_required, rate_limit, cache
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


@api_controller(prefix="/smart")
class SmartMiddlewareController(ResourceController):
    """智能中间件演示控制器"""
    
    def __init__(self):
        super().__init__(None)
    
    # 1. 不写中间件 - 默认需要认证
    @get("/profile")
    async def profile(self, request: Request) -> Response:
        """用户资料 - 默认需要认证"""
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
    
    # 2. 指定匿名访问 - 不需要认证
    @get("/public", middleware=["anonymous"])
    async def public_info(self, request: Request) -> Response:
        """公开信息 - 匿名访问"""
        return self._create_response(
            self.success_response(
                data={"message": "This is public information"},
                message="获取公开信息成功"
            )
        )
    
    # 3. 指定管理员权限 - 自动添加认证
    @get("/admin", middleware=["admin"])
    async def admin_route(self, request: Request) -> Response:
        """管理员路由 - 自动添加认证"""
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
    
    # 4. 指定多个权限 - 自动添加认证
    @get("/sensitive", middleware=["admin", "sensitive_access"])
    async def sensitive_data(self, request: Request) -> Response:
        """敏感数据 - 自动添加认证"""
        return self._create_response(
            self.success_response(
                data={"sensitive_data": "confidential"},
                message="获取敏感数据成功"
            )
        )
    
    # 5. 指定角色权限 - 自动添加认证
    @get("/finance", middleware=["finance_manager"])
    async def finance(self, request: Request) -> Response:
        """财务数据 - 自动添加认证"""
        return self._create_response(
            self.success_response(
                data={"finance": "data"},
                message="获取财务数据成功"
            )
        )
    
    # 6. 明确指定认证 - 保持原有行为
    @get("/explicit", middleware=["auth"])
    async def explicit_auth(self, request: Request) -> Response:
        """明确认证 - 保持原有行为"""
        user = request.user
        return self._create_response(
            self.success_response(
                data={"user": user.get("username")},
                message="明确认证访问成功"
            )
        )
    
    # 7. 匿名 + 其他中间件
    @get("/cached", middleware=["anonymous", "cache"])
    async def cached_public(self, request: Request) -> Response:
        """缓存公开数据 - 匿名访问 + 缓存"""
        return self._create_response(
            self.success_response(
                data={"cached_data": "expensive_operation_result"},
                message="获取缓存公开数据成功"
            )
        )
    
    # 8. 认证 + 其他中间件
    @get("/limited", middleware=["auth", "rate_limit"])
    async def limited_auth(self, request: Request) -> Response:
        """限流认证 - 认证 + 限流"""
        return self._create_response(
            self.success_response(
                data={"message": "Limited access"},
                message="限流认证访问成功"
            )
        )


@api_controller(prefix="/demo")
class DemoController(ResourceController):
    """演示控制器 - 展示各种中间件组合"""
    
    def __init__(self):
        super().__init__(None)
    
    # 默认认证
    @get("/")
    async def index(self, request: Request) -> Response:
        """首页 - 默认需要认证"""
        return self._create_response(
            self.success_response(
                data={"message": "Welcome to demo"},
                message="首页访问成功"
            )
        )
    
    # 匿名访问
    @get("/about", middleware=["anonymous"])
    async def about(self, request: Request) -> Response:
        """关于页面 - 匿名访问"""
        return self._create_response(
            self.success_response(
                data={"about": "This is a demo application"},
                message="关于页面访问成功"
            )
        )
    
    # 管理员权限
    @get("/admin", middleware=["admin"])
    async def admin(self, request: Request) -> Response:
        """管理页面 - 自动添加认证"""
        return self._create_response(
            self.success_response(
                data={"admin": "data"},
                message="管理页面访问成功"
            )
        )
    
    # 多个权限
    @post("/create", middleware=["admin", "create_users"])
    async def create(self, request: Request) -> Response:
        """创建用户 - 自动添加认证"""
        return self._create_response(
            self.success_response(
                data={"created": True},
                message="创建用户成功"
            )
        )


def demo_smart_middleware():
    """演示智能中间件系统"""
    print("🧠 智能中间件系统演示")
    print("=" * 60)
    
    print("\n📋 中间件默认行为:")
    print("-" * 60)
    print("1. 不写中间件 - 默认需要认证 (auth)")
    print("2. 指定匿名访问 - 不需要认证 (anonymous)")
    print("3. 指定权限 - 自动添加认证 (auth + 权限)")
    print("4. 明确指定 - 保持原有行为")
    
    print("\n🔗 使用示例:")
    print("-" * 60)
    print("# 默认需要认证")
    print("@get('/profile')")
    print("async def profile(self, request): pass")
    print("# 等价于: middleware=['auth']")
    print()
    print("# 匿名访问")
    print("@get('/public', middleware=['anonymous'])")
    print("async def public(self, request): pass")
    print("# 等价于: middleware=[]")
    print()
    print("# 管理员权限")
    print("@get('/admin', middleware=['admin'])")
    print("async def admin(self, request): pass")
    print("# 等价于: middleware=['auth', 'admin']")
    print()
    print("# 多个权限")
    print("@get('/sensitive', middleware=['admin', 'sensitive_access'])")
    print("async def sensitive(self, request): pass")
    print("# 等价于: middleware=['auth', 'admin', 'sensitive_access']")
    
    print("\n🎯 智能处理逻辑:")
    print("-" * 60)
    print("if not middleware:")
    print("    middleware = ['auth']  # 默认需要认证")
    print("elif 'anonymous' in middleware:")
    print("    middleware = [m for m in middleware if m != 'anonymous']  # 移除匿名标记")
    print("elif any(permission not in ['auth', 'anonymous'] for permission in middleware):")
    print("    if 'auth' not in middleware:")
    print("        middleware = ['auth'] + middleware  # 自动添加认证")
    
    print("\n💡 优势:")
    print("-" * 60)
    print("✅ 更简洁 - 大部分路由不需要写中间件")
    print("✅ 更安全 - 默认需要认证，避免忘记认证")
    print("✅ 更智能 - 自动添加必要的认证中间件")
    print("✅ 更灵活 - 支持匿名访问和复杂权限组合")
    
    print("\n🚨 注意事项:")
    print("-" * 60)
    print("⚠️  默认需要认证 - 确保所有路由都有适当的权限控制")
    print("⚠️  匿名访问 - 只有明确指定 anonymous 才不需要认证")
    print("⚠️  权限组合 - 指定权限时自动添加认证中间件")
    print("⚠️  向后兼容 - 原有的中间件写法仍然有效")
    
    print("\n📊 中间件映射表:")
    print("-" * 60)
    print("不写中间件          → ['auth']")
    print("['anonymous']       → []")
    print("['admin']           → ['auth', 'admin']")
    print("['admin', 'sensitive'] → ['auth', 'admin', 'sensitive']")
    print("['auth', 'admin']   → ['auth', 'admin'] (保持不变)")
    print("['anonymous', 'cache'] → ['cache']")
    
    print("\n🎯 最佳实践:")
    print("-" * 60)
    print("1. 大部分路由不写中间件 - 自动需要认证")
    print("2. 公开路由明确指定 anonymous - 确保匿名访问")
    print("3. 权限路由只写权限名 - 自动添加认证")
    print("4. 复杂组合明确指定 - 保持清晰")
    print("5. 测试覆盖 - 确保权限控制正确")


if __name__ == "__main__":
    demo_smart_middleware()