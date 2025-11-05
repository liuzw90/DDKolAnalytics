"""
数据库初始化脚本
"""

from app import app, db
from app.models import User, InfluencerTag, MaterialTag

# 创建应用上下文
with app.app_context():
    # 创建所有表
    db.create_all()
    
    # 检查是否已有用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # 创建默认管理员用户（投手角色）
        admin = User(
            username='admin',
            email='admin@example.com',
            role='pitcher'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # 创建默认商务用户
        business = User(
            username='business',
            email='business@example.com',
            role='business'
        )
        business.set_password('business123')
        db.session.add(business)
        
        # 添加一些默认标签
        default_influencer_tags = ['美妆', '时尚', '美食', '旅游', '健身']
        for tag_name in default_influencer_tags:
            tag = InfluencerTag(name=tag_name)
            db.session.add(tag)
        
        default_material_tags = ['产品展示', '教程', '开箱', '测评', '种草']
        for tag_name in default_material_tags:
            tag = MaterialTag(name=tag_name)
            db.session.add(tag)
        
        db.session.commit()
        print("数据库初始化完成！")
        print("默认用户：")
        print("- 管理员（投手）: username=admin, password=admin123")
        print("- 商务用户: username=business, password=business123")
    else:
        print("数据库已存在，跳过初始化")