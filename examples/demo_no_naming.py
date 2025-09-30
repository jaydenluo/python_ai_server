"""
不命名路由演示
展示自动命名功能
"""

from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    get_routes, get_route_by_name, generate_url
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


@api_controller(prefix="/demo", version="v1")
class DemoController(ResourceController):
    """演示控制器 - 不命名路由"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不命名路由 - 自动生成名称: demo.index
    @get("/")
    async def index(self, request: Request) -> Response:
        """演示首页"""
        return self._create_response(
            self.success_response(
                data={"message": "Hello from demo.index"},
                message="演示首页成功"
            )
        )
    
    # 不命名路由 - 自动生成名称: demo.show
    @get("/{id}")
    async def show(self, request: Request) -> Response:
        """演示详情"""
        return self._create_response(
            self.success_response(
                data={"id": "123", "message": "Hello from demo.show"},
                message="演示详情成功"
            )
        )
    
    # 不命名路由 - 自动生成名称: demo.store
    @post("/")
    async def store(self, request: Request) -> Response:
        """演示创建"""
        return self._create_response(
            self.success_response(
                data={"message": "Hello from demo.store"},
                message="演示创建成功",
                status_code=201
            )
        )
    
    # 不命名路由 - 自动生成名称: demo.update
    @put("/{id}")
    async def update(self, request: Request) -> Response:
        """演示更新"""
        return self._create_response(
            self.success_response(
                data={"message": "Hello from demo.update"},
                message="演示更新成功"
            )
        )
    
    # 不命名路由 - 自动生成名称: demo.destroy
    @delete("/{id}")
    async def destroy(self, request: Request) -> Response:
        """演示删除"""
        return self._create_response(
            self.success_response(
                message="演示删除成功",
                status_code=204
            )
        )


@api_controller(prefix="/mixed", version="v1")
class MixedController(ResourceController):
    """混合控制器 - 部分命名，部分不命名"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不命名路由 - 自动生成名称: mixed.index
    @get("/")
    async def index(self, request: Request) -> Response:
        """混合首页"""
        return self._create_response(
            self.success_response(
                data={"message": "Hello from mixed.index"},
                message="混合首页成功"
            )
        )
    
    # 命名路由 - 使用自定义名称: mixed.detail
    @get("/{id}", name="mixed.detail")
    async def show(self, request: Request) -> Response:
        """混合详情"""
        return self._create_response(
            self.success_response(
                data={"message": "Hello from mixed.detail"},
                message="混合详情成功"
            )
        )
    
    # 不命名路由 - 自动生成名称: mixed.store
    @post("/")
    async def store(self, request: Request) -> Response:
        """混合创建"""
        return self._create_response(
            self.success_response(
                data={"message": "Hello from mixed.store"},
                message="混合创建成功",
                status_code=201
            )
        )


def demo_no_naming():
    """演示不命名路由功能"""
    print("🚀 不命名路由演示")
    print("=" * 50)
    
    # 注册控制器
    from app.api.route_registry import register_controller
    register_controller(DemoController)
    register_controller(MixedController)
    
    # 获取所有路由
    routes = get_routes()
    
    print(f"\n📊 总共注册了 {len(routes)} 个路由")
    print("\n📋 路由列表:")
    print("-" * 50)
    
    for route in routes:
        print(f"{route.method.value:6} {route.path:15} -> {route.name}")
    
    print("\n🔍 路由查找测试:")
    print("-" * 50)
    
    # 测试自动生成的路由名称
    test_routes = [
        "demo.index",
        "demo.show", 
        "demo.store",
        "demo.update",
        "demo.destroy",
        "mixed.index",
        "mixed.detail",  # 自定义命名
        "mixed.store"
    ]
    
    for route_name in test_routes:
        route = get_route_by_name(route_name)
        if route:
            print(f"✅ {route_name:15} -> {route.method.value} {route.path}")
        else:
            print(f"❌ {route_name:15} -> 未找到")
    
    print("\n🔗 URL生成测试:")
    print("-" * 50)
    
    # 测试URL生成
    test_urls = [
        ("demo.index", {}),
        ("demo.show", {"id": 123}),
        ("demo.store", {}),
        ("mixed.detail", {"id": 456}),
    ]
    
    for route_name, params in test_urls:
        try:
            url = generate_url(route_name, **params)
            print(f"✅ {route_name:15} -> {url}")
        except Exception as e:
            print(f"❌ {route_name:15} -> 错误: {e}")
    
    print("\n📝 命名规则说明:")
    print("-" * 50)
    print("1. 不命名路由: 自动生成 {类名}.{方法名}")
    print("2. 命名路由: 使用自定义名称")
    print("3. 混合使用: 可以部分命名，部分不命名")
    print("4. 类名自动转小写")
    
    print("\n🎯 优势:")
    print("-" * 50)
    print("✅ 代码更简洁 - 无需手动命名")
    print("✅ 自动生成 - 遵循命名规范")
    print("✅ 减少错误 - 避免命名冲突")
    print("✅ 易于维护 - 统一命名规则")


if __name__ == "__main__":
    demo_no_naming()