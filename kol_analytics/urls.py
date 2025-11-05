"""
Django项目URL路由配置
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # 管理员后台
    path('admin/', admin.site.urls),
    
    # 账户应用路由
    path('accounts/', include('accounts.urls', namespace='accounts')),
    
    # 达人应用路由
    path('influencers/', include('influencers.urls', namespace='influencers')),
    
    # 推广应用路由
    path('promotions/', include('promotions.urls', namespace='promotions')),
    
    # 首页/仪表盘
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
]