# 数据库快速开始指南

## 5分钟快速配置

### 1. 选择数据库类型

```python
# PostgreSQL (推荐，默认)
from app.core.config.settings import DatabaseConfig, DatabaseType

config = DatabaseConfig(
    type=DatabaseType.POSTGRESQL,
    host="localhost",
    port=5432,
    database="ai_framework",
    username="postgres",
    password="password"
)
```

```python
# MySQL
config = DatabaseConfig(
    type=DatabaseType.MYSQL,
    host="localhost",
    port=3306,
    database="ai_framework",
    username="root",
    password="password"
)
```

```python
# SQLite (最简单)
config = DatabaseConfig(
    type=DatabaseType.SQLITE,
    sqlite_path="database.db"
)
```

### 2. 初始化数据库

```python
from app.core.database import init_database

# 初始化数据库
db_manager = init_database(config)

# 测试连接
if db_manager.test_connection():
    print("✅ 数据库连接成功")
else:
    print("❌ 数据库连接失败")
```

### 3. 使用数据库

```python
from app.core.database import get_database_manager

# 获取数据库管理器
db_manager = get_database_manager()

# 执行SQL
with db_manager.get_session() as session:
    # 创建表
    session.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
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
        print(f"用户: {user[1]}, 邮箱: {user[2]}")
```

## 环境变量配置

### 1. 设置环境变量

```bash
# PostgreSQL
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ai_framework
export DB_USER=postgres
export DB_PASSWORD=password

# 或使用URL
export DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_framework
```

```bash
# MySQL
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=ai_framework
export DB_USER=root
export DB_PASSWORD=password
```

```bash
# SQLite
export DB_TYPE=sqlite
export SQLITE_PATH=database.db
```

### 2. 使用默认配置

```python
from app.core.database import get_database_manager

# 自动读取环境变量
db_manager = get_database_manager()
```

## 数据库迁移

### 1. 创建迁移

```python
from app.core.database.migrations import create_migration

# 创建用户表迁移
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

# 执行迁移
migrate()
```

### 3. 回滚迁移

```python
from app.core.database.migrations import rollback

# 回滚一个迁移
rollback(1)
```

## 常用配置

### 1. 开发环境

```python
# SQLite + 调试模式
config = DatabaseConfig(
    type=DatabaseType.SQLITE,
    sqlite_path="dev.db",
    echo=True  # 显示SQL
)
```

### 2. 生产环境

```python
# PostgreSQL + 连接池
config = DatabaseConfig(
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

### 3. 测试环境

```python
# SQLite + 内存数据库
config = DatabaseConfig(
    type=DatabaseType.SQLITE,
    sqlite_path=":memory:"  # 内存数据库
)
```

## 错误处理

```python
from app.core.database import get_database_manager
from app.core.database.exceptions import DatabaseConnectionError

try:
    db_manager = get_database_manager()
    db_manager.connect()
except DatabaseConnectionError as e:
    print(f"数据库连接失败: {e}")
```

## 完整示例

```python
"""
完整的数据库使用示例
"""

from app.core.config.settings import DatabaseConfig, DatabaseType
from app.core.database import init_database, get_database_manager
from app.core.database.migrations import create_migration, migrate

def main():
    # 1. 配置数据库
    config = DatabaseConfig(
        type=DatabaseType.SQLITE,
        sqlite_path="example.db"
    )
    
    # 2. 初始化数据库
    db_manager = init_database(config)
    
    # 3. 测试连接
    if not db_manager.test_connection():
        print("❌ 数据库连接失败")
        return
    
    print("✅ 数据库连接成功")
    
    # 4. 创建迁移
    create_migration(
        name="create_users_table",
        up_sql="""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        down_sql="DROP TABLE users"
    )
    
    # 5. 执行迁移
    migrate()
    
    # 6. 使用数据库
    with db_manager.get_session() as session:
        # 插入数据
        session.execute(
            "INSERT INTO users (name, email) VALUES (:name, :email)",
            {"name": "张三", "email": "zhangsan@example.com"}
        )
        
        # 查询数据
        result = session.execute("SELECT * FROM users")
        users = result.fetchall()
        
        print(f"查询到 {len(users)} 个用户:")
        for user in users:
            print(f"  ID: {user[0]}, 姓名: {user[1]}, 邮箱: {user[2]}")

if __name__ == "__main__":
    main()
```

## 总结

✅ **5分钟配置**：选择数据库类型，设置连接参数  
✅ **自动连接**：框架自动管理连接和会话  
✅ **迁移支持**：版本化的数据库变更管理  
✅ **多数据库**：支持PostgreSQL、MySQL、SQLite、MongoDB等  
✅ **错误处理**：完善的异常处理机制  

现在你可以开始使用多数据库支持了！