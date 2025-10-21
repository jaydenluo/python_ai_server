# 自动导入系统 - 实用示例

## 📚 目录

1. [基础使用示例](#基础使用示例)
2. [项目结构示例](#项目结构示例)
3. [迁移示例](#迁移示例)
4. [高级用法示例](#高级用法示例)
5. [测试示例](#测试示例)
6. [故障排除示例](#故障排除示例)

---

## 🚀 基础使用示例

### 示例 1: 模型类自动导入

#### 设置 `app/models/entities/__init__.py`

```python
"""
数据实体模块
包含用户、AI模型、文章、评论等实体类
使用智能导入，自动发现所有模型类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入 - 只需要这两行代码！
__getattr__, __dir__ = setup_smart_import(__name__)
```

#### 模型文件结构

```
app/models/entities/
├── __init__.py          # 智能导入设置
├── __init__.pyi         # 类型存根（自动生成）
├── user.py             # 用户模型
├── ai_model.py         # AI模型
├── post.py             # 文章模型
└── comment.py          # 评论模型
```

#### 使用示例

```python
# 在任何地方都可以直接导入
from app.models.entities import User, AIModel, Post, Comment

# 创建实例
user = User(
    name="张三",
    email="zhang@example.com",
    age=25
)

ai_model = AIModel(
    name="GPT-4",
    type="language_model",
    version="4.0"
)

post = Post(
    title="自动导入系统介绍",
    content="这是一个很棒的系统...",
    author_id=user.id
)

# 查看所有可用模型
import app.models.entities as entities
print("可用模型:", dir(entities))
# 输出: ['User', 'AIModel', 'Post', 'Comment', 'EnhancedUser']
```

### 示例 2: 服务类自动导入

#### 设置 `app/services/__init__.py`

```python
"""
业务服务模块
提供认证、用户管理、AI等业务逻辑
使用智能导入，自动发现所有服务类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入
__getattr__, __dir__ = setup_smart_import(__name__)
```

#### 使用示例

```python
from app.services import AuthService, UserService, EmailService

# 认证服务
auth_service = AuthService()
login_result = auth_service.login("user@example.com", "password123")

if login_result.success:
    print(f"登录成功: {login_result.user.name}")
    
    # 用户服务
    user_service = UserService()
    user_profile = user_service.get_profile(login_result.user.id)
    
    # 邮件服务
    email_service = EmailService()
    email_service.send_welcome_email(login_result.user.email)
```

### 示例 3: AI 服务自动导入

#### 设置 `app/services/ai/__init__.py`

```python
"""
AI服务层
提供AI工作流编排、智能体管理、RAG系统等核心功能
使用智能导入，自动发现所有AI服务类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入
__getattr__, __dir__ = setup_smart_import(__name__)
```

#### 使用示例

```python
from app.services.ai import WorkflowService, AgentService, RAGService, MonitoringService

# 工作流服务
workflow_service = WorkflowService()
workflow = workflow_service.create_workflow({
    "name": "客户服务工作流",
    "steps": [
        {"type": "rag", "config": {"knowledge_base": "customer_faq"}},
        {"type": "llm", "config": {"model": "gpt-4"}},
        {"type": "response", "config": {"format": "json"}}
    ]
})

# 智能体服务
agent_service = AgentService()
agent = agent_service.create_agent({
    "name": "客服助手",
    "role": "customer_support",
    "capabilities": ["rag_search", "conversation", "escalation"]
})

# RAG 服务
rag_service = RAGService()
rag_service.add_documents("customer_faq", [
    {"content": "如何重置密码？", "metadata": {"category": "account"}},
    {"content": "支付方式有哪些？", "metadata": {"category": "payment"}}
])

# 监控服务
monitoring_service = MonitoringService()
metrics = monitoring_service.get_workflow_metrics(workflow.id)
print(f"工作流执行次数: {metrics.execution_count}")
```

---

## 🏗️ 项目结构示例

### 完整的项目结构

```
my_ai_platform/
├── app/
│   ├── models/
│   │   ├── entities/
│   │   │   ├── __init__.py          # 智能导入设置
│   │   │   ├── __init__.pyi         # 类型存根
│   │   │   ├── user.py
│   │   │   ├── ai_model.py
│   │   │   ├── workflow.py
│   │   │   ├── agent.py
│   │   │   └── knowledge_base.py
│   │   └── enums/
│   │       ├── __init__.py          # 智能导入设置
│   │       ├── user_status.py
│   │       ├── model_type.py
│   │       └── workflow_status.py
│   ├── services/
│   │   ├── __init__.py              # 智能导入设置
│   │   ├── __init__.pyi             # 类型存根
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── email_service.py
│   │   └── ai/
│   │       ├── __init__.py          # 智能导入设置
│   │       ├── __init__.pyi         # 类型存根
│   │       ├── workflow_service.py
│   │       ├── agent_service.py
│   │       ├── rag_service.py
│   │       └── monitoring_service.py
│   ├── controller/
│   │   ├── admin/
│   │   │   ├── __init__.py          # 智能导入设置
│   │   │   ├── user_admin_api.py
│   │   │   ├── workflow_admin_api.py
│   │   │   └── system_admin_api.py
│   │   ├── api/
│   │   │   ├── __init__.py          # 智能导入设置
│   │   │   ├── user_api.py
│   │   │   ├── auth_api.py
│   │   │   └── ai_model_api.py
│   │   └── web/
│   │       ├── __init__.py          # 智能导入设置
│   │       ├── user_web_api.py
│   │       └── ai_web_api.py
│   └── core/
│       └── discovery/               # 自动导入系统核心
├── docs/
│   ├── auto_import_system.md        # 完整文档
│   ├── auto_import_quick_reference.md
│   └── auto_import_examples.md      # 本文档
├── examples/
│   ├── complete_smart_import_test.py
│   └── smart_import_example.py
└── main.py
```

### 使用整个项目

```python
# main.py - 项目入口文件
from app.models.entities import User, AIModel, Workflow, Agent
from app.services import AuthService, UserService
from app.services.ai import WorkflowService, AgentService, RAGService
from app.controller.api import UserApi, AuthApi

def main():
    """主函数 - 演示完整的自动导入使用"""
    
    # 1. 创建用户
    user = User(name="AI开发者", email="dev@ai.com")
    
    # 2. 认证服务
    auth_service = AuthService()
    token = auth_service.create_token(user)
    
    # 3. 创建AI模型
    ai_model = AIModel(
        name="GPT-4",
        type="language_model",
        provider="openai"
    )
    
    # 4. 创建工作流
    workflow_service = WorkflowService()
    workflow = workflow_service.create_workflow({
        "name": "智能客服工作流",
        "model_id": ai_model.id,
        "steps": [
            {"type": "input_validation"},
            {"type": "rag_search"},
            {"type": "llm_generation"},
            {"type": "response_formatting"}
        ]
    })
    
    # 5. 创建智能体
    agent_service = AgentService()
    agent = agent_service.create_agent({
        "name": "客服小助手",
        "workflow_id": workflow.id,
        "personality": "友好、专业、耐心"
    })
    
    print(f"✅ 成功创建AI平台组件:")
    print(f"   用户: {user.name}")
    print(f"   模型: {ai_model.name}")
    print(f"   工作流: {workflow.name}")
    print(f"   智能体: {agent.name}")

if __name__ == "__main__":
    main()
```

---

## 🔄 迁移示例

### 从手动导入迁移

#### 迁移前 - 复杂的手动导入

```python
# app/models/entities/__init__.py (旧版本 - 50+ 行)
"""
数据实体模块
"""

# 手动导入所有模型
from .user import User
from .ai_model import AIModel
from .workflow import Workflow
from .agent import Agent
from .knowledge_base import KnowledgeBase
from .conversation import Conversation
from .message import Message
from .feedback import Feedback

# 手动维护导出列表
__all__ = [
    "User",
    "AIModel", 
    "Workflow",
    "Agent",
    "KnowledgeBase",
    "Conversation",
    "Message",
    "Feedback"
]

# 提供便捷函数
def get_all_models():
    """获取所有模型类"""
    return [
        User, AIModel, Workflow, Agent,
        KnowledgeBase, Conversation, Message, Feedback
    ]

def get_model_by_name(name: str):
    """根据名称获取模型"""
    models = {
        "User": User,
        "AIModel": AIModel,
        "Workflow": Workflow,
        "Agent": Agent,
        "KnowledgeBase": KnowledgeBase,
        "Conversation": Conversation,
        "Message": Message,
        "Feedback": Feedback
    }
    return models.get(name)

# 模型注册（用于某些框架）
REGISTERED_MODELS = [
    User, AIModel, Workflow, Agent,
    KnowledgeBase, Conversation, Message, Feedback
]
```

#### 迁移后 - 智能导入

```python
# app/models/entities/__init__.py (新版本 - 4 行)
"""
数据实体模块
使用智能导入，自动发现所有模型类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入 - 只需要这两行代码！
__getattr__, __dir__ = setup_smart_import(__name__)
```

#### 迁移脚本

```python
# migrate_to_smart_import.py
"""
自动迁移脚本：从手动导入迁移到智能导入
"""

import os
import shutil
from pathlib import Path

def backup_init_files():
    """备份所有 __init__.py 文件"""
    for init_file in Path(".").rglob("__init__.py"):
        backup_file = str(init_file) + ".backup"
        shutil.copy2(init_file, backup_file)
        print(f"✅ 备份: {init_file} -> {backup_file}")

def migrate_package(package_path: str, package_name: str, description: str):
    """迁移单个包"""
    init_file = Path(package_path) / "__init__.py"
    
    new_content = f'''"""
{description}
使用智能导入，自动发现所有类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入
__getattr__, __dir__ = setup_smart_import(__name__)
'''
    
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 迁移完成: {package_path}")

def main():
    """主迁移函数"""
    print("🚀 开始迁移到智能导入系统")
    
    # 1. 备份现有文件
    print("\n📦 备份现有 __init__.py 文件...")
    backup_init_files()
    
    # 2. 迁移各个包
    packages = [
        ("app/models/entities", "app.models.entities", "数据实体模块"),
        ("app/services", "app.services", "业务服务模块"),
        ("app/services/ai", "app.services.ai", "AI服务层"),
        ("app/controller/admin", "app.controller.admin", "管理员控制器模块"),
        ("app/controller/api", "app.controller.api", "API控制器模块"),
        ("app/controller/web", "app.controller.web", "Web控制器模块"),
    ]
    
    print("\n🔄 迁移包...")
    for package_path, package_name, description in packages:
        if Path(package_path).exists():
            migrate_package(package_path, package_name, description)
    
    # 3. 生成类型存根文件
    print("\n📝 生成类型存根文件...")
    try:
        from app.core.discovery import generate_all_stubs
        generated_files = generate_all_stubs()
        print(f"✅ 生成了 {len(generated_files)} 个存根文件")
    except Exception as e:
        print(f"⚠️ 存根文件生成失败: {e}")
    
    # 4. 测试迁移结果
    print("\n🧪 测试迁移结果...")
    try:
        from app.models.entities import User, AIModel
        from app.services import AuthService
        print("✅ 迁移测试通过！")
    except Exception as e:
        print(f"❌ 迁移测试失败: {e}")
    
    print("\n🎉 迁移完成！")
    print("📋 后续步骤:")
    print("   1. 运行完整测试: python examples/complete_smart_import_test.py")
    print("   2. 检查 IDE 自动补全是否正常")
    print("   3. 如有问题，可从 .backup 文件恢复")

if __name__ == "__main__":
    main()
```

---

## 🔧 高级用法示例

### 示例 1: 自定义识别规则

```python
# custom_smart_importer.py
from app.core.discovery.smart_importer import SmartImporter

class CustomSmartImporter(SmartImporter):
    """自定义智能导入器"""
    
    def _should_export_class(self, cls: type, name: str, package_name: str) -> bool:
        """自定义类识别规则"""
        
        # 处理自定义包
        if 'custom' in package_name:
            # 自定义处理器类
            if name.endswith('Handler'):
                return True
            # 自定义工具类
            if name.endswith('Util') or name.endswith('Helper'):
                return True
        
        # 处理插件包
        if 'plugins' in package_name:
            # 插件类必须继承自 BasePlugin
            base_classes = [base.__name__ for base in cls.__mro__]
            return 'BasePlugin' in base_classes
        
        # 其他情况使用默认规则
        return super()._should_export_class(cls, name, package_name)

# 使用自定义导入器
def setup_custom_smart_import(package_name: str):
    """设置自定义智能导入"""
    custom_importer = CustomSmartImporter()
    
    def __getattr__(name: str):
        return custom_importer.smart_import(name, package_name)
    
    def __dir__():
        return custom_importer.get_available_exports(package_name)
    
    return __getattr__, __dir__

# 在 __init__.py 中使用
# from custom_smart_importer import setup_custom_smart_import
# __getattr__, __dir__ = setup_custom_smart_import(__name__)
```

### 示例 2: 条件导入

```python
# conditional_import.py
import os
from app.core.discovery.module_hooks import setup_smart_import

def setup_conditional_smart_import(package_name: str):
    """根据环境条件设置智能导入"""
    
    # 开发环境：使用智能导入
    if os.getenv('ENVIRONMENT') == 'development':
        return setup_smart_import(package_name)
    
    # 生产环境：使用传统导入（更可控）
    else:
        def __getattr__(name: str):
            # 手动映射关键类
            manual_imports = {
                'User': lambda: __import__('app.models.entities.user', fromlist=['User']).User,
                'AuthService': lambda: __import__('app.services.auth_service', fromlist=['AuthService']).AuthService,
            }
            
            if name in manual_imports:
                return manual_imports[name]()
            else:
                raise AttributeError(f"module '{package_name}' has no attribute '{name}'")
        
        def __dir__():
            return list(manual_imports.keys())
        
        return __getattr__, __dir__
```

### 示例 3: 性能监控

```python
# performance_monitoring.py
import time
import logging
from functools import wraps
from app.core.discovery.module_hooks import setup_smart_import

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_monitored_smart_import(package_name: str):
    """带性能监控的智能导入"""
    
    base_getattr, base_dir = setup_smart_import(package_name)
    
    @wraps(base_getattr)
    def monitored_getattr(name: str):
        start_time = time.time()
        try:
            result = base_getattr(name)
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            
            logger.info(f"导入 {package_name}.{name} 耗时: {duration:.2f}ms")
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            logger.error(f"导入 {package_name}.{name} 失败 (耗时: {duration:.2f}ms): {e}")
            raise
    
    return monitored_getattr, base_dir

# 使用示例
# from performance_monitoring import setup_monitored_smart_import
# __getattr__, __dir__ = setup_monitored_smart_import(__name__)
```

---

## 🧪 测试示例

### 单元测试示例

```python
# test_auto_import.py
import unittest
import sys
from unittest.mock import patch

class TestAutoImport(unittest.TestCase):
    """自动导入系统单元测试"""
    
    def test_model_import(self):
        """测试模型导入"""
        from app.models.entities import User, AIModel
        
        self.assertIsNotNone(User)
        self.assertIsNotNone(AIModel)
        self.assertTrue(hasattr(User, '__tablename__'))
    
    def test_service_import(self):
        """测试服务导入"""
        from app.services import AuthService, UserService
        
        self.assertIsNotNone(AuthService)
        self.assertIsNotNone(UserService)
        self.assertTrue(callable(AuthService))
    
    def test_dir_functionality(self):
        """测试目录功能"""
        import app.models.entities as entities
        
        available = dir(entities)
        self.assertIn('User', available)
        self.assertIn('AIModel', available)
        self.assertIsInstance(available, list)
    
    def test_lazy_loading(self):
        """测试延迟加载"""
        # 记录导入前的模块数量
        modules_before = len(sys.modules)
        
        # 导入但不使用
        from app.models.entities import User
        
        # 模块数量应该没有显著增加
        modules_after_import = len(sys.modules)
        self.assertLess(modules_after_import - modules_before, 5)
        
        # 使用类时才真正加载
        user = User()
        modules_after_use = len(sys.modules)
        self.assertGreater(modules_after_use, modules_after_import)
    
    def test_error_handling(self):
        """测试错误处理"""
        with self.assertRaises(AttributeError):
            from app.models.entities import NonExistentModel
    
    def test_caching(self):
        """测试缓存机制"""
        import time
        
        # 首次导入
        start = time.time()
        from app.models.entities import User
        first_import_time = time.time() - start
        
        # 重复导入（应该使用缓存）
        start = time.time()
        from app.models.entities import User
        cached_import_time = time.time() - start
        
        # 缓存导入应该更快
        self.assertLess(cached_import_time, first_import_time)

if __name__ == '__main__':
    unittest.main()
```

### 集成测试示例

```python
# test_integration.py
import unittest
from app.models.entities import User, AIModel
from app.services import AuthService, UserService
from app.services.ai import WorkflowService

class TestIntegration(unittest.TestCase):
    """集成测试 - 测试各组件协同工作"""
    
    def setUp(self):
        """测试前准备"""
        self.user_service = UserService()
        self.auth_service = AuthService()
        self.workflow_service = WorkflowService()
    
    def test_user_workflow(self):
        """测试完整的用户工作流"""
        
        # 1. 创建用户
        user = User(
            name="测试用户",
            email="test@example.com"
        )
        
        # 2. 用户注册
        registration_result = self.user_service.register(user)
        self.assertTrue(registration_result.success)
        
        # 3. 用户登录
        login_result = self.auth_service.login(
            "test@example.com", 
            "password123"
        )
        self.assertTrue(login_result.success)
        
        # 4. 创建AI工作流
        workflow = self.workflow_service.create_workflow({
            "name": "测试工作流",
            "owner_id": login_result.user.id,
            "steps": [
                {"type": "input", "config": {}},
                {"type": "llm", "config": {"model": "gpt-4"}},
                {"type": "output", "config": {}}
            ]
        })
        
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.owner_id, login_result.user.id)
    
    def test_ai_model_integration(self):
        """测试AI模型集成"""
        
        # 创建AI模型
        ai_model = AIModel(
            name="GPT-4",
            type="language_model",
            provider="openai"
        )
        
        # 在工作流中使用模型
        workflow = self.workflow_service.create_workflow({
            "name": "AI模型测试工作流",
            "model_id": ai_model.id,
            "steps": [
                {"type": "llm", "config": {"model_id": ai_model.id}}
            ]
        })
        
        self.assertEqual(workflow.model_id, ai_model.id)

if __name__ == '__main__':
    unittest.main()
```

---

## 🔍 故障排除示例

### 调试工具示例

```python
# debug_auto_import.py
"""
自动导入系统调试工具
"""

import sys
import traceback
from app.core.discovery.smart_importer import _smart_importer

def debug_import_issue(package_name: str, class_name: str):
    """调试导入问题"""
    
    print(f"🔍 调试导入问题: {package_name}.{class_name}")
    print("=" * 50)
    
    # 1. 检查包是否存在
    try:
        import importlib
        package = importlib.import_module(package_name)
        print(f"✅ 包存在: {package}")
        print(f"   包路径: {package.__path__}")
    except ImportError as e:
        print(f"❌ 包不存在: {e}")
        return
    
    # 2. 检查缓存状态
    print(f"\n📦 缓存状态:")
    if package_name in _smart_importer._cache:
        cached_classes = list(_smart_importer._cache[package_name].keys())
        print(f"   已缓存的类: {cached_classes}")
        
        if class_name in _smart_importer._cache[package_name]:
            print(f"✅ {class_name} 在缓存中")
        else:
            print(f"❌ {class_name} 不在缓存中")
    else:
        print(f"   包未被扫描")
    
    # 3. 手动扫描包
    print(f"\n🔍 手动扫描包:")
    try:
        _smart_importer._scan_package(package_name)
        available = _smart_importer.get_available_exports(package_name)
        print(f"   扫描结果: {available}")
        
        if class_name in available:
            print(f"✅ {class_name} 被识别")
        else:
            print(f"❌ {class_name} 未被识别")
    except Exception as e:
        print(f"❌ 扫描失败: {e}")
        traceback.print_exc()
    
    # 4. 检查文件是否存在
    print(f"\n📁 文件检查:")
    import os
    from pathlib import Path
    
    if hasattr(package, '__path__'):
        package_path = Path(package.__path__[0])
        
        # 查找可能的文件名
        possible_files = [
            f"{class_name.lower()}.py",
            f"{class_name}.py",
            f"{'_'.join(class_name.split()).lower()}.py"
        ]
        
        for filename in possible_files:
            file_path = package_path / filename
            if file_path.exists():
                print(f"✅ 找到文件: {file_path}")
                
                # 检查文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if f"class {class_name}" in content:
                            print(f"✅ 文件包含类定义: class {class_name}")
                        else:
                            print(f"❌ 文件不包含类定义: class {class_name}")
                except Exception as e:
                    print(f"⚠️ 读取文件失败: {e}")
                break
        else:
            print(f"❌ 未找到对应的文件")
    
    # 5. 尝试手动导入
    print(f"\n🔧 尝试手动导入:")
    try:
        module_name = f"{package_name}.{class_name.lower()}"
        module = importlib.import_module(module_name)
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            print(f"✅ 手动导入成功: {cls}")
            
            # 检查类是否符合识别规则
            should_export = _smart_importer._should_export_class(cls, class_name, package_name)
            print(f"   符合识别规则: {should_export}")
        else:
            print(f"❌ 模块中没有类: {class_name}")
    except Exception as e:
        print(f"❌ 手动导入失败: {e}")

def check_system_health():
    """检查系统健康状态"""
    
    print("🏥 系统健康检查")
    print("=" * 30)
    
    # 检查核心模块
    try:
        from app.core.discovery.smart_importer import SmartImporter
        from app.core.discovery.module_hooks import setup_smart_import
        print("✅ 核心模块正常")
    except ImportError as e:
        print(f"❌ 核心模块异常: {e}")
        return
    
    # 检查各个包
    packages = [
        "app.models.entities",
        "app.services", 
        "app.services.ai",
        "app.controller.admin",
        "app.controller.api",
        "app.controller.web"
    ]
    
    for package in packages:
        try:
            exports = _smart_importer.get_available_exports(package)
            print(f"✅ {package}: {len(exports)} 个类")
        except Exception as e:
            print(f"❌ {package}: {e}")
    
    # 检查性能
    import time
    start = time.time()
    try:
        from app.models.entities import User
        from app.services import AuthService
        end = time.time()
        print(f"✅ 导入性能: {(end-start)*1000:.2f}ms")
    except Exception as e:
        print(f"❌ 导入性能测试失败: {e}")

# 使用示例
if __name__ == "__main__":
    # 检查系统健康
    check_system_health()
    
    # 调试特定导入问题
    debug_import_issue("app.models.entities", "User")
    debug_import_issue("app.services", "AuthService")
```

### 常见问题解决示例

```python
# fix_common_issues.py
"""
常见问题自动修复工具
"""

def fix_missing_stub_files():
    """修复缺失的类型存根文件"""
    print("🔧 修复类型存根文件...")
    
    try:
        from app.core.discovery import generate_all_stubs
        generated = generate_all_stubs()
        print(f"✅ 生成了 {len(generated)} 个存根文件")
        return True
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def fix_cache_issues():
    """修复缓存问题"""
    print("🔧 清理缓存...")
    
    try:
        from app.core.discovery.smart_importer import _smart_importer
        
        # 清理缓存
        _smart_importer._cache.clear()
        _smart_importer._scanned_modules.clear()
        
        print("✅ 缓存已清理")
        
        # 重新扫描
        packages = ["app.models.entities", "app.services"]
        for package in packages:
            _smart_importer._scan_package(package)
        
        print("✅ 重新扫描完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def fix_import_paths():
    """修复导入路径问题"""
    print("🔧 检查导入路径...")
    
    import sys
    from pathlib import Path
    
    # 确保项目根目录在 Python 路径中
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"✅ 添加项目根目录到路径: {project_root}")
    
    return True

def auto_fix_all():
    """自动修复所有常见问题"""
    print("🚀 自动修复常见问题")
    print("=" * 30)
    
    fixes = [
        ("导入路径", fix_import_paths),
        ("缓存问题", fix_cache_issues), 
        ("存根文件", fix_missing_stub_files)
    ]
    
    success_count = 0
    for name, fix_func in fixes:
        print(f"\n🔧 修复 {name}...")
        if fix_func():
            success_count += 1
    
    print(f"\n🎯 修复结果: {success_count}/{len(fixes)} 成功")
    
    # 测试修复效果
    print("\n🧪 测试修复效果...")
    try:
        from app.models.entities import User
        from app.services import AuthService
        print("✅ 修复成功！自动导入正常工作")
    except Exception as e:
        print(f"❌ 修复后仍有问题: {e}")

if __name__ == "__main__":
    auto_fix_all()
```

---

## 🎯 总结

这些示例展示了自动导入系统的各种使用场景：

### 🚀 基础使用
- 简单的 2 行设置
- 透明的导入体验
- 完整的功能演示

### 🏗️ 项目集成
- 完整的项目结构
- 实际的业务场景
- 最佳实践展示

### 🔄 系统迁移
- 从手动导入的平滑迁移
- 自动化迁移脚本
- 迁移前后对比

### 🔧 高级定制
- 自定义识别规则
- 条件导入策略
- 性能监控集成

### 🧪 测试验证
- 完整的单元测试
- 集成测试示例
- 性能测试方法

### 🔍 问题诊断
- 调试工具和方法
- 常见问题解决
- 自动修复脚本

通过这些示例，您可以快速上手并充分利用自动导入系统的强大功能！