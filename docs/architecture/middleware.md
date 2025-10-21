# 中间件系统文档

## 📖 概述

中间件系统是Python AI开发框架的核心安全组件，负责处理用户认证、权限控制、角色验证等安全相关的功能。通过中间件链的方式，可以灵活地组合不同的安全策略。

## 🧠 智能中间件系统

### 1. 默认行为

- **不写中间件**: 默认需要认证 (`auth`)
- **匿名访问**: 明确指定 `middleware=["anonymous"]`
- **权限控制**: 指定权限时自动添加认证
- **向后兼容**: 原有的中间件写法仍然有效

### 2. 智能处理逻辑

```python
# 智能中间件处理逻辑
if not middleware:
    middleware = ["auth"]  # 默认需要认证
elif "anonymous" in middleware:
    middleware = [m for m in middleware if m != "anonymous"]  # 移除匿名标记
elif any(permission not in ["auth", "anonymous"] for permission in middleware):
    if "auth" not in middleware:
        middleware = ["auth"] + middleware  # 自动添加认证
```

### 3. 中间件映射表

| 写法 | 实际中间件 | 说明 |
|------|------------|------|
| 不写中间件 | `["auth"]` | 默认需要认证 |
| `["anonymous"]` | `[]` | 匿名访问 |
| `["admin"]` | `["auth", "admin"]` | 自动添加认证 |
| `["admin", "sensitive"]` | `["auth", "admin", "sensitive"]` | 自动添加认证 |
| `["auth", "admin"]` | `["auth", "admin"]` | 保持不变 |

## 🔐 中间件类型

### 1. 认证中间件 (AuthMiddleware)

**功能**: 验证用户身份，确保用户已登录

**工作原理**:
1. 检查请求头中的 `Authorization` 字段
2. 验证JWT令牌的有效性
3. 检查令牌是否过期
4. 将用户信息添加到请求对象中

```python
# 使用认证中间件
@get("/", middleware=["auth"])
async def protected_route(self, request: Request) -> Response:
    # 这里可以安全地访问 request.user
    user_id = request.user.get("id")
    return self.success_response(data={"user_id": user_id})
```

### 2. 权限中间件 (PermissionMiddleware)

**功能**: 验证用户权限，确保用户有特定权限

**工作原理**:
1. 检查用户是否已认证
2. 获取用户的权限列表
3. 验证用户是否拥有所需权限
4. 拒绝没有权限的请求

```python
# 使用权限中间件
@get("/admin", middleware=["auth", "admin"])
async def admin_route(self, request: Request) -> Response:
    # 这里确保用户已登录且是管理员
    return self.success_response(data={"message": "Admin access granted"})
```

### 3. 角色中间件 (RoleMiddleware)

**功能**: 验证用户角色，确保用户有特定角色

**工作原理**:
1. 检查用户是否已认证
2. 获取用户的角色列表
3. 验证用户是否拥有所需角色
4. 拒绝没有角色的请求

```python
# 使用角色中间件
@get("/manager", middleware=["auth", "manager"])
async def manager_route(self, request: Request) -> Response:
    # 这里确保用户已登录且是经理
    return self.success_response(data={"message": "Manager access granted"})
```

## 🛡️ 中间件组合

### 1. 智能中间件（推荐）

```python
# 默认需要认证 - 不写中间件
@get("/profile")
async def profile(self, request: Request) -> Response:
    pass  # 自动应用: middleware=["auth"]

# 匿名访问 - 明确指定
@get("/public", middleware=["anonymous"])
async def public(self, request: Request) -> Response:
    pass  # 等价于: middleware=[]

# 管理员权限 - 自动添加认证
@get("/admin", middleware=["admin"])
async def admin(self, request: Request) -> Response:
    pass  # 自动应用: middleware=["auth", "admin"]

# 多个权限 - 自动添加认证
@get("/sensitive", middleware=["admin", "sensitive_access"])
async def sensitive(self, request: Request) -> Response:
    pass  # 自动应用: middleware=["auth", "admin", "sensitive_access"]
```

### 2. 传统中间件（兼容）

```python
# 明确指定认证
@get("/profile", middleware=["auth"])
async def profile(self, request: Request) -> Response:
    pass

# 明确指定认证 + 权限
@get("/admin", middleware=["auth", "admin"])
async def admin(self, request: Request) -> Response:
    pass

# 明确指定认证 + 多个权限
@get("/reports", middleware=["auth", "view_reports"])
async def reports(self, request: Request) -> Response:
    pass
```

### 2. 复杂组合

```python
# 要求登录 + 管理员权限 + 特定权限
@get("/sensitive", middleware=["auth", "admin", "sensitive_access"])
async def sensitive(self, request: Request) -> Response:
    pass

# 要求登录 + 经理角色 + 财务权限
@get("/finance", middleware=["auth", "manager", "finance_access"])
async def finance(self, request: Request) -> Response:
    pass
```

## 🔧 中间件配置

### 1. 全局中间件配置

```python
# 在API框架中配置全局中间件
class APIFramework:
    def __init__(self):
        self.app = FastAPI()
        self._register_middleware()
    
    def _register_middleware(self):
        # 注册全局中间件
        self.app.middleware("http")(self._dispatch_middleware)
    
    async def _dispatch_middleware(self, request: Request, call_next):
        # 中间件处理逻辑
        middleware_classes = [
            LoggingMiddleware,
            RateLimitMiddleware,
            # 其他全局中间件
        ]
        
        # 应用中间件
        for middleware_class in middleware_classes:
            middleware = middleware_class()
            request = await middleware.process_request(request)
        
        response = await call_next(request)
        return response
```

### 2. 路由级中间件配置

```python
# 在控制器中配置中间件
@api_controller(prefix="/users", middleware=["auth"])
class UserController(ResourceController):
    """用户控制器 - 所有路由都需要认证"""
    
    @get("/")
    async def index(self, request: Request) -> Response:
        # 自动应用 auth 中间件
        pass
    
    @get("/{id}")
    async def show(self, request: Request) -> Response:
        # 自动应用 auth 中间件
        pass
```

### 3. 方法级中间件配置

```python
# 在方法上配置中间件
@api_controller(prefix="/users")
class UserController(ResourceController):
    @get("/")
    async def index(self, request: Request) -> Response:
        # 不需要认证
        pass
    
    @get("/{id}", middleware=["auth"])
    async def show(self, request: Request) -> Response:
        # 需要认证
        pass
    
    @post("/", middleware=["auth", "admin"])
    async def store(self, request: Request) -> Response:
        # 需要认证 + 管理员权限
        pass
```

## 🎯 中间件执行顺序

### 1. 执行优先级

```
请求 → 全局中间件 → 控制器中间件 → 方法中间件 → 业务逻辑 → 响应
```

### 2. 中间件链示例

```python
# 请求: GET /api/v1/users/123
# 中间件链: [LoggingMiddleware, RateLimitMiddleware, AuthMiddleware, AdminMiddleware]

@api_controller(prefix="/users", middleware=["auth"])
class UserController(ResourceController):
    @get("/{id}", middleware=["admin"])
    async def show(self, request: Request) -> Response:
        # 执行顺序:
        # 1. LoggingMiddleware - 记录请求日志
        # 2. RateLimitMiddleware - 检查限流
        # 3. AuthMiddleware - 验证用户身份
        # 4. AdminMiddleware - 验证管理员权限
        # 5. 执行业务逻辑
        pass
```

## 🔍 中间件实现细节

### 1. 认证中间件实现

```python
class AuthMiddleware(Middleware):
    async def handle(self, request: Request, next_handler) -> Response:
        # 1. 获取Authorization头
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return Response(status_code=401, body={"error": "Invalid authorization header"})
        
        # 2. 提取令牌
        token = auth_header[7:]
        
        try:
            # 3. 验证JWT令牌
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 4. 检查令牌过期
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                return Response(status_code=401, body={"error": "Token expired"})
            
            # 5. 将用户信息添加到请求中
            request.user = {
                "id": payload.get("user_id"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", [])
            }
            
            # 6. 继续处理请求
            return await next_handler()
            
        except jwt.InvalidTokenError:
            return Response(status_code=401, body={"error": "Invalid token"})
```

### 2. 权限中间件实现

```python
class PermissionMiddleware(Middleware):
    def __init__(self, required_permissions: list = None):
        self.required_permissions = required_permissions or []
    
    async def handle(self, request: Request, next_handler) -> Response:
        # 1. 检查用户是否已认证
        if not request.user:
            return Response(status_code=401, body={"error": "Authentication required"})
        
        # 2. 获取用户权限
        user_permissions = request.user.get("permissions", [])
        
        # 3. 检查权限
        for permission in self.required_permissions:
            if permission not in user_permissions:
                return Response(status_code=403, body={"error": f"Permission denied: {permission} required"})
        
        # 4. 继续处理请求
        return await next_handler()
```

## 📊 中间件使用示例

### 1. 用户管理示例

```python
@api_controller(prefix="/users")
class UserController(ResourceController):
    # 公开路由 - 无需认证
    @get("/public")
    async def public_info(self, request: Request) -> Response:
        return self.success_response(data={"message": "Public information"})
    
    # 需要登录 - 用户信息
    @get("/profile", middleware=["auth"])
    async def profile(self, request: Request) -> Response:
        user = request.user
        return self.success_response(data={"user": user})
    
    # 需要管理员权限 - 用户列表
    @get("/", middleware=["auth", "admin"])
    async def index(self, request: Request) -> Response:
        return self.success_response(data={"users": []})
    
    # 需要特定权限 - 删除用户
    @delete("/{id}", middleware=["auth", "delete_users"])
    async def destroy(self, request: Request) -> Response:
        return self.success_response(message="User deleted")
```

### 2. 管理员功能示例

```python
@api_controller(prefix="/admin", middleware=["auth", "admin"])
class AdminController(ResourceController):
    """管理员控制器 - 所有路由都需要管理员权限"""
    
    @get("/dashboard")
    async def dashboard(self, request: Request) -> Response:
        # 自动应用 auth + admin 中间件
        return self.success_response(data={"dashboard": "data"})
    
    @get("/users")
    async def users(self, request: Request) -> Response:
        # 自动应用 auth + admin 中间件
        return self.success_response(data={"users": []})
    
    @post("/bulk-action", middleware=["auth", "admin", "bulk_operations"])
    async def bulk_action(self, request: Request) -> Response:
        # 需要认证 + 管理员权限 + 批量操作权限
        return self.success_response(message="Bulk action completed")
```

### 3. 角色权限示例

```python
@api_controller(prefix="/finance")
class FinanceController(ResourceController):
    # 需要财务权限
    @get("/reports", middleware=["auth", "finance_access"])
    async def reports(self, request: Request) -> Response:
        return self.success_response(data={"reports": []})
    
    # 需要财务经理权限
    @get("/budget", middleware=["auth", "finance_manager"])
    async def budget(self, request: Request) -> Response:
        return self.success_response(data={"budget": "data"})
    
    # 需要财务总监权限
    @post("/approve", middleware=["auth", "finance_director"])
    async def approve(self, request: Request) -> Response:
        return self.success_response(message="Approved")
```

## 🚨 错误处理

### 1. 认证失败

```python
# 401 Unauthorized - 未认证
{
    "error": "Invalid authorization header"
}

# 401 Unauthorized - 令牌过期
{
    "error": "Token expired"
}

# 401 Unauthorized - 无效令牌
{
    "error": "Invalid token"
}
```

### 2. 权限不足

```python
# 403 Forbidden - 权限不足
{
    "error": "Permission denied: admin required"
}

# 403 Forbidden - 角色不足
{
    "error": "Role required: manager"
}
```

## 🔧 自定义中间件

### 1. 创建自定义中间件

```python
class CustomMiddleware(Middleware):
    def __init__(self, custom_param: str = None):
        self.custom_param = custom_param
    
    async def handle(self, request: Request, next_handler) -> Response:
        # 自定义逻辑
        if self.custom_param:
            request.custom_data = self.custom_param
        
        # 继续处理请求
        return await next_handler()
```

### 2. 使用自定义中间件

```python
@get("/custom", middleware=["auth", "custom"])
async def custom_route(self, request: Request) -> Response:
    # 可以访问 request.custom_data
    return self.success_response(data={"custom": request.custom_data})
```

## 📈 性能优化

### 1. 中间件缓存

```python
class CachedAuthMiddleware(Middleware):
    def __init__(self):
        self.token_cache = {}
    
    async def handle(self, request: Request, next_handler) -> Response:
        # 使用缓存避免重复验证
        token = self.extract_token(request)
        if token in self.token_cache:
            request.user = self.token_cache[token]
        else:
            # 验证令牌并缓存结果
            user = self.verify_token(token)
            self.token_cache[token] = user
            request.user = user
        
        return await next_handler()
```

### 2. 中间件优化

```python
# 避免不必要的中间件
@get("/public")
async def public_route(self, request: Request) -> Response:
    # 公开路由不需要认证中间件
    pass

# 合理使用中间件
@get("/admin", middleware=["auth", "admin"])
async def admin_route(self, request: Request) -> Response:
    # 只使用必要的中间件
    pass
```

## 🎯 最佳实践

### 1. 中间件设计原则

- **单一职责**: 每个中间件只负责一个功能
- **可组合性**: 中间件可以灵活组合
- **性能考虑**: 避免不必要的中间件
- **错误处理**: 提供清晰的错误信息

### 2. 安全建议

- **最小权限原则**: 只授予必要的权限
- **权限分离**: 区分认证和授权
- **令牌管理**: 合理设置令牌过期时间
- **日志记录**: 记录安全相关事件

### 3. 开发建议

- **测试覆盖**: 为中间件编写测试
- **文档完善**: 详细说明中间件功能
- **版本兼容**: 保持中间件接口稳定
- **性能监控**: 监控中间件性能影响

---

**中间件系统** - 为您的API提供强大的安全保障！