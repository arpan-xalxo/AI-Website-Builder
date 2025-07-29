from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
import os
from dotenv import load_dotenv
from middleware import init_middleware, security_headers
from flask import send_from_directory

# Load environment variables
load_dotenv('config.env')

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey123')
CORS(app)

# Configurations
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/website_builder')
mongo = PyMongo(app)

# Initialize middleware
init_middleware(app)

# Add security headers to all responses
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
app.register_blueprint(ai_bp)
app.register_blueprint(preview_bp)
app.register_blueprint(docs_bp)

# Health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'AI Website Builder API is running'}

@app.route('/favicon.svg')
def favicon():
    return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')    

if __name__ == "__main__":
    app.run(debug=True) 