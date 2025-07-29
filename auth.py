from flask import Blueprint, request, jsonify, current_app
from models import User, Role
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Helper: Generate JWT token
def generate_token(user_id, role_id):
    payload = {
        'user_id': str(user_id),
        'role_id': str(role_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, current_app.config.get('SECRET_KEY', 'secret'), algorithm='HS256')
    return token

# Sign-Up API
@auth_bp.route('/signup', methods=['POST'])
def signup():
    from app import mongo
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role_name = data.get('role', 'Viewer')  # Default role is Viewer

    if User.find_by_email(mongo, email):
        return jsonify({'msg': 'User already exists'}), 400

    role = Role.find_by_name(mongo, role_name)
    if not role:
        return jsonify({'msg': 'Role does not exist'}), 400

    user = User(email, password, role['_id'])
    user_id = user.save(mongo).inserted_id
    token = generate_token(str(user_id), str(role['_id']))
    return jsonify({'token': token}), 201

# Login API
@auth_bp.route('/login', methods=['POST'])
def login():
    from app import mongo
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.find_by_email(mongo, email)
    if not user or not User.check_password(user['password_hash'], password):
        return jsonify({'msg': 'Invalid credentials'}), 401
    token = generate_token(str(user['_id']), str(user['role_id']))
    return jsonify({'token': token}), 200

# JWT-required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return jsonify({'msg': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config.get('SECRET_KEY', 'secret'), algorithms=['HS256'])
            user_id = data['user_id']
            role_id = data['role_id']
        except Exception as e:
            return jsonify({'msg': 'Token is invalid!'}), 401
        return f(user_id, role_id, *args, **kwargs)
    return decorated 