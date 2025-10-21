from flask import jsonify, request, g
from . import api
from app.models import User, AnonymousUser
from app import db


@api.route('/token', methods=['POST'])
def get_token():
    """获取认证token的端点 - 使用HTTP Basic Auth"""
    # 这里使用Flask-HTTPAuth，用户名实际上是邮箱
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': '邮箱和密码不能为空'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.verify_password(data['password']):
        # 生成认证token
        token = user.generate_auth_token(expiration=3600)
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.name if user.role else 'user'
            }
        })
    else:
        return jsonify({'success': False, 'message': '邮箱或密码错误'}), 401


@api.route('/register', methods=['POST'])
def register():
    """注册新用户 - 公开端点"""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'success': False, 'message': '用户名、邮箱和密码不能为空'}), 400

    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': '该邮箱已被注册'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': '该用户名已被使用'}), 400

    # 创建新用户
    user = User(
        email=data['email'],
        username=data['username'],
        password=data['password']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '注册成功，请登录'
    })


@api.route('/me', methods=['GET'])
def get_current_user():
    """获取当前用户信息 - 需要认证"""
    if g.current_user.is_anonymous:
        return jsonify({'success': False, 'message': '未登录'}), 401

    return jsonify({
        'success': True,
        'user': {
            'id': g.current_user.id,
            'username': g.current_user.username,
            'email': g.current_user.email,
            'role': g.current_user.role.name if g.current_user.role else 'user'
        }
    })