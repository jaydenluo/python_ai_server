# ORM文件重组说明

## 📁 重组后的文件结构

### 新的文件组织

```
app/
├── core/
│   └── orm/                    # ORM框架核心
│       ├── __init__.py       # ORM模块入口
│       ├── models.py         # 基础模型类 (原 app/models/base.py)
│       ├── query.py          # 查询构建器 (原 app/models/query.py)
│       ├── migration_system.py  # 智能迁移系统
│       ├── commands.py       # ORM命令工具
│       └── decorators.py     # ORM装饰器
├── models/                    # 数据实体目录
│   ├── __init__.py           # 数据模型入口
│   ├── user.py              # 用户实体
│   └── ai_model.py           # AI模型实体
```

## 🎯 重组原则

### 1. 职责分离
- **`app/core/orm/`** - ORM框架核心，提供基础功能
- **`app/models/`** - 具体的数据实体，只包含业务模型

### 2. 文件分类

#### ORM框架文件 (`app/core/orm/`)
- `models.py` - 基础Model类，提供ORM核心功能
- `query.py` - 查询构建器，提供数据库查询功能
- `migration_system.py` - 智能迁移系统
- `commands.py` - 命令行工具
- `decorators.py` - 装饰器系统

#### 数据实体文件 (`app/models/`)
- `user.py` - 用户数据模型
- `ai_model.py` - AI模型数据模型
- 其他业务实体...

## 🔄 迁移过程

### 1. 文件移动
```bash
# 原文件位置
app/models/base.py          → app/core/orm/models.py
app/models/query.py         → app/core/orm/query.py

# 新增文件
app/core/orm/migration_system.py
app/core/orm/commands.py
app/core/orm/decorators.py
```

### 2. 导入路径更新
```python
# 旧导入方式
from app.models.base import Model
from app.models.query import ModelQuery

# 新导入方式
from app.core.orm.models import Model
from app.core.orm.query import ModelQuery
```

### 3. 模块结构优化
```python
# app/core/orm/__init__.py
from .models import Model, RelationshipType, Relationship
from .query import ModelQuery, QueryOperator
from .migration_system import migration_manager
from .commands import ORMCommands
from .decorators import auto_migrate, track_changes

# app/models/__init__.py
from app.core.orm.models import Model
from .user import User
from .ai_model import AIModel
```

## 📋 使用方式

### 1. 导入基础组件
```python
# 导入ORM基础组件
from app.core.orm.models import Model
from app.core.orm.query import ModelQuery
from app.core.orm.decorators import auto_migrate, track_changes

# 导入数据模型
from app.models.user import User
from app.models.ai_model import AIModel
```

### 2. 创建数据模型
```python
# app/models/user.py
from app.core.orm.models import Model
from app.core.orm.decorators import auto_migrate, track_changes

@auto_migrate
@track_changes
class User(Model):
    __table__ = "users"
    username: str
    email: str
```

### 3. 使用ORM功能
```python
# 查询数据
users = User.query().where('status', '=', 'active').get()

# 创建数据
user = User.create(username='john', email='john@example.com')

# 智能迁移
python -m app.core.orm.commands migrate --dry-run
```

## 🎉 重组优势

### 1. 清晰的职责分离
- ORM框架与业务模型分离
- 框架代码集中管理
- 业务模型专注于数据定义

### 2. 更好的可维护性
- 框架功能独立维护
- 业务模型独立开发
- 减少文件间的耦合

### 3. 更灵活的扩展
- 可以独立升级ORM框架
- 可以独立开发业务模型
- 支持插件化扩展

### 4. 更清晰的依赖关系
- 业务模型依赖ORM框架
- ORM框架不依赖业务模型
- 避免循环依赖

## 🚀 下一步计划

1. **完善数据库连接** - 实现真实的数据库操作
2. **添加测试用例** - 确保系统稳定性
3. **优化性能** - 大表查询的性能优化
4. **添加监控** - 查询和迁移的监控

---

**文件重组完成！** 现在ORM框架和数据实体有了清晰的分离，更易于维护和扩展。