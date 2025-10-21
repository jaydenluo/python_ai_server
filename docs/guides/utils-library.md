# 全局工具函数库使用指南

## 📖 概述

本文档详细介绍了AI工作流编排平台的全局工具函数库，提供了丰富的工具函数来简化开发工作，提高代码复用性和系统一致性。

## 🗂️ 目录结构

```
app/utils/
├── __init__.py              # 工具库入口
├── crypto.py                # 加密与安全工具
├── string_utils.py          # 字符串处理工具
├── file_utils.py            # 文件与路径处理工具
├── random_utils.py          # 随机生成工具
├── datetime_utils.py        # 时间日期工具
├── validators.py            # 数据验证工具
├── http_utils.py            # 网络请求工具
├── db_utils.py              # 数据库工具
├── data_utils.py            # 数据处理工具
├── image_utils.py           # 图像处理工具
├── communication.py         # 通信工具
├── search_utils.py          # 搜索与过滤工具
├── cache_utils.py           # 缓存工具
└── system_utils.py          # 系统工具
```

## 🔐 加密与安全工具 (crypto.py)

### 密码加密

```python
from app.utils import hash_password, verify_password

# 密码哈希
hashed = hash_password("my_password")

# 密码验证
is_valid = verify_password("my_password", hashed)
```

### JWT令牌管理

```python
from app.utils import generate_jwt_token, decode_jwt_token, refresh_jwt_token

# 生成JWT令牌
payload = {"user_id": 123, "username": "john"}
token = generate_jwt_token(payload)

# 解码JWT令牌
decoded = decode_jwt_token(token)

# 刷新JWT令牌
new_token = refresh_jwt_token(token)
```

### 数据加密

```python
from app.utils import encrypt_data, decrypt_data, generate_encryption_key

# 生成加密密钥
key = generate_encryption_key()

# 数据加密
encrypted = encrypt_data("sensitive data", key)

# 数据解密
decrypted = decrypt_data(encrypted, key)
```

### API签名

```python
from app.utils import generate_signature, verify_signature

# 生成签名
data = {"param1": "value1", "param2": "value2"}
signature = generate_signature(data, "secret_key")

# 验证签名
is_valid = verify_signature(data, signature, "secret_key")
```

## 🔤 字符串处理工具 (string_utils.py)

### 命名转换

```python
from app.utils import to_snake_case, to_camel_case, to_pascal_case, to_kebab_case

# 各种命名转换
snake = to_snake_case("MyVariableName")      # "my_variable_name"
camel = to_camel_case("my_variable_name")    # "myVariableName"
pascal = to_pascal_case("my_variable_name")  # "MyVariableName"
kebab = to_kebab_case("MyVariableName")      # "my-variable-name"
```

### 数据验证

```python
from app.utils import is_email, is_phone, is_url, is_chinese

# 格式验证
is_email("user@example.com")     # True
is_phone("13812345678")          # True
is_url("https://example.com")    # True
is_chinese("中文字符")            # True
```

### 文本处理

```python
from app.utils import truncate_string, remove_html_tags, clean_text

# 文本截断
short_text = truncate_string("很长的文本内容", 10, "...")

# 移除HTML标签
clean = remove_html_tags("<p>Hello <b>World</b></p>")

# 清理文本
cleaned = clean_text("  多余的   空格  ", remove_extra_spaces=True)
```

## 📁 文件与路径处理工具 (file_utils.py)

### 路径操作

```python
from app.utils import safe_join, get_file_extension, ensure_dir_exists

# 安全路径拼接
safe_path = safe_join("/base/path", "subdir", "file.txt")

# 获取文件扩展名
ext = get_file_extension("document.pdf")  # "pdf"

# 确保目录存在
ensure_dir_exists("/path/to/directory")
```

### 文件操作

```python
from app.utils import (
    save_uploaded_file, get_file_size, get_file_info, 
    copy_file, move_file, delete_file_safe
)

# 保存上传文件
file_path = save_uploaded_file(file_content, "image.jpg", "/uploads/")

# 获取文件大小
size = get_file_size("/path/to/file.txt")

# 获取文件详细信息
info = get_file_info("/path/to/file.txt")

# 文件操作
copy_file("/src/file.txt", "/dst/file.txt")
move_file("/old/path.txt", "/new/path.txt")
delete_file_safe("/path/to/delete.txt")
```

### 文件处理

```python
from app.utils import get_file_hash, format_file_size, is_binary_file

# 计算文件哈希
hash_value = get_file_hash("/path/to/file.txt", "md5")

# 格式化文件大小
size_str = format_file_size(1024000)  # "1000.0 KB"

# 检查是否为二进制文件
is_binary = is_binary_file("/path/to/file.exe")
```

## 🎲 随机生成工具 (random_utils.py)

### ID生成

```python
from app.utils import generate_uuid, generate_short_id, generate_numeric_id

# 生成各种ID
uuid = generate_uuid()                    # "550e8400-e29b-41d4-a716-446655440000"
short_id = generate_short_id(8)          # "aB3xY9zM"
numeric_id = generate_numeric_id(6)      # "123456"
```

### 随机字符串

```python
from app.utils import generate_random_string, generate_password, generate_verification_code

# 生成随机字符串
random_str = generate_random_string(10)

# 生成安全密码
password = generate_password(12, include_symbols=True)

# 生成验证码
code = generate_verification_code(6, 'numeric')  # "123456"
```

### 模拟数据

```python
from app.utils import generate_mock_name, generate_mock_phone, generate_mock_email

# 生成模拟数据
name = generate_mock_name('male')        # "张伟"
phone = generate_mock_phone()           # "13812345678"
email = generate_mock_email()           # "user123@gmail.com"
```

### 复杂数据生成

```python
from app.utils import generate_mock_data

# 根据模式生成模拟数据
schema = {
    'name': {'type': 'name'},
    'age': {'type': 'int', 'min': 18, 'max': 65},
    'email': {'type': 'email'},
    'status': {'type': 'choice', 'choices': ['active', 'inactive']}
}

mock_user = generate_mock_data(schema)
```

## ⏰ 时间日期工具 (datetime_utils.py)

### 时间格式化

```python
from app.utils import format_datetime, parse_datetime, get_timestamp

from datetime import datetime

# 格式化时间
dt = datetime.now()
formatted = format_datetime(dt, "%Y-%m-%d %H:%M:%S")

# 解析时间字符串
parsed = parse_datetime("2024-01-01 12:00:00")

# 获取时间戳
timestamp = get_timestamp(dt)
```

### 时间计算

```python
from app.utils import add_days, add_hours, get_time_diff, is_expired

# 时间计算
future_date = add_days(datetime.now(), 7)
future_time = add_hours(datetime.now(), 2)

# 计算时间差
start = datetime(2024, 1, 1)
end = datetime(2024, 1, 2)
diff = get_time_diff(start, end)

# 检查是否过期
expired = is_expired(datetime(2023, 1, 1))
```

### 相对时间

```python
from app.utils import get_relative_time, get_week_range, get_month_range

# 相对时间描述
relative = get_relative_time(datetime.now() - timedelta(hours=2))  # "2小时前"

# 获取时间范围
week_start, week_end = get_week_range()
month_start, month_end = get_month_range()
```

## 🔢 数据验证工具 (validators.py)

### 基础验证

```python
from app.utils import (
    is_valid_json, validate_required_fields, is_integer, 
    validate_email, validate_phone, validate_url
)

# JSON验证
is_valid = is_valid_json('{"key": "value"}')

# 必需字段验证
data = {"name": "John", "age": 30}
missing = validate_required_fields(data, ["name", "email"])

# 类型验证
is_int = is_integer("123")

# 格式验证
valid_email = validate_email("user@example.com")
valid_phone = validate_phone("13812345678", "CN")
valid_url = validate_url("https://example.com")
```

### 复杂验证

```python
from app.utils import (
    validate_id_card, validate_bank_card, validate_password_strength,
    validate_date_range, validate_numeric_range
)

# 身份证验证
valid_id = validate_id_card("110101199001011234")

# 银行卡验证
valid_card = validate_bank_card("6222021234567890123")

# 密码强度验证
strength = validate_password_strength("MyPassword123!")

# 范围验证
valid_range = validate_numeric_range(50, min_val=0, max_val=100)
```

## 🌐 网络请求工具 (http_utils.py)

### HTTP请求

```python
from app.utils import make_http_request, download_file

# 发送HTTP请求
response = make_http_request(
    "https://api.example.com/data",
    method="POST",
    json_data={"key": "value"}
)

# 下载文件
success = download_file("https://example.com/file.pdf", "/local/path.pdf")
```

### API响应

```python
from app.utils import build_api_response, build_error_response, paginate_data

# 构建标准API响应
response = build_api_response(
    data={"users": []},
    message="获取成功",
    code=200
)

# 构建错误响应
error_response = build_error_response("参数错误", code=400)

# 数据分页
paginated = paginate_data(user_list, page=1, per_page=10)
```

### 请求工具

```python
from app.utils import (
    get_client_ip, parse_query_params, build_cors_headers,
    generate_request_id
)

# 获取客户端IP
ip = get_client_ip(request.headers)

# 解析查询参数
params = parse_query_params("?name=john&age=30")

# 生成请求ID
req_id = generate_request_id()

# 构建CORS头
cors_headers = build_cors_headers(
    origin="https://example.com",
    methods=["GET", "POST"],
    credentials=True
)
```

## 🗄️ 数据库工具 (db_utils.py)

### 查询构建

```python
from app.utils import build_where_clause, build_order_clause, build_pagination

# 构建WHERE子句
conditions = {
    "status": "active",
    "age": {"gte": 18, "lt": 65},
    "city": {"in": ["北京", "上海"]}
}
where_clause, params = build_where_clause(conditions)

# 构建ORDER BY子句
order_by = [{"field": "created_at", "direction": "desc"}]
order_clause = build_order_clause(order_by)

# 构建分页
offset, limit = build_pagination(page=2, per_page=20)
```

### 数据转换

```python
from app.utils import dict_to_model, model_to_dict, build_select_sql

# 字典转模型
user_data = {"name": "John", "age": 30}
user_model = dict_to_model(user_data, User)

# 模型转字典
user_dict = model_to_dict(user_model, exclude=["password"])

# 构建SELECT SQL
sql, params = build_select_sql(
    table_name="users",
    fields=["id", "name", "email"],
    conditions={"status": "active"},
    order_by=[{"field": "created_at", "direction": "desc"}],
    page=1,
    per_page=10
)
```

## 📊 数据处理工具 (data_utils.py)

### 格式转换

```python
from app.utils import dict_to_json, json_to_dict, csv_to_dict_list

# 数据格式转换
json_str = dict_to_json({"name": "John", "age": 30})
data_dict = json_to_dict(json_str)

# CSV处理
csv_content = "name,age\nJohn,30\nJane,25"
dict_list = csv_to_dict_list(csv_content)
```

### 数据清洗

```python
from app.utils import (
    remove_empty_values, clean_text, remove_duplicates,
    normalize_phone_number
)

# 移除空值
clean_data = remove_empty_values({
    "name": "John",
    "email": "",
    "age": None,
    "tags": []
})

# 清理文本
cleaned = clean_text("  多余空格和特殊字符@#$  ")

# 去重
unique_list = remove_duplicates(user_list, key="id")

# 标准化手机号
normalized = normalize_phone_number("138-1234-5678")
```

### 数据操作

```python
from app.utils import (
    merge_dicts, flatten_dict, group_by_field, 
    calculate_statistics
)

# 合并字典
merged = merge_dicts(dict1, dict2, deep=True)

# 扁平化字典
flat_dict = flatten_dict({"user": {"name": "John", "age": 30}})

# 按字段分组
grouped = group_by_field(user_list, "department")

# 计算统计信息
stats = calculate_statistics([1, 2, 3, 4, 5])
```

## 🎨 图像处理工具 (image_utils.py)

### 基础操作

```python
from app.utils import (
    resize_image, compress_image, generate_thumbnail,
    get_image_info, is_valid_image
)

# 调整图片尺寸
resized_path = resize_image("input.jpg", 800, 600, "output.jpg")

# 压缩图片
compressed_path = compress_image("input.jpg", quality=80)

# 生成缩略图
thumb_path = generate_thumbnail("input.jpg", (200, 200))

# 获取图片信息
info = get_image_info("image.jpg")

# 验证图片
is_valid = is_valid_image("image.jpg")
```

### 高级操作

```python
from app.utils import (
    add_watermark, convert_format, crop_image, 
    rotate_image, image_to_base64
)

# 添加水印
watermarked = add_watermark(
    "input.jpg", 
    "© 2024 Company", 
    position="bottom-right"
)

# 格式转换
converted = convert_format("input.png", "JPEG")

# 裁剪图片
cropped = crop_image("input.jpg", (100, 100, 400, 400))

# 旋转图片
rotated = rotate_image("input.jpg", 90)

# 转换为Base64
base64_str = image_to_base64("image.jpg")
```

## 📧 通信工具 (communication.py)

### 邮件服务

```python
from app.utils.communication import EmailService

# 初始化邮件服务
email_service = EmailService(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your-email@gmail.com",
    password="your-password"
)

# 发送邮件
success = email_service.send_email(
    to_email="recipient@example.com",
    subject="测试邮件",
    content="这是一封测试邮件",
    content_type="html",
    attachments=["/path/to/file.pdf"]
)

# 批量发送
result = email_service.send_bulk_email(
    recipients=["user1@example.com", "user2@example.com"],
    subject="批量邮件",
    content="批量发送的内容"
)
```

### 短信服务

```python
from app.utils.communication import SMSService

# 初始化短信服务
sms_service = SMSService(
    api_url="https://api.sms-provider.com/send",
    api_key="your-api-key",
    api_secret="your-api-secret"
)

# 发送短信
success = sms_service.send_sms("13812345678", "您的验证码是：123456")

# 发送验证码
success = sms_service.send_verification_sms("13812345678", "123456")
```

### 推送通知

```python
from app.utils.communication import PushNotificationService

# 初始化推送服务
push_service = PushNotificationService(
    api_url="https://api.push-provider.com/send",
    api_key="your-api-key"
)

# 发送推送
success = push_service.send_push_notification(
    user_id="user123",
    title="新消息",
    content="您有一条新消息",
    data={"type": "message", "id": "msg123"}
)
```

### 消息模板

```python
from app.utils.communication import message_templates

# 使用预定义模板
message = message_templates.render_template(
    'verification_code',
    code='123456',
    minutes=5
)

# 添加自定义模板
message_templates.add_template(
    'welcome',
    '欢迎 {username} 加入我们的平台！'
)
```

## 🔍 搜索与过滤工具 (search_utils.py)

### 模糊搜索

```python
from app.utils import fuzzy_search, full_text_search, regex_search

# 模糊搜索
users = [
    {"name": "张三", "email": "zhangsan@example.com"},
    {"name": "李四", "email": "lisi@example.com"}
]

results = fuzzy_search("张", users, ["name", "email"], threshold=0.6)

# 全文搜索
is_match = full_text_search("python 开发", "我是一名python开发工程师")

# 正则搜索
regex_results = regex_search(r"\d+", users, ["phone"])
```

### 数据过滤

```python
from app.utils import filter_data, sort_data, multi_sort_data

# 数据过滤
filters = {
    "status": "active",
    "age": {"gte": 18, "lte": 65},
    "city": {"in": ["北京", "上海"]}
}
filtered_users = filter_data(users, filters)

# 数据排序
sorted_users = sort_data(users, "created_at", "desc")

# 多字段排序
sort_rules = [
    {"field": "department", "order": "asc"},
    {"field": "salary", "order": "desc"}
]
multi_sorted = multi_sort_data(users, sort_rules)
```

### 高级搜索

```python
from app.utils import advanced_search, search_with_autocomplete

# 高级搜索
search_config = {
    "query": "开发工程师",
    "fields": ["title", "description"],
    "filters": {"department": "技术部"},
    "sort": [{"field": "salary", "order": "desc"}],
    "fuzzy": True,
    "threshold": 0.7
}

results = advanced_search(job_list, search_config)

# 自动完成
suggestions = ["python", "java", "javascript", "typescript"]
matches = search_with_autocomplete("py", suggestions)
```

## 💾 缓存工具 (cache_utils.py)

### 基础缓存操作

```python
from app.utils import cache_get, cache_set, cache_delete, cache_clear_pattern

# 基础缓存操作
cache_set("user:123", {"name": "John", "age": 30}, expire=3600)
user_data = cache_get("user:123")
cache_delete("user:123")

# 批量清理
count = cache_clear_pattern("user:*")
```

### 缓存装饰器

```python
from app.utils import cache_result, cache_with_lock

# 缓存函数结果
@cache_result(expire=1800, key_prefix="api:")
def get_user_profile(user_id):
    # 耗时的数据库查询
    return fetch_user_from_db(user_id)

# 带锁的缓存（防止缓存击穿）
@cache_with_lock(expire=3600, lock_timeout=10)
def expensive_calculation(param1, param2):
    # 耗时计算
    return complex_calculation(param1, param2)
```

### 缓存管理

```python
from app.utils.cache_utils import CacheManager, cache_aside_pattern

# 自定义缓存管理器
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
cache_manager = CacheManager(redis_client)

# Cache-Aside模式
def load_user_data(user_id):
    return database.get_user(user_id)

user_data = cache_aside_pattern(
    key=f"user:{user_id}",
    data_loader=lambda: load_user_data(user_id),
    expire=3600
)
```

## 🖥️ 系统工具 (system_utils.py)

### 系统信息

```python
from app.utils import (
    get_system_info, get_memory_usage, get_cpu_usage, 
    get_disk_usage, get_network_info
)

# 获取系统信息
system_info = get_system_info()
memory_info = get_memory_usage()
cpu_info = get_cpu_usage()
disk_info = get_disk_usage()
network_info = get_network_info()
```

### 健康检查

```python
from app.utils import (
    check_database_health, check_redis_health, 
    check_external_api_health, check_port_open
)

# 健康检查
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "mydb"
}

db_healthy = check_database_health(db_config)
redis_healthy = check_redis_health({"host": "localhost", "port": 6379})
api_healthy = check_external_api_health("https://api.example.com/health")
port_open = check_port_open("localhost", 8080)
```

### 系统监控

```python
from app.utils import monitor_system_resources, execute_command

# 系统资源监控
monitoring_data = monitor_system_resources(duration=300, interval=10)

# 执行系统命令
result = execute_command("ls -la /tmp", timeout=30)
if result['success']:
    print(result['stdout'])
else:
    print(f"Error: {result['stderr']}")
```

## 🚀 使用示例

### 完整的用户注册流程

```python
from app.utils import (
    validate_email, validate_password_strength, hash_password,
    generate_verification_code, send_sms, cache_set, generate_uuid
)

def register_user(email, password, phone):
    # 1. 验证输入
    if not validate_email(email):
        return {"error": "邮箱格式不正确"}
    
    password_check = validate_password_strength(password)
    if not password_check['is_valid']:
        return {"error": "密码强度不够", "issues": password_check['issues']}
    
    # 2. 生成验证码
    verification_code = generate_verification_code(6, 'numeric')
    
    # 3. 发送短信
    sms_config = {
        "api_url": "https://sms.example.com/send",
        "api_key": "your-key",
        "api_secret": "your-secret"
    }
    
    sms_sent = send_sms(sms_config, phone, f"验证码：{verification_code}")
    if not sms_sent:
        return {"error": "短信发送失败"}
    
    # 4. 缓存验证码
    cache_key = f"verification:{phone}"
    cache_set(cache_key, verification_code, expire=300)  # 5分钟过期
    
    # 5. 加密密码
    hashed_password = hash_password(password)
    
    # 6. 生成用户ID
    user_id = generate_uuid()
    
    return {
        "success": True,
        "user_id": user_id,
        "message": "注册成功，请验证手机号"
    }
```

### 文件上传处理

```python
from app.utils import (
    is_allowed_file_type, save_uploaded_file, resize_image,
    compress_image, generate_thumbnail, get_file_info
)

def handle_image_upload(file_content, filename, upload_dir):
    # 1. 验证文件类型
    allowed_types = ['jpg', 'jpeg', 'png', 'gif']
    if not is_allowed_file_type(filename, allowed_types):
        return {"error": "不支持的文件类型"}
    
    # 2. 保存原始文件
    original_path = save_uploaded_file(file_content, filename, upload_dir)
    
    # 3. 获取文件信息
    file_info = get_file_info(original_path)
    
    # 4. 生成不同尺寸的图片
    try:
        # 压缩原图
        compressed_path = compress_image(original_path, quality=85)
        
        # 生成缩略图
        thumbnail_path = generate_thumbnail(original_path, (200, 200))
        
        # 生成中等尺寸图片
        medium_path = resize_image(original_path, 800, 600)
        
        return {
            "success": True,
            "files": {
                "original": original_path,
                "compressed": compressed_path,
                "thumbnail": thumbnail_path,
                "medium": medium_path
            },
            "info": file_info
        }
    except Exception as e:
        return {"error": f"图片处理失败: {str(e)}"}
```

### 数据导出功能

```python
from app.utils import (
    dict_list_to_csv, dict_list_to_excel, format_datetime,
    generate_random_string
)

def export_users_data(users, format_type='csv'):
    # 1. 数据预处理
    export_data = []
    for user in users:
        export_data.append({
            "ID": user.id,
            "姓名": user.name,
            "邮箱": user.email,
            "手机": user.phone,
            "注册时间": format_datetime(user.created_at, "%Y-%m-%d %H:%M:%S"),
            "状态": "激活" if user.is_active else "未激活"
        })
    
    # 2. 生成文件名
    timestamp = format_datetime(datetime.now(), "%Y%m%d_%H%M%S")
    random_suffix = generate_random_string(6)
    
    if format_type == 'csv':
        filename = f"users_export_{timestamp}_{random_suffix}.csv"
        content = dict_list_to_csv(export_data)
        
        return {
            "success": True,
            "filename": filename,
            "content": content,
            "content_type": "text/csv"
        }
    
    elif format_type == 'excel':
        filename = f"users_export_{timestamp}_{random_suffix}.xlsx"
        file_path = f"/tmp/{filename}"
        
        success = dict_list_to_excel(export_data, file_path)
        
        return {
            "success": success,
            "filename": filename,
            "file_path": file_path,
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
```

## 📋 最佳实践

### 1. 错误处理

```python
from app.utils import cache_get, hash_password

def safe_operation():
    try:
        # 使用工具函数
        data = cache_get("some_key")
        if data is None:
            # 处理缓存未命中
            data = load_from_database()
        
        return {"success": True, "data": data}
    
    except Exception as e:
        # 记录错误日志
        logger.error(f"操作失败: {str(e)}")
        return {"success": False, "error": "操作失败"}
```

### 2. 配置管理

```python
# config.py
CRYPTO_CONFIG = {
    "jwt_secret": "your-jwt-secret",
    "jwt_expire_hours": 24
}

SMS_CONFIG = {
    "api_url": "https://sms.provider.com/api",
    "api_key": "your-api-key",
    "api_secret": "your-api-secret"
}

EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-password"
}
```

### 3. 性能优化

```python
from app.utils import cache_result, cache_with_lock

# 缓存耗时操作
@cache_result(expire=3600)
def get_statistics():
    # 复杂的统计计算
    return calculate_complex_stats()

# 防止缓存击穿
@cache_with_lock(expire=1800, lock_timeout=10)
def get_popular_articles():
    # 热门文章查询
    return query_popular_articles()
```

### 4. 安全考虑

```python
from app.utils import sanitize_input, validate_required_fields, mask_sensitive_data

def process_user_input(data):
    # 1. 验证必需字段
    required_fields = ["name", "email"]
    missing = validate_required_fields(data, required_fields)
    if missing:
        return {"error": f"缺少必需字段: {missing}"}
    
    # 2. 清理输入
    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned_data[key] = sanitize_input(value)
        else:
            cleaned_data[key] = value
    
    # 3. 敏感数据脱敏（用于日志）
    log_data = cleaned_data.copy()
    if 'password' in log_data:
        log_data['password'] = mask_sensitive_data(log_data['password'])
    
    logger.info(f"处理用户输入: {log_data}")
    
    return {"success": True, "data": cleaned_data}
```

## 🔧 扩展指南

### 添加新的工具函数

1. **选择合适的模块**：根据功能选择对应的工具模块
2. **遵循命名规范**：使用清晰、描述性的函数名
3. **添加类型注解**：使用Python类型提示
4. **编写文档字符串**：详细说明参数和返回值
5. **添加错误处理**：妥善处理异常情况
6. **编写测试**：确保函数的正确性

### 示例：添加新的字符串工具

```python
# app/utils/string_utils.py

def extract_hashtags(text: str) -> List[str]:
    """
    从文本中提取话题标签
    
    Args:
        text: 输入文本
        
    Returns:
        List[str]: 话题标签列表
    """
    import re
    
    # 匹配 #话题 格式
    pattern = r'#([^\s#]+)'
    hashtags = re.findall(pattern, text)
    
    return list(set(hashtags))  # 去重
```

### 性能监控

```python
import time
import functools

def monitor_performance(func):
    """性能监控装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        if execution_time > 1.0:  # 超过1秒记录警告
            logger.warning(f"{func.__name__} 执行时间: {execution_time:.2f}秒")
        
        return result
    return wrapper
```

## 📞 技术支持

如果您在使用工具函数库时遇到问题，请：

1. 查阅本文档的相关章节
2. 检查函数的文档字符串
3. 查看示例代码
4. 提交Issue或联系开发团队

## 📝 更新日志

- **v1.0.0** (2024-01-01): 初始版本发布
  - 实现14个工具模块
  - 提供200+个工具函数
  - 完整的文档和示例

---

*本文档持续更新中，最后更新时间：2024-01-01*