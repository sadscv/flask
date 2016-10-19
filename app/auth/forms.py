from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import  DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models import User


class LoginForm(Form):
    email = StringField('Email', validators = [DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('keep me logged in')
    submit = SubmitField('login')

class RegistrationForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('username', validators=[
        DataRequired(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                            'Usernames must have only letters, '
                                            'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords not matched')])
    password2 = PasswordField('Retype Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise  ValidationError('Email is already regiested')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise  ValidationError('Username is already used')

class ChangePasswordForm(Form):
    previous_password = PasswordField('previous password',
                                      validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='password  not matched')])
    password2 = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('OK')