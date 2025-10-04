import unittest
import json
import os
import tempfile
from flask import current_app, request, g, session
from app import create_app, db
from app.models import User, Role, Permission, Post, Thought, Mood
from werkzeug.utils import secure_filename


class TestCase(unittest.TestCase):
    """测试基类，提供通用的测试工具和方法"""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # 创建角色
        Role.insert_roles()

        # 创建测试用户
        self.user = self.create_user('test@example.com', 'password', False)
        self.admin = self.create_user('admin@example.com', 'admin', True)

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_user(self, email, password, is_admin=False):
        """创建测试用户"""
        if is_admin:
            role = Role.query.filter_by(name='Administrator').first()
        else:
            role = Role.query.filter_by(name='User').first()

        # 生成用户名
        username = email.split('@')[0]

        user = User(
            email=email,
            username=username,
            password=password,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return user

    def create_post(self, title='Test Post', body='Test body', author=None):
        """创建测试文章"""
        if author is None:
            author = self.user

        post = Post(
            title=title,
            body=body,
            author=author
        )
        db.session.add(post)
        db.session.commit()
        return post

    def create_thought(self, content='Test thought', author=None):
        """创建测试想法"""
        if author is None:
            author = self.user

        thought = Thought(
            content=content,
            author=author
        )
        db.session.add(thought)
        db.session.commit()
        return thought

    def create_mood(self, mood_score=5, author=None):
        """创建测试心情"""
        if author is None:
            author = self.user

        mood = Mood(
            mood_score=mood_score,
            author=author
        )
        db.session.add(mood)
        db.session.commit()
        return mood

    def login(self, email, password):
        """登录用户"""
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        """登出用户"""
        return self.client.get('/auth/logout', follow_redirects=True)

    def get_auth_headers(self, email=None, password=None):
        """获取API认证头"""
        if email is None:
            email = self.user.email
        if password is None:
            password = 'password'

        response = self.client.post('/auth/login', data={
            'email': email,
            'password': password
        })

        # 如果登录成功，尝试获取token
        if response.status_code == 200:
            try:
                data = json.loads(response.data)
                if 'token' in data:
                    return {
                        'Authorization': f'Bearer {data["token"]}',
                        'Content-Type': 'application/json'
                    }
            except (json.JSONDecodeError, KeyError):
                pass

        # 如果没有token，返回基本的headers
        return {
            'Content-Type': 'application/json'
        }

    def assert_redirects(self, response, expected_endpoint):
        """断言重定向到指定端点"""
        self.assertEqual(response.status_code, 302)
        self.assertIn(expected_endpoint, response.location)

    def assert_template_used(self, template_name):
        """断言使用了指定的模板"""
        self.assertIn(template_name, [template.name for template in response.jinja_env.list_templates()])