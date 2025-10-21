# 控制器结构规范

## 📁 目录结构

所有控制器必须放在 `app/controller/` 目录下，按功能模块组织：

```
app/controller/
├── admin/          # 后台管理控制器
├── api/            # API 控制器（标准 REST API）
└── web/            # Web 控制器（前端页面）
```

## ⚠️ 重要规则

1. **禁止在 `app/api/` 下编写控制器逻辑**
   - `app/api/` 目录只用于路由注册
   - 所有业务逻辑必须在 `app/controller/` 下

2. **路由文件只负责路由注册**
   - `app/api/v1/users.py` → 只导入并注册路由
   - `app/controller/api/user_controller.py` → 实际的控制器逻辑

## 📝 示例

### ✅ 正确的做法

**app/controller/api/user_controller.py**（控制器）：
```python
from fastapi import APIRouter, Depends
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.get("")
async def get_users(user_service: UserService = Depends()):
    """获取用户列表"""
    return user_service.get_all_users()
```

**app/api/v1/users.py**（路由注册）：
```python
from app.controller.api.user_controller import router

__all__ = ["router"]
```

### ❌ 错误的做法

**app/api/v1/users.py**（不要这样做）：
```python
# ❌ 不要在 api 目录下编写控制器逻辑
from fastapi import APIRouter

router = APIRouter(prefix="/users")

@router.get("")
async def get_users():
    # ❌ 业务逻辑不应该在这里
    pass
```

## 🔄 迁移指南

如果现有代码在 `app/api/` 下有控制器逻辑：

1. 将控制器逻辑移到 `app/controller/` 对应目录
2. 在原路由文件中只保留导入和注册
3. 更新相关的导入引用

## 📚 相关文件

- `app/framework.py` - 框架主入口，负责注册所有路由
- `app/api/v1/__init__.py` - v1 API 路由汇总
- `app/controller/api/` - API 控制器目录


