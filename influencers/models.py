"""
达人信息管理模型
"""

from django.db import models
from accounts.models import User

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
    
    def __str__(self):
        return f'{self.name} ({self.douyin_id})'

class MaterialTag(models.Model):
    """素材标签表，用于存储素材的各种标签"""
    name = models.CharField(max_length=50, verbose_name='标签名称', unique=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '素材标签'
        verbose_name_plural = '素材标签管理'
        db_table = 'material_tags'
    
    def __str__(self):
        return self.name

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
    
    def __str__(self):
        return f'{self.material_id} - {self.influencer.name}'