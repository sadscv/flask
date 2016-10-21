from flask import g, jsonify
from flask import request
from flask import url_for

from app import db
from app.api_1_0 import api
from app.api_1_0.decorators import permission_required
from app.api_1_0.errors import forbidden
from app.models import Post, Permission


@api.route('/posts/')
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts':[post.to_json() for post in posts]})

@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
        not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficent permission')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())

@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
           {'Location':url_for('api.get_post', id=post.id, _external=True)}
