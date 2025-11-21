from flask import Blueprint, render_template, request, redirect, url_for,session,flash,jsonify
from datetime import datetime,timedelta
from models import *
import jwt
from config import SECRET_KEY
from werkzeug.security import generate_password_hash, check_password_hash
api_users_bp = Blueprint('api_users', __name__, url_prefix='/api/users')
TOKEN_EXPIRES=7200

@api_users_bp.route("/register", methods=["POST"])
def register():
    # Ensure JSON request
    if not request.is_json:
        return jsonify({"error": "JSON data required"}), 400

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Check if user exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    # Hash password and create user
    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, password=hashed_pw)
    db2.session.add(new_user)
    db2.session.commit()

    # Generate JWT token
    token = jwt.encode({
        "user_id": new_user.id,
        "exp": datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRES)
    }, SECRET_KEY, algorithm="HS256")

    # Return success JSON with token
    return jsonify({
        "message": "Registration successful!",
        "token": token,
        "user": {"id": new_user.id, "username": new_user.username}
    }), 201
    
@api_users_bp.route("/login", methods=["POST"])
def login():
    # Ensure JSON request
    if not request.is_json:
        return jsonify({"error": "JSON data required"}), 400

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Find user in DB
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate JWT token
    token = jwt.encode({
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRES)
    }, SECRET_KEY, algorithm="HS256")
    print("token:",token)
    # Return success JSON with token
    return jsonify({
        "message": "Login successful!",
        "token": token,
        "user": {"id": user.id, "username": user.username}
    }), 200