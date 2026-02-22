"""
Smart Recipe-Aware Completion - Test Script
Demonstrates how the system now handles crafting chains
Example: oak_log → oak_planks → sticks
"""

from backend.utils.project_completion import ProjectCompletionCalculator


def test_smart_completion():
    """Test the recipe-aware completion calculation"""
    
    print("=" * 70)
    print("SMART RECIPE-AWARE PROJECT COMPLETION TEST")
    print("=" * 70)
    
    # Initialize calculator
    calculator = ProjectCompletionCalculator(version="1.19.2")
    
    # Example: Project that needs sticks
    example_project = {
        '_id': 'project_sticks',
        'project_name': 'Wooden Pickaxe',
        'final_item': 'wooden_pickaxe',
        'required_items': [
            {'name': 'oak_planks', 'quantity': 3},
            {'name': 'stick', 'quantity': 2}
        ],
        'owner_id': 'user_123',
        'world_name': 'Survival World'
    }
    
    # User has oak_logs (can be crafted to planks and sticks)
    example_inventory = {
        'oak_log': 4,      # Have logs, can make planks
        'oak_planks': 0,   # No planks yet
        'stick': 0         # No sticks yet
    }
    
    print("\n📋 PROJECT:")
    print(f"  Name: {example_project['project_name']}")
    print(f"  Requires:")
    for item in example_project['required_items']:
        print(f"    - {item['name']}: {item['quantity']}")
    
    print("\n📦 INVENTORY:")
    for item, qty in example_inventory.items():
        print(f"  - {item}: {qty}")
    
    print("\n🧪 TESTING RECIPE-AWARE CALCULATION...\n")
    
    # Test individual items
    print("Testing individual items:")
    print("-" * 70)
    
    # Test oak_planks
    print("\n✓ Testing oak_planks (need 3):")
    oak_planks_result = calculator.calculate_item_completion_with_recipes(
        'oak_planks',
        3,
        example_inventory
    )
    print(f"  Required: {oak_planks_result['required']}")
    print(f"  Direct inventory: {oak_planks_result['available_direct']}")
    print(f"  Can craft from available: {oak_planks_result['available_craftable']}")
    print(f"  Collected: {oak_planks_result['collected']}")
    print(f"  Status: {oak_planks_result['status']}")
    if oak_planks_result.get('crafting_notes'):
        print(f"  Crafting Notes:")
        for note in oak_planks_result['crafting_notes']:
            print(f"    {note}")
    
    # Test sticks
    print("\n✓ Testing sticks (need 2):")
    sticks_result = calculator.calculate_item_completion_with_recipes(
        'stick',
        2,
        example_inventory
    )
    print(f"  Required: {sticks_result['required']}")
    print(f"  Direct inventory: {sticks_result['available_direct']}")
    print(f"  Can craft from available: {sticks_result['available_craftable']}")
    print(f"  Collected: {sticks_result['collected']}")
    print(f"  Status: {sticks_result['status']}")
    if sticks_result.get('crafting_notes'):
        print(f"  Crafting Notes:")
        for note in sticks_result['crafting_notes']:
            print(f"    {note}")
    
    print("\n" + "=" * 70)
    print("TESTING RECIPE INGREDIENT LOOKUP")
    print("=" * 70)
    
    # Show what's needed to craft sticks
    print("\n📖 Recipe for sticks:")
    stick_recipe = calculator.get_recipe_ingredients('stick')
    if stick_recipe:
        print(f"  Ingredients needed:")
        for ingredient, qty in stick_recipe.items():
            print(f"    - {ingredient}: {qty}")
    else:
        print("  Recipe not found")
    
    # Show what's needed to craft oak planks
    print("\n📖 Recipe for oak_planks:")
    plank_recipe = calculator.get_recipe_ingredients('oak_planks')
    if plank_recipe:
        print(f"  Ingredients needed:")
        for ingredient, qty in plank_recipe.items():
            print(f"    - {ingredient}: {qty}")
    else:
        print("  Recipe not found")
    
    print("\n" + "=" * 70)
    print("TESTING CRAFTABILITY CHECK")
    print("=" * 70)
    
    # Check if we can craft sticks
    print("\n🔍 Can we craft sticks from oak_logs?")
    can_craft, craft_path = calculator.check_if_craftable('stick', example_inventory)
    print(f"  Result: {can_craft}")
    if craft_path:
        for step in craft_path:
            print(f"    {step}")
    
    # Check if we can craft oak planks
    print("\n🔍 Can we craft oak_planks from oak_logs?")
    can_craft, craft_path = calculator.check_if_craftable('oak_planks', example_inventory)
    print(f"  Result: {can_craft}")
    if craft_path:
        for step in craft_path:
            print(f"    {step}")
    
    print("\n" + "=" * 70)
    print("✅ SMART COMPLETION TEST COMPLETED")
    print("=" * 70)
    print("\n💡 Key Points:")
    print("  • Oak logs can be crafted into oak planks")
    print("  • Oak planks can be crafted into sticks")
    print("  • System recognizes this crafting chain")
    print("  • Shows progress even when intermediates aren't yet crafted")
    print("\n")


if __name__ == '__main__':
    try:
        test_smart_completion()
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        import traceback
        traceback.print_exc()
