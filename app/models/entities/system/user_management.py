"""
用户管理相关实体模型
基于Django-Vue3-Admin的用户管理功能
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.models.base import AuditModel, BaseModel
from app.core.auto_schema import auto_schema


# 用户角色关联表
users_role = Table(
    'users_role',
    BaseModel.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('users_id', BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('role_id', BigInteger, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('updated_at', DateTime, nullable=True),
    Column('created_by', BigInteger, nullable=True),
    Column('updated_by', BigInteger, nullable=True),
    Column('description', String(255), nullable=True)
)

# 用户岗位关联表
users_post = Table(
    'users_post',
    BaseModel.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('users_id', BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('post_id', BigInteger, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('updated_at', DateTime, nullable=True),
    Column('created_by', BigInteger, nullable=True),
    Column('updated_by', BigInteger, nullable=True),
    Column('description', String(255), nullable=True)
)

# 用户管理部门关联表
users_manage_dept = Table(
    'users_manage_dept',
    BaseModel.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('users_id', BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('dept_id', BigInteger, ForeignKey('depts.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('updated_at', DateTime, nullable=True),
    Column('created_by', BigInteger, nullable=True),
    Column('updated_by', BigInteger, nullable=True),
    Column('description', String(255), nullable=True)
)


@auto_schema()
class User(AuditModel):
    """用户表"""
    __tablename__ = 'users'
    
    # 基础字段
    password = Column(String(128), nullable=False, comment="密码")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    is_superuser = Column(Boolean, default=False, nullable=False, comment="是否超级用户")
    username = Column(String(150), unique=True, nullable=False, comment="用户名")
    first_name = Column(String(150), default='', nullable=False, comment="名")
    last_name = Column(String(150), default='', nullable=False, comment="姓")
    email = Column(String(254), nullable=True, comment="邮箱")
    is_staff = Column(Boolean, default=False, nullable=False, comment="是否员工")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    date_joined = Column(DateTime, nullable=False, comment="加入时间")
    
    # 扩展字段
    mobile = Column(String(255), nullable=True, comment="手机号")
    avatar = Column(String(255), nullable=True, comment="头像")
    name = Column(String(40), nullable=False, comment="姓名")
    gender = Column(Integer, default=0, comment="性别: 0-未知 1-男 2-女")
    user_type = Column(Integer, default=0, comment="用户类型: 0-后台用户 1-前台用户")
    dept_id = Column(BigInteger, ForeignKey('depts.id', ondelete='PROTECT'), nullable=True, comment="部门ID")
    current_role_id = Column(BigInteger, ForeignKey('roles.id', ondelete='SET NULL'), nullable=True, comment="当前角色ID")
    login_error_count = Column(Integer, default=0, comment="登录错误次数")
    pwd_change_count = Column(Integer, default=0, comment="密码修改次数")
    
    # 关系
    dept = relationship("Dept", back_populates="users")
    current_role = relationship("Role", back_populates="users")
    roles = relationship("Role", secondary=users_role, back_populates="users")
    posts = relationship("Post", secondary=users_post, back_populates="users")
    manage_depts = relationship("Dept", secondary=users_manage_dept, back_populates="managers")
    
    def set_password(self, raw_password: str):
        """设置密码"""
        import hashlib
        if raw_password:
            # 使用MD5+Django内置hash进行双重加密
            md5_hash = hashlib.md5(raw_password.encode(encoding="UTF-8")).hexdigest()
            # 这里可以添加Django的密码哈希逻辑
            self.password = md5_hash
    
    def check_password(self, raw_password: str) -> bool:
        """验证密码"""
        import hashlib
        md5_hash = hashlib.md5(raw_password.encode(encoding="UTF-8")).hexdigest()
        return self.password == md5_hash


@auto_schema()
class Role(AuditModel):
    """角色表"""
    __tablename__ = 'roles'
    
    name = Column(String(64), nullable=False, comment="角色名称")
    key = Column(String(64), unique=True, nullable=False, comment="权限字符")
    sort = Column(Integer, default=1, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
    
    # 关系
    users = relationship("User", secondary=users_role, back_populates="roles")
    menus = relationship("Menu", secondary="role_menu_permission", back_populates="roles")
    buttons = relationship("MenuButton", secondary="role_menu_button_permission", back_populates="roles")


@auto_schema()
class Dept(AuditModel):
    """部门表"""
    __tablename__ = 'depts'
    
    name = Column(String(64), nullable=False, comment="部门名称")
    key = Column(String(64), unique=True, nullable=True, comment="部门编码")
    sort = Column(Integer, default=1, comment="排序")
    owner = Column(String(32), nullable=True, comment="负责人")
    phone = Column(String(32), nullable=True, comment="联系电话")
    email = Column(String(32), nullable=True, comment="邮箱")
    status = Column(Boolean, default=True, comment="状态")
    parent_id = Column(BigInteger, ForeignKey('depts.id', ondelete='CASCADE'), nullable=True, comment="父部门ID")
    
    # 关系
    parent = relationship("Dept", remote_side=[id], back_populates="children")
    children = relationship("Dept", back_populates="parent")
    users = relationship("User", back_populates="dept")
    managers = relationship("User", secondary=users_manage_dept, back_populates="manage_depts")


@auto_schema()
class Post(AuditModel):
    """岗位表"""
    __tablename__ = 'posts'
    
    name = Column(String(64), nullable=False, comment="岗位名称")
    code = Column(String(32), nullable=False, comment="岗位编码")
    sort = Column(Integer, default=1, comment="排序")
    status = Column(Integer, default=1, comment="状态: 0-离职 1-在职")
    
    # 关系
    users = relationship("User", secondary=users_post, back_populates="posts")
