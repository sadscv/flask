"""
心情相关的视图函数
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import db
from app.services.auth_service import require_delete_permission
from app.services.ajax_service import ajax_route, is_ajax_request, ajax_success
from app.models import Mood
from .forms import MoodForm, MoodSearchForm
from . import main


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


@main.route('/mood/<int:id>/delete', methods=['POST'])
@login_required
def delete_mood(id):
    """删除心情记录"""
    from flask import jsonify

    mood = Mood.query.get_or_404(id)

    # 检查删除权限
    require_delete_permission(mood.author)

    db.session.delete(mood)
    db.session.commit()

    # 检查是否为AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': '心情记录已删除'})

    flash('心情记录已删除', 'success')
    return redirect(url_for('.mood_history'))