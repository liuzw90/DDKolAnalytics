"""
API路由定义
提供系统的所有API接口
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.api.client import douyin_client
from app.models import db, Influencer, Material, MaterialTag, PromotionData
from datetime import datetime

# 创建API蓝图
api_bp = Blueprint('api', __name__)

@api_bp.route('/influencer/from-url', methods=['POST'])
def get_influencer_from_url():
    """
    通过视频链接获取达人信息
    
    POST参数：
        video_url: 视频素材链接
    """
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'error': '视频链接不能为空'}), 400
        
        # 调用API获取达人信息
        influencer_info = douyin_client.get_influencer_info(video_url)
        
        if not influencer_info:
            return jsonify({'error': '获取达人信息失败'}), 500
        
        return jsonify(influencer_info), 200
        
    except Exception as e:
        current_app.logger.error(f'获取达人信息API错误: {str(e)}')
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/material/batch', methods=['POST'])
def get_batch_materials():
    """
    批量获取素材数据
    
    POST参数：
        material_ids: 素材ID列表
    """
    try:
        data = request.get_json()
        material_ids = data.get('material_ids', [])
        
        if not material_ids:
            return jsonify({'error': '素材ID列表不能为空'}), 400
        
        # 调用API获取素材数据
        materials_data = douyin_client.get_material_data(material_ids)
        
        return jsonify(materials_data), 200
        
    except Exception as e:
        current_app.logger.error(f'批量获取素材API错误: {str(e)}')
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/promotion/data', methods=['POST'])
def get_promotion_data():
    """
    获取素材推广数据
    
    POST参数：
        material_id: 素材ID
        start_date: 开始日期 (可选)
        end_date: 结束日期 (可选)
    """
    try:
        data = request.get_json()
        material_id = data.get('material_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not material_id:
            return jsonify({'error': '素材ID不能为空'}), 400
        
        date_range = None
        if start_date and end_date:
            date_range = (start_date, end_date)
        
        # 调用API获取推广数据
        promotion_data = douyin_client.get_promotion_data(material_id, date_range)
        
        return jsonify(promotion_data), 200
        
    except Exception as e:
        current_app.logger.error(f'获取推广数据API错误: {str(e)}')
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/influencer/materials', methods=['POST'])
def get_influencer_materials():
    """
    获取达人的所有素材ID
    
    POST参数：
        influencer_uid: 达人UID
    """
    try:
        data = request.get_json()
        influencer_uid = data.get('influencer_uid')
        
        if not influencer_uid:
            return jsonify({'error': '达人UID不能为空'}), 400
        
        # 调用API获取达人所有素材ID
        material_ids = douyin_client.fetch_all_material_ids(influencer_uid)
        
        return jsonify({'material_ids': material_ids}), 200
        
    except Exception as e:
        current_app.logger.error(f'获取达人素材列表API错误: {str(e)}')
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/material/auto-fetch', methods=['POST'])
@login_required
def auto_fetch_material_data():
    """
    自动获取素材信息并保存
    需要登录，仅商务用户可调用
    
    POST参数：
        video_url: 视频素材链接
        influencer_id: 达人ID (可选，如果未提供则自动创建)
    """
    try:
        # 权限检查
        if not current_user.is_business():
            return jsonify({'error': '权限不足，仅商务用户可操作'}), 403
        
        data = request.get_json()
        video_url = data.get('video_url')
        influencer_id = data.get('influencer_id')
        
        if not video_url:
            return jsonify({'error': '视频链接不能为空'}), 400
        
        # 获取达人信息
        influencer_info = douyin_client.get_influencer_info(video_url)
        
        if not influencer_info:
            return jsonify({'error': '获取达人信息失败'}), 500
        
        # 查找或创建达人
        influencer = None
        if influencer_id:
            influencer = Influencer.query.get(influencer_id)
        
        if not influencer:
            # 检查是否已存在该达人
            influencer = Influencer.query.filter_by(uid=influencer_info['uid']).first()
            
        if not influencer:
            # 创建新达人
            influencer = Influencer(
                name=influencer_info['name'],
                douyin_id=influencer_info['douyin_id'],
                uid=influencer_info['uid'],
                influencer_level=influencer_info.get('influencer_level'),
                created_by_id=current_user.id
            )
            db.session.add(influencer)
            db.session.commit()
        
        # 从URL中提取素材ID（简化处理）
        material_id = video_url.split('/')[-1] if '/' in video_url else video_url
        
        # 检查素材是否已存在
        existing_material = Material.query.filter_by(material_id=material_id).first()
        
        if existing_material:
            return jsonify({
                'error': '素材已存在',
                'influencer': {
                    'id': influencer.id,
                    'name': influencer.name
                },
                'material': {
                    'id': existing_material.id,
                    'material_id': existing_material.material_id
                }
            }), 200
        
        # 创建新素材
        new_material = Material(
            influencer_id=influencer.id,
            material_id=material_id,
            video_url=video_url,
            created_by_id=current_user.id
        )
        db.session.add(new_material)
        db.session.commit()
        
        return jsonify({
            'message': '素材自动创建成功',
            'influencer': {
                'id': influencer.id,
                'name': influencer.name
            },
            'material': {
                'id': new_material.id,
                'material_id': new_material.material_id
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'自动获取素材API错误: {str(e)}')
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/promotion/auto-fetch', methods=['POST'])
@login_required
def auto_fetch_promotion_data():
    """
    自动获取推广数据并保存
    需要登录，仅投手用户可调用
    
    POST参数：
        material_id: 素材ID
        start_date: 开始日期
        end_date: 结束日期
    """
    try:
        # 权限检查
        if not current_user.is_pitcher():
            return jsonify({'error': '权限不足，仅投手用户可操作'}), 403
        
        data = request.get_json()
        material_id = data.get('material_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not material_id:
            return jsonify({'error': '素材ID不能为空'}), 400
        
        # 查找素材
        material = Material.query.filter_by(material_id=material_id).first()
        
        if not material:
            return jsonify({'error': '素材不存在'}), 404
        
        # 获取推广数据
        date_range = None
        if start_date and end_date:
            date_range = (start_date, end_date)
        
        promotion_data_list = douyin_client.get_promotion_data(material_id, date_range)
        
        if not promotion_data_list:
            return jsonify({'error': '获取推广数据失败'}), 500
        
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
        
        return jsonify({
            'message': '推广数据自动获取成功',
            'saved_count': saved_count,
            'material_id': material_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'自动获取推广数据API错误: {str(e)}')
        return jsonify({'error': '服务器内部错误'}), 500