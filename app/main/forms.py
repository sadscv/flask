from flask_wtf.file import FileRequired, FileAllowed
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField, IntegerField, FileField, BooleanField, DateField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError, NumberRange, Optional

from app.models import Role, User
from . import main

class NameForm(Form):
    name = StringField('what is your name', validators = [DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PostForm(Form):
    title = StringField('标题', validators=[Length(0, 64, message='标题过长')])
    content = TextAreaField('正文', validators=[DataRequired()])
    publish = SubmitField('发布')
    save = SubmitField('保存')
    delete = SubmitField('删除')

class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[
        DataRequired(), Length(1, 64), Email()
    ])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Username must have only letters,'
                                              ' numbers, dotcs or underscores')])
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me ')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if field.data != self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise  ValidationError('Username already used.')


class ThoughtForm(Form):
    content = TextAreaField('想法', validators=[
        DataRequired(message='请输入你的想法'), Length(min=1, max=500, message='内容长度应在1-500字符之间')])
    tags = StringField('标签', description='用逗号分隔')
    thought_type = SelectField('类型', choices=[
        ('note', '笔记'),
        ('quote', '引用'),
        ('idea', '想法'),
        ('task', '任务')
    ], default='note')
    source_url = StringField('来源链接', validators=[Length(0, 500)])
    is_public = BooleanField('公开', default=True)
    submit = SubmitField('发布想法')


class FileUploadForm(Form):
    upload = FileField('file')
    submit = SubmitField('Submit')


class MoodForm(Form):
    """心情记录表单"""
    mood_type = SelectField('今日心情',
                          choices=[('happy', '😊 开心'),
                                 ('calm', '😌 平静'),
                                 ('anxious', '😰 焦虑'),
                                 ('sad', '😢 伤心'),
                                 ('angry', '😠 愤怒'),
                                 ('custom', '💭 自定义')],
                          validators=[DataRequired()])

    custom_mood = StringField('自定义心情',
                            validators=[Optional(), Length(min=1, max=50)])

    intensity = IntegerField('心情强度 (1-10)',
                           default=5,
                           validators=[DataRequired(), NumberRange(min=1, max=10)])

    diary = TextAreaField('今日日记',
                        validators=[Optional(), Length(max=1000)],
                        description='记录今天发生的事情，不超过1000字')

    date = DateField('日期',
                    validators=[Optional()],
                    description='选择日期查看或记录心情')

    submit = SubmitField('保存心情')


class CommentForm(Form):
    """评论表单"""
    body = TextAreaField('评论内容', validators=[DataRequired(), Length(min=1, max=500, message='评论内容长度应在1-500字之间')])
    submit = SubmitField('发表评论')


class MoodSearchForm(Form):
    """心情搜索表单"""
    start_date = DateField('开始日期', validators=[Optional()])
    end_date = DateField('结束日期', validators=[Optional()])
    mood_type = SelectField('心情类型', choices=[
        ('', '全部'),
        ('happy', '开心'),
        ('calm', '平静'),
        ('anxious', '焦虑'),
        ('sad', '伤心'),
        ('angry', '愤怒')
    ], validators=[Optional()])

    submit = SubmitField('搜索')


