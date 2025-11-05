"""
表单定义
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, URLField, DateField, DecimalField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, Optional
from app.models import User, Influencer, Material, MaterialTag, InfluencerTag, PromotionData

# 用户登录表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 50)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

# 用户注册表单
class UserRegisterForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), 
        Length(1, 50),
        Regexp(r'^[a-zA-Z0-9_]+$', message='用户名只能包含字母、数字和下划线')
    ])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 100)])
    password = PasswordField('密码', validators=[
        DataRequired(), 
        Length(6, 100),
        EqualTo('confirm_password', message='两次输入的密码必须一致')
    ])
    confirm_password = PasswordField('确认密码', validators=[DataRequired()])
    role = SelectField('角色', choices=[
        ('business', '商务'),
        ('pitcher', '投手')
    ], validators=[DataRequired()])
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册')

# 达人标签表单
class InfluencerTagForm(FlaskForm):
    name = StringField('标签名称', validators=[DataRequired(), Length(1, 50)])
    submit = SubmitField('创建')
    
    def validate_name(self, name):
        tag = InfluencerTag.query.filter_by(name=name.data).first()
        if tag:
            raise ValidationError('该标签已存在')

# 达人表单
class InfluencerForm(FlaskForm):
    name = StringField('达人名称', validators=[DataRequired(), Length(1, 100)])
    douyin_id = StringField('抖音号', validators=[DataRequired(), Length(1, 100)])
    uid = StringField('UID', validators=[DataRequired(), Length(1, 100)])
    product_link = URLField('挂车商品链接', validators=[Optional(), Length(0, 200)])
    influencer_level = StringField('达人等级', validators=[Optional(), Length(0, 50)])
    tags = SelectMultipleField('达人标签', coerce=int)
    submit = SubmitField('保存')
    
    def __init__(self, *args, **kwargs):
        super(InfluencerForm, self).__init__(*args, **kwargs)
        # 设置标签选项
        self.tags.choices = [(tag.id, tag.name) for tag in InfluencerTag.query.all()]
    
    def validate_uid(self, uid):
        # 如果是编辑表单，需要排除当前达人的UID
        if hasattr(self, 'obj') and self.obj:
            existing = Influencer.query.filter_by(uid=uid.data).first()
            if existing and existing.id == self.obj.id:
                return
        
        influencer = Influencer.query.filter_by(uid=uid.data).first()
        if influencer:
            raise ValidationError('该UID已存在')

# 素材表单
class MaterialForm(FlaskForm):
    influencer_id = SelectField('关联达人', coerce=int, validators=[DataRequired()])
    material_id = StringField('素材ID', validators=[DataRequired(), Length(1, 100)])
    video_url = URLField('视频素材链接', validators=[DataRequired(), Length(1, 200)])
    tags = SelectMultipleField('素材标签', coerce=int)
    submit = SubmitField('保存')
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MaterialForm, self).__init__(*args, **kwargs)
        
        # 根据用户角色设置达人选项
        if user and user.is_business():
            # 商务用户只能选择自己创建的达人
            self.influencer_id.choices = [(inf.id, f"{inf.name} ({inf.douyin_id})") 
                                         for inf in Influencer.query.filter_by(created_by_id=user.id).all()]
        else:
            # 投手用户可以选择所有达人
            self.influencer_id.choices = [(inf.id, f"{inf.name} ({inf.douyin_id})") 
                                         for inf in Influencer.query.all()]
        
        # 设置标签选项
        self.tags.choices = [(tag.id, tag.name) for tag in MaterialTag.query.all()]
    
    def validate_material_id(self, material_id):
        # 如果是编辑表单，需要排除当前素材的ID
        if hasattr(self, 'obj') and self.obj:
            if Material.query.filter_by(id=self.obj.id).first():
                return
        
        material = Material.query.filter_by(material_id=material_id.data).first()
        if material:
            raise ValidationError('该素材ID已存在')

# 素材标签表单
class MaterialTagForm(FlaskForm):
    name = StringField('标签名称', validators=[DataRequired(), Length(1, 50)])
    submit = SubmitField('创建')
    
    def validate_name(self, name):
        tag = MaterialTag.query.filter_by(name=name.data).first()
        if tag:
            raise ValidationError('该标签已存在')

# 推广数据表单
class PromotionDataForm(FlaskForm):
    name = StringField('推广名称', validators=[DataRequired(), Length(1, 100)])
    influencer_id = SelectField('关联达人', coerce=int, validators=[DataRequired()])
    material_id = SelectField('关联素材', coerce=int, validators=[DataRequired()])
    date = DateField('推广日期', validators=[DataRequired()], format='%Y-%m-%d')
    impressions = DecimalField('曝光量', validators=[DataRequired()])
    clicks = DecimalField('点击量', validators=[DataRequired()])
    conversions = DecimalField('转化量', validators=[DataRequired()])
    cost = DecimalField('推广消耗', validators=[DataRequired()], places=2)
    revenue = DecimalField('收入', validators=[DataRequired()], places=2)
    notes = TextAreaField('备注', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('保存')
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PromotionDataForm, self).__init__(*args, **kwargs)
        
        # 根据用户角色设置达人选项
        if user and user.is_business():
            # 商务用户只能选择自己创建的达人
            influencers = Influencer.query.filter_by(created_by_id=user.id).all()
        else:
            # 投手用户可以选择所有达人
            influencers = Influencer.query.all()
        
        self.influencer_id.choices = [(inf.id, f"{inf.name} ({inf.douyin_id})") for inf in influencers]
        
        # 初始素材选项为空，将通过JavaScript动态加载
        self.material_id.choices = []
        
        # 如果是编辑表单，设置当前选中的达人对应的素材
        if hasattr(self, 'obj') and self.obj:
            self.influencer_id.data = self.obj.material.influencer_id
            materials = Material.query.filter_by(influencer_id=self.obj.material.influencer_id).all()
            self.material_id.choices = [(mat.id, f"{mat.material_id} - {mat.video_url}") for mat in materials]
            self.material_id.data = self.obj.material_id
    
    def validate(self):
        if not super(PromotionDataForm, self).validate():
            return False
        
        # 检查是否已存在相同素材和日期的记录
        from app.models import PromotionData
        existing = PromotionData.query.filter_by(
            material_id=self.material_id.data,
            date=self.date.data
        ).first()
        
        # 如果是编辑表单，需要排除当前记录
        if hasattr(self, 'obj') and self.obj and existing and existing.id == self.obj.id:
            existing = None
        
        if existing:
            self.date.errors.append('该素材在指定日期已存在推广数据')
            return False
        
        return True