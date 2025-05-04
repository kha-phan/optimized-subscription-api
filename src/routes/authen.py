from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import User
from src import db
from datetime import datetime, timedelta

import jwt
import os

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
TOKEN_EXPIRATION_MINUTES = 30


def generate_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'message': 'Username, password, and email are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        token = generate_token(user)
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401
