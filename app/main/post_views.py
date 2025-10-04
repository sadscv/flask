"""
文章相关的视图函数
"""

from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.services.permission_service import require_admin
from app.services.auth_service import require_delete_permission
from app.services.ajax_service import ajax_route, is_ajax_request, ajax_success
from app.models import Post, Comment, Permission
from .forms import PostForm, CommentForm
from . import main
from datetime import datetime


@main.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    """创建文章"""
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.content.data,
                    title=form.title.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash('文章已创建')
        return redirect(url_for('.index'))
    return render_template('create_post.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    """文章详情页"""
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


@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    """编辑文章"""
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.content.data
        post.title = form.title.data
        post.edit_date = datetime.utcnow()
        db.session.add(post)
        flash('文章已更新')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.content.data = post.body
    return render_template('edit_post.html', form=form, post=post)


@main.route('/delete_post/<int:id>', methods=['GET'])
@login_required
@require_admin
@ajax_route
def delete_post(id):
    """删除文章"""
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()

    if is_ajax_request():
        return ajax_success('文章已删除')

    flash('文章已删除')
    return redirect(url_for('.index'))