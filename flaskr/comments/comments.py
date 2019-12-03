from flask import Blueprint, request, Response, jsonify
from werkzeug.exceptions import abort

from flaskr.auth.auth import auth
from flaskr.db import get_db
from flaskr.auth.queries import get_user_by_username
from flaskr.comments.queries import (get_comment_list, get_comment, create_comment, update_comment, delete_comment)


bp = Blueprint("comments", __name__, url_prefix="/blog/posts")


@bp.route("/<int:post_id>/comments/", methods=["GET"])
@auth.login_required
def get_post_comments(post_id):
    comments = get_comment_list(get_db(), post_id)

    if not comments:
        return Response("No comments", 204)

    return jsonify([dict(comment) for comment in comments])


def check_comment(id, check_author=True):
    comment = get_comment(get_db(), id)
    if comment is None:
        abort(404, description=f"Comment id {id} doesn't exist.")

    user_id = get_user_by_username(get_db(), auth.username())['id']
    if check_author and comment["author_id"] != user_id:
        abort(403)

    return comment


@bp.route("/<int:post_id>/comments/", methods=["POST"])
@auth.login_required
def create(post_id):
    """Create a new comment"""
    json = request.get_json()

    if json.get('text'):
        text = json['text']
        user_id = get_user_by_username(get_db(), auth.username())['id']
        create_comment(get_db(), post_id, user_id, text)
        return Response("Success: comment was created", 200)

    abort(400, description='Error: Text and body is required')


@bp.route("/<int:post_id>/comments/<int:comment_id>/", methods=['PUT'])
@auth.login_required
def update(post_id, comment_id):
    """Update a comment if the current user is the author."""
    check_comment(comment_id)
    json = request.get_json()

    if json.get('text'):
        text = json['text']
        update_comment(get_db(), comment_id, text)
        return Response("Success: comment was updated", 200)

    abort(400, description='Error: Text and body is required')


@bp.route("/<int:post_id>/comments/<int:comment_id>/", methods=["DELETE"])
@auth.login_required
def delete(post_id, comment_id):
    """Delete a comment"""
    check_comment(comment_id)
    delete_comment(get_db(), comment_id)
    return Response("Success: comment was deleted", 200)
