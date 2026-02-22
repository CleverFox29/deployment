"""
Minecraft recipe lookup using minecraft-data library.
Retrieves shaped and shapeless recipes for Minecraft items.
"""

import json
import os
import sys
from typing import Optional, Dict, List, Any, Union

try:
    import minecraft_data
except ImportError:
    print("Error: minecraft-data not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


class MinecraftRecipeLookup:
    """Lookup Minecraft recipes using minecraft-data library."""

    def __init__(self, version: str = "1.19.2", edition: str = "pc"):
        """
        Initialize recipe lookup for a specific Minecraft version.
        
        Args:
            version: Minecraft version (e.g., "1.19.2", "1.18.2", "1.16.5")
            edition: Edition type ("pc" for Java Edition)
        """
        self.version = version
        self.edition = edition
        self._load_data()

    def _load_data(self):
        """Load minecraft-data from package."""
        try:
            # Get the minecraft_data package path
            pkg_path = minecraft_data.__path__[0]
            data_path = os.path.join(pkg_path, 'data', 'data')
            
            # Read dataPaths.json to find version-specific paths
            dpaths_file = os.path.join(data_path, 'dataPaths.json')
            with open(dpaths_file, 'r') as f:
                self.data_paths = json.load(f)
            
            if self.edition not in self.data_paths:
                raise ValueError(f"Edition {self.edition} not found")
            
            if self.version not in self.data_paths[self.edition]:
                available = sorted(self.data_paths[self.edition].keys())
                raise ValueError(
                    f"Version {self.version} not found. Available versions: {', '.join(available[-5:])}"
                )
            
            self.data_base_path = data_path
            self._load_items()
            self._load_recipes()
            
        except Exception as e:
            print(f"Error loading minecraft-data: {e}")
            raise

    def _load_items(self):
        """Load items data for name/ID mapping."""
        try:
            version_paths = self.data_paths[self.edition][self.version]
            items_path_rel = version_paths.get('items')
            
            if not items_path_rel:
                raise ValueError("Items data not found for this version")
            
            items_file = os.path.join(self.data_base_path, items_path_rel, 'items.json')
            
            with open(items_file, 'r') as f:
                items_list = json.load(f)
            
            # Create name->id and id->name mappings
            self.items_by_id = {item['id']: item for item in items_list}
            self.items_by_name = {item['name']: item for item in items_list}
            
        except Exception as e:
            print(f"Error loading items: {e}")
            self.items_by_id = {}
            self.items_by_name = {}

    def _load_recipes(self):
        """Load recipes data."""
        try:
            version_paths = self.data_paths[self.edition][self.version]
            recipes_path_rel = version_paths.get('recipes')
            
            if not recipes_path_rel:
                self.recipes_by_id = {}
                return
            
            recipes_file = os.path.join(self.data_base_path, recipes_path_rel, 'recipes.json')
            
            with open(recipes_file, 'r') as f:
                self.recipes_by_id = json.load(f)
            
        except Exception as e:
            print(f"Error loading recipes: {e}")
            self.recipes_by_id = {}

    def get_recipes_for_item(self, item_name: str) -> List[Dict[str, Any]]:
        """
        Get all recipes that produce a specific item by name.
        
        Args:
            item_name: Name of the item (e.g., "stick", "crafting_table")
            
        Returns:
            List of recipe dictionaries
        """
        # Find the item by name
        item = self.items_by_name.get(item_name.lower())
        if not item:
            return []
        
        item_id = item['id']
        return self.recipes_by_id.get(str(item_id), [])

    def get_item_name(self, item_id: int) -> str:
        """Get the name of an item by ID."""
        item = self.items_by_id.get(item_id, {})
        return item.get('name', f'item_{item_id}')

    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Get full item data by ID.
        
        Args:
            item_id: Numeric ID of the item
            
        Returns:
            Dictionary containing item data (id, name, displayName, etc.) or None if not found
            
        Example:
            >>> lookup = MinecraftRecipeLookup("1.19.2")
            >>> item = lookup.get_item_by_id(765)  # Get item with ID 765
            >>> print(item['name'])
        """
        return self.items_by_id.get(item_id)

    def format_item_ref(self, item_ref: Union[int, Dict]) -> str:
        """Format an item reference (ID or dict) to a readable string."""
        if isinstance(item_ref, dict):
            name = self.get_item_name(item_ref.get('id', 0))
            count = item_ref.get('count', 1)
            return f"{count}x {name}" if count > 1 else name
        elif isinstance(item_ref, int):
            name = self.get_item_name(item_ref)
            return name
        return str(item_ref)

    def get_recipe_requirements(self, recipe: Dict) -> Dict[str, int]:
        """
        Extract recipe requirements as a dictionary of item names and amounts.
        
        Args:
            recipe: Recipe dictionary (shaped or shapeless)
            
        Returns:
            Dictionary mapping item names to required amounts
            
        Example:
            >>> lookup = MinecraftRecipeLookup("1.19.2")
            >>> recipes = lookup.get_recipes_for_item("stick")
            >>> requirements = lookup.get_recipe_requirements(recipes[0])
            >>> print(requirements)  # Output: {"oak_planks": 2}
        """
        requirements = {}
        
        # Handle shaped recipes (inShape)
        if "inShape" in recipe:
            for row in recipe.get("inShape", []):
                for item_ref in row:
                    if item_ref is not None:
                        item_name = self.format_item_ref(item_ref)
                        requirements[item_name] = requirements.get(item_name, 0) + 1
        
        # Handle shapeless recipes (ingredients)
        elif "ingredients" in recipe:
            for item_ref in recipe.get("ingredients", []):
                item_name = self.format_item_ref(item_ref)
                requirements[item_name] = requirements.get(item_name, 0) + 1
        
        return requirements

    def get_recipe_completion(self, recipe: Dict, collected_items: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate the completion percentage of a recipe based on items collected.
        
        Args:
            recipe: Recipe dictionary (shaped or shapeless)
            collected_items: Dictionary mapping item names to quantities already collected
                            Example: {"oak_planks": 3, "stick": 1}
            
        Returns:
            Dictionary containing:
                - "completion_percent": Overall completion percentage (0-100)
                - "required": Total items needed
                - "collected": Total items already collected
                - "missing": Total items still needed
                - "details": Dictionary with per-item breakdown
                - "status": "complete" / "incomplete"
                
        Example:
            >>> lookup = MinecraftRecipeLookup("1.19.2")
            >>> recipes = lookup.get_recipes_for_item("crafting_table")
            >>> collected = {"oak_planks": 3}
            >>> completion = lookup.get_recipe_completion(recipes[0], collected)
            >>> print(completion)
            {
              "completion_percent": 75.0,
              "required": 4,
              "collected": 3,
              "missing": 1,
              "details": {
                "oak_planks": {"required": 4, "collected": 3, "missing": 1, "percent": 75.0}
              },
              "status": "incomplete"
            }
        """
        requirements = self.get_recipe_requirements(recipe)
        
        total_required = sum(requirements.values())
        total_collected = 0
        details = {}
        
        for item_name, required_amount in requirements.items():
            collected_amount = collected_items.get(item_name, 0)
            total_collected += min(collected_amount, required_amount)
            
            collected_amount = min(collected_amount, required_amount)
            missing = max(0, required_amount - collected_amount)
            percent = (collected_amount / required_amount * 100) if required_amount > 0 else 0
            
            details[item_name] = {
                "required": required_amount,
                "collected": collected_amount,
                "missing": missing,
                "percent": round(percent, 2)
            }
        
        total_missing = total_required - total_collected
        completion_percent = (total_collected / total_required * 100) if total_required > 0 else 0
        
        return {
            "completion_percent": round(completion_percent, 2),
            "required": total_required,
            "collected": total_collected,
            "missing": total_missing,
            "details": details,
            "status": "complete" if total_missing == 0 else "incomplete"
        }

    def get_recipe_completion_recursive(self, item_name: str, collected_items: Dict[str, int], depth: int = 0, max_depth: int = 10) -> Dict[str, Any]:
        """
        Calculate the total resources needed to craft an item, recursively breaking down
        into component recipes if needed (e.g., needing oak_log to make planks for crafting_table).
        
        Args:
            item_name: Name of the item to craft (e.g., "crafting_table")
            collected_items: Dictionary of items already collected
                            Example: {"oak_log": 2, "oak_planks": 1}
            depth: Current recursion depth (stops at max_depth to prevent infinite loops)
            max_depth: Maximum recursion depth (default: 10)
            
        Returns:
            Dictionary containing:
                - "completion_percent": Overall completion percentage (0-100)
                - "required": Total direct items needed
                - "collected": Total items already have
                - "missing": Total items still needed
                - "total_requirements": All items needed (recursive)
                - "details": Per-item breakdown (including components)
                - "status": "complete" / "incomplete"
                - "components": Breakdown of recipes needed for components
                
        Example:
            >>> lookup = MinecraftRecipeLookup("1.19.2")
            >>> collected = {"oak_log": 2}
            >>> completion = lookup.get_recipe_completion_recursive("crafting_table", collected)
            >>> print(completion)
            {
              "completion_percent": 50.0,
              "required": 4,
              "collected": 2,
              "missing": 2,
              "total_requirements": {"oak_log": 4},
              "details": {...},
              "status": "incomplete",
              "components": {...}
            }
        """
        if depth > max_depth:
            return {
                "error": f"Maximum recursion depth ({max_depth}) reached",
                "item_name": item_name,
                "depth": depth
            }
        
        # Get recipes for the item
        recipes = self.get_recipes_for_item(item_name.lower())
        if not recipes:
            return {
                "item_name": item_name,
                "completion_percent": 100.0 if collected_items.get(item_name, 0) > 0 else 0.0,
                "required": 0,
                "collected": collected_items.get(item_name, 0),
                "missing": 0,
                "status": "available" if collected_items.get(item_name, 0) > 0 else "no_recipe",
                "total_requirements": {},
                "details": {}
            }
        
        # Use the first recipe
        recipe = recipes[0]
        direct_requirements = self.get_recipe_requirements(recipe)
        
        # Total requirements (will accumulate recursively)
        total_requirements = {}
        component_details = {}
        details = {}
        
        # Process each direct requirement
        for req_item, req_amount in direct_requirements.items():
            collected_amount = collected_items.get(req_item, 0)
            missing_amount = max(0, req_amount - collected_amount)
            
            # Add to total requirements
            total_requirements[req_item] = total_requirements.get(req_item, 0) + req_amount
            
            # If we have a shortfall, try to find a recipe for this component
            if missing_amount > 0 and depth < max_depth:
                component_recipes = self.get_recipes_for_item(req_item.lower())
                if component_recipes:
                    # Recursively get requirements for this component
                    component_result = self.get_recipe_completion_recursive(
                        req_item,
                        collected_items,
                        depth + 1,
                        max_depth
                    )
                    
                    # Merge component requirements into total
                    if "total_requirements" in component_result:
                        for sub_item, sub_amount in component_result["total_requirements"].items():
                            # Calculate how many we need to craft
                            component_recipes_needed = missing_amount
                            total_requirements[sub_item] = total_requirements.get(sub_item, 0) + (sub_amount * component_recipes_needed)
                    
                    component_details[req_item] = component_result
            
            # Add to details
            details[req_item] = {
                "required": req_amount,
                "collected": collected_amount,
                "missing": missing_amount,
                "percent": round((collected_amount / req_amount * 100) if req_amount > 0 else 0, 2),
                "has_recipe": len(self.get_recipes_for_item(req_item.lower())) > 0
            }
        
        # Calculate overall completion based on total requirements
        total_required = sum(total_requirements.values())
        total_collected = sum(collected_items.get(item, 0) for item in total_requirements.keys())
        total_missing = total_required - total_collected
        
        overall_percent = (total_collected / total_required * 100) if total_required > 0 else 0
        
        return {
            "item_name": item_name,
            "completion_percent": round(overall_percent, 2),
            "required": sum(direct_requirements.values()),
            "collected": sum(min(collected_items.get(item, 0), direct_requirements[item]) for item in direct_requirements),
            "missing": sum(max(0, direct_requirements[item] - collected_items.get(item, 0)) for item in direct_requirements),
            "total_requirements": total_requirements,
            "total_collected": total_collected,
            "total_missing": total_missing,
            "details": details,
            "status": "complete" if total_missing == 0 else "incomplete",
            "components": component_details if component_details else None,
            "depth": depth
        }

    def format_shaped_recipe(self, recipe: Dict) -> str:
        """Format a shaped crafting recipe."""
        lines = ["Crafting Type: Shaped (grid-based)"]
        
        inShape = recipe.get("inShape", [])
        if inShape:
            lines.append("\nCrafting Pattern:")
            for row in inShape:
                row_items = []
                for item in row:
                    if item is None:
                        row_items.append("[    ]")
                    else:
                        row_items.append(f"[{self.format_item_ref(item):5}]")
                lines.append("  " + " ".join(row_items))
        
        result = recipe.get("result", {})
        lines.append(f"\nResult: {self.format_item_ref(result)}")
        
        return "\n".join(lines)

    def format_shapeless_recipe(self, recipe: Dict) -> str:
        """Format a shapeless crafting recipe."""
        lines = ["Crafting Type: Shapeless"]
        
        ingredients = recipe.get("ingredients", [])
        if ingredients:
            lines.append("\nIngredients needed:")
            for ing in ingredients:
                lines.append(f"  • {self.format_item_ref(ing)}")
        
        result = recipe.get("result", {})
        lines.append(f"\nResult: {self.format_item_ref(result)}")
        
        return "\n".join(lines)

    def display_recipe(self, recipe: Dict, recipe_num: int = 1) -> str:
        """Display a recipe in a readable format."""
        lines = [f"Recipe #{recipe_num}:"]
        
        if "inShape" in recipe:
            lines.append(self.format_shaped_recipe(recipe))
        elif "ingredients" in recipe:
            lines.append(self.format_shapeless_recipe(recipe))
        else:
            lines.append("(Unknown recipe format)")
            lines.append(json.dumps(recipe, indent=2))
        
        return "\n".join(lines)

    def list_items(self, limit: Optional[int] = None) -> str:
        """List available items."""
        items = sorted([item['name'] for item in self.items_by_id.values()])
        if limit:
            items = items[:limit]
        return "\n".join(f"  {item}" for item in items)

    def search_items(self, term: str, limit: int = 20) -> List[str]:
        """Search for items by name."""
        term = term.lower()
        matches = [
            item['name'] for item in self.items_by_id.values()
            if term in item['name'].lower()
        ]
        return sorted(list(set(matches)))[:limit]

    def get_all_items(self) -> List[str]:
        """
        Get a list of all available items in Minecraft.
        
        Returns:
            Sorted list of all item names (e.g., ["diamond_axe", "diamond_hoe", "diamond_pickaxe", ...])
            
        Example:
            >>> lookup = MinecraftRecipeLookup("1.19.2")
            >>> all_items = lookup.get_all_items()
            >>> print(len(all_items))  # Number of items
            >>> print(all_items[:5])   # First 5 items
        """
        return sorted([item['name'] for item in self.items_by_id.values()])

    def get_all_items_with_metadata(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available items with full metadata.
        
        Returns:
            Sorted list of item dictionaries containing:
                - id: Item ID number
                - name: Item identifier (e.g., "diamond_pickaxe")
                - displayName: Display name (e.g., "Diamond Pickaxe")
                - stackSize: Max stack size
                - Any other metadata from minecraft-data
                
        Example:
            >>> lookup = MinecraftRecipeLookup("1.19.2")
            >>> items = lookup.get_all_items_with_metadata()
            >>> print(items[0])
            {
                'id': 278,
                'name': 'diamond_pickaxe',
                'displayName': 'Diamond Pickaxe',
                'stackSize': 1,
                ...
            }
        """
        items = list(self.items_by_id.values())
        # Sort by name
        return sorted(items, key=lambda x: x.get('name', ''))

    def get_available_versions(self) -> List[str]:
        """Get list of available versions for this edition."""
        return sorted(self.data_paths.get(self.edition, {}).keys())

    def get_recipes_json(self, item_name: str, indent: int = 2) -> str:
        """
        Get all recipes for an item as a JSON string.
        
        Args:
            item_name: Name of the item (e.g., "stick", "crafting_table")
            indent: JSON indentation level (None for compact, default: 2)
            
        Returns:
            JSON string containing all recipes for the item, or error message
            
        Example:
            >>> lookup = MinecraftRecipeLookup("1.19.2")
            >>> json_str = lookup.get_recipes_json("stick")
            >>> print(json_str)
        """
        recipes = self.get_recipes_for_item(item_name)
        
        if not recipes:
            result = {
                "error": f"No recipes found for item: {item_name}",
                "item_name": item_name,
                "version": self.version,
                "edition": self.edition
            }
        else:
            result = {
                "item_name": item_name,
                "version": self.version,
                "edition": self.edition,
                "recipe_count": len(recipes),
                "recipes": recipes
            }
        
        return json.dumps(result, indent=indent)

    def get_recipe_json(self, item_name: str, recipe_index: int = 0, indent: int = 2) -> str:
        """
        Get a specific recipe for an item as a JSON string.
        
        Args:
            item_name: Name of the item (e.g., "stick", "crafting_table")
            recipe_index: Index of the recipe (0-based, default: 0)
            indent: JSON indentation level (None for compact, default: 2)
            
        Returns:
            JSON string containing a single recipe or error message
            
        Example:
            >>> lookup = MinecraftRecipeLookup("1.19.2")
            >>> json_str = lookup.get_recipe_json("stick", recipe_index=0)
            >>> print(json_str)
        """
        recipes = self.get_recipes_for_item(item_name)
        
        if not recipes:
            result = {
                "error": f"No recipes found for item: {item_name}",
                "item_name": item_name,
                "version": self.version,
                "edition": self.edition
            }
        elif recipe_index < 0 or recipe_index >= len(recipes):
            result = {
                "error": f"Recipe index {recipe_index} out of range. Item has {len(recipes)} recipes.",
                "item_name": item_name,
                "available_recipes": len(recipes),
                "version": self.version,
                "edition": self.edition
            }
        else:
            result = {
                "item_name": item_name,
                "recipe_index": recipe_index,
                "total_recipes": len(recipes),
                "version": self.version,
                "edition": self.edition,
                "recipe": recipes[recipe_index]
            }
        
        return json.dumps(result, indent=indent)



