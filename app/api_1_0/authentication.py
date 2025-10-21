from flask import g
from flask_httpauth import HTTPBasicAuth

from . import api
from app.models import AnonymousUser, User
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    # 确保g.current_user总是被设置
    g.current_user = AnonymousUser()
    g.token_used = False

    if email_or_token == '':
        return True
    if password == '':
        user = User.verify_auth_token(email_or_token)
        if user:
            g.current_user = user
            g.token_used = True
        return user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.before_request
@auth.login_required
def before_request():
    try:
        if hasattr(g, 'current_user') and g.current_user and \
           not g.current_user.is_anonymous and \
           not g.current_user.is_authenticated:
            return forbidden('Unconfirmed account')
    except AttributeError:
        # 如果current_user不存在，设为匿名用户
        g.current_user = AnonymousUser()