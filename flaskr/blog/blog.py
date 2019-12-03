from flask import Blueprint, request, jsonify, Response
from werkzeug.exceptions import abort

from flaskr.auth.auth import auth
from flaskr.db import get_db
from flaskr.blog.queries import (create_post, delete_post, get_post, update_post, get_post_list)
from flaskr.auth.queries import get_user_by_username


bp = Blueprint("blog", __name__, url_prefix="/blog/posts")


@bp.route("/", methods=["GET"])
@auth.login_required
def get_posts():
    """Show all the posts, most recent first."""
    posts = get_post_list(get_db())

    if not posts:
        return Response("No posts", 204)

    return jsonify([dict(post) for post in posts])


def check_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = get_post(get_db(), id)
    if post is None:
        abort(404, description=f"Post id {id} doesn't exist.")

    user_id = get_user_by_username(get_db(), auth.username())['id']
    if check_author and post["author_id"] != user_id:
        abort(403)

    return post


@bp.route("/", methods=["POST"])
@auth.login_required
def create():
    """Create a new post for the current user."""
    json = request.get_json()

    if json.get('title') and json.get('body'):
        title, body = json['title'], json['body']
        user_id = get_user_by_username(get_db(), auth.username())['id']
        create_post(get_db(), title, body, user_id)
        return Response("Success: post was created", 200)

    abort(400, description='Error: Title and body is required')


@bp.route("/<int:post_id>/", methods=['PUT'])
@auth.login_required
def update(post_id):
    """Update a post if the current user is the author."""
    check_post(post_id)
    json = request.get_json()

    if json.get('title') and json.get('body'):
        title, body = json['title'], json['body']
        update_post(get_db(), title, body, post_id)
        return Response("Success: post was updated", 200)

    abort(400, description='Error: Title and body is required')


@bp.route("/<int:post_id>/", methods=["DELETE"])
@auth.login_required
def delete(post_id):
    """Delete a post."""
    check_post(post_id)
    delete_post(get_db(), post_id)
    return Response("Success: post was deleted", 200)
