# KOL Analytics 系统

## 项目概述
KOL Analytics 系统是一个用于管理达人（KOL）信息和推广数据的分析平台。系统支持商务账号和投手账号两种角色，实现了完整的数据录入、查询、管理和权限控制功能。

## 功能特性

### 1. 用户认证与权限管理
- 支持两种角色：商务账号和投手账号
- 基于角色的访问控制（RBAC）
- 安全的密码验证和会话管理

### 2. 达人数据管理
- 达人信息录入和编辑
- 支持多标签分类
- 达人搜索和筛选
- 素材管理和关联

### 3. 推广数据分析
- 推广数据录入和查询
- ROI 自动计算
- 数据验证和错误处理
- 基于用户角色的数据访问控制

### 4. 系统特性
- 美观的 Bootstrap 5 界面
- 响应式设计，支持移动端
- 完善的异常处理机制
- 友好的错误提示页面

## 技术栈

- **后端框架**：Django 4.2.10
- **数据库**：MySQL
- **前端**：Bootstrap 5
- **表单处理**：django-crispy-forms
- **数据导入导出**：django-import-export
- **配置管理**：django-decouple

## 安装部署

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+
- pip 包管理工具

### 2. 安装步骤

#### 2.1 克隆项目
```bash
git clone <repository-url>
cd DDKolAnalytics
```

#### 2.2 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.4 配置环境变量
创建 `.env` 文件，包含以下配置：
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=kol_analytics
DB_USER=root
DB_PASSWORD=your-database-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

#### 2.5 数据库迁移
```bash
python manage.py migrate
```

#### 2.6 创建超级用户
```bash
python manage.py createsuperuser
```

#### 2.7 运行开发服务器
```bash
python manage.py runserver
```

## 使用说明

### 1. 登录系统
访问 `http://127.0.0.1:8000/accounts/login/` 登录系统。

### 2. 角色功能

#### 2.1 商务账号
- 管理所有达人信息和标签
- 查看所有推广数据
- 添加和管理素材

#### 2.2 投手账号
- 录入推广数据
- 查看自己录入的推广数据
- 编辑和删除自己的数据

### 3. 主要模块

#### 3.1 达人管理
- 达人列表：`/influencers/list/`
- 添加达人：`/influencers/create/`
- 达人详情：`/influencers/<pk>/`
- 标签管理：`/influencers/tags/`

#### 3.2 素材管理
- 素材列表：`/influencers/materials/`
- 添加素材：`/influencers/materials/create/`

#### 3.3 推广数据
- 推广数据列表：`/promotions/`
- 添加推广数据：`/promotions/create/`
- 推广数据详情：`/promotions/<pk>/`

## 系统配置

### 1. 数据库配置
在 `kol_analytics/settings.py` 中配置数据库连接信息：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

### 2. 静态文件配置
```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 项目结构
```
DDKolAnalytics/
├── accounts/           # 用户认证应用
├── influencers/        # 达人管理应用
├── promotions/         # 推广数据应用
├── kol_analytics/      # 项目配置目录
├── templates/          # HTML模板
│   ├── accounts/       # 账号相关模板
│   ├── influencers/    # 达人相关模板
│   ├── promotions/     # 推广数据模板
│   └── errors/         # 错误页面模板
├── static/             # 静态资源文件
├── manage.py           # Django管理脚本
├── requirements.txt    # 项目依赖
└── README.md           # 项目文档
```

## 常见问题

### 1. 数据库连接失败
- 检查数据库服务是否运行
- 验证 `.env` 文件中的数据库配置是否正确
- 确保 MySQL 用户有足够的权限

### 2. 静态文件无法加载
- 确保 `STATIC_URL` 和 `STATICFILES_DIRS` 配置正确
- 运行 `python manage.py collectstatic` 收集静态文件

### 3. 权限错误
- 检查用户角色是否正确设置
- 验证视图函数中的权限装饰器是否正确使用

## 许可证
本项目仅供内部使用，未经授权不得用于商业用途。

## 更新日志

### v1.0.0
- 初始版本发布
- 实现完整的达人管理和推广数据分析功能
- 支持用户权限控制和数据验证