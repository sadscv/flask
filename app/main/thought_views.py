"""
想法相关的视图函数
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.services.auth_service import require_delete_permission
from app.services.ajax_service import ajax_route, is_ajax_request, ajax_success
from app.models import Thought
from .forms import ThoughtForm
from . import main


@main.route('/thoughts', methods=['GET', 'POST'])
@login_required
def thoughts():
    """想法记录页面"""
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


@main.route('/thought/<int:id>/delete', methods=['POST'])
@login_required
def delete_thought(id):
    """删除想法（软删除）"""
    from flask import jsonify

    thought = Thought.query.get_or_404(id)

    # 检查删除权限
    require_delete_permission(thought.author)

    thought.is_deleted = True
    db.session.add(thought)
    db.session.commit()

    # 检查是否为AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': '想法已删除'})

    flash('想法已删除')
    return redirect(url_for('.thoughts'))


@main.route('/thoughts/tag/<tag>')
def thoughts_by_tag(tag):
    """按标签筛选想法"""
    page = request.args.get('page', 1, type=int)
    pagination = Thought.query.filter(Thought.tags.contains(tag))\
        .filter_by(is_deleted=False, is_public=True)\
        .order_by(Thought.timestamp.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    thoughts = pagination.items
    return render_template('thoughts_tag.html', thoughts=thoughts,
                         tag=tag, pagination=pagination)


@main.route('/thoughts/search')
def search_thoughts():
    """搜索想法"""
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