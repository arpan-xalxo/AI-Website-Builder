from flask import Blueprint, request, jsonify
from models import Website
from bson.objectid import ObjectId
from auth import token_required
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import render_template
from website import can_edit_website 


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

@ai_bp.route('/generate-website', methods=['POST'])
@token_required
def generate_website(email, user_id, role_id):
        from app import mongo
        try:
            # This call now uses the secure, imported function from website.py
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


@ai_bp.route('/regenerate-website/<website_id>', methods=['PUT'])
@token_required
def regenerate_website(email, user_id, role_id, website_id):
    from app import mongo
    from website import can_edit_website 
    
   
    website_to_edit = mongo.db.websites.find_one({'_id': ObjectId(website_id)})
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
        print(f"Error re-generating website: {e}")
        return jsonify({'msg': f'Error re-generating website: {str(e)}'}), 500
