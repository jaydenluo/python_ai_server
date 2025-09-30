"""
数据库迁移系统
支持多种数据库的迁移管理
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from app.core.database.connection_manager import get_database_manager
from app.core.database.exceptions import DatabaseMigrationError


class Migration:
    """迁移类"""
    
    def __init__(self, version: str, name: str, up_sql: str, down_sql: str = ""):
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "version": self.version,
            "name": self.name,
            "up_sql": self.up_sql,
            "down_sql": self.down_sql,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Migration':
        """从字典创建迁移"""
        migration = cls(
            version=data["version"],
            name=data["name"],
            up_sql=data["up_sql"],
            down_sql=data.get("down_sql", "")
        )
        migration.created_at = datetime.fromisoformat(data["created_at"])
        return migration


class MigrationManager:
    """迁移管理器"""
    
    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(exist_ok=True)
        self.db_manager = get_database_manager()
    
    def create_migration(self, name: str, up_sql: str, down_sql: str = "") -> Migration:
        """创建迁移"""
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        migration = Migration(version, name, up_sql, down_sql)
        
        # 保存迁移文件
        migration_file = self.migrations_dir / f"{version}_{name}.json"
        with open(migration_file, 'w', encoding='utf-8') as f:
            json.dump(migration.to_dict(), f, ensure_ascii=False, indent=2)
        
        return migration
    
    def load_migrations(self) -> List[Migration]:
        """加载所有迁移"""
        migrations = []
        
        for migration_file in self.migrations_dir.glob("*.json"):
            try:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    migrations.append(Migration.from_dict(data))
            except Exception as e:
                print(f"警告: 无法加载迁移文件 {migration_file}: {e}")
        
        # 按版本排序
        migrations.sort(key=lambda m: m.version)
        return migrations
    
    def get_applied_migrations(self) -> List[str]:
        """获取已应用的迁移版本"""
        with self.db_manager.get_session() as session:
            # 检查迁移表是否存在
            if not self._migration_table_exists(session):
                self._create_migration_table(session)
            
            result = session.execute(text("SELECT version FROM migrations ORDER BY version"))
            return [row[0] for row in result.fetchall()]
    
    def _migration_table_exists(self, session: Session) -> bool:
        """检查迁移表是否存在"""
        inspector = inspect(session.bind)
        tables = inspector.get_table_names()
        return "migrations" in tables
    
    def _create_migration_table(self, session: Session):
        """创建迁移表"""
        # 根据数据库类型创建不同的迁移表
        db_type = self.db_manager.config.type.value
        
        if db_type == "postgresql":
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        elif db_type == "mysql":
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                version VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        elif db_type == "sqlite":
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            # 默认使用通用SQL
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY,
                version VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        
        session.execute(text(create_table_sql))
        session.commit()
    
    def apply_migration(self, migration: Migration):
        """应用迁移"""
        with self.db_manager.get_session() as session:
            try:
                # 执行迁移SQL
                if migration.up_sql:
                    session.execute(text(migration.up_sql))
                
                # 记录迁移
                session.execute(text(
                    "INSERT INTO migrations (version, name) VALUES (:version, :name)"
                ), {"version": migration.version, "name": migration.name})
                
                session.commit()
                print(f"✅ 迁移 {migration.version}_{migration.name} 应用成功")
                
            except Exception as e:
                session.rollback()
                raise DatabaseMigrationError(f"迁移 {migration.version}_{migration.name} 应用失败: {e}")
    
    def rollback_migration(self, migration: Migration):
        """回滚迁移"""
        with self.db_manager.get_session() as session:
            try:
                # 执行回滚SQL
                if migration.down_sql:
                    session.execute(text(migration.down_sql))
                
                # 删除迁移记录
                session.execute(text(
                    "DELETE FROM migrations WHERE version = :version"
                ), {"version": migration.version})
                
                session.commit()
                print(f"✅ 迁移 {migration.version}_{migration.name} 回滚成功")
                
            except Exception as e:
                session.rollback()
                raise DatabaseMigrationError(f"迁移 {migration.version}_{migration.name} 回滚失败: {e}")
    
    def migrate(self):
        """执行所有未应用的迁移"""
        migrations = self.load_migrations()
        applied_migrations = self.get_applied_migrations()
        
        pending_migrations = [
            m for m in migrations 
            if m.version not in applied_migrations
        ]
        
        if not pending_migrations:
            print("✅ 所有迁移都已应用")
            return
        
        print(f"📦 发现 {len(pending_migrations)} 个待应用迁移")
        
        for migration in pending_migrations:
            print(f"🔄 应用迁移: {migration.version}_{migration.name}")
            self.apply_migration(migration)
    
    def rollback(self, steps: int = 1):
        """回滚指定数量的迁移"""
        migrations = self.load_migrations()
        applied_migrations = self.get_applied_migrations()
        
        # 获取已应用的迁移
        applied_migration_objects = [
            m for m in migrations 
            if m.version in applied_migrations
        ]
        
        # 按版本倒序排列，回滚最新的迁移
        applied_migration_objects.sort(key=lambda m: m.version, reverse=True)
        
        rollback_count = min(steps, len(applied_migration_objects))
        
        if rollback_count == 0:
            print("✅ 没有可回滚的迁移")
            return
        
        print(f"🔄 回滚 {rollback_count} 个迁移")
        
        for i in range(rollback_count):
            migration = applied_migration_objects[i]
            print(f"🔄 回滚迁移: {migration.version}_{migration.name}")
            self.rollback_migration(migration)
    
    def status(self):
        """显示迁移状态"""
        migrations = self.load_migrations()
        applied_migrations = self.get_applied_migrations()
        
        print("📊 迁移状态:")
        print(f"总迁移数: {len(migrations)}")
        print(f"已应用: {len(applied_migrations)}")
        print(f"待应用: {len(migrations) - len(applied_migrations)}")
        print()
        
        print("📋 迁移列表:")
        for migration in migrations:
            status = "✅ 已应用" if migration.version in applied_migrations else "⏳ 待应用"
            print(f"  {migration.version}_{migration.name} - {status}")


# 全局迁移管理器实例
_migration_manager: Optional[MigrationManager] = None


def get_migration_manager() -> MigrationManager:
    """获取全局迁移管理器实例"""
    global _migration_manager
    if _migration_manager is None:
        _migration_manager = MigrationManager()
    return _migration_manager


def create_migration(name: str, up_sql: str, down_sql: str = "") -> Migration:
    """创建迁移"""
    manager = get_migration_manager()
    return manager.create_migration(name, up_sql, down_sql)


def migrate():
    """执行迁移"""
    manager = get_migration_manager()
    manager.migrate()


def rollback(steps: int = 1):
    """回滚迁移"""
    manager = get_migration_manager()
    manager.rollback(steps)


def migration_status():
    """显示迁移状态"""
    manager = get_migration_manager()
    manager.status()