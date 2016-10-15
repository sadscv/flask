from flask import Flask
from datetime import datetime as dt

from flask import flash
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask_migrate import Migrate, MigrateCommand
from flask_script import Shell
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'mysql+pymysql://flask:sadsad@localhost:3306/flask_blog'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

class NameForm(Form):
    name = StringField('what is your name', validators = [DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %s>' % self.username


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))

@app.route('/')
def hello_world():
    time = dt.now()
    if session['name'] == 'sadscv@hotmail.com':
        flash('OMG')
    return render_template('base.html', time=time)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.username.data
        return redirect(url_for('hello_world'))
    return  render_template('login.html', form=form)


# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404
#
# @app.errorhandler(500)
# def internal_error(e):
#     return render_template('404.html'), 500


if __name__ == '__main__':
    manager.run()
