"""
用户账户URL路由配置
"""

from django.urls import path
from .views import LoginView, RegisterView, user_logout, dashboard

app_name = 'accounts'

urlpatterns = [
    # 登录视图
    path('login/', LoginView.as_view(), name='login'),
    
    # 注册视图
    path('register/', RegisterView.as_view(), name='register'),
    
    # 注销视图
    path('logout/', user_logout, name='logout'),
    
    # 仪表盘（在主URL中已配置，但这里保留便于扩展）
    path('dashboard/', dashboard, name='dashboard'),
]