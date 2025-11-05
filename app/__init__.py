"""
Flask应用初始化模块
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
import os
import logging

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置应用
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://admin:password@localhost/ddkol')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # 配置登录视图
    login_manager.login_view = 'accounts.login'
    login_manager.login_message = '请先登录后再访问'
    login_manager.login_message_category = 'info'
    
    # 注册蓝图
    from app.views.accounts import accounts_bp
    from app.views.influencers import influencers_bp
    from app.views.promotions import promotions_bp
    from app.views.dashboard import dashboard_bp
    from app.api.routes import api_bp
    
    app.register_blueprint(accounts_bp)
    app.register_blueprint(influencers_bp)
    app.register_blueprint(promotions_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 加载用户回调
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # 错误处理
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500
    
    # 初始化定时任务
    from app.utils.scheduler import init_scheduler
    init_scheduler(app)
    
    # 应用上下文销毁时关闭调度器
    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        from app.utils.scheduler import shutdown_scheduler as stop_scheduler
        stop_scheduler()
    
    return app

# 导入需要在应用上下文中运行的模块
from app.models import User, Influencer, Material, MaterialTag, PromotionData