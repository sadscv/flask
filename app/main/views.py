from flask import abort
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta

from app import db
from app.decorator import admin_required
from app.models import Post, Permission, User, Role, Thought, Mood, Comment
from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm, \
                    FileUploadForm, ThoughtForm, MoodForm, MoodSearchForm, CommentForm


#主页
@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASK_POST_PER_PAGE'],
        error_out=False)
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



#用户信息
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


#文章地址
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        # 创建新评论
        comment = Comment(
            body=form.body.data,
            author_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('评论发表成功！', 'success')
        return redirect(url_for('.post', id=post.id))

    # 获取评论列表
    comments = Comment.query.filter_by(post_id=post.id, disabled=False)\
                          .order_by(Comment.timestamp.asc()).all()

    # 增加阅读数
    post.views = (post.views or 0) + 1
    db.session.commit()

    return render_template('post.html', posts=[post], form=form, comments=comments)


#创建文章
@main.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.content.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    return render_template('create_post.html', form=form)


#编辑文章内容
@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.content.data
        post.title = form.title.data
        post.edit_date = dt.utcnow()
        db.session.add(post)
        flash('post has been updated')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.content.data = post.body
    return render_template('edit_post.html', form=form, post=post)

#删除文章
@main.route('/delete_post/<int:id>', methods=['GET'])
@login_required
@admin_required
def delete_post(id):
    if not current_user.can(Permission.ADMIN):
        abort(403)
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    flash('post deleted')
    return redirect(url_for('.index'))



#修改个人信息
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

#修改用户信息（Admin)
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
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
        flash('profile has already been updated')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)




#想法记录页面
@main.route('/thoughts', methods=['GET', 'POST'])
@login_required
def thoughts():
    form = ThoughtForm()
    if form.validate_on_submit():
        thought = Thought(
            content=form.content.data,
            author=current_user._get_current_object(),
            tags=form.tags.data,
            thought_type=form.thought_type.data,
            source_url=form.source_url.data,
            is_public=form.is_public.data
        )
        db.session.add(thought)
        db.session.commit()
        flash('想法已记录！')
        return redirect(url_for('.thoughts'))

    # 分页显示想法
    page = request.args.get('page', 1, type=int)
    pagination = Thought.query.filter_by(is_deleted=False)\
        .filter_by(is_public=True)\
        .order_by(Thought.timestamp.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    thoughts = pagination.items
    return render_template('thoughts.html', form=form,
                         thoughts=thoughts, pagination=pagination)


#删除想法（软删除）
@main.route('/thought/<int:id>/delete', methods=['POST'])
@login_required
def delete_thought(id):
    thought = Thought.query.get_or_404(id)
    if thought.author != current_user:
        abort(403)
    thought.is_deleted = True
    db.session.add(thought)
    db.session.commit()
    flash('想法已删除')
    return redirect(url_for('.thoughts'))


#按标签筛选想法
@main.route('/thoughts/tag/<tag>')
def thoughts_by_tag(tag):
    page = request.args.get('page', 1, type=int)
    pagination = Thought.query.filter(Thought.tags.contains(tag))\
        .filter_by(is_deleted=False, is_public=True)\
        .order_by(Thought.timestamp.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    thoughts = pagination.items
    return render_template('thoughts_tag.html', thoughts=thoughts,
                         tag=tag, pagination=pagination)


#搜索想法
@main.route('/thoughts/search')
def search_thoughts():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('.thoughts'))

    page = request.args.get('page', 1, type=int)
    pagination = Thought.query.filter(Thought.content.contains(query))\
        .filter_by(is_deleted=False, is_public=True)\
        .order_by(Thought.timestamp.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    thoughts = pagination.items
    return render_template('thoughts_search.html', thoughts=thoughts,
                         query=query, pagination=pagination)


#上传页面
@login_required
@main.route('/upload', methods=['GET', 'POST'])
def handle_upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.upload.data.filename)
        form.upload.data.save('uploads/images/' + filename)
        flash('www.sadscv.com/images/'+filename)
    else:
        filename = None
    return render_template('upload.html', form=form, filename=filename)


#心情记录主页
@main.route('/mood', methods=['GET', 'POST'])
@login_required
def mood_index():
    """心情记录主页"""
    form = MoodForm()
    today = date.today()

    # 检查今天是否已经记录过心情
    today_mood = Mood.query.filter_by(
        author_id=current_user.id,
        date=today
    ).first()

    if form.validate_on_submit():
        # 如果今天已有记录，更新它
        if today_mood:
            today_mood.mood_type = form.mood_type.data
            today_mood.custom_mood = form.custom_mood.data if form.mood_type.data == 'custom' else None
            today_mood.intensity = form.intensity.data
            today_mood.diary = form.diary.data
            today_mood.timestamp = datetime.utcnow()
        else:
            # 创建新的心情记录
            mood = Mood(
                mood_type=form.mood_type.data,
                custom_mood=form.custom_mood.data if form.mood_type.data == 'custom' else None,
                intensity=form.intensity.data,
                diary=form.diary.data,
                date=today,
                author_id=current_user.id
            )
            db.session.add(mood)

        db.session.commit()
        flash('心情记录成功！', 'success')
        return redirect(url_for('.mood_history'))

    # 如果有今天的记录，填充表单
    if today_mood:
        form.mood_type.data = today_mood.mood_type
        form.custom_mood.data = today_mood.custom_mood
        form.intensity.data = today_mood.intensity
        form.diary.data = today_mood.diary

    # 获取最近7天的心情记录用于统计
    week_stats = Mood.get_mood_stats(current_user.id, days=7)

    return render_template('mood/index.html',
                         form=form,
                         today_mood=today_mood,
                         week_stats=week_stats,
                         Mood=Mood)


#心情历史记录
@main.route('/mood/history')
@login_required
def mood_history():
    """心情历史记录页面"""
    page = request.args.get('page', 1, type=int)
    search_form = MoodSearchForm()

    # 构建查询
    query = Mood.query.filter_by(author_id=current_user.id)

    # 处理搜索参数
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        query = query.filter(Mood.date >= start_date)

    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        query = query.filter(Mood.date <= end_date)

    if request.args.get('mood_type'):
        query = query.filter_by(mood_type=request.args.get('mood_type'))

    # 分页查询
    pagination = query.order_by(Mood.date.desc()).paginate(
        page=page, per_page=30, error_out=False
    )
    moods = pagination.items

    # 获取统计信息
    month_stats = Mood.get_mood_stats(current_user.id, days=30)

    return render_template('mood/history.html',
                         moods=moods,
                         pagination=pagination,
                         search_form=search_form,
                         month_stats=month_stats,
                         Mood=Mood)


#心情日历视图
@main.route('/mood/calendar')
@login_required
def mood_calendar():
    """心情日历视图"""
    # 获取当前年月
    now = datetime.now()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)

    # 获取该月所有心情记录
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    moods = Mood.query.filter_by(author_id=current_user.id)\
        .filter(Mood.date >= start_date, Mood.date <= end_date)\
        .order_by(Mood.date.desc())\
        .all()

    # 构建日历数据
    calendar_data = {}
    for mood in moods:
        calendar_data[mood.date.day] = mood

    return render_template('mood/calendar.html',
                         year=year,
                         month=month,
                         calendar_data=calendar_data,
                         Mood=Mood,
                         date=date)


#查看特定日期的心情
@main.route('/mood/date/<date_str>')
@login_required
def mood_by_date(date_str):
    """查看特定日期的心情记录"""
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('无效的日期格式', 'error')
        return redirect(url_for('.mood_history'))

    mood = Mood.query.filter_by(
        author_id=current_user.id,
        date=target_date
    ).first()

    if not mood:
        flash(f'{date_str} 没有心情记录', 'info')
        return redirect(url_for('.mood_history'))

    # 计算相邻日期
    prev_date = mood.date - timedelta(days=1)
    next_date = mood.date + timedelta(days=1)

    return render_template('mood/detail.html', mood=mood, Mood=Mood,
                         prev_date=prev_date, next_date=next_date)


#删除心情记录
@main.route('/mood/<int:id>/delete', methods=['POST'])
@login_required
def delete_mood(id):
    """删除心情记录"""
    mood = Mood.query.get_or_404(id)
    if mood.author != current_user:
        abort(403)

    db.session.delete(mood)
    db.session.commit()
    flash('心情记录已删除', 'success')
    return redirect(url_for('.mood_history'))
