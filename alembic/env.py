from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入我们的模型和数据库配置
from app.core.database.connection_manager import get_database_manager
from app.core.models.base import Base
from app.models import *  # 导入所有模型
from app.models.entities import *
from app.models.entities.system import *
from app.models.entities.common import *
from app.models.entities.business import *

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置目标元数据
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # 直接从 config.yaml 获取数据库配置
    try:
        from app.core.config.settings import config
        db_config = config.get_database_config()
        
        # 构建连接URL
        if db_config.type.value == 'postgresql':
            url = f"postgresql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
        elif db_config.type.value == 'mysql':
            url = f"mysql+pymysql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
        elif db_config.type.value == 'sqlite':
            url = f"sqlite:///{db_config.sqlite_path}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_config.type.value}")
            
    except Exception as e:
        print(f"❌ 无法获取数据库配置: {e}")
        return
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # 直接从 config.yaml 获取数据库配置并创建引擎
    try:
        from app.core.config.settings import config
        db_config = config.get_database_config()
        
        # 构建连接URL
        if db_config.type.value == 'postgresql':
            url = f"postgresql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
        elif db_config.type.value == 'mysql':
            url = f"mysql+pymysql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
        elif db_config.type.value == 'sqlite':
            url = f"sqlite:///{db_config.sqlite_path}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_config.type.value}")
            
        # 创建引擎
        engine = engine_from_config(
            {"sqlalchemy.url": url},
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        
    except Exception as e:
        print(f"❌ 无法获取数据库配置: {e}")
        return

    with engine.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
