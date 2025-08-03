from flask import Blueprint, request, jsonify
from models import Website
from bson.objectid import ObjectId
from auth import token_required, can_edit_website
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv('config.env')

ai_bp = Blueprint('ai', __name__)

# Configure Gemini
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Could not configure Gemini: {e}")
    model = None

def generate_website_content_gemini(business_type, industry, description=""):
    """Generate website content using Gemini"""
    if not model:
        return None
        
    prompt = f"""
    Create professional website content for a {business_type} business in the {industry} industry.
    Business description: {description}
    Generate a JSON structure with the following sections:
    1. Hero section (heading, subheading)
    2. About section (title, content)
    3. Services section (array of 3-5 services with name and description)
    4. Contact section (title, content)
    Return only valid JSON without any additional text or markdown formatting.
    """
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Clean up potential markdown code fences
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        return content
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

# Generate website with AI
@ai_bp.route('/generate-website', methods=['POST'])
@token_required
def generate_website(email, user_id, role_id):
    from app import mongo
    try:
        if not can_edit_website(user_id, role_id):
            return jsonify({'msg': 'Insufficient permissions'}), 403
            
        data = request.get_json()
        business_type = data.get('business_type', '')
        industry = data.get('industry', '')
        description = data.get('description', '')

        if not business_type or not industry:
            return jsonify({'msg': 'Business type and industry are required'}), 400

        generated_content = generate_website_content_gemini(business_type, industry, description)
        if not generated_content:
            return jsonify({'msg': 'Failed to generate content. Please try again.'}), 500

        website_data = json.loads(generated_content)
        website_data['metadata'] = {
            'business_type': business_type,
            'industry': industry,
            'description': description,
            'generated_by_ai': True,
            'ai_model': 'gemini'
        }
        website = Website(user_id, website_data)
        result = website.save(mongo)
        
        return jsonify({
            'msg': 'Website generated successfully',
            'website_id': str(result.inserted_id),
            'content': website_data,
            'ai_model_used': 'gemini'
        }), 201

    except json.JSONDecodeError:
        return jsonify({'msg': 'Failed to parse AI-generated content. Please try again.'}), 500
    except Exception as e:
        return jsonify({'msg': f'An unexpected error occurred: {str(e)}'}), 500

# Re-generate website with AI
@ai_bp.route('/regenerate-website/<website_id>', methods=['PUT'])
@token_required
def regenerate_website(email, user_id, role_id, website_id):
    from app import mongo
    
    website_to_edit = Website.find_by_id(mongo, website_id)
    if not website_to_edit:
        return jsonify({'msg': 'Website not found'}), 404
        
    if not can_edit_website(user_id, role_id, website_to_edit.get('owner_id')):
        return jsonify({'msg': 'Insufficient permissions'}), 403

    data = request.get_json()
    business_type = data.get('business_type', '')
    industry = data.get('industry', '')
    description = data.get('description', '')

    if not business_type or not industry:
        return jsonify({'msg': 'Business type and industry are required'}), 400

    generated_content = generate_website_content_gemini(business_type, industry, description)
    if not generated_content:
        return jsonify({'msg': 'Failed to generate content. Please try again.'}), 500
        
    try:
        website_data = json.loads(generated_content)
        website_data['metadata'] = {
            'business_type': business_type,
            'industry': industry,
            'description': description,
            'generated_by_ai': True,
            'ai_model': 'gemini'
        }
        
        mongo.db.websites.update_one(
            {'_id': ObjectId(website_id)},
            {'$set': {'data': website_data}}
        )
        
        return jsonify({
            'msg': 'Website re-generated successfully',
            'website_id': website_id,
            'content': website_data
        }), 200

    except Exception as e:
        return jsonify({'msg': f'Error re-generating website: {str(e)}'}), 500