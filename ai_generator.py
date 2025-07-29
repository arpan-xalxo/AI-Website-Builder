from flask import Blueprint, request, jsonify
from models import Website
from bson.objectid import ObjectId
from auth import token_required
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

ai_bp = Blueprint('ai', __name__)

# Configure Gemini
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def generate_website_content_gemini(business_type, industry, description=""):
    """Generate website content using Gemini"""
    prompt = f"""
    Create a professional website content for a {business_type} business in the {industry} industry.
    
    Business description: {description}
    
    Generate a JSON structure with the following sections:
    1. Hero section (heading, subheading)
    2. About section (title, content)
    3. Services section (array of 3-5 services with name and description)
    4. Contact section (title, content)
    
    Return only valid JSON without any additional text or markdown formatting.
    """
    try:
        # Try gemini-2.5-flash first, fallback to gemini-pro
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
        except Exception as e:
            print(f"gemini-2.5-flash failed, trying gemini-pro: {e}")
            response = client.models.generate_content(
                model="gemini-pro",
                contents=prompt
            )
        content = response.text.strip()
        # Clean the response - remove markdown code blocks if present
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
        print(f"Error type: {type(e)}")
        return None

def generate_website_content(business_type, industry, description="", model="gemini"):
    """Generate website content using Gemini only"""
    return generate_website_content_gemini(business_type, industry, description)

# Generate website with AI
@ai_bp.route('/generate-website', methods=['POST'])
@token_required
def generate_website(user_id, role_id):
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
        generated_content = generate_website_content(business_type, industry, description)
        if not generated_content:
            return jsonify({'msg': 'Failed to generate content. Please try again.'}), 500
        try:
            import json
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
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Generated content: {generated_content}")
            return jsonify({'msg': 'Failed to parse generated content. Please try again.'}), 500
        except Exception as e:
            print(f"Error creating website: {e}")
            return jsonify({'msg': f'Error creating website: {str(e)}'}), 500
    except Exception as e:
        print(f"Unexpected error in generate_website: {e}")
        return jsonify({'msg': f'Unexpected error: {str(e)}'}), 500

def can_edit_website(user_id, role_id, website_owner_id=None):
    from app import mongo
    role = mongo.db.roles.find_one({'_id': ObjectId(role_id)})
    if not role:
        return False
    if role['name'] == 'Admin':
        return True
    elif role['name'] == 'Editor':
        return str(website_owner_id) == str(user_id) if website_owner_id else True
    return False 