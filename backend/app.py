"""
CraftChain Flask API Server
"""
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from backend.db import init_db

load_dotenv()

# Initialize Flask App with static and template folders
app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), '..'),
            static_url_path='',
            template_folder=os.path.join(os.path.dirname(__file__), '..'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS
CORS(app)

# Initialize Database
init_db()

# Import and register blueprints
from backend.routes.auth import auth_bp
from backend.routes.projects import projects_bp
from backend.routes.contributions import contributions_bp
from backend.routes.activity import activity_bp
from backend.routes.admin import admin_bp
from backend.routes.items import items_bp
from backend.routes.inventory import inventory_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(projects_bp, url_prefix='/api/projects')
app.register_blueprint(contributions_bp, url_prefix='/api/contributions')
app.register_blueprint(activity_bp, url_prefix='/api/activity')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(items_bp, url_prefix='/api/items')
app.register_blueprint(inventory_bp, url_prefix='/api/inventory')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'ok', 'message': 'CraftChain API is running'}, 200

# Serve index.html on root
@app.route('/', methods=['GET'])
def index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..'), 'index.html')

# Serve other static files (CSS, JS, HTML)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..'), path)

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=os.getenv('FLASK_DEBUG', True))
