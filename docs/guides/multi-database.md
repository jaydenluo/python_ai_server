# 多数据库支持指南

## 概述

本框架支持多种数据库类型，默认使用PostgreSQL，同时支持MySQL、SQLite、MongoDB、Oracle、SQL Server等数据库。

## 支持的数据库类型

| 数据库类型 | 状态 | 驱动 | 特殊配置 |
|-----------|------|------|----------|
| PostgreSQL | ✅ 默认 | psycopg2 | 无 |
| MySQL | ✅ 支持 | PyMySQL | charset, collation |
| MariaDB | ✅ 支持 | PyMySQL | 同MySQL |
| SQLite | ✅ 支持 | 内置 | sqlite_path |
| MongoDB | ✅ 支持 | motor | auth_source, auth_mechanism |
| Oracle | ✅ 支持 | cx_Oracle | 无 |
| SQL Server | ✅ 支持 | pyodbc | 无 |

## 配置方式

### 1. 环境变量配置

#### PostgreSQL (默认)
```bash
# 基础配置
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ai_framework
export DB_USER=postgres
export DB_PASSWORD=password

# 或使用URL
export DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_framework
```

#### MySQL
```bash
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=ai_framework
export DB_USER=root
export DB_PASSWORD=password
```

#### SQLite
```bash
export DB_TYPE=sqlite
export SQLITE_PATH=./database.db
```

#### MongoDB
```bash
export DB_TYPE=mongodb
export DB_HOST=localhost
export DB_PORT=27017
export DB_NAME=ai_framework
export DB_USER=
export DB_PASSWORD=
```

### 2. 配置文件

创建 `config.yaml` 文件：

```yaml
database:
  type: postgresql  # 或 mysql, sqlite, mongodb 等
  host: localhost
  port: 5432
  database: ai_framework
  username: postgres
  password: password
  
  # 连接池配置
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  pool_recycle: 3600
  
  # MySQL 特殊配置
  charset: utf8mb4
  collation: utf8mb4_unicode_ci
  
  # SQLite 特殊配置
  sqlite_path: database.db
  
  # MongoDB 特殊配置
  mongodb_auth_source: admin
  mongodb_auth_mechanism: SCRAM-SHA-1
```

### 3. 代码配置

```python
from app.core.config.settings import DatabaseConfig, DatabaseType
from app.core.database import init_database

# PostgreSQL 配置
postgresql_config = DatabaseConfig(
    type=DatabaseType.POSTGRESQL,
    host="localhost",
    port=5432,
    database="ai_framework",
    username="postgres",
    password="password"
)

# MySQL 配置
mysql_config = DatabaseConfig(
    type=DatabaseType.MYSQL,
    host="localhost",
    port=3306,
    database="ai_framework",
    username="root",
    password="password",
    charset="utf8mb4"
)

# SQLite 配置
sqlite_config = DatabaseConfig(
    type=DatabaseType.SQLITE,
    sqlite_path="database.db"
)

# MongoDB 配置
mongodb_config = DatabaseConfig(
    type=DatabaseType.MONGODB,
    host="localhost",
    port=27017,
    database="ai_framework"
)

# 初始化数据库
db_manager = init_database(postgresql_config)
```

## 使用方法

### 1. 基础使用

```python
from app.core.database import get_database_manager

# 获取数据库管理器
db_manager = get_database_manager()

# 测试连接
if db_manager.test_connection():
    print("数据库连接成功")
else:
    print("数据库连接失败")

# 获取数据库信息
info = db_manager.get_database_info()
print(f"数据库类型: {info['type']}")
print(f"主机: {info['host']}")
print(f"端口: {info['port']}")
```

### 2. SQL 数据库操作

```python
from app.core.database import get_database_manager

db_manager = get_database_manager()

# 使用会话进行数据库操作
with db_manager.get_session() as session:
    # 创建表
    session.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 插入数据
    session.execute(
        "INSERT INTO users (name, email) VALUES (:name, :email)",
        {"name": "张三", "email": "zhangsan@example.com"}
    )
    
    # 查询数据
    result = session.execute("SELECT * FROM users")
    users = result.fetchall()
    for user in users:
        print(f"ID: {user[0]}, 姓名: {user[1]}, 邮箱: {user[2]}")
```

### 3. MongoDB 操作

```python
from app.core.database import get_database_manager

db_manager = get_database_manager()

# 获取MongoDB客户端
client = db_manager.get_mongodb_client()
db = db_manager.get_mongodb_database()

# 操作集合
collection = db["users"]

# 插入文档
result = collection.insert_one({
    "name": "张三",
    "email": "zhangsan@example.com",
    "age": 25
})
print(f"插入成功: {result.inserted_id}")

# 查询文档
users = collection.find({"age": {"$gte": 18}})
for user in users:
    print(f"用户: {user['name']}, 邮箱: {user['email']}")
```

### 4. 原生SQL执行

```python
from app.core.database import get_database_manager

db_manager = get_database_manager()

# 执行原生SQL
result = db_manager.execute_raw_sql(
    "SELECT COUNT(*) FROM users",
    {}
)
count = result.fetchone()[0]
print(f"用户总数: {count}")
```

## 数据库迁移

### 1. 创建迁移

```python
from app.core.database.migrations import create_migration

# 创建迁移
migration = create_migration(
    name="create_users_table",
    up_sql="""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    down_sql="DROP TABLE users"
)
```

### 2. 执行迁移

```python
from app.core.database.migrations import migrate, migration_status

# 查看迁移状态
migration_status()

# 执行所有待应用的迁移
migrate()
```

### 3. 回滚迁移

```python
from app.core.database.migrations import rollback

# 回滚一个迁移
rollback(1)

# 回滚多个迁移
rollback(3)
```

## 连接池配置

### 1. 基础配置

```python
from app.core.config.settings import DatabaseConfig, DatabaseType

config = DatabaseConfig(
    type=DatabaseType.POSTGRESQL,
    host="localhost",
    port=5432,
    database="ai_framework",
    username="postgres",
    password="password",
    
    # 连接池配置
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 最大溢出连接数
    pool_timeout=30,     # 连接超时时间（秒）
    pool_recycle=3600   # 连接回收时间（秒）
)
```

### 2. 高级配置

```python
# 高并发配置
high_concurrency_config = DatabaseConfig(
    type=DatabaseType.POSTGRESQL,
    host="localhost",
    port=5432,
    database="ai_framework",
    username="postgres",
    password="password",
    pool_size=20,        # 更大的连接池
    max_overflow=50,     # 更多溢出连接
    pool_timeout=60,     # 更长超时时间
    pool_recycle=7200   # 更长回收时间
)

# 低资源配置
low_resource_config = DatabaseConfig(
    type=DatabaseType.SQLITE,
    sqlite_path="database.db",
    pool_size=1,         # 最小连接池
    max_overflow=0,      # 无溢出连接
    pool_timeout=10      # 短超时时间
)
```

## 错误处理

### 1. 连接错误

```python
from app.core.database import get_database_manager
from app.core.database.exceptions import DatabaseConnectionError

try:
    db_manager = get_database_manager()
    db_manager.connect()
except DatabaseConnectionError as e:
    print(f"数据库连接失败: {e}")
```

### 2. 配置错误

```python
from app.core.database.exceptions import DatabaseConfigurationError

try:
    # 使用不支持的数据库类型
    config = DatabaseConfig(type="unsupported_db")
except DatabaseConfigurationError as e:
    print(f"数据库配置错误: {e}")
```

## 最佳实践

### 1. 环境分离

```python
# 开发环境
development_config = DatabaseConfig(
    type=DatabaseType.SQLITE,
    sqlite_path="dev.db"
)

# 测试环境
testing_config = DatabaseConfig(
    type=DatabaseType.SQLITE,
    sqlite_path="test.db"
)

# 生产环境
production_config = DatabaseConfig(
    type=DatabaseType.POSTGRESQL,
    host="prod-db.example.com",
    port=5432,
    database="ai_framework",
    username="app_user",
    password="secure_password",
    pool_size=20,
    max_overflow=50
)
```

### 2. 连接管理

```python
from app.core.database import get_database_manager

# 使用上下文管理器
with get_database_manager() as db_manager:
    # 数据库操作
    pass
# 自动关闭连接
```

### 3. 迁移管理

```python
# 在应用启动时执行迁移
from app.core.database.migrations import migrate

def startup():
    try:
        migrate()
        print("✅ 数据库迁移完成")
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
```

## 故障排除

### 1. 连接问题

```python
# 检查数据库配置
db_manager = get_database_manager()
info = db_manager.get_database_info()
print(f"数据库信息: {info}")

# 测试连接
if db_manager.test_connection():
    print("✅ 连接正常")
else:
    print("❌ 连接失败")
```

### 2. 迁移问题

```python
# 检查迁移状态
from app.core.database.migrations import migration_status
migration_status()

# 手动回滚
from app.core.database.migrations import rollback
rollback(1)
```

### 3. 性能问题

```python
# 调整连接池配置
config = DatabaseConfig(
    # ... 其他配置
    pool_size=50,        # 增加连接池大小
    max_overflow=100,    # 增加溢出连接
    pool_timeout=120     # 增加超时时间
)
```

## 总结

多数据库支持系统提供了：

✅ **统一接口**：所有数据库使用相同的API  
✅ **自动适配**：根据配置自动选择适配器  
✅ **连接池**：高效的连接管理  
✅ **迁移系统**：版本化的数据库变更  
✅ **错误处理**：完善的异常处理机制  
✅ **灵活配置**：支持多种配置方式  

选择适合你项目的数据库类型，享受统一的开发体验！