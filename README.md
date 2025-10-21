# Python AI开发框架

一个融合Laravel和RuoYi优点的Python AI开发框架，专门为人工智能项目提供API接口与AI能力。

## 📚 快速开始

**→ [API 开发指南](API_DEVELOPMENT_GUIDE.md)** - 完整的 API 开发教程（推荐从这里开始）

## 🚀 框架特性

### 核心特性
- **🎯 优雅的语法**: 类似Laravel的简洁API设计，开发者友好
- **🔧 强大的ORM**: 类似Laravel Eloquent的ORM系统，关系映射简单直观
- **🛡️ 内置安全**: CSRF保护、SQL注入防护、XSS防护
- **🚀 高性能**: 异步处理、智能缓存、负载均衡
- **🔌 丰富的生态**: 中间件系统、事件系统、服务容器

### 企业级特性
- **🏢 企业级权限**: 基于RBAC的权限模型，细粒度权限控制
- **📊 后台管理**: 完整的后台管理系统，开箱即用
- **🔐 安全认证**: JWT认证、多租户支持
- **📈 监控系统**: 操作日志、系统监控、性能分析
- **🎨 前端集成**: Vue.js前端，响应式设计

### AI原生特性
- **🤖 模型管理**: AI模型的上传、版本管理、部署
- **🧠 推理服务**: 模型推理API，支持批处理
- **📊 训练服务**: 模型训练任务管理
- **🔍 数据预处理**: 数据清洗、特征工程
- **📈 模型监控**: 性能监控、准确率跟踪

## 📁 项目结构

```
python_ai_framework/
├── app/                          # 应用核心
│   ├── core/                     # 核心框架
│   │   ├── routing/             # 路由系统
│   │   ├── middleware/          # 中间件
│   │   ├── container/           # 依赖注入
│   │   ├── events/              # 事件系统
│   │   └── cache/               # 缓存系统
│   ├── models/                   # 数据模型
│   │   ├── base.py              # 基础模型
│   │   ├── query.py             # 查询构建器
│   │   ├── user.py              # 用户模型
│   │   └── ai_model.py          # AI模型
│   ├── services/                 # 业务服务
│   │   ├── auth/                # 认证服务
│   │   ├── ai/                  # AI服务
│   │   └── user/                # 用户服务
│   ├── api/                      # API接口
│   │   ├── v1/                  # API版本1
│   │   └── middleware/          # API中间件
│   └── admin/                    # 后台管理
│       ├── views/               # 管理视图
│       └── templates/           # 模板文件
├── ai_engine/                    # AI引擎
│   ├── models/                   # 模型管理
│   ├── inference/               # 推理服务
│   ├── training/                # 训练服务
│   └── monitoring/               # 监控服务
├── frontend/                     # 前端项目
│   ├── admin/                   # 管理后台
│   └── api-docs/                # API文档
├── tests/                        # 测试代码
├── docs/                         # 文档
├── scripts/                      # 脚本工具
└── docker/                       # Docker配置
```

## 🛠️ 技术栈

### 后端技术栈
- **Python 3.11+**: 核心开发语言
- **FastAPI**: 高性能Web框架
- **SQLAlchemy**: ORM框架
- **Pydantic**: 数据验证
- **Redis**: 缓存和会话存储
- **Celery**: 异步任务队列
- **Docker**: 容器化部署

### AI技术栈
- **PyTorch/TensorFlow**: 深度学习框架
- **Transformers**: 预训练模型
- **ONNX**: 模型格式转换
- **MLflow**: 模型生命周期管理
- **Ray**: 分布式计算

### 前端技术栈
- **Vue.js 3**: 管理后台框架
- **Element Plus**: UI组件库
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Pinia**: 状态管理

### 数据库技术栈
- **PostgreSQL**: 主数据库
- **Redis**: 缓存和会话
- **MinIO**: 对象存储
- **Elasticsearch**: 全文搜索
- **InfluxDB**: 时序数据

## 🚀 快速开始

### 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd python_ai_framework

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 配置环境

```bash
# 复制配置文件模板
cp config.example.yaml config.yaml

# 编辑配置文件
vim config.yaml
```

### 运行项目

```bash

# 启动
python main.py

# 或使用Docker
docker-compose up -d
```

## 📖 使用示例

### 1. 注解路由（V2版本，推荐）

```python
from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    auth_required, admin_required, rate_limit, cache, api_doc
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response

# 最优雅的写法 - 不写版本参数，不写路由名称
@api_controller(prefix="/users", middleware=["auth"])
class UserController(ResourceController):
    """用户控制器 - 使用注解路由"""
    
    # 不命名路由，不写版本 - 自动生成: users.index (v1)
    # 默认需要认证，无需写中间件
    @get("/")
    @rate_limit(requests_per_minute=60)
    @cache(ttl=300)
    @api_doc(
        summary="获取用户列表",
        description="获取系统中的所有用户列表",
        tags=["用户管理"]
    )
    async def index(self, request: Request) -> Response:
        """获取用户列表"""
        return self._create_response(
            self.success_response(
                data=[],
                message="获取用户列表成功"
            )
        )
    
    # 不命名路由，不写版本 - 自动生成: users.store (v1)
    # 指定管理员权限，自动添加认证
    @post("/", middleware=["admin"])
    async def store(self, request: Request) -> Response:
        """创建用户"""
        pass
```

### 2. 传统路由（V1版本）

```python
from app.core.routing import router, get, post

@get("/users", name="users.index")
def get_users():
    return {"users": []}

@post("/users", name="users.store")
def create_user():
    return {"message": "User created"}
```

### 2. 模型定义

```python
from app.models.base import Model

class User(Model):
    __table__ = "users"
    __fillable__ = ["username", "email", "password"]
    
    def roles(self):
        return self.belongs_to_many(Role, "user_roles", "user_id", "role_id")
```

### 3. 查询使用

```python
# 获取所有用户
users = User.query().get()

# 条件查询
user = User.query().where("email", "user@example.com").first()

# 关联查询
users_with_roles = User.query().with_("roles").get()
```

### 4. 中间件使用

```python
from app.core.middleware import AuthMiddleware

# 注册中间件
middleware_manager.register("auth", AuthMiddleware(secret_key="your-secret-key"))

# 使用中间件
@get("/protected", middleware=["auth"])
def protected_route():
    return {"message": "This is protected"}
```

### 5. AI模型管理

```python
from app.models.ai_model import AIModel

# 创建AI模型
model = AIModel(
    name="my_model",
    type="classification",
    framework="pytorch"
)
model.save()

# 部署模型
deployment = model.deploy()
```

### 6. API使用示例

```python
from examples.api_usage import APIClient

# 创建API客户端
client = APIClient("http://localhost:8000")

# 用户登录
login_result = client.login("username", "password")

# 获取用户列表
users = client.get_users(page=1, per_page=15)

# 创建AI模型
model = client.create_model({
    "name": "my_model",
    "type": "classification",
    "framework": "pytorch"
})

# 模型预测
prediction = client.predict_model(model_id, input_data)
```

## 🔧 配置说明

### 配置文件

项目使用单一的 `config.yaml` 配置文件管理所有配置：

```yaml
# config.yaml
app:
  name: "Python AI Framework"
  debug: true
  port: 8000

database:
  type: "sqlite"  # postgresql, mysql, sqlite, mongodb
  sqlite_path: "database.db"
  auto_migrate: true  # 是否自动执行迁移

redis:
  host: "localhost"
  port: 6379

security:
  secret_key: "your-secret-key"
```

### 数据库迁移

```yaml
# 开发环境 - 启用自动迁移
database:
  auto_migrate: true

# 生产环境 - 禁用自动迁移
database:
  auto_migrate: false
```

### 环境变量（可选）

仅用于敏感信息：

```bash
# 设置数据库密码
export DB_PASSWORD=your-secure-password

# 设置安全密钥
export SECRET_KEY=your-secret-key
```

## 📚 文档

- [架构设计](docs/framework_architecture.md)
- [API文档](docs/api.md)
- [部署指南](docs/deployment.md)
- [开发指南](docs/development.md)

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢以下开源项目的启发：
- [Laravel](https://laravel.com/) - PHP Web框架
- [RuoYi](https://gitee.com/y_project/RuoYi) - Java企业级框架
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python ORM

## 📞 联系我们

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 邮箱: [your-email@example.com]

---

**Python AI开发框架** - 让AI开发更简单、更高效！