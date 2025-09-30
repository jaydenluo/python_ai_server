"""
RBAC权限控制示例
展示权限与角色的具体控制机制
"""

from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    auth_required, admin_required, rate_limit, cache
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


@api_controller(prefix="/rbac-demo")
class RBACDemoController(ResourceController):
    """RBAC权限控制演示控制器"""
    
    def __init__(self):
        super().__init__(None)
    
    # 1. 公开路由 - 无需任何权限
    @get("/public")
    async def public_route(self, request: Request) -> Response:
        """公开路由 - 任何人都可以访问"""
        return self._create_response(
            self.success_response(
                data={"message": "This is a public route"},
                message="公开路由访问成功"
            )
        )
    
    # 2. 需要登录 - 用户资料
    @get("/profile", middleware=["auth"])
    async def profile(self, request: Request) -> Response:
        """用户资料 - 需要登录"""
        user = request.user
        return self._create_response(
            self.success_response(
                data={
                    "user_id": user.get("id"),
                    "username": user.get("username"),
                    "email": user.get("email"),
                    "roles": user.get("roles", []),
                    "permissions": user.get("permissions", [])
                },
                message="获取用户资料成功"
            )
        )
    
    # 3. 需要管理员权限 - 用户管理
    @get("/users", middleware=["auth", "admin"])
    async def users(self, request: Request) -> Response:
        """用户列表 - 需要登录 + 管理员权限"""
        return self._create_response(
            self.success_response(
                data={"users": []},
                message="获取用户列表成功"
            )
        )
    
    # 4. 需要特定权限 - 查看报告
    @get("/reports", middleware=["auth", "view_reports"])
    async def reports(self, request: Request) -> Response:
        """报告列表 - 需要登录 + 查看报告权限"""
        return self._create_response(
            self.success_response(
                data={"reports": []},
                message="获取报告列表成功"
            )
        )
    
    # 5. 需要多个权限 - 敏感数据
    @get("/sensitive", middleware=["auth", "admin", "sensitive_access"])
    async def sensitive_data(self, request: Request) -> Response:
        """敏感数据 - 需要登录 + 管理员权限 + 敏感数据权限"""
        return self._create_response(
            self.success_response(
                data={"sensitive_data": "confidential"},
                message="获取敏感数据成功"
            )
        )
    
    # 6. 需要角色权限 - 财务管理
    @get("/finance", middleware=["auth", "finance_manager"])
    async def finance(self, request: Request) -> Response:
        """财务数据 - 需要登录 + 财务经理角色"""
        return self._create_response(
            self.success_response(
                data={"finance": "data"},
                message="获取财务数据成功"
            )
        )
    
    # 7. 需要多个角色 - 高级管理
    @get("/executive", middleware=["auth", "executive", "board_member"])
    async def executive_data(self, request: Request) -> Response:
        """高管数据 - 需要登录 + 高管角色 + 董事会成员角色"""
        return self._create_response(
            self.success_response(
                data={"executive": "data"},
                message="获取高管数据成功"
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


def demo_rbac_system():
    """演示RBAC权限控制系统"""
    print("🔐 RBAC权限控制系统演示")
    print("=" * 60)
    
    print("\n📋 权限控制机制:")
    print("-" * 60)
    print("1. 认证中间件 (auth) - 验证用户是否已登录")
    print("2. 权限中间件 (permission) - 验证用户是否有特定权限")
    print("3. 角色中间件 (role) - 验证用户是否有特定角色")
    print("4. 组合中间件 - 同时验证多个权限或角色")
    
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
    print()
    print("# 要求登录 + 角色权限")
    print("@get('/finance', middleware=['auth', 'finance_manager'])")
    print("async def finance(self, request): pass")
    
    print("\n🎯 权限验证流程:")
    print("-" * 60)
    print("请求 → 认证中间件 → 权限中间件 → 角色中间件 → 业务逻辑")
    print()
    print("示例：GET /api/v1/admin/dashboard")
    print("1. AuthMiddleware - 验证用户身份")
    print("2. AdminMiddleware - 验证管理员权限")
    print("3. 执行业务逻辑")
    
    print("\n🚨 错误处理:")
    print("-" * 60)
    print("401 Unauthorized - 未认证或令牌无效")
    print("403 Forbidden - 权限不足或角色不符")
    print("429 Too Many Requests - 限流触发")
    
    print("\n💡 权限设计原则:")
    print("-" * 60)
    print("✅ 最小权限原则 - 只授予必要的权限")
    print("✅ 权限分离 - 区分认证和授权")
    print("✅ 角色继承 - 支持角色层级关系")
    print("✅ 权限缓存 - 提高性能")
    
    print("\n🔧 权限配置示例:")
    print("-" * 60)
    print("# 系统角色")
    print("ROLES = {")
    print("    'admin': {'name': '管理员', 'permissions': ['*']},")
    print("    'manager': {'name': '经理', 'permissions': ['view_users', 'create_users']},")
    print("    'user': {'name': '普通用户', 'permissions': ['view_profile']}")
    print("}")
    print()
    print("# 系统权限")
    print("PERMISSIONS = {")
    print("    'view_users': '查看用户列表',")
    print("    'create_users': '创建用户',")
    print("    'delete_users': '删除用户',")
    print("    'view_reports': '查看报告',")
    print("    'approve_reports': '审批报告'")
    print("}")
    
    print("\n📊 权限检查逻辑:")
    print("-" * 60)
    print("def check_permission(user, permission):")
    print("    # 1. 检查直接权限")
    print("    if user.has_direct_permission(permission):")
    print("        return True")
    print("    ")
    print("    # 2. 检查角色权限")
    print("    for role in user.roles:")
    print("        if role.has_permission(permission):")
    print("            return True")
    print("    ")
    print("    # 3. 权限不足")
    print("    return False")
    
    print("\n🎯 最佳实践:")
    print("-" * 60)
    print("1. 权限命名 - 使用清晰的权限命名")
    print("2. 角色设计 - 合理设计角色层级")
    print("3. 权限分配 - 遵循最小权限原则")
    print("4. 定期审计 - 定期检查权限分配")
    print("5. 日志记录 - 记录权限相关操作")
    print("6. 测试覆盖 - 为权限系统编写测试")


if __name__ == "__main__":
    demo_rbac_system()