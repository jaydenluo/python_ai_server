# 🔌 API 参考

API 框架和控制器的详细文档。

## 📚 文档列表

### 1. [API 框架](framework.md)
**内容**: API 框架完整文档
- FastAPI 集成
- 路由注册
- 请求处理
- 响应格式
- 错误处理
- API 版本控制

### 2. [控制器](controllers.md)
**内容**: 控制器组织和使用
- 控制器基类
- RESTful 控制器
- 资源控制器
- 控制器装饰器
- 请求验证
- 响应序列化

## 🎯 快速参考

### 创建 API 端点

```python
from app.core.controllers.base_controller import *

@api_controller(prefix="/api", version="v1")
class UserController(ResourceController):
    """用户控制器"""
    
    @get("/users")
    async def get_users(self):
        """获取用户列表"""
        return {"users": []}
    
    @post("/users")
    async def create_user(self, user_data: dict):
        """创建用户"""
        return {"user": user_data}
```

### 使用认证

```python
@api_controller(prefix="/api", version="v1")
@auth  # 添加认证装饰器
class ProtectedController(BaseController):
    """受保护的控制器"""
    
    @get("/protected")
    async def protected_route(self):
        """需要认证的路由"""
        return {"message": "This is protected"}
```

## 📖 相关文档

- **路由系统**: [architecture/routing.md](../architecture/routing.md)
- **API 使用指南**: [guides/api-usage.md](../guides/api-usage.md)
- **中间件**: [architecture/middleware.md](../architecture/middleware.md)

---

[← 返回文档中心](../README.md)

