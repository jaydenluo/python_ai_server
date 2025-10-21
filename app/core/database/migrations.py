"""
数据库迁移模块
基于 Alembic 的迁移系统集成
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from app.core.config.settings import config


def migrate(revision: str = "head") -> bool:
    """
    执行数据库迁移
    
    Args:
        revision: 目标版本，默认为 "head"（最新版本）
        
    Returns:
        bool: 迁移是否成功
    """
    try:
        print(f"🔄 执行数据库迁移到版本: {revision}")
        
        # 获取 Alembic 可执行文件路径
        alembic_path = _get_alembic_path()
        if not alembic_path:
            print("❌ 找不到 Alembic 可执行文件")
            return False
        
        # 执行迁移命令
        cmd = [str(alembic_path), "upgrade", revision]
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent.parent, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 数据库迁移成功")
            return True
        else:
            print(f"❌ 数据库迁移失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        return False


def migration_status() -> Dict[str, Any]:
    """
    获取迁移状态
    
    Returns:
        Dict[str, Any]: 迁移状态信息
    """
    try:
        # 获取 Alembic 可执行文件路径
        alembic_path = _get_alembic_path()
        if not alembic_path:
            return {
                "status": "error",
                "message": "找不到 Alembic 可执行文件",
                "current_revision": None,
                "available_revisions": []
            }
        
        # 获取当前版本
        current_result = subprocess.run(
            [str(alembic_path), "current"], 
            cwd=Path(__file__).parent.parent.parent.parent,
            capture_output=True, text=True
        )
        
        # 获取历史版本
        history_result = subprocess.run(
            [str(alembic_path), "history", "--verbose"], 
            cwd=Path(__file__).parent.parent.parent.parent,
            capture_output=True, text=True
        )
        
        current_revision = None
        if current_result.returncode == 0:
            current_output = current_result.stdout.strip()
            if current_output:
                # 解析当前版本信息
                lines = current_output.split('\n')
                for line in lines:
                    if 'Rev:' in line:
                        current_revision = line.split('Rev:')[1].strip().split()[0]
                        break
        
        available_revisions = []
        if history_result.returncode == 0:
            # 解析历史版本信息
            history_output = history_result.stdout
            lines = history_output.split('\n')
            for line in lines:
                if 'Rev:' in line and 'Parent:' in line:
                    revision_info = line.strip()
                    available_revisions.append(revision_info)
        
        return {
            "status": "success",
            "current_revision": current_revision,
            "available_revisions": available_revisions,
            "current_output": current_result.stdout if current_result.returncode == 0 else None,
            "history_output": history_result.stdout if history_result.returncode == 0 else None
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"获取迁移状态时发生错误: {e}",
            "current_revision": None,
            "available_revisions": []
        }


def create_migration(message: str = "auto migration") -> bool:
    """
    创建新的迁移文件
    
    Args:
        message: 迁移描述信息
        
    Returns:
        bool: 创建是否成功
    """
    try:
        print(f"📝 创建迁移文件: {message}")
        
        # 获取 Alembic 可执行文件路径
        alembic_path = _get_alembic_path()
        if not alembic_path:
            print("❌ 找不到 Alembic 可执行文件")
            return False
        
        # 执行创建迁移命令
        cmd = [str(alembic_path), "revision", "--autogenerate", "-m", message]
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent.parent, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 迁移文件创建成功")
            print(f"输出: {result.stdout}")
            return True
        else:
            print(f"❌ 迁移文件创建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 创建迁移文件时发生错误: {e}")
        return False


def _get_alembic_path() -> Optional[Path]:
    """
    获取 Alembic 可执行文件路径
    
    Returns:
        Optional[Path]: Alembic 可执行文件路径，如果找不到则返回 None
    """
    # 尝试多个可能的路径
    possible_paths = [
        # 项目根目录下的 .conda 环境
        Path(__file__).parent.parent.parent.parent / ".conda" / "Scripts" / "alembic.exe",
        Path(__file__).parent.parent.parent.parent / ".conda" / "bin" / "alembic",
        # 系统路径中的 alembic
        Path("alembic"),
        # 使用 python -m alembic
        None  # 特殊标记，表示使用 python -m alembic
    ]
    
    for path in possible_paths:
        if path is None:
            # 尝试使用 python -m alembic
            try:
                result = subprocess.run([sys.executable, "-m", "alembic", "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return None  # 返回 None 表示使用 python -m alembic
            except:
                continue
        elif path.exists() and path.is_file():
            return path
    
    return None


def _run_alembic_command(*args) -> subprocess.CompletedProcess:
    """
    运行 Alembic 命令
    
    Args:
        *args: Alembic 命令参数
        
    Returns:
        subprocess.CompletedProcess: 命令执行结果
    """
    alembic_path = _get_alembic_path()
    
    if alembic_path is None:
        # 使用 python -m alembic
        cmd = [sys.executable, "-m", "alembic"] + list(args)
    else:
        # 使用直接路径
        cmd = [str(alembic_path)] + list(args)
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent.parent, 
                         capture_output=True, text=True)


# 为了向后兼容，提供一些别名函数
def upgrade(revision: str = "head") -> bool:
    """升级数据库到指定版本（migrate 的别名）"""
    return migrate(revision)


def downgrade(revision: str = "-1") -> bool:
    """
    降级数据库到指定版本
    
    Args:
        revision: 目标版本，默认为 "-1"（上一个版本）
        
    Returns:
        bool: 降级是否成功
    """
    try:
        print(f"⬇️ 降级数据库到版本: {revision}")
        
        result = _run_alembic_command("downgrade", revision)
        
        if result.returncode == 0:
            print("✅ 数据库降级成功")
            return True
        else:
            print(f"❌ 数据库降级失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 降级过程中发生错误: {e}")
        return False


def current() -> Optional[str]:
    """
    获取当前数据库版本
    
    Returns:
        Optional[str]: 当前版本号，如果获取失败则返回 None
    """
    try:
        result = _run_alembic_command("current")
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                # 解析当前版本信息
                lines = output.split('\n')
                for line in lines:
                    if 'Rev:' in line:
                        return line.split('Rev:')[1].strip().split()[0]
        
        return None
        
    except Exception as e:
        print(f"❌ 获取当前版本时发生错误: {e}")
        return None


def history() -> list:
    """
    获取迁移历史
    
    Returns:
        list: 迁移历史列表
    """
    try:
        result = _run_alembic_command("history", "--verbose")
        
        if result.returncode == 0:
            history_list = []
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Rev:' in line and 'Parent:' in line:
                    history_list.append(line.strip())
            return history_list
        
        return []
        
    except Exception as e:
        print(f"❌ 获取迁移历史时发生错误: {e}")
        return []
