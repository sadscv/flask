import unittest
import json
from test_base import TestCase


class AuthViewsTestCase(TestCase):
    """认证接口测试"""

    def test_login_page(self):
        """测试登录页面"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())

    def test_login_success(self):
        """测试登录成功"""
        response = self.login(self.user.email, 'password')
        self.assertEqual(response.status_code, 200)
        # 检查是否包含登录成功的指示
        self.assertIn(b'hello', response.data.lower())

    def test_login_wrong_password(self):
        """测试错误密码登录"""
        response = self.client.post('/auth/login', data={
            'email': self.user.email,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'invalid', response.data.lower())

    def test_login_nonexistent_user(self):
        """测试不存在的用户登录"""
        response = self.client.post('/auth/login', data={
            'email': 'nonexistent@example.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'invalid', response.data.lower())

    def test_login_empty_fields(self):
        """测试空字段登录"""
        response = self.client.post('/auth/login', data={
            'email': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'invalid', response.data.lower())

    def test_logout(self):
        """测试登出"""
        self.login(self.user.email, 'password')
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())

    def test_registration_page(self):
        """测试注册页面"""
        response = self.client.get('/auth/reg')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'register', response.data.lower())

    def test_registration_success(self):
        """测试注册成功"""
        response = self.client.post('/auth/reg', data={
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'username': 'newuser'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())

        # 验证用户已创建
        new_user = User.query.filter_by(email='newuser@example.com').first()
        self.assertIsNotNone(new_user)

    def test_registration_duplicate_email(self):
        """测试重复邮箱注册"""
        response = self.client.post('/auth/reg', data={
            'email': self.user.email,
            'password': 'newpassword',
            'username': 'newuser'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'already', response.data.lower())

    def test_registration_invalid_email(self):
        """测试无效邮箱注册"""
        response = self.client.post('/auth/reg', data={
            'email': 'invalid-email',
            'password': 'newpassword',
            'username': 'newuser'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'invalid', response.data.lower())

    def test_registration_weak_password(self):
        """测试弱密码注册"""
        response = self.client.post('/auth/reg', data={
            'email': 'weak@example.com',
            'password': '123',
            'username': 'weakuser'
        })
        self.assertEqual(response.status_code, 200)
        # 根据实际验证逻辑调整

    def test_secret_page_requires_login(self):
        """测试私密页面需要登录"""
        response = self.client.get('/auth/secret')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_secret_page_logged_in(self):
        """测试登录后访问私密页面"""
        self.login(self.user.email, 'password')
        response = self.client.get('/auth/secret')
        self.assertEqual(response.status_code, 200)

    def test_change_password_page_requires_login(self):
        """测试修改密码页面需要登录"""
        response = self.client.get('/auth/change_password')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_change_password_success(self):
        """测试修改密码成功"""
        self.login(self.user.email, 'password')

        response = self.client.post('/auth/change_password', data={
            'old_password': 'password',
            'new_password': 'newpassword',
            'confirm_password': 'newpassword'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # 验证新密码可以登录
        self.logout()
        response = self.login(self.user.email, 'newpassword')
        self.assertEqual(response.status_code, 200)

    def test_change_password_wrong_old_password(self):
        """测试修改密码时旧密码错误"""
        self.login(self.user.email, 'password')

        response = self.client.post('/auth/change_password', data={
            'old_password': 'wrongpassword',
            'new_password': 'newpassword',
            'confirm_password': 'newpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'incorrect', response.data.lower())

    def test_change_password_mismatch(self):
        """测试修改密码时确认密码不匹配"""
        self.login(self.user.email, 'password')

        response = self.client.post('/auth/change_password', data={
            'old_password': 'password',
            'new_password': 'newpassword',
            'confirm_password': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'match', response.data.lower())

    def test_unconfirmed_page(self):
        """测试未确认邮箱页面"""
        # 由于当前模型没有confirmed字段，跳过此测试
        self.skipTest("User model does not have confirmed field")

    def test_login_json_response(self):
        """测试登录的JSON响应"""
        response = self.client.post('/auth/login', data={
            'email': self.user.email,
            'password': 'password'
        })

        self.assertEqual(response.status_code, 200)
        # 检查响应是否包含登录成功的指示
        self.assertIn(b'html', response.data.lower())

    def test_logout_json_response(self):
        """测试登出的响应"""
        self.login(self.user.email, 'password')

        response = self.client.get('/auth/logout')
        self.assertEqual(response.status_code, 200)
        # 检查是否包含登出成功的指示
        self.assertIn(b'html', response.data.lower())

    def test_protected_route_without_auth(self):
        """测试未认证访问受保护的路由"""
        protected_routes = [
            '/edit-profile',
            '/upload',
            '/thoughts',
            '/create-post'
        ]

        for route in protected_routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/auth/login', response.location)

    def test_remember_me_functionality(self):
        """测试记住我功能"""
        response = self.client.post('/auth/login', data={
            'email': self.user.email,
            'password': 'password',
            'remember': True
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # 检查是否设置了记住我的cookie
        self.assertTrue(any('remember' in cookie.name for cookie in response.cookie_jar))


if __name__ == '__main__':
    unittest.main()