"""
安全令牌服务 - 替换不安全的令牌验证系统
"""

import jwt
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
from werkzeug.security import check_password_hash
from app.models import User


class TokenService:
    """安全的JWT令牌服务"""

    @staticmethod
    def generate_token(user):
        """生成安全的JWT令牌"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'exp': datetime.utcnow() + current_app.config.get('JWT_EXPIRATION_DELTA', timedelta(hours=24)),
            'iat': datetime.utcnow(),
            'jti': secrets.token_hex(16)  # JWT ID for uniqueness
        }

        secret_key = current_app.config.get('SECRET_KEY')
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def verify_token(token):
        """验证JWT令牌"""
        try:
            secret_key = current_app.config.get('SECRET_KEY')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])

            # 检查用户是否仍然存在
            user = User.query.get(payload['user_id'])
            if not user:
                return None

            return user
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    @staticmethod
    def auth_required(f):
        """认证装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'success': False,
                    'message': '缺少认证令牌'
                }), 401

            token = auth_header.split(' ')[1]
            user = TokenService.verify_token(token)

            if not user:
                return jsonify({
                    'success': False,
                    'message': '无效或已过期的认证令牌'
                }), 401

            # 将用户信息添加到请求上下文
            request.current_user = user
            return f(*args, **kwargs)
        return decorated_function

    @staticmethod
    def admin_required(f):
        """管理员权限装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'success': False,
                    'message': '缺少认证令牌'
                }), 401

            token = auth_header.split(' ')[1]
            user = TokenService.verify_token(token)

            if not user:
                return jsonify({
                    'success': False,
                    'message': '无效或已过期的认证令牌'
                }), 401

            if not user.is_administrator():
                return jsonify({
                    'success': False,
                    'message': '需要管理员权限'
                }), 403

            request.current_user = user
            return f(*args, **kwargs)
        return decorated_function


def verify_token_from_request():
    """从请求中提取并验证Authorization header的令牌"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        # Try secure token validation first
        user = TokenService.verify_token(token)
        if not user:
            # Check if it's a legacy token and migrate it
            if LegacyTokenMigrator.is_legacy_token(token):
                new_token = LegacyTokenMigrator.migrate_legacy_token(token)
                user = TokenService.verify_token(new_token) if new_token else None

        return user
    except Exception:
        return None


class LegacyTokenMigrator:
    """处理旧版不安全令牌的迁移"""

    @staticmethod
    def is_legacy_token(token):
        """检查是否为旧版不安全令牌"""
        return token.startswith('real_token_')

    @staticmethod
    def migrate_legacy_token(token):
        """迁移旧版令牌到安全令牌（仅用于过渡期）"""
        try:
            if not LegacyTokenMigrator.is_legacy_token(token):
                return None

            # 解析旧令牌获取用户ID
            token_parts = token.split('_')
            if len(token_parts) < 3:
                return None

            user_id = int(token_parts[2])
            user = User.query.get(user_id)

            if not user:
                return None

            # 生成新的安全令牌
            return TokenService.generate_token(user)
        except (IndexError, ValueError):
            return None


# 向Flask应用配置中添加JWT相关设置
def configure_jwt(app):
    """配置JWT相关设置"""
    app.config.setdefault('JWT_EXPIRATION_DELTA', timedelta(hours=24))
    app.config.setdefault('JWT_ALGORITHM', 'HS256')