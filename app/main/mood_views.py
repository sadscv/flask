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


def calculate_primary_mood(moods):
    """
    计算主导心情的智能算法
    权重：时间(40%) + 强度(35%) + 情绪类型(25%)
    """
    if not moods:
        return None

    if len(moods) == 1:
        return moods[0]

    def calculate_mood_score(mood):
        """计算单个心情的权重分数"""
        from datetime import datetime

        # 时间权重：越新的记录权重越高
        now = datetime.utcnow()
        hours_diff = (now - mood.timestamp).total_seconds() / 3600
        time_weight = max(0.1, 1.0 - hours_diff / 24)  # 24小时内的记录有较高权重

        # 强度权重：直接使用强度值
        intensity_weight = mood.intensity / 10.0

        # 情绪类型权重：积极情绪略高
        emotion_weights = {
            'happy': 0.9,    # 开心权重最高
            'calm': 0.8,     # 平静较高
            'anxious': 0.6,  # 焦虑中等
            'sad': 0.4,      # 伤心较低
            'angry': 0.3,    # 愤怒最低
            'custom': 0.7    # 自定义中等偏高
        }
        emotion_weight = emotion_weights.get(mood.mood_type, 0.5)

        # 综合评分
        total_score = (time_weight * 0.4 +
                      intensity_weight * 0.35 +
                      emotion_weight * 0.25)

        return total_score

    # 计算每个心情的评分
    scored_moods = []
    for mood in moods:
        score = calculate_mood_score(mood)
        scored_moods.append((mood, score))

    # 按评分排序，返回最高分的心情
    scored_moods.sort(key=lambda x: x[1], reverse=True)
    return scored_moods[0][0]


@main.route('/mood', methods=['GET', 'POST'])
@login_required
def mood_index():
    """心情记录主页 - 支持每天多次记录"""
    form = MoodForm()
    today = date.today()

    # 获取今天所有的心情记录（支持多次打卡）
    today_moods = Mood.query.filter_by(
        author_id=current_user.id,
        date=today
    ).order_by(Mood.timestamp.desc()).all()

    # 获取最新的心情记录用于表单预设
    latest_mood = today_moods[0] if today_moods else None

    if form.validate_on_submit():
        # 创建新的心情记录（支持多次打卡）
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
        flash('心情记录成功！今天已记录 {} 次心情'.format(len(today_moods) + 1), 'success')
        return redirect(url_for('.mood_history'))

    # 如果有今天的记录，用最新的记录填充表单
    if latest_mood:
        form.mood_type.data = latest_mood.mood_type
        form.custom_mood.data = latest_mood.custom_mood
        form.intensity.data = latest_mood.intensity
        form.diary.data = latest_mood.diary

    # 获取最近7天的心情记录用于统计
    week_stats = Mood.get_mood_stats(current_user.id, days=7)

    return render_template('mood/index.html',
                         form=form,
                         today_moods=today_moods,
                         latest_mood=latest_mood,
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

    # 构建日历数据 - 支持同一天多次记录
    calendar_data = {}
    for mood in moods:
        day = mood.date.day
        if day not in calendar_data:
            calendar_data[day] = []
        calendar_data[day].append(mood)

    # 为每条记录添加智能分析
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

    return render_template('mood/calendar.html',
                         year=year,
                         month=month,
                         calendar_data=calendar_data,
                         Mood=Mood,
                         date=date)


@main.route('/mood/date/<date_str>')
@login_required
def mood_by_date(date_str):
    """查看特定日期的心情记录 - 支持多次记录"""
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('无效的日期格式', 'error')
        return redirect(url_for('.mood_history'))

    # 获取该日期所有的心情记录
    moods = Mood.query.filter_by(
        author_id=current_user.id,
        date=target_date
    ).order_by(Mood.timestamp.desc()).all()

    if not moods:
        flash(f'{date_str} 没有心情记录', 'info')
        return redirect(url_for('.mood_history'))

    # 计算统计信息
    primary_mood = calculate_primary_mood(moods)
    avg_intensity = sum(m.intensity for m in moods) / len(moods)

    # 按时间顺序排列用于时间轴显示
    timeline_moods = sorted(moods, key=lambda x: x.timestamp)

    # 计算相邻日期
    prev_date = target_date - timedelta(days=1)
    next_date = target_date + timedelta(days=1)

    # 如果只有一条记录，使用原有模板
    if len(moods) == 1:
        return render_template('mood/detail.html', mood=moods[0], Mood=Mood,
                             prev_date=prev_date, next_date=next_date)
    else:
        # 多条记录使用新模板
        return render_template('mood/detail_multi.html',
                             moods=moods,
                             primary_mood=primary_mood,
                             timeline_moods=timeline_moods,
                             avg_intensity=avg_intensity,
                             target_date=target_date,
                             Mood=Mood,
                             prev_date=prev_date,
                             next_date=next_date)


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