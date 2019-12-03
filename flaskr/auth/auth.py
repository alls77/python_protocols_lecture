from flask import Blueprint, Response, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.auth.queries import (create_user, get_user_by_username)


bp = Blueprint("auth", __name__, url_prefix="/auth")

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = get_user_by_username(get_db(), username)
    if user:
        return check_password_hash(user['password'], password)
    return False


@bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    json = request.get_json()

    if json.get('username') and json.get('password'):
        username, password = json['username'], json['password']

        if get_user_by_username(get_db(), username) is not None:
            abort(409, description=f"User {username} is already registered.")

        create_user(get_db(), username, password)
        return Response("Success: user was registered", 200)

    abort(400, description="Error: Username and Password is required.")
