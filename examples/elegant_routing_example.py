"""
优雅路由示例
展示如何简化版本参数的使用
"""

from app.api.decorators.route_decorators import (
    api_controller, api_resource, get, post, put, delete,
    auth_required, admin_required, rate_limit, cache
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


# 方式1: 完全不写版本参数（使用默认v1）
@api_controller(prefix="/users")
class UserController(ResourceController):
    """用户控制器 - 最简洁的写法"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不命名路由，不写版本 - 自动生成: users.index
    @get("/")
    @auth_required
    @cache(ttl=300)
    async def index(self, request: Request) -> Response:
        """用户列表"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取用户列表成功"
            )
        )
    
    # 不命名路由，不写版本 - 自动生成: users.show
    @get("/{id}")
    @auth_required
    async def show(self, request: Request) -> Response:
        """用户详情"""
        return self._create_response(
            self.success_response(
                data={},
                message="获取用户详情成功"
            )
        )
    
    # 不命名路由，不写版本 - 自动生成: users.store
    @post("/")
    @admin_required
    async def store(self, request: Request) -> Response:
        """创建用户"""
        return self._create_response(
            self.success_response(
                data={},
                message="创建用户成功",
                status_code=201
            )
        )


# 方式2: 使用api_resource装饰器（最简洁）
@api_resource("products")
class ProductController(ResourceController):
    """产品控制器 - 使用api_resource装饰器"""
    
    def __init__(self):
        super().__init__(None)
    
    # 这些方法会自动生成路由，无需手动装饰器
    async def index(self, request: Request) -> Response:
        """产品列表"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取产品列表成功"
            )
        )
    
    async def show(self, request: Request) -> Response:
        """产品详情"""
        return self._create_response(
            self.success_response(
                data={},
                message="获取产品详情成功"
            )
        )
    
    async def store(self, request: Request) -> Response:
        """创建产品"""
        return self._create_response(
            self.success_response(
                data={},
                message="创建产品成功",
                status_code=201
            )
        )


# 方式3: 需要自定义版本时
@api_controller(prefix="/admin", version="v2")
class AdminController(ResourceController):
    """管理员控制器 - 使用v2版本"""
    
    def __init__(self):
        super().__init__(None)
    
    @get("/dashboard")
    @admin_required
    @cache(ttl=600)
    async def dashboard(self, request: Request) -> Response:
        """管理面板"""
        return self._create_response(
            self.success_response(
                data={"users": 100, "orders": 500},
                message="获取管理面板成功"
            )
        )
    
    @post("/bulk-action")
    @admin_required
    @rate_limit(requests_per_minute=5)
    async def bulk_action(self, request: Request) -> Response:
        """批量操作"""
        return self._create_response(
            self.success_response(
                data={"processed": 100},
                message="批量操作成功"
            )
        )


# 方式4: 混合使用（部分需要版本，部分不需要）
@api_controller(prefix="/api")
class APIController(ResourceController):
    """API控制器 - 混合使用"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不写版本 - 使用默认v1
    @get("/status")
    async def status(self, request: Request) -> Response:
        """API状态"""
        return self._create_response(
            self.success_response(
                data={"status": "healthy"},
                message="API状态正常"
            )
        )
    
    # 需要特定版本时
    @get("/version", version="v2")
    async def version(self, request: Request) -> Response:
        """API版本信息"""
        return self._create_response(
            self.success_response(
                data={"version": "2.0.0"},
                message="获取版本信息成功"
            )
        )


# 方式5: 使用api_resource + 自定义版本
@api_resource("orders", prefix="/api", version="v2")
class OrderController(ResourceController):
    """订单控制器 - 使用v2版本"""
    
    def __init__(self):
        super().__init__(None)
    
    async def index(self, request: Request) -> Response:
        """订单列表"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取订单列表成功"
            )
        )
    
    async def show(self, request: Request) -> Response:
        """订单详情"""
        return self._create_response(
            self.success_response(
                data={},
                message="获取订单详情成功"
            )
        )


def demo_elegant_routing():
    """演示优雅路由"""
    print("🎨 优雅路由演示")
    print("=" * 50)
    
    # 注册控制器
    from app.api.route_registry import register_controller
    register_controller(UserController)
    register_controller(ProductController)
    register_controller(AdminController)
    register_controller(APIController)
    register_controller(OrderController)
    
    # 获取所有路由
    from app.api.decorators.route_decorators import get_routes
    routes = get_routes()
    
    print(f"\n📊 总共注册了 {len(routes)} 个路由")
    print("\n📋 路由列表:")
    print("-" * 50)
    
    for route in routes:
        print(f"{route.method.value:6} {route.path:20} -> {route.name} (v{route.version})")
    
    print("\n🎯 优雅写法总结:")
    print("-" * 50)
    print("✅ 不写版本参数 - 自动使用v1")
    print("✅ 不写路由名称 - 自动生成")
    print("✅ 使用api_resource - 最简洁的CRUD")
    print("✅ 需要时指定版本 - 灵活控制")
    print("✅ 混合使用 - 最佳实践")
    
    print("\n📝 推荐写法:")
    print("-" * 50)
    print("# 最简洁的写法")
    print("@api_controller(prefix='/users')")
    print("@get('/')")
    print("async def index(self, request): pass")
    print()
    print("# 或者使用api_resource")
    print("@api_resource('products')")
    print("class ProductController:")
    print("    async def index(self, request): pass")


if __name__ == "__main__":
    demo_elegant_routing()