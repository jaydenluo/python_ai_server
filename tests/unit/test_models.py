"""
模型单元测试
"""
import pytest
from app.models.entities.system.user_management import User, Role, Dept


class TestUserModel:
    """用户模型测试"""
    
    def test_user_password_hashing(self):
        """测试密码加密"""
        user = User()
        user.set_password("test123456")
        
        assert user.password != "test123456"  # 密码应该被加密
        assert user.check_password("test123456")  # 能够验证正确密码
        assert not user.check_password("wrong_password")  # 错误密码验证失败


class TestRoleModel:
    """角色模型测试"""
    
    def test_role_creation(self):
        """测试角色创建"""
        role = Role()
        role.name = "管理员"
        role.key = "admin"
        
        assert role.name == "管理员"
        assert role.key == "admin"

