"""
版本参数对比示例
展示优化前后的差异
"""

from app.api.decorators.route_decorators import (
    api_controller, api_resource, get, post, put, delete,
    auth_required, admin_required, rate_limit, cache
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


# 优化前：需要写很多参数
@api_controller(prefix="/users", version="v1", middleware=["auth"])
class UserControllerOld(ResourceController):
    """用户控制器 - 优化前"""
    
    def __init__(self):
        super().__init__(None)
    
    @get("/", name="users.index", middleware=["auth"], version="v1")
    @auth_required
    async def index(self, request: Request) -> Response:
        """用户列表"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取用户列表成功"
            )
        )
    
    @get("/{id}", name="users.show", middleware=["auth"], version="v1")
    @auth_required
    async def show(self, request: Request) -> Response:
        """用户详情"""
        return self._create_response(
            self.success_response(
                data={},
                message="获取用户详情成功"
            )
        )
    
    @post("/", name="users.store", middleware=["auth"], version="v1")
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


# 优化后：最简洁的写法
@api_controller(prefix="/users", middleware=["auth"])
class UserControllerNew(ResourceController):
    """用户控制器 - 优化后"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不写版本参数，不写路由名称 - 自动生成: users.index (v1)
    @get("/")
    @auth_required
    async def index(self, request: Request) -> Response:
        """用户列表"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取用户列表成功"
            )
        )
    
    # 不写版本参数，不写路由名称 - 自动生成: users.show (v1)
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
    
    # 不写版本参数，不写路由名称 - 自动生成: users.store (v1)
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


# 最简洁的CRUD写法
@api_resource("products")
class ProductController(ResourceController):
    """产品控制器 - 最简洁的CRUD"""
    
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


# 需要自定义版本时
@api_controller(prefix="/admin", version="v2")
class AdminController(ResourceController):
    """管理员控制器 - 使用v2版本"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不写版本参数 - 使用控制器级版本v2
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
    
    # 需要特定版本时
    @get("/stats", version="v3")
    @admin_required
    async def stats(self, request: Request) -> Response:
        """统计信息"""
        return self._create_response(
            self.success_response(
                data={"total": 1000},
                message="获取统计信息成功"
            )
        )


def demo_version_comparison():
    """演示版本参数对比"""
    print("🔄 版本参数对比演示")
    print("=" * 60)
    
    print("\n📊 优化前后对比:")
    print("-" * 60)
    
    print("优化前（需要写很多参数）:")
    print("```python")
    print("@api_controller(prefix='/users', version='v1', middleware=['auth'])")
    print("@get('/', name='users.index', middleware=['auth'], version='v1')")
    print("async def index(self, request): pass")
    print("```")
    
    print("\n优化后（最简洁的写法）:")
    print("```python")
    print("@api_controller(prefix='/users', middleware=['auth'])")
    print("@get('/')")
    print("async def index(self, request): pass")
    print("```")
    
    print("\n🎯 优化效果:")
    print("-" * 60)
    print("✅ 减少代码量 - 无需重复写版本参数")
    print("✅ 自动生成 - 路由名称和版本自动处理")
    print("✅ 更简洁 - 专注于业务逻辑")
    print("✅ 更灵活 - 需要时可以自定义")
    
    print("\n📝 版本参数优先级:")
    print("-" * 60)
    print("1. 方法级版本 > 控制器级版本 > 默认版本(v1)")
    print("2. 不写版本参数时，自动使用v1")
    print("3. 控制器级版本会影响所有方法")
    print("4. 方法级版本会覆盖控制器级版本")
    
    print("\n🚀 推荐写法:")
    print("-" * 60)
    print("# 最简洁的写法")
    print("@api_controller(prefix='/users')")
    print("@get('/')")
    print("async def index(self, request): pass")
    print()
    print("# 或者使用api_resource")
    print("@api_resource('products')")
    print("class ProductController:")
    print("    async def index(self, request): pass")
    
    print("\n💡 最佳实践:")
    print("-" * 60)
    print("1. 大部分情况下不写版本参数")
    print("2. 需要特定版本时再指定")
    print("3. 使用api_resource进行CRUD操作")
    print("4. 混合使用控制器级和方法级版本")


if __name__ == "__main__":
    demo_version_comparison()