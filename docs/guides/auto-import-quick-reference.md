# 自动导入系统快速参考

## 🎯 简介

自动导入系统让您无需在 `__init__.py` 中手动注册类，系统会自动发现并导入所有模型、服务和控制器。

## 🚀 快速使用

### 1. 设置自动导入

在任何包的 `__init__.py` 文件中，只需添加两行代码：

```python
from app.core.discovery.module_hooks import setup_smart_import
__getattr__, __dir__ = setup_smart_import(__name__)
```

### 2. 正常导入使用

```python
# 导入模型
from app.models.entities import User, AIModel, Post, Comment

# 导入服务
from app.services import AuthService, BaseService, PermissionService

# 导入AI服务
from app.services.ai import WorkflowService, AgentService, RAGService

# 导入控制器
from app.controller.admin import UserAdminApi, RoleAdminApi
from app.controller.api import UserApi, AuthApi
from app.controller.web import UserWebApi, AIWebApi
```

### 3. 查看可用类

```python
import app.models.entities as entities
print(dir(entities))  # 显示所有可用模型

import app.services as services
print(dir(services))   # 显示所有可用服务
```

## 📋 类识别规则

系统会自动识别以下类型的类：

### 模型类
- 继承自 `BaseModel`、`Model`、`Entity` 等基类
- 包含 `__tablename__` 属性
- 类名以 `Model` 或 `Entity` 结尾

### 服务类
- 继承自 `BaseService` 基类
- 类名以 `Service` 结尾

### 控制器类
- 使用 `@api_controller` 装饰器
- 类名包含 `Controller` 或以 `Api` 结尾

## ✨ 主要优势

- **极简设置**: 只需2行代码
- **自动发现**: 无需手动注册
- **延迟加载**: 提高启动性能
- **IDE支持**: 完整的自动补全
- **透明使用**: 导入体验完全一致

## 🔧 已配置的模块

以下模块已经配置了自动导入：

- `app.models.entities` - 数据模型
- `app.services` - 业务服务
- `app.services.ai` - AI服务
- `app.controller.admin` - 管理员控制器
- `app.controller.api` - API控制器
- `app.controller.web` - Web控制器

## 📝 示例

```python
# 创建用户
from app.models.entities import User
user = User(name="张三", email="zhang@example.com")

# 使用认证服务
from app.services import AuthService
auth = AuthService()
result = auth.login(username="admin", password="123456")

# 使用AI工作流服务
from app.services.ai import WorkflowService
workflow = WorkflowService()
workflow.create_workflow("数据分析流程")

# 使用控制器
from app.controller.api import UserApi
api = UserApi()
```

## 🎉 就这么简单！

现在您可以专注于业务逻辑，而不用担心导入配置。系统会自动处理所有的类发现和导入工作。