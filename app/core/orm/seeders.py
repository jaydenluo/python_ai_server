"""
种子数据系统
提供数据库种子数据管理功能
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Type, Callable
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import importlib
import inspect

from app.core.orm.models import Model
from app.core.orm.migration_system import migration_manager


@dataclass
class SeederInfo:
    """种子数据信息"""
    name: str
    model: Type[Model]
    data: List[Dict[str, Any]]
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    enabled: bool = True


class SeederManager:
    """种子数据管理器"""
    
    def __init__(self, seeders_dir: str = "database/seeders"):
        self.seeders_dir = Path(seeders_dir)
        self.seeders_dir.mkdir(parents=True, exist_ok=True)
        
        self.seeders: Dict[str, SeederInfo] = {}
        self.logger = logging.getLogger(__name__)
        
        # 种子数据状态文件
        self.status_file = self.seeders_dir / "seeder_status.json"
        self._load_status()
    
    def _load_status(self):
        """加载种子数据状态"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    self._status = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load seeder status: {e}")
                self._status = {}
        else:
            self._status = {}
    
    def _save_status(self):
        """保存种子数据状态"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self._status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save seeder status: {e}")
    
    def register_seeder(self, seeder_info: SeederInfo):
        """注册种子数据"""
        self.seeders[seeder_info.name] = seeder_info
        self.logger.info(f"Registered seeder: {seeder_info.name}")
    
    def create_seeder(self, name: str, model: Type[Model], data: List[Dict[str, Any]], 
                     dependencies: List[str] = None, priority: int = 0) -> SeederInfo:
        """创建种子数据"""
        seeder_info = SeederInfo(
            name=name,
            model=model,
            data=data,
            dependencies=dependencies or [],
            priority=priority
        )
        
        self.register_seeder(seeder_info)
        return seeder_info
    
    def run_seeder(self, name: str, force: bool = False) -> bool:
        """运行指定的种子数据"""
        if name not in self.seeders:
            self.logger.error(f"Seeder '{name}' not found")
            return False
        
        # 检查是否已经运行过
        if not force and self._status.get(name, {}).get('executed', False):
            self.logger.info(f"Seeder '{name}' already executed, skipping")
            return True
        
        seeder_info = self.seeders[name]
        
        try:
            self.logger.info(f"Running seeder: {name}")
            
            # 运行依赖的种子数据
            for dep in seeder_info.dependencies:
                if not self.run_seeder(dep, force):
                    self.logger.error(f"Failed to run dependency seeder: {dep}")
                    return False
            
            # 执行种子数据
            success = self._execute_seeder(seeder_info)
            
            if success:
                # 更新状态
                self._status[name] = {
                    'executed': True,
                    'executed_at': datetime.now().isoformat(),
                    'model': seeder_info.model.__name__,
                    'data_count': len(seeder_info.data)
                }
                self._save_status()
                
                self.logger.info(f"Seeder '{name}' executed successfully")
            else:
                self.logger.error(f"Seeder '{name}' execution failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error running seeder '{name}': {e}")
            return False
    
    def _execute_seeder(self, seeder_info: SeederInfo) -> bool:
        """执行种子数据"""
        try:
            model = seeder_info.model
            data = seeder_info.data
            
            # 获取数据库会话
            session = migration_manager.get_session()
            
            created_count = 0
            updated_count = 0
            
            for item_data in data:
                # 检查是否已存在
                existing = None
                if hasattr(model, 'find_by_unique_fields'):
                    existing = model.find_by_unique_fields(item_data)
                else:
                    # 默认查找逻辑
                    if 'id' in item_data:
                        existing = session.query(model).filter(model.id == item_data['id']).first()
                    elif 'email' in item_data:
                        existing = session.query(model).filter(model.email == item_data['email']).first()
                    elif 'username' in item_data:
                        existing = session.query(model).filter(model.username == item_data['username']).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in item_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    updated_count += 1
                else:
                    # 创建新记录
                    instance = model(**item_data)
                    session.add(instance)
                    created_count += 1
            
            session.commit()
            
            self.logger.info(f"Seeder executed: {created_count} created, {updated_count} updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing seeder: {e}")
            return False
    
    def run_all_seeders(self, force: bool = False) -> bool:
        """运行所有种子数据"""
        # 按优先级排序
        sorted_seeders = sorted(
            self.seeders.items(),
            key=lambda x: (x[1].priority, x[0])
        )
        
        success_count = 0
        total_count = len(sorted_seeders)
        
        for name, seeder_info in sorted_seeders:
            if not seeder_info.enabled:
                self.logger.info(f"Skipping disabled seeder: {name}")
                continue
            
            if self.run_seeder(name, force):
                success_count += 1
            else:
                self.logger.error(f"Failed to run seeder: {name}")
                return False
        
        self.logger.info(f"All seeders executed: {success_count}/{total_count} successful")
        return success_count == total_count
    
    def reset_seeder(self, name: str) -> bool:
        """重置种子数据状态"""
        if name in self._status:
            del self._status[name]
            self._save_status()
            self.logger.info(f"Reset seeder status: {name}")
            return True
        return False
    
    def reset_all_seeders(self) -> bool:
        """重置所有种子数据状态"""
        self._status = {}
        self._save_status()
        self.logger.info("Reset all seeder status")
        return True
    
    def get_seeder_status(self) -> Dict[str, Any]:
        """获取种子数据状态"""
        return {
            'seeders': list(self.seeders.keys()),
            'executed': list(self._status.keys()),
            'pending': [name for name in self.seeders.keys() if name not in self._status],
            'status_details': self._status
        }
    
    def create_seeder_file(self, name: str, model_name: str, data: List[Dict[str, Any]]) -> str:
        """创建种子数据文件"""
        seeder_file = self.seeders_dir / f"{name}_seeder.py"
        
        template = f'''"""
{name} 种子数据
自动生成的种子数据文件
"""

from app.models.entities.{model_name.lower()} import {model_name}
from app.core.orm.seeders import seeder_manager

# 种子数据
data = {data}

# 注册种子数据
seeder_info = seeder_manager.create_seeder(
    name="{name}",
    model={model_name},
    data=data,
    priority=0
)
'''
        
        with open(seeder_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        self.logger.info(f"Created seeder file: {seeder_file}")
        return str(seeder_file)
    
    def load_seeder_files(self):
        """加载种子数据文件"""
        for seeder_file in self.seeders_dir.glob("*_seeder.py"):
            try:
                # 动态导入种子数据文件
                module_name = seeder_file.stem
                spec = importlib.util.spec_from_file_location(module_name, seeder_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                self.logger.info(f"Loaded seeder file: {seeder_file}")
                
            except Exception as e:
                self.logger.error(f"Failed to load seeder file {seeder_file}: {e}")


class SeederDecorator:
    """种子数据装饰器"""
    
    def __init__(self, name: str, priority: int = 0, dependencies: List[str] = None):
        self.name = name
        self.priority = priority
        self.dependencies = dependencies or []
    
    def __call__(self, func: Callable) -> Callable:
        """装饰器实现"""
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 注册种子数据
        seeder_manager.register_seeder(SeederInfo(
            name=self.name,
            model=None,  # 将在运行时确定
            data=[],  # 将在运行时确定
            dependencies=self.dependencies,
            priority=self.priority
        ))
        
        return wrapper


# 全局种子数据管理器
seeder_manager = SeederManager()


def seeder(name: str, priority: int = 0, dependencies: List[str] = None):
    """种子数据装饰器"""
    return SeederDecorator(name, priority, dependencies)


def create_seeder(name: str, model: Type[Model], data: List[Dict[str, Any]], 
                 dependencies: List[str] = None, priority: int = 0) -> SeederInfo:
    """创建种子数据"""
    return seeder_manager.create_seeder(name, model, data, dependencies, priority)


def run_seeder(name: str, force: bool = False) -> bool:
    """运行种子数据"""
    return seeder_manager.run_seeder(name, force)


def run_all_seeders(force: bool = False) -> bool:
    """运行所有种子数据"""
    return seeder_manager.run_all_seeders(force)


def reset_seeders() -> bool:
    """重置种子数据状态"""
    return seeder_manager.reset_all_seeders()