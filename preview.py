from flask import Blueprint, render_template, request, jsonify
from models import Website
from bson.objectid import ObjectId
from auth import token_required

preview_bp = Blueprint('preview', __name__)

# Preview website (public route - no authentication required)
@preview_bp.route('/preview/<website_id>')
def preview_website(website_id):
    from app import mongo
    
    try:
        # Get website data from MongoDB
        website = Website.find_by_id(mongo, website_id)
        
        if not website:
            return jsonify({'msg': 'Website not found'}), 404
        
        # Extract the website data
        website_data = website.get('data', {})
        
        # Add title from metadata if available
        if 'metadata' in website_data:
            website_data['title'] = website_data['metadata'].get('business_type', 'Business Website')
        
        # Render the template with website data
        return render_template('website_template.html', website_data=website_data)
        
    except Exception as e:
        print(f"Error in preview: {e}")
        return jsonify({'msg': 'Error loading website preview'}), 500

# Preview website with authentication (for private websites)
@preview_bp.route('/preview-auth/<website_id>')
@token_required
def preview_website_auth(user_id, role_id, website_id):
    from app import mongo
    
    try:
        # Get website data from MongoDB
        website = Website.find_by_id(mongo, website_id)
        
        if not website:
            return jsonify({'msg': 'Website not found'}), 404
        
        # Check if user has permission to view this website
        from website import can_access_website
        if not can_access_website(user_id, role_id, website['owner_id']):
            return jsonify({'msg': 'Insufficient permissions'}), 403
        
        # Extract the website data
        website_data = website.get('data', {})
        
        # Add title from metadata if available
        if 'metadata' in website_data:
            website_data['title'] = website_data['metadata'].get('business_type', 'Business Website')
        
        # Render the template with website data
        return render_template('website_template.html', website_data=website_data)
        
    except Exception as e:
        print(f"Error in preview: {e}")
        return jsonify({'msg': 'Error loading website preview'}), 500 