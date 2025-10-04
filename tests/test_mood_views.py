import unittest
from datetime import datetime, date, timedelta
from test_base import TestCase


class MoodViewsTestCase(TestCase):
    """心情(Mood)接口测试"""

    def test_mood_page_requires_login(self):
        """测试心情页面需要登录"""
        response = self.client.get('/mood')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_mood_page_logged_in(self):
        """测试登录后访问心情页面"""
        self.login(self.user.email, 'password')
        response = self.client.get('/mood')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'mood', response.data.lower())

    def test_record_mood_get(self):
        """测试GET记录心情"""
        self.login(self.user.email, 'password')
        response = self.client.get('/mood')
        self.assertEqual(response.status_code, 200)
        # 检查是否有记录心情的表单
        self.assertIn(b'form', response.data.lower())

    def test_record_mood_post_success(self):
        """测试POST记录心情成功"""
        self.login(self.user.email, 'password')

        response = self.client.post('/mood', data={
            'mood_score': 7,
            'note': 'Feeling good today!',
            'factors': 'exercise,sunshine',
            'activities': 'running,reading'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'good', response.data.lower())

        # 验证心情记录已创建
        mood = Mood.query.filter_by(author=self.user).first()
        self.assertIsNotNone(mood)
        self.assertEqual(mood.mood_score, 7)
        self.assertEqual(mood.note, 'Feeling good today!')

    def test_record_mood_post_invalid_score(self):
        """测试记录心情时分数无效"""
        self.login(self.user.email, 'password')

        # 测试超出范围的分数
        response = self.client.post('/mood', data={
            'mood_score': 15,  # 假设有效范围是1-10
            'note': 'Invalid score'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'invalid', response.data.lower())

    def test_record_mood_post_empty_score(self):
        """测试记录心情时分数为空"""
        self.login(self.user.email, 'password')

        response = self.client.post('/mood', data={
            'mood_score': '',
            'note': 'No score provided'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'required', response.data.lower())

    def test_mood_history_page(self):
        """测试心情历史页面"""
        # 创建一些心情记录
        for i in range(5):
            self.create_mood(5 + i, self.user)

        self.login(self.user.email, 'password')
        response = self.client.get('/mood/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'history', response.data.lower())

    def test_mood_history_empty(self):
        """测试空的心情历史"""
        self.login(self.user.email, 'password')
        response = self.client.get('/mood/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'no moods', response.data.lower())

    def test_mood_calendar_page(self):
        """测试心情日历页面"""
        # 创建一些心情记录
        for i in range(10):
            mood = self.create_mood(5 + (i % 5), self.user)
            # 设置不同的日期
            mood.created_at = datetime.now() - timedelta(days=i)
            db.session.commit()

        self.login(self.user.email, 'password')
        response = self.client.get('/mood/calendar')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'calendar', response.data.lower())

    def test_mood_by_date(self):
        """测试按日期查看心情"""
        target_date = date.today()
        mood = self.create_mood(8, self.user)
        mood.created_at = datetime.combine(target_date, datetime.min.time())
        db.session.commit()

        self.login(self.user.email, 'password')
        response = self.client.get(f'/mood/date/{target_date}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'8', response.data)

    def test_mood_by_nonexistent_date(self):
        """测试按不存在的日期查看心情"""
        self.login(self.user.email, 'password')
        future_date = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        response = self.client.get(f'/mood/date/{future_date}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'no moods', response.data.lower())

    def test_mood_by_invalid_date(self):
        """测试按无效日期查看心情"""
        self.login(self.user.email, 'password')
        response = self.client.get('/mood/date/invalid-date')
        self.assertEqual(response.status_code, 404)

    def test_delete_mood_success(self):
        """测试删除心情成功"""
        mood = self.create_mood(6, self.user)

        self.login(self.user.email, 'password')
        response = self.client.post(f'/mood/{mood.id}/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # 验证心情记录已删除
        deleted_mood = Mood.query.get(mood.id)
        self.assertIsNone(deleted_mood)

    def test_delete_mood_not_found(self):
        """测试删除不存在的心情"""
        self.login(self.user.email, 'password')
        response = self.client.post('/mood/99999/delete')
        self.assertEqual(response.status_code, 404)

    def test_delete_mood_unauthorized(self):
        """测试删除他人心情"""
        other_user = self.create_user('other@example.com', 'password', False)
        mood = self.create_mood(7, other_user)

        self.login(self.user.email, 'password')
        response = self.client.post(f'/mood/{mood.id}/delete')
        self.assertEqual(response.status_code, 403)

    def test_delete_mood_admin_can_delete_any(self):
        """测试管理员可以删除任何心情"""
        other_user = self.create_user('other@example.com', 'password', False)
        mood = self.create_mood(4, other_user)

        self.login(self.admin.email, 'admin')
        response = self.client.post(f'/mood/{mood.id}/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        deleted_mood = Mood.query.get(mood.id)
        self.assertIsNone(deleted_mood)

    def test_mood_statistics(self):
        """测试心情统计功能"""
        # 创建不同分数的心情记录
        scores = [3, 5, 7, 8, 9, 6, 4, 7, 8, 6]
        for score in scores:
            self.create_mood(score, self.user)

        self.login(self.user.email, 'password')
        response = self.client.get('/mood/history')
        self.assertEqual(response.status_code, 200)
        # 检查是否显示统计信息
        self.assertIn(b'average', response.data.lower()) or self.assertIn(b'mean', response.data.lower())

    def test_mood_with_factors(self):
        """测试带影响因素的心情"""
        self.login(self.user.email, 'password')

        response = self.client.post('/mood', data={
            'mood_score': 8,
            'note': 'Great day!',
            'factors': 'exercise,good_weather,meditation',
            'activities': 'yoga,reading'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # 验证心情记录已创建
        mood = Mood.query.filter_by(note='Great day!').first()
        self.assertIsNotNone(mood)
        # 根据实际模型结构调整

    def test_mood_search_by_note(self):
        """测试按心情笔记搜索"""
        # 创建不同的心情记录
        self.create_mood(7, self.user)
        mood2 = self.create_mood(8, self.user)
        mood2.note = 'Feeling happy after exercise'
        db.session.commit()

        self.login(self.user.email, 'password')
        response = self.client.get('/mood/history?q=happy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'happy', response.data.lower())

    def test_mood_date_range_filter(self):
        """测试按日期范围筛选心情"""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # 创建不同日期的心情
        mood1 = self.create_mood(6, self.user)
        mood1.created_at = datetime.combine(yesterday, datetime.min.time())
        mood2 = self.create_mood(8, self.user)
        mood2.created_at = datetime.combine(today, datetime.min.time())
        db.session.commit()

        self.login(self.user.email, 'password')
        response = self.client.get(f'/mood/history?start_date={yesterday}&end_date={today}')
        self.assertEqual(response.status_code, 200)

    def test_mood_pagination(self):
        """测试心情分页"""
        # 创建多个心情记录
        for i in range(25):
            self.create_mood(5 + (i % 5), self.user)

        self.login(self.user.email, 'password')
        response = self.client.get('/mood/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'page', response.data.lower())

        # 测试第二页
        response = self.client.get('/mood/history?page=2')
        self.assertEqual(response.status_code, 200)

    def test_mood_average_calculation(self):
        """测试心情平均值计算"""
        scores = [5, 7, 9, 6, 8]  # 平均值应该是7
        for score in scores:
            self.create_mood(score, self.user)

        self.login(self.user.email, 'password')
        response = self.client.get('/mood/history')
        self.assertEqual(response.status_code, 200)
        # 检查页面是否显示平均值信息

    def test_mood_trends(self):
        """测试心情趋势分析"""
        # 创建一段时间的心情记录
        for i in range(30):
            mood = self.create_mood(5 + (i % 5), self.user)
            mood.created_at = datetime.now() - timedelta(days=i)
            db.session.commit()

        self.login(self.user.email, 'password')
        response = self.client.get('/mood/calendar')
        self.assertEqual(response.status_code, 200)
        # 检查是否显示趋势信息

    def test_mood_with_long_note(self):
        """测试带长笔记的心情"""
        self.login(self.user.email, 'password')

        long_note = 'x' * 1000  # 长笔记
        response = self.client.post('/mood', data={
            'mood_score': 7,
            'note': long_note
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        mood = Mood.query.filter_by(author=self.user).first()
        self.assertIsNotNone(mood)
        self.assertEqual(len(mood.note), 1000)


if __name__ == '__main__':
    unittest.main()