"""
数据库连接管理器
提供统一的数据库连接管理
"""

from typing import Optional, Dict, Any
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config.settings import config, DatabaseConfig
from app.core.database.adapters import create_adapter, DatabaseAdapter
from app.core.database.exceptions import DatabaseConnectionError, DatabaseConfigurationError


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_config: Optional[DatabaseConfig] = None):
        self.config = db_config or config.get_database_config()
        self._adapter: Optional[DatabaseAdapter] = None
        self._connected = False
    
    def get_adapter(self) -> DatabaseAdapter:
        """获取数据库适配器"""
        if not self._adapter:
            try:
                self._adapter = create_adapter(self.config)
                self._connected = True
            except Exception as e:
                raise DatabaseConnectionError(f"无法创建数据库适配器: {e}")
        return self._adapter
    
    def connect(self):
        """建立数据库连接"""
        if not self._connected:
            adapter = self.get_adapter()
            try:
                # 测试连接
                if hasattr(adapter, 'get_session'):
                    with adapter.get_session() as session:
                        session.execute(text("SELECT 1"))
                elif hasattr(adapter, 'get_client'):
                    # MongoDB 连接测试
                    client = adapter.get_client()
                    client.admin.command('ping')
                self._connected = True
            except Exception as e:
                raise DatabaseConnectionError(f"数据库连接失败: {e}")
    
    def disconnect(self):
        """断开数据库连接"""
        if self._adapter:
            self._adapter.close()
            self._adapter = None
            self._connected = False
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected
    
    @contextmanager
    def get_session(self):
        """获取数据库会话（上下文管理器）"""
        if not self._connected:
            self.connect()
        
        adapter = self.get_adapter()
        if not hasattr(adapter, 'get_session'):
            raise DatabaseConnectionError("当前数据库类型不支持SQL会话")
        
        session = adapter.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_mongodb_client(self):
        """获取MongoDB客户端"""
        if not self._connected:
            self.connect()
        
        adapter = self.get_adapter()
        if not hasattr(adapter, 'get_client'):
            raise DatabaseConnectionError("当前数据库类型不是MongoDB")
        
        return adapter.get_client()
    
    def get_mongodb_database(self):
        """获取MongoDB数据库"""
        if not self._connected:
            self.connect()
        
        adapter = self.get_adapter()
        if not hasattr(adapter, 'get_database'):
            raise DatabaseConnectionError("当前数据库类型不是MongoDB")
        
        return adapter.get_database()
    
    def execute_raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None):
        """执行原生SQL"""
        with self.get_session() as session:
            return session.execute(text(sql), params or {})
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        adapter = self.get_adapter()
        return {
            "type": self.config.type.value,
            "host": getattr(self.config, 'host', 'N/A'),
            "port": getattr(self.config, 'port', 'N/A'),
            "database": getattr(self.config, 'database', 'N/A'),
            "username": getattr(self.config, 'username', 'N/A'),
            "connected": self._connected,
            "adapter": adapter.__class__.__name__
        }
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            self.connect()
            return True
        except Exception:
            return False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()


# 全局数据库管理器实例
_database_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """获取全局数据库管理器实例"""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager


def init_database(config: Optional[DatabaseConfig] = None):
    """初始化数据库"""
    global _database_manager
    _database_manager = DatabaseManager(config)
    return _database_manager


def close_database():
    """关闭数据库连接"""
    global _database_manager
    if _database_manager:
        _database_manager.disconnect()
        _database_manager = None