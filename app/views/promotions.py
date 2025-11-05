"""
推广数据管理视图
处理推广数据的增删改查功能
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import PromotionData, Material
from app.forms import PromotionDataForm
from datetime import datetime
from app.api.client import douyin_client

# 创建推广管理蓝图
promotions_bp = Blueprint('promotions', __name__, template_folder='templates')

@promotions_bp.route('/promotions')
@login_required
def promotion_list():
    """
    推广数据列表视图
    - 商务用户：只显示自己创建的推广数据
    - 投手用户：显示所有推广数据
    """
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 筛选参数
    material_id = request.args.get('material_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 构建查询
    query = PromotionData.query
    
    # 根据用户角色过滤
    if current_user.is_business():
        # 商务用户只能看到自己创建的推广数据
        query = query.filter_by(created_by_id=current_user.id)
    
    # 应用筛选条件
    if material_id:
        query = query.filter_by(material_id=material_id)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(PromotionData.date >= start)
        except ValueError:
            flash('开始日期格式无效，请使用YYYY-MM-DD格式', 'warning')
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(PromotionData.date <= end)
        except ValueError:
            flash('结束日期格式无效，请使用YYYY-MM-DD格式', 'warning')
    
    # 排序并分页
    promotions = query.order_by(PromotionData.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 获取所有素材用于筛选
    if current_user.is_business():
        materials = Material.query.filter_by(created_by_id=current_user.id).all()
    else:
        materials = Material.query.all()
    
    return render_template('promotions/promotion_list.html', 
                          title='推广数据列表', 
                          promotions=promotions,
                          materials=materials,
                          current_material_id=material_id,
                          current_start_date=start_date,
                          current_end_date=end_date)

@promotions_bp.route('/promotions/create', methods=['GET', 'POST'])
@login_required
def promotion_create():
    """
    创建推广数据视图
    只有投手用户可以创建推广数据
    """
    # 权限检查
    if not current_user.is_pitcher():
        flash('权限不足，仅投手用户可创建推广数据', 'danger')
        return redirect(url_for('promotions.promotion_list'))
    
    form = PromotionDataForm()
    
    # 设置素材选择
    form.material_id.choices = [(mat.id, f"{mat.material_id} - {mat.influencer.name}") for mat in 
                              Material.query.all()]
    
    if form.validate_on_submit():
        # 检查数据是否已存在
        existing = PromotionData.query.filter_by(
            material_id=form.material_id.data,
            date=form.date.data
        ).first()
        
        if existing:
            flash('该日期的推广数据已存在', 'warning')
            return redirect(url_for('promotions.promotion_create'))
        
        # 创建新推广数据
        promotion = PromotionData(
            material_id=form.material_id.data,
            date=form.date.data,
            cost=form.cost.data,
            sales_amount=form.sales_amount.data,
            roi=form.roi.data,
            created_by_id=current_user.id
        )
        
        # 保存到数据库
        db.session.add(promotion)
        db.session.commit()
        
        flash('推广数据创建成功', 'success')
        return redirect(url_for('promotions.promotion_detail', promotion_id=promotion.id))
    
    return render_template('promotions/promotion_form.html', 
                          title='创建推广数据', 
                          form=form, 
                          is_edit=False)

@promotions_bp.route('/promotions/<int:promotion_id>/edit', methods=['GET', 'POST'])
@login_required
def promotion_edit(promotion_id):
    """
    编辑推广数据视图
    只有投手用户可以编辑推广数据
    """
    # 获取推广数据
    promotion = PromotionData.query.get_or_404(promotion_id)
    
    # 权限检查
    if not current_user.is_pitcher():
        flash('权限不足，仅投手用户可编辑推广数据', 'danger')
        return redirect(url_for('promotions.promotion_list'))
    
    form = PromotionDataForm(obj=promotion)
    
    # 设置素材选择
    form.material_id.choices = [(mat.id, f"{mat.material_id} - {mat.influencer.name}") for mat in 
                              Material.query.all()]
    
    if form.validate_on_submit():
        # 更新推广数据
        form.populate_obj(promotion)
        
        # 保存更改
        db.session.commit()
        
        flash('推广数据更新成功', 'success')
        return redirect(url_for('promotions.promotion_detail', promotion_id=promotion.id))
    
    return render_template('promotions/promotion_form.html', 
                          title='编辑推广数据', 
                          form=form, 
                          is_edit=True)

@promotions_bp.route('/promotions/<int:promotion_id>/delete', methods=['POST'])
@login_required
def promotion_delete(promotion_id):
    """
    删除推广数据视图
    只有投手用户可以删除推广数据
    """
    # 获取推广数据
    promotion = PromotionData.query.get_or_404(promotion_id)
    
    # 权限检查
    if not current_user.is_pitcher():
        flash('权限不足，仅投手用户可删除推广数据', 'danger')
        return redirect(url_for('promotions.promotion_list'))
    
    # 删除推广数据
    db.session.delete(promotion)
    db.session.commit()
    
    flash('推广数据删除成功', 'success')
    return redirect(url_for('promotions.promotion_list'))

@promotions_bp.route('/promotions/<int:promotion_id>')
@login_required
def promotion_detail(promotion_id):
    """
    推广数据详情视图
    """
    # 获取推广数据
    promotion = PromotionData.query.get_or_404(promotion_id)
    
    return render_template('promotions/promotion_detail.html', 
                          title='推广数据详情', 
                          promotion=promotion)

@promotions_bp.route('/promotions/batch-fetch', methods=['GET', 'POST'])
@login_required
def batch_fetch_promotions():
    """
    批量获取推广数据视图
    只有投手用户可以使用
    """
    # 权限检查
    if not current_user.is_pitcher():
        flash('权限不足，仅投手用户可批量获取推广数据', 'danger')
        return redirect(url_for('promotions.promotion_list'))
    
    # 筛选参数
    material_id = request.args.get('material_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 获取所有素材
    materials = Material.query.all()
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            material_id = request.form.get('material_id', type=int)
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            if not material_id:
                flash('请选择素材', 'danger')
                return redirect(url_for('promotions.batch_fetch_promotions'))
            
            # 获取素材
            material = Material.query.get_or_404(material_id)
            
            # 准备日期范围
            date_range = None
            if start_date and end_date:
                date_range = (start_date, end_date)
            
            # 调用API获取推广数据
            promotion_data_list = douyin_client.get_promotion_data(material.material_id, date_range)
            
            if not promotion_data_list:
                flash('未获取到推广数据', 'info')
                return redirect(url_for('promotions.batch_fetch_promotions'))
            
            # 保存推广数据
            saved_count = 0
            for pd in promotion_data_list:
                # 检查是否已存在
                existing = PromotionData.query.filter_by(
                    material_id=material.id,
                    date=datetime.strptime(pd['date'], '%Y-%m-%d').date()
                ).first()
                
                if not existing:
                    promotion_data = PromotionData(
                        material_id=material.id,
                        date=datetime.strptime(pd['date'], '%Y-%m-%d').date(),
                        cost=pd['cost'],
                        sales_amount=pd['sales_amount'],
                        roi=pd['roi'],
                        created_by_id=current_user.id
                    )
                    db.session.add(promotion_data)
                    saved_count += 1
            
            db.session.commit()
            
            flash(f'成功获取并保存 {saved_count} 条推广数据', 'success')
            return redirect(url_for('promotions.promotion_list', material_id=material_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'获取数据失败: {str(e)}', 'danger')
    
    return render_template('promotions/batch_fetch.html', 
                          title='批量获取推广数据', 
                          materials=materials,
                          current_material_id=material_id,
                          current_start_date=start_date,
                          current_end_date=end_date)