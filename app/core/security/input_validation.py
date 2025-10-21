"""
输入验证
数据验证和清理
"""

import re
import json
import email
import ipaddress
from typing import Dict, List, Set, Optional, Any, Pattern, Union, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, date

from app.core.middleware.base import Middleware, Request, Response


class ValidationError(Exception):
    """验证错误"""
    pass


class ValidationRule(Enum):
    """验证规则"""
    REQUIRED = "required"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"
    DATE = "date"
    DATETIME = "datetime"
    NUMBER = "number"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    STRING = "string"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    PATTERN = "pattern"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    CUSTOM = "custom"


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    cleaned_data: Any


@dataclass
class ValidationRule:
    """验证规则"""
    rule: ValidationRule
    value: Any = None
    message: str = ""
    custom_validator: Optional[Callable] = None


class InputValidator:
    """输入验证器"""
    
    def __init__(self):
        self.patterns = self._load_validation_patterns()
        self.custom_validators: Dict[str, Callable] = {}
        
    def _load_validation_patterns(self) -> Dict[str, Pattern]:
        """加载验证模式"""
        patterns = {
            "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
            "url": re.compile(r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
            "phone": re.compile(r"^\+?[\d\s\-\(\)]{10,}$"),
            "ipv4": re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"),
            "ipv6": re.compile(r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"),
            "date": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
            "datetime": re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"),
            "number": re.compile(r"^-?\d+(?:\.\d+)?$"),
            "integer": re.compile(r"^-?\d+$"),
            "float": re.compile(r"^-?\d+\.\d+$"),
            "boolean": re.compile(r"^(true|false|0|1|yes|no|on|off)$", re.IGNORECASE),
            "alphanumeric": re.compile(r"^[a-zA-Z0-9]+$"),
            "alphabetic": re.compile(r"^[a-zA-Z]+$"),
            "numeric": re.compile(r"^\d+$"),
            "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE),
            "slug": re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$"),
            "username": re.compile(r"^[a-zA-Z0-9_]{3,20}$"),
            "password": re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"),
        }
        
        return patterns
    
    def validate(self, data: Any, rules: Dict[str, List[ValidationRule]]) -> ValidationResult:
        """验证数据"""
        errors = []
        cleaned_data = data
        
        for field, field_rules in rules.items():
            field_value = self._get_field_value(data, field)
            field_errors = []
            
            for rule in field_rules:
                try:
                    if rule.rule == ValidationRule.REQUIRED:
                        if not self._is_required(field_value):
                            field_errors.append(f"{field} is required")
                    
                    elif rule.rule == ValidationRule.EMAIL:
                        if not self._is_email(field_value):
                            field_errors.append(f"{field} must be a valid email address")
                    
                    elif rule.rule == ValidationRule.URL:
                        if not self._is_url(field_value):
                            field_errors.append(f"{field} must be a valid URL")
                    
                    elif rule.rule == ValidationRule.PHONE:
                        if not self._is_phone(field_value):
                            field_errors.append(f"{field} must be a valid phone number")
                    
                    elif rule.rule == ValidationRule.IP_ADDRESS:
                        if not self._is_ip_address(field_value):
                            field_errors.append(f"{field} must be a valid IP address")
                    
                    elif rule.rule == ValidationRule.DATE:
                        if not self._is_date(field_value):
                            field_errors.append(f"{field} must be a valid date")
                    
                    elif rule.rule == ValidationRule.DATETIME:
                        if not self._is_datetime(field_value):
                            field_errors.append(f"{field} must be a valid datetime")
                    
                    elif rule.rule == ValidationRule.NUMBER:
                        if not self._is_number(field_value):
                            field_errors.append(f"{field} must be a valid number")
                    
                    elif rule.rule == ValidationRule.INTEGER:
                        if not self._is_integer(field_value):
                            field_errors.append(f"{field} must be a valid integer")
                    
                    elif rule.rule == ValidationRule.FLOAT:
                        if not self._is_float(field_value):
                            field_errors.append(f"{field} must be a valid float")
                    
                    elif rule.rule == ValidationRule.BOOLEAN:
                        if not self._is_boolean(field_value):
                            field_errors.append(f"{field} must be a valid boolean")
                    
                    elif rule.rule == ValidationRule.STRING:
                        if not self._is_string(field_value):
                            field_errors.append(f"{field} must be a valid string")
                    
                    elif rule.rule == ValidationRule.MIN_LENGTH:
                        if not self._is_min_length(field_value, rule.value):
                            field_errors.append(f"{field} must be at least {rule.value} characters long")
                    
                    elif rule.rule == ValidationRule.MAX_LENGTH:
                        if not self._is_max_length(field_value, rule.value):
                            field_errors.append(f"{field} must be at most {rule.value} characters long")
                    
                    elif rule.rule == ValidationRule.MIN_VALUE:
                        if not self._is_min_value(field_value, rule.value):
                            field_errors.append(f"{field} must be at least {rule.value}")
                    
                    elif rule.rule == ValidationRule.MAX_VALUE:
                        if not self._is_max_value(field_value, rule.value):
                            field_errors.append(f"{field} must be at most {rule.value}")
                    
                    elif rule.rule == ValidationRule.PATTERN:
                        if not self._matches_pattern(field_value, rule.value):
                            field_errors.append(f"{field} must match the required pattern")
                    
                    elif rule.rule == ValidationRule.IN_LIST:
                        if not self._is_in_list(field_value, rule.value):
                            field_errors.append(f"{field} must be one of: {', '.join(rule.value)}")
                    
                    elif rule.rule == ValidationRule.NOT_IN_LIST:
                        if not self._is_not_in_list(field_value, rule.value):
                            field_errors.append(f"{field} must not be one of: {', '.join(rule.value)}")
                    
                    elif rule.rule == ValidationRule.CUSTOM:
                        if rule.custom_validator and not rule.custom_validator(field_value):
                            field_errors.append(f"{field} failed custom validation")
                    
                except Exception as e:
                    field_errors.append(f"{field} validation error: {str(e)}")
            
            if field_errors:
                errors.extend(field_errors)
            else:
                # 清理数据
                cleaned_data = self._clean_field_value(cleaned_data, field, field_value, field_rules)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            cleaned_data=cleaned_data
        )
    
    def _get_field_value(self, data: Any, field: str) -> Any:
        """获取字段值"""
        if isinstance(data, dict):
            return data.get(field)
        elif hasattr(data, field):
            return getattr(data, field)
        else:
            return None
    
    def _clean_field_value(self, data: Any, field: str, value: Any, rules: List[ValidationRule]) -> Any:
        """清理字段值"""
        if isinstance(data, dict):
            data[field] = self._clean_value(value, rules)
        elif hasattr(data, field):
            setattr(data, field, self._clean_value(value, rules))
        
        return data
    
    def _clean_value(self, value: Any, rules: List[ValidationRule]) -> Any:
        """清理值"""
        if value is None:
            return value
        
        # 根据规则清理
        for rule in rules:
            if rule.rule == ValidationRule.STRING:
                value = str(value).strip()
            elif rule.rule == ValidationRule.INTEGER:
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    pass
            elif rule.rule == ValidationRule.FLOAT:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    pass
            elif rule.rule == ValidationRule.BOOLEAN:
                if isinstance(value, str):
                    value = value.lower() in ['true', '1', 'yes', 'on']
                else:
                    value = bool(value)
        
        return value
    
    def _is_required(self, value: Any) -> bool:
        """检查是否必需"""
        return value is not None and str(value).strip() != ""
    
    def _is_email(self, value: Any) -> bool:
        """检查是否为邮箱"""
        if not isinstance(value, str):
            return False
        try:
            email.validate_email(value)
            return True
        except email.validators.EmailNotValidError:
            return False
    
    def _is_url(self, value: Any) -> bool:
        """检查是否为URL"""
        if not isinstance(value, str):
            return False
        return bool(self.patterns["url"].match(value))
    
    def _is_phone(self, value: Any) -> bool:
        """检查是否为电话"""
        if not isinstance(value, str):
            return False
        return bool(self.patterns["phone"].match(value))
    
    def _is_ip_address(self, value: Any) -> bool:
        """检查是否为IP地址"""
        if not isinstance(value, str):
            return False
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False
    
    def _is_date(self, value: Any) -> bool:
        """检查是否为日期"""
        if not isinstance(value, str):
            return False
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _is_datetime(self, value: Any) -> bool:
        """检查是否为日期时间"""
        if not isinstance(value, str):
            return False
        try:
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False
    
    def _is_number(self, value: Any) -> bool:
        """检查是否为数字"""
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            return bool(self.patterns["number"].match(value))
        return False
    
    def _is_integer(self, value: Any) -> bool:
        """检查是否为整数"""
        if isinstance(value, int):
            return True
        if isinstance(value, str):
            return bool(self.patterns["integer"].match(value))
        return False
    
    def _is_float(self, value: Any) -> bool:
        """检查是否为浮点数"""
        if isinstance(value, float):
            return True
        if isinstance(value, str):
            return bool(self.patterns["float"].match(value))
        return False
    
    def _is_boolean(self, value: Any) -> bool:
        """检查是否为布尔值"""
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return bool(self.patterns["boolean"].match(value))
        return False
    
    def _is_string(self, value: Any) -> bool:
        """检查是否为字符串"""
        return isinstance(value, str)
    
    def _is_min_length(self, value: Any, min_length: int) -> bool:
        """检查最小长度"""
        if not isinstance(value, str):
            return False
        return len(value) >= min_length
    
    def _is_max_length(self, value: Any, max_length: int) -> bool:
        """检查最大长度"""
        if not isinstance(value, str):
            return False
        return len(value) <= max_length
    
    def _is_min_value(self, value: Any, min_value: Union[int, float]) -> bool:
        """检查最小值"""
        if not isinstance(value, (int, float)):
            return False
        return value >= min_value
    
    def _is_max_value(self, value: Any, max_value: Union[int, float]) -> bool:
        """检查最大值"""
        if not isinstance(value, (int, float)):
            return False
        return value <= max_value
    
    def _matches_pattern(self, value: Any, pattern: Union[str, Pattern]) -> bool:
        """检查是否匹配模式"""
        if not isinstance(value, str):
            return False
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return bool(pattern.match(value))
    
    def _is_in_list(self, value: Any, allowed_values: List[Any]) -> bool:
        """检查是否在列表中"""
        return value in allowed_values
    
    def _is_not_in_list(self, value: Any, forbidden_values: List[Any]) -> bool:
        """检查是否不在列表中"""
        return value not in forbidden_values
    
    def add_custom_validator(self, name: str, validator: Callable):
        """添加自定义验证器"""
        self.custom_validators[name] = validator
    
    def get_validation_schema(self, data_type: str) -> Dict[str, List[ValidationRule]]:
        """获取验证模式"""
        schemas = {
            "user": {
                "username": [
                    ValidationRule(ValidationRule.REQUIRED),
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.MIN_LENGTH, 3),
                    ValidationRule(ValidationRule.MAX_LENGTH, 20),
                    ValidationRule(ValidationRule.PATTERN, self.patterns["username"])
                ],
                "email": [
                    ValidationRule(ValidationRule.REQUIRED),
                    ValidationRule(ValidationRule.EMAIL)
                ],
                "password": [
                    ValidationRule(ValidationRule.REQUIRED),
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.MIN_LENGTH, 8),
                    ValidationRule(ValidationRule.PATTERN, self.patterns["password"])
                ],
                "age": [
                    ValidationRule(ValidationRule.INTEGER),
                    ValidationRule(ValidationRule.MIN_VALUE, 0),
                    ValidationRule(ValidationRule.MAX_VALUE, 150)
                ]
            },
            "ai_model": {
                "name": [
                    ValidationRule(ValidationRule.REQUIRED),
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.MIN_LENGTH, 1),
                    ValidationRule(ValidationRule.MAX_LENGTH, 100)
                ],
                "description": [
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.MAX_LENGTH, 1000)
                ],
                "version": [
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.PATTERN, r"^\d+\.\d+\.\d+$")
                ]
            }
        }
        
        return schemas.get(data_type, {})


class ValidationMiddleware(Middleware):
    """验证中间件"""
    
    def __init__(self, 
                 validator: InputValidator = None,
                 validation_schemas: Dict[str, Dict[str, List[ValidationRule]]] = None,
                 block_invalid: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.validator = validator or InputValidator()
        self.validation_schemas = validation_schemas or {}
        self.block_invalid = block_invalid
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理验证"""
        # 获取验证模式
        schema_name = self._get_schema_name(request)
        if schema_name not in self.validation_schemas:
            return await next_handler()
        
        # 验证请求数据
        validation_result = self.validator.validate(
            request.body,
            self.validation_schemas[schema_name]
        )
        
        # 如果验证失败，返回错误
        if not validation_result.is_valid and self.block_invalid:
            return self._create_validation_error_response(validation_result.errors)
        
        # 更新请求数据为清理后的数据
        if validation_result.cleaned_data:
            request.body = validation_result.cleaned_data
        
        # 继续处理请求
        response = await next_handler()
        
        return response
    
    def _get_schema_name(self, request: Request) -> str:
        """获取验证模式名称"""
        # 根据路径确定验证模式
        if "/users" in request.path:
            return "user"
        elif "/ai-models" in request.path:
            return "ai_model"
        else:
            return "default"
    
    def _create_validation_error_response(self, errors: List[str]) -> Response:
        """创建验证错误响应"""
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            body={
                "error": "Validation Error",
                "message": "Invalid input data",
                "code": "VALIDATION_ERROR",
                "errors": errors
            }
        )


# 全局验证器实例
input_validator = None


def init_input_validator():
    """初始化输入验证器"""
    global input_validator
    input_validator = InputValidator()
    return input_validator


def get_input_validator() -> InputValidator:
    """获取输入验证器实例"""
    if input_validator is None:
        raise RuntimeError("Input validator not initialized")
    return input_validator