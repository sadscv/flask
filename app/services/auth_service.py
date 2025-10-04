"""
认证相关服务
"""

from flask import abort
from flask_login import current_user
from .permission_service import check_admin_permission


def can_delete_content(content_author):
    """检查当前用户是否可以删除内容"""
    # 内容作者可以删除自己的内容
    if content_author == current_user:
        return True

    # 管理员可以删除任何内容
    if check_admin_permission():
        return True

    return False


def require_delete_permission(content_author):
    """要求删除权限，如果没有则抛出403错误"""
    if not can_delete_content(content_author):
        abort(403)