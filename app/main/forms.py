from flask_wtf import Form, validators
from wtforms import  StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email

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


