"""
智能ORM系统使用示例
展示如何通过修改模型自动更新数据库
"""

from app.models.base import Model
from app.core.orm.decorators import (
    auto_migrate, track_changes, auto_timestamps, auto_validate,
    required, email, min_length, max_length
)
from app.core.orm.commands import ORMCommands
from typing import Optional, List
from datetime import datetime


# 示例1: 基础模型定义
@auto_migrate
@track_changes
@auto_timestamps
@auto_validate
class User(Model):
    """用户模型 - 展示智能ORM功能"""
    
    __table__ = "users"
    __fillable__ = ["username", "email", "first_name", "last_name", "phone", "age"]
    __hidden__ = ["password"]
    
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
        
        self.add_validation_rule("age", required)
    
    @property
    def full_name(self) -> str:
        """获取全名"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self):
        """保存用户"""
        if self.has_changes():
            changes = self.get_changes()
            print(f"🔍 检测到用户变更: {changes}")
        
        # 执行验证
        self._validate()
        
        # 保存逻辑
        print(f"💾 保存用户: {self.username}")
        return True


# 示例2: 模型变更演示
class UserV1(Model):
    """用户模型 V1 - 原始版本"""
    username: str
    email: str
    first_name: str
    last_name: str


class UserV2(Model):
    """用户模型 V2 - 添加新字段"""
    username: str
    email: str
    first_name: str
    last_name: str
    phone: str          # 新增字段
    age: int           # 新增字段
    status: str = "active"  # 新增字段，带默认值


class UserV3(Model):
    """用户模型 V3 - 修改字段类型"""
    username: str
    email: str
    first_name: str
    last_name: str
    phone: str
    age: int
    status: str = "active"
    is_verified: bool = False  # 新增布尔字段
    last_login: Optional[datetime] = None  # 新增可选字段


# 示例3: 关系模型
@auto_migrate
@track_changes
class Post(Model):
    """文章模型"""
    
    __table__ = "posts"
    __fillable__ = ["title", "content", "user_id", "status"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 添加验证规则
        self.add_validation_rule("title", required)
        self.add_validation_rule("title", min_length(5))
        self.add_validation_rule("title", max_length(100))
        
        self.add_validation_rule("content", required)
        self.add_validation_rule("content", min_length(10))


@auto_migrate
@track_changes
class Comment(Model):
    """评论模型"""
    
    __table__ = "comments"
    __fillable__ = ["content", "user_id", "post_id"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 添加验证规则
        self.add_validation_rule("content", required)
        self.add_validation_rule("content", min_length(1))
        self.add_validation_rule("content", max_length(500))


def demo_smart_orm():
    """演示智能ORM功能"""
    print("🚀 智能ORM系统演示")
    print("=" * 50)
    
    # 1. 创建用户实例
    print("\n1. 创建用户实例")
    user = User(
        username="john_doe",
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        phone="1234567890",
        age=25
    )
    
    print(f"用户: {user.full_name}")
    print(f"邮箱: {user.email}")
    print(f"电话: {user.phone}")
    
    # 2. 演示变更跟踪
    print("\n2. 演示变更跟踪")
    print(f"初始变更状态: {user.has_changes()}")
    
    user.phone = "0987654321"
    print(f"修改电话后变更状态: {user.has_changes()}")
    
    if user.has_changes():
        changes = user.get_changes()
        print(f"变更详情: {changes}")
    
    # 3. 演示验证
    print("\n3. 演示数据验证")
    try:
        user.save()
        print("✅ 用户保存成功")
    except ValueError as e:
        print(f"❌ 验证失败: {e}")
    
    # 4. 演示模型变更检测
    print("\n4. 演示模型变更检测")
    print("🔍 检测模型变更...")
    
    # 这里会触发自动迁移检测
    # 实际使用中，系统会自动检测模型结构变更


def demo_migration_commands():
    """演示迁移命令"""
    print("\n🔧 迁移命令演示")
    print("=" * 50)
    
    # 模拟命令行参数
    import sys
    original_argv = sys.argv
    
    try:
        # 模拟 status 命令
        print("\n📊 查看模型状态:")
        sys.argv = ["orm_commands", "status"]
        commands = ORMCommands()
        commands.status(commands._create_args(["status"]))
        
        # 模拟 analyze 命令
        print("\n🔍 分析模型结构:")
        sys.argv = ["orm_commands", "analyze"]
        commands.analyze_models(commands._create_args(["analyze"]))
        
    except Exception as e:
        print(f"⚠️  命令执行出错: {e}")
    finally:
        sys.argv = original_argv


def demo_model_evolution():
    """演示模型演进"""
    print("\n📈 模型演进演示")
    print("=" * 50)
    
    print("1. 原始模型 (UserV1)")
    print("   - username: str")
    print("   - email: str")
    print("   - first_name: str")
    print("   - last_name: str")
    
    print("\n2. 第一次演进 (UserV2)")
    print("   - 新增 phone: str")
    print("   - 新增 age: int")
    print("   - 新增 status: str = 'active'")
    print("   - 系统会自动生成迁移文件")
    
    print("\n3. 第二次演进 (UserV3)")
    print("   - 新增 is_verified: bool = False")
    print("   - 新增 last_login: Optional[datetime] = None")
    print("   - 系统会检测变更并生成新的迁移文件")
    
    print("\n🔄 自动迁移流程:")
    print("   1. 检测模型结构变更")
    print("   2. 生成迁移文件")
    print("   3. 执行数据库更新")
    print("   4. 验证数据完整性")


def demo_validation_rules():
    """演示验证规则"""
    print("\n✅ 验证规则演示")
    print("=" * 50)
    
    # 创建用户实例
    user = User()
    
    print("测试验证规则:")
    
    # 测试必填验证
    try:
        user.username = ""
        user.save()
    except ValueError as e:
        print(f"❌ 用户名不能为空: {e}")
    
    # 测试长度验证
    try:
        user.username = "ab"  # 太短
        user.save()
    except ValueError as e:
        print(f"❌ 用户名太短: {e}")
    
    # 测试邮箱验证
    try:
        user.email = "invalid-email"
        user.save()
    except ValueError as e:
        print(f"❌ 邮箱格式无效: {e}")
    
    # 测试成功案例
    try:
        user.username = "john_doe"
        user.email = "john@example.com"
        user.first_name = "John"
        user.last_name = "Doe"
        user.age = 25
        user.save()
        print("✅ 用户验证通过")
    except ValueError as e:
        print(f"❌ 验证失败: {e}")


if __name__ == "__main__":
    print("🎯 智能ORM系统完整演示")
    print("=" * 60)
    
    # 运行演示
    demo_smart_orm()
    demo_migration_commands()
    demo_model_evolution()
    demo_validation_rules()
    
    print("\n🎉 演示完成！")
    print("\n💡 使用提示:")
    print("1. 使用 @auto_migrate 装饰器自动检测模型变更")
    print("2. 使用 @track_changes 装饰器跟踪数据变更")
    print("3. 使用 @auto_validate 装饰器自动验证数据")
    print("4. 使用命令行工具管理迁移")
    print("5. 在生产环境使用前，务必在测试环境验证")