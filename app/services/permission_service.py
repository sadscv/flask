"""
权限相关服务
"""

from flask_login import current_user
from app.models import Permission


def check_admin_permission():
    """检查是否具有管理员权限"""
    return current_user.is_authenticated and current_user.can(Permission.ADMIN)


def check_permission(permission):
    """检查特定权限"""
    return current_user.is_authenticated and current_user.can(permission)


def require_permission(permission):
    """要求特定权限的装饰器，如果没有则抛出403错误"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not check_permission(permission):
                from flask import abort
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_admin(f):
    """要求管理员权限的装饰器，如果没有则抛出403错误"""
    def decorated_function(*args, **kwargs):
        if not check_admin_permission():
            from flask import abort
            abort(403)
        return f(*args, **kwargs)
    return decorated_function