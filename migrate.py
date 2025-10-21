#!/usr/bin/env python3
"""
基于 Alembic 的数据库迁移管理工具
使用 SQLAlchemy 官方推荐的迁移工具
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_alembic(*args):
    """运行 Alembic 命令"""
    try:
        # 使用项目环境中的 alembic
        cmd = [".conda/Scripts/alembic.exe"] + list(args)
        print(f"执行: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False

def create_migration(message: str = "auto migration"):
    """创建新的迁移文件"""
    print(f"创建迁移: {message}")
    return run_alembic("revision", "--autogenerate", "-m", message)

def upgrade_database(revision: str = "head"):
    """升级数据库到指定版本"""
    print(f"升级数据库到: {revision}")
    return run_alembic("upgrade", revision)

def downgrade_database(revision: str = "-1"):
    """降级数据库到指定版本"""
    print(f"降级数据库到: {revision}")
    return run_alembic("downgrade", revision)

def show_current():
    """显示当前数据库版本"""
    print("当前数据库版本:")
    return run_alembic("current")

def show_history():
    """显示迁移历史"""
    print("迁移历史:")
    return run_alembic("history", "--verbose")

def show_pending():
    """显示待应用的迁移"""
    print("待应用的迁移:")
    return run_alembic("show", "head")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="基于 Alembic 的数据库迁移管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python migrate.py create "添加用户表"     # 创建迁移
  python migrate.py upgrade              # 应用所有迁移
  python migrate.py upgrade +1           # 应用下一个迁移
  python migrate.py downgrade -1         # 回滚一个迁移
  python migrate.py current               # 查看当前版本
  python migrate.py history               # 查看迁移历史
        """
    )
    
    parser.add_argument(
        "command",
        choices=["create", "upgrade", "downgrade", "current", "history", "show"],
        help="迁移命令"
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="命令参数"
    )
    
    args = parser.parse_args()
    
    print("Alembic 迁移管理工具")
    print("=" * 50)
    
    if args.command == "create":
        message = args.args[0] if args.args else "auto migration"
        create_migration(message)
    elif args.command == "upgrade":
        revision = args.args[0] if args.args else "head"
        upgrade_database(revision)
    elif args.command == "downgrade":
        revision = args.args[0] if args.args else "-1"
        downgrade_database(revision)
    elif args.command == "current":
        show_current()
    elif args.command == "history":
        show_history()
    elif args.command == "show":
        show_pending()

if __name__ == "__main__":
    main()
