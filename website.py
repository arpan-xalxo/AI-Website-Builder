from flask import Blueprint, request, jsonify
from models import Website
from bson.objectid import ObjectId
from auth import token_required ,can_access_website, can_edit_website

website_bp = Blueprint('website', __name__)

# Create website
@website_bp.route('/websites', methods=['POST'])
@token_required
def create_website(email,user_id, role_id):
    from app import mongo
    if not can_edit_website(user_id, role_id):
        return jsonify({'msg': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    website_data = data.get('data', {})
    
    website = Website(user_id, website_data)
    result = website.save(mongo)
    
    return jsonify({
        'msg': 'Website created',
        'website_id': str(result.inserted_id)
    }), 201

@website_bp.route('/websites', methods=['GET'])
@token_required
def get_websites(email, user_id, role_id):
    from app import mongo
    role = mongo.db.roles.find_one({'_id': ObjectId(role_id)})
    
    if not role:
        return jsonify({'msg': 'Role not found for user, cannot determine permissions.'}), 404

    if role['name'] == 'Admin':
        websites = list(mongo.db.websites.find())
    elif role['name'] == 'Editor':
        websites = list(mongo.db.websites.find({'owner_id': ObjectId(user_id)}))
    else:
       
        websites = list(mongo.db.websites.find())
    
    for w in websites:
        w['_id'] = str(w['_id'])
        owner_obj_id = w.get('owner_id')
        if owner_obj_id:
            w['owner_id'] = str(owner_obj_id)
            owner = mongo.db.users.find_one({'_id': owner_obj_id})
            if owner:
                w['owner_email'] = owner.get('email')
    
    return jsonify(websites)
# Get specific website
@website_bp.route('/websites/<website_id>', methods=['GET'])
@token_required
def get_website(email,user_id, role_id, website_id):
    from app import mongo
    website = Website.find_by_id(mongo, website_id)
    
    if not website:
        return jsonify({'msg': 'Website not found'}), 404
    
    if not can_access_website(user_id, role_id, website['owner_id']):
        return jsonify({'msg': 'Insufficient permissions'}), 403
    
    website['_id'] = str(website['_id'])
    website['owner_id'] = str(website['owner_id'])
    
    return jsonify(website)

# Update website
@website_bp.route('/websites/<website_id>', methods=['PUT'])
@token_required
def update_website(email,user_id, role_id, website_id):
    from app import mongo
    website = Website.find_by_id(mongo, website_id)
    
    if not website:
        return jsonify({'msg': 'Website not found'}), 404
    
    if not can_edit_website(user_id, role_id, website['owner_id']):
        return jsonify({'msg': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    website_data = data.get('data', {})
    
    result = mongo.db.websites.update_one(
        {'_id': ObjectId(website_id)},
        {'$set': {'data': website_data}}
    )
    
    if result.modified_count == 0:
        return jsonify({'msg': 'No changes made'}), 400
    
    return jsonify({'msg': 'Website updated'})

# Delete website
@website_bp.route('/websites/<website_id>', methods=['DELETE'])
@token_required
def delete_website(email,user_id, role_id, website_id):
    from app import mongo
    website = Website.find_by_id(mongo, website_id)
    
    if not website:
        return jsonify({'msg': 'Website not found'}), 404
    
    if not can_edit_website(user_id, role_id, website['owner_id']):
        return jsonify({'msg': 'Insufficient permissions'}), 403
    
    result = mongo.db.websites.delete_one({'_id': ObjectId(website_id)})
    
    if result.deleted_count == 0:
        return jsonify({'msg': 'Website not found'}), 404
    
    return jsonify({'msg': 'Website deleted'}) 