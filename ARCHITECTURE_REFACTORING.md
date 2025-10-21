# 架构重构说明

## 🎯 重构目标

1. ✅ 将框架核心组件和业务服务分离
2. ✅ 遵循单一职责原则
3. ✅ 更清晰的目录结构

## 📁 目录结构调整

### 之前（不规范）

```
app/
├── core/
│   ├── repositories/
│   │   └── repository.py          ← 框架核心
│   └── controllers/
│       └── base_controller.py     ← 框架核心
└── services/
    └── base_service.py             ← ❌ 混合了框架核心和业务代码
        ├── BaseService (核心)      ← 应该在 core
        └── UserService (业务)      ← 应该独立文件
```

### 现在（规范）

```
app/
├── core/                           ← 框架核心目录
│   ├── repositories/
│   │   └── repository.py          ← 数据访问层基类
│   ├── controllers/
│   │   └── base_controller.py     ← 控制器基类
│   └── services/                   ← ✅ 新增
│       ├── __init__.py
│       └── base_service.py        ← ✅ 服务层基类
└── services/                       ← 业务服务目录
    ├── base_service.py            ← ⚠️ 废弃（向后兼容）
    ├── user_service.py            ← ✅ 用户服务（新增）
    ├── auth_service.py            ← 认证服务
    └── ai/
        ├── voice_service.py       ← AI服务
        └── xunfei_service.py      ← 第三方服务
```

## 🔄 主要变更

### 1. BaseService 位置调整

**之前**：
```python
# app/services/base_service.py
class BaseService:
    """基础服务类"""
    pass

class UserService(BaseService):  # ❌ 混在一起
    """用户服务"""
    pass
```

**现在**：
```python
# app/core/services/base_service.py
class BaseService:
    """基础服务类 - 框架核心"""
    pass

# app/services/user_service.py
class UserService(BaseService):  # ✅ 独立文件
    """用户服务 - 业务实现"""
    pass
```

### 2. 导入路径变更

**推荐使用新路径**：
```python
from app.core.services import BaseService  # ✅ 新路径
```

**旧路径仍然兼容**（但会在未来版本移除）：
```python
from app.services.base_service import BaseService  # ⚠️ 已废弃
```

## 📝 迁移指南

### 如果你正在使用 BaseService

#### 步骤 1: 更新导入路径

```python
# 之前
from app.services.base_service import BaseService

# 现在
from app.core.services import BaseService
```

#### 步骤 2: 检查是否真的需要继承

如果你的服务**不需要数据库操作**，考虑移除继承：

```python
# 如果服务只调用第三方API或处理内存数据
class MyService:  # ✅ 不继承
    def __init__(self):
        pass

# 如果服务需要 CRUD 操作
class MyService(BaseService):  # ✅ 继承
    def __init__(self, session):
        repository = Repository(MyModel, session)
        super().__init__(repository)
```

## 🏗️ 设计原则

### Core vs Services

| 目录 | 用途 | 特点 | 示例 |
|------|------|------|------|
| **app/core/** | 框架核心组件 | 通用、可复用、不包含业务逻辑 | Repository, BaseService, BaseController |
| **app/services/** | 业务服务 | 具体业务逻辑、领域模型 | UserService, OrderService, PaymentService |

### 判断是否应该放在 core

**问题清单**：
1. 是否是所有项目都需要的通用功能？
2. 是否与具体业务逻辑无关？
3. 是否可以直接在其他项目中复用？

如果**全部回答"是"** → 放在 `app/core/`  
如果**有任何"否"** → 放在 `app/services/`

**示例**：

| 组件 | 是否 core | 原因 |
|------|-----------|------|
| BaseService | ✅ 是 | 所有项目都需要，通用基类 |
| UserService | ❌ 否 | 特定业务，用户管理逻辑 |
| Repository | ✅ 是 | 数据访问通用模式 |
| OrderService | ❌ 否 | 特定业务，订单管理逻辑 |
| BaseController | ✅ 是 | 控制器通用基类 |
| XunfeiService | ❌ 否 | 特定第三方服务封装 |

## ⚠️ 废弃通知

### app/services/base_service.py

此文件已标记为**废弃（DEPRECATED）**：

```python
"""
⚠️ DEPRECATED - 已废弃

此文件已移动到 app/core/services/base_service.py
请更新导入路径
"""
```

**时间线**：
- ✅ **当前版本**：保留文件，仅用于向后兼容
- ⚠️ **下一个版本（v2.1）**：显示弃用警告
- ❌ **v3.0**：完全移除此文件

## ✨ 优势

### 重构前

```
❌ BaseService 和 UserService 混在一个文件
❌ 框架核心和业务逻辑耦合
❌ 不清楚哪些是可复用的核心组件
❌ 难以单独测试和维护
```

### 重构后

```
✅ 清晰的分层：core（框架）和 services（业务）
✅ 单一职责：每个文件只负责一个类
✅ 易于理解：一看目录就知道哪些是核心，哪些是业务
✅ 便于维护：框架升级不影响业务代码
✅ 更好的可测试性：可以单独测试核心组件
```

## 🔍 相关文档

- [SERVICE_ARCHITECTURE.md](./SERVICE_ARCHITECTURE.md) - 服务架构指南
- [API_DEVELOPMENT_GUIDE.md](./API_DEVELOPMENT_GUIDE.md) - API开发指南

## 📞 问题反馈

如果在迁移过程中遇到问题，请查看：
1. 是否已更新导入路径
2. 是否真的需要继承 BaseService
3. 参考 `app/services/user_service.py` 的实现示例

