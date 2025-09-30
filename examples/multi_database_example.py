"""
多数据库支持示例
演示如何使用不同的数据库配置
"""

import os
from app.core.database import get_database_manager, init_database
from app.core.config.settings import DatabaseConfig, DatabaseType
from app.core.database.migrations import create_migration, migrate, rollback, migration_status


def demo_postgresql():
    """演示PostgreSQL配置"""
    print("=== PostgreSQL 配置示例 ===\n")
    
    # 方式1: 使用环境变量
    os.environ["DB_TYPE"] = "postgresql"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_NAME"] = "ai_framework"
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASSWORD"] = "password"
    
    # 方式2: 使用数据库URL
    # os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/ai_framework"
    
    # 初始化数据库
    db_manager = init_database()
    
    # 测试连接
    if db_manager.test_connection():
        print("✅ PostgreSQL 连接成功")
        print(f"数据库信息: {db_manager.get_database_info()}")
    else:
        print("❌ PostgreSQL 连接失败")


def demo_mysql():
    """演示MySQL配置"""
    print("\n=== MySQL 配置示例 ===\n")
    
    # 配置MySQL
    mysql_config = DatabaseConfig(
        type=DatabaseType.MYSQL,
        host="localhost",
        port=3306,
        database="ai_framework",
        username="root",
        password="password",
        charset="utf8mb4"
    )
    
    # 初始化数据库
    db_manager = init_database(mysql_config)
    
    # 测试连接
    if db_manager.test_connection():
        print("✅ MySQL 连接成功")
        print(f"数据库信息: {db_manager.get_database_info()}")
    else:
        print("❌ MySQL 连接失败")


def demo_sqlite():
    """演示SQLite配置"""
    print("\n=== SQLite 配置示例 ===\n")
    
    # 配置SQLite
    sqlite_config = DatabaseConfig(
        type=DatabaseType.SQLITE,
        sqlite_path="example.db"
    )
    
    # 初始化数据库
    db_manager = init_database(sqlite_config)
    
    # 测试连接
    if db_manager.test_connection():
        print("✅ SQLite 连接成功")
        print(f"数据库信息: {db_manager.get_database_info()}")
    else:
        print("❌ SQLite 连接失败")


def demo_mongodb():
    """演示MongoDB配置"""
    print("\n=== MongoDB 配置示例 ===\n")
    
    # 配置MongoDB
    mongodb_config = DatabaseConfig(
        type=DatabaseType.MONGODB,
        host="localhost",
        port=27017,
        database="ai_framework",
        username="",
        password=""
    )
    
    # 初始化数据库
    db_manager = init_database(mongodb_config)
    
    # 测试连接
    if db_manager.test_connection():
        print("✅ MongoDB 连接成功")
        print(f"数据库信息: {db_manager.get_database_info()}")
        
        # 使用MongoDB
        try:
            client = db_manager.get_mongodb_client()
            db = db_manager.get_mongodb_database()
            
            # 测试集合
            collection = db["test_collection"]
            result = collection.insert_one({"message": "Hello MongoDB!"})
            print(f"✅ MongoDB 插入成功: {result.inserted_id}")
            
        except Exception as e:
            print(f"❌ MongoDB 操作失败: {e}")
    else:
        print("❌ MongoDB 连接失败")


def demo_database_operations():
    """演示数据库操作"""
    print("\n=== 数据库操作示例 ===\n")
    
    # 使用SQLite进行演示
    sqlite_config = DatabaseConfig(
        type=DatabaseType.SQLITE,
        sqlite_path="demo.db"
    )
    
    db_manager = init_database(sqlite_config)
    
    if not db_manager.test_connection():
        print("❌ 数据库连接失败")
        return
    
    try:
        # 创建表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        with db_manager.get_session() as session:
            session.execute(create_table_sql)
            session.commit()
            print("✅ 表创建成功")
        
        # 插入数据
        insert_sql = "INSERT INTO users (name, email) VALUES (:name, :email)"
        with db_manager.get_session() as session:
            session.execute(insert_sql, {
                "name": "张三",
                "email": "zhangsan@example.com"
            })
            session.commit()
            print("✅ 数据插入成功")
        
        # 查询数据
        select_sql = "SELECT * FROM users"
        with db_manager.get_session() as session:
            result = session.execute(select_sql)
            users = result.fetchall()
            print(f"✅ 查询到 {len(users)} 条记录")
            for user in users:
                print(f"  ID: {user[0]}, 姓名: {user[1]}, 邮箱: {user[2]}")
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")


def demo_migrations():
    """演示数据库迁移"""
    print("\n=== 数据库迁移示例 ===\n")
    
    # 使用SQLite进行演示
    sqlite_config = DatabaseConfig(
        type=DatabaseType.SQLITE,
        sqlite_path="migration_demo.db"
    )
    
    db_manager = init_database(sqlite_config)
    
    if not db_manager.test_connection():
        print("❌ 数据库连接失败")
        return
    
    try:
        # 创建迁移
        migration1 = create_migration(
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
        print(f"✅ 创建迁移: {migration1.version}_{migration1.name}")
        
        migration2 = create_migration(
            name="create_posts_table",
            up_sql="""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            down_sql="DROP TABLE posts"
        )
        print(f"✅ 创建迁移: {migration2.version}_{migration2.name}")
        
        # 查看迁移状态
        print("\n📊 迁移前状态:")
        migration_status()
        
        # 执行迁移
        print("\n🔄 执行迁移:")
        migrate()
        
        # 查看迁移后状态
        print("\n📊 迁移后状态:")
        migration_status()
        
        # 回滚一个迁移
        print("\n🔄 回滚一个迁移:")
        rollback(1)
        
        # 查看回滚后状态
        print("\n📊 回滚后状态:")
        migration_status()
        
    except Exception as e:
        print(f"❌ 迁移操作失败: {e}")


def demo_connection_pooling():
    """演示连接池"""
    print("\n=== 连接池示例 ===\n")
    
    # 配置连接池
    config = DatabaseConfig(
        type=DatabaseType.SQLITE,
        sqlite_path="pool_demo.db",
        pool_size=5,
        max_overflow=10,
        pool_timeout=30
    )
    
    db_manager = init_database(config)
    
    if not db_manager.test_connection():
        print("❌ 数据库连接失败")
        return
    
    print("✅ 连接池配置成功")
    print(f"连接池大小: {config.pool_size}")
    print(f"最大溢出: {config.max_overflow}")
    print(f"连接超时: {config.pool_timeout}秒")


if __name__ == "__main__":
    print("🚀 多数据库支持示例\n")
    
    # 演示不同数据库配置
    demo_postgresql()
    demo_mysql()
    demo_sqlite()
    demo_mongodb()
    
    # 演示数据库操作
    demo_database_operations()
    
    # 演示数据库迁移
    demo_migrations()
    
    # 演示连接池
    demo_connection_pooling()
    
    print("\n✅ 示例完成！")