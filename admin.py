from flask import Blueprint, request, jsonify
from models import Role, User
from bson.objectid import ObjectId
from auth import token_required

admin_bp = Blueprint('admin', __name__)

# Helper: Check if user is admin
def is_admin(role_id):
    from app import mongo
    role = mongo.db.roles.find_one({'_id': ObjectId(role_id)})
    return role and role['name'] == 'Admin'

# all roles
@admin_bp.route('/roles', methods=['GET'])
@token_required
def list_roles(email,user_id, role_id):
    from app import mongo
    if not is_admin(role_id):
        return jsonify({'msg': 'Admin only'}), 403
    roles = list(mongo.db.roles.find())
    for r in roles:
        r['_id'] = str(r['_id'])
    return jsonify(roles)

# Create a new role
@admin_bp.route('/roles', methods=['POST'])
@token_required
def create_role(email,user_id, role_id):
    from app import mongo
    if not is_admin(role_id):
        return jsonify({'msg': 'Admin only'}), 403
    data = request.get_json()
    name = data.get('name')
    permissions = data.get('permissions', [])
    if mongo.db.roles.find_one({'name': name}):
        return jsonify({'msg': 'Role already exists'}), 400
    role = Role(name, permissions)
    role.save(mongo)
    return jsonify({'msg': 'Role created'}), 201

# Update a role
@admin_bp.route('/roles/<role_id_param>', methods=['PUT'])
@token_required
def update_role(email,user_id, role_id, role_id_param):
    from app import mongo
    if not is_admin(role_id):
        return jsonify({'msg': 'Admin only'}), 403
    data = request.get_json()
    permissions = data.get('permissions', [])
    result = mongo.db.roles.update_one({'_id': ObjectId(role_id_param)}, {'$set': {'permissions': permissions}})
    if result.matched_count == 0:
        return jsonify({'msg': 'Role not found'}), 404
    return jsonify({'msg': 'Role updated'})

# Delete a role
@admin_bp.route('/roles/<role_id_param>', methods=['DELETE'])
@token_required
def delete_role(email,user_id, role_id, role_id_param):
    from app import mongo
    if not is_admin(role_id):
        return jsonify({'msg': 'Admin only'}), 403
    result = mongo.db.roles.delete_one({'_id': ObjectId(role_id_param)})
    if result.deleted_count == 0:
        return jsonify({'msg': 'Role not found'}), 404
    return jsonify({'msg': 'Role deleted'})

# Assign role to user
@admin_bp.route('/users/<user_id_param>/role', methods=['PUT'])
@token_required
def assign_role(email,user_id, role_id, user_id_param):
    from app import mongo
    if not is_admin(role_id):
        return jsonify({'msg': 'Admin only'}), 403
    data = request.get_json()
    new_role_id = data.get('role_id')
    result = mongo.db.users.update_one({'_id': ObjectId(user_id_param)}, {'$set': {'role_id': ObjectId(new_role_id)}})
    if result.matched_count == 0:
        return jsonify({'msg': 'User not found'}), 404
    return jsonify({'msg': 'Role assigned'}) 