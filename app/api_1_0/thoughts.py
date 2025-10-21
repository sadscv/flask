"""
想法相关的API端点
"""

from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Thought, User
from . import api
from .decorators import permission_required
from app.models import Permission


@api.route('/thoughts', methods=['GET'])
def get_thoughts():
    """获取想法列表"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    query = Thought.query.filter_by(is_deleted=False)

    # 根据用户筛选
    author = request.args.get('author')
    if author:
        query = query.join(Thought.author).filter(User.username == author)

    # 根据类型筛选
    thought_type = request.args.get('type')
    if thought_type:
        query = query.filter_by(thought_type=thought_type)

    # 根据标签筛选
    tag = request.args.get('tag')
    if tag:
        query = query.filter(Thought.tags.contains(tag))

    # 筛选公开状态
    show_private = request.args.get('show_private', 'false').lower() == 'true'
    if not current_user.is_authenticated or not show_private:
        query = query.filter_by(is_public=True)
    elif current_user.is_authenticated:
        # 显示用户自己的私有想法和所有公开想法
        query = query.filter((Thought.is_public == True) |
                           (Thought.author_id == current_user.id))

    # 排序
    sort_by = request.args.get('sort', 'latest')
    if sort_by == 'oldest':
        query = query.order_by(Thought.timestamp.asc())
    else:  # latest
        query = query.order_by(Thought.timestamp.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    thoughts = []
    for thought in pagination.items:
        thoughts.append({
            'id': thought.id,
            'content': thought.content,
            'thought_type': thought.thought_type,
            'tags': thought.tags,
            'timestamp': thought.timestamp.isoformat(),
            'is_public': thought.is_public,
            'author': thought.author.username if thought.author else 'Anonymous',
            'content_html': thought.content_html
        })

    return jsonify({
        'success': True,
        'thoughts': thoughts,
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


@api.route('/thoughts/<int:id>', methods=['GET'])
def get_thought(id):
    """获取单条想法"""
    thought = Thought.query.get_or_404(id)

    # 检查权限：私有想法只有作者可以查看
    if not thought.is_public and (not current_user.is_authenticated or
                                thought.author_id != current_user.id):
        return jsonify({'success': False, 'message': '无权查看此想法'}), 403

    return jsonify({
        'success': True,
        'thought': {
            'id': thought.id,
            'content': thought.content,
            'thought_type': thought.thought_type,
            'tags': thought.tags,
            'timestamp': thought.timestamp.isoformat(),
            'is_public': thought.is_public,
            'author': thought.author.username if thought.author else 'Anonymous',
            'content_html': thought.content_html,
            'source_url': thought.source_url
        }
    })


@api.route('/thoughts', methods=['POST'])
@login_required
@permission_required(Permission.WRITE_THOUGHTS)
def create_thought():
    """创建想法"""
    data = request.get_json() or {}

    # 验证必填字段
    if not data.get('content'):
        return jsonify({'success': False, 'message': '内容不能为空'}), 400

    thought = Thought(
        content=data['content'],
        author=current_user._get_current_object(),
        thought_type=data.get('thought_type', 'note'),
        tags=data.get('tags', ''),
        source_url=data.get('source_url', ''),
        is_public=data.get('is_public', True)
    )

    db.session.add(thought)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '想法创建成功',
        'thought': {
            'id': thought.id,
            'content': thought.content,
            'thought_type': thought.thought_type,
            'tags': thought.tags,
            'timestamp': thought.timestamp.isoformat(),
            'is_public': thought.is_public,
            'author': thought.author.username,
            'content_html': thought.content_html
        }
    }), 201


@api.route('/thoughts/<int:id>', methods=['PUT'])
@login_required
def update_thought(id):
    """更新想法"""
    thought = Thought.query.get_or_404(id)

    # 检查权限
    if thought.author_id != current_user.id:
        return jsonify({'success': False, 'message': '无权编辑此想法'}), 403

    data = request.get_json() or {}

    if 'content' in data:
        thought.content = data['content']
    if 'thought_type' in data:
        thought.thought_type = data['thought_type']
    if 'tags' in data:
        thought.tags = data['tags']
    if 'source_url' in data:
        thought.source_url = data['source_url']
    if 'is_public' in data:
        thought.is_public = data['is_public']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '想法更新成功',
        'thought': {
            'id': thought.id,
            'content': thought.content,
            'thought_type': thought.thought_type,
            'tags': thought.tags,
            'timestamp': thought.timestamp.isoformat(),
            'is_public': thought.is_public,
            'author': thought.author.username,
            'content_html': thought.content_html
        }
    })


@api.route('/thoughts/<int:id>', methods=['DELETE'])
@login_required
def delete_thought(id):
    """删除想法（软删除）"""
    thought = Thought.query.get_or_404(id)

    # 检查权限
    if thought.author_id != current_user.id:
        return jsonify({'success': False, 'message': '无权删除此想法'}), 403

    thought.is_deleted = True
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '想法删除成功'
    })


@api.route('/thoughts/search', methods=['GET'])
def search_thoughts():
    """搜索想法"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'success': False, 'message': '搜索关键词不能为空'}), 400

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # 构建搜索查询
    search_query = Thought.query.filter(
        Thought.content.contains(query),
        Thought.is_deleted == False
    )

    # 筛选公开状态
    if not current_user.is_authenticated:
        search_query = search_query.filter_by(is_public=True)
    else:
        # 显示公开想法和用户自己的私有想法
        search_query = search_query.filter(
            (Thought.is_public == True) | (Thought.author_id == current_user.id)
        )

    # 根据类型筛选
    thought_type = request.args.get('type')
    if thought_type:
        search_query = search_query.filter_by(thought_type=thought_type)

    # 排序
    search_query = search_query.order_by(Thought.timestamp.desc())

    pagination = search_query.paginate(page=page, per_page=per_page, error_out=False)

    thoughts = []
    for thought in pagination.items:
        thoughts.append({
            'id': thought.id,
            'content': thought.content,
            'thought_type': thought.thought_type,
            'tags': thought.tags,
            'timestamp': thought.timestamp.isoformat(),
            'is_public': thought.is_public,
            'author': thought.author.username if thought.author else 'Anonymous',
            'content_html': thought.content_html
        })

    return jsonify({
        'success': True,
        'thoughts': thoughts,
        'query': query,
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


@api.route('/thoughts/tag/<tag>', methods=['GET'])
def get_thoughts_by_tag(tag):
    """根据标签获取想法"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    query = Thought.query.filter(
        Thought.tags.contains(tag),
        Thought.is_deleted == False
    )

    # 筛选公开状态
    if not current_user.is_authenticated:
        query = query.filter_by(is_public=True)
    else:
        query = query.filter(
            (Thought.is_public == True) | (Thought.author_id == current_user.id)
        )

    pagination = query.order_by(Thought.timestamp.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)

    thoughts = []
    for thought in pagination.items:
        thoughts.append({
            'id': thought.id,
            'content': thought.content,
            'thought_type': thought.thought_type,
            'tags': thought.tags,
            'timestamp': thought.timestamp.isoformat(),
            'is_public': thought.is_public,
            'author': thought.author.username if thought.author else 'Anonymous',
            'content_html': thought.content_html
        })

    return jsonify({
        'success': True,
        'thoughts': thoughts,
        'tag': tag,
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


@api.route('/thoughts/user/<username>', methods=['GET'])
def get_user_thoughts(username):
    """获取指定用户的想法"""
    from app.models import User

    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    query = Thought.query.filter_by(author=user, is_deleted=False)

    # 只有用户本人或管理员可以查看私有想法
    if not current_user.is_authenticated or (current_user.username != username and not current_user.can(Permission.ADMIN)):
        query = query.filter_by(is_public=True)

    pagination = query.order_by(Thought.timestamp.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)

    thoughts = []
    for thought in pagination.items:
        thoughts.append({
            'id': thought.id,
            'content': thought.content,
            'thought_type': thought.thought_type,
            'tags': thought.tags,
            'timestamp': thought.timestamp.isoformat(),
            'is_public': thought.is_public,
            'author': thought.author.username,
            'content_html': thought.content_html
        })

    return jsonify({
        'success': True,
        'thoughts': thoughts,
        'username': username,
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


@api.route('/thoughts/<int:id>/toggle-public', methods=['POST'])
@login_required
def toggle_thought_public(id):
    """切换想法的公开状态"""
    thought = Thought.query.get_or_404(id)

    # 检查权限
    if thought.author_id != current_user.id:
        return jsonify({'success': False, 'message': '无权修改此想法'}), 403

    thought.is_public = not thought.is_public
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'想法已设为{"公开" if thought.is_public else "私有"}',
        'is_public': thought.is_public
    })


@api.route('/thoughts/types', methods=['GET'])
def get_thought_types():
    """获取想法类型列表"""
    types = [
        {'value': 'note', 'label': '笔记', 'color': 'blue'},
        {'value': 'quote', 'label': '引用', 'color': 'green'},
        {'value': 'idea', 'label': '想法', 'color': 'purple'},
        {'value': 'task', 'label': '任务', 'color': 'orange'}
    ]

    return jsonify({
        'success': True,
        'types': types
    })


@api.route('/thoughts/tags/popular', methods=['GET'])
def get_popular_tags():
    """获取热门标签"""
    # 这里简化处理，实际项目中可能需要更复杂的统计逻辑
    thoughts = Thought.query.filter_by(is_deleted=False, is_public=True).all()

    tag_count = {}
    for thought in thoughts:
        if thought.tags:
            tags = [tag.strip() for tag in thought.tags.split(',')]
            for tag in tags:
                if tag:
                    tag_count[tag] = tag_count.get(tag, 0) + 1

    # 按使用次数排序并返回前20个
    popular_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:20]

    return jsonify({
        'success': True,
        'tags': [{'tag': tag, 'count': count} for tag, count in popular_tags]
    })