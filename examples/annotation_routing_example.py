"""
注解路由使用示例
展示如何使用注解方式定义API路由
"""

from app.api.decorators.route_decorators import (
    api_controller, api_resource, get, post, put, patch, delete,
    auth_required, admin_required, rate_limit, cache, validate, api_doc
)
from app.api.controllers.base import ResourceController, APIResponse
from app.core.middleware.base import Request, Response


# 示例1: 基础控制器
@api_controller(prefix="/products", version="v1", middleware=["auth"])
class ProductController(ResourceController):
    """产品控制器 - 使用注解路由"""
    
    def __init__(self):
        super().__init__(None)  # 这里应该传入Product模型
    
    @get("/", name="products.index")
    @auth_required
    @rate_limit(requests_per_minute=60)
    @cache(ttl=300)
    @api_doc(
        summary="获取产品列表",
        description="获取系统中的所有产品列表",
        tags=["产品管理"]
    )
    async def index(self, request: Request) -> Response:
        """获取产品列表"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取产品列表成功"
            )
        )
    
    @get("/{id}", name="products.show")
    @auth_required
    @cache(ttl=600)
    @api_doc(
        summary="获取单个产品",
        description="根据产品ID获取产品详细信息",
        tags=["产品管理"]
    )
    async def show(self, request: Request) -> Response:
        """获取单个产品"""
        return self._create_response(
            self.success_response(
                data={},
                message="获取产品信息成功"
            )
        )
    
    @post("/", name="products.store")
    @admin_required
    @validate({"name": "required", "price": "required|numeric"})
    @api_doc(
        summary="创建产品",
        description="创建新的产品",
        tags=["产品管理"]
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
    
    @put("/{id}", name="products.update")
    @patch("/{id}", name="products.patch")
    @auth_required
    @api_doc(
        summary="更新产品",
        description="更新产品信息",
        tags=["产品管理"]
    )
    async def update(self, request: Request) -> Response:
        """更新产品"""
        return self._create_response(
            self.success_response(
                data={},
                message="更新产品成功"
            )
        )
    
    @delete("/{id}", name="products.destroy")
    @admin_required
    @api_doc(
        summary="删除产品",
        description="删除产品",
        tags=["产品管理"]
    )
    async def destroy(self, request: Request) -> Response:
        """删除产品"""
        return self._create_response(
            self.success_response(
                message="删除产品成功",
                status_code=204
            )
        )


# 示例2: 使用api_resource装饰器
@api_resource("orders", prefix="/api/v1", version="v1", middleware=["auth"])
class OrderController(ResourceController):
    """订单控制器 - 使用api_resource装饰器"""
    
    def __init__(self):
        super().__init__(None)  # 这里应该传入Order模型
    
    # 这些方法会自动生成路由
    async def index(self, request: Request) -> Response:
        """获取订单列表"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取订单列表成功"
            )
        )
    
    async def show(self, request: Request) -> Response:
        """获取单个订单"""
        return self._create_response(
            self.success_response(
                data={},
                message="获取订单信息成功"
            )
        )
    
    async def store(self, request: Request) -> Response:
        """创建订单"""
        return self._create_response(
            self.success_response(
                data={},
                message="创建订单成功",
                status_code=201
            )
        )
    
    async def update(self, request: Request) -> Response:
        """更新订单"""
        return self._create_response(
            self.success_response(
                data={},
                message="更新订单成功"
            )
        )
    
    async def destroy(self, request: Request) -> Response:
        """删除订单"""
        return self._create_response(
            self.success_response(
                message="删除订单成功",
                status_code=204
            )
        )


# 示例3: 自定义路由
@api_controller(prefix="/custom", version="v1")
class CustomController(ResourceController):
    """自定义控制器"""
    
    def __init__(self):
        super().__init__(None)
    
    @get("/hello", name="custom.hello")
    @api_doc(
        summary="Hello World",
        description="简单的Hello World接口",
        tags=["自定义"]
    )
    async def hello(self, request: Request) -> Response:
        """Hello World"""
        return self._create_response(
            self.success_response(
                data={"message": "Hello, World!"},
                message="Hello World成功"
            )
        )
    
    @post("/upload", name="custom.upload")
    @auth_required
    @rate_limit(requests_per_minute=10)
    @api_doc(
        summary="文件上传",
        description="上传文件到服务器",
        tags=["自定义"]
    )
    async def upload(self, request: Request) -> Response:
        """文件上传"""
        return self._create_response(
            self.success_response(
                data={"file_id": "12345"},
                message="文件上传成功"
            )
        )
    
    @get("/search", name="custom.search")
    @cache(ttl=60)
    @api_doc(
        summary="搜索",
        description="搜索功能",
        tags=["自定义"]
    )
    async def search(self, request: Request) -> Response:
        """搜索"""
        query = request.query_params.get("q", "")
        return self._create_response(
            self.success_response(
                data={"query": query, "results": []},
                message="搜索成功"
            )
        )


# 示例4: 中间件组合使用
@api_controller(prefix="/admin", version="v1", middleware=["auth", "admin"])
class AdminController(ResourceController):
    """管理员控制器"""
    
    def __init__(self):
        super().__init__(None)
    
    @get("/dashboard", name="admin.dashboard")
    @admin_required
    @cache(ttl=300)
    @api_doc(
        summary="管理面板",
        description="管理员面板数据",
        tags=["管理员"]
    )
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
    
    @post("/bulk-action", name="admin.bulk_action")
    @admin_required
    @rate_limit(requests_per_minute=5)
    @api_doc(
        summary="批量操作",
        description="执行批量操作",
        tags=["管理员"]
    )
    async def bulk_action(self, request: Request) -> Response:
        """批量操作"""
        return self._create_response(
            self.success_response(
                data={"processed": 100},
                message="批量操作成功"
            )
        )


# 示例5: 验证和错误处理
@api_controller(prefix="/validation", version="v1")
class ValidationController(ResourceController):
    """验证控制器"""
    
    def __init__(self):
        super().__init__(None)
    
    @post("/user", name="validation.create_user")
    @validate({
        "username": "required|min:3|max:20",
        "email": "required|email",
        "password": "required|min:8",
        "age": "required|integer|min:18|max:100"
    })
    @api_doc(
        summary="创建用户（带验证）",
        description="创建用户并验证输入数据",
        tags=["验证"]
    )
    async def create_user(self, request: Request) -> Response:
        """创建用户（带验证）"""
        data = request.body if isinstance(request.body, dict) else {}
        
        # 这里会自动进行验证
        return self._create_response(
            self.success_response(
                data=data,
                message="用户创建成功",
                status_code=201
            )
        )
    
    @post("/login", name="validation.login")
    @rate_limit(requests_per_minute=5, requests_per_hour=50)
    @validate({
        "username": "required",
        "password": "required"
    })
    @api_doc(
        summary="用户登录（带验证和限流）",
        description="用户登录，包含验证和限流",
        tags=["验证"]
    )
    async def login(self, request: Request) -> Response:
        """用户登录（带验证和限流）"""
        data = request.body if isinstance(request.body, dict) else {}
        
        return self._create_response(
            self.success_response(
                data={"token": "fake_token"},
                message="登录成功"
            )
        )


# 示例6: 路由注册和URL生成
def example_route_registration():
    """路由注册示例"""
    from app.api.route_registry import register_controller, get_auto_registry
    
    # 注册控制器
    register_controller(ProductController)
    register_controller(OrderController)
    register_controller(CustomController)
    register_controller(AdminController)
    register_controller(ValidationController)
    
    # 获取注册器
    registry = get_auto_registry()
    
    # 打印所有路由
    registry.print_routes()
    
    # 生成URL
    from app.api.decorators.route_decorators import generate_url
    
    # 生成产品列表URL
    products_url = generate_url("products.index")
    print(f"产品列表URL: {products_url}")
    
    # 生成带参数的产品详情URL
    product_url = generate_url("products.show", id=123)
    print(f"产品详情URL: {product_url}")
    
    # 生成订单URL
    orders_url = generate_url("orders.index")
    print(f"订单列表URL: {orders_url}")


if __name__ == "__main__":
    # 运行示例
    example_route_registration()
    
    print("\n=== 注解路由示例 ===")
    print("1. 基础控制器: ProductController")
    print("2. 资源控制器: OrderController")
    print("3. 自定义控制器: CustomController")
    print("4. 管理员控制器: AdminController")
    print("5. 验证控制器: ValidationController")
    print("\n启动服务器查看效果:")
    print("python main.py v2")