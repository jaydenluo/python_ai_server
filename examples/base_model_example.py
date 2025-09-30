"""
基础模型使用示例
展示如何使用BaseModel基类
"""

from app.core.models.base import BaseModel, SoftDeleteModel, AuditModel
from app.models.entities.user import User
from app.models.enums.user_status import UserStatus


def demo_base_model():
    """演示基础模型功能"""
    print("🚀 基础模型功能演示")
    print("=" * 50)
    
    # 1. 创建用户实例
    print("\n1. 创建用户实例")
    user = User(
        username="john_doe",
        email="john@example.com",
        password="hashed_password",
        first_name="John",
        last_name="Doe",
        phone="1234567890",
        status=UserStatus.ACTIVE.value
    )
    
    print(f"用户: {user}")
    print(f"全名: {user.full_name}")
    print(f"是否激活: {user.is_active}")
    print(f"是否已验证: {user.is_verified}")
    
    # 2. 序列化功能
    print("\n2. 序列化功能")
    
    # 基础序列化
    user_dict = user.to_dict()
    print(f"基础序列化: {user_dict}")
    
    # 公开序列化（隐藏敏感信息）
    public_dict = user.to_public_dict()
    print(f"公开序列化: {public_dict}")
    
    # 管理员序列化（包含所有信息）
    admin_dict = user.to_admin_dict()
    print(f"管理员序列化: {admin_dict}")
    
    # JSON序列化
    user_json = user.to_json()
    print(f"JSON序列化: {user_json}")
    
    # 3. 从字典创建
    print("\n3. 从字典创建")
    user_data = {
        "username": "jane_doe",
        "email": "jane@example.com",
        "password": "hashed_password",
        "first_name": "Jane",
        "last_name": "Doe",
        "status": "active"
    }
    
    new_user = User.from_dict(user_data)
    print(f"从字典创建: {new_user}")
    
    # 4. 从JSON创建
    print("\n4. 从JSON创建")
    json_data = '{"username": "bob_smith", "email": "bob@example.com", "first_name": "Bob", "last_name": "Smith"}'
    json_user = User.from_json(json_data)
    print(f"从JSON创建: {json_user}")


def demo_soft_delete():
    """演示软删除功能"""
    print("\n🔒 软删除功能演示")
    print("=" * 50)
    
    # 创建软删除模型实例
    class SoftDeleteUser(SoftDeleteModel):
        __tablename__ = "soft_delete_users"
        
        username = Column(String(50), nullable=False)
        email = Column(String(255), nullable=False)
    
    user = SoftDeleteUser(
        username="soft_user",
        email="soft@example.com"
    )
    
    print(f"创建用户: {user}")
    print(f"是否已删除: {user.is_deleted}")
    
    # 软删除
    user.soft_delete()
    print(f"软删除后: {user.is_deleted}")
    print(f"删除时间: {user.deleted_at}")
    
    # 恢复
    user.restore()
    print(f"恢复后: {user.is_deleted}")


def demo_audit_model():
    """演示审计模型功能"""
    print("\n📊 审计模型功能演示")
    print("=" * 50)
    
    # 创建审计模型实例
    class AuditUser(AuditModel):
        __tablename__ = "audit_users"
        
        username = Column(String(50), nullable=False)
        email = Column(String(255), nullable=False)
    
    user = AuditUser(
        username="audit_user",
        email="audit@example.com"
    )
    
    print(f"创建用户: {user}")
    
    # 设置创建者
    user.set_created_by(1)
    print(f"创建者ID: {user.created_by}")
    
    # 设置更新者
    user.set_updated_by(2)
    print(f"更新者ID: {user.updated_by}")
    
    # 序列化包含审计信息
    audit_dict = user.to_dict()
    print(f"审计信息: {audit_dict}")


def demo_model_operations():
    """演示模型操作功能"""
    print("\n🔧 模型操作功能演示")
    print("=" * 50)
    
    # 模拟数据库会话
    class MockSession:
        def __init__(self):
            self.objects = []
            self.next_id = 1
        
        def add(self, obj):
            obj.id = self.next_id
            self.next_id += 1
            self.objects.append(obj)
        
        def commit(self):
            pass
        
        def query(self, model_class):
            return MockQuery(model_class, self.objects)
        
        def delete(self, obj):
            self.objects.remove(obj)
        
        def refresh(self, obj):
            pass
    
    class MockQuery:
        def __init__(self, model_class, objects):
            self.model_class = model_class
            self.objects = objects
        
        def filter(self, condition):
            return self
        
        def first(self):
            return self.objects[0] if self.objects else None
        
        def all(self):
            return self.objects
        
        def count(self):
            return len(self.objects)
    
    # 创建模拟会话
    session = MockSession()
    
    # 创建用户
    user = User.create(session, 
        username="test_user",
        email="test@example.com",
        password="password",
        first_name="Test",
        last_name="User"
    )
    print(f"创建用户: {user}")
    
    # 根据ID获取
    found_user = User.get_by_id(session, user.id)
    print(f"根据ID获取: {found_user}")
    
    # 获取所有用户
    all_users = User.get_all(session)
    print(f"所有用户: {all_users}")
    
    # 统计用户数量
    user_count = User.count(session)
    print(f"用户数量: {user_count}")
    
    # 更新用户
    updated_user = User.update_by_id(session, user.id, 
        first_name="Updated", 
        last_name="Name"
    )
    print(f"更新用户: {updated_user}")
    
    # 删除用户
    deleted = User.delete_by_id(session, user.id)
    print(f"删除用户: {deleted}")


if __name__ == "__main__":
    print("🎯 基础模型完整演示")
    print("=" * 60)
    
    # 运行演示
    demo_base_model()
    demo_soft_delete()
    demo_audit_model()
    demo_model_operations()
    
    print("\n🎉 演示完成！")
    print("\n💡 使用提示:")
    print("1. 所有实体模型都继承自BaseModel")
    print("2. 自动获得序列化功能：to_dict(), to_json(), to_public_dict()")
    print("3. 自动获得CRUD操作：create(), get_by_id(), update_by_id(), delete_by_id()")
    print("4. 支持软删除：SoftDeleteModel")
    print("5. 支持审计：AuditModel")
    print("6. 支持多租户：TenantModel")