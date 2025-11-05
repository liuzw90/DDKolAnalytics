# DDKolAnalytics 系统

## 项目概述
DDKolAnalytics 系统是一个基于 Flask 的达人（KOL）信息管理和推广数据分析平台。系统支持商务用户和投手用户两种角色，实现了完整的数据录入、查询、管理、分析和权限控制功能，帮助团队高效管理达人资源和评估推广效果。

## 功能特性

### 1. 用户认证与权限管理
- 支持两种角色：商务用户和投手用户
- 基于角色的访问控制（RBAC）
- 安全的密码哈希存储和会话管理
- 不同角色有不同的数据访问权限

### 2. 达人数据管理
- 达人信息的增删改查操作
- 达人标签管理和分类
- 达人搜索功能
- 素材信息关联和管理

### 3. 素材管理
- 素材信息的录入和编辑
- 素材标签分类
- 素材统计数据展示
- 与达人的关联管理

### 4. 推广数据分析
- 推广数据的录入、编辑、删除和查询
- ROI 自动计算和展示
- 数据验证和错误处理
- 转化漏斗和ROI分析图表
- 基于用户角色的数据访问控制（商务用户只能操作自己创建的数据）

### 5. 系统特性
- 美观的 Bootstrap 样式界面
- 响应式设计，支持移动端访问
- 完善的异常处理和错误页面
- 实时搜索和结果过滤
- 数据可视化展示

## 技术栈

- **后端框架**：Flask 3.0.3
- **数据库**：PostgreSQL
- **ORM**：SQLAlchemy 3.1.1
- **用户认证**：Flask-Login 0.6.3
- **表单处理**：Flask-WTF 1.2.1
- **密码加密**：Flask-Bcrypt 1.0.1
- **数据迁移**：Flask-Migrate 4.0.7
- **配置管理**：python-dotenv 1.0.0
- **数据分析**：pandas 2.1.4, matplotlib 3.8.2
- **前端**：HTML5, CSS3, JavaScript, Bootstrap

## 安装部署

### 1. 环境要求
- Python 3.8+
- PostgreSQL 12+
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
确保 `.env` 文件包含以下配置（可根据需要修改）：
```
# 数据库配置
DATABASE_URL="postgresql://admin:password@localhost:5432/example_db"

# 应用配置
SECRET_KEY="your-secret-key-change-in-production"
FLASK_APP="app"
FLASK_ENV="development"
FLASK_DEBUG="True"
FLASK_HOST="0.0.0.0"
FLASK_PORT="5000"

# API配置（示例）
DOUYIN_API_KEY="your-douyin-api-key"
DOUYIN_API_SECRET="your-douyin-api-secret"
```

#### 2.5 初始化数据库
```bash
python init_db.py
```

该命令会自动创建数据库表并初始化默认用户：
- 管理员（投手）: username=admin, password=admin123
- 商务用户: username=business, password=business123

#### 2.6 运行开发服务器
```bash
python app.py
```

## 使用说明

### 1. 登录系统
访问 `http://localhost:5000/login` 登录系统。

### 2. 角色功能

#### 2.1 商务用户
- 只能管理自己创建的达人信息
- 只能管理自己创建的素材
- 可以查看所有推广数据
- 可以管理标签

#### 2.2 投手用户（管理员）
- 可以管理所有达人信息
- 可以管理所有素材
- 可以管理所有推广数据
- 拥有系统的全部权限

### 3. 主要模块

#### 3.1 仪表盘
- 访问首页查看数据概览
- 展示达人总数、素材总数、推广数据总数
- 显示最近的推广数据记录

#### 3.2 达人管理
- 达人列表：`/influencers`
- 添加达人：`/influencers/add`
- 达人详情：`/influencers/<id>`
- 编辑达人：`/influencers/<id>/edit`

#### 3.3 素材管理
- 素材列表：`/materials`
- 添加素材：`/materials/add`
- 素材详情：`/materials/<id>`
- 编辑素材：`/materials/<id>/edit`
- 标签管理：`/tags`

#### 3.4 推广数据
- 推广数据列表：`/promotions`
- 添加推广数据：`/promotions/add`
- 推广数据详情：`/promotions/<id>`
- 编辑推广数据：`/promotions/<id>/edit`

#### 3.5 搜索功能
- 全局搜索：`/search?q=关键词&type=类型`
- 支持搜索达人、素材和推广数据
- 可按类型筛选搜索结果

## 系统配置

### 1. 数据库配置
在 `.env` 文件中配置数据库连接信息：
```
DATABASE_URL="postgresql://admin:password@localhost:5432/example_db"
```

### 2. 应用配置
```
# 调试模式
FLASK_DEBUG="True"
# 监听地址
FLASK_HOST="0.0.0.0"
# 监听端口
FLASK_PORT="5000"
# 密钥（生产环境务必修改）
SECRET_KEY="your-secret-key-change-in-production"
```

## 项目结构
```
DDKolAnalytics/
├── app/                # 主应用目录
│   ├── __init__.py     # 应用初始化
│   ├── api/            # API相关模块
│   ├── forms/          # 表单定义
│   ├── models/         # 数据库模型
│   ├── static/         # 静态资源文件
│   │   ├── css/        # 样式文件
│   │   └── js/         # JavaScript文件
│   ├── templates/      # HTML模板
│   │   ├── accounts/   # 账号相关模板
│   │   ├── errors/     # 错误页面
│   │   ├── influencers/# 达人相关模板
│   │   ├── promotions/ # 推广相关模板
│   │   ├── base.html   # 基础模板
│   │   ├── dashboard.html # 仪表盘
│   │   ├── login.html  # 登录页面
│   │   └── search_results.html # 搜索结果
│   ├── utils/          # 工具函数
│   └── views/          # 视图函数
│       ├── accounts.py # 账号视图
│       ├── influencers.py # 达人视图
│       └── promotions.py # 推广视图
├── app.py              # 应用入口
├── init_db.py          # 数据库初始化脚本
├── requirements.txt    # 项目依赖
├── .env                # 环境变量配置
└── README.md           # 项目文档
```

## 常见问题

### 1. 数据库连接失败
- 检查 PostgreSQL 服务是否运行
- 验证 `.env` 文件中的数据库配置是否正确
- 确保数据库用户有足够的权限

### 2. 权限错误
- 检查用户角色是否正确设置
- 商务用户只能操作自己创建的数据
- 投手用户可以操作所有数据

### 3. 服务器启动失败
- 检查端口是否被占用
- 确保所有依赖已正确安装
- 查看错误日志获取详细信息

## 开发说明

### 1. 添加新功能
- 在 `app/views/` 中添加新的视图函数
- 在 `app/templates/` 中创建对应的模板文件
- 在 `app/models/` 中定义相关的数据模型
- 在 `app/__init__.py` 中注册新的蓝图（如果需要）

### 2. 数据库迁移
- 使用 Flask-Migrate 进行数据库迁移
- 生成迁移：`flask db migrate -m "描述信息"`
- 应用迁移：`flask db upgrade`

## 许可证
本项目仅供内部使用，未经授权不得用于商业用途。

## 更新日志

### v2.0.0
- 项目从 Django 重构为 Flask 框架
- 数据库从 MySQL 迁移到 PostgreSQL
- 优化了用户角色权限控制
- 增强了数据分析和可视化功能
- 完善了错误处理机制

### v1.0.0
- 初始版本发布
- 实现基本的达人管理和推广数据分析功能