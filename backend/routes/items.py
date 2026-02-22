"""
Items Routes - Minecraft items and recipes
"""
from flask import Blueprint, request, jsonify
from backend.items.recipes import MinecraftRecipeLookup

items_bp = Blueprint('items', __name__)

# Global lookup instance
_lookup = None

def get_lookup():
    """Get or create MinecraftRecipeLookup instance."""
    global _lookup
    if _lookup is None:
        try:
            _lookup = MinecraftRecipeLookup("1.19.2")
        except Exception as e:
            print(f"Error initializing MinecraftRecipeLookup: {e}")
            _lookup = None
    return _lookup

@items_bp.route('/list', methods=['GET'])
def list_all_items():
    """Get list of all Minecraft items for the current version."""
    try:
        lookup = get_lookup()
        if lookup is None:
            return {'error': 'Minecraft data not available'}, 503
        
        items = lookup.get_all_items()
        return {
            'items': items,
            'count': len(items),
            'version': lookup.version
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@items_bp.route('/metadata', methods=['GET'])
def get_items_metadata():
    """Get list of all Minecraft items with metadata (displayName, stackSize, etc)."""
    try:
        lookup = get_lookup()
        if lookup is None:
            return {'error': 'Minecraft data not available'}, 503
        
        items = lookup.get_all_items_with_metadata()
        return {
            'items': items,
            'count': len(items),
            'version': lookup.version
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@items_bp.route('/search', methods=['GET'])
def search_items():
    """Search for items by name (partial match allowed)."""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return {'error': 'Search query required'}, 400
        
        lookup = get_lookup()
        if lookup is None:
            return {'error': 'Minecraft data not available'}, 503
        
        results = lookup.search_items(query, limit=limit)
        return {
            'query': query,
            'results': results,
            'count': len(results)
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@items_bp.route('/<item_name>/recipe', methods=['GET'])
def get_item_recipe(item_name):
    """Get crafting recipe for a specific item."""
    try:
        lookup = get_lookup()
        if lookup is None:
            return {'error': 'Minecraft data not available'}, 503
        
        recipes = lookup.get_recipes_for_item(item_name.lower())
        if not recipes:
            return {'error': f'No recipes found for item: {item_name}'}, 404
        
        recipe = recipes[0]  # Get first recipe
        requirements = lookup.get_recipe_requirements(recipe)
        
        return {
            'item_name': item_name,
            'recipe_found': True,
            'requirements': requirements,
            'total_items': sum(requirements.values())
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@items_bp.route('/<item_name>/exists', methods=['GET'])
def check_item_exists(item_name):
    """Check if an item exists in Minecraft."""
    try:
        lookup = get_lookup()
        if lookup is None:
            return {'error': 'Minecraft data not available'}, 503
        
        item = lookup.items_by_name.get(item_name.lower())
        if not item:
            return {'exists': False, 'item_name': item_name}, 404
        
        return {'exists': True, 'item': item}, 200
    except Exception as e:
        return {'error': str(e)}, 500
