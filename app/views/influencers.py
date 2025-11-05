"""
达人管理视图
处理达人信息的增删改查功能
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Influencer, Material
from app.forms import InfluencerForm, MaterialForm, MaterialTagForm

# 创建达人管理蓝图
influencers_bp = Blueprint('influencers', __name__, template_folder='templates')

@influencers_bp.route('/influencers')
@login_required
def influencer_list():
    """
    达人列表视图
    - 商务用户：只显示自己创建的达人
    - 投手用户：显示所有达人
    """
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 根据用户角色查询达人列表
    if current_user.is_business():
        # 商务用户只看到自己创建的达人
        influencers = Influencer.query.filter_by(created_by_id=current_user.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        # 投手用户可以看到所有达人
        influencers = Influencer.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('influencers/influencer_list.html', 
                          title='达人列表', 
                          influencers=influencers)

@influencers_bp.route('/influencers/create', methods=['GET', 'POST'])
@login_required
def influencer_create():
    """
    创建达人视图
    只有商务用户可以创建达人
    """
    # 权限检查
    if not current_user.is_business():
        flash('权限不足，仅商务用户可创建达人', 'danger')
        return redirect(url_for('influencers.influencer_list'))
    
    form = InfluencerForm()
    
    if form.validate_on_submit():
        # 创建新达人
        influencer = Influencer(
            name=form.name.data,
            douyin_id=form.douyin_id.data,
            uid=form.uid.data,
            influencer_level=form.influencer_level.data,
            created_by_id=current_user.id
        )
        
        # 保存到数据库
        db.session.add(influencer)
        db.session.commit()
        
        flash('达人创建成功', 'success')
        return redirect(url_for('influencers.influencer_detail', influencer_id=influencer.id))
    
    return render_template('influencers/influencer_form.html', 
                          title='创建达人', 
                          form=form, 
                          is_edit=False)

@influencers_bp.route('/influencers/<int:influencer_id>/edit', methods=['GET', 'POST'])
@login_required
def influencer_edit(influencer_id):
    """
    编辑达人视图
    只有商务用户可以编辑自己创建的达人
    """
    # 获取达人信息
    influencer = Influencer.query.get_or_404(influencer_id)
    
    # 权限检查
    if not current_user.is_business() or influencer.created_by_id != current_user.id:
        flash('权限不足，无法编辑此达人', 'danger')
        return redirect(url_for('influencers.influencer_list'))
    
    form = InfluencerForm(obj=influencer)
    
    if form.validate_on_submit():
        # 更新达人信息
        form.populate_obj(influencer)
        
        # 保存更改
        db.session.commit()
        
        flash('达人更新成功', 'success')
        return redirect(url_for('influencers.influencer_detail', influencer_id=influencer.id))
    
    return render_template('influencers/influencer_form.html', 
                          title='编辑达人', 
                          form=form, 
                          is_edit=True)

@influencers_bp.route('/influencers/<int:influencer_id>/delete', methods=['POST'])
@login_required
def influencer_delete(influencer_id):
    """
    删除达人视图
    只有商务用户可以删除自己创建的达人
    """
    # 获取达人信息
    influencer = Influencer.query.get_or_404(influencer_id)
    
    # 权限检查
    if not current_user.is_business() or influencer.created_by_id != current_user.id:
        flash('权限不足，无法删除此达人', 'danger')
        return redirect(url_for('influencers.influencer_list'))
    
    # 检查是否有关联的素材
    if influencer.materials.count() > 0:
        flash('无法删除，该达人有关联的素材', 'danger')
        return redirect(url_for('influencers.influencer_detail', influencer_id=influencer_id))
    
    # 删除达人
    db.session.delete(influencer)
    db.session.commit()
    
    flash('达人删除成功', 'success')
    return redirect(url_for('influencers.influencer_list'))

@influencers_bp.route('/influencers/<int:influencer_id>')
@login_required
def influencer_detail(influencer_id):
    """
    达人详情视图
    """
    # 获取达人信息
    influencer = Influencer.query.get_or_404(influencer_id)
    
    # 权限检查：商务用户只能查看自己创建的达人
    if current_user.is_business() and influencer.created_by_id != current_user.id:
        flash('权限不足，无法查看此达人', 'danger')
        return redirect(url_for('influencers.influencer_list'))
    
    # 获取该达人的素材列表
    materials = influencer.materials.order_by(Material.created_at.desc()).all()
    
    return render_template('influencers/influencer_detail.html', 
                          title='达人详情', 
                          influencer=influencer,
                          materials=materials)

@influencers_bp.route('/materials')
@login_required
def material_list():
    """
    素材列表视图
    - 商务用户：只显示自己创建的素材
    - 投手用户：显示所有素材
    """
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 根据用户角色查询素材列表
    if current_user.is_business():
        # 商务用户只看到自己创建的素材
        materials = Material.query.filter_by(created_by_id=current_user.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        # 投手用户可以看到所有素材
        materials = Material.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('influencers/material_list.html', 
                          title='素材列表', 
                          materials=materials)

@influencers_bp.route('/materials/create', methods=['GET', 'POST'])
@login_required
def material_create():
    """
    创建素材视图
    只有商务用户可以创建素材
    """
    # 权限检查
    if not current_user.is_business():
        flash('权限不足，仅商务用户可创建素材', 'danger')
        return redirect(url_for('influencers.material_list'))
    
    form = MaterialForm()
    
    # 过滤商务用户只能选择自己创建的达人
    form.influencer_id.choices = [(inf.id, inf.name) for inf in 
                                  Influencer.query.filter_by(created_by_id=current_user.id).all()]
    
    if form.validate_on_submit():
        # 创建新素材
        material = Material(
            influencer_id=form.influencer_id.data,
            material_id=form.material_id.data,
            video_url=form.video_url.data,
            created_by_id=current_user.id
        )
        
        # 保存到数据库
        db.session.add(material)
        db.session.commit()
        
        flash('素材创建成功', 'success')
        return redirect(url_for('influencers.material_detail', material_id=material.id))
    
    return render_template('influencers/material_form.html', 
                          title='创建素材', 
                          form=form, 
                          is_edit=False)

@influencers_bp.route('/materials/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
def material_edit(material_id):
    """
    编辑素材视图
    只有商务用户可以编辑自己创建的素材
    """
    # 获取素材信息
    material = Material.query.get_or_404(material_id)
    
    # 权限检查
    if not current_user.is_business() or material.created_by_id != current_user.id:
        flash('权限不足，无法编辑此素材', 'danger')
        return redirect(url_for('influencers.material_list'))
    
    form = MaterialForm(obj=material)
    
    # 过滤商务用户只能选择自己创建的达人
    form.influencer_id.choices = [(inf.id, inf.name) for inf in 
                                  Influencer.query.filter_by(created_by_id=current_user.id).all()]
    
    if form.validate_on_submit():
        # 更新素材信息
        form.populate_obj(material)
        
        # 保存更改
        db.session.commit()
        
        flash('素材更新成功', 'success')
        return redirect(url_for('influencers.material_detail', material_id=material.id))
    
    return render_template('influencers/material_form.html', 
                          title='编辑素材', 
                          form=form, 
                          is_edit=True)

@influencers_bp.route('/materials/<int:material_id>/delete', methods=['POST'])
@login_required
def material_delete(material_id):
    """
    删除素材视图
    只有商务用户可以删除自己创建的素材
    """
    # 获取素材信息
    material = Material.query.get_or_404(material_id)
    
    # 权限检查
    if not current_user.is_business() or material.created_by_id != current_user.id:
        flash('权限不足，无法删除此素材', 'danger')
        return redirect(url_for('influencers.material_list'))
    
    # 检查是否有关联的推广数据
    if material.promotion_data.count() > 0:
        flash('无法删除，该素材有关联的推广数据', 'danger')
        return redirect(url_for('influencers.material_detail', material_id=material_id))
    
    # 删除素材
    db.session.delete(material)
    db.session.commit()
    
    flash('素材删除成功', 'success')
    return redirect(url_for('influencers.material_list'))

@influencers_bp.route('/materials/<int:material_id>')
@login_required
def material_detail(material_id):
    """
    素材详情视图
    """
    # 获取素材信息
    material = Material.query.get_or_404(material_id)
    
    # 权限检查：商务用户只能查看自己创建的素材
    if current_user.is_business() and material.created_by_id != current_user.id:
        flash('权限不足，无法查看此素材', 'danger')
        return redirect(url_for('influencers.material_list'))
    
    return render_template('influencers/material_detail.html', 
                          title='素材详情', 
                          material=material)

@influencers_bp.route('/tags', methods=['GET', 'POST'])
@login_required
def tag_management():
    """
    标签管理视图
    只有商务用户可以管理标签
    """
    # 权限检查
    if not current_user.is_business():
        flash('权限不足，仅商务用户可管理标签', 'danger')
        return redirect(url_for('accounts.dashboard'))
    
    from app.models import MaterialTag
    
    # 获取所有标签
    tags = MaterialTag.query.all()
    
    form = MaterialTagForm()
    
    if form.validate_on_submit():
        # 检查标签是否已存在
        existing_tag = MaterialTag.query.filter_by(name=form.name.data).first()
        if existing_tag:
            flash('标签已存在', 'warning')
        else:
            # 创建新标签
            tag = MaterialTag(name=form.name.data)
            db.session.add(tag)
            db.session.commit()
            flash('标签创建成功', 'success')
            return redirect(url_for('influencers.tag_management'))
    
    return render_template('influencers/tag_management.html', 
                          title='标签管理', 
                          form=form, 
                          tags=tags)