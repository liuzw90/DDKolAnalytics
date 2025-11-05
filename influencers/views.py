"""
达人信息管理视图
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from accounts.decorators import business_required, business_or_owner_required
from .models import Influencer, Material, MaterialTag
from .forms import InfluencerForm, MaterialForm, MaterialTagForm

# 达人管理视图
@login_required
def influencer_list(request):
    """达人列表视图
    - 商务用户：只能看到自己创建的达人
    - 投手用户：可以看到所有达人
    """
    if request.user.is_business():
        influencers = Influencer.objects.filter(created_by=request.user).order_by('-create_time')
    else:
        influencers = Influencer.objects.all().order_by('-create_time')
    
    # 分页
    paginator = Paginator(influencers, 10)
    page = request.GET.get('page')
    influencers_page = paginator.get_page(page)
    
    return render(request, 'influencers/influencer_list.html', {
        'influencers': influencers_page
    })

@business_required
def influencer_create(request):
    """创建达人视图（仅商务用户可访问）"""
    if request.method == 'POST':
        form = InfluencerForm(request.POST)
        if form.is_valid():
            influencer = form.save(commit=False)
            influencer.created_by = request.user
            influencer.save()
            messages.success(request, '达人信息创建成功')
            return redirect('influencers:influencer_list')
    else:
        form = InfluencerForm()
    
    return render(request, 'influencers/influencer_form.html', {
        'form': form,
        'title': '创建达人'
    })

@business_or_owner_required(Influencer)
def influencer_edit(request, pk):
    """编辑达人视图（仅商务用户或创建者可访问）"""
    influencer = get_object_or_404(Influencer, pk=pk)
    
    if request.method == 'POST':
        form = InfluencerForm(request.POST, instance=influencer)
        if form.is_valid():
            form.save()
            messages.success(request, '达人信息更新成功')
            return redirect('influencers:influencer_list')
    else:
        form = InfluencerForm(instance=influencer)
    
    return render(request, 'influencers/influencer_form.html', {
        'form': form,
        'title': '编辑达人'
    })

@business_or_owner_required(Influencer)
def influencer_delete(request, pk):
    """删除达人视图（仅商务用户或创建者可访问）"""
    influencer = get_object_or_404(Influencer, pk=pk)
    
    if request.method == 'POST':
        influencer.delete()
        messages.success(request, '达人信息已删除')
        return redirect('influencers:influencer_list')
    
    return render(request, 'influencers/influencer_confirm_delete.html', {
        'influencer': influencer
    })

@login_required
def influencer_detail(request, pk):
    """达人详情视图
    - 商务用户：只能查看自己创建的达人详情
    - 投手用户：可以查看所有达人详情
    """
    influencer = get_object_or_404(Influencer, pk=pk)
    
    # 权限检查
    if request.user.is_business() and influencer.created_by != request.user:
        messages.error(request, '您没有权限查看此达人信息')
        return redirect('influencers:influencer_list')
    
    # 获取该达人的所有素材
    materials = Material.objects.filter(influencer=influencer)
    
    return render(request, 'influencers/influencer_detail.html', {
        'influencer': influencer,
        'materials': materials
    })

# 素材管理视图
@login_required
def material_list(request):
    """素材列表视图
    - 商务用户：只能看到自己创建的素材
    - 投手用户：可以看到所有素材
    """
    if request.user.is_business():
        materials = Material.objects.filter(created_by=request.user).order_by('-create_time')
    else:
        materials = Material.objects.all().order_by('-create_time')
    
    # 分页
    paginator = Paginator(materials, 10)
    page = request.GET.get('page')
    materials_page = paginator.get_page(page)
    
    return render(request, 'influencers/material_list.html', {
        'materials': materials_page
    })

@business_required
def material_create(request):
    """创建素材视图（仅商务用户可访问）"""
    if request.method == 'POST':
        form = MaterialForm(request.POST, user=request.user)
        if form.is_valid():
            material = form.save(commit=False)
            material.created_by = request.user
            material.save()
            form.save_m2m()  # 保存多对多关系（标签）
            messages.success(request, '素材创建成功')
            return redirect('influencers:material_list')
    else:
        form = MaterialForm(user=request.user)
    
    # 获取所有标签，用于前端显示
    tags = MaterialTag.objects.all()
    
    return render(request, 'influencers/material_form.html', {
        'form': form,
        'tags': tags,
        'title': '创建素材'
    })

@business_or_owner_required(Material)
def material_edit(request, pk):
    """编辑素材视图（仅商务用户或创建者可访问）"""
    material = get_object_or_404(Material, pk=pk)
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '素材更新成功')
            return redirect('influencers:material_list')
    else:
        form = MaterialForm(instance=material, user=request.user)
    
    # 获取所有标签，用于前端显示
    tags = MaterialTag.objects.all()
    
    return render(request, 'influencers/material_form.html', {
        'form': form,
        'tags': tags,
        'title': '编辑素材'
    })

@business_or_owner_required(Material)
def material_delete(request, pk):
    """删除素材视图（仅商务用户或创建者可访问）"""
    material = get_object_or_404(Material, pk=pk)
    
    if request.method == 'POST':
        material.delete()
        messages.success(request, '素材已删除')
        return redirect('influencers:material_list')
    
    return render(request, 'influencers/material_confirm_delete.html', {
        'material': material
    })

@login_required
def material_detail(request, pk):
    """素材详情视图
    - 商务用户：只能查看自己创建的素材详情
    - 投手用户：可以查看所有素材详情
    """
    material = get_object_or_404(Material, pk=pk)
    
    # 权限检查
    if request.user.is_business() and material.created_by != request.user:
        messages.error(request, '您没有权限查看此素材信息')
        return redirect('influencers:material_list')
    
    return render(request, 'influencers/material_detail.html', {
        'material': material
    })

@business_required
def tag_management(request):
    """标签管理视图（仅商务用户可访问）"""
    tags = MaterialTag.objects.all()
    
    if request.method == 'POST':
        form = MaterialTagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '标签创建成功')
            return redirect('influencers:tag_management')
    else:
        form = MaterialTagForm()
    
    return render(request, 'influencers/tag_management.html', {
        'form': form,
        'tags': tags
    })