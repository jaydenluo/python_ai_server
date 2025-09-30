# 自动模型发现系统

## 概述

自动模型发现系统允许你**只需要写好实体类**，无需在 `__init__.py` 中手动注册。系统会自动扫描和导入所有模型。

## 核心特性

✅ **零配置**：写好模型类即可，无需手动注册  
✅ **自动发现**：自动扫描 `entities/` 和 `enums/` 目录  
✅ **懒加载**：按需加载模型类  
✅ **智能导入**：支持多种导入方式  
✅ **热重载**：支持运行时重新扫描  

## 使用方法

### 1. 创建模型类

只需要在对应目录下创建模型文件：

```python
# app/models/entities/user.py
from app.core.models.base import BaseModel

class User(BaseModel):
    name: str
    email: str
```

```python
# app/models/enums/user_status.py
from enum import Enum

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
```

### 2. 导入模型

#### 方式1：直接导入（推荐）
```python
from app.models import User, UserStatus

# 直接使用
user = User(name="张三", email="zhang@example.com")
status = UserStatus.ACTIVE
```

#### 方式2：智能导入器
```python
from app.models import smart_models

# 动态获取模型
User = smart_models.User
UserStatus = smart_models.UserStatus

user = User(name="张三", email="zhang@example.com")
```

#### 方式3：便捷函数
```python
from app.models import get_model, list_models

# 列出所有可用模型
models = list_models()
print(models)  # ['User', 'AIModel', 'Post', 'Comment', 'UserStatus', ...]

# 获取特定模型
User = get_model('User')
UserStatus = get_model('UserStatus')
```

### 3. 高级功能

#### 重新扫描模型
```python
from app.models import reload_models

# 重新扫描所有模型（开发时有用）
reload_models()
```

#### 检查可用模型
```python
from app.models import list_models

available_models = list_models()
for model_name in available_models:
    print(f"发现模型: {model_name}")
```

## 目录结构

```
app/models/
├── __init__.py              # 自动导入配置
├── entities/                # 实体模型目录
│   ├── __init__.py         # 可选，系统会自动扫描
│   ├── user.py            # User 类
│   ├── ai_model.py        # AIModel 类
│   └── post.py            # Post 类
└── enums/                  # 枚举目录
    ├── __init__.py         # 可选，系统会自动扫描
    ├── user_status.py     # UserStatus 枚举
    └── model_status.py    # ModelStatus 枚举
```

## 优势对比

### 传统方式（需要手动注册）
```python
# 1. 创建模型文件
# app/models/entities/user.py
class User(BaseModel): ...

# 2. 在 entities/__init__.py 中注册
from .user import User
__all__ = ["User"]

# 3. 在主 __init__.py 中注册
from .entities import User
__all__ = ["User"]
```

### 自动发现方式（零配置）
```python
# 1. 创建模型文件
# app/models/entities/user.py
class User(BaseModel): ...

# 2. 直接使用
from app.models import User  # 自动发现！
```

## 注意事项

1. **文件命名**：模型文件名应该与类名匹配（不区分大小写）
2. **类名规范**：类名应该以大写字母开头
3. **模块结构**：模型类必须在正确的目录下（entities/ 或 enums/）
4. **导入路径**：建议使用 `from app.models import ModelName` 方式

## 故障排除

### 模型未找到
```python
# 检查模型是否在正确目录
from app.models import list_models
print(list_models())  # 查看所有发现的模型

# 手动重新扫描
from app.models import reload_models
reload_models()
```

### 导入错误
```python
# 使用智能导入器
from app.models import smart_models
try:
    User = smart_models.User
except AttributeError:
    print("User 模型未找到")
```

## 总结

自动模型发现系统让你专注于**编写业务逻辑**，而不是管理导入配置。只需要：

1. ✅ 在 `entities/` 或 `enums/` 目录下创建模型文件
2. ✅ 使用 `from app.models import ModelName` 导入
3. ✅ 开始使用模型

**无需**在 `__init__.py` 中手动注册！