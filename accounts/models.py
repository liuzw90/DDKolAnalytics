"""
用户账户模型
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """自定义用户管理器"""
    def create_user(self, username, email, password=None, **extra_fields):
        """创建普通用户"""
        if not email:
            raise ValueError(_('必须提供邮箱地址'))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('超级用户必须设置 is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('超级用户必须设置 is_superuser=True'))
        
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    """自定义用户模型，包含商务和投手两类用户"""
    ROLE_CHOICES = [
        ('business', '商务'),
        ('pitcher', '投手'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='用户角色',
        help_text='商务账号可以管理达人信息，投手账号可以管理推广数据'
    )
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号码')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        db_table = 'users'
    
    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
    
    def is_business(self):
        """判断用户是否为商务角色"""
        return self.role == 'business'
    
    def is_pitcher(self):
        """判断用户是否为投手角色"""
        return self.role == 'pitcher'