from recipes import MinecraftRecipeLookup


lookup = MinecraftRecipeLookup("1.19.2")
recipes = lookup.get_recipes_for_item("diamond_sword")
if recipes:
    requirements = lookup.get_recipe_requirements(recipes[0])
    print(requirements)

recipes = lookup.get_recipes_for_item("crafting_table")
if recipes:
    requirements = lookup.get_recipe_requirements(recipes[0])
    print(requirements)  # Output: {"oak_planks": 4}