"""
Projects Routes - CRUD operations for crafting projects
"""
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from backend.db import (
    projects_collection, 
    contributions_collection, 
    activity_log_collection,
    ensure_world_folder,
    get_user_worlds,
    create_world,
    delete_world
)
from backend.models.models import CraftingProject
from backend.utils.auth import token_required
from backend.utils.project_completion import ProjectCompletionCalculator

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('', methods=['POST'])
@token_required
def create_project():
    """Create a new crafting project"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        if not data or not all(k in data for k in ['project_name', 'final_item', 'required_items', 'world_name']):
            return {'error': 'Missing required fields (project_name, final_item, required_items, world_name)'}, 400
        
        world_name = data['world_name'].strip()
        if not world_name:
            return {'error': 'World name cannot be empty'}, 400
        
        project = CraftingProject(
            project_name=data['project_name'],
            final_item=data['final_item'],
            required_items=data['required_items'],  # [{"name": "wood", "quantity": 10, "completed": 0}, ...]
            owner_id=user_id,
            world_name=world_name
        )
        
        # Ensure the world exists in user's folder hierarchy
        ensure_world_folder(user_id, world_name)
        
        project_doc = {
            '_id': project._id,
            'project_name': project.project_name,
            'final_item': project.final_item,
            'required_items': project.required_items,
            'owner_id': project.owner_id,
            'world_name': project.world_name,
            'collaborators': project.collaborators,
            'created_at': project.created_at,
            'updated_at': project.updated_at,
            'status': project.status,
            'contributions': project.contributions
        }
        
        projects_collection.insert_one(project_doc)
        
        # Log activity
        activity_log_collection.insert_one({
            'project_id': str(project._id),
            'user_id': user_id,
            'action': 'project_created',
            'description': f'Created project: {project.project_name}',
            'created_at': datetime.utcnow()
        })
        
        return {
            'message': 'Project created successfully',
            'project_id': str(project._id),
            'project': project.to_dict()
        }, 201
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/<project_id>', methods=['GET'])
@token_required
def get_project(project_id):
    """Get a specific project"""
    try:
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        project['_id'] = str(project['_id'])
        project['created_at'] = project['created_at'].isoformat()
        project['updated_at'] = project['updated_at'].isoformat()
        
        return {
            'project': project
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('', methods=['GET'])
@token_required
def list_projects():
    """List all projects for current user, optionally filtered by world"""
    try:
        user_id = request.user_id
        world_name = request.args.get('world_name')  # Optional filter by world
        
        # Build query
        query = {
            '$or': [
                {'owner_id': user_id},
                {'collaborators': user_id}
            ]
        }
        
        # Add world filter if specified
        if world_name:
            query['world_name'] = world_name
        
        # Get projects owned or collaborated on by user
        projects = list(projects_collection.find(query).sort('created_at', -1))
        
        for project in projects:
            project['_id'] = str(project['_id'])
            project['created_at'] = project['created_at'].isoformat()
            project['updated_at'] = project['updated_at'].isoformat()
        
        return {
            'projects': projects,
            'count': len(projects)
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/<project_id>', methods=['PUT'])
@token_required
def update_project(project_id):
    """Update a project"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        if project['owner_id'] != user_id:
            return {'error': 'You do not have permission to update this project'}, 403
        
        allowed_updates = ['project_name', 'required_items', 'status']
        update_data = {k: v for k, v in data.items() if k in allowed_updates}
        update_data['updated_at'] = datetime.utcnow()
        
        projects_collection.update_one(
            {'_id': ObjectId(project_id)},
            {'$set': update_data}
        )
        
        updated_project = projects_collection.find_one({'_id': ObjectId(project_id)})
        updated_project['_id'] = str(updated_project['_id'])
        
        return {
            'message': 'Project updated successfully',
            'project': updated_project
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/<project_id>', methods=['DELETE'])
@token_required
def delete_project(project_id):
    """Delete a project"""
    try:
        user_id = request.user_id
        
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        if project['owner_id'] != user_id:
            return {'error': 'You do not have permission to delete this project'}, 403
        
        # Delete associated contributions
        contributions_collection.delete_many({'project_id': project_id})
        
        # Delete activity logs
        activity_log_collection.delete_many({'project_id': project_id})
        
        # Delete the project
        projects_collection.delete_one({'_id': ObjectId(project_id)})
        
        return {
            'message': 'Project deleted successfully'
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/<project_id>/add-collaborator', methods=['POST'])
@token_required
def add_collaborator(project_id):
    """Add a collaborator to project"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        if project['owner_id'] != user_id:
            return {'error': 'Only project owner can add collaborators'}, 403
        
        collaborator_id = data.get('collaborator_id')
        
        if collaborator_id in project.get('collaborators', []):
            return {'error': 'User is already a collaborator'}, 400
        
        projects_collection.update_one(
            {'_id': ObjectId(project_id)},
            {'$push': {'collaborators': collaborator_id}}
        )
        
        return {'message': 'Collaborator added successfully'}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/<project_id>/progress', methods=['GET'])
@token_required
def get_project_progress(project_id):
    """Get detailed progress of a project"""
    try:
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        total_required = sum(item.get('quantity', 0) for item in project['required_items'])
        total_completed = sum(item.get('completed', 0) for item in project['required_items'])
        
        progress_percent = (total_completed / total_required * 100) if total_required > 0 else 0
        
        # Find bottlenecks (items blocking the most progress)
        bottlenecks = [
            item for item in project['required_items']
            if item.get('completed', 0) < item.get('quantity', 0)
        ]
        bottlenecks.sort(key=lambda x: x.get('quantity', 0) - x.get('completed', 0), reverse=True)
        
        return {
            'project_id': project_id,
            'progress_percent': round(progress_percent, 2),
            'total_required': total_required,
            'total_completed': total_completed,
            'required_items': project['required_items'],
            'bottlenecks': bottlenecks[:5]  # Top 5 blocking items
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500

@projects_bp.route('/worlds', methods=['GET'])
@token_required
def list_worlds():
    """
    List all worlds for the current user.
    Worlds are loaded from user's folder hierarchy (user_folders_collection).
    """
    try:
        user_id = request.user_id
        
        # Get worlds from user's folder hierarchy
        worlds = get_user_worlds(user_id)
        
        # Get project counts per world
        world_data = []
        for world in worlds:
            world_name = world.get('name')
            project_count = projects_collection.count_documents({
                'owner_id': user_id,
                'world_name': world_name
            })
            world_data.append({
                'world_name': world_name,
                'created_at': world.get('created_at'),
                'project_count': project_count
            })
        
        return {
            'worlds': world_data,
            'count': len(world_data)
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/worlds', methods=['POST'])
@token_required
def create_world_endpoint():
    """Create a new world in user's folder hierarchy."""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        if not data or 'world_name' not in data:
            return {'error': 'world_name is required'}, 400
        
        world_name = data['world_name'].strip()
        if not world_name:
            return {'error': 'World name cannot be empty'}, 400
        
        world = create_world(user_id, world_name)
        
        return {
            'message': 'World created successfully',
            'world': {
                'world_name': world['name'],
                'created_at': world['created_at'].isoformat()
            }
        }, 201
        
    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/worlds/<world_name>', methods=['DELETE'])
@token_required
def delete_world_endpoint(world_name):
    """Delete a world from user's folder hierarchy."""
    try:
        user_id = request.user_id
        
        deleted = delete_world(user_id, world_name)
        
        if deleted:
            return {'message': f"World '{world_name}' deleted successfully"}, 200
        else:
            return {'error': 'World not found'}, 404
        
    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/hierarchy', methods=['GET'])
@token_required
def get_hierarchy():
    """
    Get full User → Worlds → Projects hierarchy for current user.
    All data loaded DIRECTLY from database - NO caching or localStorage.
    """
    try:
        user_id = request.user_id
        
        # Query database: Get all user's projects
        # Worlds are extracted dynamically from projects
        projects = list(projects_collection.find({
            '$or': [
                {'owner_id': user_id},
                {'collaborators': user_id}
            ]
        }).sort('world_name', 1))
        
        # Organize by world
        hierarchy = {}
        for project in projects:
            world_name = project.get('world_name', 'Unknown')
            
            if world_name not in hierarchy:
                hierarchy[world_name] = []
            
            project['_id'] = str(project['_id'])
            project['created_at'] = project['created_at'].isoformat()
            project['updated_at'] = project['updated_at'].isoformat()
            
            hierarchy[world_name].append(project)
        
        # Convert to list format
        result = [
            {
                'world_name': world,
                'projects': projects
            }
            for world, projects in hierarchy.items()
        ]
        
        return {
            'user_id': user_id,
            'worlds': result,
            'total_worlds': len(result),
            'total_projects': len(projects)
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/<project_id>/completion/smart', methods=['GET'])
@token_required
def get_project_completion_smart(project_id):
    """
    Calculate project completion using smart recipe-aware calculation.
    Understands crafting chains (e.g., oak_log → oak_planks → sticks).
    Automatically expands recipes (e.g., diamond_pickaxe → diamonds + sticks).
    Shows whether items can be crafted from available materials.
    """
    try:
        user_id = request.user_id
        
        # Get the project
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        # Check permission
        if project['owner_id'] != user_id and user_id not in project.get('collaborators', []):
            return {'error': 'You do not have permission to view this project'}, 403
        
        # Get user's inventory
        calculator = ProjectCompletionCalculator()
        inventory = calculator.get_world_inventory(user_id, project['world_name'])
        
        required_items = project.get('required_items', [])
        
        # Expand required items if they're craftable (e.g., diamond_pickaxe → diamonds + sticks)
        required_items = calculator.expand_required_items_from_recipes(required_items)
        
        if not required_items:
            return {
                'completion': {
                    'project_id': str(project.get('_id', '')),
                    'project_name': project.get('project_name', ''),
                    'world_name': project['world_name'],
                    'overall_percent': 0.0,
                    'total_required': 0,
                    'total_collected': 0,
                    'total_missing': 0,
                    'items': [],
                    'status': 'no_items'
                }
            }, 200
        
        # Calculate completion for each item using smart recipe-aware method
        items_breakdown = []
        total_required = 0
        total_collected = 0
        
        for req_item in required_items:
            item_name = req_item.get('name', req_item.get('item_name', ''))
            required_qty = req_item.get('quantity', 0)
            
            if not item_name or required_qty <= 0:
                continue
            
            # Use recipe-aware completion calculation
            completion = calculator.calculate_item_completion_with_recipes(
                item_name,
                required_qty,
                inventory
            )
            
            items_breakdown.append(completion)
            total_required += required_qty
            total_collected += completion['collected']
        
        total_missing = total_required - total_collected
        overall_percent = (total_collected / total_required * 100) if total_required > 0 else 0
        
        # Determine overall status
        if total_missing == 0 and total_required > 0:
            overall_status = "complete"
        elif total_collected == 0:
            overall_status = "not_started"
        else:
            overall_status = "in_progress"
        
        return {
            'completion': {
                'project_id': str(project.get('_id', '')),
                'project_name': project.get('project_name', ''),
                'final_item': project.get('final_item', ''),
                'world_name': project['world_name'],
                'overall_percent': round(overall_percent, 2),
                'total_required': total_required,
                'total_collected': total_collected,
                'total_missing': total_missing,
                'items': items_breakdown,
                'status': overall_status,
                'calculation_method': 'recipe-aware (considers crafting)'
            }
        }, 200
        
    except Exception as e:
        import traceback
        return {
            'error': str(e),
            'traceback': traceback.format_exc()
        }, 500



@token_required
def get_project_completion(project_id):
    """
    Calculate project completion based on current inventory.
    Compares required items against world inventory.
    """
    try:
        user_id = request.user_id
        
        # Get the project
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        # Check permission
        if project['owner_id'] != user_id and user_id not in project.get('collaborators', []):
            return {'error': 'You do not have permission to view this project'}, 403
        
        # Calculate completion using the calculator
        calculator = ProjectCompletionCalculator()
        completion = calculator.calculate_project_completion(
            project,
            user_id,
            project['world_name']
        )
        
        return {'completion': completion}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/world/<world_name>/completion', methods=['GET'])
@token_required
def get_world_projects_completion(world_name):
    """
    Calculate completion for all projects in a world based on inventory.
    """
    try:
        user_id = request.user_id
        world_name = world_name.strip()
        
        # Get all projects in this world
        projects = list(projects_collection.find({
            'owner_id': user_id,
            'world_name': world_name
        }))
        
        if not projects:
            return {
                'world_name': world_name,
                'projects': [],
                'count': 0
            }, 200
        
        # Calculate completion for each project
        calculator = ProjectCompletionCalculator()
        completions = calculator.calculate_projects_completion(
            projects,
            user_id,
            world_name
        )
        
        return {
            'world_name': world_name,
            'projects': completions,
            'count': len(completions)
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/<project_id>/recipe-check', methods=['GET'])
@token_required
def check_project_recipe_status(project_id):
    """
    Check recipe availability and requirements for the project's final item.
    """
    try:
        user_id = request.user_id
        
        # Get the project
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        # Check permission
        if project['owner_id'] != user_id and user_id not in project.get('collaborators', []):
            return {'error': 'You do not have permission to view this project'}, 403
        
        # Get inventory for this world
        calculator = ProjectCompletionCalculator()
        inventory = calculator.get_world_inventory(user_id, project['world_name'])
        
        # Check recipe for final item
        final_item = project.get('final_item', '')
        recipe_info = calculator.get_recipe_requirements(final_item, inventory)
        
        return {
            'project_id': project_id,
            'final_item': final_item,
            'recipe_info': recipe_info
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@projects_bp.route('/<project_id>/debug', methods=['GET'])
@token_required
def debug_project_completion(project_id):
    """
    Debug endpoint to show inventory matching for a project.
    Helps identify naming mismatches between inventory and required items.
    """
    try:
        user_id = request.user_id
        
        # Get the project
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        
        if not project:
            return {'error': 'Project not found'}, 404
        
        # Check permission
        if project['owner_id'] != user_id and user_id not in project.get('collaborators', []):
            return {'error': 'You do not have permission to view this project'}, 403
        
        calculator = ProjectCompletionCalculator()
        
        # Get raw inventory from database
        from backend.db import inventory_collection
        raw_inventory_items = list(inventory_collection.find({
            'owner_id': user_id,
            'world_name': project['world_name']
        }))
        
        raw_inventory = {item['item_name']: item['quantity'] for item in raw_inventory_items}
        
        # Get normalized inventory
        normalized_inventory = calculator.get_world_inventory(user_id, project['world_name'])
        
        # Check each required item
        required_items = project.get('required_items', [])
        item_matching = []
        
        for req_item in required_items:
            item_name = req_item.get('name', req_item.get('item_name', ''))
            required_qty = req_item.get('quantity', 0)
            
            if not item_name:
                continue
            
            # Try to find in inventory
            available, found_as = calculator.find_inventory_item(item_name, normalized_inventory)
            
            item_matching.append({
                "required_item": item_name,
                "required_qty": required_qty,
                "found_in_inventory": found_as in raw_inventory,
                "found_as": found_as,
                "available_qty": available,
                "match_status": "✅ FOUND" if available > 0 else "❌ NOT FOUND"
            })
        
        return {
            'project_name': project.get('project_name', ''),
            'world_name': project['world_name'],
            'raw_inventory': raw_inventory,
            'normalized_inventory': normalized_inventory,
            'required_items': required_items,
            'item_matching': item_matching,
            'debug_info': {
                'total_raw_items': len(raw_inventory),
                'total_normalized_items': len(normalized_inventory),
                'matching_results': f"{sum(1 for x in item_matching if x['match_status'].startswith('✅'))}/{len(item_matching)} items found"
            }
        }, 200
        
    except Exception as e:
        import traceback
        return {'error': str(e), 'traceback': traceback.format_exc()}, 500