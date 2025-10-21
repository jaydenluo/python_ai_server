# ORM关系映射指南

## 🎯 使用SQLAlchemy原生关系映射

SQLAlchemy已经提供了非常完善的关系映射功能，我们不需要重新实现。以下是使用指南：

## 📋 目录

- [一对一关系](#一对一关系)
- [一对多关系](#一对多关系)
- [多对多关系](#多对多关系)
- [关系配置选项](#关系配置选项)
- [最佳实践](#最佳实践)

## 🔗 一对一关系

### 基本语法

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    
    # 一对一关系
    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserProfile(BaseModel):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    bio = Column(String(500))
    
    # 反向关系
    user = relationship("User", back_populates="profile")
```

### 使用示例

```python
# 创建用户和档案
user = User(username="john", email="john@example.com")
profile = UserProfile(first_name="John", last_name="Doe", bio="Software Developer")
user.profile = profile

# 查询
user = session.query(User).filter(User.username == "john").first()
print(user.profile.first_name)  # John

profile = session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
print(profile.user.username)  # john
```

## 🔗 一对多关系

### 基本语法

```python
class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    
    # 一对多关系
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

class Post(BaseModel):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(String(5000))
    author_id = Column(Integer, ForeignKey("users.id"))
    
    # 反向关系
    author = relationship("User", back_populates="posts")
```

### 使用示例

```python
# 创建用户和文章
user = User(username="john")
post1 = Post(title="First Post", content="Hello World")
post2 = Post(title="Second Post", content="Another post")

user.posts.append(post1)
user.posts.append(post2)

# 查询
user = session.query(User).filter(User.username == "john").first()
print(f"User {user.username} has {len(user.posts)} posts")

for post in user.posts:
    print(f"- {post.title}")

# 反向查询
post = session.query(Post).filter(Post.title == "First Post").first()
print(f"Post '{post.title}' by {post.author.username}")
```

## 🔗 多对多关系

### 基本语法

```python
from sqlalchemy import Table

# 中间表
post_tags = Table(
    'post_tags',
    BaseModel.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Post(BaseModel):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(String(5000))
    
    # 多对多关系
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")

class Tag(BaseModel):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    
    # 反向关系
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
```

### 使用示例

```python
# 创建文章和标签
post = Post(title="Python Tutorial", content="Learn Python programming")
tag1 = Tag(name="python")
tag2 = Tag(name="tutorial")

# 建立关系
post.tags.append(tag1)
post.tags.append(tag2)

# 查询
post = session.query(Post).filter(Post.title == "Python Tutorial").first()
print(f"Post '{post.title}' has tags: {[tag.name for tag in post.tags]}")

tag = session.query(Tag).filter(Tag.name == "python").first()
print(f"Tag '{tag.name}' has posts: {[post.title for post in tag.posts]}")
```

## ⚙️ 关系配置选项

### 级联操作

```python
# 级联删除
posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

# 级联保存
posts = relationship("Post", back_populates="author", cascade="save-update, merge")

# 级联刷新
posts = relationship("Post", back_populates="author", cascade="refresh")
```

### 延迟加载选项

```python
# 立即加载
posts = relationship("Post", back_populates="author", lazy="joined")

# 子查询加载
posts = relationship("Post", back_populates="author", lazy="subquery")

# 动态加载
posts = relationship("Post", back_populates="author", lazy="dynamic")

# 选择加载（默认）
posts = relationship("Post", back_populates="author", lazy="select")
```

### 外键约束

```python
from sqlalchemy import ForeignKey

class Post(BaseModel):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
```

## 🎯 最佳实践

### 1. 使用back_populates而不是backref

```python
# ✅ 推荐：使用back_populates
class User(BaseModel):
    posts = relationship("Post", back_populates="author")

class Post(BaseModel):
    author = relationship("User", back_populates="posts")

# ❌ 不推荐：使用backref
class User(BaseModel):
    posts = relationship("Post", backref="author")
```

### 2. 合理使用级联操作

```python
# 用户删除时，删除所有相关文章
posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

# 用户删除时，保留文章但清空作者
posts = relationship("Post", back_populates="author", cascade="save-update, merge")
```

### 3. 使用适当的延迟加载

```python
# 经常需要访问的关系使用joined
profile = relationship("UserProfile", back_populates="user", lazy="joined")

# 大量数据的关系使用dynamic
posts = relationship("Post", back_populates="author", lazy="dynamic")
```

### 4. 关系查询优化

```python
# 使用joinedload预加载关系
from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.posts)).all()

# 使用selectinload子查询加载
from sqlalchemy.orm import selectinload

users = session.query(User).options(selectinload(User.posts)).all()
```

### 5. 关系验证

```python
class Post(BaseModel):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    author = relationship("User", back_populates="posts")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.author_id and not self.author:
            raise ValueError("Post must have an author")
```

## 📝 总结

SQLAlchemy的关系映射功能已经非常完善，包括：

- ✅ **一对一关系** - `relationship(uselist=False)`
- ✅ **一对多关系** - `relationship(uselist=True)`
- ✅ **多对多关系** - `relationship(secondary=table)`
- ✅ **级联操作** - `cascade`参数
- ✅ **延迟加载** - `lazy`参数
- ✅ **外键约束** - `ForeignKey`约束
- ✅ **关系查询** - `joinedload`, `selectinload`等

我们不需要重新实现这些功能，直接使用SQLAlchemy的原生功能即可！