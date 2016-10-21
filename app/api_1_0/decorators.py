from functools import wraps

from flask import g

from app.api_1_0.errors import forbidden


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permission')
            return f(*args, **kwargs)
        return decorator_function
    return decorator