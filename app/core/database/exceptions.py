"""
数据库异常类
"""


class DatabaseError(Exception):
    """数据库基础异常"""
    pass


class DatabaseConnectionError(DatabaseError):
    """数据库连接异常"""
    pass


class DatabaseConfigurationError(DatabaseError):
    """数据库配置异常"""
    pass


class DatabaseQueryError(DatabaseError):
    """数据库查询异常"""
    pass


class DatabaseMigrationError(DatabaseError):
    """数据库迁移异常"""
    pass