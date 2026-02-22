"""
CraftChain Flask API Server
Production-ready configuration for Railway deployment
"""
import os
import logging
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from backend.db import init_db

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask App with static and template folders
app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), '..'),
            static_url_path='',
            template_folder=os.path.join(os.path.dirname(__file__), '..'))

# Security Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("SECRET_KEY environment variable must be set for security")

# Check if running in production
IS_PRODUCTION = os.getenv('RAILWAY_ENVIRONMENT') is not None or os.getenv('FLASK_ENV') == 'production'

# Enable CORS with proper configuration
if IS_PRODUCTION:
    # In production, configure CORS with your frontend domain
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)
    logger.info(f"Production mode: CORS enabled for origins: {ALLOWED_ORIGINS}")
else:
    # In development, allow all origins
    CORS(app)
    logger.info("Development mode: CORS enabled for all origins")

# Initialize Database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

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
    """Health check endpoint for Railway and monitoring"""
    try:
        # You could add database connectivity check here
        return jsonify({
            'status': 'ok',
            'message': 'CraftChain API is running',
            'environment': 'production' if IS_PRODUCTION else 'development'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Service unhealthy'
        }), 503

# Error handlers
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Serve index.html on root
@app.route('/', methods=['GET'])
def index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..'), 'index.html')

# Serve other static files (CSS, JS, HTML)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..'), path)

if __name__ == '__main__':
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    # Debug mode should be False in production
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true' and not IS_PRODUCTION
    
    logger.info(f"Starting CraftChain API on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
