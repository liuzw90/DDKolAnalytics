from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import HttpResponseForbidden
from accounts.decorators import pitcher_required
from influencers.models import Material
from .models import Promotion
from .forms import PromotionForm


class PromotionListView(ListView):
    """推广数据列表视图"""
    model = Promotion
    template_name = 'promotions/promotion_list.html'
    context_object_name = 'promotions'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        queryset = Promotion.objects.select_related('material', 'material__influencer', 'created_by')
        
        # 过滤数据：商务只能看到自己创建的达人的推广数据，投手可以看到所有数据
        if user.is_business:
            # 商务用户只能看到自己创建的达人的推广数据
            influencer_ids = Material.objects.filter(created_by=user).values_list('influencer_id', flat=True)
            material_ids = Material.objects.filter(influencer_id__in=influencer_ids).values_list('id', flat=True)
            queryset = queryset.filter(material_id__in=material_ids)
        
        # 按日期降序排序
        queryset = queryset.order_by('-date', '-create_time')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 可以在这里添加额外的上下文数据
        return context


class PromotionDetailView(DetailView):
    """推广数据详情视图"""
    model = Promotion
    template_name = 'promotions/promotion_detail.html'
    context_object_name = 'promotion'
    
    def dispatch(self, request, *args, **kwargs):
        # 权限检查
        promotion = self.get_object()
        user = request.user
        
        # 商务用户只能查看自己创建的达人的推广数据
        if user.is_business:
            if promotion.material.created_by != user:
                return HttpResponseForbidden("您无权查看此推广数据")
        
        return super().dispatch(request, *args, **kwargs)


class PromotionCreateView(CreateView):
    """推广数据创建视图"""
    model = Promotion
    form_class = PromotionForm
    template_name = 'promotions/promotion_form.html'
    
    def get_success_url(self):
        messages.success(self.request, '推广数据添加成功！')
        return reverse_lazy('promotions:promotion_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '添加推广数据'
        # 处理URL参数，预选素材
        material_id = self.request.GET.get('material')
        if material_id:
            try:
                material = Material.objects.get(pk=material_id)
                context['form'].initial['material'] = material
            except Material.DoesNotExist:
                pass
        return context
    
    @pitcher_required
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PromotionUpdateView(UpdateView):
    """推广数据更新视图"""
    model = Promotion
    form_class = PromotionForm
    template_name = 'promotions/promotion_form.html'
    
    def get_success_url(self):
        messages.success(self.request, '推广数据更新成功！')
        return reverse_lazy('promotions:promotion_detail', kwargs={'pk': self.object.pk})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '编辑推广数据'
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # 权限检查：只有创建者才能编辑
        promotion = self.get_object()
        if promotion.created_by != request.user:
            return HttpResponseForbidden("您无权编辑此推广数据")
        return super().dispatch(request, *args, **kwargs)


class PromotionDeleteView(DeleteView):
    """推广数据删除视图"""
    model = Promotion
    template_name = 'promotions/promotion_confirm_delete.html'
    success_url = reverse_lazy('promotions:promotion_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '推广数据删除成功！')
        return super().delete(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        # 权限检查：只有创建者才能删除
        promotion = self.get_object()
        if promotion.created_by != request.user:
            return HttpResponseForbidden("您无权删除此推广数据")
        return super().dispatch(request, *args, **kwargs)