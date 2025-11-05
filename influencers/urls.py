"""
达人信息管理URL路由配置
"""

from django.urls import path
from .views import (
    influencer_list, influencer_create, influencer_edit, 
    influencer_delete, influencer_detail,
    material_list, material_create, material_edit,
    material_delete, material_detail, tag_management
)

app_name = 'influencers'

urlpatterns = [
    # 达人相关路由
    path('influencers/', influencer_list, name='influencer_list'),
    path('influencers/create/', influencer_create, name='influencer_create'),
    path('influencers/<int:pk>/edit/', influencer_edit, name='influencer_edit'),
    path('influencers/<int:pk>/delete/', influencer_delete, name='influencer_delete'),
    path('influencers/<int:pk>/', influencer_detail, name='influencer_detail'),
    
    # 素材相关路由
    path('materials/', material_list, name='material_list'),
    path('materials/create/', material_create, name='material_create'),
    path('materials/<int:pk>/edit/', material_edit, name='material_edit'),
    path('materials/<int:pk>/delete/', material_delete, name='material_delete'),
    path('materials/<int:pk>/', material_detail, name='material_detail'),
    
    # 标签管理路由
    path('tags/', tag_management, name='tag_management'),
]