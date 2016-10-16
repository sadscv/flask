from flask_wtf import Form
from wtforms import  StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email

from . import main

class NameForm(Form):
    name = StringField('what is your name', validators = [DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Submit')



