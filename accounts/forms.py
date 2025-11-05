"""
用户账户表单
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class LoginForm(forms.Form):
    """用户登录表单"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'})
    )

class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '邮箱地址'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '手机号码'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '确认密码'}),
        }