# 智能ORM系统使用指南

## 🎯 系统概述

智能ORM系统能够通过修改模型实体自动更新数据库表结构，提供以下核心功能：

1. **模型变更检测** - 自动检测模型结构变更
2. **自动迁移生成** - 根据模型变更生成迁移文件
3. **数据库同步** - 自动更新数据库表结构
4. **数据保护** - 保护现有数据不丢失
5. **回滚机制** - 支持迁移回滚

## 🚀 快速开始

### 1. 基础模型定义

```python
from app.models.base import Model
from app.core.orm.decorators import auto_migrate, track_changes, auto_timestamps, auto_validate
from app.core.orm.decorators import required, email, min_length, max_length

@auto_migrate
@track_changes
@auto_timestamps
@auto_validate
class User(Model):
    """用户模型"""
    
    __table__ = "users"
    __fillable__ = ["username", "email", "first_name", "last_name"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 添加验证规则
        self.add_validation_rule("username", required)
        self.add_validation_rule("username", min_length(3))
        self.add_validation_rule("username", max_length(20))
        
        self.add_validation_rule("email", required)
        self.add_validation_rule("email", email)
        
        self.add_validation_rule("first_name", required)
        self.add_validation_rule("first_name", min_length(2))
```

### 2. 模型变更检测

当你修改模型时，系统会自动检测变更：

```python
# 原始模型
class User(Model):
    username: str
    email: str

# 修改后的模型
class User(Model):
    username: str
    email: str
    phone: str          # 新增字段
    age: int           # 新增字段
    status: str = "active"  # 新增字段，带默认值
```

### 3. 自动迁移生成

系统会自动生成迁移文件：

```python
# 生成的迁移文件: 20241201_143022_a1b2c3d4_users.py
"""
迁移文件: Add column phone to users
生成时间: 2024-12-01 14:30:22
"""

def up():
    """执行迁移"""
    sql = "ALTER TABLE users ADD COLUMN phone VARCHAR(255);"
    # 执行SQL
    database.execute(sql)

def down():
    """回滚迁移"""
    sql = "ALTER TABLE users DROP COLUMN phone;"
    # 执行SQL
    database.execute(sql)
```

## 🔧 命令行工具

### 1. 检测模型变更

```bash
# 预览模式，不执行迁移
python -m app.core.orm.commands migrate --dry-run

# 执行迁移
python -m app.core.orm.commands migrate --execute
```

### 2. 查看模型状态

```bash
# 查看所有模型状态
python -m app.core.orm.commands status
```

### 3. 生成新模型

```bash
# 生成新模型
python -m app.core.orm.commands generate Product --table products
```

### 4. 分析模型结构

```bash
# 分析模型结构
python -m app.core.orm.commands analyze
```

## 🎨 装饰器系统

### 1. 自动迁移装饰器

```python
@auto_migrate
class User(Model):
    """自动检测变更并生成迁移"""
    pass
```

### 2. 变更跟踪装饰器

```python
@track_changes
class User(Model):
    """跟踪模型属性变更"""
    
    def save(self):
        if self.has_changes():
            changes = self.get_changes()
            print(f"检测到变更: {changes}")
        super().save()
```

### 3. 自动时间戳装饰器

```python
@auto_timestamps
class User(Model):
    """自动添加created_at和updated_at字段"""
    pass
```

### 4. 自动验证装饰器

```python
@auto_validate
class User(Model):
    """自动验证模型数据"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_validation_rule("email", required)
        self.add_validation_rule("email", email)
```

## 📊 迁移类型

### 1. 创建表

```python
# 当创建新模型时
class NewModel(Model):
    __table__ = "new_table"
    name: str
    description: str
```

### 2. 添加列

```python
# 当添加新字段时
class User(Model):
    username: str
    email: str
    phone: str  # 新增字段
```

### 3. 删除列

```python
# 当删除字段时
class User(Model):
    username: str
    # email: str  # 删除字段
```

### 4. 修改列

```python
# 当修改字段类型时
class User(Model):
    username: str
    age: int  # 从 str 改为 int
```

## 🔒 数据保护机制

### 1. 备份策略

```python
# 自动备份重要数据
@auto_migrate(backup=True)
class User(Model):
    pass
```

### 2. 数据迁移

```python
# 自定义数据迁移
def migrate_user_data():
    """迁移用户数据"""
    users = User.all()
    for user in users:
        if not hasattr(user, 'phone'):
            user.phone = ""
            user.save()
```

### 3. 回滚机制

```python
# 支持迁移回滚
def rollback_migration(migration_id: str):
    """回滚指定迁移"""
    migration_manager.rollback(migration_id)
```

## 🎯 最佳实践

### 1. 模型设计

```python
# 使用类型注解
class User(Model):
    username: str
    email: str
    age: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

### 2. 验证规则

```python
# 添加适当的验证规则
class User(Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 必填验证
        self.add_validation_rule("username", required)
        self.add_validation_rule("email", required)
        
        # 格式验证
        self.add_validation_rule("email", email)
        
        # 长度验证
        self.add_validation_rule("username", min_length(3))
        self.add_validation_rule("username", max_length(20))
```

### 3. 关系定义

```python
# 定义模型关系
class User(Model):
    posts: List['Post'] = relationship("has_many", "Post", "user_id")

class Post(Model):
    user: 'User' = relationship("belongs_to", "User", "user_id")
```

## 🚨 注意事项

### 1. 生产环境

- 在生产环境使用前，务必在测试环境验证迁移
- 重要数据变更前，先备份数据库
- 使用 `--dry-run` 参数预览变更

### 2. 数据完整性

- 删除字段前，确保没有重要数据
- 修改字段类型时，注意数据兼容性
- 添加非空字段时，提供默认值

### 3. 性能考虑

- 大表结构变更可能影响性能
- 考虑在低峰期执行迁移
- 使用索引优化查询性能

## 📈 高级功能

### 1. 自定义迁移

```python
# 自定义迁移逻辑
def custom_migration():
    """自定义迁移"""
    # 复杂的数据迁移逻辑
    pass
```

### 2. 批量操作

```python
# 批量模型操作
def batch_update_models():
    """批量更新模型"""
    models = [User, Post, Comment]
    migration_manager.auto_migrate(models)
```

### 3. 监控和日志

```python
# 迁移监控
def monitor_migrations():
    """监控迁移状态"""
    status = migration_manager.get_status()
    print(f"待执行迁移: {status['pending']}")
    print(f"已执行迁移: {status['executed']}")
```

---

**智能ORM系统** - 让数据库管理更智能、更安全！