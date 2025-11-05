"""
数据库模型定义
"""

from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    """用户加载器，用于Flask-Login"""
    return User.query.get(int(user_id))

# 用户表
class User(db.Model, UserMixin):
    """用户表，包含商务和投手两类用户"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # 增加长度以适应哈希值
    role = db.Column(db.String(20), nullable=False)  # 'business' 或 'pitcher'
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系 - 兼容现有和新增的引用方式
    created_influencers = relationship('Influencer', backref='created_by', lazy=True)
    created_materials = relationship('Material', backref='created_by', lazy=True)
    created_promotions = relationship('PromotionData', backref='created_by', lazy=True)
    influencers = relationship('Influencer', backref='created_by_user', lazy=True)
    materials = relationship('Material', backref='created_by_user', lazy=True)
    promotions = relationship('PromotionData', backref='created_by_user', lazy=True)
    
    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password, password)
    
    def is_business(self):
        return self.role == 'business'
    
    def is_pitcher(self):
        return self.role == 'pitcher'
    
    def get_role_display(self):
        return '商务' if self.role == 'business' else '投手'
    
    def __repr__(self):
        return f'<User {self.username}>'

# 达人标签表
class InfluencerTag(db.Model):
    """达人标签表，用于存储达人的各种标签"""
    __tablename__ = 'influencer_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    influencers = relationship('Influencer', secondary='influencer_tag_association', back_populates='tags')
    
    @property
    def usage_count(self):
        """获取标签使用次数"""
        return len(self.influencers)
    
    def __repr__(self):
        return f'<InfluencerTag {self.name}>'

# 达人-标签关联表（多对多关系）
influencer_tag_association = db.Table('influencer_tag_association',
    db.Column('influencer_id', db.Integer, db.ForeignKey('influencers.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('influencer_tags.id'), primary_key=True)
)

# 达人信息表
class Influencer(db.Model):
    """达人信息表，存储达人的基本信息"""
    __tablename__ = 'influencers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    douyin_id = db.Column(db.String(100), nullable=False)
    uid = db.Column(db.String(100), unique=True, nullable=False)
    product_link = db.Column(db.String(200), nullable=True)
    influencer_level = db.Column(db.String(50), nullable=True)
    follower_count = db.Column(db.Integer, default=0)  # 新增粉丝数
    avg_views = db.Column(db.Integer, default=0)  # 新增平均播放量
    contact_info = db.Column(db.String(200))  # 新增联系方式
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 兼容新增的引用方式
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    materials = relationship('Material', backref='influencer', lazy=True, cascade='all, delete-orphan')
    promotions = relationship('PromotionData', backref='influencer', lazy=True)
    tags = relationship('InfluencerTag', secondary='influencer_tag_association', back_populates='influencers')
    
    def __repr__(self):
        return f'<Influencer {self.name}>'

# 素材标签表
class MaterialTag(db.Model):
    """素材标签表，用于存储素材的各种标签"""
    __tablename__ = 'material_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    materials = relationship('Material', secondary='material_tag_association', back_populates='tags')

# 素材-标签关联表（多对多关系）
material_tag_association = db.Table('material_tag_association',
    db.Column('material_id', db.Integer, db.ForeignKey('materials.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('material_tags.id'), primary_key=True)
)

# 素材表
class Material(db.Model):
    """素材表，存储达人的视频素材信息"""
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
    material_id = db.Column(db.String(100), unique=True, nullable=False)
    video_url = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200))  # 新增标题
    material_type = db.Column(db.String(50))  # 新增素材类型
    play_count = db.Column(db.Integer, default=0)  # 新增播放量
    like_count = db.Column(db.Integer, default=0)  # 新增点赞量
    comment_count = db.Column(db.Integer, default=0)  # 新增评论量
    share_count = db.Column(db.Integer, default=0)  # 新增分享量
    publish_time = db.Column(db.DateTime)  # 新增发布时间
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 兼容新增的引用方式
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    tags = relationship('MaterialTag', secondary='material_tag_association', back_populates='materials')
    promotion_data = relationship('PromotionData', backref='material', lazy=True, cascade='all, delete-orphan')
    promotions = relationship('PromotionData', backref='material_ref', lazy=True)  # 兼容新增的引用方式
    
    def __repr__(self):
        return f'<Material {self.material_id}>'

# 推广数据表
class PromotionData(db.Model):
    """推广数据表，存储每个素材的推广数据"""
    __tablename__ = 'promotion_data'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 新增推广名称
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'))  # 新增达人关联
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    exposure_count = db.Column(db.Integer, default=0)  # 新增曝光量
    click_count = db.Column(db.Integer, default=0)  # 新增点击量
    conversion_count = db.Column(db.Integer, default=0)  # 新增转化量
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    sales_amount = db.Column(db.Numeric(10, 2), nullable=False)
    revenue = db.Column(db.Numeric(10, 2), nullable=False)  # 新增收入字段（与sales_amount保持一致）
    roi = db.Column(db.Numeric(6, 2), nullable=True)
    notes = db.Column(db.Text)  # 新增备注
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 兼容新增的引用方式
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('material_id', 'date', name='_material_date_uc'),)
    
    # 计算ROI
    def calculate_roi(self):
        if self.cost > 0:
            self.roi = (self.sales_amount - self.cost) / self.cost
        else:
            self.roi = None
    
    # 计算属性
    @property
    def ctr(self):
        """计算点击率"""
        if self.exposure_count > 0:
            return self.click_count / self.exposure_count
        return 0
    
    @property
    def conversion_rate(self):
        """计算转化率"""
        if self.click_count > 0:
            return self.conversion_count / self.click_count
        return 0
    
    @property
    def roas(self):
        """计算ROAS（广告支出回报率）"""
        if self.cost > 0:
            return float(self.sales_amount / self.cost)
        return 0
    
    # 设置revenue时同步更新sales_amount
    @revenue.setter
    def revenue(self, value):
        self.sales_amount = value
    
    # 获取revenue时返回sales_amount
    @revenue.getter
    def revenue(self):
        return self.sales_amount
    
    def __repr__(self):
        return f'<PromotionData {self.name or "推广数据"}>'

# 别名，保持兼容性
Promotion = PromotionData

# 导出所有模型
__all__ = ['db', 'User', 'Influencer', 'Material', 'PromotionData', 'Promotion', 'MaterialTag', 'InfluencerTag']