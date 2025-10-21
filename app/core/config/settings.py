"""
配置管理
提供环境配置、动态配置等功能
"""

import os
import yaml
import json
from typing import Any, Dict, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class Environment(Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseType(Enum):
    """数据库类型枚举"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MARIADB = "mariadb"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"
    MONGODB = "mongodb"


@dataclass
class DatabaseConfig:
    """数据库配置"""
    # 数据库类型
    type: DatabaseType = DatabaseType.POSTGRESQL
    
    # 连接配置
    host: str = "localhost"
    port: int = 5432
    database: str = "ai_framework"
    username: str = "postgres"
    password: str = ""
    
    # 连接池配置
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # 其他配置
    echo: bool = False
    charset: str = "utf8mb4"
    collation: str = "utf8mb4_unicode_ci"
    
    # 迁移配置
    auto_migrate: bool = True  # 是否自动执行迁移
    
    # SQLite 特殊配置
    sqlite_path: str = "database.db"
    
    # MongoDB 特殊配置
    mongodb_auth_source: str = "admin"
    mongodb_auth_mechanism: str = "SCRAM-SHA-1"


@dataclass
class RedisConfig:
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    decode_responses: bool = True


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration: int = 300  # 5分钟


@dataclass
class AIConfig:
    """AI配置"""
    model_storage_path: str = "./models"
    max_model_size: int = 1024 * 1024 * 1024  # 1GB
    supported_formats: list = field(default_factory=lambda: ["pkl", "joblib", "onnx", "pt"])
    inference_timeout: int = 30
    max_batch_size: int = 100


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class RateLimitConfig:
    """限流配置"""
    enabled: bool = True
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 100


class Config:
    """配置管理类"""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        # 加载默认配置
        self._load_default_config()
        
        # 加载环境配置
        self._load_environment_config()
        
        # 加载文件配置
        self._load_file_config()
    
    def _load_default_config(self):
        """加载默认配置"""
        self._config = {
            "app": {
                "name": "AI Framework",
                "version": "1.0.0",
                "debug": self.environment == Environment.DEVELOPMENT,
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 1
            },
            "database": DatabaseConfig(),
            "redis": RedisConfig(),
            "security": SecurityConfig(),
            "ai": AIConfig(),
            "logging": LoggingConfig(),
            "rate_limit": RateLimitConfig()
        }
    
    def _load_environment_config(self):
        """加载环境变量配置（简化版，仅支持必要的环境变量）"""
        # 只保留必要的环境变量支持
        if os.getenv("ENVIRONMENT"):
            env = os.getenv("ENVIRONMENT").lower()
            if env in ["development", "testing", "staging", "production"]:
                self.environment = Environment(env)
        
        # 数据库密码（如果设置了环境变量）
        if os.getenv("DB_PASSWORD"):
            self._config["database"].password = os.getenv("DB_PASSWORD")
        
        # Redis密码（如果设置了环境变量）
        if os.getenv("REDIS_PASSWORD"):
            self._config["redis"].password = os.getenv("REDIS_PASSWORD")
        
        # 安全密钥（如果设置了环境变量）
        if os.getenv("SECRET_KEY"):
            self._config["security"].secret_key = os.getenv("SECRET_KEY")
    
    def _load_file_config(self):
        """加载文件配置"""
        config_files = [
            "config.yaml",
            "config.yml",
            "config.json",
            f"config_{self.environment.value}.yaml",
            f"config_{self.environment.value}.yml",
            f"config_{self.environment.value}.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                self._load_config_file(config_file)
                break
    
    def _load_config_file(self, file_path: str):
        """加载配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    file_config = json.load(f)
                else:
                    file_config = yaml.safe_load(f)
                
                # 合并配置
                self._merge_config(self._config, file_config)
        except Exception as e:
            print(f"Warning: Failed to load config file {file_path}: {e}")
    
    def _merge_config(self, base_config: Dict, new_config: Dict):
        """合并配置"""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                # 特殊处理数据库配置
                if key == "database" and isinstance(value, dict):
                    # 将字典转换为DatabaseConfig对象
                    db_config = base_config[key]
                    if isinstance(db_config, DatabaseConfig):
                        # 更新现有DatabaseConfig对象的属性
                        for attr_name, attr_value in value.items():
                            if hasattr(db_config, attr_name):
                                # 处理特殊类型转换
                                if attr_name == "type" and isinstance(attr_value, str):
                                    try:
                                        attr_value = DatabaseType(attr_value)
                                    except ValueError:
                                        pass  # 保持原值
                                setattr(db_config, attr_name, attr_value)
                    else:
                        base_config[key] = value
                else:
                    base_config[key] = value
    
    def _parse_database_url(self, url: str) -> DatabaseConfig:
        """解析数据库URL"""
        # 支持的URL格式:
        # postgresql://user:password@host:port/database
        # mysql://user:password@host:port/database
        # sqlite:///path/to/database.db
        # mongodb://user:password@host:port/database
        
        if url.startswith("postgresql://"):
            return self._parse_postgresql_url(url)
        elif url.startswith("mysql://"):
            return self._parse_mysql_url(url)
        elif url.startswith("sqlite://"):
            return self._parse_sqlite_url(url)
        elif url.startswith("mongodb://"):
            return self._parse_mongodb_url(url)
        else:
            # 默认按PostgreSQL解析
            return self._parse_postgresql_url(f"postgresql://{url}")
    
    def _parse_postgresql_url(self, url: str) -> DatabaseConfig:
        """解析PostgreSQL URL"""
        url = url[13:]  # 移除 postgresql:// 前缀
        
        if "@" in url:
            auth, host_db = url.split("@", 1)
            if ":" in auth:
                username, password = auth.split(":", 1)
            else:
                username, password = auth, ""
        else:
            username, password = "", ""
            host_db = url
        
        if "/" in host_db:
            host_port, database = host_db.split("/", 1)
        else:
            host_port, database = host_db, ""
        
        if ":" in host_port:
            host, port = host_port.split(":", 1)
            port = int(port)
        else:
            host, port = host_port, 5432
        
        return DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host=host,
            port=port,
            database=database,
            username=username,
            password=password
        )
    
    def _parse_mysql_url(self, url: str) -> DatabaseConfig:
        """解析MySQL URL"""
        url = url[8:]  # 移除 mysql:// 前缀
        
        if "@" in url:
            auth, host_db = url.split("@", 1)
            if ":" in auth:
                username, password = auth.split(":", 1)
            else:
                username, password = auth, ""
        else:
            username, password = "", ""
            host_db = url
        
        if "/" in host_db:
            host_port, database = host_db.split("/", 1)
        else:
            host_port, database = host_db, ""
        
        if ":" in host_port:
            host, port = host_port.split(":", 1)
            port = int(port)
        else:
            host, port = host_port, 3306
        
        return DatabaseConfig(
            type=DatabaseType.MYSQL,
            host=host,
            port=port,
            database=database,
            username=username,
            password=password
        )
    
    def _parse_sqlite_url(self, url: str) -> DatabaseConfig:
        """解析SQLite URL"""
        # 格式: sqlite:///path/to/database.db
        path = url[10:]  # 移除 sqlite:/// 前缀
        return DatabaseConfig(
            type=DatabaseType.SQLITE,
            sqlite_path=path
        )
    
    def _parse_mongodb_url(self, url: str) -> DatabaseConfig:
        """解析MongoDB URL"""
        url = url[10:]  # 移除 mongodb:// 前缀
        
        if "@" in url:
            auth, host_db = url.split("@", 1)
            if ":" in auth:
                username, password = auth.split(":", 1)
            else:
                username, password = auth, ""
        else:
            username, password = "", ""
            host_db = url
        
        if "/" in host_db:
            host_port, database = host_db.split("/", 1)
        else:
            host_port, database = host_db, ""
        
        if ":" in host_port:
            host, port = host_port.split(":", 1)
            port = int(port)
        else:
            host, port = host_port, 27017
        
        return DatabaseConfig(
            type=DatabaseType.MONGODB,
            host=host,
            port=port,
            database=database,
            username=username,
            password=password
        )
    
    def _parse_redis_url(self, url: str) -> RedisConfig:
        """解析Redis URL"""
        # 格式: redis://[:password]@host:port/db
        if url.startswith("redis://"):
            url = url[8:]  # 移除协议前缀
        
        if "@" in url:
            auth, host_port_db = url.split("@", 1)
            password = auth if auth else None
        else:
            password = None
            host_port_db = url
        
        if "/" in host_port_db:
            host_port, db = host_port_db.split("/", 1)
            db = int(db)
        else:
            host_port, db = host_port_db, 0
        
        if ":" in host_port:
            host, port = host_port.split(":", 1)
            port = int(port)
        else:
            host, port = host_port, 6379
        
        return RedisConfig(
            host=host,
            port=port,
            password=password,
            db=db
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self._config["database"]
    
    def get_redis_config(self) -> RedisConfig:
        """获取Redis配置"""
        return self._config["redis"]
    
    def get_security_config(self) -> SecurityConfig:
        """获取安全配置"""
        return self._config["security"]
    
    def get_ai_config(self) -> AIConfig:
        """获取AI配置"""
        return self._config["ai"]
    
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        return self._config["logging"]
    
    def get_rate_limit_config(self) -> RateLimitConfig:
        """获取限流配置"""
        return self._config["rate_limit"]
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.environment == Environment.TESTING


# 全局配置实例
config = Config(Environment(os.getenv("ENVIRONMENT", "development")))