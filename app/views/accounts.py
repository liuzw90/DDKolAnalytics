"""
用户账户视图
处理用户登录、注册、注销和仪表盘功能
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User
from app.forms import LoginForm, UserRegisterForm

# 创建账户蓝图
accounts_bp = Blueprint('accounts', __name__, template_folder='templates')

@accounts_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录视图
    """
    # 如果用户已登录，重定向到仪表盘
    if current_user.is_authenticated:
        return redirect(url_for('accounts.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter_by(username=form.username.data).first()
        
        # 验证用户和密码
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # 登录用户
            login_user(user, remember=form.remember.data)
            
            # 获取下一个页面参数
            next_page = request.args.get('next')
            
            flash('登录成功', 'success')
            return redirect(next_page) if next_page else redirect(url_for('accounts.dashboard'))
        else:
            flash('登录失败，请检查用户名和密码', 'danger')
    
    return render_template('accounts/login.html', title='登录', form=form)

@accounts_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册视图
    """
    # 如果用户已登录，重定向到仪表盘
    if current_user.is_authenticated:
        return redirect(url_for('accounts.dashboard'))
    
    form = UserRegisterForm()
    
    if form.validate_on_submit():
        # 生成密码哈希
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # 创建新用户
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            role=form.role.data
        )
        
        # 保存用户到数据库
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('accounts.login'))
    
    return render_template('accounts/register.html', title='注册', form=form)

@accounts_bp.route('/logout')
def logout():
    """
    用户注销视图
    """
    logout_user()
    return redirect(url_for('accounts.login'))

@accounts_bp.route('/dashboard')
@login_required
def dashboard():
    """
    用户仪表盘视图
    显示不同角色的用户仪表盘
    """
    # 根据用户角色渲染不同的仪表盘内容
    if current_user.is_business():
        # 商务用户仪表盘
        # 显示该商务创建的达人数量和素材数量
        influencers_count = User.query.get(current_user.id).created_influencers.count()
        materials_count = User.query.get(current_user.id).created_materials.count()
        
        context = {
            'title': '商务仪表盘',
            'user_type': '商务',
            'stats': {
                'influencers_count': influencers_count,
                'materials_count': materials_count
            }
        }
        
    elif current_user.is_pitcher():
        # 投手用户仪表盘
        # 显示所有可查看的素材数量和推广数据数量
        materials_count = User.query.get(current_user.id).created_materials.count()
        promotions_count = User.query.get(current_user.id).created_promotions.count()
        
        context = {
            'title': '投手仪表盘',
            'user_type': '投手',
            'stats': {
                'materials_count': materials_count,
                'promotions_count': promotions_count
            }
        }
    else:
        # 默认仪表盘
        context = {
            'title': '仪表盘',
            'user_type': '用户',
            'stats': {}
        }
    
    return render_template('accounts/dashboard.html', **context)