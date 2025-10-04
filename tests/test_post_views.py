import unittest
from test_base import TestCase


class PostViewsTestCase(TestCase):
    """文章(Post)接口测试"""

    def test_create_post_page_requires_permission(self):
        """测试创建文章页面需要权限"""
        # 普通用户没有写文章权限时
        response = self.client.get('/create-post')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_create_post_page_with_permission(self):
        """测试有权限时访问创建文章页面"""
        # 给用户添加写文章权限
        self.user.role.permissions = Permission.WRITE_ARTICLES
        db.session.commit()

        self.login(self.user.email, 'password')
        response = self.client.get('/create-post')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'create', response.data.lower())

    def test_create_post_success(self):
        """测试创建文章成功"""
        # 给用户添加写文章权限
        self.user.role.permissions = Permission.WRITE_ARTICLES
        db.session.commit()

        self.login(self.user.email, 'password')

        response = self.client.post('/create-post', data={
            'title': 'Test Post Title',
            'body': 'This is a test post content with **markdown**.',
            'tags': 'test,example'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post Title', response.data)

        # 验证文章已创建
        post = Post.query.filter_by(title='Test Post Title').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.author, self.user)

    def test_create_post_without_permission(self):
        """测试没有权限时创建文章"""
        self.login(self.user.email, 'password')

        response = self.client.post('/create-post', data={
            'title': 'Unauthorized Post',
            'body': 'This should not be created'
        })

        self.assertEqual(response.status_code, 403)

    def test_create_post_empty_title(self):
        """测试创建空标题文章"""
        self.user.role.permissions = Permission.WRITE_ARTICLES
        db.session.commit()

        self.login(self.user.email, 'password')

        response = self.client.post('/create-post', data={
            'title': '',
            'body': 'Content without title'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'required', response.data.lower())

    def test_create_post_empty_body(self):
        """测试创建空内容文章"""
        self.user.role.permissions = Permission.WRITE_ARTICLES
        db.session.commit()

        self.login(self.user.email, 'password')

        response = self.client.post('/create-post', data={
            'title': 'Title without content',
            'body': ''
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'required', response.data.lower())

    def test_view_post_page(self):
        """测试查看文章页面"""
        post = self.create_post('Test Post', 'Test content')

        response = self.client.get(f'/post/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post', response.data)
        self.assertIn(b'Test content', response.data)

    def test_view_nonexistent_post(self):
        """测试查看不存在的文章"""
        response = self.client.get('/post/99999')
        self.assertEqual(response.status_code, 404)

    def test_edit_post_page_author(self):
        """测试作者编辑文章页面"""
        post = self.create_post('Test Post', 'Test content', self.user)

        self.login(self.user.email, 'password')
        response = self.client.get(f'/edit_post/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post', response.data)

    def test_edit_post_page_admin(self):
        """测试管理员编辑文章页面"""
        post = self.create_post('Test Post', 'Test content', self.user)

        self.login(self.admin.email, 'admin')
        response = self.client.get(f'/edit_post/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post', response.data)

    def test_edit_post_page_unauthorized(self):
        """测试未授权用户编辑文章页面"""
        other_user = self.create_user('other@example.com', 'password', False)
        post = self.create_post('Test Post', 'Test content', other_user)

        self.login(self.user.email, 'password')
        response = self.client.get(f'/edit_post/{post.id}')
        self.assertEqual(response.status_code, 403)

    def test_edit_post_success(self):
        """测试编辑文章成功"""
        post = self.create_post('Original Title', 'Original content', self.user)

        self.login(self.user.email, 'password')

        response = self.client.post(f'/edit_post/{post.id}', data={
            'title': 'Updated Title',
            'body': 'Updated content with more details'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated Title', response.data)

        # 验证文章已更新
        updated_post = Post.query.get(post.id)
        self.assertEqual(updated_post.title, 'Updated Title')
        self.assertEqual(updated_post.body, 'Updated content with more details')

    def test_edit_post_admin_success(self):
        """测试管理员编辑文章成功"""
        post = self.create_post('Original Title', 'Original content', self.user)

        self.login(self.admin.email, 'admin')

        response = self.client.post(f'/edit_post/{post.id}', data={
            'title': 'Admin Updated Title',
            'body': 'Admin updated content'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        updated_post = Post.query.get(post.id)
        self.assertEqual(updated_post.title, 'Admin Updated Title')

    def test_edit_post_unauthorized(self):
        """测试未授权编辑文章"""
        other_user = self.create_user('other@example.com', 'password', False)
        post = self.create_post('Test Post', 'Test content', other_user)

        self.login(self.user.email, 'password')

        response = self.client.post(f'/edit_post/{post.id}', data={
            'title': 'Hacked Title',
            'body': 'Hacked content'
        })

        self.assertEqual(response.status_code, 403)

    def test_delete_post_author(self):
        """测试作者删除文章"""
        post = self.create_post('Test Post', 'Test content', self.user)

        self.login(self.user.email, 'password')
        response = self.client.get(f'/delete_post/{post.id}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # 验证文章已删除
        deleted_post = Post.query.get(post.id)
        self.assertIsNone(deleted_post)

    def test_delete_post_admin(self):
        """测试管理员删除文章"""
        post = self.create_post('Test Post', 'Test content', self.user)

        self.login(self.admin.email, 'admin')
        response = self.client.get(f'/delete_post/{post.id}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        deleted_post = Post.query.get(post.id)
        self.assertIsNone(deleted_post)

    def test_delete_post_unauthorized(self):
        """测试未授权删除文章"""
        other_user = self.create_user('other@example.com', 'password', False)
        post = self.create_post('Test Post', 'Test content', other_user)

        self.login(self.user.email, 'password')
        response = self.client.get(f'/delete_post/{post.id}')
        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_post(self):
        """测试删除不存在的文章"""
        self.login(self.user.email, 'password')
        response = self.client.get('/delete_post/99999')
        self.assertEqual(response.status_code, 404)

    def test_post_with_markdown_content(self):
        """测试包含Markdown内容的文章"""
        self.user.role.permissions = Permission.WRITE_ARTICLES
        db.session.commit()

        self.login(self.user.email, 'password')

        markdown_content = '''
# Heading 1
## Heading 2

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2
- List item 3

```python
def hello_world():
    print("Hello, World!")
```

[Link](https://example.com)
        '''.strip()

        response = self.client.post('/create-post', data={
            'title': 'Markdown Test Post',
            'body': markdown_content
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Heading 1', response.data)

        # 验证文章已创建
        post = Post.query.filter_by(title='Markdown Test Post').first()
        self.assertIsNotNone(post)
        self.assertIn('# Heading 1', post.body)

    def test_post_pagination(self):
        """测试文章分页"""
        # 创建多个文章
        for i in range(25):
            self.create_post(f'Post {i}', f'Content {i}')

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'page', response.data.lower())

        # 测试第二页
        response = self.client.get('/?page=2')
        self.assertEqual(response.status_code, 200)

    def test_post_by_user(self):
        """测试按用户查看文章"""
        # 创建不同用户的文章
        other_user = self.create_user('author@example.com', 'password', False)
        self.create_post('User Post 1', 'Content 1', other_user)
        self.create_post('User Post 2', 'Content 2', other_user)

        response = self.client.get(f'/user/{other_user.username}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User Post 1', response.data)
        self.assertIn(b'User Post 2', response.data)

    def test_post_search(self):
        """测试搜索文章"""
        # 创建一些文章
        self.create_post('Python Tutorial', 'Learn Python programming')
        self.create_post('Flask Guide', 'Learn Flask web framework')
        self.create_post('JavaScript Basics', 'Learn JavaScript fundamentals')

        # 搜索 'Python'
        response = self.client.get('/?q=Python')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Python Tutorial', response.data)
        self.assertNotIn(b'JavaScript Basics', response.data)

    def test_post_with_long_title(self):
        """测试长标题文章"""
        self.user.role.permissions = Permission.WRITE_ARTICLES
        db.session.commit()

        self.login(self.user.email, 'password')

        long_title = 'x' * 200  # 很长的标题
        response = self.client.post('/create-post', data={
            'title': long_title,
            'body': 'Content with long title'
        })

        # 根据实际验证逻辑调整
        self.assertIn(response.status_code, [200, 400])

    def test_post_creation_timestamp(self):
        """测试文章创建时间戳"""
        import time
        before_creation = int(time.time())

        self.user.role.permissions = Permission.WRITE_ARTICLES
        db.session.commit()

        self.login(self.user.email, 'password')

        response = self.client.post('/create-post', data={
            'title': 'Timestamp Test',
            'body': 'Testing timestamp'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        post = Post.query.filter_by(title='Timestamp Test').first()
        self.assertIsNotNone(post)
        self.assertGreaterEqual(int(post.timestamp.timestamp()), before_creation)


if __name__ == '__main__':
    unittest.main()