"""
简单路由示例
展示不命名路由的用法
"""

from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    auth_required, admin_required, rate_limit, cache
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


@api_controller(prefix="/simple", version="v1")
class SimpleController(ResourceController):
    """简单控制器 - 不命名路由示例"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不命名路由 - 自动生成名称
    @get("/")
    async def index(self, request: Request) -> Response:
        """获取列表 - 自动生成名称: simple.index"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取列表成功"
            )
        )
    
    @get("/{id}")
    async def show(self, request: Request) -> Response:
        """获取单个 - 自动生成名称: simple.show"""
        return self._create_response(
            self.success_response(
                data={},
                message="获取详情成功"
            )
        )
    
    @post("/")
    async def store(self, request: Request) -> Response:
        """创建 - 自动生成名称: simple.store"""
        return self._create_response(
            self.success_response(
                data={},
                message="创建成功",
                status_code=201
            )
        )
    
    @put("/{id}")
    async def update(self, request: Request) -> Response:
        """更新 - 自动生成名称: simple.update"""
        return self._create_response(
            self.success_response(
                data={},
                message="更新成功"
            )
        )
    
    @delete("/{id}")
    async def destroy(self, request: Request) -> Response:
        """删除 - 自动生成名称: simple.destroy"""
        return self._create_response(
            self.success_response(
                message="删除成功",
                status_code=204
            )
        )


@api_controller(prefix="/blog", version="v1")
class BlogController(ResourceController):
    """博客控制器 - 混合命名示例"""
    
    def __init__(self):
        super().__init__(None)
    
    # 不命名路由
    @get("/")
    async def index(self, request: Request) -> Response:
        """博客列表 - 自动生成名称: blog.index"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取博客列表成功"
            )
        )
    
    # 命名路由
    @get("/{id}", name="blog.detail")
    async def show(self, request: Request) -> Response:
        """博客详情 - 使用自定义名称: blog.detail"""
        return self._create_response(
            self.success_response(
                data={},
                message="获取博客详情成功"
            )
        )
    
    # 不命名路由
    @post("/")
    async def store(self, request: Request) -> Response:
        """创建博客 - 自动生成名称: blog.store"""
        return self._create_response(
            self.success_response(
                data={},
                message="创建博客成功",
                status_code=201
            )
        )
    
    # 带中间件的不命名路由
    @put("/{id}")
    @auth_required
    async def update(self, request: Request) -> Response:
        """更新博客 - 自动生成名称: blog.update"""
        return self._create_response(
            self.success_response(
                data={},
                message="更新博客成功"
            )
        )
    
    # 带多个装饰器的不命名路由
    @delete("/{id}")
    @admin_required
    @rate_limit(requests_per_minute=10)
    async def destroy(self, request: Request) -> Response:
        """删除博客 - 自动生成名称: blog.destroy"""
        return self._create_response(
            self.success_response(
                message="删除博客成功",
                status_code=204
            )
        )


@api_controller(prefix="/api", version="v1")
class APIController(ResourceController):
    """API控制器 - 完全自定义路由"""
    
    def __init__(self):
        super().__init__(None)
    
    # 自定义路径，不命名
    @get("/hello")
    async def hello(self, request: Request) -> Response:
        """Hello接口 - 自动生成名称: api.hello"""
        return self._create_response(
            self.success_response(
                data={"message": "Hello, World!"},
                message="Hello成功"
            )
        )
    
    # 自定义路径，命名
    @get("/status", name="api.health")
    async def status(self, request: Request) -> Response:
        """状态检查 - 使用自定义名称: api.health"""
        return self._create_response(
            self.success_response(
                data={"status": "healthy"},
                message="状态检查成功"
            )
        )
    
    # 带参数的自定义路径
    @get("/user/{user_id}/posts")
    async def user_posts(self, request: Request) -> Response:
        """用户文章 - 自动生成名称: api.user_posts"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取用户文章成功"
            )
        )
    
    # 带查询参数的路由
    @get("/search")
    async def search(self, request: Request) -> Response:
        """搜索 - 自动生成名称: api.search"""
        query = request.query_params.get("q", "")
        return self._create_response(
            self.success_response(
                data={"query": query, "results": []},
                message="搜索成功"
            )
        )


# 路由注册示例
def register_simple_routes():
    """注册简单路由"""
    from app.api.route_registry import register_controller
    
    # 注册控制器
    register_controller(SimpleController)
    register_controller(BlogController)
    register_controller(APIController)
    
    # 获取注册器
    from app.api.route_registry import get_auto_registry
    registry = get_auto_registry()
    
    # 打印所有路由
    print("\n=== 简单路由示例 ===")
    registry.print_routes()
    
    # 展示自动生成的路由名称
    routes = registry.get_all_routes()
    print("\n=== 自动生成的路由名称 ===")
    for route in routes:
        print(f"{route['method']:6} {route['path']:30} -> {route['name']}")


if __name__ == "__main__":
    # 运行示例
    register_simple_routes()
    
    print("\n=== 路由命名说明 ===")
    print("1. 不命名路由: 自动生成 类名.方法名")
    print("2. 命名路由: 使用自定义名称")
    print("3. 混合使用: 可以部分命名，部分不命名")
    print("\n启动服务器查看效果:")
    print("python main.py v2")