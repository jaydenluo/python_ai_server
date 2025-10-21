# Service层架构设计

## 🎯 架构原则

### 1. **分层架构**
- **模型层 (Model)** - 数据定义和序列化
- **仓储层 (Repository)** - 数据访问
- **服务层 (Service)** - 业务逻辑
- **控制器层 (Controller)** - 请求处理

### 2. **职责分离**
- 每层都有明确的职责
- 避免跨层调用
- 保持低耦合高内聚

## 📋 各层职责

### 1. **模型层 (Model)**
```python
class User(BaseModel):
    """用户模型 - 只负责数据定义"""
    
    __tablename__ = "users"
    
    username = Column(String(20), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    
    # 只包含数据定义和序列化方法
    # 不包含CRUD操作
```

**职责：**
- 定义数据结构和字段
- 提供序列化方法
- 定义数据验证规则
- 不包含业务逻辑

### 2. **仓储层 (Repository)**
```python
class BaseRepository:
    """基础仓储类 - 提供通用数据访问"""
    
    def create(self, **kwargs) -> T:
        """创建记录"""
        pass
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """根据ID获取记录"""
        pass
    
    def update(self, id: Any, **kwargs) -> Optional[T]:
        """更新记录"""
        pass
    
    def delete(self, id: Any) -> bool:
        """删除记录"""
        pass
```

**职责：**
- 提供通用的CRUD操作
- 处理数据库查询
- 管理数据库事务
- 不包含业务逻辑

### 3. **服务层 (Service)**
```python
class UserService(BaseService):
    """用户服务类 - 处理用户相关业务逻辑"""
    
    def create_user(self, username: str, email: str, password: str) -> User:
        """创建用户（带业务逻辑）"""
        # 检查用户名是否已存在
        if self.repository.get_by_field("username", username):
            raise ValueError("用户名已存在")
        
        # 密码加密
        hashed_password = self._hash_password(password)
        
        return self.repository.create(
            username=username,
            email=email,
            password=hashed_password
        )
```

**职责：**
- 处理业务逻辑
- 数据验证和转换
- 调用Repository进行数据操作
- 处理业务异常

### 4. **控制器层 (Controller)**
```python
class UserController:
    """用户控制器 - 处理HTTP请求"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def create_user(self, request):
        """创建用户接口"""
        try:
            user = self.user_service.create_user(
                username=request.json['username'],
                email=request.json['email'],
                password=request.json['password']
            )
            return user.to_dict()
        except ValueError as e:
            return {"error": str(e)}, 400
```

**职责：**
- 处理HTTP请求和响应
- 参数验证和转换
- 调用Service处理业务逻辑
- 返回JSON响应

## 🚀 使用方式

### 1. **基础使用**

```python
# 创建Repository
user_repository = BaseRepository(User, session)

# 创建Service
user_service = UserService(user_repository)

# 使用Service进行业务操作
user = user_service.create_user(
    username="john_doe",
    email="john@example.com",
    password="password123"
)
```

### 2. **高级使用**

```python
# 复杂业务逻辑
class UserService(BaseService):
    def create_user_with_profile(self, user_data: dict, profile_data: dict) -> User:
        """创建用户并设置档案"""
        # 创建用户
        user = self.create_user(**user_data)
        
        # 设置档案
        user.profile_data = profile_data
        self.repository.update(user.id, profile_data=profile_data)
        
        # 发送欢迎邮件
        self._send_welcome_email(user.email)
        
        return user
    
    def _send_welcome_email(self, email: str):
        """发送欢迎邮件"""
        # 邮件发送逻辑
        pass
```

### 3. **错误处理**

```python
class UserService(BaseService):
    def create_user(self, username: str, email: str, password: str) -> User:
        try:
            # 业务逻辑验证
            if not self._validate_username(username):
                raise ValueError("用户名格式不正确")
            
            if not self._validate_email(email):
                raise ValueError("邮箱格式不正确")
            
            # 创建用户
            return self.repository.create(
                username=username,
                email=email,
                password=self._hash_password(password)
            )
        except SQLAlchemyError as e:
            # 数据库错误处理
            raise DatabaseError("数据库操作失败")
        except Exception as e:
            # 其他错误处理
            raise BusinessError(f"创建用户失败: {str(e)}")
```

## 🔧 最佳实践

### 1. **依赖注入**

```python
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def create_user(self, request):
        return self.user_service.create_user(**request.json)
```

### 2. **事务管理**

```python
class UserService(BaseService):
    def create_user_with_roles(self, user_data: dict, roles: list) -> User:
        """创建用户并分配角色"""
        try:
            # 开始事务
            with self.repository.session.begin():
                # 创建用户
                user = self.repository.create(**user_data)
                
                # 分配角色
                for role in roles:
                    self._assign_role(user.id, role)
                
                return user
        except Exception as e:
            # 事务回滚
            self.repository.session.rollback()
            raise e
```

### 3. **缓存处理**

```python
class UserService(BaseService):
    def __init__(self, repository: BaseRepository, cache_service: CacheService):
        super().__init__(repository)
        self.cache_service = cache_service
    
    def get_by_id(self, id: Any) -> Optional[User]:
        """获取用户（带缓存）"""
        cache_key = f"user:{id}"
        
        # 尝试从缓存获取
        cached_user = self.cache_service.get(cache_key)
        if cached_user:
            return User.from_dict(cached_user)
        
        # 从数据库获取
        user = self.repository.get_by_id(id)
        if user:
            # 存入缓存
            self.cache_service.set(cache_key, user.to_dict(), ttl=3600)
        
        return user
```

### 4. **日志记录**

```python
import logging

class UserService(BaseService):
    def __init__(self, repository: BaseRepository):
        super().__init__(repository)
        self.logger = logging.getLogger(__name__)
    
    def create_user(self, username: str, email: str, password: str) -> User:
        """创建用户（带日志）"""
        self.logger.info(f"开始创建用户: {username}")
        
        try:
            user = self.repository.create(
                username=username,
                email=email,
                password=self._hash_password(password)
            )
            
            self.logger.info(f"用户创建成功: {user.id}")
            return user
        except Exception as e:
            self.logger.error(f"用户创建失败: {str(e)}")
            raise e
```

## 📊 性能优化

### 1. **查询优化**

```python
class UserService(BaseService):
    def get_users_with_posts(self, limit: int = 10) -> List[User]:
        """获取用户及其文章（优化查询）"""
        # 使用JOIN查询减少数据库访问
        return self.repository.session.query(User).join(Post).limit(limit).all()
    
    def get_active_users_count(self) -> int:
        """获取活跃用户数量（使用COUNT查询）"""
        return self.repository.session.query(User).filter(
            User.status == "active"
        ).count()
```

### 2. **批量操作**

```python
class UserService(BaseService):
    def bulk_create_users(self, users_data: List[dict]) -> List[User]:
        """批量创建用户"""
        return self.repository.bulk_create(users_data)
    
    def bulk_update_status(self, user_ids: List[int], status: str) -> int:
        """批量更新用户状态"""
        updates = [{"id": user_id, "status": status} for user_id in user_ids]
        return self.repository.bulk_update(updates)
```

## 🎉 总结

### 优势
1. **职责分离** - 每层都有明确的职责
2. **易于测试** - 可以单独测试每一层
3. **易于维护** - 修改业务逻辑不影响数据访问
4. **可扩展性** - 容易添加新功能
5. **代码复用** - Repository提供通用CRUD操作

### 使用建议
1. **模型层** - 只定义数据结构和序列化
2. **Repository层** - 提供通用数据访问
3. **Service层** - 处理业务逻辑
4. **Controller层** - 处理HTTP请求

这样的架构设计既保持了代码的清晰性，又提供了良好的可维护性和可扩展性。