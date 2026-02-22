"""
Inventory Routes - Manage world inventory items
"""
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from backend.db import (
    inventory_collection,
    activity_log_collection
)
from backend.models.models import InventoryItem
from backend.utils.auth import token_required

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/<world_name>', methods=['GET'])
@token_required
def get_world_inventory(world_name):
    """Get all inventory items for a specific world"""
    try:
        user_id = request.user_id
        world_name = world_name.strip()
        
        if not world_name:
            return {'error': 'World name cannot be empty'}, 400
        
        # Get all inventory items for this world
        items = list(inventory_collection.find({
            'owner_id': user_id,
            'world_name': world_name
        }))
        
        # Convert ObjectIds to strings
        for item in items:
            item['_id'] = str(item['_id'])
            if isinstance(item['created_at'], datetime):
                item['created_at'] = item['created_at'].isoformat()
            if isinstance(item['updated_at'], datetime):
                item['updated_at'] = item['updated_at'].isoformat()
        
        # Calculate total items
        total_items = sum(item['quantity'] for item in items)
        
        return {
            'world_name': world_name,
            'items': items,
            'count': len(items),
            'total_items': total_items
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@inventory_bp.route('/<world_name>/item', methods=['POST'])
@token_required
def add_inventory_item(world_name):
    """Add or update an item in world inventory"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        if not data or not all(k in data for k in ['item_name', 'quantity']):
            return {'error': 'Missing required fields (item_name, quantity)'}, 400
        
        world_name = world_name.strip()
        item_name = data['item_name'].strip().lower()
        quantity = int(data['quantity'])
        
        if not world_name:
            return {'error': 'World name cannot be empty'}, 400
        
        if not item_name:
            return {'error': 'Item name cannot be empty'}, 400
        
        if quantity <= 0:
            return {'error': 'Quantity must be greater than 0'}, 400
        
        # Check if item already exists in inventory
        existing_item = inventory_collection.find_one({
            'owner_id': user_id,
            'world_name': world_name,
            'item_name': item_name
        })
        
        if existing_item:
            # Update existing item
            updated_doc = {
                '$set': {
                    'quantity': quantity,
                    'updated_at': datetime.utcnow()
                }
            }
            inventory_collection.update_one(
                {'_id': existing_item['_id']},
                updated_doc
            )
            item_id = str(existing_item['_id'])
            action = 'inventory_item_updated'
        else:
            # Create new item
            inventory_item = InventoryItem(
                owner_id=user_id,
                world_name=world_name,
                item_name=item_name,
                quantity=quantity
            )
            
            inventory_doc = {
                '_id': inventory_item._id,
                'owner_id': inventory_item.owner_id,
                'world_name': inventory_item.world_name,
                'item_name': inventory_item.item_name,
                'quantity': inventory_item.quantity,
                'created_at': inventory_item.created_at,
                'updated_at': inventory_item.updated_at
            }
            
            inventory_collection.insert_one(inventory_doc)
            item_id = str(inventory_item._id)
            action = 'inventory_item_added'
        
        # Log activity
        activity_log_collection.insert_one({
            'world_name': world_name,
            'user_id': user_id,
            'action': action,
            'description': f'{action.replace("_", " ").title()}: {item_name} x{quantity}',
            'created_at': datetime.utcnow()
        })
        
        return {
            'message': f'Item {action}',
            'item_id': item_id,
            'world_name': world_name,
            'item_name': item_name,
            'quantity': quantity
        }, 201
        
    except ValueError:
        return {'error': 'Invalid quantity value'}, 400
    except Exception as e:
        return {'error': str(e)}, 500


@inventory_bp.route('/<world_name>/item/<item_id>', methods=['GET'])
@token_required
def get_inventory_item(world_name, item_id):
    """Get a specific inventory item"""
    try:
        user_id = request.user_id
        world_name = world_name.strip()
        
        item = inventory_collection.find_one({
            '_id': ObjectId(item_id),
            'owner_id': user_id,
            'world_name': world_name
        })
        
        if not item:
            return {'error': 'Item not found'}, 404
        
        item['_id'] = str(item['_id'])
        item['created_at'] = item['created_at'].isoformat() if isinstance(item['created_at'], datetime) else item['created_at']
        item['updated_at'] = item['updated_at'].isoformat() if isinstance(item['updated_at'], datetime) else item['updated_at']
        
        return {'item': item}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@inventory_bp.route('/<world_name>/item/<item_id>', methods=['DELETE'])
@token_required
def delete_inventory_item(world_name, item_id):
    """Delete an inventory item"""
    try:
        user_id = request.user_id
        world_name = world_name.strip()
        
        # Find item first to get item_name for logging
        item = inventory_collection.find_one({
            '_id': ObjectId(item_id),
            'owner_id': user_id,
            'world_name': world_name
        })
        
        if not item:
            return {'error': 'Item not found'}, 404
        
        item_name = item['item_name']
        
        # Delete the item
        result = inventory_collection.delete_one({
            '_id': ObjectId(item_id),
            'owner_id': user_id,
            'world_name': world_name
        })
        
        if result.deleted_count == 0:
            return {'error': 'Failed to delete item'}, 500
        
        # Log activity
        activity_log_collection.insert_one({
            'world_name': world_name,
            'user_id': user_id,
            'action': 'inventory_item_deleted',
            'description': f'Deleted item: {item_name}',
            'created_at': datetime.utcnow()
        })
        
        return {
            'message': 'Item deleted successfully',
            'item_id': item_id,
            'item_name': item_name
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


@inventory_bp.route('/<world_name>/item/<item_name>/increment', methods=['POST'])
@token_required
def increment_item(world_name, item_name):
    """Increment quantity of an item by 1 (or specified amount)"""
    try:
        user_id = request.user_id
        world_name = world_name.strip()
        item_name = item_name.strip().lower()
        
        data = request.get_json() or {}
        increment_by = int(data.get('amount', 1))
        
        if increment_by <= 0:
            return {'error': 'Increment amount must be greater than 0'}, 400
        
        item = inventory_collection.find_one({
            'owner_id': user_id,
            'world_name': world_name,
            'item_name': item_name
        })
        
        if not item:
            return {'error': 'Item not found in inventory'}, 404
        
        new_quantity = item['quantity'] + increment_by
        
        inventory_collection.update_one(
            {'_id': item['_id']},
            {
                '$set': {
                    'quantity': new_quantity,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        # Log activity
        activity_log_collection.insert_one({
            'world_name': world_name,
            'user_id': user_id,
            'action': 'inventory_item_incremented',
            'description': f'Incremented {item_name} by {increment_by}',
            'created_at': datetime.utcnow()
        })
        
        return {
            'message': 'Item incremented',
            'item_name': item_name,
            'previous_quantity': item['quantity'],
            'new_quantity': new_quantity
        }, 200
        
    except ValueError:
        return {'error': 'Invalid increment amount'}, 400
    except Exception as e:
        return {'error': str(e)}, 500


@inventory_bp.route('/<world_name>/item/<item_name>/decrement', methods=['POST'])
@token_required
def decrement_item(world_name, item_name):
    """Decrement quantity of an item by 1 (or specified amount)"""
    try:
        user_id = request.user_id
        world_name = world_name.strip()
        item_name = item_name.strip().lower()
        
        data = request.get_json() or {}
        decrement_by = int(data.get('amount', 1))
        
        if decrement_by <= 0:
            return {'error': 'Decrement amount must be greater than 0'}, 400
        
        item = inventory_collection.find_one({
            'owner_id': user_id,
            'world_name': world_name,
            'item_name': item_name
        })
        
        if not item:
            return {'error': 'Item not found in inventory'}, 404
        
        new_quantity = max(0, item['quantity'] - decrement_by)
        
        if new_quantity == 0:
            # Delete item if quantity reaches 0
            inventory_collection.delete_one({'_id': item['_id']})
            activity_log_collection.insert_one({
                'world_name': world_name,
                'user_id': user_id,
                'action': 'inventory_item_deleted',
                'description': f'Depleted and removed {item_name}',
                'created_at': datetime.utcnow()
            })
            return {
                'message': 'Item depleted and removed from inventory',
                'item_name': item_name,
                'previous_quantity': item['quantity'],
                'new_quantity': 0
            }, 200
        else:
            # Update quantity
            inventory_collection.update_one(
                {'_id': item['_id']},
                {
                    '$set': {
                        'quantity': new_quantity,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Log activity
            activity_log_collection.insert_one({
                'world_name': world_name,
                'user_id': user_id,
                'action': 'inventory_item_decremented',
                'description': f'Decremented {item_name} by {decrement_by}',
                'created_at': datetime.utcnow()
            })
            
            return {
                'message': 'Item decremented',
                'item_name': item_name,
                'previous_quantity': item['quantity'],
                'new_quantity': new_quantity
            }, 200
        
    except ValueError:
        return {'error': 'Invalid decrement amount'}, 400
    except Exception as e:
        return {'error': str(e)}, 500
