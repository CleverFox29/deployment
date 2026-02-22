from recipes import MinecraftRecipeLookup
import json


lookup = MinecraftRecipeLookup("1.19.2")

# Example: Diamond sword - partial collection
item = "diamond_sword"
print("\n" + "="*60)
print(f"Example: {item}")
print("="*60)
recipes = lookup.get_recipes_for_item(item) # Find the recipe
if recipes:
    recipe = recipes[0]
    requirements = lookup.get_recipe_requirements(recipe) # Print the requirements
    print(f"Requirements: {requirements}")
    
    # Partial collection
    collected = {"diamond": 2, "": 1}
    completion = lookup.get_recipe_completion_recursive(item, collected) # Get percentage completion (pass item name, not recipe)
    print(f"\nCompletion Status:")
    print(json.dumps(completion, indent=2))
else:
    print(f"No recipes found for {item}")