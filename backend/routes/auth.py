"""
Authentication Routes
"""
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from backend.db import (
    users_collection,
    projects_collection,
    contributions_collection,
    ensure_user_folder,
    drop_user_folder,
)
from backend.models.models import User
from backend.utils.auth import hash_password, verify_password, generate_token, decode_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return {'error': 'Missing required fields'}, 400
        
        username = data.get('username', '').strip() or data.get('user_id', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return {'error': 'Username and password are required'}, 400
        
        # Validate inputs
        if len(username) < 4:
            return {'error': 'Username must be at least 4 characters'}, 400
        if len(password) < 6:
            return {'error': 'Password must be at least 6 characters'}, 400
        
        # Check if user already exists
        if users_collection.find_one({'username': username}):
            return {'error': 'User already exists'}, 409
        
        # Create new user
        password_hash = hash_password(password)
        new_user = User(username, password_hash)
        
        users_collection.insert_one({
            '_id': new_user._id,
            'username': username,
            'password_hash': password_hash,
            'role': 'player',
            'created_at': new_user.created_at
        })

        # Provision a lightweight per-user folder metadata doc
        ensure_user_folder(str(new_user._id))
        
        token = generate_token(str(new_user._id))
        
        return {
            'message': 'User created successfully',
            'user_id': str(new_user._id),
            'username': username,
            'token': token
        }, 201
        
    except Exception as e:
        return {'error': str(e)}, 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return token"""
    try:
        data = request.get_json()
        
        if not data:
            return {'error': 'Username and password required'}, 400
        
        username = data.get('username', '').strip() or data.get('user_id', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return {'error': 'Username and password are required'}, 400
        
        # Find user by username only
        user = users_collection.find_one({'username': username})
        
        if not user or not verify_password(password, user['password_hash']):
            return {'error': 'Invalid credentials'}, 401
        
        token = generate_token(str(user['_id']))
        
        return {
            'message': 'Login successful',
            'user_id': str(user['_id']),
            'username': user['username'],
            'token': token
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user info from token (server-side only)"""
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return {'error': 'Authorization header missing'}, 401
        
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return {'error': 'Invalid token format'}, 401
        
        payload = decode_token(token)
        
        if not payload:
            return {'error': 'Invalid or expired token'}, 401
        
        user = users_collection.find_one({'_id': ObjectId(payload['user_id'])})
        
        if not user:
            return {'error': 'User not found'}, 404
        
        return {
            'user_id': str(user['_id']),
            'username': user['username'],
            'role': user.get('role', 'player'),
            'created_at': user['created_at']
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    try:
        from backend.utils.auth import token_required
        
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return {'error': 'Authorization header missing'}, 401
        
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return {'error': 'Invalid token format'}, 401
        
        from backend.utils.auth import decode_token
        payload = decode_token(token)
        
        if not payload:
            return {'error': 'Invalid or expired token'}, 401
        
        user = users_collection.find_one({'_id': ObjectId(payload['user_id'])})
        
        if not user:
            return {'error': 'User not found'}, 404
        
        return {
            'user_id': str(user['_id']),
            'username': user['username'],
            'role': user.get('role', 'player'),
            'created_at': user['created_at']
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@auth_bp.route('/delete', methods=['DELETE'])
def delete_user():
    """Delete the current user (requires Authorization bearer token)."""
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return {'error': 'Authorization header missing'}, 401

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return {'error': 'Invalid token format'}, 401

        payload = decode_token(token)
        if not payload:
            return {'error': 'Invalid or expired token'}, 401

        user_id = payload.get('user_id')
        if not user_id:
            return {'error': 'Invalid token payload'}, 400

        # Delete by ObjectId when possible; fall back to string id
        deleted = 0
        try:
            deleted = users_collection.delete_one({'_id': ObjectId(user_id)}).deleted_count
        except Exception:
            deleted = users_collection.delete_one({'_id': user_id}).deleted_count

        if deleted == 0:
            return {'error': 'User not found'}, 404

        # Optional cleanup: remove owned projects and contributions by this user
        try:
            projects_collection.delete_many({'owner_id': user_id})
            contributions_collection.delete_many({'user_id': user_id})
        except Exception:
            # Best-effort cleanup; do not block user deletion on failure
            pass

        # Remove the user's folder metadata
        try:
            drop_user_folder(user_id)
        except Exception:
            pass

        return {'message': 'User deleted successfully'}, 200

    except Exception as e:
        return {'error': str(e)}, 500
