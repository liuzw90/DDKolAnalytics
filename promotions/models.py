from django.db import models
from django.conf import settings
from influencers.models import Material


class Promotion(models.Model):
    """推广数据表，记录每个素材的推广数据"""
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='promotions', verbose_name='关联素材')
    date = models.DateField(verbose_name='推广日期')
    spend = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='推广消耗（元）')
    sales_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='销售额（元）')
    roi = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ROI', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '推广数据'
        verbose_name_plural = '推广数据'
        unique_together = ('material', 'date', 'created_by')  # 确保每个投手每天对同一素材只有一条记录
        ordering = ['-date']
    
    def save(self, *args, **kwargs):
        # 自动计算ROI
        if self.spend > 0:
            self.roi = self.sales_amount / self.spend
        else:
            self.roi = 0
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.material.material_id} - {self.date} - {self.created_by}'