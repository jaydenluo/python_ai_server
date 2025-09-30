"""
注解路由测试
测试不命名路由的自动命名功能
"""

import pytest
from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    get_routes, get_route_by_name
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


@api_controller(prefix="/test", version="v1")
class TestController(ResourceController):
    """测试控制器"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不命名路由测试
    @get("/")
    async def index(self, request: Request) -> Response:
        """测试索引"""
        pass
    
    @get("/{id}")
    async def show(self, request: Request) -> Response:
        """测试显示"""
        pass
    
    @post("/")
    async def store(self, request: Request) -> Response:
        """测试存储"""
        pass
    
    @put("/{id}")
    async def update(self, request: Request) -> Response:
        """测试更新"""
        pass
    
    @delete("/{id}")
    async def destroy(self, request: Request) -> Response:
        """测试删除"""
        pass


@api_controller(prefix="/blog", version="v1")
class BlogController(ResourceController):
    """博客控制器 - 混合命名测试"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不命名路由
    @get("/")
    async def index(self, request: Request) -> Response:
        """博客列表"""
        pass
    
    # 命名路由
    @get("/{id}", name="blog.detail")
    async def show(self, request: Request) -> Response:
        """博客详情"""
        pass
    
    # 不命名路由
    @post("/")
    async def store(self, request: Request) -> Response:
        """创建博客"""
        pass


def test_auto_naming():
    """测试自动命名功能"""
    # 注册控制器
    from app.api.route_registry import register_controller
    register_controller(TestController)
    register_controller(BlogController)
    
    # 获取所有路由
    routes = get_routes()
    
    # 测试TestController的自动命名
    test_routes = [route for route in routes if route.name.startswith("test.")]
    assert len(test_routes) == 5
    
    # 检查自动生成的路由名称
    expected_names = [
        "test.index",
        "test.show", 
        "test.store",
        "test.update",
        "test.destroy"
    ]
    
    actual_names = [route.name for route in test_routes]
    for expected_name in expected_names:
        assert expected_name in actual_names, f"Expected {expected_name} in {actual_names}"
    
    # 测试BlogController的混合命名
    blog_routes = [route for route in routes if route.name.startswith("blog.")]
    assert len(blog_routes) == 3
    
    # 检查混合命名
    blog_names = [route.name for route in blog_routes]
    assert "blog.index" in blog_names
    assert "blog.detail" in blog_names  # 自定义命名
    assert "blog.store" in blog_names


def test_route_lookup():
    """测试路由查找功能"""
    # 测试自动生成的路由名称
    route = get_route_by_name("test.index")
    assert route is not None
    assert route.method.value == "GET"
    assert route.path == "/"
    
    # 测试自定义路由名称
    route = get_route_by_name("blog.detail")
    assert route is not None
    assert route.method.value == "GET"
    assert route.path == "/{id}"
    
    # 测试不存在的路由
    route = get_route_by_name("nonexistent.route")
    assert route is None


def test_route_generation():
    """测试URL生成功能"""
    from app.api.decorators.route_decorators import generate_url
    
    # 测试简单路由
    url = generate_url("test.index")
    assert url == "/api/v1/test/"
    
    # 测试带参数的路由
    url = generate_url("test.show", id=123)
    assert url == "/api/v1/test/123"
    
    # 测试自定义命名路由
    url = generate_url("blog.detail", id=456)
    assert url == "/api/v1/blog/456"


def test_route_info():
    """测试路由信息"""
    routes = get_routes()
    
    # 检查路由信息完整性
    for route in routes:
        assert route.name is not None
        assert route.method is not None
        assert route.path is not None
        assert route.handler is not None
        assert route.version == "v1"
        assert route.prefix in ["/test", "/blog"]


def test_controller_registration():
    """测试控制器注册"""
    from app.api.route_registry import get_auto_registry
    
    registry = get_auto_registry()
    routes = registry.get_all_routes()
    
    # 检查路由数量
    assert len(routes) >= 8  # TestController(5) + BlogController(3)
    
    # 检查路由方法分布
    methods = {}
    for route in routes:
        method = route['method']
        methods[method] = methods.get(method, 0) + 1
    
    # 应该有GET、POST、PUT、DELETE方法
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


if __name__ == "__main__":
    # 运行测试
    test_auto_naming()
    test_route_lookup()
    test_route_generation()
    test_route_info()
    test_controller_registration()
    
    print("✅ 所有测试通过！")
    print("\n=== 路由命名测试结果 ===")
    
    # 显示所有路由
    routes = get_routes()
    for route in routes:
        print(f"{route.method.value:6} {route.path:20} -> {route.name}")
    
    print(f"\n总共注册了 {len(routes)} 个路由")