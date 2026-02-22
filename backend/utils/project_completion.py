"""
Project Completion Calculator
Calculates project completion based on inventory and recipes
"""

from typing import Dict, List, Any, Optional
from backend.db import inventory_collection
from backend.items.recipes import MinecraftRecipeLookup


class ProjectCompletionCalculator:
    """Calculate project completion based on available inventory"""
    
    def __init__(self, version: str = "1.19.2"):
        """
        Initialize the completion calculator.
        
        Args:
            version: Minecraft version for recipe lookup
        """
        try:
            self.lookup = MinecraftRecipeLookup(version)
            self.version = version
        except Exception as e:
            print(f"Warning: Could not initialize recipe lookup: {e}")
            self.lookup = None
    
    @staticmethod
    def normalize_item_name(name: str) -> str:
        """
        Normalize item names to handle variations.
        Converts spaces to underscores, lowercase, and handles common variations.
        
        Examples:
            oak logs → oak_log
            Oak Logs → oak_log
            oak_log → oak_log
            OAK LOG → oak_log
        """
        if not name:
            return ""
        
        # Convert to lowercase and replace spaces with underscores
        normalized = name.lower().strip().replace(' ', '_')
        
        # Handle plural forms (remove trailing 's' if it's likely a plural)
        if normalized.endswith('s') and len(normalized) > 1:
            singular = normalized[:-1]
            # Keep plural if it's a known item (we'll check inventory both ways)
            return normalized
        
        return normalized
    
    def find_inventory_item(self, required_name: str, inventory: Dict[str, int]) -> tuple:
        """
        Find an item in inventory with flexible name matching.
        
        Args:
            required_name: Name of item needed
            inventory: User's inventory dictionary
            
        Returns:
            Tuple of (found_quantity, actual_item_name_in_inventory) or (0, required_name)
        """
        if not required_name or not inventory:
            return 0, required_name
        
        required_normalized = self.normalize_item_name(required_name)
        
        # Try exact match first (after normalization)
        for inv_item_name, quantity in inventory.items():
            inv_normalized = self.normalize_item_name(inv_item_name)
            if inv_normalized == required_normalized:
                return quantity, inv_item_name
        
        # Try partial matches (handle singular/plural variations)
        for inv_item_name, quantity in inventory.items():
            inv_normalized = self.normalize_item_name(inv_item_name)
            req_normalized = required_normalized
            
            # Check if one is singular and other is plural
            if inv_normalized.rstrip('s') == req_normalized.rstrip('s'):
                return quantity, inv_item_name
            
            # Check if names are similar (Levenshtein-like simple check)
            if inv_normalized.replace('_', '') == req_normalized.replace('_', ''):
                return quantity, inv_item_name
        
        return 0, required_name
    
    def expand_required_items_from_recipes(self, required_items: List[Dict]) -> List[Dict]:
        """
        Expand required items by looking up recipes.
        If an item is craftable (like diamond_pickaxe), expand to its ingredients.
        
        Args:
            required_items: List of {name, quantity} items
            
        Returns:
            Expanded list with recipes looked up
            
        Example:
            Input: [{name: "diamond_pickaxe", quantity: 1}]
            Output: [{name: "diamond", quantity: 3}, {name: "stick", quantity: 2}]
        """
        if not self.lookup or not required_items:
            return required_items
        
        expanded = []
        
        for req_item in required_items:
            item_name = req_item.get('name', req_item.get('item_name', ''))
            quantity = req_item.get('quantity', 0)
            
            if not item_name or quantity <= 0:
                continue
            
            # Try to get recipe for this item
            try:
                recipe_ingredients = self.get_recipe_ingredients(item_name)
                
                if recipe_ingredients:
                    # This is a craftable item, expand to its ingredients
                    for ingredient_name, ingredient_qty in recipe_ingredients.items():
                        total_needed = ingredient_qty * quantity
                        expanded.append({
                            'name': ingredient_name,
                            'quantity': total_needed,
                            'from_recipe': item_name
                        })
                else:
                    # No recipe found, keep as is
                    expanded.append(req_item)
            except Exception as e:
                # If recipe lookup fails, keep original
                print(f"Warning: Could not expand recipe for {item_name}: {e}")
                expanded.append(req_item)
        
        return expanded
    
    def get_world_inventory(self, user_id: str, world_name: str) -> Dict[str, int]:
        """
        Fetch all inventory items for a world.
        
        Args:
            user_id: User ID
            world_name: Name of the world
            
        Returns:
            Dictionary mapping item names to quantities (keys are normalized)
        """
        try:
            items = list(inventory_collection.find({
                'owner_id': user_id,
                'world_name': world_name
            }))
            
            inventory = {}
            for item in items:
                item_name = self.normalize_item_name(item['item_name'])
                inventory[item_name] = item['quantity']
            
            return inventory
        except Exception as e:
            print(f"Error fetching inventory: {e}")
            return {}
    
    def calculate_item_completion(
        self,
        item_name: str,
        required_quantity: int,
        inventory: Dict[str, int],
        inventory_by_exact_name: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Calculate completion for a single required item.
        
        Args:
            item_name: Name of the item needed for the project
            required_quantity: Total quantity needed
            inventory: User's inventory dictionary (normalized names)
            inventory_by_exact_name: Optional dict with exact names from DB
            
        Returns:
            Dictionary with completion details
        """
        # Try to find the item with flexible matching
        available, found_name = self.find_inventory_item(item_name, inventory)
        
        collected = min(available, required_quantity)
        missing = max(0, required_quantity - collected)
        percent = (collected / required_quantity * 100) if required_quantity > 0 else 0
        
        return {
            "item_name": item_name,
            "required": required_quantity,
            "collected": collected,
            "available": available,
            "missing": missing,
            "percent": round(percent, 2),
            "status": "complete" if missing == 0 else "incomplete",
            "found_as": found_name if available > 0 else None
        }
    
    def calculate_project_completion(
        self,
        project: Dict[str, Any],
        user_id: str,
        world_name: str
    ) -> Dict[str, Any]:
        """
        Calculate overall project completion based on inventory.
        
        Args:
            project: Project document with required_items
            user_id: User ID
            world_name: World name
            
        Returns:
            Dictionary with detailed completion breakdown
            
        Example:
            {
                "project_id": "...",
                "project_name": "Diamond Pickaxe",
                "world_name": "Survival",
                "overall_percent": 75.5,
                "total_required": 8,
                "total_collected": 6,
                "total_missing": 2,
                "items": [
                    {
                        "item_name": "diamond",
                        "required": 3,
                        "collected": 3,
                        "missing": 0,
                        "percent": 100.0,
                        "status": "complete"
                    },
                    ...
                ],
                "status": "in_progress"
            }
        """
        # Get user's inventory
        inventory = self.get_world_inventory(user_id, world_name)
        
        required_items = project.get('required_items', [])
        
        # Expand required items if they're craftable (e.g., diamond_pickaxe → diamonds + sticks)
        required_items = self.expand_required_items_from_recipes(required_items)
        
        if not required_items:
            return {
                "project_id": str(project.get('_id', '')),
                "project_name": project.get('project_name', ''),
                "world_name": world_name,
                "overall_percent": 0.0,
                "total_required": 0,
                "total_collected": 0,
                "total_missing": 0,
                "items": [],
                "status": "no_items"
            }
        
        # Calculate completion for each item
        items_breakdown = []
        total_required = 0
        total_collected = 0
        
        for req_item in required_items:
            item_name = req_item.get('name', req_item.get('item_name', ''))
            required_qty = req_item.get('quantity', 0)
            
            if not item_name or required_qty <= 0:
                continue
            
            completion = self.calculate_item_completion(
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
            "project_id": str(project.get('_id', '')),
            "project_name": project.get('project_name', ''),
            "final_item": project.get('final_item', ''),
            "world_name": world_name,
            "overall_percent": round(overall_percent, 2),
            "total_required": total_required,
            "total_collected": total_collected,
            "total_missing": total_missing,
            "items": items_breakdown,
            "status": overall_status
        }
    
    def calculate_projects_completion(
        self,
        projects: List[Dict[str, Any]],
        user_id: str,
        world_name: str
    ) -> List[Dict[str, Any]]:
        """
        Calculate completion for multiple projects.
        
        Args:
            projects: List of project documents
            user_id: User ID
            world_name: World name
            
        Returns:
            List of completion details for each project
        """
        results = []
        for project in projects:
            completion = self.calculate_project_completion(project, user_id, world_name)
            results.append(completion)
        
        return results
    
    def get_recipe_ingredients(self, item_name: str) -> Dict[str, int]:
        """
        Get the ingredients needed to craft an item using the recipe library.
        
        Args:
            item_name: Name of the item to craft
            
        Returns:
            Dictionary of {ingredient_name: quantity_needed}
        """
        if not self.lookup:
            return {}
        
        try:
            recipes = self.lookup.get_recipes_for_item(item_name)
            if not recipes:
                return {}
            
            # Get requirements from first (most common) recipe
            recipe = recipes[0]
            requirements = self.lookup.get_recipe_requirements(recipe)
            return requirements
        except Exception as e:
            print(f"Error getting recipe for {item_name}: {e}")
            return {}
    
    def check_if_craftable(
        self,
        item_name: str,
        inventory: Dict[str, int],
        max_depth: int = 3,
        visited: set = None
    ) -> tuple:
        """
        Check if an item can be crafted from available inventory.
        Recursively checks recipe chains (e.g., oak_log → oak_planks → sticks).
        
        Args:
            item_name: Name of item to check
            inventory: Available items in inventory
            max_depth: Max recursion depth to prevent infinite loops
            visited: Set of already visited items
            
        Returns:
            Tuple of (is_craftable, crafting_path) where crafting_path is list of steps
        """
        if visited is None:
            visited = set()
        
        if max_depth <= 0:
            return False, []
        
        normalized_item = self.normalize_item_name(item_name)
        
        # Check if we already have it
        for inv_name, qty in inventory.items():
            if self.normalize_item_name(inv_name) == normalized_item and qty > 0:
                return True, [f"Have {normalized_item} in inventory"]
        
        # Avoid infinite loops
        if normalized_item in visited:
            return False, []
        
        visited.add(normalized_item)
        
        # Try to get recipe
        recipe_ingredients = self.get_recipe_ingredients(item_name)
        
        if not recipe_ingredients:
            return False, []
        
        # Check if we have all ingredients (or can craft them)
        craftable = True
        paths = []
        
        for ingredient_name, needed_qty in recipe_ingredients.items():
            ingredient_normalized = self.normalize_item_name(ingredient_name)
            
            # Check if we have the ingredient
            available, found_as = self.find_inventory_item(ingredient_name, inventory)
            
            if available >= needed_qty:
                paths.append(f"✅ Have {needed_qty}x {ingredient_name} ({available} available)")
            else:
                # Try to see if we can craft this ingredient
                can_craft, craft_path = self.check_if_craftable(
                    ingredient_name,
                    inventory,
                    max_depth - 1,
                    visited.copy()
                )
                
                if can_craft:
                    paths.extend(craft_path)
                    paths.append(f"  → Can craft {ingredient_name} from available items")
                else:
                    craftable = False
                    paths.append(f"❌ Missing: {needed_qty}x {ingredient_name} (have {available})")
        
        if craftable:
            paths.insert(0, f"✅ Can craft: {normalized_item}")
        else:
            paths.insert(0, f"❌ Cannot craft: {normalized_item}")
        
        return craftable, paths
    
    def get_recipe_output_quantity(self, recipe: Dict) -> int:
        """
        Get the output quantity from a recipe.
        
        Args:
            recipe: Recipe dictionary
            
        Returns:
            Quantity produced (default 1 if not specified)
        """
        try:
            result = recipe.get("result", {})
            if isinstance(result, dict):
                return result.get("count", 1)
            return 1
        except:
            return 1
    
    def calculate_craftable_quantity(
        self,
        item_name: str,
        inventory: Dict[str, int],
        depth: int = 0,
        visited: set = None
    ) -> tuple:
        """
        Calculate how many of an item can be crafted from available inventory.
        Recursively handles crafting chains (oak_planks → sticks).
        
        Args:
            item_name: Item to craft
            inventory: Available materials
            depth: Current recursion depth
            visited: Items already processed to avoid loops
            
        Returns:
            Tuple of (quantity_craftable, crafting_notes)
        """
        if visited is None:
            visited = set()
        
        if depth > 5:  # Prevent infinite recursion
            return 0, [f"⚠️ Recipe chain too deep for {item_name}"]
        
        normalized_item = self.normalize_item_name(item_name)
        
        # Avoid processing same item twice
        if normalized_item in visited:
            return 0, []
        
        visited.add(normalized_item)
        
        # Get recipe for this item
        if not self.lookup:
            return 0, [f"⚠️ Recipe lookup unavailable"]
        
        try:
            recipes = self.lookup.get_recipes_for_item(item_name)
            if not recipes:
                return 0, [f"⚠️ No recipes for {item_name}"]
            
            recipe = recipes[0]
            recipe_requirements = self.lookup.get_recipe_requirements(recipe)
            output_qty = self.get_recipe_output_quantity(recipe)
            
            if not recipe_requirements:
                return 0, [f"⚠️ Invalid recipe for {item_name}"]
            
            # Check how many batches we can make
            min_batches = float('inf')
            bottleneck_item = None
            crafting_log = []
            
            for ingredient_name, needed_qty_per_batch in recipe_requirements.items():
                # Check if we have this ingredient in inventory
                available_qty, found_as = self.find_inventory_item(ingredient_name, inventory)
                
                if available_qty >= needed_qty_per_batch:
                    # Have enough for at least one batch
                    batches = available_qty // needed_qty_per_batch
                    if batches < min_batches:
                        min_batches = batches
                        bottleneck_item = ingredient_name
                    crafting_log.append(f"  ✅ {ingredient_name}: need {needed_qty_per_batch}/batch, have {available_qty} ({batches} batches)")
                else:
                    # Don't have this ingredient, try to craft it
                    craftable, craft_notes = self.calculate_craftable_quantity(
                        ingredient_name, 
                        inventory, 
                        depth + 1, 
                        visited.copy()
                    )
                    
                    if craftable >= needed_qty_per_batch:
                        batches = craftable // needed_qty_per_batch
                        if batches < min_batches:
                            min_batches = batches
                            bottleneck_item = ingredient_name
                        crafting_log.append(f"  🔧 {ingredient_name}: can craft {craftable} ({batches} batches)")
                        crafting_log.extend(craft_notes)
                    else:
                        # Can't get enough of this ingredient
                        crafting_log.append(f"  ❌ {ingredient_name}: need {needed_qty_per_batch}/batch, only have/can make {craftable}")
                        return 0, crafting_log
            
            if min_batches == float('inf'):
                return 0, [f"⚠️ Cannot craft {item_name}"]
            
            total_craftable = min_batches * output_qty
            crafting_log.insert(0, f"🔨 Can craft {total_craftable}x {item_name}")
            
            return total_craftable, crafting_log
            
        except Exception as e:
            return 0, [f"⚠️ Error crafting {item_name}: {str(e)}"]
    
    def calculate_item_completion_with_recipes(
        self,
        item_name: str,
        required_quantity: int,
        inventory: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Calculate completion for an item, checking both direct inventory and craftable items.
        This is smarter version that understands crafting chains and calculates actual quantities.
        
        Args:
            item_name: Name of the item needed
            required_quantity: How many are needed
            inventory: Available items in inventory
            
        Returns:
            Dictionary with completion details including crafting info
        """
        # First check direct inventory
        available_direct, found_name = self.find_inventory_item(item_name, inventory)
        
        total_available = available_direct
        crafting_notes = []
        
        # If we don't have enough, try to craft it
        if total_available < required_quantity:
            craftable_qty, craft_notes = self.calculate_craftable_quantity(item_name, inventory)
            total_available = available_direct + craftable_qty
            crafting_notes = craft_notes
        
        # Calculate final numbers
        collected = min(total_available, required_quantity)
        missing = max(0, required_quantity - collected)
        percent = (collected / required_quantity * 100) if required_quantity > 0 else 0
        
        return {
            "item_name": item_name,
            "required": required_quantity,
            "collected": collected,
            "available_direct": available_direct,
            "available_craftable": total_available - available_direct,
            "total_available": total_available,
            "missing": missing,
            "percent": round(percent, 2),
            "status": "complete" if missing == 0 else "incomplete",
            "found_as": found_name if available_direct > 0 else None,
            "crafting_notes": crafting_notes
        }
    

    def get_recipes_for_project_item(
        self,
        item_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all recipes that can produce a specific item.
        
        Args:
            item_name: Name of the item to craft
            
        Returns:
            List of recipe dictionaries
        """
        if not self.lookup:
            return []
        
        try:
            return self.lookup.get_recipes_for_item(item_name)
        except Exception as e:
            print(f"Error getting recipes for {item_name}: {e}")
            return []
    
    def get_recipe_requirements(
        self,
        item_name: str,
        inventory: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Get recipe requirements for an item and check against inventory.
        
        Args:
            item_name: Name of the item to craft
            inventory: User's inventory dictionary
            
        Returns:
            Dictionary with recipe requirements and completion
        """
        if not self.lookup:
            return {"error": "Recipe lookup not available"}
        
        try:
            recipes = self.lookup.get_recipes_for_item(item_name)
            
            if not recipes:
                return {
                    "item_name": item_name,
                    "recipes_available": False,
                    "message": f"No recipes found for {item_name}"
                }
            
            # Get the first (most common) recipe
            recipe = recipes[0]
            requirements = self.lookup.get_recipe_requirements(recipe)
            
            # Calculate completion for this recipe
            completion = self.lookup.get_recipe_completion(recipe, inventory)
            
            return {
                "item_name": item_name,
                "recipes_available": True,
                "recipe_count": len(recipes),
                "requirements": requirements,
                "completion": completion
            }
        
        except Exception as e:
            print(f"Error calculating recipe requirements: {e}")
            return {"error": str(e)}
