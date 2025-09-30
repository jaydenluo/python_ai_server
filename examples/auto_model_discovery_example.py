"""
自动模型发现系统使用示例
演示如何在不手动注册的情况下使用模型
"""

from app.models import (
    # 基础模型（仍然需要显式导入）
    BaseModel, SoftDeleteModel, AuditModel, TenantModel,
    
    # 智能导入器
    smart_models,
    
    # 便捷函数
    get_model, list_models, reload_models
)

def demo_auto_discovery():
    """演示自动发现功能"""
    
    print("=== 自动模型发现系统演示 ===\n")
    
    # 1. 列出所有发现的模型
    print("1. 所有发现的模型:")
    available_models = list_models()
    for model_name in available_models:
        print(f"   - {model_name}")
    print()
    
    # 2. 使用智能导入器获取模型
    print("2. 使用智能导入器:")
    try:
        # 这些会自动发现，无需手动导入
        User = smart_models.User
        AIModel = smart_models.AIModel
        ModelStatus = smart_models.ModelStatus
        
        print(f"   - User 类: {User}")
        print(f"   - AIModel 类: {AIModel}")
        print(f"   - ModelStatus 枚举: {ModelStatus}")
    except AttributeError as e:
        print(f"   错误: {e}")
    print()
    
    # 3. 使用便捷函数获取模型
    print("3. 使用便捷函数:")
    try:
        User = get_model("User")
        Post = get_model("Post")
        Comment = get_model("Comment")
        
        print(f"   - User: {User}")
        print(f"   - Post: {Post}")
        print(f"   - Comment: {Comment}")
    except AttributeError as e:
        print(f"   错误: {e}")
    print()
    
    # 4. 演示模型使用
    print("4. 模型使用示例:")
    try:
        # 假设我们有这些模型
        if hasattr(smart_models, 'User'):
            User = smart_models.User
            print(f"   - 可以创建 User 实例: {User}")
        
        if hasattr(smart_models, 'ModelStatus'):
            ModelStatus = smart_models.ModelStatus
            print(f"   - 可以使用 ModelStatus 枚举: {ModelStatus}")
            
    except Exception as e:
        print(f"   错误: {e}")
    print()
    
    # 5. 重新加载模型
    print("5. 重新加载模型:")
    print("   调用 reload_models() 重新扫描所有模型...")
    reload_models()
    print("   重新加载完成！")


def demo_usage_patterns():
    """演示不同的使用模式"""
    
    print("\n=== 使用模式演示 ===\n")
    
    # 模式1: 直接导入（推荐）
    print("模式1: 直接导入（推荐）")
    print("from app.models import User, ModelStatus")
    print("user = User()")
    print()
    
    # 模式2: 智能导入器
    print("模式2: 智能导入器")
    print("from app.models import smart_models")
    print("User = smart_models.User")
    print("user = User()")
    print()
    
    # 模式3: 便捷函数
    print("模式3: 便捷函数")
    print("from app.models import get_model")
    print("User = get_model('User')")
    print("user = User()")
    print()
    
    # 模式4: 动态获取
    print("模式4: 动态获取")
    print("from app.models import list_models, get_model")
    print("models = list_models()")
    print("for model_name in models:")
    print("    model_class = get_model(model_name)")
    print()


if __name__ == "__main__":
    demo_auto_discovery()
    demo_usage_patterns()