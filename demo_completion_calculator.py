"""
Project Completion Calculator - Test/Demo Script
Shows how to use the ProjectCompletionCalculator with inventory data
"""

from backend.utils.project_completion import ProjectCompletionCalculator
from backend.items.recipes import MinecraftRecipeLookup


def demo_project_completion():
    """Demonstrate project completion calculation"""
    
    print("=" * 60)
    print("PROJECT COMPLETION CALCULATOR DEMO")
    print("=" * 60)
    
    # Initialize calculator
    calculator = ProjectCompletionCalculator(version="1.19.2")
    
    # Example project data
    example_project = {
        '_id': 'project_123',
        'project_name': 'Diamond Pickaxe',
        'final_item': 'diamond_pickaxe',
        'required_items': [
            {'name': 'diamond', 'quantity': 3},
            {'name': 'stick', 'quantity': 2}
        ],
        'owner_id': 'user_123',
        'world_name': 'Survival World'
    }
    
    # Example inventory
    example_inventory = {
        'diamond': 2,        # Have 2 diamonds, need 3
        'stick': 2,          # Have 2 sticks, need 2 (complete!)
        'oak_planks': 5      # Extra items in inventory
    }
    
    print("\n📋 PROJECT DETAILS:")
    print(f"  Project: {example_project['project_name']}")
    print(f"  Final Item: {example_project['final_item']}")
    print(f"  World: {example_project['world_name']}")
    
    print("\n📦 INVENTORY:")
    for item, qty in example_inventory.items():
        print(f"  - {item}: {qty}")
    
    print("\n🎯 REQUIRED ITEMS:")
    for item in example_project['required_items']:
        print(f"  - {item['name']}: {item['quantity']}")
    
    # Calculate completion
    print("\n⏳ CALCULATING COMPLETION...\n")
    completion = calculator.calculate_project_completion(
        example_project,
        user_id='user_123',
        world_name='Survival World'
    )
    
    print("✅ COMPLETION RESULTS:")
    print(f"  Overall Progress: {completion['overall_percent']}%")
    print(f"  Total Required: {completion['total_required']} items")
    print(f"  Total Collected: {completion['total_collected']} items")
    print(f"  Total Missing: {completion['total_missing']} items")
    print(f"  Status: {completion['status'].upper()}")
    
    print("\n📊 ITEM BREAKDOWN:")
    for item in completion['items']:
        status_icon = "✅" if item['status'] == 'complete' else "⏳"
        print(f"  {status_icon} {item['item_name']}:")
        print(f"     Required: {item['required']}")
        print(f"     Collected: {item['collected']}")
        print(f"     Available: {item['available']}")
        print(f"     Missing: {item['missing']}")
        print(f"     Progress: {item['percent']}%")
    
    print("\n" + "=" * 60)


def demo_recipe_check():
    """Demonstrate recipe checking"""
    
    print("\n" + "=" * 60)
    print("RECIPE CHECK DEMO")
    print("=" * 60)
    
    calculator = ProjectCompletionCalculator(version="1.19.2")
    
    # Example: Check what we need to craft a crafting table
    final_item = "crafting_table"
    inventory = {
        'oak_planks': 3,      # Have 3, need 4
        'spruce_planks': 2    # Have 2, don't need
    }
    
    print(f"\n🔍 CHECKING RECIPE FOR: {final_item}")
    print(f"📦 Available Inventory: {inventory}")
    
    recipe_info = calculator.get_recipe_requirements(final_item, inventory)
    
    if recipe_info.get('error'):
        print(f"❌ Error: {recipe_info['error']}")
    elif not recipe_info.get('recipes_available'):
        print(f"❌ {recipe_info.get('message')}")
    else:
        print(f"\n✅ Recipes Found: {recipe_info['recipe_count']}")
        print(f"\n📋 Requirements:")
        for item, qty in recipe_info['requirements'].items():
            available = inventory.get(item.lower(), 0)
            print(f"  - {item}: need {qty}, have {available}")
        
        completion = recipe_info['completion']
        print(f"\n📊 Recipe Completion:")
        print(f"  Overall: {completion['completion_percent']}%")
        print(f"  Required: {completion['required']} items")
        print(f"  Available: {completion['collected']} items")
        print(f"  Missing: {completion['missing']} items")
        
        print(f"\n📋 Item Details:")
        for item_name, details in completion['details'].items():
            status = "✅" if details['missing'] == 0 else "⏳"
            print(f"  {status} {item_name}:")
            print(f"     Need: {details['required']}, Have: {details['collected']}, Missing: {details['missing']}")
    
    print("\n" + "=" * 60)


def demo_multi_project():
    """Demonstrate calculating completion for multiple projects"""
    
    print("\n" + "=" * 60)
    print("MULTI-PROJECT COMPLETION DEMO")
    print("=" * 60)
    
    calculator = ProjectCompletionCalculator(version="1.19.2")
    
    # Multiple projects in one world
    projects = [
        {
            '_id': 'proj_1',
            'project_name': 'Crafting Table',
            'final_item': 'crafting_table',
            'required_items': [
                {'name': 'oak_planks', 'quantity': 4}
            ],
            'owner_id': 'user_1',
            'world_name': 'SurvivalWorld'
        },
        {
            '_id': 'proj_2',
            'project_name': 'Wooden Pickaxe',
            'final_item': 'wooden_pickaxe',
            'required_items': [
                {'name': 'oak_planks', 'quantity': 3},
                {'name': 'stick', 'quantity': 2}
            ],
            'owner_id': 'user_1',
            'world_name': 'SurvivalWorld'
        }
    ]
    
    world_inventory = {
        'oak_planks': 5,
        'stick': 3
    }
    
    print(f"\n🌍 WORLD: SurvivalWorld")
    print(f"📦 Available Inventory:")
    for item, qty in world_inventory.items():
        print(f"  - {item}: {qty}")
    
    # Calculate for all projects
    user_id = 'user_1'
    world_name = 'SurvivalWorld'
    
    completions = calculator.calculate_projects_completion(
        projects,
        user_id,
        world_name
    )
    
    print(f"\n📊 PROJECT COMPLETIONS:")
    for completion in completions:
        status_emoji = "✅" if completion['status'] == 'complete' else "⏳"
        print(f"\n{status_emoji} {completion['project_name']}")
        print(f"   Progress: {completion['overall_percent']}%")
        print(f"   {completion['total_collected']}/{completion['total_required']} items")
        print(f"   Status: {completion['status']}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    # Run all demos
    try:
        demo_project_completion()
        demo_recipe_check()
        demo_multi_project()
        print("\n✨ All demos completed successfully!")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()
