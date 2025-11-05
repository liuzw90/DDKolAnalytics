"""
数据库模型设计文件
使用Django ORM进行数据库设计
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

# 自定义用户模型，扩展AbstractUser
class User(AbstractUser):
    """用户表，包含商务和投手两类用户"""
    ROLE_CHOICES = [
        ('business', '商务'),
        ('pitcher', '投手'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='用户角色')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        db_table = 'users'

# 达人信息表
class Influencer(models.Model):
    """达人信息表，存储达人的基本信息"""
    name = models.CharField(max_length=100, verbose_name='达人名称')
    douyin_id = models.CharField(max_length=100, verbose_name='抖音号')
    uid = models.CharField(max_length=100, verbose_name='UID', unique=True)
    product_link = models.URLField(verbose_name='挂车商品链接', blank=True, null=True)
    influencer_level = models.CharField(max_length=50, verbose_name='达人等级', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_influencers', verbose_name='创建者')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '达人信息'
        verbose_name_plural = '达人信息管理'
        db_table = 'influencers'

# 素材标签表
class MaterialTag(models.Model):
    """素材标签表，用于存储素材的各种标签"""
    name = models.CharField(max_length=50, verbose_name='标签名称', unique=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '素材标签'
        verbose_name_plural = '素材标签管理'
        db_table = 'material_tags'

# 素材表
class Material(models.Model):
    """素材表，存储达人的视频素材信息"""
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name='materials', verbose_name='关联达人')
    material_id = models.CharField(max_length=100, verbose_name='素材ID', unique=True)
    video_url = models.URLField(verbose_name='视频素材链接')
    tags = models.ManyToManyField(MaterialTag, related_name='materials', verbose_name='素材标签', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_materials', verbose_name='创建者')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '素材'
        verbose_name_plural = '素材管理'
        db_table = 'materials'

# 推广数据表
class PromotionData(models.Model):
    """推广数据表，存储每个素材的推广数据"""
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='promotion_data', verbose_name='关联素材')
    date = models.DateField(verbose_name='推广日期')
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='推广消耗')
    sales_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='销售额')
    roi = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='ROI', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_promotions', verbose_name='创建者')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '推广数据'
        verbose_name_plural = '推广数据管理'
        db_table = 'promotion_data'
        # 确保每个素材每天只有一条推广数据记录
        unique_together = ('material', 'date')