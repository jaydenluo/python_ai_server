"""
数据库适配器
支持多种数据库的适配器实现
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import sqlite3

# 可选的MongoDB依赖
try:
    import pymongo
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGODB_AVAILABLE = True
except ImportError:
    pymongo = None
    AsyncIOMotorClient = None
    MONGODB_AVAILABLE = False

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
        
        try:
            engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo
            )
            
            # 测试连接（静默）
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return engine
            
        except Exception as e:
            print(f"\n❌ PostgreSQL连接失败！")
            print(f"❌ 错误类型: {type(e).__name__}")
            print(f"❌ 错误详情: {str(e)}")
            
            # 分析具体原因
            error_msg = str(e).lower()
            if "could not translate host name" in error_msg or "nodename nor servname provided" in error_msg:
                print(f"\n💡 原因分析: 主机名 '{self.config.host}' 无法解析")
                print(f"   - 'local' 不是有效的主机名")
                print(f"   - 应该使用 'localhost' 或 '127.0.0.1'")
            elif "connection refused" in error_msg:
                print(f"\n💡 原因分析: PostgreSQL服务未启动或端口不正确")
                print(f"   - 检查PostgreSQL是否在 {self.config.host}:{self.config.port} 运行")
                print(f"   - Windows: net start postgresql-x64-[版本]")
                print(f"   - 或检查端口号是否正确")
            elif "password authentication failed" in error_msg or "role" in error_msg:
                print(f"\n💡 原因分析: 用户名或密码错误")
                print(f"   - PostgreSQL默认用户通常是 'postgres'，不是 'root'")
                print(f"   - 请检查用户名和密码是否正确")
            elif "database" in error_msg and "does not exist" in error_msg:
                print(f"\n💡 原因分析: 数据库 '{self.config.database}' 不存在")
                print(f"   - 需要先创建数据库")
                print(f"   - 命令: CREATE DATABASE {self.config.database};")
            elif "timeout" in error_msg:
                print(f"\n💡 原因分析: 连接超时")
                print(f"   - 网络问题或数据库响应慢")
                print(f"   - 检查防火墙设置")
            else:
                print(f"\n💡 未知错误，请检查上述错误详情")
            
            raise


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
    }
    
    # 只有安装了MongoDB依赖时才支持MongoDB
    if MONGODB_AVAILABLE:
        adapter_map[DatabaseType.MONGODB] = MongoDBAdapter
    
    adapter_class = adapter_map.get(config.type)
    if not adapter_class:
        if config.type == DatabaseType.MONGODB and not MONGODB_AVAILABLE:
            raise DatabaseConfigurationError(
                "MongoDB支持需要安装pymongo和motor依赖。"
                "请运行: pip install pymongo motor"
            )
        raise DatabaseConfigurationError(f"不支持的数据库类型: {config.type}")
    
    return adapter_class(config)