from flask_wtf import Form, validators
from wtforms import  StringField, SubmitField, PasswordField, TextAreaField, SelectField
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
    body = TextAreaField("enter the content", validators=[DataRequired()])
    submit = SubmitField('Submit')

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
