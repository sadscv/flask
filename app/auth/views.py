from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required, login_user, logout_user, current_user

from app import db
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm
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


@auth.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/secret')
@login_required
def secret():
    return 'okay, u logined.'


@auth.route('/change_password', methods=['GET' ,'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.previous_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('your password has been updated')
            return redirect(url_for('main.index'))
        else:
            flash('previous password is not matched')
    return render_template('auth/change_password.html', form=form)


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))
    return redirect(url_for('main.index'))
    # return render_template('auth/unconfirmed.html')


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        # if request.endpoint[:5] != 'auth.':
        #     return render_template(url_for('auth.unconfirmed'))
