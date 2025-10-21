# 安全防护系统指南

## 🛡️ 概述

本指南介绍Python AI框架的安全防护系统，包括CSRF保护、SQL注入防护、XSS防护和输入验证等功能。

## 📋 目录

- [CSRF保护](#csrf保护)
- [SQL注入防护](#sql注入防护)
- [XSS防护](#xss防护)
- [输入验证](#输入验证)
- [安全中间件](#安全中间件)
- [最佳实践](#最佳实践)
- [配置示例](#配置示例)

## 🔒 CSRF保护

### 功能特性

- **令牌生成**: 自动生成CSRF令牌
- **令牌验证**: 验证请求中的CSRF令牌
- **令牌刷新**: 支持令牌刷新机制
- **用户隔离**: 支持多用户令牌管理
- **过期管理**: 自动处理令牌过期

### 使用方法

```python
from app.core.security import CSRFProtection, CSRFMiddleware
from app.core.cache import CacheManager

# 初始化CSRF保护
cache = CacheManager()
csrf_protection = CSRFProtection("your-secret-key", cache)

# 生成CSRF令牌
token = csrf_protection.generate_token("user123")

# 验证CSRF令牌
is_valid = csrf_protection.validate_token(token, "user123")

# 刷新令牌
new_token = csrf_protection.refresh_token(token, "user123")
```

### 中间件使用

```python
# 创建CSRF中间件
csrf_middleware = CSRFMiddleware(
    secret_key="your-secret-key",
    cache=cache,
    exempt_methods={"GET", "HEAD", "OPTIONS"},
    exempt_paths={"/api/health", "/api/info"}
)
```

## 🚫 SQL注入防护

### 功能特性

- **模式检测**: 检测多种SQL注入模式
- **威胁分级**: 根据威胁级别进行分类
- **输入清理**: 自动清理危险输入
- **IP黑名单**: 自动阻止可疑IP
- **日志记录**: 记录可疑活动

### 检测模式

- **基础SQL关键字**: SELECT, INSERT, UPDATE, DELETE等
- **注释符**: --, #, /* */
- **时间延迟**: SLEEP, WAITFOR, DELAY
- **信息收集**: VERSION, USER, DATABASE等
- **文件操作**: LOAD_FILE, INTO OUTFILE等
- **系统命令**: SYSTEM, SHELL, CMD等
- **联合查询**: UNION SELECT
- **存储过程**: EXEC, EXECUTE, CALL等

### 使用方法

```python
from app.core.security import SQLInjectionProtection, SQLInjectionMiddleware

# 初始化SQL注入防护
sql_protection = SQLInjectionProtection()

# 检测SQL注入
threats = sql_protection.detect_sql_injection("'; DROP TABLE users; --")
print(f"检测到威胁: {len(threats)}")

# 清理输入
cleaned_input = sql_protection.sanitize_input("'; DROP TABLE users; --")

# 验证SQL查询
is_valid = sql_protection.validate_sql_query("SELECT * FROM users WHERE id = ?")
```

### 中间件使用

```python
# 创建SQL注入中间件
sql_middleware = SQLInjectionMiddleware(
    protection=sql_protection,
    block_threats=True,
    log_threats=True
)
```

## 🚫 XSS防护

### 功能特性

- **脚本检测**: 检测JavaScript脚本标签
- **事件检测**: 检测JavaScript事件属性
- **协议检测**: 检测危险协议（javascript:, vbscript:等）
- **标签清理**: 移除危险HTML标签
- **属性清理**: 清理危险属性
- **编码检测**: 检测各种编码方式

### 检测模式

- **脚本标签**: `<script>`, `</script>`
- **事件属性**: `onclick`, `onload`, `onerror`等
- **危险协议**: `javascript:`, `vbscript:`, `data:`
- **CSS表达式**: `expression()`
- **危险标签**: `<iframe>`, `<object>`, `<embed>`等
- **字符编码**: `&#`, `\x`, `%`等

### 使用方法

```python
from app.core.security import XSSProtection, XSSMiddleware

# 初始化XSS防护
xss_protection = XSSProtection()

# 检测XSS攻击
threats = xss_protection.detect_xss("<script>alert('XSS')</script>")
print(f"检测到威胁: {len(threats)}")

# 清理HTML
cleaned_html = xss_protection.sanitize_html("<script>alert('XSS')</script><p>Hello</p>")

# 转义HTML
escaped_text = xss_protection.escape_html("<script>alert('XSS')</script>")

# 验证URL
is_valid_url = xss_protection.validate_url("https://example.com")
```

### 中间件使用

```python
# 创建XSS中间件
xss_middleware = XSSMiddleware(
    protection=xss_protection,
    block_threats=True,
    log_threats=True,
    sanitize_output=True
)
```

## ✅ 输入验证

### 功能特性

- **类型验证**: 验证数据类型（字符串、数字、布尔值等）
- **格式验证**: 验证邮箱、URL、电话等格式
- **长度验证**: 验证最小/最大长度
- **范围验证**: 验证数值范围
- **模式验证**: 使用正则表达式验证
- **自定义验证**: 支持自定义验证规则

### 验证规则

- **必需字段**: `REQUIRED`
- **邮箱格式**: `EMAIL`
- **URL格式**: `URL`
- **电话格式**: `PHONE`
- **IP地址**: `IP_ADDRESS`
- **日期格式**: `DATE`, `DATETIME`
- **数字类型**: `NUMBER`, `INTEGER`, `FLOAT`
- **布尔值**: `BOOLEAN`
- **字符串**: `STRING`
- **长度限制**: `MIN_LENGTH`, `MAX_LENGTH`
- **数值范围**: `MIN_VALUE`, `MAX_VALUE`
- **模式匹配**: `PATTERN`
- **列表验证**: `IN_LIST`, `NOT_IN_LIST`
- **自定义验证**: `CUSTOM`

### 使用方法

```python
from app.core.security import InputValidator, ValidationRule, ValidationMiddleware

# 初始化验证器
validator = InputValidator()

# 定义验证规则
user_rules = {
    "username": [
        ValidationRule(ValidationRule.REQUIRED),
        ValidationRule(ValidationRule.STRING),
        ValidationRule(ValidationRule.MIN_LENGTH, 3),
        ValidationRule(ValidationRule.MAX_LENGTH, 20),
        ValidationRule(ValidationRule.PATTERN, r"^[a-zA-Z0-9_]+$")
    ],
    "email": [
        ValidationRule(ValidationRule.REQUIRED),
        ValidationRule(ValidationRule.EMAIL)
    ],
    "password": [
        ValidationRule(ValidationRule.REQUIRED),
        ValidationRule(ValidationRule.STRING),
        ValidationRule(ValidationRule.MIN_LENGTH, 8),
        ValidationRule(ValidationRule.PATTERN, r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")
    ],
    "age": [
        ValidationRule(ValidationRule.INTEGER),
        ValidationRule(ValidationRule.MIN_VALUE, 0),
        ValidationRule(ValidationRule.MAX_VALUE, 150)
    ]
}

# 验证数据
data = {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "Password123!",
    "age": 25
}

result = validator.validate(data, user_rules)
print(f"验证结果: {result.is_valid}")
print(f"错误: {result.errors}")
print(f"清理后的数据: {result.cleaned_data}")
```

### 中间件使用

```python
# 创建验证中间件
validation_middleware = ValidationMiddleware(
    validator=validator,
    validation_schemas={
        "user": user_rules,
        "ai_model": ai_model_rules
    },
    block_invalid=True
)
```

## 🔧 安全中间件

### 中间件组合

```python
from app.core.security import (
    CSRFMiddleware,
    SQLInjectionMiddleware,
    XSSMiddleware,
    ValidationMiddleware
)

# 创建安全中间件链
security_middlewares = [
    CSRFMiddleware(secret_key="secret", cache=cache),
    SQLInjectionMiddleware(block_threats=True),
    XSSMiddleware(block_threats=True, sanitize_output=True),
    ValidationMiddleware(block_invalid=True)
]
```

### 中间件配置

```python
# CSRF中间件配置
csrf_config = {
    "secret_key": "your-secret-key",
    "cache": cache,
    "exempt_methods": {"GET", "HEAD", "OPTIONS"},
    "exempt_paths": {"/api/health", "/api/info"}
}

# SQL注入中间件配置
sql_config = {
    "block_threats": True,
    "log_threats": True
}

# XSS中间件配置
xss_config = {
    "block_threats": True,
    "log_threats": True,
    "sanitize_output": True
}

# 验证中间件配置
validation_config = {
    "block_invalid": True,
    "validation_schemas": {
        "user": user_rules,
        "ai_model": ai_model_rules
    }
}
```

## 🎯 最佳实践

### 1. 安全配置

```python
# 安全配置
SECURITY_CONFIG = {
    "csrf": {
        "secret_key": "your-secret-key",
        "token_expire_hours": 24,
        "max_tokens_per_user": 10
    },
    "sql_injection": {
        "block_threats": True,
        "log_threats": True,
        "max_suspicious_requests": 5
    },
    "xss": {
        "block_threats": True,
        "log_threats": True,
        "sanitize_output": True,
        "max_input_length": 10000
    },
    "validation": {
        "block_invalid": True,
        "validation_schemas": {
            "user": user_rules,
            "ai_model": ai_model_rules
        }
    }
}
```

### 2. 错误处理

```python
# 安全错误处理
async def handle_security_error(error):
    """处理安全错误"""
    if isinstance(error, CSRFError):
        return Response(
            status_code=403,
            body={"error": "CSRF token missing or invalid"}
        )
    elif isinstance(error, SQLInjectionError):
        return Response(
            status_code=400,
            body={"error": "SQL injection detected"}
        )
    elif isinstance(error, XSSError):
        return Response(
            status_code=400,
            body={"error": "XSS attack detected"}
        )
    elif isinstance(error, ValidationError):
        return Response(
            status_code=400,
            body={"error": "Validation failed", "details": str(error)}
        )
```

### 3. 日志记录

```python
# 安全日志记录
import logging

security_logger = logging.getLogger("security")

def log_security_event(event_type, details):
    """记录安全事件"""
    security_logger.warning(f"Security Event: {event_type}", extra=details)
```

### 4. 监控和告警

```python
# 安全监控
class SecurityMonitor:
    def __init__(self):
        self.threat_count = 0
        self.blocked_ips = set()
    
    def record_threat(self, threat_type, client_ip):
        """记录威胁"""
        self.threat_count += 1
        if self.threat_count > 100:  # 阈值
            self.blocked_ips.add(client_ip)
            self.send_alert(f"High threat count: {self.threat_count}")
    
    def send_alert(self, message):
        """发送告警"""
        # 实现告警逻辑
        pass
```

## 📝 配置示例

### 完整配置示例

```python
# 安全防护配置
from app.core.security import (
    init_csrf_protection,
    init_sql_injection_protection,
    init_xss_protection,
    init_input_validator
)
from app.core.cache import CacheManager

# 初始化缓存
cache = CacheManager()

# 初始化安全防护
csrf_protection = init_csrf_protection("your-secret-key", cache)
sql_protection = init_sql_injection_protection()
xss_protection = init_xss_protection()
validator = init_input_validator()

# 创建安全中间件
security_middlewares = [
    CSRFMiddleware(secret_key="your-secret-key", cache=cache),
    SQLInjectionMiddleware(protection=sql_protection),
    XSSMiddleware(protection=xss_protection),
    ValidationMiddleware(validator=validator)
]

# 应用中间件
for middleware in security_middlewares:
    app.add_middleware(middleware)
```

### 环境变量配置

```bash
# 安全配置环境变量
SECURITY_CSRF_SECRET_KEY=your-secret-key
SECURITY_CSRF_TOKEN_EXPIRE_HOURS=24
SECURITY_SQL_INJECTION_BLOCK_THREATS=true
SECURITY_XSS_BLOCK_THREATS=true
SECURITY_VALIDATION_BLOCK_INVALID=true
```

## 🚀 快速开始

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置安全防护**
```python
from app.core.security import init_csrf_protection, init_sql_injection_protection

# 初始化安全防护
csrf_protection = init_csrf_protection("your-secret-key", cache)
sql_protection = init_sql_injection_protection()
```

3. **使用安全中间件**
```python
from app.core.security import CSRFMiddleware, SQLInjectionMiddleware

# 添加安全中间件
app.add_middleware(CSRFMiddleware(secret_key="secret", cache=cache))
app.add_middleware(SQLInjectionMiddleware())
```

4. **验证输入数据**
```python
from app.core.security import InputValidator, ValidationRule

# 验证用户输入
validator = InputValidator()
result = validator.validate(user_data, validation_rules)
```

## 📚 相关文档

- [API使用指南](api_usage_guide.md)
- [中间件系统](middleware_system.md)
- [配置管理](configuration_guide.md)
- [缓存系统](cache_guide.md)

## 🤝 贡献

欢迎贡献安全防护功能的改进和建议！

## 📄 许可证

本项目采用MIT许可证。