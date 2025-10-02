#! /usr/bin/env python
import os
import unittest

from flask_migrate import Migrate
from flask.cli import FlaskGroup

from app import create_app, db
from app.models import User, Role, Post, Thought

def create_app_wrapper():
    return create_app(os.getenv('FLASK_CONFIG') or 'default')

app = create_app_wrapper()
cli = FlaskGroup(create_app=create_app_wrapper)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Thought=Thought)

@app.cli.command()
def test():
    """Run the unit tests"""
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)