# This file implements the authentication for the Flask application.

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

# Create the authentication blueprint with a URL prefix
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/v1/auth')

# Remove this shit and use a database
USERS_DB = {
    "testuser": {
        "password_hash": generate_password_hash("supersecret")
    }
}

@auth_bp.route("/login", methods=["POST"])
def login():
    """
        Authenticates the user and returns access and refresh token.
    """
    data = request.get_json()
    username = data.get("username", None)
    password = data.get("password", None)

    user = USERS_DB.get(username)
    if user and check_password_hash(user["password_hash"], password):
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return jsonify(access_token=access_token, refresh_token=refresh_token)
    
    return jsonify({"msg": "Usuário ou senha inválidos"}), 401


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
        Generates a new access token from a valid refresh token.
    """
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token)