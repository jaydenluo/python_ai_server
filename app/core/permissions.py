"""
权限控制模块
实现RBAC权限控制
"""
from functools import wraps
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities.system.user_management import User as Users, Role
from app.models.entities.system.menu import Menu, MenuButton


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_user_permission(self, user_id: int, permission: str) -> bool:
        """
        检查用户权限
        
        Args:
            user_id: 用户ID
            permission: 权限标识
            
        Returns:
            是否有权限
        """
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return False
        
        # 超级用户拥有所有权限
        if user.is_superuser:
            return True
        
        # 检查用户角色权限
        for role in user.roles:
            if self._check_role_permission(role.id, permission):
                return True
        
        return False
    
    def _check_role_permission(self, role_id: int, permission: str) -> bool:
        """检查角色权限"""
        # 检查菜单权限
        menu_permission = self.db.query(Menu).join(
            Menu.roles
        ).filter(
            Role.id == role_id,
            Menu.web_path == permission
        ).first()
        
        if menu_permission:
            return True
        
        # 检查按钮权限
        button_permission = self.db.query(MenuButton).join(
            MenuButton.roles
        ).filter(
            Role.id == role_id,
            MenuButton.value == permission
        ).first()
        
        return button_permission is not None
    
    def get_user_menus(self, user_id: int) -> List[dict]:
        """获取用户菜单权限"""
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return []
        
        # 超级用户获取所有菜单
        if user.is_superuser:
            menus = self.db.query(Menu).filter(Menu.status == True).all()
        else:
            # 根据角色获取菜单
            menus = self.db.query(Menu).join(
                Menu.roles
            ).filter(
                Role.id.in_([role.id for role in user.roles]),
                Menu.status == True
            ).distinct().all()
        
        return [self._format_menu(menu) for menu in menus]
    
    def get_user_buttons(self, user_id: int) -> List[str]:
        """获取用户按钮权限"""
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return []
        
        # 超级用户拥有所有按钮权限
        if user.is_superuser:
            buttons = self.db.query(MenuButton).all()
        else:
            # 根据角色获取按钮权限
            buttons = self.db.query(MenuButton).join(
                MenuButton.roles
            ).filter(
                Role.id.in_([role.id for role in user.roles])
            ).distinct().all()
        
        return [button.value for button in buttons]
    
    def _format_menu(self, menu: Menu) -> dict:
        """格式化菜单数据"""
        return {
            'id': menu.id,
            'parent_id': menu.parent_id,
            'name': menu.name,
            'icon': menu.icon,
            'web_path': menu.web_path,
            'component': menu.component,
            'component_name': menu.component_name,
            'sort': menu.sort,
            'is_link': menu.is_link,
            'link_url': menu.link_url,
            'is_catalog': menu.is_catalog,
            'cache': menu.cache,
            'visible': menu.visible,
            'is_iframe': menu.is_iframe,
            'is_affix': menu.is_affix
        }


def require_permission(permission: str):
    """
    权限装饰器
    
    Args:
        permission: 需要的权限标识
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 这里需要从请求中获取用户信息
            # 实际实现中需要根据具体的认证方式调整
            user_id = kwargs.get('user_id')  # 从JWT或其他方式获取
            
            if not user_id:
                return {'code': 4001, 'msg': '未登录'}
            
            db = next(get_db())
            checker = PermissionChecker(db)
            
            if not checker.check_user_permission(user_id, permission):
                return {'code': 4003, 'msg': '权限不足'}
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_data_permission(user_id: int, data_range: int, dept_id: Optional[int] = None) -> bool:
    """
    检查数据权限
    
    Args:
        user_id: 用户ID
        data_range: 数据权限范围
        dept_id: 数据所属部门ID
        
    Returns:
        是否有权限访问
    """
    db = next(get_db())
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return False
    
    # 超级用户拥有所有数据权限
    if user.is_superuser:
        return True
    
    # 根据数据权限范围判断
    if data_range == 0:  # 仅本人数据权限
        return True  # 由业务逻辑控制
    elif data_range == 1:  # 本部门及以下数据权限
        return user.dept_id == dept_id or _is_sub_dept(user.dept_id, dept_id, db)
    elif data_range == 2:  # 本部门数据权限
        return user.dept_id == dept_id
    elif data_range == 3:  # 全部数据权限
        return True
    elif data_range == 4:  # 自定数据权限
        # 需要检查用户的管理部门
        return _check_custom_data_permission(user_id, dept_id, db)
    
    return False


def _is_sub_dept(user_dept_id: int, data_dept_id: int, db: Session) -> bool:
    """检查是否为子部门"""
    # 递归检查部门层级关系
    # 这里需要根据实际的部门表结构实现
    pass


def _check_custom_data_permission(user_id: int, dept_id: int, db: Session) -> bool:
    """检查自定数据权限"""
    # 检查用户是否管理该部门
    # 这里需要根据实际的管理部门关联表实现
    pass