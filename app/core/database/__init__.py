"""
数据库模块
提供多数据库支持和连接管理
"""

from .connection_manager import DatabaseManager, get_database_manager
from .adapters import DatabaseAdapter, PostgreSQLAdapter, MySQLAdapter, SQLiteAdapter, MongoDBAdapter
from .exceptions import DatabaseConnectionError, DatabaseConfigurationError

__all__ = [
    "DatabaseManager",
    "get_database_manager", 
    "DatabaseAdapter",
    "PostgreSQLAdapter",
    "MySQLAdapter", 
    "SQLiteAdapter",
    "MongoDBAdapter",
    "DatabaseConnectionError",
    "DatabaseConfigurationError"
]