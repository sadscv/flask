from flask import flash
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask.ext.login import login_required

from app import db
from app.decorator import admin_required, permission_required
from app.models import Post, Permission
from . import main
from datetime import datetime as dt
from .forms import LoginForm, PostForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,author_id=1)
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)
@main.route('/hello')
def hello_world():
    time = dt.now()
    if session:
        if session['name'] == 'sadscv@hotmail.com':
            flash('OMG')
    return render_template('base.html', time=time)

@main.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.username.data
        return redirect(url_for('.hello_world'))
    return  render_template('login.html', form=form)

@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return 'for admin'

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderator_only():
    return 'for comment moderator'

