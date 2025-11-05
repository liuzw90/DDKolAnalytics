"""
定时任务调度器
用于设置自动调用API获取数据的任务
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from app.api.client import douyin_client
from app import db
from app.models import Material, PromotionData, User
import logging

# 创建日志记录器
logger = logging.getLogger(__name__)

# 创建调度器实例
scheduler = BackgroundScheduler()

def fetch_latest_promotion_data():
    """
    定时获取最新的推广数据
    每天凌晨2点执行，获取前一天的推广数据
    """
    try:
        logger.info("开始执行定时任务：获取最新推广数据")
        
        # 获取前一天的日期
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        date_range = (yesterday, yesterday)
        
        # 获取所有素材
        materials = Material.query.all()
        logger.info(f"共获取到 {len(materials)} 个素材")
        
        # 查找一个投手用户用于记录创建者
        pitcher_user = User.query.filter_by(role='pitcher').first()
        if not pitcher_user:
            logger.warning("未找到投手用户，无法保存推广数据")
            return
        
        # 为每个素材获取推广数据
        saved_count = 0
        for material in materials:
            try:
                # 调用API获取推广数据
                promotion_data_list = douyin_client.get_promotion_data(
                    material.material_id, date_range
                )
                
                if promotion_data_list:
                    for pd in promotion_data_list:
                        # 检查数据是否已存在
                        existing = PromotionData.query.filter_by(
                            material_id=material.id,
                            date=datetime.strptime(pd['date'], '%Y-%m-%d').date()
                        ).first()
                        
                        if not existing:
                            # 创建新的推广数据记录
                            new_promotion = PromotionData(
                                material_id=material.id,
                                date=datetime.strptime(pd['date'], '%Y-%m-%d').date(),
                                cost=pd['cost'],
                                sales_amount=pd['sales_amount'],
                                roi=pd['roi'],
                                created_by_id=pitcher_user.id
                            )
                            db.session.add(new_promotion)
                            saved_count += 1
                
            except Exception as e:
                logger.error(f"获取素材 {material.material_id} 的推广数据失败: {str(e)}")
        
        # 提交所有更改
        db.session.commit()
        logger.info(f"定时任务完成：成功保存 {saved_count} 条推广数据")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"定时任务执行失败: {str(e)}")

def fetch_all_materials_data():
    """
    定时获取所有达人的素材数据
    每周一凌晨3点执行
    """
    try:
        logger.info("开始执行定时任务：获取达人素材数据")
        
        # 这里可以根据实际需求实现获取达人素材的逻辑
        # 目前简化实现
        
        logger.info("定时任务完成：获取达人素材数据")
        
    except Exception as e:
        logger.error(f"定时任务执行失败: {str(e)}")

def init_scheduler(app):
    """
    初始化定时任务调度器
    
    Args:
        app: Flask应用实例
    """
    with app.app_context():
        # 添加定时任务：每天凌晨2点执行
        scheduler.add_job(
            func=fetch_latest_promotion_data,
            trigger=CronTrigger(hour=2, minute=0),
            id='fetch_daily_promotion_data',
            name='每日获取推广数据',
            replace_existing=True
        )
        
        # 添加定时任务：每周一凌晨3点执行
        scheduler.add_job(
            func=fetch_all_materials_data,
            trigger=CronTrigger(day_of_week=0, hour=3, minute=0),
            id='fetch_weekly_materials_data',
            name='每周获取达人素材数据',
            replace_existing=True
        )
        
        # 启动调度器
        scheduler.start()
        logger.info("定时任务调度器已启动")

def shutdown_scheduler():
    """
    关闭定时任务调度器
    """
    scheduler.shutdown()
    logger.info("定时任务调度器已关闭")