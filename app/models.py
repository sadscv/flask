from datetime import datetime

import bleach
from flask import current_app
from flask import url_for
from itsdangerous import Serializer
from markdown import markdown
from wtforms import ValidationError

from . import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0X08
    WRITE_THOUGHTS = 0x10
    ADMIN = 0x80


class User(UserMixin, db.Model):
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # 初始化权限。若role不存在则用户身份只可能是admin或者anonymous.
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(permission=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    thoughts = db.relationship('Thought', backref='author', lazy='dynamic')
    moods = db.relationship('Mood', backref='author', lazy='dynamic')
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)


    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id' : self.id}).decode('utf-8')

    def to_json(self):
        json_user = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return None
        return User.query.get(data['id'])

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMIN)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %s>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_anonymous(self):
        return True

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role')

    @staticmethod
    def insert_roles():
        roles = {
            'User' : (Permission.FOLLOW|
                      Permission.COMMENT|
                      Permission.WRITE_ARTICLES|
                      Permission.WRITE_THOUGHTS, True),
            'Moderator' : (Permission.FOLLOW|
                           Permission.COMMENT|
                           Permission.WRITE_ARTICLES|
                           Permission.WRITE_THOUGHTS|
                           Permission.MODERATE_COMMENTS, False),
            'Admin' : (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Post(db.Model):
    __tablename__ = 'Posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column('title', db.String(128))
    edit_date = db.Column('edit_date', db.DateTime)
    views = db.Column(db.Integer, default=0)  # 阅读数
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def to_json(self):
        json_post = {
            'url' : url_for('api.get_post', id=self.id, _external=True),
            'body' : self.body,
            'body_html' : self.body_html,
            'timestamp' : self.timestamp,
            # 'author' : url_for('api.get_user', id=self.author_id,
            #                    _external=True),
        }
        return json_post

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img',
                        'table', 'thead', 'tbody', 'tr', 'th', 'td',
                        'div', 'span', 'hr', 'br', 'del', 'ins', 'mark',
                        'kbd', 'samp', 'var', 'sub', 'sup', 'small']
        target.body_html = bleach.linkify(markdown(value, output_format='html',
                                                  extensions=['codehilite', 'tables', 'toc', 'fenced_code']))
        # target.body_html = bleach.clean(
        #     markdown(value, output_format='html'),
        #     tags=allowed_tags, strip=True)

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


    def __repr__(self):
        return '<Post %s>' % self.id

class Thought(db.Model):
    __tablename__ = 'thoughts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    content_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tags = db.Column(db.String(200))
    is_public = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    thought_type = db.Column(db.String(20), default='note')
    source_url = db.Column(db.String(500))

    def to_json(self):
        json_thought = {
            'url': url_for('api.get_thought', id=self.id, _external=True),
            'content': self.content,
            'content_html': self.content_html,
            'timestamp': self.timestamp,
            'author': self.author.username,
            'tags': self.tags.split(',') if self.tags else [],
            'thought_type': self.thought_type,
            'source_url': self.source_url,
            'is_public': self.is_public
        }
        return json_thought

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        thought_types = ['note', 'quote', 'idea', 'task']

        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            thought = Thought(
                content=forgery_py.lorem_ipsum.sentence(randint(5, 15)),
                timestamp=forgery_py.date.date(True),
                author=u,
                thought_type=randint(0, 3),
                is_public=randint(0, 1) == 1
            )
            db.session.add(thought)
        db.session.commit()

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'br', 'span']
        target.content_html = bleach.linkify(markdown(value, output_format='html'))

    @staticmethod
    def from_json(json_thought):
        content = json_thought.get('content')
        if content is None or content == '':
            raise ValidationError('thought does not have content')
        return Thought(
            content=content,
            tags=json_thought.get('tags', ''),
            thought_type=json_thought.get('thought_type', 'note'),
            source_url=json_thought.get('source_url', ''),
            is_public=json_thought.get('is_public', True)
        )

    def __repr__(self):
        return '<Thought %s>' % self.id


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('Posts.id'))
    disabled = db.Column(db.Boolean, default=False)  # 是否被禁用

    # 关系定义
    author = db.relationship('User', backref='comments', lazy='joined')

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': self.author.username,
            'post_id': self.post_id
        }
        return json_comment

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(markdown(value, output_format='html'))

    def __repr__(self):
        return '<Comment %s>' % self.id


class Mood(db.Model):
    __tablename__ = 'moods'
    id = db.Column(db.Integer, primary_key=True)
    mood_type = db.Column(db.String(20), nullable=False)  # 开心、平静、焦虑、伤心、愤怒、自定义
    custom_mood = db.Column(db.String(50))  # 自定义心情名称
    diary = db.Column(db.Text)  # 日记内容
    intensity = db.Column(db.Integer, default=5)  # 心情强度 1-10
    date = db.Column(db.Date, index=True, default=datetime.utcnow().date)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 预定义的心情类型和对应的颜色、图标
    MOOD_CONFIG = {
        'happy': {'color': 'bg-yellow-100', 'text_color': 'text-yellow-800', 'icon': '😊', 'label': '开心'},
        'calm': {'color': 'bg-blue-100', 'text_color': 'text-blue-800', 'icon': '😌', 'label': '平静'},
        'anxious': {'color': 'bg-purple-100', 'text_color': 'text-purple-800', 'icon': '😰', 'label': '焦虑'},
        'sad': {'color': 'bg-gray-100', 'text_color': 'text-gray-800', 'icon': '😢', 'label': '伤心'},
        'angry': {'color': 'bg-red-100', 'text_color': 'text-red-800', 'icon': '😠', 'label': '愤怒'},
        'custom': {'color': 'bg-green-100', 'text_color': 'text-green-800', 'icon': '💭', 'label': '自定义'}
    }

    def to_json(self):
        return {
            'id': self.id,
            'mood_type': self.mood_type,
            'custom_mood': self.custom_mood,
            'diary': self.diary,
            'intensity': self.intensity,
            'date': self.date.isoformat() if self.date else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'author': self.author.username
        }

    @staticmethod
    def get_mood_stats(user_id, days=30):
        """获取用户最近几天的心情统计"""
        try:
            from datetime import timedelta
            from sqlalchemy import func

            start_date = datetime.utcnow().date() - timedelta(days=days)

            # 查询指定天数内的心情记录
            try:
                moods = Mood.query.filter(
                    Mood.author_id == user_id,
                    Mood.date >= start_date
                ).all()
            except:
                # 如果查询失败，返回空数据
                return {
                    'mood_distribution': {},
                    'daily_moods': {},
                    'total_days': 0
                }

            # 按心情类型分组统计
            mood_counts = {}
            for mood in moods:
                try:
                    key = mood.custom_mood if mood.mood_type == 'custom' else mood.mood_type
                    mood_counts[key] = mood_counts.get(key, 0) + 1
                except:
                    continue

            # 按日期统计
            daily_moods = {}
            for mood in moods:
                try:
                    daily_moods[mood.date.isoformat()] = {
                        'mood': mood.custom_mood if mood.mood_type == 'custom' else mood.mood_type,
                        'intensity': mood.intensity or 5
                    }
                except:
                    continue

            return {
                'mood_distribution': mood_counts,
                'daily_moods': daily_moods,
                'total_days': len(set(m.date for m in moods if hasattr(m, 'date')))
            }
        except Exception as e:
            # 出现任何错误，返回安全的默认值
            print(f"Error in get_mood_stats: {e}")
            return {
                'mood_distribution': {},
                'daily_moods': {},
                'total_days': 0
            }

    def __repr__(self):
        return f'<Mood {self.mood_type} on {self.date}>'


db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Thought.content, 'set', Thought.on_changed_content)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)
