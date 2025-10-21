"""
数据库模块
提供多数据库支持和连接管理
"""

from typing import Generator
from sqlalchemy.orm import Session
from .connection_manager import DatabaseManager, get_database_manager, init_database
from .adapters import DatabaseAdapter, PostgreSQLAdapter, MySQLAdapter, SQLiteAdapter, MongoDBAdapter
from .exceptions import DatabaseConnectionError, DatabaseConfigurationError


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（用于FastAPI依赖注入）
    
    使用示例：
    ```python
    from fastapi import Depends
    from app.core.database import get_db
    
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()
    ```
    """
    db_manager = get_database_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


__all__ = [
    "DatabaseManager",
    "get_database_manager",
    "init_database",
    "get_db",
    "DatabaseAdapter",
    "PostgreSQLAdapter",
    "MySQLAdapter", 
    "SQLiteAdapter",
    "MongoDBAdapter",
    "DatabaseConnectionError",
    "DatabaseConfigurationError"
]