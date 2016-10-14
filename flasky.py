from flask import Flask
from datetime import datetime as dt

from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess'
bootstrap = Bootstrap(app)

class NameForm(Form):
    name = StringField('what is your name', validators = [DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
def hello_world():
    time = dt.now()
    return render_template('base.html', time=time)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.username.data
        return redirect('/test')
    return  render_template('login.html', form=form)


# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404
#
# @app.errorhandler(500)
# def internal_error(e):
#     return render_template('404.html'), 500


if __name__ == '__main__':
    app.run()
