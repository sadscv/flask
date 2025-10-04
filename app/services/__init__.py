"""
服务层模块
"""
from .auth_service import can_delete_content, require_delete_permission
from .permission_service import check_admin_permission, check_permission, require_permission, require_admin
from .ajax_service import ajax_route, is_ajax_request, ajax_success, ajax_error

__all__ = [
    'can_delete_content',
    'require_delete_permission',
    'check_admin_permission',
    'check_permission',
    'require_permission',
    'require_admin',
    'ajax_route',
    'is_ajax_request',
    'ajax_success',
    'ajax_error'
]