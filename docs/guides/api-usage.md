# API使用指南

本指南介绍如何使用Python AI框架的API功能，包括注解路由、中间件、权限控制等。

## 📋 目录

- [注解路由](#注解路由)
- [中间件系统](#中间件系统)
- [权限控制](#权限控制)
- [API文档生成](#api文档生成)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)

## 🛣️ 注解路由

### 基本路由定义

```python
from app.api.decorators import get, post, put, delete, route

class UserController:
    @get("/users")
    def get_users(self):
        """获取用户列表"""
        return {"users": []}
    
    @post("/users")
    def create_user(self, user_data: dict):
        """创建用户"""
        return {"message": "用户创建成功"}
    
    @get("/users/{user_id}")
    def get_user(self, user_id: int):
        """获取单个用户"""
        return {"user": {"id": user_id}}
    
    @put("/users/{user_id}")
    def update_user(self, user_id: int, user_data: dict):
        """更新用户"""
        return {"message": "用户更新成功"}
    
    @delete("/users/{user_id}")
    def delete_user(self, user_id: int):
        """删除用户"""
        return {"message": "用户删除成功"}
```

### 路由参数

```python
class UserController:
    @get("/users", name="users.list", version="v1", middleware=["auth"])
    def get_users(self):
        """获取用户列表 - 需要认证"""
        pass
    
    @post("/users", p="/api/users", v="v2", m=["auth", "admin"])
    def create_user(self):
        """创建用户 - 需要管理员权限"""
        pass
    
    @get("/users/{user_id}", name="users.show")
    def get_user(self, user_id: int):
        """获取用户详情"""
        pass
```

### 控制器组织

```python
# app/api/controllers/admin/user_controller.py
from app.api.decorators import get, post, put, delete

@controller(prefix="/admin/users", middleware=["auth", "admin"])
class AdminUserController:
    @get("/")
    def list_users(self):
        """管理员用户列表"""
        pass
    
    @post("/")
    def create_user(self):
        """创建用户"""
        pass

# app/api/controllers/api/user_controller.py
@controller(prefix="/api/users", middleware=["auth"])
class UserController:
    @get("/")
    def list_users(self):
        """用户列表"""
        pass
    
    @get("/profile")
    def get_profile(self):
        """获取个人资料"""
        pass

# app/api/controllers/web/user_controller.py
@controller(prefix="/web/users", middleware=["anonymous"])
class WebUserController:
    @get("/")
    def list_users(self):
        """公开用户列表"""
        pass
```

## 🛡️ 中间件系统

### 内置中间件

```python
from app.core.middleware import auth, admin, rate_limit, logging

class UserController:
    @get("/users", middleware=["auth"])
    def get_users(self):
        """需要认证的用户列表"""
        pass
    
    @post("/users", middleware=["auth", "admin"])
    def create_user(self):
        """需要管理员权限"""
        pass
    
    @get("/public", middleware=["anonymous"])
    def public_data(self):
        """匿名访问"""
        pass
```

### 自定义中间件

```python
from app.core.middleware import Middleware

class CustomMiddleware(Middleware):
    def handle(self, request, next):
        # 前置处理
        print(f"请求开始: {request.method} {request.path}")
        
        # 调用下一个中间件
        response = next(request)
        
        # 后置处理
        print(f"请求完成: {response.status_code}")
        
        return response

# 使用自定义中间件
@get("/users", middleware=["custom"])
def get_users(self):
    pass
```

### 中间件参数

```python
class RateLimitMiddleware(Middleware):
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
    
    def handle(self, request, next):
        # 实现限流逻辑
        pass

# 使用带参数的中间件
@get("/users", middleware=["rate_limit:100"])
def get_users(self):
    pass
```

## 🔐 权限控制

### 基于角色的访问控制

```python
from app.services.auth import AuthService, PermissionService

class UserController:
    def __init__(self, auth_service: AuthService, permission_service: PermissionService):
        self.auth_service = auth_service
        self.permission_service = permission_service
    
    @get("/users", middleware=["auth"])
    def get_users(self, request):
        """获取用户列表 - 需要认证"""
        user = self.auth_service.get_current_user(request)
        return {"users": []}
    
    @post("/users", middleware=["auth", "admin"])
    def create_user(self, request):
        """创建用户 - 需要管理员权限"""
        user = self.auth_service.get_current_user(request)
        if not self.permission_service.has_permission(user, "create_user"):
            return {"error": "权限不足"}, 403
        return {"message": "用户创建成功"}
    
    @delete("/users/{user_id}", middleware=["auth", "admin"])
    def delete_user(self, user_id: int, request):
        """删除用户 - 需要管理员权限"""
        user = self.auth_service.get_current_user(request)
        if not self.permission_service.has_permission(user, "delete_user"):
            return {"error": "权限不足"}, 403
        return {"message": "用户删除成功"}
```

### 权限检查

```python
class UserController:
    @get("/users/{user_id}")
    def get_user(self, user_id: int, request):
        """获取用户详情"""
        user = self.auth_service.get_current_user(request)
        
        # 检查是否可以访问该用户
        if not self.permission_service.can_access_user(user, user_id):
            return {"error": "无权访问该用户"}, 403
        
        return {"user": {"id": user_id}}
    
    @put("/users/{user_id}")
    def update_user(self, user_id: int, user_data: dict, request):
        """更新用户"""
        user = self.auth_service.get_current_user(request)
        
        # 检查是否可以更新该用户
        if not self.permission_service.can_update_user(user, user_id):
            return {"error": "无权更新该用户"}, 403
        
        return {"message": "用户更新成功"}
```

## 📚 API文档生成

### 自动文档生成

```python
from app.api.docs import OpenAPIGenerator

# 生成OpenAPI文档
generator = OpenAPIGenerator()
api_doc = generator.generate()

# 保存文档
with open("api_doc.json", "w") as f:
    json.dump(api_doc, f, indent=2)
```

### 文档配置

```python
# app/api/docs/config.py
API_INFO = {
    "title": "Python AI Framework API",
    "version": "1.0.0",
    "description": "基于Python的AI框架API文档",
    "contact": {
        "name": "API支持",
        "email": "support@example.com"
    }
}

TAGS = [
    {
        "name": "用户管理",
        "description": "用户相关的API接口"
    },
    {
        "name": "AI模型",
        "description": "AI模型相关的API接口"
    }
]
```

### 接口文档

```python
class UserController:
    @get("/users", 
         summary="获取用户列表",
         description="获取系统中所有用户的列表",
         tags=["用户管理"],
         responses={
             200: {"description": "成功获取用户列表"},
             401: {"description": "未认证"},
             403: {"description": "权限不足"}
         })
    def get_users(self):
        """获取用户列表"""
        pass
    
    @post("/users",
          summary="创建用户",
          description="创建新的用户账户",
          tags=["用户管理"],
          request_body={
              "type": "object",
              "properties": {
                  "username": {"type": "string"},
                  "email": {"type": "string"},
                  "password": {"type": "string"}
              }
          })
    def create_user(self, user_data: dict):
        """创建用户"""
        pass
```

## ⚠️ 错误处理

### 全局错误处理

```python
from app.api.exceptions import APIException, ValidationError, NotFoundError

class UserController:
    @get("/users/{user_id}")
    def get_user(self, user_id: int):
        try:
            user = self.user_service.get_by_id(user_id)
            if not user:
                raise NotFoundError("用户不存在")
            return {"user": user}
        except ValidationError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": "服务器内部错误"}, 500
```

### 自定义异常

```python
from app.api.exceptions import APIException

class UserNotFoundError(APIException):
    def __init__(self, user_id: int):
        super().__init__(f"用户 {user_id} 不存在", 404)

class InsufficientPermissionError(APIException):
    def __init__(self, action: str):
        super().__init__(f"权限不足，无法执行 {action}", 403)

# 使用自定义异常
class UserController:
    @get("/users/{user_id}")
    def get_user(self, user_id: int):
        user = self.user_service.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return {"user": user}
```

### 错误响应格式

```python
# 标准错误响应格式
{
    "error": {
        "code": "USER_NOT_FOUND",
        "message": "用户不存在",
        "details": {
            "user_id": 123
        }
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "path": "/api/users/123"
}
```

## 🎯 最佳实践

### 1. 控制器设计

```python
# ✅ 好的做法
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    @get("/users")
    def get_users(self):
        return self.user_service.get_all()

# ❌ 避免的做法
class UserController:
    @get("/users")
    def get_users(self):
        # 直接在控制器中处理业务逻辑
        users = User.query.all()
        return [user.to_dict() for user in users]
```

### 2. 路由命名

```python
# ✅ 好的做法
@get("/users", name="users.list")
@get("/users/{id}", name="users.show")
@post("/users", name="users.create")

# ❌ 避免的做法
@get("/users")  # 没有命名
@get("/users/{id}")  # 没有命名
```

### 3. 中间件使用

```python
# ✅ 好的做法
@get("/users", middleware=["auth"])
@post("/users", middleware=["auth", "admin"])
@get("/public", middleware=["anonymous"])

# ❌ 避免的做法
@get("/users")  # 没有中间件保护
@post("/users")  # 没有权限控制
```

### 4. 错误处理

```python
# ✅ 好的做法
@get("/users/{user_id}")
def get_user(self, user_id: int):
    try:
        user = self.user_service.get_by_id(user_id)
        if not user:
            raise NotFoundError("用户不存在")
        return {"user": user}
    except ValidationError as e:
        return {"error": str(e)}, 400

# ❌ 避免的做法
@get("/users/{user_id}")
def get_user(self, user_id: int):
    user = self.user_service.get_by_id(user_id)
    return {"user": user}  # 没有错误处理
```

### 5. 响应格式

```python
# ✅ 好的做法
@get("/users")
def get_users(self):
    users = self.user_service.get_all()
    return {
        "data": users,
        "total": len(users),
        "page": 1,
        "per_page": 20
    }

# ❌ 避免的做法
@get("/users")
def get_users(self):
    return self.user_service.get_all()  # 没有统一的响应格式
```

## 📊 性能优化

### 1. 缓存使用

```python
class UserController:
    def __init__(self, user_service: UserService, cache: CacheManager):
        self.user_service = user_service
        self.cache = cache
    
    @get("/users")
    def get_users(self):
        # 使用缓存
        users = self.cache.remember("users:list", 
                                  lambda: self.user_service.get_all(), 
                                  ttl=300)
        return {"users": users}
```

### 2. 分页查询

```python
@get("/users")
def get_users(self, page: int = 1, per_page: int = 20):
    result = self.user_service.paginate(page, per_page)
    return {
        "data": result["items"],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"]
    }
```

### 3. 字段选择

```python
@get("/users")
def get_users(self, fields: str = None):
    if fields:
        field_list = fields.split(",")
        users = self.user_service.get_all(select_fields=field_list)
    else:
        users = self.user_service.get_all()
    return {"users": users}
```

## 🔧 调试和测试

### 1. 调试模式

```python
# 启用调试模式
config.set("app.debug", True)

# 调试信息
@get("/users")
def get_users(self, request):
    if config.get("app.debug"):
        print(f"请求路径: {request.path}")
        print(f"请求参数: {request.args}")
    return {"users": []}
```

### 2. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

@get("/users")
def get_users(self):
    logger.info("获取用户列表")
    users = self.user_service.get_all()
    logger.info(f"返回 {len(users)} 个用户")
    return {"users": users}
```

### 3. 单元测试

```python
import unittest
from app.api.controllers.user_controller import UserController

class TestUserController(unittest.TestCase):
    def setUp(self):
        self.controller = UserController()
    
    def test_get_users(self):
        response = self.controller.get_users()
        self.assertEqual(response["status_code"], 200)
        self.assertIn("users", response["data"])
```

## 📈 监控和指标

### 1. 性能监控

```python
import time

class UserController:
    @get("/users")
    def get_users(self):
        start_time = time.time()
        
        users = self.user_service.get_all()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 记录性能指标
        self.metrics.record("api.users.get_users.response_time", response_time)
        
        return {"users": users}
```

### 2. 请求统计

```python
class UserController:
    @get("/users")
    def get_users(self, request):
        # 记录请求统计
        self.stats.increment("api.users.get_users.requests")
        self.stats.increment("api.users.get_users.requests_by_ip", request.remote_addr)
        
        return {"users": []}
```

## 📚 总结

通过合理使用API功能，您可以构建出：

- **高性能**: 通过缓存和优化提升响应速度
- **安全可靠**: 通过中间件和权限控制保障安全
- **易于维护**: 通过注解路由和统一错误处理
- **文档完善**: 通过自动文档生成和标准化响应

这些功能为您的API提供了完整的解决方案！