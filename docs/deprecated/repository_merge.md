# 仓储层合并说明

## 📁 合并概述

将 `app/core/repositories/` 下的 `base_repository.py` 和 `advanced_repository.py` 合并成一个 `repository.py` 文件，提供统一的数据访问接口。

## 🔄 合并的文件

### 1. 基础仓储类
- **原文件**: `app/core/repositories/base_repository.py`
- **功能**: 基础CRUD操作
- **状态**: 已合并到 `repository.py`

### 2. 高级仓储类
- **原文件**: `app/core/repositories/advanced_repository.py`
- **功能**: 高级查询和复杂操作
- **状态**: 已合并到 `repository.py`

### 3. 新的统一仓储类
- **新文件**: `app/core/repositories/repository.py`
- **功能**: 整合基础和高级功能
- **类名**: `Repository`

## 📂 新的目录结构

```
app/core/repositories/
├── __init__.py         # 仓储模块入口
└── repository.py       # 统一的仓储类
```

## 🎯 合并优势

### 1. 统一的接口
- 一个类提供所有数据访问功能
- 避免功能重复和混淆
- 更简洁的API设计

### 2. 完整的功能覆盖
- **基础CRUD**: create, get_by_id, update, delete
- **查询功能**: 条件查询、搜索、排序、分页
- **关联查询**: 预加载关联数据
- **聚合查询**: 统计、分组、聚合函数
- **高级查询**: 原生SQL、JSON查询、数组查询
- **批量操作**: 批量插入、更新、删除
- **事务管理**: 事务执行、批量操作

### 3. 更好的维护性
- 单一文件，易于维护
- 功能集中，减少重复代码
- 统一的错误处理

## 📝 使用方式

### 基础使用
```python
from app.core.repositories import Repository

# 创建仓储实例
user_repo = Repository(User, session)

# 基础CRUD操作
user = user_repo.create(username="john", email="john@example.com")
user = user_repo.get_by_id(1)
users = user_repo.get_all()
user_repo.update(1, username="jane")
user_repo.delete(1)
```

### 高级查询
```python
# 条件查询
users = user_repo.filter_by_conditions({
    "status": {"operator": "eq", "value": "active"},
    "created_at": {"operator": "gte", "value": date.today() - timedelta(days=30)}
})

# 全文搜索
users = user_repo.search_by_text(["username", "email"], "john")

# 关联查询
user = user_repo.get_with_relations(1, ["posts", "comments"])

# 分页查询
result = user_repo.paginate(page=1, per_page=10, order_by="created_at")
```

### 聚合查询
```python
# 统计信息
stats = user_repo.get_field_stats("login_count")

# 分组统计
groups = user_repo.group_by_field("status", "count")

# 原生SQL
results = user_repo.get_by_sql("SELECT * FROM users WHERE status = :status", {"status": "active"})
```

### 批量操作
```python
# 批量插入
users = user_repo.bulk_insert([
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"}
])

# 批量更新
updated_count = user_repo.bulk_update_by_conditions(
    {"status": "pending"}, 
    {"status": "active"}
)

# 批量删除
deleted_count = user_repo.bulk_delete_by_conditions({"status": "inactive"})
```

## 🔧 迁移步骤

1. **创建新文件**: 合并两个文件的功能到 `repository.py`
2. **更新导入**: 修改所有引用旧类的代码
3. **测试功能**: 确保所有功能正常工作
4. **删除旧文件**: 删除 `base_repository.py` 和 `advanced_repository.py`
5. **更新文档**: 更新相关文档和示例

## ✅ 完成状态

- [x] 创建统一的 `repository.py` 文件
- [x] 合并基础和高级功能
- [x] 更新 `__init__.py` 导入
- [x] 删除旧文件
- [x] 创建合并说明文档

## 🎉 总结

通过这次合并，我们实现了：

1. **统一的接口**: 一个类提供所有数据访问功能
2. **完整的功能**: 涵盖基础和高级查询需求
3. **更好的维护性**: 单一文件，易于维护
4. **简洁的API**: 避免功能重复和混淆

这样的设计更符合单一职责原则，提供了完整而统一的数据访问解决方案！🚀