"""
AJAX相关服务
"""

from flask import jsonify, request
from functools import wraps


def ajax_route(f):
    """AJAX路由装饰器，自动处理AJAX检测和响应"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)

            # 如果已经是JSON响应，直接返回
            if isinstance(result, tuple) and len(result) == 2:
                response, status_code = result
                if hasattr(response, 'mimetype') and response.mimetype == 'application/json':
                    return result

            # 检查是否为AJAX请求
            if is_ajax_request():
                # 如果返回的是字典，转换为JSON响应
                if isinstance(result, dict):
                    return jsonify(result)
                # 如果是其他类型，包装成成功响应
                return jsonify({'success': True, 'data': result})

            return result

        except Exception as e:
            # AJAX请求出错时返回JSON错误响应
            if is_ajax_request():
                return jsonify({'success': False, 'error': str(e)}), 500
            raise

    return decorated_function


def is_ajax_request():
    """检查是否为AJAX请求"""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def ajax_success(message=None, data=None):
    """返回AJAX成功响应"""
    response = {'success': True}
    if message:
        response['message'] = message
    if data:
        response['data'] = data
    return jsonify(response)


def ajax_error(message, status_code=400):
    """返回AJAX错误响应"""
    return jsonify({'success': False, 'message': message}), status_code