"""
数据库适配器
支持多种数据库的适配器实现
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import sqlite3
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config.settings import DatabaseConfig, DatabaseType
from .exceptions import DatabaseConnectionError, DatabaseConfigurationError


class DatabaseAdapter(ABC):
    """数据库适配器基类"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
    
    @abstractmethod
    def create_connection_string(self) -> str:
        """创建连接字符串"""
        pass
    
    @abstractmethod
    def create_engine(self) -> Engine:
        """创建数据库引擎"""
        pass
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        if not self._session_factory:
            self._engine = self.create_engine()
            self._session_factory = sessionmaker(bind=self._engine)
        return self._session_factory()
    
    def close(self):
        """关闭连接"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL适配器"""
    
    def create_connection_string(self) -> str:
        """创建PostgreSQL连接字符串"""
        return (
            f"postgresql://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )
    
    def create_engine(self) -> Engine:
        """创建PostgreSQL引擎"""
        connection_string = self.create_connection_string()
        
        return create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            echo=self.config.echo
        )


class MySQLAdapter(DatabaseAdapter):
    """MySQL适配器"""
    
    def create_connection_string(self) -> str:
        """创建MySQL连接字符串"""
        return (
            f"mysql+pymysql://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
            f"?charset={self.config.charset}"
        )
    
    def create_engine(self) -> Engine:
        """创建MySQL引擎"""
        connection_string = self.create_connection_string()
        
        return create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            echo=self.config.echo
        )


class SQLiteAdapter(DatabaseAdapter):
    """SQLite适配器"""
    
    def create_connection_string(self) -> str:
        """创建SQLite连接字符串"""
        return f"sqlite:///{self.config.sqlite_path}"
    
    def create_engine(self) -> Engine:
        """创建SQLite引擎"""
        connection_string = self.create_connection_string()
        
        return create_engine(
            connection_string,
            echo=self.config.echo,
            # SQLite 特殊配置
            connect_args={"check_same_thread": False}
        )


class MongoDBAdapter(DatabaseAdapter):
    """MongoDB适配器"""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self._client: Optional[AsyncIOMotorClient] = None
        self._database = None
    
    def create_connection_string(self) -> str:
        """创建MongoDB连接字符串"""
        if self.config.username and self.config.password:
            return (
                f"mongodb://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.database}"
                f"?authSource={self.config.mongodb_auth_source}"
                f"&authMechanism={self.config.mongodb_auth_mechanism}"
            )
        else:
            return f"mongodb://{self.config.host}:{self.config.port}/{self.config.database}"
    
    def create_engine(self) -> Engine:
        """MongoDB不使用SQLAlchemy引擎"""
        raise NotImplementedError("MongoDB使用原生客户端，不需要SQLAlchemy引擎")
    
    def get_client(self) -> AsyncIOMotorClient:
        """获取MongoDB客户端"""
        if not self._client:
            connection_string = self.create_connection_string()
            self._client = AsyncIOMotorClient(connection_string)
        return self._client
    
    def get_database(self):
        """获取MongoDB数据库"""
        if not self._database:
            client = self.get_client()
            self._database = client[self.config.database]
        return self._database
    
    def close(self):
        """关闭MongoDB连接"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None


class MariaDBAdapter(MySQLAdapter):
    """MariaDB适配器（继承MySQL适配器）"""
    
    def create_connection_string(self) -> str:
        """创建MariaDB连接字符串"""
        return (
            f"mysql+pymysql://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
            f"?charset={self.config.charset}"
        )


class OracleAdapter(DatabaseAdapter):
    """Oracle适配器"""
    
    def create_connection_string(self) -> str:
        """创建Oracle连接字符串"""
        return (
            f"oracle+cx_oracle://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )
    
    def create_engine(self) -> Engine:
        """创建Oracle引擎"""
        connection_string = self.create_connection_string()
        
        return create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            echo=self.config.echo
        )


class SQLServerAdapter(DatabaseAdapter):
    """SQL Server适配器"""
    
    def create_connection_string(self) -> str:
        """创建SQL Server连接字符串"""
        return (
            f"mssql+pyodbc://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
            f"?driver=ODBC+Driver+17+for+SQL+Server"
        )
    
    def create_engine(self) -> Engine:
        """创建SQL Server引擎"""
        connection_string = self.create_connection_string()
        
        return create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            echo=self.config.echo
        )


def create_adapter(config: DatabaseConfig) -> DatabaseAdapter:
    """根据配置创建相应的数据库适配器"""
    adapter_map = {
        DatabaseType.POSTGRESQL: PostgreSQLAdapter,
        DatabaseType.MYSQL: MySQLAdapter,
        DatabaseType.MARIADB: MariaDBAdapter,
        DatabaseType.SQLITE: SQLiteAdapter,
        DatabaseType.ORACLE: OracleAdapter,
        DatabaseType.SQLSERVER: SQLServerAdapter,
        DatabaseType.MONGODB: MongoDBAdapter,
    }
    
    adapter_class = adapter_map.get(config.type)
    if not adapter_class:
        raise DatabaseConfigurationError(f"不支持的数据库类型: {config.type}")
    
    return adapter_class(config)