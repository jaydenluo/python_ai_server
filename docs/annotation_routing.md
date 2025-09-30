# 注解路由系统文档

## 📖 概述

注解路由系统是Python AI开发框架V2的核心特性，它允许开发者使用装饰器直接在控制器方法上定义路由，类似于Laravel的Route Model Binding和Spring Boot的注解方式。这种方式让代码更加简洁、直观，并且支持自动路由注册。

## 🚀 核心特性

### 1. 装饰器路由
- **@get, @post, @put, @patch, @delete**: HTTP方法装饰器
- **@api_controller**: 控制器装饰器
- **@api_resource**: 资源装饰器，自动生成CRUD路由
- **@auth_required, @admin_required**: 权限装饰器
- **@rate_limit**: 限流装饰器
- **@cache**: 缓存装饰器
- **@validate**: 验证装饰器
- **@api_doc**: API文档装饰器

### 2. 自动路由注册
- 自动扫描控制器中的路由装饰器
- 自动注册到FastAPI路由器
- 支持路由分组和版本控制
- 自动生成API文档

### 3. 中间件支持
- 全局中间件
- 路由级中间件
- 方法级中间件
- 中间件组合

## 🛠️ 使用方法

### 1. 基础控制器（最优雅的写法）

```python
from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    auth_required, admin_required, rate_limit, cache, api_doc
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response

# 最简洁的写法 - 不写版本参数，自动使用v1
@api_controller(prefix="/products", middleware=["auth"])
class ProductController(ResourceController):
    """产品控制器"""
    
    def __init__(self):
        super().__init__(Product)  # 传入模型类
    
    # 不命名路由，不写版本 - 自动生成: products.index
    @get("/")
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
        # 实现逻辑
        pass
    
    # 不命名路由，不写版本 - 自动生成: products.show
    @get("/{id}")
    @auth_required
    @cache(ttl=600)
    async def show(self, request: Request) -> Response:
        """获取单个产品"""
        # 实现逻辑
        pass
    
    # 不命名路由，不写版本 - 自动生成: products.store
    @post("/")
    @admin_required
    async def store(self, request: Request) -> Response:
        """创建产品"""
        # 实现逻辑
        pass
    
    # 不命名路由，不写版本 - 自动生成: products.update
    @put("/{id}")
    @auth_required
    async def update(self, request: Request) -> Response:
        """更新产品"""
        # 实现逻辑
        pass
    
    # 不命名路由，不写版本 - 自动生成: products.destroy
    @delete("/{id}")
    @admin_required
    async def destroy(self, request: Request) -> Response:
        """删除产品"""
        # 实现逻辑
        pass
```

### 2. 资源控制器

```python
from app.api.decorators.route_decorators import api_resource

@api_resource("orders", prefix="/api/v1", version="v1", middleware=["auth"])
class OrderController(ResourceController):
    """订单控制器 - 自动生成CRUD路由"""
    
    def __init__(self):
        super().__init__(Order)
    
    # 这些方法会自动生成路由:
    # GET /api/v1/orders -> index()
    # GET /api/v1/orders/{id} -> show()
    # POST /api/v1/orders -> store()
    # PUT /api/v1/orders/{id} -> update()
    # PATCH /api/v1/orders/{id} -> patch()
    # DELETE /api/v1/orders/{id} -> destroy()
    
    async def index(self, request: Request) -> Response:
        """获取订单列表"""
        pass
    
    async def show(self, request: Request) -> Response:
        """获取单个订单"""
        pass
    
    async def store(self, request: Request) -> Response:
        """创建订单"""
        pass
    
    async def update(self, request: Request) -> Response:
        """更新订单"""
        pass
    
    async def destroy(self, request: Request) -> Response:
        """删除订单"""
        pass
```

### 3. 自定义路由

```python
@api_controller(prefix="/custom", version="v1")
class CustomController(ResourceController):
    """自定义控制器"""
    
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
    async def upload(self, request: Request) -> Response:
        """文件上传"""
        pass
    
    @get("/search", name="custom.search")
    @cache(ttl=60)
    async def search(self, request: Request) -> Response:
        """搜索"""
        query = request.query_params.get("q", "")
        return self._create_response(
            self.success_response(
                data={"query": query, "results": []},
                message="搜索成功"
            )
        )
```

### 4. 中间件组合

```python
@api_controller(prefix="/admin", version="v1", middleware=["auth", "admin"])
class AdminController(ResourceController):
    """管理员控制器"""
    
    @get("/dashboard", name="admin.dashboard")
    @admin_required
    @cache(ttl=300)
    async def dashboard(self, request: Request) -> Response:
        """管理面板"""
        pass
    
    @post("/bulk-action", name="admin.bulk_action")
    @admin_required
    @rate_limit(requests_per_minute=5)
    async def bulk_action(self, request: Request) -> Response:
        """批量操作"""
        pass
```

### 5. 数据验证

```python
@api_controller(prefix="/validation", version="v1")
class ValidationController(ResourceController):
    """验证控制器"""
    
    @post("/user", name="validation.create_user")
    @validate({
        "username": "required|min:3|max:20",
        "email": "required|email",
        "password": "required|min:8",
        "age": "required|integer|min:18|max:100"
    })
    async def create_user(self, request: Request) -> Response:
        """创建用户（带验证）"""
        # 验证会自动进行
        pass
    
    @post("/login", name="validation.login")
    @rate_limit(requests_per_minute=5, requests_per_hour=50)
    @validate({
        "username": "required",
        "password": "required"
    })
    async def login(self, request: Request) -> Response:
        """用户登录（带验证和限流）"""
        pass
```

## 🎨 优雅写法指南

### 1. 最简洁的写法（推荐）

```python
# 不写版本参数，不写路由名称 - 最简洁
@api_controller(prefix="/users")
class UserController(ResourceController):
    @get("/")
    async def index(self, request: Request) -> Response:
        pass  # 自动生成: users.index (v1)
    
    @get("/{id}")
    async def show(self, request: Request) -> Response:
        pass  # 自动生成: users.show (v1)
    
    @post("/")
    async def store(self, request: Request) -> Response:
        pass  # 自动生成: users.store (v1)
```

### 2. 使用api_resource（最简洁的CRUD）

```python
# 最简洁的CRUD写法
@api_resource("products")
class ProductController(ResourceController):
    # 这些方法会自动生成路由，无需手动装饰器
    async def index(self, request: Request) -> Response:
        pass  # 自动生成: products.index (v1)
    
    async def show(self, request: Request) -> Response:
        pass  # 自动生成: products.show (v1)
    
    async def store(self, request: Request) -> Response:
        pass  # 自动生成: products.store (v1)
```

### 3. 需要自定义版本时

```python
# 需要特定版本时
@api_controller(prefix="/admin", version="v2")
class AdminController(ResourceController):
    @get("/dashboard")
    async def dashboard(self, request: Request) -> Response:
        pass  # 自动生成: admin.dashboard (v2)
```

### 4. 混合使用（最佳实践）

```python
@api_controller(prefix="/api")
class APIController(ResourceController):
    # 不写版本 - 使用默认v1
    @get("/status")
    async def status(self, request: Request) -> Response:
        pass  # 自动生成: api.status (v1)
    
    # 需要特定版本时
    @get("/version", version="v2")
    async def version(self, request: Request) -> Response:
        pass  # 自动生成: api.version (v2)
```

### 5. 版本参数优先级

1. **方法级版本** > **控制器级版本** > **默认版本(v1)**
2. 不写版本参数时，自动使用v1
3. 控制器级版本会影响所有方法
4. 方法级版本会覆盖控制器级版本

## 🏷️ 路由命名规则

### 1. 不命名路由（推荐）

```python
@api_controller(prefix="/users", version="v1")
class UserController(ResourceController):
    """用户控制器"""
    
    # 不命名路由 - 自动生成名称: users.index
    @get("/")
    async def index(self, request: Request) -> Response:
        pass
    
    # 不命名路由 - 自动生成名称: users.show
    @get("/{id}")
    async def show(self, request: Request) -> Response:
        pass
    
    # 不命名路由 - 自动生成名称: users.store
    @post("/")
    async def store(self, request: Request) -> Response:
        pass
```

### 2. 命名路由

```python
@api_controller(prefix="/users", version="v1")
class UserController(ResourceController):
    """用户控制器"""
    
    # 命名路由
    @get("/", name="users.list")
    async def index(self, request: Request) -> Response:
        pass
    
    # 命名路由
    @get("/{id}", name="users.detail")
    async def show(self, request: Request) -> Response:
        pass
```

### 3. 混合命名

```python
@api_controller(prefix="/users", version="v1")
class UserController(ResourceController):
    """用户控制器"""
    
    # 不命名路由 - 自动生成: users.index
    @get("/")
    async def index(self, request: Request) -> Response:
        pass
    
    # 命名路由
    @get("/{id}", name="users.detail")
    async def show(self, request: Request) -> Response:
        pass
    
    # 不命名路由 - 自动生成: users.store
    @post("/")
    async def store(self, request: Request) -> Response:
        pass
```

### 4. 自动命名规则

- **格式**: `{类名}.{方法名}`
- **类名**: 控制器类名转小写
- **方法名**: 方法名保持不变

```python
# 示例
@api_controller(prefix="/products", version="v1")
class ProductController(ResourceController):
    # 自动生成名称: products.index
    @get("/")
    async def index(self, request: Request) -> Response:
        pass
    
    # 自动生成名称: products.show
    @get("/{id}")
    async def show(self, request: Request) -> Response:
        pass
    
    # 自动生成名称: products.create
    @post("/")
    async def create(self, request: Request) -> Response:
        pass
```

## 🔧 装饰器详解

### 1. 路由装饰器

#### HTTP方法装饰器
```python
@get("/path", name="route.name", middleware=["auth"])
@post("/path", name="route.name", middleware=["auth"])
@put("/path", name="route.name", middleware=["auth"])
@patch("/path", name="route.name", middleware=["auth"])
@delete("/path", name="route.name", middleware=["auth"])
```

#### 控制器装饰器
```python
@api_controller(prefix="/api", version="v1", middleware=["auth"])
class MyController:
    pass
```

#### 资源装饰器
```python
@api_resource("users", prefix="/api/v1", version="v1", middleware=["auth"])
class UserController:
    pass
```

### 2. 权限装饰器

```python
@auth_required  # 需要认证
@admin_required  # 需要管理员权限
```

### 3. 限流装饰器

```python
@rate_limit(requests_per_minute=60, requests_per_hour=1000)
```

### 4. 缓存装饰器

```python
@cache(ttl=300, key="custom_key")
```

### 5. 验证装饰器

```python
@validate({
    "field1": "required|min:3",
    "field2": "required|email",
    "field3": "optional|integer"
})
```

### 6. 文档装饰器

```python
@api_doc(
    summary="接口摘要",
    description="接口描述",
    tags=["标签"],
    responses={
        "200": {"description": "成功响应"},
        "400": {"description": "错误响应"}
    }
)
```

## 🚀 路由注册

### 1. 自动注册

```python
from app.api.route_registry import register_controller

# 注册单个控制器
register_controller(ProductController)

# 批量注册控制器
from app.api.route_registry import register_controllers
register_controllers([
    ProductController,
    OrderController,
    UserController
])
```

### 2. 自动发现

```python
from app.api.route_registry import auto_discover_controllers

# 自动发现控制器
auto_discover_controllers("app.api.controllers")
```

### 3. 获取路由信息

```python
from app.api.route_registry import get_auto_registry

registry = get_auto_registry()

# 获取所有路由
routes = registry.get_all_routes()

# 打印路由
registry.print_routes()
```

## 🔗 URL生成

### 1. 生成URL

```python
from app.api.decorators.route_decorators import generate_url

# 生成简单URL
url = generate_url("products.index")
# 结果: /api/v1/products

# 生成带参数URL
url = generate_url("products.show", id=123)
# 结果: /api/v1/products/123
```

### 2. 路由反向查找

```python
from app.api.decorators.route_decorators import get_route_by_name

route = get_route_by_name("products.show")
if route:
    print(f"路由方法: {route.method}")
    print(f"路由路径: {route.path}")
    print(f"中间件: {route.middleware}")
```

## 📊 路由信息

### 1. 获取所有路由

```python
from app.api.decorators.route_decorators import get_routes

routes = get_routes()
for route in routes:
    print(f"{route.method.value} {route.path} -> {route.handler.__name__}")
```

### 2. 路由统计

```python
from app.api.route_registry import get_auto_registry

registry = get_auto_registry()
routes = registry.get_all_routes()

# 按方法统计
methods = {}
for route in routes:
    method = route['method']
    methods[method] = methods.get(method, 0) + 1

print("路由统计:")
for method, count in methods.items():
    print(f"{method}: {count}")
```

## 🧪 测试

### 1. 单元测试

```python
import pytest
from fastapi.testclient import TestClient
from app.api.api_framework_v2 import app_v2

client = TestClient(app_v2)

def test_products_index():
    """测试产品列表接口"""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_products_create():
    """测试产品创建接口"""
    product_data = {
        "name": "测试产品",
        "price": 99.99
    }
    response = client.post("/api/v1/products", json=product_data)
    assert response.status_code == 201
    assert response.json()["success"] == True
```

### 2. 路由测试

```python
def test_route_registration():
    """测试路由注册"""
    from app.api.decorators.route_decorators import get_routes
    
    routes = get_routes()
    route_names = [route.name for route in routes]
    
    assert "products.index" in route_names
    assert "products.show" in route_names
    assert "products.store" in route_names
```

## 🚀 启动应用

### 1. 启动V2版本

```bash
# 启动注解路由版本
python main.py v2

# 或者直接启动
python -m app.api.api_framework_v2
```

### 2. 查看路由

```bash
# 访问API信息
curl http://localhost:8000/api/v1/info

# 访问API文档
open http://localhost:8000/docs
```

## 📚 最佳实践

### 1. 控制器设计

```python
# ✅ 好的做法
@api_controller(prefix="/users", version="v1", middleware=["auth"])
class UserController(ResourceController):
    """用户控制器"""
    
    @get("/", name="users.index")
    @auth_required
    @cache(ttl=300)
    async def index(self, request: Request) -> Response:
        """获取用户列表"""
        pass

# ❌ 避免的做法
class UserController:
    def get_users(self):
        pass  # 没有使用装饰器
```

### 2. 路由命名

```python
# ✅ 推荐：不命名路由（自动生成）
@get("/")
async def index(self, request: Request) -> Response:
    pass  # 自动生成名称: users.index

@get("/{id}")
async def show(self, request: Request) -> Response:
    pass  # 自动生成名称: users.show

# ✅ 好的命名（需要自定义时）
@get("/", name="users.index")
@get("/{id}", name="users.show")
@post("/", name="users.store")

# ❌ 避免的命名
@get("/", name="get_users")
@get("/{id}", name="get_user")
```

### 3. 中间件使用

```python
# ✅ 合理使用中间件
@get("/", name="users.index")
@auth_required
@rate_limit(requests_per_minute=60)
@cache(ttl=300)
async def index(self, request: Request) -> Response:
    pass

# ❌ 过度使用中间件
@get("/", name="users.index")
@auth_required
@admin_required
@rate_limit(requests_per_minute=1)
@cache(ttl=1)
async def index(self, request: Request) -> Response:
    pass
```

### 4. 错误处理

```python
@get("/{id}", name="users.show")
@auth_required
async def show(self, request: Request) -> Response:
    """获取用户信息"""
    try:
        # 业务逻辑
        pass
    except Exception as e:
        return self._create_response(
            self.server_error_response(f"获取用户信息失败: {str(e)}")
        )
```

## 🔧 故障排除

### 1. 路由未注册

```python
# 检查控制器是否正确注册
from app.api.route_registry import get_auto_registry

registry = get_auto_registry()
routes = registry.get_all_routes()
print([route['name'] for route in routes])
```

### 2. 中间件不生效

```python
# 检查中间件是否正确配置
@get("/", name="test", middleware=["auth"])
async def test(self, request: Request) -> Response:
    pass
```

### 3. 验证失败

```python
# 检查验证规则
@validate({
    "username": "required|min:3",  # 确保规则正确
    "email": "required|email"
})
async def create_user(self, request: Request) -> Response:
    pass
```

## 📈 性能优化

### 1. 缓存策略

```python
# 合理使用缓存
@get("/", name="users.index")
@cache(ttl=300)  # 5分钟缓存
async def index(self, request: Request) -> Response:
    pass

@get("/{id}", name="users.show")
@cache(ttl=600)  # 10分钟缓存
async def show(self, request: Request) -> Response:
    pass
```

### 2. 限流策略

```python
# 合理设置限流
@get("/", name="users.index")
@rate_limit(requests_per_minute=60)  # 每分钟60次
async def index(self, request: Request) -> Response:
    pass

@post("/", name="users.store")
@rate_limit(requests_per_minute=10)  # 每分钟10次
async def store(self, request: Request) -> Response:
    pass
```

---

**注解路由系统** - 让API开发更简单、更优雅！