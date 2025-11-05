"""
达人信息管理表单
"""

from django import forms
from .models import Influencer, Material, MaterialTag
from django.forms import ModelMultipleChoiceField

class InfluencerForm(forms.ModelForm):
    """达人信息表单"""
    class Meta:
        model = Influencer
        fields = ['name', 'douyin_id', 'uid', 'product_link', 'influencer_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '达人名称'}),
            'douyin_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '抖音号'}),
            'uid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UID'}),
            'product_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': '挂车商品链接'}),
            'influencer_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '达人等级'}),
        }
        labels = {
            'name': '达人名称',
            'douyin_id': '抖音号',
            'uid': 'UID',
            'product_link': '挂车商品链接',
            'influencer_level': '达人等级',
        }
    
    def clean_uid(self):
        """验证UID的唯一性"""
        uid = self.cleaned_data.get('uid')
        instance = self.instance
        if instance.pk:
            # 编辑模式，排除当前实例
            if Influencer.objects.exclude(pk=instance.pk).filter(uid=uid).exists():
                raise forms.ValidationError('该UID已存在')
        else:
            # 新增模式
            if Influencer.objects.filter(uid=uid).exists():
                raise forms.ValidationError('该UID已存在')
        return uid

class MaterialTagForm(forms.ModelForm):
    """素材标签表单"""
    class Meta:
        model = MaterialTag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '标签名称'}),
        }

class MaterialForm(forms.ModelForm):
    """素材信息表单"""
    # 自定义多选标签字段，支持选择多个标签
    tags = ModelMultipleChoiceField(
        queryset=MaterialTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='素材标签'
    )
    
    class Meta:
        model = Material
        fields = ['influencer', 'material_id', 'video_url', 'tags']
        widgets = {
            'influencer': forms.Select(attrs={'class': 'form-control'}),
            'material_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '素材ID'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': '视频素材链接'}),
        }
        labels = {
            'influencer': '关联达人',
            'material_id': '素材ID',
            'video_url': '视频素材链接',
        }
    
    def clean_material_id(self):
        """验证素材ID的唯一性"""
        material_id = self.cleaned_data.get('material_id')
        instance = self.instance
        if instance.pk:
            # 编辑模式，排除当前实例
            if Material.objects.exclude(pk=instance.pk).filter(material_id=material_id).exists():
                raise forms.ValidationError('该素材ID已存在')
        else:
            # 新增模式
            if Material.objects.filter(material_id=material_id).exists():
                raise forms.ValidationError('该素材ID已存在')
        return material_id
    
    def __init__(self, *args, **kwargs):
        # 获取当前用户
        user = kwargs.pop('user', None)
        super(MaterialForm, self).__init__(*args, **kwargs)
        
        # 如果有用户且是商务角色，只显示该用户创建的达人
        if user and user.is_business():
            self.fields['influencer'].queryset = Influencer.objects.filter(created_by=user)
        else:
            # 投手角色可以看到所有达人
            self.fields['influencer'].queryset = Influencer.objects.all()