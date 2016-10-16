from flask import flash
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for

from . import main
from datetime import datetime as dt
from .forms import LoginForm


@main.route('/')
def index():
    return render_template('base.html')
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
