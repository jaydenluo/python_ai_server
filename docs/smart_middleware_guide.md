# 智能中间件使用指南

## 📖 概述

智能中间件系统是Python AI开发框架的核心特性，它通过智能的默认行为，让开发者可以更简洁地编写安全的API路由。系统会自动处理认证和权限控制，减少重复代码，提高开发效率。

## 🧠 核心特性

### 1. 智能默认行为
- **默认需要认证**: 不写中间件时自动需要认证
- **匿名访问**: 明确指定 `anonymous` 时不需要认证
- **自动添加认证**: 指定权限时自动添加认证中间件
- **向后兼容**: 原有的中间件写法仍然有效

### 2. 安全优先
- **默认安全**: 所有路由默认需要认证，避免忘记认证
- **明确匿名**: 只有明确指定才允许匿名访问
- **权限自动**: 指定权限时自动确保用户已认证

## 🎯 使用方式

### 1. 默认认证（推荐）

```python
@api_controller(prefix="/users")
class UserController(ResourceController):
    # 默认需要认证 - 不写中间件
    @get("/profile")
    async def profile(self, request: Request) -> Response:
        user = request.user  # 自动有用户信息
        return self.success_response(data={"user": user})
    
    # 默认需要认证 - 不写中间件
    @get("/settings")
    async def settings(self, request: Request) -> Response:
        return self.success_response(data={"settings": "data"})
```

### 2. 匿名访问

```python
@api_controller(prefix="/public")
class PublicController(ResourceController):
    # 匿名访问 - 明确指定
    @get("/info", middleware=["anonymous"])
    async def info(self, request: Request) -> Response:
        return self.success_response(data={"info": "public"})
    
    # 匿名访问 - 明确指定
    @get("/about", middleware=["anonymous"])
    async def about(self, request: Request) -> Response:
        return self.success_response(data={"about": "company"})
```

### 3. 权限控制

```python
@api_controller(prefix="/admin")
class AdminController(ResourceController):
    # 管理员权限 - 自动添加认证
    @get("/dashboard", middleware=["admin"])
    async def dashboard(self, request: Request) -> Response:
        return self.success_response(data={"dashboard": "data"})
    
    # 多个权限 - 自动添加认证
    @get("/sensitive", middleware=["admin", "sensitive_access"])
    async def sensitive(self, request: Request) -> Response:
        return self.success_response(data={"sensitive": "data"})
    
    # 角色权限 - 自动添加认证
    @get("/finance", middleware=["finance_manager"])
    async def finance(self, request: Request) -> Response:
        return self.success_response(data={"finance": "data"})
```

### 4. 混合使用

```python
@api_controller(prefix="/mixed")
class MixedController(ResourceController):
    # 默认认证
    @get("/profile")
    async def profile(self, request: Request) -> Response:
        pass
    
    # 匿名访问
    @get("/public", middleware=["anonymous"])
    async def public(self, request: Request) -> Response:
        pass
    
    # 管理员权限
    @get("/admin", middleware=["admin"])
    async def admin(self, request: Request) -> Response:
        pass
    
    # 明确指定认证
    @get("/explicit", middleware=["auth"])
    async def explicit(self, request: Request) -> Response:
        pass
```

## 🔧 智能处理逻辑

### 1. 处理规则

```python
def process_middleware(middleware):
    if not middleware:
        return ["auth"]  # 默认需要认证
    elif "anonymous" in middleware:
        return [m for m in middleware if m != "anonymous"]  # 移除匿名标记
    elif any(permission not in ["auth", "anonymous"] for permission in middleware):
        if "auth" not in middleware:
            return ["auth"] + middleware  # 自动添加认证
    return middleware  # 保持不变
```

### 2. 映射表

| 写法 | 实际中间件 | 说明 |
|------|------------|------|
| 不写中间件 | `["auth"]` | 默认需要认证 |
| `["anonymous"]` | `[]` | 匿名访问 |
| `["admin"]` | `["auth", "admin"]` | 自动添加认证 |
| `["admin", "sensitive"]` | `["auth", "admin", "sensitive"]` | 自动添加认证 |
| `["auth", "admin"]` | `["auth", "admin"]` | 保持不变 |
| `["anonymous", "cache"]` | `["cache"]` | 匿名访问 + 缓存 |

## 📊 使用示例

### 1. 用户管理示例

```python
@api_controller(prefix="/users")
class UserController(ResourceController):
    # 默认认证 - 用户资料
    @get("/profile")
    async def profile(self, request: Request) -> Response:
        user = request.user
        return self.success_response(data={"user": user})
    
    # 默认认证 - 用户设置
    @get("/settings")
    async def settings(self, request: Request) -> Response:
        return self.success_response(data={"settings": "data"})
    
    # 管理员权限 - 用户列表
    @get("/", middleware=["admin"])
    async def index(self, request: Request) -> Response:
        return self.success_response(data={"users": []})
    
    # 多个权限 - 删除用户
    @delete("/{id}", middleware=["admin", "delete_users"])
    async def destroy(self, request: Request) -> Response:
        return self.success_response(message="User deleted")
```

### 2. 公开API示例

```python
@api_controller(prefix="/api")
class APIController(ResourceController):
    # 匿名访问 - API信息
    @get("/info", middleware=["anonymous"])
    async def info(self, request: Request) -> Response:
        return self.success_response(data={"version": "1.0.0"})
    
    # 匿名访问 - 健康检查
    @get("/health", middleware=["anonymous"])
    async def health(self, request: Request) -> Response:
        return self.success_response(data={"status": "healthy"})
    
    # 默认认证 - 用户数据
    @get("/user-data")
    async def user_data(self, request: Request) -> Response:
        return self.success_response(data={"data": "user_specific"})
```

### 3. 管理后台示例

```python
@api_controller(prefix="/admin")
class AdminController(ResourceController):
    # 管理员权限 - 仪表板
    @get("/dashboard", middleware=["admin"])
    async def dashboard(self, request: Request) -> Response:
        return self.success_response(data={"dashboard": "data"})
    
    # 管理员权限 - 用户管理
    @get("/users", middleware=["admin"])
    async def users(self, request: Request) -> Response:
        return self.success_response(data={"users": []})
    
    # 多个权限 - 敏感操作
    @post("/bulk-action", middleware=["admin", "bulk_operations"])
    async def bulk_action(self, request: Request) -> Response:
        return self.success_response(message="Bulk action completed")
```

## 🚨 错误处理

### 1. 认证错误

```python
# 401 Unauthorized - 未认证
{
    "error": "Authentication required",
    "status_code": 401
}

# 401 Unauthorized - 令牌无效
{
    "error": "Invalid token",
    "status_code": 401
}
```

### 2. 权限错误

```python
# 403 Forbidden - 权限不足
{
    "error": "Permission denied: admin required",
    "status_code": 403
}

# 403 Forbidden - 角色不足
{
    "error": "Role required: manager",
    "status_code": 403
}
```

## 💡 最佳实践

### 1. 路由设计

```python
# ✅ 推荐：默认认证
@get("/profile")
async def profile(self, request: Request) -> Response:
    pass

# ✅ 推荐：匿名访问
@get("/public", middleware=["anonymous"])
async def public(self, request: Request) -> Response:
    pass

# ✅ 推荐：权限控制
@get("/admin", middleware=["admin"])
async def admin(self, request: Request) -> Response:
    pass

# ❌ 避免：忘记认证
@get("/sensitive")  # 默认需要认证，这是安全的
async def sensitive(self, request: Request) -> Response:
    pass
```

### 2. 权限命名

```python
# ✅ 好的权限命名
@get("/users", middleware=["admin"])
@get("/reports", middleware=["view_reports"])
@get("/finance", middleware=["finance_manager"])

# ❌ 避免的权限命名
@get("/users", middleware=["user_admin"])  # 不够清晰
@get("/reports", middleware=["reports"])    # 不够具体
```

### 3. 中间件组合

```python
# ✅ 推荐：简洁的权限控制
@get("/admin", middleware=["admin"])
@get("/sensitive", middleware=["admin", "sensitive_access"])

# ✅ 推荐：匿名访问
@get("/public", middleware=["anonymous"])
@get("/cached", middleware=["anonymous", "cache"])

# ❌ 避免：过度使用中间件
@get("/simple", middleware=["auth", "admin", "user", "basic"])
async def simple(self, request: Request) -> Response:
    pass
```

## 🔧 配置管理

### 1. 中间件配置

```python
# config/middleware.py
MIDDLEWARE_CONFIG = {
    "default_auth": True,  # 默认需要认证
    "anonymous_keyword": "anonymous",  # 匿名访问关键字
    "auto_auth": True,  # 自动添加认证
    "cache_enabled": True,  # 启用缓存
    "cache_ttl": 300  # 缓存时间
}
```

### 2. 权限配置

```python
# config/permissions.py
PERMISSION_CONFIG = {
    "admin_permissions": ["admin", "super_admin"],
    "user_permissions": ["user", "member"],
    "guest_permissions": ["guest", "visitor"],
    "system_permissions": ["system", "root"]
}
```

## 📈 性能优化

### 1. 中间件缓存

```python
class SmartMiddleware:
    def __init__(self):
        self.middleware_cache = {}
    
    def get_middleware(self, route_path, middleware):
        cache_key = f"{route_path}:{str(middleware)}"
        if cache_key in self.middleware_cache:
            return self.middleware_cache[cache_key]
        
        processed_middleware = self.process_middleware(middleware)
        self.middleware_cache[cache_key] = processed_middleware
        return processed_middleware
```

### 2. 权限缓存

```python
class PermissionCache:
    def __init__(self):
        self.permission_cache = {}
        self.role_cache = {}
    
    def get_user_permissions(self, user_id):
        if user_id in self.permission_cache:
            return self.permission_cache[user_id]
        
        permissions = self.query_permissions(user_id)
        self.permission_cache[user_id] = permissions
        return permissions
```

## 🎯 总结

智能中间件系统通过以下方式提高开发效率：

1. **默认安全**: 所有路由默认需要认证，避免安全漏洞
2. **简洁语法**: 大部分路由不需要写中间件
3. **智能处理**: 自动添加必要的认证中间件
4. **灵活控制**: 支持匿名访问和复杂权限组合
5. **向后兼容**: 保持原有写法的兼容性

这种设计让开发者可以专注于业务逻辑，而不用担心安全问题！

---

**智能中间件系统** - 让API开发更安全、更简洁！