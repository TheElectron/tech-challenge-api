# This file implements the authentication for the Flask application.

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

# Create the authentication blueprint with a URL prefix
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/v1/auth')

# Remove this shit and use a real database
USERS_DB = {
  "testuser": {
      "password_hash": generate_password_hash("supersecret")
  }
}

@auth_bp.route("/login", methods=["POST"])
def login():
  """
  Authenticates the user and returns access and refresh token.
  Raise an exception if there is an error while authenticating user.
  Returns a message that indicates success on login.
  ---
  tags:
    - Authentication Endpoints
  parameters:
    - name: body
      in: body
      required: true
      schema:
        id: UserLogin
        required:
          - username
          - password
        properties:
          username:
            type: string
            description: Username.
            example: "testuser"
          password:
            type: string
            description: Password.
            example: "supersecret"
  responses:
    200:
      description: Login successful.
      schema:
        type: object
        properties:
          access_token:
            type: string
          refresh_token:
            type: string
    401:
      description: Invalid credentials.
      schema:
        type: object
        properties:
          msg:
            type: string
    500:
      description: Invalid credentials.
      schema:
        type: object
        properties:
          msg:
            type: string
  """
  try:
    data = request.get_json()
    username = data.get("username", None)
    password = data.get("password", None)
    user = USERS_DB.get(username)
    if user and check_password_hash(user["password_hash"], password):
      access_token = create_access_token(identity=username)
      refresh_token = create_refresh_token(identity=username)
      return jsonify(access_token=access_token, refresh_token=refresh_token)
    return jsonify({"msg": "Invalid username or password"}), 401
  except Exception as e:
    print(f"Error while authenticating user: {e}")
    return jsonify({'msg': 'Error while authenticating user.'}), 500

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
  """
  Generates a new access token from a valid refresh token.
  Raise an exception if there is an error while generating a new access token.\n
  Returns a new access token.
  ---
  tags:
    - Authentication
  security:
    - Bearer: []
  parameters:
    - in: header
      name: Authorization
      required: true
      description: "O Refresh Token válido, precedido pelo esquema 'Bearer '. Exemplo: 'Bearer Bla bla...'"
      schema:
        type: string
  responses:
    200:
      description: Access token renewed successfully.
      schema:
        type: object
        properties:
          access_token:
            type: string
    401:
      description: Invalid or missing refresh token.
      schema:
        type: object
        properties:
          msg:
            type: string
    500:
      description: Error while authenticating user.
      schema:
        type: object
        properties:
          msg:
            type: string
  """
  try:
    current_user = get_jwt_identity()
    if current_user is None:
      return jsonify({'msg': 'Invalid or missing refresh token.'}), 401
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token)
  except Exception as e:
    print(f"Error while authenticating user: {e}")
    return jsonify({'msg': 'Error while authenticating user.'}), 500