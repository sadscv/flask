from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required, login_user, logout_user

from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from . import auth

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logged out')
    return redirect(url_for('main.index'))

@auth.route('/reg')
def reg():
    form = RegistrationForm()
    return render_template('auth/register.html', form=form)

@auth.route('/secret')
@login_required
def secret():
    return 'okay, u logined.'
