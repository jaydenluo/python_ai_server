# 基于SQLAlchemy的实体模型设计指南

## 🎯 为什么选择SQLAlchemy？

### 1. **成熟稳定**
- 经过多年发展，功能完善
- 社区活跃，文档齐全
- 生产环境广泛使用

### 2. **功能强大**
- 完整的ORM功能
- 强大的查询构建器
- 自动迁移支持
- 关系管理

### 3. **性能优秀**
- 连接池管理
- 查询优化
- 懒加载支持

## 📋 实体模型设计原则

### 1. **专注数据定义**
- 定义字段类型、长度、约束
- 设置字段注释和默认值
- 配置索引和关系

### 2. **清晰的字段注释**
- 每个字段都有明确的注释
- 说明字段的用途和约束
- 便于数据库文档生成

### 3. **合理的约束设置**
- 主键、外键、唯一约束
- 非空约束和默认值
- 检查约束和索引

## 🚀 最佳实践

### 1. **字段定义**

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, Index
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    
    # 主键字段
    id = Column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="用户ID，主键"
    )
    
    # 字符串字段
    username = Column(
        String(20), 
        nullable=False, 
        unique=True,
        comment="用户登录名，唯一"
    )
    
    email = Column(
        String(255), 
        nullable=False, 
        unique=True,
        comment="用户邮箱地址，唯一"
    )
    
    # 时间字段
    created_at = Column(
        DateTime, 
        nullable=False, 
        default=func.now(),
        comment="创建时间"
    )
    
    updated_at = Column(
        DateTime, 
        nullable=False, 
        default=func.now(), 
        onupdate=func.now(),
        comment="更新时间"
    )
    
    # JSON字段
    permissions = Column(
        JSON, 
        nullable=True,
        comment="用户权限列表，JSON格式"
    )
```

### 2. **约束和索引**

```python
# 唯一约束
username = Column(String(20), nullable=False, unique=True)

# 非空约束
email = Column(String(255), nullable=False)

# 默认值
status = Column(String(20), nullable=False, default="pending")

# 索引
__table_args__ = (
    Index('idx_users_email', 'email'),
    Index('idx_users_username', 'username'),
    Index('idx_users_status', 'status'),
)
```

### 3. **关系定义**

```python
from sqlalchemy.orm import relationship

class User(Base):
    # 一对多关系
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    
    # 一对一关系
    profile = relationship("UserProfile", back_populates="user", uselist=False)

class Post(Base):
    # 多对一关系
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="posts")
```

### 4. **字段类型选择**

```python
# 字符串类型
username = Column(String(20))        # 短字符串
email = Column(String(255))         # 邮箱地址
description = Column(Text)           # 长文本

# 数值类型
age = Column(Integer)               # 整数
price = Column(Numeric(10, 2))      # 小数

# 布尔类型
is_active = Column(Boolean, default=True)

# 时间类型
created_at = Column(DateTime, default=func.now())
updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# JSON类型
metadata = Column(JSON)             # JSON数据
settings = Column(JSON)             # 设置信息
```

## 🔧 高级功能

### 1. **自动时间戳**

```python
class TimestampMixin:
    """时间戳混入"""
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

class User(Base, TimestampMixin):
    __tablename__ = "users"
    # 自动包含 created_at 和 updated_at 字段
```

### 2. **软删除**

```python
class SoftDeleteMixin:
    """软删除混入"""
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

class User(Base, SoftDeleteMixin):
    __tablename__ = "users"
    # 自动包含软删除字段
```

### 3. **审计日志**

```python
class AuditMixin:
    """审计混入"""
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))
    
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
```

### 4. **多租户支持**

```python
class TenantMixin:
    """多租户混入"""
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    tenant = relationship("Tenant")

class User(Base, TenantMixin):
    __tablename__ = "users"
    # 自动包含租户字段
```

## 📊 性能优化

### 1. **索引优化**

```python
# 单列索引
__table_args__ = (
    Index('idx_users_email', 'email'),
    Index('idx_users_created_at', 'created_at'),
)

# 复合索引
__table_args__ = (
    Index('idx_users_status_created', 'status', 'created_at'),
    Index('idx_users_tenant_status', 'tenant_id', 'status'),
)
```

### 2. **查询优化**

```python
# 使用select_related减少查询次数
users = session.query(User).options(joinedload(User.profile)).all()

# 使用only选择特定字段
users = session.query(User).options(load_only(User.id, User.username)).all()
```

### 3. **连接池配置**

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

## 🎨 使用示例

### 1. **创建模型**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 创建引擎
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()
```

### 2. **数据操作**

```python
# 创建用户
user = User(
    username="john_doe",
    email="john@example.com",
    first_name="John",
    last_name="Doe"
)
session.add(user)
session.commit()

# 查询用户
user = session.query(User).filter(User.email == "john@example.com").first()

# 更新用户
user.last_login_at = datetime.now()
session.commit()

# 删除用户
session.delete(user)
session.commit()
```

### 3. **关系查询**

```python
# 获取用户的所有文章
posts = user.posts

# 获取文章的作者
author = post.user

# 预加载关系
users = session.query(User).options(joinedload(User.posts)).all()
```

## 🔍 调试和监控

### 1. **SQL查询日志**

```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 2. **性能监控**

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.1:  # 记录慢查询
        print(f"Slow query: {statement} took {total:.2f}s")
```

## 🚀 迁移管理

### 1. **使用Alembic**

```bash
# 初始化迁移
alembic init migrations

# 生成迁移文件
alembic revision --autogenerate -m "Add user table"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 2. **迁移文件示例**

```python
def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

def downgrade():
    op.drop_table('users')
```

---

**基于SQLAlchemy的实体模型设计** - 利用成熟框架的强大功能，专注于数据定义！