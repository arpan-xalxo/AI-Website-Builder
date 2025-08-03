from flask import Blueprint, render_template, jsonify, make_response
from models import Website
from bson.objectid import ObjectId
from auth import token_required, can_access_website

preview_bp = Blueprint('preview', __name__)

# Add a route that accepts an optional, random cache-busting segment in the path
@preview_bp.route('/preview/<website_id>/<cache_bust>')
@preview_bp.route('/preview/<website_id>')
@token_required
def preview_website(email, user_id, role_id, website_id, cache_bust=None): 
    # The 'cache_bust' parameter is ignored. Its only purpose is to make the URL unique.
    from app import mongo

    try:
        website = Website.find_by_id(mongo, website_id)

        if not website:
            return jsonify({'msg': 'Website not found'}), 404

        owner_id = website.get('owner_id') 
        
        if not can_access_website(user_id, role_id, owner_id):
            return jsonify({'msg': 'Insufficient permissions'}), 403

        website_data = website.get('data', {})
        
        if 'metadata' in website_data:
            website_data['title'] = website_data['metadata'].get('business_type', 'Business Website')

        html_response = render_template('website_template.html', website_data=website_data)
        response = make_response(html_response)
        
        # Keep the forceful no-cache headers as a best practice
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response

    except Exception as e:
        print(f"Error in preview: {e}")
        return jsonify({'msg': 'Error loading website preview'}), 500