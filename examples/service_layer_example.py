"""
Service层使用示例
展示如何使用Repository和Service层
"""

from app.core.repositories.base_repository import BaseRepository
from app.services.base_service import BaseService, UserService
from app.models.entities.user import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


def demo_service_layer():
    """演示Service层使用"""
    print("🚀 Service层使用演示")
    print("=" * 50)
    
    # 1. 创建数据库连接（模拟）
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 2. 创建Repository
    user_repository = BaseRepository(User, session)
    
    # 3. 创建Service
    user_service = UserService(user_repository)
    
    # 4. 使用Service进行CRUD操作
    print("\n1. 创建用户")
    try:
        user = user_service.create_user(
            username="john_doe",
            email="john@example.com",
            password="password123",
            first_name="John",
            last_name="Doe"
        )
        print(f"创建用户成功: {user}")
    except ValueError as e:
        print(f"创建用户失败: {e}")
    
    # 5. 获取用户
    print("\n2. 获取用户")
    user = user_service.get_by_id(1)
    if user:
        print(f"获取用户: {user}")
        print(f"用户信息: {user.to_dict()}")
    
    # 6. 用户认证
    print("\n3. 用户认证")
    authenticated_user = user_service.authenticate("john@example.com", "password123")
    if authenticated_user:
        print(f"认证成功: {authenticated_user.username}")
    else:
        print("认证失败")
    
    # 7. 更新用户
    print("\n4. 更新用户")
    updated_user = user_service.update(1, first_name="Updated John")
    if updated_user:
        print(f"更新用户: {updated_user.first_name}")
    
    # 8. 获取所有用户
    print("\n5. 获取所有用户")
    all_users = user_service.get_all()
    print(f"所有用户: {len(all_users)}")
    
    # 9. 分页查询
    print("\n6. 分页查询")
    page_result = user_service.paginate(page=1, per_page=10)
    print(f"分页结果: {page_result}")
    
    # 10. 删除用户
    print("\n7. 删除用户")
    deleted = user_service.delete(1)
    print(f"删除用户: {deleted}")


def demo_repository_direct():
    """演示直接使用Repository"""
    print("\n🔧 Repository直接使用演示")
    print("=" * 50)
    
    # 创建Repository
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    user_repository = BaseRepository(User, session)
    
    # 直接使用Repository
    print("\n1. 创建用户")
    user = user_repository.create(
        username="jane_doe",
        email="jane@example.com",
        password="hashed_password",
        first_name="Jane",
        last_name="Doe"
    )
    print(f"创建用户: {user}")
    
    print("\n2. 根据字段查询")
    found_user = user_repository.get_by_field("username", "jane_doe")
    print(f"根据用户名查询: {found_user}")
    
    print("\n3. 模糊搜索")
    search_results = user_repository.search("first_name", "Jane")
    print(f"搜索结果: {search_results}")
    
    print("\n4. 过滤查询")
    filtered_users = user_repository.filter(status="active")
    print(f"过滤结果: {filtered_users}")
    
    print("\n5. 排序查询")
    ordered_users = user_repository.order_by("created_at", "desc")
    print(f"排序结果: {ordered_users}")


def demo_business_logic():
    """演示业务逻辑处理"""
    print("\n💼 业务逻辑处理演示")
    print("=" * 50)
    
    # 创建Service
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    user_repository = BaseRepository(User, session)
    user_service = UserService(user_repository)
    
    # 创建用户
    user = user_service.create_user(
        username="business_user",
        email="business@example.com",
        password="password123",
        first_name="Business",
        last_name="User"
    )
    print(f"创建用户: {user.username}")
    
    # 业务逻辑：激活用户
    print("\n1. 激活用户")
    activated_user = user_service.activate_user(user.id)
    if activated_user:
        print(f"用户状态: {activated_user.status}")
    
    # 业务逻辑：获取活跃用户
    print("\n2. 获取活跃用户")
    active_users = user_service.get_active_users()
    print(f"活跃用户数量: {len(active_users)}")
    
    # 业务逻辑：用户认证
    print("\n3. 用户认证")
    auth_user = user_service.authenticate("business@example.com", "password123")
    if auth_user:
        print(f"认证成功: {auth_user.username}")
    
    # 业务逻辑：停用用户
    print("\n4. 停用用户")
    deactivated_user = user_service.deactivate_user(user.id)
    if deactivated_user:
        print(f"用户状态: {deactivated_user.status}")


def demo_error_handling():
    """演示错误处理"""
    print("\n❌ 错误处理演示")
    print("=" * 50)
    
    # 创建Service
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    user_repository = BaseRepository(User, session)
    user_service = UserService(user_repository)
    
    # 创建第一个用户
    user1 = user_service.create_user(
        username="test_user",
        email="test@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )
    print(f"创建第一个用户: {user1.username}")
    
    # 尝试创建重复用户名的用户
    print("\n1. 尝试创建重复用户名")
    try:
        user2 = user_service.create_user(
            username="test_user",  # 重复用户名
            email="test2@example.com",
            password="password123",
            first_name="Test2",
            last_name="User2"
        )
    except ValueError as e:
        print(f"创建失败: {e}")
    
    # 尝试创建重复邮箱的用户
    print("\n2. 尝试创建重复邮箱")
    try:
        user3 = user_service.create_user(
            username="test_user3",
            email="test@example.com",  # 重复邮箱
            password="password123",
            first_name="Test3",
            last_name="User3"
        )
    except ValueError as e:
        print(f"创建失败: {e}")
    
    # 尝试认证不存在的用户
    print("\n3. 尝试认证不存在的用户")
    auth_user = user_service.authenticate("nonexistent@example.com", "password123")
    if auth_user:
        print(f"认证成功: {auth_user.username}")
    else:
        print("认证失败: 用户不存在或密码错误")


if __name__ == "__main__":
    print("🎯 Service层完整演示")
    print("=" * 60)
    
    # 运行演示
    demo_service_layer()
    demo_repository_direct()
    demo_business_logic()
    demo_error_handling()
    
    print("\n🎉 演示完成！")
    print("\n💡 架构优势:")
    print("1. 模型层：只负责数据定义和序列化")
    print("2. Repository层：负责数据访问，提供通用CRUD操作")
    print("3. Service层：负责业务逻辑，处理复杂业务规则")
    print("4. 职责分离：每层都有明确的职责")
    print("5. 易于测试：可以单独测试每一层")
    print("6. 易于维护：修改业务逻辑不影响数据访问")