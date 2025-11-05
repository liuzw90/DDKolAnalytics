from django import forms
from django.contrib.auth import get_user_model
from influencers.models import Material
from .models import Promotion
import datetime

User = get_user_model()


class PromotionForm(forms.ModelForm):
    """推广数据表单"""
    
    # 根据当前用户过滤素材选项
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PromotionForm, self).__init__(*args, **kwargs)
        
        # 根据用户角色设置素材选择范围
        if user and user.is_pitcher:
            # 投手可以选择所有商务录入的素材
            self.fields['material'].queryset = Material.objects.all()
        else:
            self.fields['material'].queryset = Material.objects.none()
        
        # 如果是编辑，不允许修改关联的素材和日期
        if self.instance.pk:
            self.fields['material'].disabled = True
            self.fields['date'].disabled = True
    
    class Meta:
        model = Promotion
        fields = ['material', 'date', 'spend', 'sales_amount']
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'max': datetime.date.today().strftime('%Y-%m-%d')}
            ),
            'spend': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'sales_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
        labels = {
            'material': '关联素材',
            'date': '推广日期',
            'spend': '推广消耗（元）',
            'sales_amount': '销售额（元）',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        spend = cleaned_data.get('spend')
        sales_amount = cleaned_data.get('sales_amount')
        material = cleaned_data.get('material')
        date = cleaned_data.get('date')
        
        # 验证消耗和销售额不能为负数
        if spend is not None and spend < 0:
            self.add_error('spend', '推广消耗不能为负数')
        
        if sales_amount is not None and sales_amount < 0:
            self.add_error('sales_amount', '销售额不能为负数')
        
        # 验证不能为未来日期
        if date and date > datetime.date.today():
            self.add_error('date', '推广日期不能是未来日期')
        
        # 验证不能重复提交同一素材同一天的数据
        if material and date and not self.instance.pk:
            user = self.initial.get('user')
            if Promotion.objects.filter(material=material, date=date, created_by=user).exists():
                self.add_error('date', '您已经为该素材提交过此日期的推广数据')
        
        return cleaned_data