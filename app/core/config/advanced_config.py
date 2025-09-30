"""
高级配置管理
提供环境配置、动态配置、配置验证等功能
"""

import os
import json
import yaml
from typing import Any, Dict, List, Optional, Union, Type, Callable
from pathlib import Path
from datetime import datetime, timedelta
import threading
from abc import ABC, abstractmethod


class ConfigValidator(ABC):
    """配置验证器基类"""
    
    @abstractmethod
    def validate(self, value: Any) -> bool:
        """验证配置值"""
        pass
    
    @abstractmethod
    def get_error_message(self, key: str, value: Any) -> str:
        """获取错误信息"""
        pass


class TypeValidator(ConfigValidator):
    """类型验证器"""
    
    def __init__(self, expected_type: Type):
        self.expected_type = expected_type
    
    def validate(self, value: Any) -> bool:
        return isinstance(value, self.expected_type)
    
    def get_error_message(self, key: str, value: Any) -> str:
        return f"Configuration '{key}' must be of type {self.expected_type.__name__}, got {type(value).__name__}"


class RangeValidator(ConfigValidator):
    """范围验证器"""
    
    def __init__(self, min_value: Union[int, float] = None, max_value: Union[int, float] = None):
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, (int, float)):
            return False
        
        if self.min_value is not None and value < self.min_value:
            return False
        
        if self.max_value is not None and value > self.max_value:
            return False
        
        return True
    
    def get_error_message(self, key: str, value: Any) -> str:
        if self.min_value is not None and self.max_value is not None:
            return f"Configuration '{key}' must be between {self.min_value} and {self.max_value}"
        elif self.min_value is not None:
            return f"Configuration '{key}' must be at least {self.min_value}"
        elif self.max_value is not None:
            return f"Configuration '{key}' must be at most {self.max_value}"
        return f"Configuration '{key}' is invalid"


class ChoiceValidator(ConfigValidator):
    """选择验证器"""
    
    def __init__(self, choices: List[Any]):
        self.choices = choices
    
    def validate(self, value: Any) -> bool:
        return value in self.choices
    
    def get_error_message(self, key: str, value: Any) -> str:
        return f"Configuration '{key}' must be one of {self.choices}"


class ConfigSource(ABC):
    """配置源基类"""
    
    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """加载配置"""
        pass
    
    @abstractmethod
    def save(self, config: Dict[str, Any]) -> None:
        """保存配置"""
        pass


class FileConfigSource(ConfigSource):
    """文件配置源"""
    
    def __init__(self, file_path: Union[str, Path], format: str = 'json'):
        self.file_path = Path(file_path)
        self.format = format.lower()
    
    def load(self) -> Dict[str, Any]:
        if not self.file_path.exists():
            return {}
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            if self.format == 'json':
                return json.load(f)
            elif self.format == 'yaml':
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported format: {self.format}")
    
    def save(self, config: Dict[str, Any]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            if self.format == 'json':
                json.dump(config, f, indent=2, ensure_ascii=False)
            elif self.format == 'yaml':
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(f"Unsupported format: {self.format}")


class EnvironmentConfigSource(ConfigSource):
    """环境变量配置源"""
    
    def __init__(self, prefix: str = '', separator: str = '_'):
        self.prefix = prefix.upper()
        self.separator = separator
    
    def load(self) -> Dict[str, Any]:
        config = {}
        
        for key, value in os.environ.items():
            if self.prefix and not key.startswith(self.prefix):
                continue
            
            # 移除前缀
            if self.prefix:
                key = key[len(self.prefix):].lstrip(self.separator)
            
            # 转换为嵌套字典
            keys = key.split(self.separator)
            current = config
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = self._parse_value(value)
        
        return config
    
    def save(self, config: Dict[str, Any]) -> None:
        # 环境变量是只读的，不能保存
        raise NotImplementedError("Cannot save to environment variables")
    
    def _parse_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为数字
        if value.isdigit():
            return int(value)
        
        # 尝试解析为浮点数
        try:
            return float(value)
        except ValueError:
            pass
        
        # 尝试解析为布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 尝试解析为JSON
        if value.startswith('{') or value.startswith('['):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        return value


class AdvancedConfig:
    """高级配置管理器"""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._sources: List[ConfigSource] = []
        self._validators: Dict[str, List[ConfigValidator]] = {}
        self._watchers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._last_modified = datetime.now()
    
    def add_source(self, source: ConfigSource, priority: int = 0) -> 'AdvancedConfig':
        """添加配置源"""
        with self._lock:
            self._sources.append((priority, source))
            self._sources.sort(key=lambda x: x[0], reverse=True)
        return self
    
    def load(self) -> 'AdvancedConfig':
        """加载配置"""
        with self._lock:
            self._config.clear()
            
            for priority, source in self._sources:
                try:
                    source_config = source.load()
                    self._merge_config(source_config)
                except Exception as e:
                    print(f"Error loading config from source: {e}")
            
            self._last_modified = datetime.now()
        
        return self
    
    def save(self) -> 'AdvancedConfig':
        """保存配置"""
        with self._lock:
            for priority, source in self._sources:
                try:
                    source.save(self._config)
                except NotImplementedError:
                    # 某些源不支持保存（如环境变量）
                    continue
                except Exception as e:
                    print(f"Error saving config to source: {e}")
        
        return self
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        with self._lock:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
    
    def set(self, key: str, value: Any) -> 'AdvancedConfig':
        """设置配置值"""
        with self._lock:
            # 验证配置
            if key in self._validators:
                for validator in self._validators[key]:
                    if not validator.validate(value):
                        raise ValueError(validator.get_error_message(key, value))
            
            # 设置配置
            keys = key.split('.')
            current = self._config
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            
            # 通知观察者
            if key in self._watchers:
                for watcher in self._watchers[key]:
                    try:
                        watcher(key, value)
                    except Exception as e:
                        print(f"Error in config watcher: {e}")
            
            self._last_modified = datetime.now()
        
        return self
    
    def has(self, key: str) -> bool:
        """检查配置是否存在"""
        return self.get(key) is not None
    
    def remove(self, key: str) -> 'AdvancedConfig':
        """移除配置"""
        with self._lock:
            keys = key.split('.')
            current = self._config
            
            for k in keys[:-1]:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return self
            
            if isinstance(current, dict) and keys[-1] in current:
                del current[keys[-1]]
        
        return self
    
    def add_validator(self, key: str, validator: ConfigValidator) -> 'AdvancedConfig':
        """添加配置验证器"""
        with self._lock:
            if key not in self._validators:
                self._validators[key] = []
            self._validators[key].append(validator)
        
        return self
    
    def add_watcher(self, key: str, watcher: Callable[[str, Any], None]) -> 'AdvancedConfig':
        """添加配置观察者"""
        with self._lock:
            if key not in self._watchers:
                self._watchers[key] = []
            self._watchers[key].append(watcher)
        
        return self
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        with self._lock:
            return self._config.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.get_all()
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.get_all(), indent=2, ensure_ascii=False)
    
    def is_modified_since(self, timestamp: datetime) -> bool:
        """检查是否在指定时间后修改过"""
        return self._last_modified > timestamp
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """合并配置"""
        def merge_dict(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
            return base
        
        self._config = merge_dict(self._config, new_config)


# 全局配置实例
config = AdvancedConfig()

# 默认配置源
config.add_source(EnvironmentConfigSource('APP'))
config.add_source(FileConfigSource('config.json'))
config.add_source(FileConfigSource('config.yaml', 'yaml'))