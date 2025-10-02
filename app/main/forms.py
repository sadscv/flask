from flask_wtf.file import FileRequired, FileAllowed
from flask_wtf import FlaskForm as Form
from wtforms import  StringField, SubmitField, PasswordField, TextAreaField, SelectField, IntegerField, FileField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError

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


