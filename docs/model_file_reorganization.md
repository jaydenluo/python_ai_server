# 模型文件重组说明

## 📁 新的文件结构

### 重组后的目录结构

```
app/
├── models/
│   ├── __init__.py           # 模型模块入口
│   ├── entities/             # 数据实体目录
│   │   ├── __init__.py      # 实体模块入口
│   │   ├── user.py          # 用户实体
│   │   ├── ai_model.py      # AI模型实体
│   │   ├── post.py          # 文章实体
│   │   └── comment.py        # 评论实体
│   └── enums/               # 枚举类型目录
│       ├── __init__.py      # 枚举模块入口
│       ├── model_status.py  # 模型状态枚举
│       ├── model_type.py    # 模型类型枚举
│       └── user_status.py   # 用户状态枚举
```

## 🎯 重组原则

### 1. 一个文件一个类
- 每个实体类独占一个文件
- 每个枚举类独占一个文件
- 便于维护和扩展

### 2. 按功能分类
- **`entities/`** - 数据实体，包含业务模型
- **`enums/`** - 枚举类型，包含状态和类型定义

### 3. 清晰的命名
- 文件名与类名保持一致
- 使用下划线命名法
- 避免文件名冲突

## 📋 文件说明

### 数据实体文件

#### 1. `app/models/entities/user.py`
```python
class User(Model):
    """用户模型"""
    __table__ = "users"
    # 用户相关属性和方法
```

#### 2. `app/models/entities/ai_model.py`
```python
class AIModel(Model):
    """AI模型"""
    __table__ = "ai_models"
    # AI模型相关属性和方法
```

#### 3. `app/models/entities/post.py`
```python
class Post(Model):
    """文章模型"""
    __table__ = "posts"
    # 文章相关属性和方法
```

#### 4. `app/models/entities/comment.py`
```python
class Comment(Model):
    """评论模型"""
    __table__ = "comments"
    # 评论相关属性和方法
```

### 枚举类型文件

#### 1. `app/models/enums/model_status.py`
```python
class ModelStatus(Enum):
    """模型状态枚举"""
    TRAINING = "training"
    TRAINED = "trained"
    # 其他状态...
```

#### 2. `app/models/enums/model_type.py`
```python
class ModelType(Enum):
    """模型类型枚举"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    # 其他类型...
```

#### 3. `app/models/enums/user_status.py`
```python
class UserStatus(Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    # 其他状态...
```

## 🚀 使用方式

### 1. 导入数据实体
```python
# 导入单个实体
from app.models.entities.user import User
from app.models.entities.ai_model import AIModel

# 导入多个实体
from app.models.entities import User, AIModel, Post, Comment
```

### 2. 导入枚举类型
```python
# 导入单个枚举
from app.models.enums.model_status import ModelStatus
from app.models.enums.model_type import ModelType

# 导入多个枚举
from app.models.enums import ModelStatus, ModelType, UserStatus
```

### 3. 统一导入
```python
# 从主模块导入
from app.models import User, AIModel, Post, Comment
from app.models import ModelStatus, ModelType, UserStatus
```

## 🎉 重组优势

### 1. 单一职责原则
- 每个文件只负责一个类
- 职责清晰，易于理解
- 便于维护和测试

### 2. 更好的可维护性
- 修改一个类不影响其他类
- 文件结构清晰
- 便于代码审查

### 3. 更灵活的扩展
- 新增实体只需创建新文件
- 不影响现有代码
- 支持团队协作开发

### 4. 更清晰的依赖关系
- 实体间依赖关系明确
- 避免循环依赖
- 便于重构

## 📈 最佳实践

### 1. 文件命名
- 使用小写字母和下划线
- 文件名与类名保持一致
- 避免使用特殊字符

### 2. 类设计
- 每个类只负责一个业务实体
- 保持类的内聚性
- 避免过大的类

### 3. 导入管理
- 使用相对导入
- 避免循环导入
- 合理使用__all__

### 4. 文档注释
- 每个文件都有文档说明
- 每个类都有详细注释
- 方法都有参数和返回值说明

## 🔄 迁移指南

### 1. 旧文件处理
```bash
# 删除旧文件
rm app/models/user.py
rm app/models/ai_model.py
```

### 2. 导入路径更新
```python
# 旧导入方式
from app.models.user import User
from app.models.ai_model import AIModel

# 新导入方式
from app.models.entities.user import User
from app.models.entities.ai_model import AIModel
```

### 3. 代码更新
- 更新所有导入语句
- 测试现有功能
- 更新相关文档

---

**模型文件重组完成！** 现在每个类都有独立的文件，结构更加清晰和易于维护。