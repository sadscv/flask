import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'hard to guess'
    FLASK_ADMIN = 'sadscv@hotmail.com'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://flask:sadsad@localhost:3306/flask_blog'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://flask:sadsad@localhost:3306/flask_blog_test'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://flask:sadsad@localhost:3306/flask_blog'

config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig
}