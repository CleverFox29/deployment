"""
Activity Feed Routes - Track and display project activities
"""
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from backend.db import activity_log_collection, projects_collection
from backend.utils.auth import token_required

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/project/<project_id>', methods=['GET'])
@token_required
def get_project_activity(project_id):
    """Get activity feed for a project"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        activities = list(activity_log_collection.find(
            {'project_id': project_id}
        ).sort('created_at', -1).limit(limit))
        
        for activity in activities:
            activity['_id'] = str(activity['_id']) if '_id' in activity else None
            activity['created_at'] = activity['created_at'].isoformat()
        
        return {
            'activities': activities,
            'count': len(activities)
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@activity_bp.route('/project/<project_id>/stats', methods=['GET'])
@token_required
def get_project_stats(project_id):
    """Get activity statistics for a project"""
    try:
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        # Get activities from last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_activities = list(activity_log_collection.find({
            'project_id': project_id,
            'created_at': {'$gte': seven_days_ago}
        }))
        
        # Count contributions by type
        contributions_count = {}
        for activity in recent_activities:
            action = activity.get('action', 'unknown')
            contributions_count[action] = contributions_count.get(action, 0) + 1
        
        # Count contributions by user
        user_contributions = {}
        for activity in recent_activities:
            user_id = activity.get('user_id', 'unknown')
            user_contributions[user_id] = user_contributions.get(user_id, 0) + 1
        
        return {
            'project_id': project_id,
            'total_activities': len(recent_activities),
            'activity_breakdown': contributions_count,
            'top_contributors': sorted(
                [(k, v) for k, v in user_contributions.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@activity_bp.route('/milestones/<project_id>', methods=['GET'])
@token_required
def get_project_milestones(project_id):
    """Get project milestones (when items are fully completed)"""
    try:
        activities = list(activity_log_collection.find(
            {'project_id': project_id, 'action': 'contribution_added'}
        ).sort('created_at', -1))
        
        # Group by item and find when each was completed
        item_completions = {}
        
        for activity in activities:
            item_name = activity.get('item_name')
            if item_name and item_name not in item_completions:
                # Check if this item is now complete in the project
                project = projects_collection.find_one({'_id': ObjectId(project_id)})
                for req_item in project.get('required_items', []):
                    if req_item['name'] == item_name:
                        if req_item.get('completed', 0) >= req_item.get('quantity', 0):
                            item_completions[item_name] = activity['created_at']
        
        milestones = [
            {'item': k, 'completed_at': v.isoformat()}
            for k, v in item_completions.items()
        ]
        milestones.sort(key=lambda x: x['completed_at'], reverse=True)
        
        return {
            'project_id': project_id,
            'milestones': milestones,
            'total_completed': len(milestones)
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
