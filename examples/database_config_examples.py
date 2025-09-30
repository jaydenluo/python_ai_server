"""
数据库配置示例
展示不同数据库的配置方法
"""

from app.core.config.settings import DatabaseConfig, DatabaseType
from app.core.database import init_database, get_database_manager


def example_postgresql():
    """PostgreSQL 配置示例"""
    print("=== PostgreSQL 配置示例 ===")
    
    # 方式1: 直接配置
    config = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="ai_framework",
        username="postgres",
        password="password",
        pool_size=10,
        max_overflow=20
    )
    
    # 方式2: 使用URL
    # config = DatabaseConfig()
    # config._parse_database_url("postgresql://postgres:password@localhost:5432/ai_framework")
    
    db_manager = init_database(config)
    print(f"PostgreSQL 配置: {db_manager.get_database_info()}")


def example_mysql():
    """MySQL 配置示例"""
    print("\n=== MySQL 配置示例 ===")
    
    config = DatabaseConfig(
        type=DatabaseType.MYSQL,
        host="localhost",
        port=3306,
        database="ai_framework",
        username="root",
        password="password",
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci"
    )
    
    db_manager = init_database(config)
    print(f"MySQL 配置: {db_manager.get_database_info()}")


def example_sqlite():
    """SQLite 配置示例"""
    print("\n=== SQLite 配置示例 ===")
    
    config = DatabaseConfig(
        type=DatabaseType.SQLITE,
        sqlite_path="example.db"
    )
    
    db_manager = init_database(config)
    print(f"SQLite 配置: {db_manager.get_database_info()}")


def example_mongodb():
    """MongoDB 配置示例"""
    print("\n=== MongoDB 配置示例 ===")
    
    config = DatabaseConfig(
        type=DatabaseType.MONGODB,
        host="localhost",
        port=27017,
        database="ai_framework",
        username="",
        password="",
        mongodb_auth_source="admin",
        mongodb_auth_mechanism="SCRAM-SHA-1"
    )
    
    db_manager = init_database(config)
    print(f"MongoDB 配置: {db_manager.get_database_info()}")


def example_connection_pooling():
    """连接池配置示例"""
    print("\n=== 连接池配置示例 ===")
    
    # 高并发配置
    high_concurrency_config = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="ai_framework",
        username="postgres",
        password="password",
        pool_size=50,        # 大连接池
        max_overflow=100,    # 大溢出
        pool_timeout=120,    # 长超时
        pool_recycle=7200    # 长回收时间
    )
    
    # 低资源配置
    low_resource_config = DatabaseConfig(
        type=DatabaseType.SQLITE,
        sqlite_path="low_resource.db",
        pool_size=1,         # 小连接池
        max_overflow=0,      # 无溢出
        pool_timeout=10      # 短超时
    )
    
    print("高并发配置:")
    print(f"  连接池大小: {high_concurrency_config.pool_size}")
    print(f"  最大溢出: {high_concurrency_config.max_overflow}")
    print(f"  连接超时: {high_concurrency_config.pool_timeout}秒")
    
    print("\n低资源配置:")
    print(f"  连接池大小: {low_resource_config.pool_size}")
    print(f"  最大溢出: {low_resource_config.max_overflow}")
    print(f"  连接超时: {low_resource_config.pool_timeout}秒")


def example_environment_configs():
    """环境配置示例"""
    print("\n=== 环境配置示例 ===")
    
    # 开发环境
    dev_config = DatabaseConfig(
        type=DatabaseType.SQLITE,
        sqlite_path="dev.db",
        echo=True  # 开发时显示SQL
    )
    
    # 测试环境
    test_config = DatabaseConfig(
        type=DatabaseType.SQLITE,
        sqlite_path="test.db",
        echo=False
    )
    
    # 生产环境
    prod_config = DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="prod-db.example.com",
        port=5432,
        database="ai_framework",
        username="app_user",
        password="secure_password",
        pool_size=20,
        max_overflow=50,
        echo=False
    )
    
    print("开发环境: SQLite + 调试模式")
    print("测试环境: SQLite + 静默模式")
    print("生产环境: PostgreSQL + 连接池")


if __name__ == "__main__":
    print("🚀 数据库配置示例\n")
    
    example_postgresql()
    example_mysql()
    example_sqlite()
    example_mongodb()
    example_connection_pooling()
    example_environment_configs()
    
    print("\n✅ 配置示例完成！")