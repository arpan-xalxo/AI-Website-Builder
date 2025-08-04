from flask import Blueprint, request, jsonify, current_app
from models import User, Role
from bson import ObjectId
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)


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
    role_name = data.get('role', 'Viewer')  

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
        from app import mongo
        token = None

       
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1] 
            except IndexError:
                return jsonify({'msg': 'Invalid token format!'}), 401
        
       
        if not token:
            token = request.args.get('token')
                
        if not token:
            return jsonify({'msg': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, current_app.config.get('SECRET_KEY', 'secret'), algorithms=['HS256'])
            user_id = data['user_id']
            role_id = data['role_id']

            
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return jsonify({'msg': 'User not found'}), 404

           
            role = mongo.db.roles.find_one({'_id': ObjectId(role_id)})
            user['role'] = role['name'] if role else 'Unknown'
            
           
            user['_id'] = str(user['_id'])
            user['role_id'] = str(user['role_id'])

        except jwt.ExpiredSignatureError:
            return jsonify({'msg': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'msg': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'msg': f'Token verification failed: {str(e)}'}), 401
            
        return f(user['email'], user['_id'], user['role_id'], *args, **kwargs)
    return decorated


def can_access_website(user_id, role_id, website_owner_id=None):
    from app import mongo
    role = mongo.db.roles.find_one({'_id': ObjectId(role_id)})
    if not role:
        return False
    
    if role['name'] == 'Admin':
        return True
    elif role['name'] == 'Editor':
        return str(website_owner_id) == str(user_id)
    elif role['name'] == 'Viewer':
        return True
    return False

def can_edit_website(user_id, role_id, website_owner_id=None):
    from app import mongo
    role = mongo.db.roles.find_one({'_id': ObjectId(role_id)})
    if not role:
        return False
    
    if role['name'] == 'Admin':
        return True
    elif role['name'] == 'Editor':
        if website_owner_id is None:
            return True 
        else:
            return str(website_owner_id) == str(user_id) 
    return False
