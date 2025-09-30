"""
基于Alembic的数据库迁移系统
集成SQLAlchemy官方迁移工具
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext

from app.core.database.connection_manager import get_database_manager
from app.core.database.exceptions import DatabaseMigrationError


class AlembicMigrationManager:
    """基于Alembic的迁移管理器"""
    
    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = Path(migrations_dir)
        self.db_manager = get_database_manager()
        self.alembic_cfg = self._setup_alembic_config()
    
    def _setup_alembic_config(self) -> Config:
        """设置Alembic配置"""
        # 创建迁移目录
        self.migrations_dir.mkdir(exist_ok=True)
        
        # 创建alembic.ini文件
        alembic_ini_path = self.migrations_dir / "alembic.ini"
        if not alembic_ini_path.exists():
            self._create_alembic_ini(alembic_ini_path)
        
        # 创建alembic配置
        alembic_cfg = Config(str(alembic_ini_path))
        
        # 设置数据库URL
        db_url = self._get_database_url()
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        # 设置脚本位置
        alembic_cfg.set_main_option("script_location", str(self.migrations_dir))
        
        return alembic_cfg
    
    def _create_alembic_ini(self, ini_path: Path):
        """创建alembic.ini配置文件"""
        ini_content = f"""[alembic]
# 迁移脚本位置
script_location = {self.migrations_dir}

# 数据库URL (会被动态设置)
sqlalchemy.url = 

# 日志配置
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        with open(ini_path, 'w', encoding='utf-8') as f:
            f.write(ini_content)
    
    def _get_database_url(self) -> str:
        """获取数据库连接URL"""
        config = self.db_manager.config
        
        if config.type.value == "postgresql":
            return f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        elif config.type.value == "mysql":
            return f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        elif config.type.value == "sqlite":
            return f"sqlite:///{config.sqlite_path}"
        else:
            raise DatabaseMigrationError(f"不支持的数据库类型: {config.type}")
    
    def init_migrations(self):
        """初始化迁移环境"""
        try:
            # 初始化Alembic
            command.init(self.alembic_cfg, str(self.migrations_dir))
            print("✅ Alembic迁移环境初始化成功")
        except Exception as e:
            raise DatabaseMigrationError(f"初始化迁移环境失败: {e}")
    
    def create_migration(self, message: str, autogenerate: bool = True) -> str:
        """创建迁移"""
        try:
            if autogenerate:
                # 自动生成迁移
                command.revision(
                    self.alembic_cfg,
                    message=message,
                    autogenerate=True
                )
            else:
                # 创建空迁移
                command.revision(
                    self.alembic_cfg,
                    message=message
                )
            
            print(f"✅ 迁移创建成功: {message}")
            return message
        except Exception as e:
            raise DatabaseMigrationError(f"创建迁移失败: {e}")
    
    def upgrade(self, revision: str = "head"):
        """执行迁移"""
        try:
            command.upgrade(self.alembic_cfg, revision)
            print(f"✅ 迁移执行成功: {revision}")
        except Exception as e:
            raise DatabaseMigrationError(f"执行迁移失败: {e}")
    
    def downgrade(self, revision: str = "-1"):
        """回滚迁移"""
        try:
            command.downgrade(self.alembic_cfg, revision)
            print(f"✅ 迁移回滚成功: {revision}")
        except Exception as e:
            raise DatabaseMigrationError(f"回滚迁移失败: {e}")
    
    def get_current_revision(self) -> Optional[str]:
        """获取当前版本"""
        try:
            with self.db_manager.get_session() as session:
                context = MigrationContext.configure(session.connection())
                return context.get_current_revision()
        except Exception:
            return None
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """获取迁移历史"""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            revisions = []
            
            for revision in script.walk_revisions():
                revisions.append({
                    "revision": revision.revision,
                    "down_revision": revision.down_revision,
                    "branch_labels": revision.branch_labels,
                    "depends_on": revision.depends_on,
                    "comment": revision.comment
                })
            
            return revisions
        except Exception as e:
            raise DatabaseMigrationError(f"获取迁移历史失败: {e}")
    
    def status(self):
        """显示迁移状态"""
        try:
            current_revision = self.get_current_revision()
            script = ScriptDirectory.from_config(self.alembic_cfg)
            head_revision = script.get_current_head()
            
            print("📊 Alembic迁移状态:")
            print(f"当前版本: {current_revision or '无'}")
            print(f"最新版本: {head_revision or '无'}")
            
            if current_revision == head_revision:
                print("✅ 数据库已是最新版本")
            else:
                print("⏳ 有待应用的迁移")
            
            print("\n📋 迁移历史:")
            history = self.get_migration_history()
            for migration in history:
                status = "✅ 已应用" if migration["revision"] == current_revision else "⏳ 待应用"
                print(f"  {migration['revision']}: {migration['comment']} - {status}")
                
        except Exception as e:
            print(f"❌ 获取迁移状态失败: {e}")
    
    def stamp(self, revision: str = "head"):
        """标记当前版本（不执行迁移）"""
        try:
            command.stamp(self.alembic_cfg, revision)
            print(f"✅ 版本标记成功: {revision}")
        except Exception as e:
            raise DatabaseMigrationError(f"标记版本失败: {e}")


# 全局Alembic迁移管理器
_alembic_manager: Optional[AlembicMigrationManager] = None


def get_alembic_manager() -> AlembicMigrationManager:
    """获取Alembic迁移管理器"""
    global _alembic_manager
    if _alembic_manager is None:
        _alembic_manager = AlembicMigrationManager()
    return _alembic_manager


def init_alembic_migrations():
    """初始化Alembic迁移"""
    manager = get_alembic_manager()
    manager.init_migrations()


def create_alembic_migration(message: str, autogenerate: bool = True):
    """创建Alembic迁移"""
    manager = get_alembic_manager()
    return manager.create_migration(message, autogenerate)


def upgrade_alembic(revision: str = "head"):
    """执行Alembic迁移"""
    manager = get_alembic_manager()
    manager.upgrade(revision)


def downgrade_alembic(revision: str = "-1"):
    """回滚Alembic迁移"""
    manager = get_alembic_manager()
    manager.downgrade(revision)


def alembic_status():
    """显示Alembic迁移状态"""
    manager = get_alembic_manager()
    manager.status()