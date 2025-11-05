"""
权限控制装饰器
用于控制不同角色用户的数据访问权限
"""

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

# 检查用户是否为商务角色
def business_required(view_func):
    """
    装饰器：仅允许商务角色访问
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_business():
            return view_func(request, *args, **kwargs)
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    return _wrapped_view

# 检查用户是否为投手角色
def pitcher_required(view_func):
    """
    装饰器：仅允许投手角色访问
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_pitcher():
            return view_func(request, *args, **kwargs)
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    return _wrapped_view

# 检查用户是否为商务角色或者数据创建者
def business_or_owner_required(model_class, model_id_param='pk', created_by_field='created_by'):
    """
    装饰器：允许商务角色访问，或允许数据的创建者访问
    
    参数：
    - model_class: 要检查的模型类
    - model_id_param: URL中模型ID的参数名，默认为'pk'
    - created_by_field: 模型中记录创建者的字段名，默认为'created_by'
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, '请先登录')
                return redirect('accounts:login')
            
            # 获取模型实例ID
            model_id = kwargs.get(model_id_param)
            if not model_id:
                messages.error(request, '参数错误')
                return redirect('dashboard')
            
            try:
                # 获取模型实例
                instance = model_class.objects.get(pk=model_id)
                # 检查是否为商务角色或创建者
                if request.user.is_business() or getattr(instance, created_by_field) == request.user:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, '您没有权限访问此数据')
                    return redirect('dashboard')
            except model_class.DoesNotExist:
                messages.error(request, '请求的数据不存在')
                return redirect('dashboard')
        return _wrapped_view
    return decorator