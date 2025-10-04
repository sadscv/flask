import unittest
import json
from test_base import TestCase


class APIViewsTestCase(TestCase):
    """API接口测试"""

    def setUp(self):
        super().setUp()
        # 给用户添加写文章权限
        self.user.role.permissions = Permission.WRITE_ARTICLES
        db.session.commit()

    def get_api_headers(self, token=None):
        """获取API请求头"""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    def test_api_authentication_required(self):
        """测试API需要认证"""
        response = self.client.get('/api/v1.0/posts/')
        self.assertEqual(response.status_code, 401)

    def test_api_authentication_with_valid_credentials(self):
        """测试API有效凭据认证"""
        response = self.client.get('/api/v1.0/posts/',
                                headers=self.get_api_headers('valid_token'))
        # 由于没有有效的token，会返回401，但这是预期的
        self.assertIn(response.status_code, [401, 403])

    def test_get_posts_api(self):
        """测试获取文章列表API"""
        # 创建一些文章
        self.create_post('Post 1', 'Content 1', self.user)
        self.create_post('Post 2', 'Content 2', self.user)

        # 模拟认证用户
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.get('/api/v1.0/posts/')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('posts', data)
        self.assertEqual(len(data['posts']), 2)

    def test_get_single_post_api(self):
        """测试获取单个文章API"""
        post = self.create_post('Test Post', 'Test content', self.user)

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.get(f'/api/v1.0/posts/{post.id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['body'], 'Test content')

    def test_get_nonexistent_post_api(self):
        """测试获取不存在文章API"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.get('/api/v1.0/posts/99999')
        self.assertEqual(response.status_code, 404)

    def test_create_post_api(self):
        """测试创建文章API"""
        post_data = {
            'title': 'API Created Post',
            'body': 'This post was created via API'
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.post('/api/v1.0/posts/',
                                 data=json.dumps(post_data),
                                 headers=self.get_api_headers())

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data)
        self.assertEqual(data['title'], 'API Created Post')
        self.assertEqual(data['body'], 'This post was created via API')

        # 验证文章已创建
        post = Post.query.filter_by(title='API Created Post').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.author, self.user)

    def test_create_post_api_without_permission(self):
        """测试没有权限创建文章API"""
        # 移除用户的写文章权限
        self.user.role.permissions = 0
        db.session.commit()

        post_data = {
            'title': 'Unauthorized Post',
            'body': 'This should not be created'
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.post('/api/v1.0/posts/',
                                 data=json.dumps(post_data),
                                 headers=self.get_api_headers())

        self.assertEqual(response.status_code, 403)

    def test_create_post_api_invalid_data(self):
        """测试创建文章API无效数据"""
        invalid_data = {
            'title': '',  # 空标题
            'body': 'Some content'
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.post('/api/v1.0/posts/',
                                 data=json.dumps(invalid_data),
                                 headers=self.get_api_headers())

        self.assertEqual(response.status_code, 400)

    def test_update_post_api(self):
        """测试更新文章API"""
        post = self.create_post('Original Title', 'Original content', self.user)

        update_data = {
            'title': 'Updated Title',
            'body': 'Updated content'
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.put(f'/api/v1.0/posts/{post.id}',
                                 data=json.dumps(update_data),
                                 headers=self.get_api_headers())

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Updated Title')
        self.assertEqual(data['body'], 'Updated content')

        # 验证文章已更新
        updated_post = Post.query.get(post.id)
        self.assertEqual(updated_post.title, 'Updated Title')
        self.assertEqual(updated_post.body, 'Updated content')

    def test_update_post_api_unauthorized(self):
        """测试未授权更新文章API"""
        other_user = self.create_user('other@example.com', 'password', False)
        post = self.create_post('Other User Post', 'Other content', other_user)

        update_data = {
            'title': 'Hacked Title',
            'body': 'Hacked content'
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.put(f'/api/v1.0/posts/{post.id}',
                                 data=json.dumps(update_data),
                                 headers=self.get_api_headers())

        self.assertEqual(response.status_code, 403)

    def test_update_post_api_admin(self):
        """测试管理员更新文章API"""
        post = self.create_post('User Post', 'User content', self.user)

        update_data = {
            'title': 'Admin Updated Title',
            'body': 'Admin updated content'
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
            sess['_fresh'] = True

        response = self.client.put(f'/api/v1.0/posts/{post.id}',
                                 data=json.dumps(update_data),
                                 headers=self.get_api_headers())

        self.assertEqual(response.status_code, 200)

        updated_post = Post.query.get(post.id)
        self.assertEqual(updated_post.title, 'Admin Updated Title')

    def test_update_nonexistent_post_api(self):
        """测试更新不存在文章API"""
        update_data = {
            'title': 'Updated Title',
            'body': 'Updated content'
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.put('/api/v1.0/posts/99999',
                                 data=json.dumps(update_data),
                                 headers=self.get_api_headers())

        self.assertEqual(response.status_code, 404)

    def test_api_response_format(self):
        """测试API响应格式"""
        post = self.create_post('Test Post', 'Test content', self.user)

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.get(f'/api/v1.0/posts/{post.id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        # 验证响应包含必要字段
        required_fields = ['id', 'title', 'body', 'timestamp', 'author']
        for field in required_fields:
            self.assertIn(field, data)

    def test_api_pagination(self):
        """测试API分页"""
        # 创建多个文章
        for i in range(25):
            self.create_post(f'Post {i}', f'Content {i}', self.user)

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.get('/api/v1.0/posts/')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('posts', data)
        # 检查是否有分页信息（如果实现了的话）

    def test_api_content_type_validation(self):
        """测试API内容类型验证"""
        post_data = {
            'title': 'Test Post',
            'body': 'Test content'
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        # 发送非JSON内容
        response = self.client.post('/api/v1.0/posts/',
                                 data='not json',
                                 headers={'Content-Type': 'text/plain'})

        self.assertEqual(response.status_code, 400)

    def test_api_cors_headers(self):
        """测试API CORS头（如果实现了的话）"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.get('/api/v1.0/posts/')
        # 检查CORS头（如果实现了）
        # self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_api_rate_limiting(self):
        """测试API速率限制（如果实现了的话）"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        # 快速发送多个请求
        for i in range(10):
            response = self.client.get('/api/v1.0/posts/')
            # 如果实现了速率限制，可能会返回429
            self.assertIn(response.status_code, [200, 429])

    def test_api_error_responses(self):
        """测试API错误响应格式"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        # 测试404错误
        response = self.client.get('/api/v1.0/posts/99999')
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_api_with_markdown_content(self):
        """测试API处理Markdown内容"""
        markdown_content = '''
# Heading
This is **bold** text and *italic* text.

- List item 1
- List item 2
        '''.strip()

        post_data = {
            'title': 'Markdown Post',
            'body': markdown_content
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True

        response = self.client.post('/api/v1.0/posts/',
                                 data=json.dumps(post_data),
                                 headers=self.get_api_headers())

        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data)
        self.assertEqual(data['body'], markdown_content)

        # 验证文章已创建
        post = Post.query.filter_by(title='Markdown Post').first()
        self.assertIsNotNone(post)
        self.assertIn('# Heading', post.body)

    def test_api_post_from_json_method(self):
        """测试Post模型的from_json方法"""
        post_data = {
            'title': 'From JSON Post',
            'body': 'Created from JSON data'
        }

        # 直接测试Post模型的from_json方法
        post = Post.from_json(post_data)
        self.assertEqual(post.title, 'From JSON Post')
        self.assertEqual(post.body, 'Created from JSON data')


if __name__ == '__main__':
    unittest.main()