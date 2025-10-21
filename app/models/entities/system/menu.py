"""
菜单权限相关实体模型
基于Django-Vue3-Admin的菜单权限功能
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.models.base import AuditModel, BaseModel


class Menu(AuditModel):
    """菜单表"""
    __tablename__ = 'menus'
    
    parent_id = Column(BigInteger, ForeignKey('menus.id', ondelete='CASCADE'), nullable=True, comment="父菜单ID")
    icon = Column(String(64), nullable=True, comment="图标")
    name = Column(String(64), nullable=False, comment="菜单名称")
    sort = Column(Integer, default=1, comment="排序")
    is_link = Column(Boolean, default=False, comment="是否外链")
    link_url = Column(String(255), nullable=True, comment="外链地址")
    is_catalog = Column(Boolean, default=False, comment="是否目录")
    web_path = Column(String(128), nullable=True, comment="前端路径")
    component = Column(String(128), nullable=True, comment="组件路径")
    component_name = Column(String(50), nullable=True, comment="组件名称")
    status = Column(Boolean, default=True, comment="状态")
    cache = Column(Boolean, default=False, comment="是否缓存")
    visible = Column(Boolean, default=True, comment="是否显示")
    is_iframe = Column(Boolean, default=False, comment="是否内嵌")
    is_affix = Column(Boolean, default=False, comment="是否固定")
    
    # 关系
    parent = relationship("Menu", remote_side=[id], back_populates="children")
    children = relationship("Menu", back_populates="parent")
    buttons = relationship("MenuButton", back_populates="menu")
    fields = relationship("MenuField", back_populates="menu")
    roles = relationship("Role", secondary="role_menu_permission", back_populates="menus")


class MenuButton(AuditModel):
    """菜单按钮权限表"""
    __tablename__ = 'menu_buttons'
    
    menu_id = Column(BigInteger, ForeignKey('menus.id', ondelete='CASCADE'), nullable=False, comment="菜单ID")
    name = Column(String(64), nullable=False, comment="按钮名称")
    value = Column(String(64), unique=True, nullable=False, comment="权限值")
    api = Column(String(200), nullable=False, comment="API地址")
    method = Column(Integer, default=0, comment="请求方法: 0-GET 1-POST 2-PUT 3-DELETE")
    
    # 关系
    menu = relationship("Menu", back_populates="buttons")
    roles = relationship("Role", secondary="role_menu_button_permission", back_populates="buttons")


class MenuField(AuditModel):
    """菜单字段表"""
    __tablename__ = 'menu_fields'
    
    model = Column(String(64), nullable=False, comment="模型名称")
    menu_id = Column(BigInteger, ForeignKey('menus.id', ondelete='CASCADE'), nullable=False, comment="菜单ID")
    field_name = Column(String(64), nullable=False, comment="字段名")
    title = Column(String(64), nullable=False, comment="字段标题")
    
    # 关系
    menu = relationship("Menu", back_populates="fields")
    permissions = relationship("FieldPermission", back_populates="field")


class FieldPermission(AuditModel):
    """字段权限表"""
    __tablename__ = 'field_permissions'
    
    role_id = Column(BigInteger, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, comment="角色ID")
    field_id = Column(BigInteger, ForeignKey('menu_fields.id', ondelete='CASCADE'), nullable=False, comment="字段ID")
    is_query = Column(Boolean, default=True, comment="是否可查询")
    is_create = Column(Boolean, default=True, comment="是否可创建")
    is_update = Column(Boolean, default=True, comment="是否可更新")
    
    # 关系
    role = relationship("Role")
    field = relationship("MenuField", back_populates="permissions")


# 角色菜单权限关联表
role_menu_permission = Table(
    'role_menu_permission',
    BaseModel.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('role_id', BigInteger, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
    Column('menu_id', BigInteger, ForeignKey('menus.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('updated_at', DateTime, nullable=True),
    Column('created_by', BigInteger, nullable=True),
    Column('updated_by', BigInteger, nullable=True),
    Column('description', String(255), nullable=True)
)

# 角色按钮权限关联表
role_menu_button_permission = Table(
    'role_menu_button_permission',
    BaseModel.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('role_id', BigInteger, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
    Column('menu_button_id', BigInteger, ForeignKey('menu_buttons.id', ondelete='CASCADE'), nullable=True),
    Column('data_range', Integer, default=0, comment="数据权限范围: 0-仅本人 1-本部门及以下 2-本部门 3-全部 4-自定"),
    Column('created_at', DateTime, nullable=False),
    Column('updated_at', DateTime, nullable=True),
    Column('created_by', BigInteger, nullable=True),
    Column('updated_by', BigInteger, nullable=True),
    Column('description', String(255), nullable=True)
)

# 角色按钮权限部门关联表
role_menu_button_permission_dept = Table(
    'role_menu_button_permission_dept',
    BaseModel.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('rolemenubuttonpermission_id', BigInteger, ForeignKey('role_menu_button_permission.id', ondelete='CASCADE'), nullable=False),
    Column('dept_id', BigInteger, ForeignKey('depts.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('updated_at', DateTime, nullable=True),
    Column('created_by', BigInteger, nullable=True),
    Column('updated_by', BigInteger, nullable=True),
    Column('description', String(255), nullable=True)
)