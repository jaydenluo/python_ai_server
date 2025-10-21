# Django-Vue3-Admin 系统功能数据表与API接口文档

## 概述

本文档提取了Django-Vue3-Admin项目中以下核心功能的数据表结构和API接口信息：
- 菜单管理
- 部门管理  
- 角色管理
- 按钮权限控制
- 字段列权限控制
- 用户管理
- 字典管理
- 地区管理
- 附件管理
- 操作日志
- 定时任务与任务日志

数据库将使用PostgreSQL 18实现。

## 1. 数据表结构

### 1.1 核心基础模型 (CoreModel)

所有业务表都继承自CoreModel，包含以下审计字段：

```sql
-- 通用审计字段
id BIGSERIAL PRIMARY KEY,
description VARCHAR(255),
creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
modifier VARCHAR(255),
dept_belong_id VARCHAR(255),
update_datetime TIMESTAMP WITH TIME ZONE,
create_datetime TIMESTAMP WITH TIME ZONE
```

### 1.2 用户管理相关表

#### 1.2.1 用户表 (users)

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254),
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
    mobile VARCHAR(255),
    avatar VARCHAR(255),
    name VARCHAR(40) NOT NULL,
    gender INTEGER DEFAULT 0 CHECK (gender IN (0, 1, 2)), -- 0:未知 1:男 2:女
    user_type INTEGER DEFAULT 0 CHECK (user_type IN (0, 1)), -- 0:后台用户 1:前台用户
    dept_id BIGINT REFERENCES dept(id) ON DELETE PROTECT,
    current_role_id BIGINT REFERENCES role(id) ON DELETE SET NULL,
    login_error_count INTEGER DEFAULT 0,
    pwd_change_count INTEGER DEFAULT 0,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);

-- 用户角色关联表
CREATE TABLE users_role (
    id BIGSERIAL PRIMARY KEY,
    users_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    UNIQUE(users_id, role_id)
);

-- 用户岗位关联表  
CREATE TABLE users_post (
    id BIGSERIAL PRIMARY KEY,
    users_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id BIGINT NOT NULL REFERENCES post(id) ON DELETE CASCADE,
    UNIQUE(users_id, post_id)
);

-- 用户管理部门关联表
CREATE TABLE users_manage_dept (
    id BIGSERIAL PRIMARY KEY,
    users_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dept_id BIGINT NOT NULL REFERENCES dept(id) ON DELETE CASCADE,
    UNIQUE(users_id, dept_id)
);
```

#### 1.2.2 角色表 (role)

```sql
CREATE TABLE role (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    key VARCHAR(64) UNIQUE NOT NULL,
    sort INTEGER DEFAULT 1,
    status BOOLEAN DEFAULT TRUE,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

#### 1.2.3 部门表 (dept)

```sql
CREATE TABLE dept (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    key VARCHAR(64) UNIQUE,
    sort INTEGER DEFAULT 1,
    owner VARCHAR(32),
    phone VARCHAR(32),
    email VARCHAR(32),
    status BOOLEAN DEFAULT TRUE,
    parent_id BIGINT REFERENCES dept(id) ON DELETE CASCADE,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

#### 1.2.4 岗位表 (post)

```sql
CREATE TABLE post (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    code VARCHAR(32) NOT NULL,
    sort INTEGER DEFAULT 1,
    status INTEGER DEFAULT 1 CHECK (status IN (0, 1)), -- 0:离职 1:在职
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

### 1.3 菜单权限相关表

#### 1.3.1 菜单表 (menu)

```sql
CREATE TABLE menu (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES menu(id) ON DELETE CASCADE,
    icon VARCHAR(64),
    name VARCHAR(64) NOT NULL,
    sort INTEGER DEFAULT 1,
    is_link BOOLEAN DEFAULT FALSE,
    link_url VARCHAR(255),
    is_catalog BOOLEAN DEFAULT FALSE,
    web_path VARCHAR(128),
    component VARCHAR(128),
    component_name VARCHAR(50),
    status BOOLEAN DEFAULT TRUE,
    cache BOOLEAN DEFAULT FALSE,
    visible BOOLEAN DEFAULT TRUE,
    is_iframe BOOLEAN DEFAULT FALSE,
    is_affix BOOLEAN DEFAULT FALSE,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

#### 1.3.2 菜单按钮权限表 (menu_button)

```sql
CREATE TABLE menu_button (
    id BIGSERIAL PRIMARY KEY,
    menu_id BIGINT NOT NULL REFERENCES menu(id) ON DELETE CASCADE,
    name VARCHAR(64) NOT NULL,
    value VARCHAR(64) UNIQUE NOT NULL,
    api VARCHAR(200) NOT NULL,
    method INTEGER DEFAULT 0 CHECK (method IN (0, 1, 2, 3)), -- 0:GET 1:POST 2:PUT 3:DELETE
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

#### 1.3.3 菜单字段表 (menu_field)

```sql
CREATE TABLE menu_field (
    id BIGSERIAL PRIMARY KEY,
    model VARCHAR(64) NOT NULL,
    menu_id BIGINT NOT NULL REFERENCES menu(id) ON DELETE CASCADE,
    field_name VARCHAR(64) NOT NULL,
    title VARCHAR(64) NOT NULL,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

#### 1.3.4 字段权限表 (field_permission)

```sql
CREATE TABLE field_permission (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    field_id BIGINT NOT NULL REFERENCES menu_field(id) ON DELETE CASCADE,
    is_query BOOLEAN DEFAULT TRUE,
    is_create BOOLEAN DEFAULT TRUE,
    is_update BOOLEAN DEFAULT TRUE,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

#### 1.3.5 角色菜单权限表 (role_menu_permission)

```sql
CREATE TABLE role_menu_permission (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    menu_id BIGINT NOT NULL REFERENCES menu(id) ON DELETE CASCADE,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

#### 1.3.6 角色按钮权限表 (role_menu_button_permission)

```sql
CREATE TABLE role_menu_button_permission (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    menu_button_id BIGINT REFERENCES menu_button(id) ON DELETE CASCADE,
    data_range INTEGER DEFAULT 0 CHECK (data_range IN (0, 1, 2, 3, 4)), -- 数据权限范围
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);

-- 角色按钮权限部门关联表
CREATE TABLE role_menu_button_permission_dept (
    id BIGSERIAL PRIMARY KEY,
    rolemenubuttonpermission_id BIGINT NOT NULL REFERENCES role_menu_button_permission(id) ON DELETE CASCADE,
    dept_id BIGINT NOT NULL REFERENCES dept(id) ON DELETE CASCADE,
    UNIQUE(rolemenubuttonpermission_id, dept_id)
);
```

### 1.4 字典管理表

#### 1.4.1 字典表 (dictionary)

```sql
CREATE TABLE dictionary (
    id BIGSERIAL PRIMARY KEY,
    label VARCHAR(100),
    value VARCHAR(200),
    parent_id BIGINT REFERENCES dictionary(id) ON DELETE PROTECT,
    type INTEGER DEFAULT 0 CHECK (type IN (0, 1, 2, 3, 4, 5, 6, 7)), -- 数据值类型
    color VARCHAR(20),
    is_value BOOLEAN DEFAULT FALSE,
    status BOOLEAN DEFAULT TRUE,
    sort INTEGER DEFAULT 1,
    remark VARCHAR(2000),
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

### 1.5 地区管理表

#### 1.5.1 地区表 (area)

```sql
CREATE TABLE area (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    level BIGINT NOT NULL, -- 1:省份 2:城市 3:区县 4:乡级
    pinyin VARCHAR(255) NOT NULL,
    initials VARCHAR(20) NOT NULL,
    enable BOOLEAN DEFAULT TRUE,
    pcode VARCHAR(20) REFERENCES area(code) ON DELETE CASCADE,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_area_code ON area(code);
```

### 1.6 文件管理表

#### 1.6.1 文件列表表 (file_list)

```sql
CREATE TABLE file_list (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200),
    url VARCHAR(100), -- 文件路径
    file_url VARCHAR(255), -- 文件地址
    engine VARCHAR(100) DEFAULT 'local',
    mime_type VARCHAR(100),
    size VARCHAR(36),
    md5sum VARCHAR(36),
    upload_method SMALLINT DEFAULT 0 CHECK (upload_method IN (0, 1)), -- 0:默认上传 1:文件选择器上传
    file_type SMALLINT DEFAULT 3 CHECK (file_type IN (0, 1, 2, 3)), -- 0:图片 1:视频 2:音频 3:其他
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

### 1.7 日志管理表

#### 1.7.1 操作日志表 (operation_log)

```sql
CREATE TABLE operation_log (
    id BIGSERIAL PRIMARY KEY,
    request_modular VARCHAR(64),
    request_path VARCHAR(400),
    request_body TEXT,
    request_method VARCHAR(8),
    request_msg TEXT,
    request_ip VARCHAR(32),
    request_browser VARCHAR(64),
    response_code VARCHAR(32),
    request_os VARCHAR(64),
    json_result TEXT,
    status BOOLEAN DEFAULT FALSE,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

#### 1.7.2 登录日志表 (login_log)

```sql
CREATE TABLE login_log (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(32),
    ip VARCHAR(32),
    agent TEXT,
    browser VARCHAR(200),
    os VARCHAR(200),
    continent VARCHAR(50),
    country VARCHAR(50),
    province VARCHAR(50),
    city VARCHAR(50),
    district VARCHAR(50),
    isp VARCHAR(50),
    area_code VARCHAR(50),
    country_english VARCHAR(50),
    country_code VARCHAR(50),
    longitude VARCHAR(50),
    latitude VARCHAR(50),
    login_type INTEGER DEFAULT 1 CHECK (login_type IN (1, 2)), -- 1:普通登录 2:微信扫码登录
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

### 1.8 系统配置表

#### 1.8.1 系统配置表 (config)

```sql
CREATE TABLE config (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES config(id) ON DELETE CASCADE,
    title VARCHAR(50) NOT NULL,
    key VARCHAR(100) NOT NULL,
    value JSONB,
    sort INTEGER DEFAULT 0,
    status BOOLEAN DEFAULT TRUE,
    data_options JSONB,
    form_item_type INTEGER DEFAULT 0 CHECK (form_item_type IN (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)),
    rule JSONB,
    placeholder VARCHAR(50),
    setting JSONB,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE,
    UNIQUE(key, parent_id)
);

CREATE INDEX idx_config_key ON config(key);
```

### 1.9 API白名单表

#### 1.9.1 API白名单表 (api_white_list)

```sql
CREATE TABLE api_white_list (
    id BIGSERIAL PRIMARY KEY,
    url VARCHAR(200) NOT NULL,
    method INTEGER DEFAULT 0 CHECK (method IN (0, 1, 2, 3)), -- 0:GET 1:POST 2:PUT 3:DELETE
    enable_datasource BOOLEAN DEFAULT TRUE,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

### 1.10 消息中心表

#### 1.10.1 消息中心表 (message_center)

```sql
CREATE TABLE message_center (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    target_type INTEGER DEFAULT 0,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);

-- 消息中心目标用户表
CREATE TABLE message_center_target_user (
    id BIGSERIAL PRIMARY KEY,
    users_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    messagecenter_id BIGINT NOT NULL REFERENCES message_center(id) ON DELETE CASCADE,
    is_read BOOLEAN DEFAULT FALSE,
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);

-- 消息中心目标部门关联表
CREATE TABLE message_center_target_dept (
    id BIGSERIAL PRIMARY KEY,
    messagecenter_id BIGINT NOT NULL REFERENCES message_center(id) ON DELETE CASCADE,
    dept_id BIGINT NOT NULL REFERENCES dept(id) ON DELETE CASCADE,
    UNIQUE(messagecenter_id, dept_id)
);

-- 消息中心目标角色关联表
CREATE TABLE message_center_target_role (
    id BIGSERIAL PRIMARY KEY,
    messagecenter_id BIGINT NOT NULL REFERENCES message_center(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    UNIQUE(messagecenter_id, role_id)
);
```

### 1.11 下载中心表

#### 1.11.1 下载中心表 (download_center)

```sql
CREATE TABLE download_center (
    id BIGSERIAL PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    task_status SMALLINT DEFAULT 0 CHECK (task_status IN (0, 1, 2, 3)), -- 0:已创建 1:进行中 2:完成 3:失败
    file_name VARCHAR(255),
    url VARCHAR(100), -- 文件路径
    size BIGINT DEFAULT 0,
    md5sum VARCHAR(36),
    description VARCHAR(255),
    creator_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    modifier VARCHAR(255),
    dept_belong_id VARCHAR(255),
    update_datetime TIMESTAMP WITH TIME ZONE,
    create_datetime TIMESTAMP WITH TIME ZONE
);
```

### 1.12 定时任务相关表

项目使用Celery + django-celery-beat + django-celery-results实现定时任务功能。

#### 1.12.1 Celery任务结果表 (django_celery_results_taskresult)

```sql
CREATE TABLE django_celery_results_taskresult (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    task_name VARCHAR(255),
    task_args TEXT,
    task_kwargs TEXT,
    status VARCHAR(50) NOT NULL,
    worker VARCHAR(100),
    content_type VARCHAR(128) NOT NULL,
    content_encoding VARCHAR(64) NOT NULL,
    result TEXT,
    date_created TIMESTAMP WITH TIME ZONE NOT NULL,
    date_done TIMESTAMP WITH TIME ZONE NOT NULL,
    traceback TEXT,
    meta TEXT,
    periodic_task_name VARCHAR(255) -- 自定义字段，用于关联定时任务
);

CREATE INDEX idx_taskresult_task_id ON django_celery_results_taskresult(task_id);
CREATE INDEX idx_taskresult_status ON django_celery_results_taskresult(status);
CREATE INDEX idx_taskresult_date_created ON django_celery_results_taskresult(date_created);
```

#### 1.12.2 Celery定时任务表 (django_celery_beat_periodictask)

```sql
CREATE TABLE django_celery_beat_periodictask (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    task VARCHAR(200) NOT NULL,
    args TEXT NOT NULL,
    kwargs TEXT NOT NULL,
    queue VARCHAR(200),
    exchange VARCHAR(200),
    routing_key VARCHAR(200),
    expires TIMESTAMP WITH TIME ZONE,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_run_at TIMESTAMP WITH TIME ZONE,
    total_run_count INTEGER NOT NULL DEFAULT 0,
    date_changed TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT,
    crontab_id INTEGER REFERENCES django_celery_beat_crontabschedule(id),
    interval_id INTEGER REFERENCES django_celery_beat_intervalschedule(id),
    solar_id INTEGER REFERENCES django_celery_beat_solarschedule(id),
    one_off BOOLEAN NOT NULL DEFAULT FALSE,
    start_time TIMESTAMP WITH TIME ZONE,
    priority INTEGER,
    headers TEXT NOT NULL,
    clocked_id INTEGER REFERENCES django_celery_beat_clockedschedule(id)
);
```

#### 1.12.3 Cron调度表 (django_celery_beat_crontabschedule)

```sql
CREATE TABLE django_celery_beat_crontabschedule (
    id SERIAL PRIMARY KEY,
    minute VARCHAR(240) NOT NULL DEFAULT '*',
    hour VARCHAR(96) NOT NULL DEFAULT '*',
    day_of_week VARCHAR(64) NOT NULL DEFAULT '*',
    day_of_month VARCHAR(124) NOT NULL DEFAULT '*',
    month_of_year VARCHAR(64) NOT NULL DEFAULT '*',
    timezone VARCHAR(63) NOT NULL DEFAULT 'UTC'
);
```

#### 1.12.4 间隔调度表 (django_celery_beat_intervalschedule)

```sql
CREATE TABLE django_celery_beat_intervalschedule (
    id SERIAL PRIMARY KEY,
    every INTEGER NOT NULL,
    period VARCHAR(24) NOT NULL
);
```

## 2. API接口文档

### 2.1 用户管理接口

#### 2.1.1 用户列表查询

**接口地址：** `GET /admin_api/system/user/`

**请求参数：**
```json
{
    "page": 1,
    "limit": 20,
    "name": "用户姓名(可选)",
    "username": "用户账号(可选)",
    "mobile": "手机号(可选)",
    "dept": "部门ID(可选)",
    "role": "角色ID(可选)"
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "username": "admin",
            "name": "管理员",
            "email": "admin@example.com",
            "mobile": "13800138000",
            "avatar": "/media/avatar/default.png",
            "gender": 1,
            "user_type": 0,
            "dept_id": 1,
            "dept_name": "总公司",
            "dept_name_all": "总公司/技术部",
            "role_info": [
                {
                    "id": 1,
                    "name": "管理员",
                    "key": "admin"
                }
            ],
            "is_active": true,
            "create_datetime": "2023-01-01T00:00:00Z"
        }
    ],
    "total": 100
}
```

#### 2.1.2 创建用户

**接口地址：** `POST /admin_api/system/user/`

**请求参数：**
```json
{
    "username": "testuser",
    "password": "123456",
    "name": "测试用户",
    "email": "test@example.com",
    "mobile": "13800138001",
    "gender": 1,
    "user_type": 0,
    "dept": 1,
    "role": [1, 2],
    "post": [1],
    "manage_dept": [1, 2]
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "创建成功",
    "data": {
        "id": 2,
        "username": "testuser",
        "name": "测试用户",
        "email": "test@example.com",
        "mobile": "13800138001",
        "gender": 1,
        "user_type": 0,
        "dept": 1,
        "create_datetime": "2023-01-01T00:00:00Z"
    }
}
```

#### 2.1.3 更新用户

**接口地址：** `PUT /admin_api/system/user/{id}/`

**请求参数：**
```json
{
    "name": "更新后的姓名",
    "email": "newemail@example.com",
    "mobile": "13800138002",
    "dept": 2,
    "role": [1, 3]
}
```

#### 2.1.4 删除用户

**接口地址：** `DELETE /admin_api/system/user/{id}/`

**响应格式：**
```json
{
    "code": 2000,
    "msg": "删除成功"
}
```

#### 2.1.5 重置用户密码

**接口地址：** `PUT /admin_api/system/user/{id}/reset_password/`

**请求参数：**
```json
{
    "password": "newpassword123"
}
```

### 2.2 角色管理接口

#### 2.2.1 角色列表查询

**接口地址：** `GET /admin_api/system/role/`

**请求参数：**
```json
{
    "page": 1,
    "limit": 20,
    "name": "角色名称(可选)",
    "key": "权限字符(可选)"
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "name": "管理员",
            "key": "admin",
            "sort": 1,
            "status": true,
            "users": [
                {
                    "id": 1,
                    "name": "管理员",
                    "dept__name": "总公司"
                }
            ],
            "create_datetime": "2023-01-01T00:00:00Z"
        }
    ],
    "total": 10
}
```

#### 2.2.2 创建角色

**接口地址：** `POST /admin_api/system/role/`

**请求参数：**
```json
{
    "name": "测试角色",
    "key": "test_role",
    "sort": 2,
    "status": true,
    "description": "测试角色描述"
}
```

#### 2.2.3 设置角色用户

**接口地址：** `PUT /admin_api/system/role/{id}/set_role_users/`

**请求参数：**
```json
{
    "direction": "right", // left: 移除用户权限, right: 添加用户权限
    "movedKeys": [1, 2, 3] // 用户ID列表
}
```

#### 2.2.4 获取角色用户

**接口地址：** `GET /admin_api/system/role/get_role_users/`

**请求参数：**
```json
{
    "role_id": 1,
    "authorized": "1", // 1: 已授权用户, 0: 未授权用户
    "name": "用户名(可选)",
    "dept": "部门ID(可选)"
}
```

### 2.3 部门管理接口

#### 2.3.1 部门列表查询

**接口地址：** `GET /admin_api/system/dept/`

**请求参数：**
```json
{
    "parent": "父部门ID(可选)",
    "name": "部门名称(可选)"
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "name": "总公司",
            "key": "company",
            "sort": 1,
            "owner": "张三",
            "phone": "010-12345678",
            "email": "company@example.com",
            "status": true,
            "parent": null,
            "parent_name": null,
            "status_label": "启用",
            "has_children": 2,
            "hasChild": true,
            "dept_user_count": 10,
            "create_datetime": "2023-01-01T00:00:00Z"
        }
    ]
}
```

#### 2.3.2 创建部门

**接口地址：** `POST /admin_api/system/dept/`

**请求参数：**
```json
{
    "name": "技术部",
    "key": "tech_dept",
    "parent": 1,
    "owner": "李四",
    "phone": "010-87654321",
    "email": "tech@example.com",
    "status": true,
    "description": "技术部门"
}
```

#### 2.3.3 部门信息统计

**接口地址：** `GET /admin_api/system/dept/dept_info/`

**请求参数：**
```json
{
    "dept_id": 1,
    "show_all": "1" // 1: 递归查询所有子部门, 0: 仅查询当前部门
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": {
        "dept_name": "技术部",
        "dept_user": 15,
        "owner": "李四",
        "description": "技术部门",
        "gender": {
            "male": 10,
            "female": 5,
            "unknown": 0
        },
        "sub_dept_map": [
            {
                "name": "前端组",
                "count": 8
            },
            {
                "name": "后端组",
                "count": 7
            }
        ]
    }
}
```

### 2.4 菜单管理接口

#### 2.4.1 菜单列表查询

**接口地址：** `GET /admin_api/system/menu/`

**请求参数：**
```json
{
    "parent": "父菜单ID(可选)",
    "name": "菜单名称(可选)",
    "status": "菜单状态(可选)"
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "parent": null,
            "icon": "el-icon-menu",
            "name": "系统管理",
            "sort": 1,
            "is_link": false,
            "link_url": null,
            "is_catalog": true,
            "web_path": "/system",
            "component": "Layout",
            "component_name": "System",
            "status": true,
            "cache": false,
            "visible": true,
            "is_iframe": false,
            "is_affix": false,
            "menuPermission": [
                {
                    "id": 1,
                    "name": "查询",
                    "value": "System:Search"
                }
            ],
            "hasChild": true,
            "create_datetime": "2023-01-01T00:00:00Z"
        }
    ]
}
```

#### 2.4.2 创建菜单

**接口地址：** `POST /admin_api/system/menu/`

**请求参数：**
```json
{
    "parent": 1,
    "icon": "el-icon-user",
    "name": "用户管理",
    "web_path": "/system/user",
    "component": "system/user/index",
    "component_name": "User",
    "status": true,
    "cache": true,
    "visible": true,
    "is_catalog": false,
    "is_link": false
}
```

#### 2.4.3 获取前端路由

**接口地址：** `GET /admin_api/system/menu/web_router/`

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "parent": null,
            "icon": "el-icon-menu",
            "sort": 1,
            "path": "/system",
            "name": "系统管理",
            "title": "系统管理",
            "is_link": false,
            "link_url": null,
            "is_catalog": true,
            "web_path": "/system",
            "component": "Layout",
            "component_name": "System",
            "cache": false,
            "visible": true,
            "is_iframe": false,
            "is_affix": false,
            "status": true
        }
    ],
    "total": 10
}
```

#### 2.4.4 菜单上移/下移

**接口地址：** `POST /admin_api/system/menu/move_up/` 或 `POST /admin_api/system/menu/move_down/`

**请求参数：**
```json
{
    "menu_id": 1
}
```

### 2.5 菜单按钮权限接口

#### 2.5.1 按钮权限列表

**接口地址：** `GET /admin_api/system/menu_button/`

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "name": "新增",
            "value": "User:Create",
            "api": "/admin_api/system/user/",
            "method": 1,
            "menu": 1
        }
    ]
}
```

#### 2.5.2 创建按钮权限

**接口地址：** `POST /admin_api/system/menu_button/`

**请求参数：**
```json
{
    "menu": 1,
    "name": "新增",
    "value": "User:Create",
    "api": "/admin_api/system/user/",
    "method": 1
}
```

#### 2.5.3 批量创建CRUD权限

**接口地址：** `POST /admin_api/system/menu_button/batch_create/`

**请求参数：**
```json
{
    "menu": 1
}
```

#### 2.5.4 获取用户所有按钮权限

**接口地址：** `GET /admin_api/system/menu_button/menu_button_all_permission/`

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": ["User:Create", "User:Update", "User:Delete", "User:Search"]
}
```

### 2.6 字段权限接口

#### 2.6.1 字段权限列表

**接口地址：** `GET /admin_api/system/menu_field/`

**请求参数：**
```json
{
    "menu": 1
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "model": "Users",
            "menu": 1,
            "field_name": "username",
            "title": "用户账号"
        }
    ]
}
```

#### 2.6.2 创建字段权限

**接口地址：** `POST /admin_api/system/menu_field/`

**请求参数：**
```json
{
    "model": "Users",
    "menu": 1,
    "field_name": "username",
    "title": "用户账号"
}
```

#### 2.6.3 获取所有模型

**接口地址：** `GET /admin_api/system/menu_field/get_models/`

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "app": "system",
            "title": "用户表",
            "key": "Users"
        }
    ]
}
```

#### 2.6.4 自动匹配字段

**接口地址：** `POST /admin_api/system/menu_field/auto_match_fields/`

**请求参数：**
```json
{
    "menu": 1,
    "model": "Users"
}
```

### 2.7 字典管理接口

#### 2.7.1 字典列表查询

**接口地址：** `GET /admin_api/system/dictionary/`

**请求参数：**
```json
{
    "parent": "父字典ID(可选)",
    "label": "字典名称(可选)"
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "label": "性别",
            "value": "gender",
            "parent": null,
            "type": 0,
            "color": null,
            "is_value": false,
            "status": true,
            "sort": 1,
            "remark": "性别字典",
            "create_datetime": "2023-01-01T00:00:00Z"
        }
    ]
}
```

#### 2.7.2 创建字典

**接口地址：** `POST /admin_api/system/dictionary/`

**请求参数：**
```json
{
    "label": "性别",
    "value": "gender",
    "parent": null,
    "type": 0,
    "status": true,
    "sort": 1,
    "remark": "性别字典"
}
```

#### 2.7.3 获取字典配置

**接口地址：** `GET /admin_api/system/dictionary/init_dictionary/`

**请求参数：**
```json
{
    "dictionary_key": "gender" // 或 "all" 获取所有字典
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "label": "男",
            "value": "1",
            "type": 1,
            "color": "blue"
        },
        {
            "label": "女",
            "value": "2",
            "type": 1,
            "color": "pink"
        }
    ]
}
```

### 2.8 地区管理接口

#### 2.8.1 地区列表查询

**接口地址：** `GET /admin_api/system/area/`

**请求参数：**
```json
{
    "pcode": "父地区编码(可选)",
    "page": 1,
    "limit": 999
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "name": "北京市",
            "code": "110000",
            "level": 1,
            "pinyin": "beijing",
            "initials": "B",
            "enable": true,
            "pcode": null,
            "pcode_count": 16,
            "hasChild": true,
            "pcode_info": [],
            "create_datetime": "2023-01-01T00:00:00Z"
        }
    ]
}
```

#### 2.8.2 创建地区

**接口地址：** `POST /admin_api/system/area/`

**请求参数：**
```json
{
    "name": "朝阳区",
    "code": "110105",
    "pcode": "110000",
    "enable": true
}
```

### 2.9 文件管理接口

#### 2.9.1 文件列表查询

**接口地址：** `GET /admin_api/system/file_list/`

**请求参数：**
```json
{
    "page": 1,
    "limit": 20,
    "name": "文件名(可选)",
    "mime_type": "文件类型(可选)",
    "file_type": "文件分类(可选)",
    "upload_method": "上传方式(可选)"
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "name": "avatar.png",
            "url": "media/files/a/b/abc123.png",
            "file_url": "https://example.com/media/files/a/b/abc123.png",
            "engine": "local",
            "mime_type": "image/png",
            "size": "102400",
            "md5sum": "abc123def456",
            "upload_method": 0,
            "file_type": 0,
            "create_datetime": "2023-01-01T00:00:00Z"
        }
    ],
    "total": 100
}
```

#### 2.9.2 上传文件

**接口地址：** `POST /admin_api/system/file_list/`

**请求参数：** (multipart/form-data)
```
file: 文件对象
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "上传成功",
    "data": {
        "id": 1,
        "name": "avatar.png",
        "url": "media/files/a/b/abc123.png",
        "file_url": "https://example.com/media/files/a/b/abc123.png",
        "engine": "local",
        "mime_type": "image/png",
        "size": "102400",
        "md5sum": "abc123def456",
        "upload_method": 0,
        "file_type": 0
    }
}
```

### 2.10 操作日志接口

#### 2.10.1 操作日志列表

**接口地址：** `GET /admin_api/system/operation_log/`

**请求参数：**
```json
{
    "page": 1,
    "limit": 20,
    "request_modular": "请求模块(可选)",
    "request_method": "请求方式(可选)",
    "status": "响应状态(可选)"
}
```

**响应格式：**
```json
{
    "code": 2000,
    "msg": "获取成功",
    "data": [
        {
            "id": 1,
            "request_modular": "用户管理",
            "request_path": "/admin_api/system/user/",
            "request_body": "{\"username\":\"test\"}",
            "request_method": "POST",
            "request_msg": "创建用户",
            "request_ip": "192.168.1.100",
            "request_browser": "Chrome",
            "response_code": "200",
            "request_os": "Windows 10",
            "json_result": "{\"code\":2000,\"msg\":\"创建成功\"}",
            "status": true,
            "create_datetime": "2023-01-01T00:00:00Z"
        }
    ],
    "total": 1000
}
```

## 3. 数据权限说明

### 3.1 数据权限范围

系统支持以下数据权限范围：
- 0: 仅本人数据权限
- 1: 本部门及以下数据权限  
- 2: 本部门数据权限
- 3: 全部数据权限
- 4: 自定数据权限

### 3.2 字段权限控制

字段权限支持以下操作：
- is_query: 是否可查询
- is_create: 是否可创建时填写
- is_update: 是否可更新

### 3.3 按钮权限控制

按钮权限通过MenuButton表管理，支持：
- 菜单级别的按钮权限
- API接口级别的权限控制
- HTTP方法级别的权限控制

## 4. 注意事项

### 4.1 数据库迁移

1. 使用PostgreSQL 18时，需要注意JSON字段的兼容性
2. 所有表都包含审计字段，需要在应用层维护
3. 外键约束使用`db_constraint=False`，需要在应用层保证数据一致性

### 4.2 密码处理

用户密码使用MD5+Django内置hash进行双重加密：
```python
def set_password(self, raw_password):
    if raw_password:
        super().set_password(hashlib.md5(raw_password.encode(encoding="UTF-8")).hexdigest())
```

### 4.3 软删除

项目支持软删除功能，通过`is_deleted`字段标记删除状态。

### 4.5 文件存储

支持多种文件存储引擎：
- local: 本地存储
- oss: 阿里云OSS
- cos: 腾讯云COS

## 5. 扩展建议

### 5.1 索引优化

建议为以下字段添加索引：
```sql
-- 用户表索引
CREATE INDEX idx_users_dept_id ON users(dept_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_mobile ON users(mobile);

-- 操作日志索引
CREATE INDEX idx_operation_log_create_time ON operation_log(create_datetime);
CREATE INDEX idx_operation_log_request_ip ON operation_log(request_ip);
CREATE INDEX idx_operation_log_creator ON operation_log(creator_id);

-- 菜单表索引
CREATE INDEX idx_menu_parent_id ON menu(parent_id);
CREATE INDEX idx_menu_component_name ON menu(component_name);
```

### 5.2 性能优化

1. 对于大数据量的操作日志表，建议按时间分表
2. 定期清理过期的任务结果数据
3. 使用Redis缓存字典数据和权限数据
4. 对文件上传实现分片上传和断点续传

### 5.3 安全加固

1. API接口添加访问频率限制
2. 敏感操作添加二次验证
3. 定期备份重要数据
4. 实现操作审计和异常监控

---

本文档基于Django-Vue3-Admin项目v3.0.8版本提取，适用于PostgreSQL 18数据库实现。在实际使用时，请根据具体需求进行调整和优化。