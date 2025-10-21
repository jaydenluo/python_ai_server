# RBAC权限控制系统文档

## 📖 概述

RBAC（Role-Based Access Control）是基于角色的访问控制系统，是Python AI开发框架的核心安全组件。它通过用户、角色、权限的三层模型，实现细粒度的权限控制。

## 🏗️ 系统架构

### 1. 三层模型

```
用户 (User) ←→ 角色 (Role) ←→ 权限 (Permission)
```

- **用户**: 系统中的实际用户
- **角色**: 用户的分组，如管理员、普通用户、访客
- **权限**: 具体的操作权限，如创建、读取、更新、删除

### 2. 关系映射

```
用户-角色关系 (User-Role)
角色-权限关系 (Role-Permission)
用户-权限关系 (User-Permission) - 直接权限
```

## 🔐 权限控制机制

### 1. 权限验证流程

```
请求 → 认证中间件 → 权限中间件 → 角色中间件 → 业务逻辑
```

### 2. 权限检查逻辑

```python
def check_permission(user, permission):
    # 1. 检查直接权限
    if user.has_direct_permission(permission):
        return True
    
    # 2. 检查角色权限
    for role in user.roles:
        if role.has_permission(permission):
            return True
    
    # 3. 权限不足
    return False
```

### 3. 角色检查逻辑

```python
def check_role(user, required_role):
    # 检查用户是否有指定角色
    return required_role in user.roles
```

## 🛠️ 中间件实现

### 1. 认证中间件 (AuthMiddleware)

```python
class AuthMiddleware(Middleware):
    async def handle(self, request, next_handler):
        # 1. 获取Authorization头
        auth_header = request.headers.get("Authorization", "")
        
        # 2. 验证JWT令牌
        token = auth_header[7:]  # 移除"Bearer "前缀
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        
        # 3. 将用户信息添加到请求中
        request.user = {
            "id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", [])
        }
        
        # 4. 继续处理请求
        return await next_handler()
```

### 2. 权限中间件 (PermissionMiddleware)

```python
class PermissionMiddleware(Middleware):
    def __init__(self, required_permissions: list = None):
        self.required_permissions = required_permissions or []
    
    async def handle(self, request, next_handler):
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

### 3. 角色中间件 (RoleMiddleware)

```python
class RoleMiddleware(Middleware):
    def __init__(self, required_roles: list = None):
        self.required_roles = required_roles or []
    
    async def handle(self, request, next_handler):
        # 1. 检查用户是否已认证
        if not request.user:
            return Response(status_code=401, body={"error": "Authentication required"})
        
        # 2. 获取用户角色
        user_roles = request.user.get("roles", [])
        
        # 3. 检查角色
        for role in self.required_roles:
            if role not in user_roles:
                return Response(status_code=403, body={"error": f"Role required: {role}"})
        
        # 4. 继续处理请求
        return await next_handler()
```

## 🎯 使用示例

### 1. 基础权限控制

```python
@api_controller(prefix="/users")
class UserController(ResourceController):
    # 公开路由 - 无需权限
    @get("/public")
    async def public_info(self, request: Request) -> Response:
        return self.success_response(data={"message": "Public information"})
    
    # 需要登录 - 用户资料
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

### 2. 角色权限控制

```python
@api_controller(prefix="/admin")
class AdminController(ResourceController):
    # 需要管理员角色
    @get("/dashboard", middleware=["auth", "admin"])
    async def dashboard(self, request: Request) -> Response:
        return self.success_response(data={"dashboard": "data"})
    
    # 需要经理角色
    @get("/reports", middleware=["auth", "manager"])
    async def reports(self, request: Request) -> Response:
        return self.success_response(data={"reports": []})
    
    # 需要财务角色
    @get("/finance", middleware=["auth", "finance"])
    async def finance(self, request: Request) -> Response:
        return self.success_response(data={"finance": "data"})
```

### 3. 复杂权限组合

```python
@api_controller(prefix="/sensitive")
class SensitiveController(ResourceController):
    # 需要登录 + 管理员权限 + 敏感数据权限
    @get("/data", middleware=["auth", "admin", "sensitive_access"])
    async def sensitive_data(self, request: Request) -> Response:
        return self.success_response(data={"sensitive": "data"})
    
    # 需要登录 + 财务角色 + 审批权限
    @post("/approve", middleware=["auth", "finance", "approve_transactions"])
    async def approve(self, request: Request) -> Response:
        return self.success_response(message="Approved")
```

## 🔧 权限服务实现

### 1. 权限检查服务

```python
class PermissionService:
    def check_permission(self, user: User, permission: str) -> PermissionResponse:
        """检查用户权限"""
        try:
            # 检查直接权限
            if self._has_direct_permission(user, permission):
                return PermissionResponse(allowed=True, result=PermissionResult.ALLOWED)
            
            # 检查角色权限
            if self._has_role_permission(user, permission):
                return PermissionResponse(allowed=True, result=PermissionResult.ALLOWED)
            
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.INSUFFICIENT_PERMISSIONS,
                message=f"缺少权限: {permission}"
            )
        except Exception as e:
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.DENIED,
                message=f"权限检查失败: {str(e)}"
            )
    
    def check_role(self, user: User, role: str) -> PermissionResponse:
        """检查用户角色"""
        try:
            user_roles = self._get_user_roles(user)
            
            if role in user_roles:
                return PermissionResponse(allowed=True, result=PermissionResult.ALLOWED)
            
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.ROLE_REQUIRED,
                message=f"缺少角色: {role}"
            )
        except Exception as e:
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.DENIED,
                message=f"角色检查失败: {str(e)}"
            )
```

### 2. 权限缓存机制

```python
class PermissionService:
    def __init__(self):
        self.cache_enabled = True
        self.permission_cache: Dict[str, List[str]] = {}
        self.role_cache: Dict[str, List[str]] = {}
    
    def get_user_permissions(self, user: User) -> List[str]:
        """获取用户所有权限（带缓存）"""
        # 检查缓存
        if self.cache_enabled and str(user.id) in self.permission_cache:
            return self.permission_cache[str(user.id)]
        
        permissions = []
        
        # 获取直接权限
        direct_permissions = self._get_direct_permissions(user)
        permissions.extend(direct_permissions)
        
        # 获取角色权限
        role_permissions = self._get_role_permissions(user)
        permissions.extend(role_permissions)
        
        # 去重
        permissions = list(set(permissions))
        
        # 缓存结果
        if self.cache_enabled:
            self.permission_cache[str(user.id)] = permissions
        
        return permissions
```

## 📊 数据库设计

### 1. 用户表 (users)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 角色表 (roles)

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 权限表 (permissions)

```sql
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(50),
    action VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. 用户角色关系表 (user_roles)

```sql
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);
```

### 5. 角色权限关系表 (role_permissions)

```sql
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);
```

### 6. 用户权限关系表 (user_permissions)

```sql
CREATE TABLE user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, permission_id)
);
```

## 🎯 权限分配示例

### 1. 角色定义

```python
# 系统角色
ROLES = {
    "admin": {
        "name": "管理员",
        "description": "系统管理员，拥有所有权限",
        "permissions": ["*"]  # 所有权限
    },
    "manager": {
        "name": "经理",
        "description": "部门经理，拥有部门管理权限",
        "permissions": [
            "view_users", "create_users", "update_users",
            "view_reports", "create_reports", "approve_reports"
        ]
    },
    "user": {
        "name": "普通用户",
        "description": "普通用户，只有基本权限",
        "permissions": [
            "view_profile", "update_profile", "view_own_data"
        ]
    },
    "guest": {
        "name": "访客",
        "description": "访客用户，只有查看权限",
        "permissions": [
            "view_public"
        ]
    }
}
```

### 2. 权限定义

```python
# 系统权限
PERMISSIONS = {
    # 用户管理权限
    "view_users": "查看用户列表",
    "create_users": "创建用户",
    "update_users": "更新用户信息",
    "delete_users": "删除用户",
    
    # 报告权限
    "view_reports": "查看报告",
    "create_reports": "创建报告",
    "approve_reports": "审批报告",
    
    # 财务权限
    "view_finance": "查看财务数据",
    "manage_finance": "管理财务数据",
    "approve_transactions": "审批交易",
    
    # 系统权限
    "system_admin": "系统管理",
    "user_admin": "用户管理",
    "role_admin": "角色管理",
    "permission_admin": "权限管理"
}
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

# 401 Unauthorized - 令牌过期
{
    "error": "Token expired",
    "status_code": 401
}
```

### 2. 权限错误

```python
# 403 Forbidden - 权限不足
{
    "error": "Permission denied: admin required",
    "status_code": 403,
    "required_permissions": ["admin"]
}

# 403 Forbidden - 角色不足
{
    "error": "Role required: manager",
    "status_code": 403,
    "required_roles": ["manager"]
}
```

## 🔧 配置管理

### 1. 权限配置

```python
# config/permissions.py
PERMISSION_CONFIG = {
    "cache_enabled": True,
    "cache_ttl": 300,  # 5分钟
    "default_roles": ["user"],
    "admin_roles": ["admin", "super_admin"],
    "guest_roles": ["guest"]
}
```

### 2. 中间件配置

```python
# config/middleware.py
MIDDLEWARE_CONFIG = {
    "auth": {
        "secret_key": "your-secret-key",
        "algorithm": "HS256",
        "token_expire_hours": 24
    },
    "permission": {
        "cache_enabled": True,
        "cache_ttl": 300
    },
    "role": {
        "cache_enabled": True,
        "cache_ttl": 300
    }
}
```

## 📈 性能优化

### 1. 权限缓存

```python
class PermissionService:
    def __init__(self):
        self.cache_enabled = True
        self.permission_cache = {}
        self.role_cache = {}
    
    def get_user_permissions(self, user: User) -> List[str]:
        # 使用缓存避免重复查询
        if self.cache_enabled and str(user.id) in self.permission_cache:
            return self.permission_cache[str(user.id)]
        
        # 查询数据库
        permissions = self._query_permissions(user)
        
        # 缓存结果
        if self.cache_enabled:
            self.permission_cache[str(user.id)] = permissions
        
        return permissions
```

### 2. 批量权限检查

```python
def check_multiple_permissions(self, user: User, permissions: List[str], 
                             require_all: bool = True) -> PermissionResponse:
    """批量检查权限"""
    if require_all:
        # 需要所有权限
        missing_permissions = []
        for permission in permissions:
            if not self._has_permission(user, permission):
                missing_permissions.append(permission)
        
        if missing_permissions:
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.INSUFFICIENT_PERMISSIONS,
                message=f"缺少权限: {', '.join(missing_permissions)}",
                required_permissions=missing_permissions
            )
        
        return PermissionResponse(allowed=True, result=PermissionResult.ALLOWED)
    else:
        # 需要任一权限
        for permission in permissions:
            if self._has_permission(user, permission):
                return PermissionResponse(allowed=True, result=PermissionResult.ALLOWED)
        
        return PermissionResponse(
            allowed=False,
            result=PermissionResult.INSUFFICIENT_PERMISSIONS,
            message=f"缺少权限: {', '.join(permissions)}",
            required_permissions=permissions
        )
```

## 🎯 最佳实践

### 1. 权限设计原则

- **最小权限原则**: 只授予必要的权限
- **权限分离**: 区分认证和授权
- **角色继承**: 支持角色层级关系
- **权限缓存**: 提高性能

### 2. 安全建议

- **定期审计**: 定期检查权限分配
- **权限回收**: 及时回收不需要的权限
- **日志记录**: 记录权限相关操作
- **测试覆盖**: 为权限系统编写测试

### 3. 开发建议

- **权限命名**: 使用清晰的权限命名
- **文档完善**: 详细说明权限含义
- **版本控制**: 管理权限变更
- **监控告警**: 监控权限异常

---

**RBAC权限控制系统** - 为您的应用提供企业级的安全保障！