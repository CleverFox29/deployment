"""
Contributions Routes - Track user contributions to projects
"""
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from backend.db import contributions_collection, projects_collection, activity_log_collection
from backend.models.models import Contribution
from backend.utils.auth import token_required

contributions_bp = Blueprint('contributions', __name__)

@contributions_bp.route('', methods=['POST'])
@token_required
def add_contribution():
    """Add a contribution to a project"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        if not data or not all(k in data for k in ['project_id', 'item_name', 'quantity', 'contribution_type']):
            return {'error': 'Missing required fields'}, 400
        
        project_id = data.get('project_id')
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        # Check if user is collaborator
        if user_id not in project.get('collaborators', []):
            return {'error': 'You are not a collaborator on this project'}, 403
        
        # Validate contribution type
        if data['contribution_type'] not in ['collected', 'crafted']:
            return {'error': "contribution_type must be 'collected' or 'crafted'"}, 400
        
        # Check dependencies - cannot mark as crafted if dependencies not met
        item_name = data['item_name']
        required_items = project['required_items']
        
        # Find the item in project
        target_item = next((item for item in required_items if item['name'] == item_name), None)
        
        if target_item is None:
            return {'error': f'Item "{item_name}" not found in project'}, 404
        
        # Create contribution record
        contribution = Contribution(
            project_id=project_id,
            user_id=user_id,
            item_name=item_name,
            quantity=data['quantity'],
            contribution_type=data['contribution_type']
        )
        
        contribution_doc = {
            '_id': contribution._id,
            'project_id': contribution.project_id,
            'user_id': contribution.user_id,
            'item_name': contribution.item_name,
            'quantity': contribution.quantity,
            'contribution_type': contribution.contribution_type,
            'created_at': contribution.created_at,
            'verified': contribution.verified
        }
        
        contributions_collection.insert_one(contribution_doc)
        
        # Update project's required_items
        current_completed = target_item.get('completed', 0)
        new_completed = min(
            current_completed + data['quantity'],
            target_item.get('quantity', 0)  # Don't exceed required quantity
        )
        
        # Update the specific item
        projects_collection.update_one(
            {'_id': ObjectId(project_id), 'required_items.name': item_name},
            {'$set': {'required_items.$.completed': new_completed, 'updated_at': datetime.utcnow()}}
        )
        
        # Log activity
        activity_log_collection.insert_one({
            'project_id': project_id,
            'user_id': user_id,
            'action': 'contribution_added',
            'description': f'{data["contribution_type"].capitalize()} {data["quantity"]}x {item_name}',
            'item_name': item_name,
            'quantity': data['quantity'],
            'created_at': datetime.utcnow()
        })
        
        return {
            'message': 'Contribution recorded successfully',
            'contribution_id': str(contribution._id),
            'contribution': contribution.to_dict()
        }, 201
        
    except Exception as e:
        return {'error': str(e)}, 500


@contributions_bp.route('/project/<project_id>', methods=['GET'])
@token_required
def get_project_contributions(project_id):
    """Get all contributions for a project"""
    try:
        contributions = list(contributions_collection.find(
            {'project_id': project_id}
        ).sort('created_at', -1))
        
        for contrib in contributions:
            contrib['_id'] = str(contrib['_id'])
            contrib['created_at'] = contrib['created_at'].isoformat()
        
        return {
            'contributions': contributions,
            'count': len(contributions)
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@contributions_bp.route('/user/<user_id>', methods=['GET'])
@token_required
def get_user_contributions(user_id):
    """Get all contributions by a user"""
    try:
        contributions = list(contributions_collection.find(
            {'user_id': user_id}
        ).sort('created_at', -1))
        
        for contrib in contributions:
            contrib['_id'] = str(contrib['_id'])
            contrib['created_at'] = contrib['created_at'].isoformat()
        
        return {
            'contributions': contributions,
            'count': len(contributions)
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@contributions_bp.route('/<contribution_id>', methods=['DELETE'])
@token_required
def delete_contribution(contribution_id):
    """Delete a contribution (undo a contribution)"""
    try:
        user_id = request.user_id
        
        contribution = contributions_collection.find_one({'_id': ObjectId(contribution_id)})
        
        if not contribution:
            return {'error': 'Contribution not found'}, 404
        
        if contribution['user_id'] != user_id:
            return {'error': 'You can only delete your own contributions'}, 403
        
        # Get project to update required_items
        project = projects_collection.find_one({'_id': ObjectId(contribution['project_id'])})
        
        # Find and update the item
        for item in project['required_items']:
            if item['name'] == contribution['item_name']:
                item['completed'] = max(0, item.get('completed', 0) - contribution['quantity'])
                break
        
        projects_collection.update_one(
            {'_id': ObjectId(contribution['project_id'])},
            {'$set': {'required_items': project['required_items'], 'updated_at': datetime.utcnow()}}
        )
        
        # Delete contribution
        contributions_collection.delete_one({'_id': ObjectId(contribution_id)})
        
        return {'message': 'Contribution deleted successfully'}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
