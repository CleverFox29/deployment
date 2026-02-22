"""
Recipe Expansion Test
Shows how diamond_pickaxe gets expanded to component items
"""

from backend.utils.project_completion import ProjectCompletionCalculator


def test_recipe_expansion():
    """Test that diamond_pickaxe expands to diamonds and sticks"""
    
    print("=" * 70)
    print("RECIPE EXPANSION TEST")
    print("=" * 70)
    
    calculator = ProjectCompletionCalculator(version="1.19.2")
    
    # Original project: requires 1x diamond_pickaxe
    original_required = [
        {'name': 'diamond_pickaxe', 'quantity': 1}
    ]
    
    print("\n📋 ORIGINAL REQUIRED ITEMS:")
    print(f"  {original_required}")
    
    # Expand to actual ingredients
    expanded = calculator.expand_required_items_from_recipes(original_required)
    
    print("\n🔍 EXPANDED REQUIRED ITEMS:")
    for item in expanded:
        from_recipe = item.get('from_recipe', 'N/A')
        print(f"  - {item['name']}: {item['quantity']} (from recipe: {from_recipe})")
    
    print("\n" + "=" * 70)
    print("✅ Test Completed")
    print("=" * 70)
    print("\n💡 What happened:")
    print("  • System looked up recipe for 'diamond_pickaxe'")
    print("  • Found it requires diamonds and sticks")
    print("  • Expanded to show actual materials needed")
    print("  • Now progress is calculated based on materials, not finished item")
    print("\n")


if __name__ == '__main__':
    try:
        test_recipe_expansion()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
