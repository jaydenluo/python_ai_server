# 控制器组织结构

## 📁 目录结构

```
app/api/controllers/
├── __init__.py                    # 控制器模块入口
├── base.py                        # 基础控制器类
├── user_controller.py             # V1 用户控制器
├── ai_model_controller.py         # V1 AI模型控制器
├── user_controller_v2.py          # V2 用户控制器
├── ai_model_controller_v2.py      # V2 AI模型控制器
├── admin/                         # 管理员控制器模块
│   ├── __init__.py
│   ├── user_controller.py         # 管理员用户控制器
│   ├── role_controller.py         # 管理员角色控制器
│   └── permission_controller.py   # 管理员权限控制器
├── api/                           # API控制器模块
│   ├── __init__.py
│   ├── user_controller.py         # API用户控制器
│   ├── ai_model_controller.py     # API AI模型控制器
│   └── auth_controller.py          # API认证控制器
└── web/                           # Web控制器模块
    ├── __init__.py
    ├── home_controller.py          # Web首页控制器
    ├── user_controller.py         # Web用户控制器
    └── ai_controller.py            # Web AI控制器
```

## 🎯 控制器分类

### 1. 管理员控制器 (`/admin`)

**前缀**: `/admin`  
**中间件**: `["auth", "admin"]`  
**用途**: 管理员专用功能

#### 控制器列表:
- **AdminUserController** - 管理员用户管理
  - `GET /admin/users` - 获取所有用户列表
  - `GET /admin/users/{id}` - 获取用户详细信息
  - `POST /admin/users` - 创建用户
  - `PUT /admin/users/{id}` - 更新用户信息
  - `DELETE /admin/users/{id}` - 删除用户
  - `POST /admin/users/{id}/reset-password` - 重置用户密码

- **AdminRoleController** - 管理员角色管理
  - `GET /admin/roles` - 获取角色列表
  - `GET /admin/roles/{id}` - 获取角色详细信息
  - `POST /admin/roles` - 创建角色
  - `PUT /admin/roles/{id}` - 更新角色信息
  - `DELETE /admin/roles/{id}` - 删除角色

- **AdminPermissionController** - 管理员权限管理
  - `GET /admin/permissions` - 获取权限列表
  - `GET /admin/permissions/{id}` - 获取权限详细信息
  - `POST /admin/permissions` - 创建权限
  - `PUT /admin/permissions/{id}` - 更新权限信息
  - `DELETE /admin/permissions/{id}` - 删除权限

### 2. API控制器 (`/api`)

**前缀**: `/api`  
**中间件**: `["auth"]` (认证控制器除外)  
**用途**: API接口功能

#### 控制器列表:
- **APIUserController** - API用户管理
  - `GET /api/users` - 获取用户列表
  - `GET /api/users/{id}` - 获取用户详细信息
  - `POST /api/users` - 创建用户
  - `PUT /api/users/{id}` - 更新用户信息
  - `DELETE /api/users/{id}` - 删除用户

- **APIAIModelController** - API AI模型管理
  - `GET /api/ai-models` - 获取AI模型列表
  - `GET /api/ai-models/{id}` - 获取AI模型详细信息
  - `POST /api/ai-models` - 创建AI模型
  - `POST /api/ai-models/{id}/predict` - AI模型预测
  - `PUT /api/ai-models/{id}` - 更新AI模型信息
  - `DELETE /api/ai-models/{id}` - 删除AI模型

- **APIAuthController** - API认证管理
  - `POST /api/auth/login` - 用户登录
  - `POST /api/auth/register` - 用户注册
  - `POST /api/auth/logout` - 用户登出
  - `POST /api/auth/refresh` - 刷新访问令牌
  - `GET /api/auth/me` - 获取当前用户信息

### 3. Web控制器 (`/web`)

**前缀**: `/web`  
**中间件**: `["anonymous"]` (用户相关功能除外)  
**用途**: Web页面功能

#### 控制器列表:
- **WebHomeController** - Web首页管理
  - `GET /web/` - 首页
  - `GET /web/about` - 关于页面
  - `GET /web/contact` - 联系我们
  - `POST /web/contact` - 提交联系表单
  - `GET /web/features` - 功能特性

- **WebUserController** - Web用户管理
  - `GET /web/profile` - 用户资料页面
  - `GET /web/settings` - 用户设置页面
  - `POST /web/settings` - 更新用户设置
  - `GET /web/dashboard` - 用户仪表板
  - `GET /web/activity` - 用户活动记录

- **WebAIController** - Web AI管理
  - `GET /web/ai` - AI模型展示页面
  - `GET /web/ai/{id}` - AI模型详情页面
  - `POST /web/ai/{id}/try` - 试用AI模型
  - `GET /web/ai/create` - 创建AI模型页面
  - `POST /web/ai/create` - 创建AI模型

## 🔗 路由映射表

| 控制器类型 | 前缀 | 中间件 | 用途 | 示例路由 |
|------------|------|--------|------|----------|
| Admin | `/admin` | `["auth", "admin"]` | 管理员功能 | `GET /admin/users` |
| API | `/api` | `["auth"]` | API接口 | `GET /api/users` |
| Web | `/web` | `["anonymous"]` | Web页面 | `GET /web/` |

## 💡 使用示例

### 1. 管理员功能
```python
# 管理员用户管理
@api_controller(prefix="/admin", version="v1", middleware=["auth", "admin"])
class AdminUserController(ResourceController):
    @get("/users")
    async def index(self, request: Request) -> Response:
        # 管理员专用功能
        pass
```

### 2. API功能
```python
# API用户管理
@api_controller(prefix="/api", version="v1", middleware=["auth"])
class APIUserController(ResourceController):
    @get("/users")
    async def index(self, request: Request) -> Response:
        # API接口功能
        pass
```

### 3. Web功能
```python
# Web首页
@api_controller(prefix="/web", version="v1", middleware=["anonymous"])
class WebHomeController(ResourceController):
    @get("/")
    async def index(self, request: Request) -> Response:
        # Web页面功能
        pass
```

## 🎯 优势

1. **模块化组织** - 按功能模块组织控制器
2. **清晰分离** - 管理员、API、Web功能分离
3. **统一前缀** - 每个模块有统一的前缀
4. **中间件管理** - 每个模块有合适的中间件配置
5. **易于维护** - 功能模块化，便于维护和扩展

## 📋 最佳实践

1. **控制器命名** - 使用描述性的控制器名称
2. **路由命名** - 使用模块前缀 + 功能名称
3. **中间件配置** - 根据功能需求配置合适的中间件
4. **版本控制** - 使用版本参数进行API版本控制
5. **文档注释** - 为每个控制器和方法添加详细的文档注释

---

**控制器组织结构** - 让代码更清晰、更易维护！