"""
Admin Routes for maintenance operations.
"""
import os
from flask import Blueprint, request
from backend.db import clear_database, verify_hierarchy_storage, get_user_hierarchy
from backend.utils.auth import token_required
from bson import ObjectId
from backend.db import users_collection

admin_bp = Blueprint('admin', __name__)

ADMIN_CLEAR_TOKEN = os.getenv('CLEAR_DB_TOKEN')


@admin_bp.route('/clear-db', methods=['POST'])
def clear_db():
    """Clear all MongoDB collections (protected by admin token)."""
    if not ADMIN_CLEAR_TOKEN:
        return {'error': 'CLEAR_DB_TOKEN not configured'}, 500

    provided = request.headers.get('X-Admin-Token')
    if not provided or provided != ADMIN_CLEAR_TOKEN:
        return {'error': 'Forbidden'}, 403

    result = clear_database()
    return {'message': 'Database cleared', 'result': result}, 200


@admin_bp.route('/verify-hierarchy', methods=['GET'])
def verify_hierarchy():
    """Verify database hierarchy structure (User → World → Project)"""
    try:
        stats = verify_hierarchy_storage()
        return {
            'message': 'Database hierarchy verified',
            'structure': 'User → World → Project',
            'stats': stats
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500


@admin_bp.route('/my-hierarchy', methods=['GET'])
@token_required
def my_hierarchy():
    """Get current user's complete hierarchy from database"""
    try:
        user_id = request.user_id
        hierarchy = get_user_hierarchy(user_id)
        
        # Get username
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if user:
            hierarchy['username'] = user.get('username')
        
        return {
            'message': 'Hierarchy retrieved from database',
            'storage_structure': 'User → Worlds → Projects (MongoDB)',
            'hierarchy': hierarchy
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500
