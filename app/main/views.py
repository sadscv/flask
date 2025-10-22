"""
主视图文件 - 重构后的精简版本
"""

from flask import render_template, request, url_for, flash, redirect, abort, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta

from app import db
from app.models import Post, Permission, User, Role, Thought, Mood
from app.services.permission_service import check_admin_permission
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, FileUploadForm

# 导入拆分的视图模块
from .thought_views import *
from .post_views import *
from .mood_views import *

# 导入表单
from .forms import ThoughtForm


# 主页
@main.route('/', methods=['GET', 'POST'])
def index():
    """主页"""
    # 处理快速创建想法的POST请求
    if request.method == 'POST' and current_user.is_authenticated:
        form = ThoughtForm()
        if form.validate_on_submit():
            # 确保快速创建的想法是公开的
            is_public = form.is_public.data
            if is_public is None:
                is_public = True

            thought = Thought(
                content=form.content.data,
                author=current_user._get_current_object(),
                tags=form.tags.data,
                thought_type=form.thought_type.data,
                source_url=form.source_url.data,
                is_public=is_public
            )
            db.session.add(thought)
            db.session.commit()
            flash('想法已记录！')
            return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False)
    posts = pagination.items

    # 获取最新的想法（最多10个）
    recent_thoughts = Thought.query.filter_by(is_deleted=False, is_public=True)\
        .order_by(Thought.timestamp.desc())\
        .limit(10).all()

    # 获取当月心情日历数据
    mood_calendar_data = None
    if current_user.is_authenticated:
        now = datetime.now()
        year = now.year
        month = now.month

        # 获取当月第一天和最后一天
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        # 获取当月所有心情记录
        moods = Mood.query.filter_by(author_id=current_user.id)\
            .filter(Mood.date >= start_date, Mood.date <= end_date)\
            .order_by(Mood.date.desc())\
            .all()

        # 构建日历数据 - 支持同一天多次记录
        calendar_data = {}
        for mood in moods:
            day = mood.date.day
            if day not in calendar_data:
                calendar_data[day] = []
            calendar_data[day].append(mood)

        # 为每天添加智能分析
        from .mood_views import calculate_primary_mood
        for day, day_moods in calendar_data.items():
            primary_mood = calculate_primary_mood(day_moods)
            calendar_data[day] = {
                'moods': [{
                    'id': m.id,
                    'mood_type': m.mood_type,
                    'custom_mood': m.custom_mood,
                    'intensity': m.intensity,
                    'diary': m.diary,
                    'date': m.date.isoformat() if m.date else None,
                    'timestamp': m.timestamp.isoformat() if m.timestamp else None
                } for m in day_moods],
                'primary_mood': {
                    'id': primary_mood.id,
                    'mood_type': primary_mood.mood_type,
                    'custom_mood': primary_mood.custom_mood,
                    'intensity': primary_mood.intensity,
                    'date': primary_mood.date.isoformat() if primary_mood.date else None,
                    'timestamp': primary_mood.timestamp.isoformat() if primary_mood.timestamp else None
                } if primary_mood else None,
                'count': len(day_moods),
                'avg_intensity': sum(m.intensity for m in day_moods) / len(day_moods)
            }

        # 预计算日期信息（避免模板中调用date函数）
        days_info = []
        for day in range(1, 32):
            try:
                day_of_week = (date(year, month, day).weekday() + 1) % 7
                days_info.append({
                    'day': day,
                    'day_of_week': day_of_week,
                    'valid': True
                })
            except ValueError:
                # 无效日期（如2月30日）
                days_info.append({
                    'day': day,
                    'day_of_week': 0,
                    'valid': False
                })

        # 计算当月天数
        if month in [1,3,5,7,8,10,12]:
            days_in_month = 31
        elif month in [4,6,9,11]:
            days_in_month = 30
        else:
            if year % 400 == 0 or (year % 100 != 0 and year % 4 == 0):
                days_in_month = 29
            else:
                days_in_month = 28

        mood_calendar_data = {
            'year': year,
            'month': month,
            'calendar_data': calendar_data,
            'days_info': days_info,
            'days_in_month': days_in_month
        }

    return render_template('index.html', posts=posts,
                           pagination=pagination, recent_thoughts=recent_thoughts,
                           mood_calendar_data=mood_calendar_data, Mood=Mood,
                           quick_form=ThoughtForm())


# 用户信息
@main.route('/user/<username>')
def user(username):
    """用户页面"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


# 修改个人信息
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """修改个人信息"""
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('个人信息已更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


# 修改用户信息（Admin)
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    """修改用户信息（管理员）"""
    from app.services import require_admin
    require_admin()

    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('用户信息已更新')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


# 上传页面
@main.route('/upload', methods=['GET', 'POST'])
@login_required
def handle_upload():
    """文件上传页面"""
    form = FileUploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.upload.data.filename)
        form.upload.data.save('uploads/images/' + filename)
        flash('www.sadscv.com/images/'+filename)
    else:
        filename = None
    return render_template('upload.html', form=form, filename=filename)


# API端点
@main.route('/api/posts')
def api_posts():
    """获取文章列表API"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
        posts = pagination.items

        # 转换为JSON格式
        posts_data = []
        for post in posts:
            post_data = {
                'id': post.id,
                'title': post.title,
                'body': post.body,
                'body_html': post.body_html,
                'timestamp': post.timestamp.isoformat() if post.timestamp else None,
                'edit_date': post.edit_date.isoformat() if post.edit_date else None,
                'author': {
                    'id': post.author.id,
                    'username': post.author.username
                } if post.author else None,
                'views': post.views or 0,
                'comments_count': post.comments.count() if post.comments else 0,
                'author_id': post.author_id
            }
            posts_data.append(post_data)

        return jsonify({
            'success': True,
            'posts': posts_data,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/posts/<int:post_id>')
def api_post_detail(post_id):
    """获取文章详情API"""
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        # 增加阅读数
        post.views = (post.views or 0) + 1
        db.session.commit()

        # 转换为JSON格式
        post_data = {
            'id': post.id,
            'title': post.title,
            'body': post.body,
            'body_html': post.body_html,
            'timestamp': post.timestamp.isoformat() if post.timestamp else None,
            'edit_date': post.edit_date.isoformat() if post.edit_date else None,
            'author': {
                'id': post.author.id,
                'username': post.author.username,
                'name': post.author.name,
                'email': post.author.email
            } if post.author else None,
            'views': post.views or 0,
            'comments_count': post.comments.count() if post.comments else 0,
            'author_id': post.author_id
        }

        return jsonify({
            'success': True,
            'post': post_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/posts/<int:post_id>', methods=['PUT'])
def api_update_post(post_id):
    """更新文章API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        # 查找文章
        post = Post.query.get(post_id)
        if not post:
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        # 检查权限 - 只有作者可以编辑自己的文章
        if post.author_id != user.id and not user.is_administrator():
            return jsonify({
                'success': False,
                'message': '没有权限编辑这个文章'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400

        # 更新文章字段
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({
                    'success': False,
                    'message': '标题不能为空'
                }), 400
            post.title = title

        if 'body' in data:
            body = data['body'].strip()
            if not body:
                return jsonify({
                    'success': False,
                    'message': '内容不能为空'
                }), 400
            post.body = body

        # 更新编辑时间
        from datetime import datetime
        post.edit_date = datetime.utcnow()

        db.session.commit()

        # 转换为JSON格式
        post_data = {
            'id': post.id,
            'title': post.title,
            'body': post.body,
            'body_html': post.body_html,
            'timestamp': post.timestamp.isoformat() if post.timestamp else None,
            'edit_date': post.edit_date.isoformat() if post.edit_date else None,
            'author': {
                'id': post.author.id,
                'username': post.author.username,
                'name': post.author.name,
                'email': post.author.email
            } if post.author else None,
            'views': post.views or 0,
            'comments_count': post.comments.count() if post.comments else 0,
            'author_id': post.author_id
        }

        return jsonify({
            'success': True,
            'post': post_data,
            'message': '文章更新成功'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/posts/<int:post_id>', methods=['DELETE'])
def api_delete_post(post_id):
    """删除文章API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        # 查找文章
        post = Post.query.get(post_id)
        if not post:
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        # 检查权限 - 只有作者可以删除自己的文章
        if post.author_id != user.id and not user.is_administrator():
            return jsonify({
                'success': False,
                'message': '没有权限删除这个文章'
            }), 403

        # 删除文章
        db.session.delete(post)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '文章已删除'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/posts', methods=['POST'])
def api_create_post():
    """创建文章API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400

        title = data.get('title', '').strip()
        body = data.get('body', '').strip()

        if not title:
            return jsonify({
                'success': False,
                'message': '标题不能为空'
            }), 400

        if not body:
            return jsonify({
                'success': False,
                'message': '内容不能为空'
            }), 400

        # 创建新文章
        post = Post(
            title=title,
            body=body,
            author=user
        )

        db.session.add(post)
        db.session.commit()

        # 转换为JSON格式
        post_data = {
            'id': post.id,
            'title': post.title,
            'body': post.body,
            'body_html': post.body_html,
            'timestamp': post.timestamp.isoformat() if post.timestamp else None,
            'edit_date': post.edit_date.isoformat() if post.edit_date else None,
            'author': {
                'id': post.author.id,
                'username': post.author.username,
                'name': post.author.name,
                'email': post.author.email
            } if post.author else None,
            'views': post.views or 0,
            'comments_count': post.comments.count() if post.comments else 0,
            'author_id': post.author_id
        }

        return jsonify({
            'success': True,
            'post': post_data,
            'message': '文章创建成功'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/thoughts')
def api_thoughts():
    """获取想法列表API"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        limit = request.args.get('limit', None, type=int)

        if limit:
            # 如果指定了limit参数，使用原来的逻辑（用于首页侧边栏）
            thoughts = Thought.query.filter_by(is_deleted=False, is_public=True)\
                .order_by(Thought.timestamp.desc())\
                .limit(limit).all()

            # 不返回分页信息
            pagination_data = None
        else:
            # 使用分页
            pagination = Thought.query.filter_by(is_deleted=False, is_public=True)\
                .order_by(Thought.timestamp.desc())\
                .paginate(page=page, per_page=per_page, error_out=False)
            thoughts = pagination.items

            # 构建分页信息
            pagination_data = {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num
            }

        # 转换为JSON格式
        thoughts_data = []
        for thought in thoughts:
            thought_data = {
                'id': thought.id,
                'content': thought.content,
                'content_html': thought.content_html,
                'type': thought.thought_type,
                'tags': thought.tags,
                'timestamp': thought.timestamp.isoformat() if thought.timestamp else None,
                'is_public': thought.is_public,
                'author': {
                    'id': thought.author.id,
                    'username': thought.author.username
                } if thought.author else None
            }
            thoughts_data.append(thought_data)

        response_data = {
            'success': True,
            'thoughts': thoughts_data
        }

        # 只有在使用分页时才添加pagination字段
        if pagination_data:
            response_data['pagination'] = pagination_data

        return jsonify(response_data)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/thoughts', methods=['POST'])
def api_create_thought():
    """创建想法API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '认证失败，请重新登录'
            }), 401

        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'message': '缺少内容字段'
            }), 400

        content = data['content'].strip()
        if not content:
            return jsonify({
                'success': False,
                'message': '内容不能为空'
            }), 400

        if len(content) > 500:
            return jsonify({
                'success': False,
                'message': '内容不能超过500个字符'
            }), 400

        # 处理is_public字段的类型转换
        is_public_raw = data.get('is_public', True)
        if isinstance(is_public_raw, str):
            # 处理前端发送的字符串值
            is_public = is_public_raw.lower() in ['true', 'y', 'yes', '1']
        else:
            # 处理布尔值或其他类型
            is_public = bool(is_public_raw)

        thought = Thought(
            content=content,
            author=user,
            tags=data.get('tags', ''),
            thought_type=data.get('thought_type', 'note'),
            source_url=data.get('source_url', ''),
            is_public=is_public
        )
        db.session.add(thought)
        db.session.commit()

        # 转换为JSON格式
        thought_data = {
            'id': thought.id,
            'content': thought.content,
            'content_html': thought.content_html,
            'type': thought.thought_type,
            'tags': thought.tags,
            'timestamp': thought.timestamp.isoformat() if thought.timestamp else None,
            'is_public': thought.is_public,
            'author': {
                'id': thought.author.id,
                'username': thought.author.username
            }
        }

        return jsonify({
            'success': True,
            'thought': thought_data,
            'message': '想法创建成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/thoughts/<int:thought_id>', methods=['DELETE'])
def api_delete_thought(thought_id):
    """删除想法API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        # 查找想法
        thought = Thought.query.get(thought_id)
        if not thought:
            return jsonify({
                'success': False,
                'message': '想法不存在'
            }), 404

        # 检查权限 - 只有作者可以删除自己的想法
        if thought.author_id != user.id and not user.is_administrator():
            return jsonify({
                'success': False,
                'message': '没有权限删除这个想法'
            }), 403

        # 软删除想法
        thought.is_deleted = True
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '想法已删除'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/moods')
def api_moods():
    """获取心情列表API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        limit = request.args.get('limit', None, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 构建查询
        query = Mood.query.filter_by(author_id=user.id)

        # 日期范围过滤
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Mood.date >= start_date_obj)
            except ValueError:
                pass

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Mood.date <= end_date_obj)
            except ValueError:
                pass

        # 排序
        query = query.order_by(Mood.date.desc(), Mood.timestamp.desc())

        if limit:
            # 如果指定了limit参数，使用limit
            moods = query.limit(limit).all()
            pagination_data = None
        else:
            # 使用分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            moods = pagination.items

            # 构建分页信息
            pagination_data = {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num
            }

        # 转换为JSON格式
        moods_data = []
        for mood in moods:
            mood_data = {
                'id': mood.id,
                'mood_type': mood.mood_type,
                'custom_mood': mood.custom_mood,
                'diary': mood.diary,
                'intensity': mood.intensity,
                'date': mood.date.isoformat() if mood.date else None,
                'timestamp': mood.timestamp.isoformat() if mood.timestamp else None,
                'author': {
                    'id': mood.author.id,
                    'username': mood.author.username
                } if mood.author else None
            }
            moods_data.append(mood_data)

        response_data = {
            'success': True,
            'moods': moods_data
        }

        # 只有在使用分页时才添加pagination字段
        if pagination_data:
            response_data['pagination'] = pagination_data

        return jsonify(response_data)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/moods/today')
def api_today_mood():
    """获取今日心情API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        # 获取今日日期
        today = date.today()

        # 查询今日心情
        today_mood = Mood.query.filter_by(
            author_id=user.id,
            date=today
        ).order_by(Mood.timestamp.desc()).first()

        if today_mood:
            mood_data = {
                'id': today_mood.id,
                'mood_type': today_mood.mood_type,
                'custom_mood': today_mood.custom_mood,
                'diary': today_mood.diary,
                'intensity': today_mood.intensity,
                'date': today_mood.date.isoformat() if today_mood.date else None,
                'timestamp': today_mood.timestamp.isoformat() if today_mood.timestamp else None
            }
        else:
            mood_data = None

        return jsonify({
            'success': True,
            'mood': mood_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/moods', methods=['POST'])
def api_create_mood():
    """创建心情记录API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400

        mood_type = data.get('mood_type')
        if not mood_type:
            return jsonify({
                'success': False,
                'message': '心情类型不能为空'
            }), 400

        intensity = data.get('intensity', 5)
        if intensity < 1 or intensity > 10:
            return jsonify({
                'success': False,
                'message': '强度必须在1-10之间'
            }), 400

        # 获取或创建今日日期
        today = date.today()

        # 创建心情记录
        mood = Mood(
            mood_type=mood_type,
            custom_mood=data.get('custom_mood', ''),
            diary=data.get('diary', ''),
            intensity=intensity,
            date=today,
            author=user
        )

        db.session.add(mood)
        db.session.commit()

        # 转换为JSON格式
        mood_data = {
            'id': mood.id,
            'mood_type': mood.mood_type,
            'custom_mood': mood.custom_mood,
            'diary': mood.diary,
            'intensity': mood.intensity,
            'date': mood.date.isoformat() if mood.date else None,
            'timestamp': mood.timestamp.isoformat() if mood.timestamp else None,
            'author': {
                'id': mood.author.id,
                'username': mood.author.username
            } if mood.author else None
        }

        return jsonify({
            'success': True,
            'mood': mood_data,
            'message': '心情记录已保存'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/moods/<int:mood_id>', methods=['PUT'])
def api_update_mood(mood_id):
    """更新心情记录API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        # 查找心情记录
        mood = Mood.query.get(mood_id)
        if not mood:
            return jsonify({
                'success': False,
                'message': '心情记录不存在'
            }), 404

        # 检查权限
        if mood.author_id != user.id and not user.is_administrator():
            return jsonify({
                'success': False,
                'message': '没有权限修改这个心情记录'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400

        # 更新字段
        if 'mood_type' in data:
            mood.mood_type = data['mood_type']

        if 'custom_mood' in data:
            mood.custom_mood = data['custom_mood']

        if 'diary' in data:
            mood.diary = data['diary']

        if 'intensity' in data:
            intensity = data['intensity']
            if intensity < 1 or intensity > 10:
                return jsonify({
                    'success': False,
                    'message': '强度必须在1-10之间'
                }), 400
            mood.intensity = intensity

        db.session.commit()

        # 转换为JSON格式
        mood_data = {
            'id': mood.id,
            'mood_type': mood.mood_type,
            'custom_mood': mood.custom_mood,
            'diary': mood.diary,
            'intensity': mood.intensity,
            'date': mood.date.isoformat() if mood.date else None,
            'timestamp': mood.timestamp.isoformat() if mood.timestamp else None,
            'author': {
                'id': mood.author.id,
                'username': mood.author.username
            } if mood.author else None
        }

        return jsonify({
            'success': True,
            'mood': mood_data,
            'message': '心情记录已更新'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/moods/<int:mood_id>', methods=['DELETE'])
def api_delete_mood(mood_id):
    """删除心情记录API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        # 查找心情记录
        mood = Mood.query.get(mood_id)
        if not mood:
            return jsonify({
                'success': False,
                'message': '心情记录不存在'
            }), 404

        # 检查权限
        if mood.author_id != user.id and not user.is_administrator():
            return jsonify({
                'success': False,
                'message': '没有权限删除这个心情记录'
            }), 403

        # 删除心情记录
        db.session.delete(mood)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '心情记录已删除'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/moods/stats')
def api_mood_stats():
    """获取心情统计API"""
    try:
        # 验证认证状态
        from app.services.token_service import verify_token_from_request
        user = verify_token_from_request()

        if not user:
            return jsonify({
                'success': False,
                'message': '无效的认证令牌'
            }), 401

        # 获取查询参数
        days = request.args.get('days', 30, type=int)
        period = request.args.get('period', 'week')

        # 使用现有的Mood.get_mood_stats方法
        stats = Mood.get_mood_stats(user.id, days)

        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    """用户登录API - 安全版本"""
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': '邮箱和密码不能为空'
            }), 400

        user = User.query.filter_by(email=data['email']).first()

        if not user:
            return jsonify({
                'success': False,
                'message': '邮箱或密码错误'
            }), 401

        # 安全的密码验证
        is_valid = user.verify_password(data['password'])

        if is_valid:
            # 使用安全的JWT令牌
            from app.services.token_service import TokenService
            token = TokenService.generate_token(user)

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
            return jsonify({
                'success': False,
                'message': '邮箱或密码错误'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    """用户注册API"""
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password') or not data.get('username'):
            return jsonify({
                'success': False,
                'message': '用户名、邮箱和密码不能为空'
            }), 400

        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': '该邮箱已被注册'
            }), 400

        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': '该用户名已被使用'
            }), 400

        # 创建新用户
        user = User(
            email=data['email'],
            username=data['username']
        )
        user.password = data['password']  # 确保调用password setter

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '注册成功，请登录'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/auth/me', methods=['GET'])
def api_auth_me():
    """获取当前用户信息API - 安全版本"""
    try:
        from app.services.token_service import TokenService

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '缺少认证令牌'
            }), 401

        token = auth_header.split(' ')[1]

        # 尝试使用安全令牌验证
        user = TokenService.verify_token(token)
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'name': user.name,
                    'location': user.location,
                    'about_me': user.about_me,
                    'role': user.role.name if user.role else 'user'
                }
            })

        # 检查是否为旧版令牌并提供迁移支持（仅用于过渡期）
        from app.services.token_service import LegacyTokenMigrator
        migrated_user = None
        if LegacyTokenMigrator.is_legacy_token(token):
            new_token = LegacyTokenMigrator.migrate_legacy_token(token)
            if new_token:
                migrated_user = TokenService.verify_token(new_token)
                # 返回新令牌以供后续使用
                if migrated_user:
                    return jsonify({
                        'success': True,
                        'user': {
                            'id': migrated_user.id,
                            'username': migrated_user.username,
                            'email': migrated_user.email,
                            'name': migrated_user.name,
                            'location': migrated_user.location,
                            'about_me': migrated_user.about_me,
                            'role': migrated_user.role.name if migrated_user.role else 'user'
                        },
                        'new_token': new_token,  # 提示客户端更新令牌
                        'message': '令牌已更新为安全版本，请保存新令牌'
                    })

        return jsonify({
            'success': False,
            'message': '无效或已过期的认证令牌'
        }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/debug/users', methods=['GET'])
def debug_users():
    """调试端点 - 查看所有用户"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'has_password_hash': bool(user.password_hash),
                    'role_id': user.role_id,
                    'role_name': user.role.name if user.role else None
                } for user in users
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@main.route('/api/debug/test-password', methods=['POST'])
def debug_password():
    """调试端点 - 测试密码验证"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'message': f'用户不存在: {email}'
            })

        # 测试密码验证
        is_valid = user.verify_password(password)

        # 重新哈希并测试
        from werkzeug.security import generate_password_hash, check_password_hash
        test_hash = generate_password_hash(password)
        test_valid = check_password_hash(test_hash, password)

        return jsonify({
            'success': True,
            'email': email,
            'user_id': user.id,
            'username': user.username,
            'password_valid': is_valid,
            'has_password_hash': bool(user.password_hash),
            'password_hash_length': len(user.password_hash) if user.password_hash else 0,
            'original_hash_start': user.password_hash[:20] if user.password_hash else None,
            'test_hash_start': test_hash[:20],
            'test_hash_valid': test_valid
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'error_type': type(e).__name__
        }), 500


@main.route('/api/debug/reset-password', methods=['POST'])
def debug_reset_password():
    """调试端点 - 重置用户密码"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'message': f'用户不存在: {email}'
            })

        # 重新设置密码
        old_hash = user.password_hash
        user.password = password
        new_hash = user.password_hash
        db.session.commit()
        db.session.refresh(user)  # 刷新对象

        # 测试新密码
        is_valid = user.verify_password(password)

        # 手动测试
        from werkzeug.security import check_password_hash
        manual_test = check_password_hash(new_hash, password)

        return jsonify({
            'success': True,
            'message': f'密码已重置，验证结果: {is_valid}',
            'email': email,
            'user_id': user.id,
            'old_hash_length': len(old_hash) if old_hash else 0,
            'new_hash_length': len(new_hash) if new_hash else 0,
            'password_valid': is_valid,
            'manual_test': manual_test,
            'hash_changed': old_hash != new_hash
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e),
            'error_type': type(e).__name__
        }), 500


