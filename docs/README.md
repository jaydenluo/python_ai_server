# 📚 Python AI Base Server 文档中心

> 欢迎来到 Python AI Base Server 的文档中心！

## 📖 文档导航

### 🚀 入门指南 (Getting Started)

新手从这里开始，快速了解项目并开始开发：

- **[快速开始](getting-started/quick-start.md)** - 5分钟快速入门
- **[数据库入门](getting-started/database.md)** - 数据库配置和使用
- **[核心功能](getting-started/core-features.md)** - 框架核心功能介绍

### 📘 使用指南 (Guides)

详细的功能使用指南和最佳实践：

#### API 开发
- **[API 使用指南](guides/api-usage.md)** - API 开发完整指南
- **[短参数指南](guides/short-parameters.md)** - 简化 API 参数

#### 数据库相关
- **[多数据库支持](guides/multi-database.md)** - 多数据库配置
- **[ORM 关系](guides/orm-relationships.md)** - 模型关系定义
- **[SQLAlchemy 实体设计](guides/sqlalchemy-entity-design.md)** - 实体设计规范
- **[自动模型发现](guides/auto-model-discovery.md)** - 模型自动导入

#### 高级功能
- **[智能导入](guides/smart-import.md)** - 智能模块导入
- **[智能中间件](guides/smart-middleware.md)** - 智能中间件系统
- **[自动导入示例](guides/auto-import-examples.md)** - 详细示例
- **[自动导入快速参考](guides/auto-import-quick-reference.md)** - 快速查阅

#### 安全性
- **[安全指南](guides/security.md)** - 安全最佳实践
- **[安全实现](guides/security-implementation.md)** - 安全功能实现

#### AI 功能
- **[AI 功能](guides/ai.md)** - AI 集成指南
- **[AI 工作流](guides/ai-workflow.md)** - AI 工作流平台

#### 工具库
- **[工具库指南](guides/utils-library.md)** - 内置工具库使用

### 🏗️ 架构设计 (Architecture)

深入了解框架的架构设计：

- **[架构概览](architecture/overview.md)** - 框架整体架构
- **[路由系统](architecture/routing.md)** - 注解路由系统
- **[中间件系统](architecture/middleware.md)** - 中间件架构
- **[RBAC 权限系统](architecture/rbac.md)** - 基于角色的权限控制
- **[服务层架构](architecture/service-layer.md)** - 服务层设计
- **[ORM 系统](architecture/orm.md)** - 智能 ORM 系统

### 🔌 API 参考 (API Reference)

API 框架和控制器文档：

- **[API 框架](api/framework.md)** - API 框架完整文档
- **[控制器](api/controllers.md)** - 控制器组织和使用

### 📦 已废弃 (Deprecated)

这些文档已过时，仅供参考：

- [文件重组](deprecated/file_reorganization.md)
- [文件重组 v2](deprecated/file_reorganization_v2.md)
- [ORM 重组](deprecated/orm_reorganization.md)
- [模型文件重组](deprecated/model_file_reorganization.md)
- [服务层重组](deprecated/services_reorganization.md)
- [仓库合并](deprecated/repository_merge.md)
- [API 框架简化](deprecated/api_framework_simplification.md)
- [迁移系统对比](deprecated/migration_systems_comparison.md)
- [进度跟踪](deprecated/progress_tracking.md)
- [功能列表](deprecated/feature-list.md)

---

## 🎯 推荐学习路径

### 初学者路径
1. 阅读 **[快速开始](getting-started/quick-start.md)**
2. 了解 **[核心功能](getting-started/core-features.md)**
3. 配置 **[数据库](getting-started/database.md)**
4. 学习 **[API 使用指南](guides/api-usage.md)**

### 进阶开发者路径
1. 深入 **[架构概览](architecture/overview.md)**
2. 理解 **[路由系统](architecture/routing.md)**
3. 掌握 **[中间件系统](architecture/middleware.md)**
4. 学习 **[RBAC 权限](architecture/rbac.md)**

### AI 开发者路径
1. 查看 **[AI 功能](guides/ai.md)**
2. 了解 **[AI 工作流](guides/ai-workflow.md)**
3. 集成 **[模型管理](guides/sqlalchemy-entity-design.md)**

---

## 📝 文档约定

### 代码示例

所有代码示例都经过测试，可以直接使用：

```python
# Python 代码示例
from app.models.entities.system.user_management import User

def get_user(user_id: int) -> User:
    """获取用户"""
    return User.query.filter_by(id=user_id).first()
```

### 命令示例

```bash
# Windows 命令
.conda\python.exe migrate.py upgrade

# 或者直接使用
python migrate.py upgrade
```

### 注意事项

> 💡 **提示**: 重要的提示信息
> 
> ⚠️ **警告**: 需要注意的事项
> 
> ❌ **错误**: 常见错误示例
> 
> ✅ **推荐**: 推荐的做法

---

## 🔗 相关链接

- **项目根目录**: [README.md](../README.md)
- **优化报告**: [OPTIMIZATION_COMPLETED.md](../OPTIMIZATION_COMPLETED.md)
- **优化总结**: [OPTIMIZATION_SUMMARY.md](../OPTIMIZATION_SUMMARY.md)
- **快速启动**: [QUICK_START_AFTER_OPTIMIZATION.md](../QUICK_START_AFTER_OPTIMIZATION.md)

---

## 🤝 贡献文档

如果您发现文档有误或需要改进，欢迎：

1. 提交 Issue
2. 发起 Pull Request
3. 联系维护团队

---

## 📄 许可证

本项目文档遵循项目主许可证。

---

**最后更新**: 2025-10-03  
**文档版本**: 2.0.0

