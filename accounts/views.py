"""
用户账户视图
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.contrib import messages

from .forms import LoginForm, UserRegisterForm

class LoginView(FormView):
    """用户登录视图"""
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'欢迎回来，{user.username}！')
            return super().form_valid(form)
        else:
            form.add_error(None, '用户名或密码错误')
            return self.form_invalid(form)

class RegisterView(CreateView):
    """用户注册视图（仅管理员可用，这里为演示创建）"""
    template_name = 'accounts/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, '注册成功，请登录！')
        return super().form_valid(form)

def user_logout(request):
    """用户注销"""
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('accounts:login')

@login_required
def dashboard(request):
    """用户仪表盘"""
    return render(request, 'dashboard.html')