import unittest
import json
from test_base import TestCase


class ThoughtViewsTestCase(TestCase):
    """想法(Thought)接口测试"""

    def test_thoughts_page_requires_login(self):
        """测试想法页面需要登录"""
        response = self.client.get('/thoughts')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_thoughts_page_logged_in(self):
        """测试登录后访问想法页面"""
        self.login(self.user.email, 'password')
        response = self.client.get('/thoughts')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'thoughts', response.data.lower())

    def test_thoughts_page_with_thoughts(self):
        """测试包含想法的想法页面"""
        # 创建一些想法
        thought1 = self.create_thought('First thought', self.user)
        thought2 = self.create_thought('Second thought', self.user)

        self.login(self.user.email, 'password')
        response = self.client.get('/thoughts')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'First thought', response.data)
        self.assertIn(b'Second thought', response.data)

    def test_create_thought_get(self):
        """测试GET创建想法"""
        self.login(self.user.email, 'password')
        response = self.client.get('/thoughts')
        self.assertEqual(response.status_code, 200)
        # 检查是否有创建想法的表单
        self.assertIn(b'content', response.data.lower())

    def test_create_thought_post_success(self):
        """测试POST创建想法成功"""
        self.login(self.user.email, 'password')

        response = self.client.post('/thoughts', data={
            'content': 'New test thought',
            'tags': 'test,example',
            'thought_type': 'note',
            'is_public': True,
            'source_url': 'https://example.com'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New test thought', response.data)

        # 验证想法已创建
        thought = Thought.query.filter_by(content='New test thought').first()
        self.assertIsNotNone(thought)
        self.assertEqual(thought.author, self.user)
        self.assertEqual(thought.thought_type, 'note')
        self.assertTrue(thought.is_public)

    def test_create_thought_post_empty_content(self):
        """测试创建想法时内容为空"""
        self.login(self.user.email, 'password')

        response = self.client.post('/thoughts', data={
            'content': '',
            'tags': 'test',
            'thought_type': 'note'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'required', response.data.lower())

    def test_create_thought_post_long_content(self):
        """测试创建想法时内容过长"""
        self.login(self.user.email, 'password')

        long_content = 'x' * 10000  # 超长内容
        response = self.client.post('/thoughts', data={
            'content': long_content,
            'thought_type': 'note'
        })

        # 根据实际验证逻辑调整
        self.assertIn(response.status_code, [200, 400])

    def test_delete_thought_success(self):
        """测试删除想法成功"""
        thought = self.create_thought('Test thought to delete', self.user)

        self.login(self.user.email, 'password')
        response = self.client.post(f'/thought/{thought.id}/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # 验证想法已被软删除
        deleted_thought = Thought.query.get(thought.id)
        self.assertTrue(deleted_thought.is_deleted)

    def test_delete_thought_not_found(self):
        """测试删除不存在的想法"""
        self.login(self.user.email, 'password')
        response = self.client.post('/thought/99999/delete')
        self.assertEqual(response.status_code, 404)

    def test_delete_thought_unauthorized(self):
        """测试删除他人想法"""
        other_user = self.create_user('other@example.com', 'password', False)
        thought = self.create_thought("Other user's thought", other_user)

        self.login(self.user.email, 'password')
        response = self.client.post(f'/thought/{thought.id}/delete')
        self.assertEqual(response.status_code, 403)

    def test_delete_thought_admin_can_delete_any(self):
        """测试管理员可以删除任何想法"""
        other_user = self.create_user('other@example.com', 'password', False)
        thought = self.create_thought("Other user's thought", other_user)

        self.login(self.admin.email, 'admin')
        response = self.client.post(f'/thought/{thought.id}/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        deleted_thought = Thought.query.get(thought.id)
        self.assertTrue(deleted_thought.is_deleted)

    def test_thoughts_by_tag(self):
        """测试按标签筛选想法"""
        # 创建不同标签的想法
        self.create_thought('Python thought', self.user)
        thought2 = self.create_thought('Flask thought', self.user)
        thought2.tags = 'python,flask'
        db.session.commit()

        self.login(self.user.email, 'password')
        response = self.client.get('/thoughts/tag/python')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Flask thought', response.data)

    def test_thoughts_by_nonexistent_tag(self):
        """测试按不存在的标签筛选想法"""
        self.login(self.user.email, 'password')
        response = self.client.get('/thoughts/tag/nonexistent')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'no thoughts', response.data.lower())

    def test_search_thoughts(self):
        """测试搜索想法"""
        # 创建一些想法
        self.create_thought('Python programming', self.user)
        self.create_thought('Flask web framework', self.user)
        self.create_thought('JavaScript frontend', self.user)

        self.login(self.user.email, 'password')

        # 搜索 'Python'
        response = self.client.get('/thoughts/search?q=Python')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Python programming', response.data)
        self.assertNotIn(b'JavaScript frontend', response.data)

    def test_search_thoughts_empty_query(self):
        """测试搜索空查询"""
        self.login(self.user.email, 'password')
        response = self.client.get('/thoughts/search?q=')
        self.assertEqual(response.status_code, 200)

    def test_thoughts_pagination(self):
        """测试想法分页"""
        # 创建多个想法
        for i in range(25):
            self.create_thought(f'Thought {i}', self.user)

        self.login(self.user.email, 'password')
        response = self.client.get('/thoughts')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'page', response.data.lower())

        # 测试第二页
        response = self.client.get('/thoughts?page=2')
        self.assertEqual(response.status_code, 200)

    def test_thought_types(self):
        """测试不同类型的想法"""
        types = ['note', 'quote', 'idea', 'task']
        for thought_type in types:
            self.create_thought(f'{thought_type} content', self.user, thought_type)

        self.login(self.user.email, 'password')
        response = self.client.get('/thoughts')
        self.assertEqual(response.status_code, 200)

        for thought_type in types:
            self.assertIn(thought_type.encode(), response.data)

    def test_private_thoughts_only_visible_to_author(self):
        """测试私有想法只对作者可见"""
        private_thought = self.create_thought('Private thought', self.user)
        private_thought.is_public = False
        db.session.commit()

        # 创建另一个用户
        other_user = self.create_user('other@example.com', 'password', False)

        # 作者可以看到私有想法
        self.login(self.user.email, 'password')
        response = self.client.get('/thoughts')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Private thought', response.data)

        # 其他用户看不到私有想法
        self.logout()
        self.login(other_user.email, 'password')
        response = self.client.get('/thoughts')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Private thought', response.data)

    def test_thought_with_source_url(self):
        """测试带来源URL的想法"""
        self.login(self.user.email, 'password')

        response = self.client.post('/thoughts', data={
            'content': 'Thought with source',
            'source_url': 'https://example.com/article'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # 验证想法已创建并有正确的来源URL
        thought = Thought.query.filter_by(content='Thought with source').first()
        self.assertIsNotNone(thought)
        self.assertEqual(thought.source_url, 'https://example.com/article')

    def test_thought_with_invalid_source_url(self):
        """测试带无效来源URL的想法"""
        self.login(self.user.email, 'password')

        response = self.client.post('/thoughts', data={
            'content': 'Thought with invalid source',
            'source_url': 'invalid-url'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # 根据实际验证逻辑调整


if __name__ == '__main__':
    unittest.main()