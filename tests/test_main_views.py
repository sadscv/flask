import unittest
import os
import tempfile
from test_base import TestCase


class MainViewsTestCase(TestCase):
    """主视图接口测试"""

    def test_index_page(self):
        """测试首页"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data.lower())

    def test_index_page_with_posts(self):
        """测试包含文章的首页"""
        self.create_post(title='Test Post 1', body='Test content 1')
        self.create_post(title='Test Post 2', body='Test content 2')

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post 1', response.data)
        self.assertIn(b'Test Post 2', response.data)

    def test_user_profile_page(self):
        """测试用户个人资料页面"""
        response = self.client.get(f'/user/{self.user.username}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(self.user.username).encode(), response.data)

    def test_user_profile_not_found(self):
        """测试不存在的用户资料页面"""
        response = self.client.get('/user/nonexistentuser')
        self.assertEqual(response.status_code, 404)

    def test_edit_profile_requires_login(self):
        """测试编辑个人资料需要登录"""
        response = self.client.get('/edit-profile')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_edit_profile_logged_in(self):
        """测试登录后编辑个人资料"""
        self.login(self.user.email, 'password')

        response = self.client.get('/edit-profile')
        self.assertEqual(response.status_code, 200)

        # 测试更新个人资料
        response = self.client.post('/edit-profile', data={
            'name': 'Updated Name',
            'location': 'Updated Location',
            'about_me': 'Updated about me'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.user = User.query.get(self.user.id)
        self.assertEqual(self.user.name, 'Updated Name')
        self.assertEqual(self.user.location, 'Updated Location')
        self.assertEqual(self.user.about_me, 'Updated about me')

    def test_edit_profile_admin_requires_admin(self):
        """测试管理员编辑个人资料需要管理员权限"""
        # 普通用户尝试访问管理员编辑页面
        self.login(self.user.email, 'password')
        response = self.client.get(f'/edit-profile/{self.user.id}')
        self.assertEqual(response.status_code, 403)

    def test_edit_profile_admin_success(self):
        """测试管理员成功编辑用户资料"""
        self.login(self.admin.email, 'admin')

        response = self.client.get(f'/edit-profile/{self.user.id}')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(f'/edit-profile/{self.user.id}', data={
            'email': 'updated@example.com',
            'name': 'Admin Updated Name',
            'role': 2  # User role
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        updated_user = User.query.get(self.user.id)
        self.assertEqual(updated_user.name, 'Admin Updated Name')

    def test_upload_page_requires_login(self):
        """测试上传页面需要登录"""
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_upload_page_logged_in(self):
        """测试登录后访问上传页面"""
        self.login(self.user.email, 'password')

        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'upload', response.data.lower())

    def test_file_upload_success(self):
        """测试文件上传成功"""
        self.login(self.user.email, 'password')

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'Test file content')
            temp_file_path = f.name

        try:
            with open(temp_file_path, 'rb') as f:
                response = self.client.post('/upload', data={
                    'file': (f, 'test.txt')
                }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            # 检查文件是否上传成功
            self.assertTrue(os.path.exists(os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                secure_filename('test.txt')
            )))
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_file_upload_no_file(self):
        """测试没有文件的上传"""
        self.login(self.user.email, 'password')

        response = self.client.post('/upload', data={}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # 应该显示错误消息
        self.assertIn(b'error', response.data.lower())

    def test_pagination(self):
        """测试分页功能"""
        # 创建多个文章
        for i in range(25):
            self.create_post(title=f'Post {i}', body=f'Content {i}')

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'page', response.data.lower())

        # 测试第二页
        response = self.client.get('/?page=2')
        self.assertEqual(response.status_code, 200)

    def test_static_files(self):
        """测试静态文件访问"""
        response = self.client.get('/static/css/main.css')
        self.assertIn(response.status_code, [200, 304])  # 304 for cached files

        response = self.client.get('/static/js/common.js')
        self.assertIn(response.status_code, [200, 304])


if __name__ == '__main__':
    unittest.main()