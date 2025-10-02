from flask import abort
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.decorator import admin_required
from app.models import Post, Permission, User, Role, Thought
from . import main
from datetime import datetime as dt
from .forms import PostForm, EditProfileForm, EditProfileAdminForm, \
                    FileUploadForm, ThoughtForm


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

    return render_template('index.html', posts=posts,
                           pagination=pagination, recent_thoughts=recent_thoughts)



#用户信息
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


#文章地址
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return  render_template('post.html', posts=[post])


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
