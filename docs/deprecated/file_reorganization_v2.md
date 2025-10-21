# 文件重组说明 v2

## 📁 重组概述

将API相关文件从 `app/api/` 移动到 `app/core/` 下，实现更清晰的架构分层。

## 🔄 移动的文件

### 1. 路由相关文件
- **原位置**: `app/api/decorators/route_decorators.py`
- **新位置**: `app/core/routing/route_decorators.py`
- **说明**: 路由装饰器是核心功能，应该放在core模块

### 2. 文档生成文件
- **原位置**: `app/api/docs/openapi_generator.py`
- **新位置**: `app/core/docs/openapi_generator.py`
- **说明**: 文档生成是框架核心功能

### 3. 中间件文件
- **原位置**: `app/api/middleware/api_middleware.py`
- **新位置**: `app/core/middleware/api_middleware.py`
- **说明**: API中间件是核心中间件功能

### 4. 控制器基类
- **原位置**: `app/api/controllers/base.py`
- **新位置**: `app/core/controllers/base_controller.py`
- **说明**: 控制器基类是核心组件

## 📂 新的目录结构

```
app/
├── core/                    # 核心框架功能
│   ├── routing/             # 路由系统
│   │   ├── __init__.py
│   │   ├── route_decorators.py
│   │   └── route_registry.py
│   ├── docs/                # 文档生成
│   │   ├── __init__.py
│   │   └── openapi_generator.py
│   ├── middleware/          # 中间件系统
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── logging.py
│   │   ├── rate_limit.py
│   │   └── api_middleware.py
│   ├── controllers/         # 控制器基类
│   │   ├── __init__.py
│   │   └── base_controller.py
│   ├── container/           # 依赖注入
│   ├── events/              # 事件系统
│   ├── config/              # 配置管理
│   ├── cache/               # 缓存系统
│   ├── models/              # 模型基类
│   ├── mixins/              # 混入类
│   ├── orm/                 # ORM系统
│   ├── query_builder/       # 查询构建器
│   └── repositories/        # 仓储层
└── api/                     # API应用层
    └── controllers/         # 具体控制器实现
        ├── admin/           # 管理端控制器
        ├── api/             # API控制器
        └── web/             # Web控制器
```

## 🎯 重组优势

### 1. 清晰的架构分层
- **core模块**: 框架核心功能，可复用
- **api模块**: 应用层实现，业务相关

### 2. 更好的模块化
- 核心功能独立，易于测试
- 应用层专注于业务逻辑

### 3. 便于维护
- 框架功能集中管理
- 减少文件查找时间

## 📝 导入路径更新

### 路由装饰器
```python
# 旧导入
from app.api.decorators import get, post, put, delete

# 新导入
from app.core.routing import get, post, put, delete
```

### 文档生成
```python
# 旧导入
from app.api.docs import OpenAPIGenerator

# 新导入
from app.core.docs import OpenAPIGenerator
```

### 中间件
```python
# 旧导入
from app.api.middleware import APIVersionMiddleware

# 新导入
from app.core.middleware.api_middleware import APIVersionMiddleware
```

### 控制器基类
```python
# 旧导入
from app.api.controllers.base import BaseController

# 新导入
from app.core.controllers import BaseController
```

## 🔧 迁移步骤

1. **更新导入路径**: 修改所有引用这些文件的代码
2. **测试功能**: 确保所有功能正常工作
3. **清理旧文件**: 删除已移动的文件
4. **更新文档**: 更新相关文档和示例

## ✅ 完成状态

- [x] 移动路由装饰器
- [x] 移动文档生成器
- [x] 移动API中间件
- [x] 移动控制器基类
- [x] 更新导入路径
- [x] 删除旧文件
- [x] 创建新的__init__.py文件

## 🎉 总结

通过这次重组，我们实现了：

1. **更清晰的架构**: 核心功能与应用层分离
2. **更好的可维护性**: 相关功能集中管理
3. **更易扩展**: 核心功能可独立升级
4. **更符合最佳实践**: 遵循框架设计原则

这样的架构更有利于长期维护和功能扩展！