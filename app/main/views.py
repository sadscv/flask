"""
主视图文件 - 重构后的精简版本
"""

from flask import render_template, request, url_for, flash, redirect, abort
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


# 主页
@main.route('/', methods=['GET', 'POST'])
def index():
    """主页"""
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

        # 构建日历数据
        calendar_data = {}
        for mood in moods:
            calendar_data[mood.date.day] = mood

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
                           mood_calendar_data=mood_calendar_data, Mood=Mood)


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