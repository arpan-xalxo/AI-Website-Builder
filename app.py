from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import os
from dotenv import load_dotenv
from middleware import init_middleware, security_headers
from flask import send_from_directory
from auth import token_required
from flask import session, redirect, url_for
from bson.objectid import ObjectId


load_dotenv('config.env')

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey123')
CORS(app)

# Configurations
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/website_builder')
mongo = PyMongo(app)

# Initialize middleware
init_middleware(app)


@app.after_request
def add_security_headers(response):
    return security_headers(response)

# Register blueprints
from auth import auth_bp
from admin import admin_bp
from website import website_bp
from ai_generator import ai_bp
from preview import preview_bp
from docs import docs_bp



app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(website_bp)
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(preview_bp)
app.register_blueprint(docs_bp)


# Health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'AI Website Builder API is running'}

@app.route('/favicon.svg')
def favicon():
    return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')

@app.route('/')
def index():
    """Redirects the root URL to the login page."""
    return redirect(url_for('login_page'))



# Static pages (for forms)
@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/login')
def login_page():
    return render_template('login.html')     

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')  

@app.route('/generate')
def generate_page():
    return render_template('generate.html')

@app.route('/my-websites')
def my_websites_page():
    return render_template('my-websites.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/website_template/<website_id>')
def website_template_page(website_id):
    website = mongo.db.websites.find_one({'_id': ObjectId(website_id)})
    if not website:
        abort(404)
    return render_template('website_template.html', website_data=website)


@app.route('/websites/<website_id>/edit-ai')
@token_required
def website_edit_ai_page(email, user_id, role_id, website_id):
    return render_template('edit_ai.html')


@app.route('/api/dashboard')
@token_required
def dashboard_api(email,user_id, role_id):
    role_doc = mongo.db.roles.find_one({'_id': ObjectId(role_id)})
    role_name = role_doc['name'] if role_doc else 'Unknown'

    return jsonify({
        'user': {
            'email': email,
            'role': role_name,
            'id': user_id
        }
    })


if __name__ == "__main__":
    app.run(debug=True)