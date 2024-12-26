# 应届生就业管理系统

基于 Django REST Framework 开发的应届生就业管理系统后端 API。

## 技术栈

- Python 3.8+
- Django 5.1.3
- Django REST Framework 3.15.2
- MySQL 8.0
- Redis 5.2.0
- JWT 认证
- SimpleUI 管理后台

## 项目结构

```
d1/
├── app/                    # 主应用目录
│   ├── migrations/        # 数据库迁移文件
│   ├── serializers/       # 序列化器
│   │   ├── student.py     # 学生相关序列化器
│   │   ├── teacher.py     # 教师相关序列化器
│   │   ├── notice.py      # 通知相关序列化器
│   │   ├── survey.py      # 问卷相关序列化器
│   │   └── teacher_manage.py  # 教师管理相关序列化器
│   ├── utils/            # 工具类
│   │   ├── captcha.py     # 验证码工具
│   │   ├── ernie_bot.py   # 百度文心一言 AI 工具
│   │   └── exception_handler.py  # 异常处理器
│   ├── views/            # 视图目录
│   │   ├── all/          # 公共视图
│   │   ├── stu/          # 学生相���视图
│   │   └── teacher/      # 教师相关视图
│   ├── models.py         # 数据模型
│   └── urls.py           # URL 配置
├── d1/                    # 项目配置目录
│   ├── settings.py       # 项目设置
│   └── urls.py           # 主 URL 配置
└── requirements.txt       # 项目依赖
```

## 功能模块

### 1. 认证模块

#### 1.1 验证码（app/utils/captcha.py）
- 生成图片验证码
- 验证码存储与验证
- 支持自定义过期时间

#### 1.2 用户认证
- JWT Token 认证（access token + refresh token）
- Token 刷新机制
- 手机号/学号 + 密码登录
- 验证码校验

### 2. 学生模块（app/views/stu/）

#### 2.1 账户管理（auth.py）
- 学生注册
- 学生登录
- 密码修改

#### 2.2 个人信息（student.py）
- 获取/更新个人信息
- 头像上传
- 就业/升学状态管理
- 意向省份/城市选择

#### 2.3 通知管理（notice.py）
- 查看通知列表
- 标记通知已读
- 未读通知统计
- 通知筛选（已读/未读）

#### 2.4 问卷管理（survey.py）
- 查看可用问卷
- 提交问卷答复
- 查看问卷状态

#### 2.5 AI 咨询（ai_consultant.py）
- 智能就业咨询
- 基于文心一言的对话系统
- 个性化建议生成

### 3. 教师模块（app/views/teacher/）

#### 3.1 账户管理（auth.py）
- 教师登录
- 密码修改

#### 3.2 个人信息（profile.py）
- 获取/更新个人信息
- 头像管理

#### 3.3 班级管理（manage_class.py）
- 创建/编辑/删除班级
- 班级学生管理
- 班级列表查询

#### 3.4 学生管理（manage.py）
- 学生信息管理
- 学生状态管理
- 批量导入学生

#### 3.5 通知管理（manage_notice.py）
- 发布/编辑/删除通知
- 查看通知阅读状态
- 通知发送记录

#### 3.6 问卷管理（survey.py）
- 问卷统计分析
- 查看问卷详情
- 导出问卷数据

#### 3.7 数据统计（statistics.py）
- 班级人数统计
- 就业率统计
- 地区分布统计
- 数据可视化

### 4. 公共模块（app/views/all/）

#### 4.1 基础数据
- 获取班级列表
- 获取教师列表
- 获取验证码

#### 4.2 Token 管理
- Token 刷新
- Token 验证

### 5. 数据模型（app/models.py）

#### 5.1 用户模型
- Teacher：教师模型
- Student：学生模型
- Class：班级模型

#### 5.2 业务模型
- Notice：通知模型
- Survey：问卷模型
- SurveyResponse：问卷回答模型

## API 响应规范

### 成功响应
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": null
}
```

### 错误响应
```json
{
    "status": "false",
    "code": 400,
    "message": "错误信息"
}
```

## 错误码说明

- 400：请求参数错误
- 401：未认证或认证已过期
- 403：权限不足
- 404：资源不存在
- 500：服务器内部错误

## 安装部署

1. 克隆项目
```bash
git clone <项目地址>
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置数据库
```python
# d1/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'graduate',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

4. 配置 Redis
```python
# d1/settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

5. 运行迁移
```bash
python manage.py migrate
```

6. 创建超级用户
```bash
python manage.py createsuperuser
```

7. 启动服务
```bash
python manage.py runserver
```

## 作者

- 作者：[杨海浪]
- 邮箱：202162238@huat.edu.cn 