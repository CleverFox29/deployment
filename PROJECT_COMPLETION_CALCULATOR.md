# Project Completion Calculator

## Overview

The **Project Completion Calculator** automatically calculates project completion percentages based on a user's world inventory and the Minecraft recipes library. Instead of manually tracking "completed" items, the system compares required items against what's actually stored in the world inventory.

## Features

✅ Automatic completion calculation from inventory  
✅ Per-item breakdown showing required vs collected quantities  
✅ Color-coded progress (green = complete, blue = in progress, orange = not started)  
✅ Visual progress bars in project display  
✅ Recipe checking and requirements lookup  
✅ Multi-project completion calculations  
✅ Activity logging for all changes  

---

## Architecture

### Core Components

#### 1. **ProjectCompletionCalculator** (`backend/utils/project_completion.py`)

Main service class that handles all completion calculations.

**Key Methods:**

```python
# Get world inventory
inventory = calculator.get_world_inventory(user_id, world_name)

# Calculate single project completion
completion = calculator.calculate_project_completion(project, user_id, world_name)

# Calculate multiple projects
completions = calculator.calculate_projects_completion(projects, user_id, world_name)

# Check recipe for an item
recipe_info = calculator.get_recipe_requirements(item_name, inventory)
```

#### 2. **API Endpoints** (`backend/routes/projects.py`)

Three new endpoints for completion calculation:

**GET `/api/projects/<project_id>/completion`**
- Calculate completion for a single project
- Returns detailed item breakdown

**GET `/api/projects/world/<world_name>/completion`**
- Get completion for all projects in a world
- Useful for dashboard overview

**GET `/api/projects/<project_id>/recipe-check`**
- Check recipe requirements for a project's final item
- Helps users understand what's needed

#### 3. **Frontend Integration** (`js/dashboard.js`)

Updated project display to:
- Fetch completion data from API
- Display visual progress bar
- Show item breakdown in expandable details
- Color-code by status

---

## How It Works

### Completion Calculation Flow

```
User's Project
    ↓
Get Required Items [diamond: 3, stick: 2]
    ↓
Query World Inventory [diamond: 2, stick: 2, oak_planks: 5]
    ↓
Compare Required vs Available
    ├─ diamond: 2/3 (67%)
    ├─ stick: 2/2 (100%)
    ↓
Calculate Overall Progress
    └─ 4/5 items (80%)
```

### Data Flow

**Database:**
```
user_id: "user_123"
    ↓
inventory_collection
    ├─ diamond (qty: 2)
    ├─ stick (qty: 2)
    └─ oak_planks (qty: 5)
    
projects_collection
    ├─ Project 1: required_items: [{name: "diamond", quantity: 3}, ...]
    └─ Project 2: required_items: [{name: "stick", quantity: 2}, ...]
```

**API Response:**
```json
{
  "completion": {
    "project_id": "proj_123",
    "project_name": "Diamond Pickaxe",
    "overall_percent": 80.0,
    "total_required": 5,
    "total_collected": 4,
    "total_missing": 1,
    "status": "in_progress",
    "items": [
      {
        "item_name": "diamond",
        "required": 3,
        "collected": 2,
        "available": 2,
        "missing": 1,
        "percent": 66.67,
        "status": "incomplete"
      },
      {
        "item_name": "stick",
        "required": 2,
        "collected": 2,
        "available": 2,
        "missing": 0,
        "percent": 100.0,
        "status": "complete"
      }
    ]
  }
}
```

---

## Frontend Display

### Project Card with Completion

The dashboard now shows:

```
PROJECT: Diamond Pickaxe
├─ Final Item: diamond_pickaxe
├─ Status: in_progress
├─ Progress: 80% [████████░] 4/5 items
└─ Item Breakdown (expandable)
   ├─ ✅ diamond: 2/3
   ├─ ✅ stick: 2/2
   └─ ...
```

**Color Coding:**
- 🟢 **Green**: Complete (100%)
- 🔵 **Blue**: In Progress (1-99%)
- 🟠 **Orange**: Not Started (0%)

---

## Storage

### Inventory Collection

```json
{
  "_id": ObjectId("..."),
  "owner_id": "user_123",
  "world_name": "Survival World",
  "item_name": "diamond",
  "quantity": 2,
  "created_at": ISODate("2026-02-22T..."),
  "updated_at": ISODate("2026-02-22T...")
}
```

### Projects Collection (Already Existed)

```json
{
  "_id": ObjectId("..."),
  "project_name": "Diamond Pickaxe",
  "owner_id": "user_123",
  "world_name": "Survival World",
  "required_items": [
    {"name": "diamond", "quantity": 3},
    {"name": "stick", "quantity": 2}
  ],
  ...
}
```

---

## Usage Examples

### From Frontend (JavaScript)

```javascript
// Get single project completion
const completion = await getProjectCompletion(projectId);
console.log(completion.overall_percent); // 80.0

// Get all projects in a world
const completions = await getWorldProjectsCompletion(worldName);
completions.forEach(c => {
    console.log(`${c.project_name}: ${c.overall_percent}%`);
});
```

### From Backend (Python)

```python
from backend.utils.project_completion import ProjectCompletionCalculator

# Initialize
calculator = ProjectCompletionCalculator(version="1.19.2")

# Get inventory
inventory = calculator.get_world_inventory(user_id, world_name)

# Calculate single project
completion = calculator.calculate_project_completion(project, user_id, world_name)
print(f"Progress: {completion['overall_percent']}%")
print(f"Missing: {completion['total_missing']} items")

# Calculate multiple
completions = calculator.calculate_projects_completion(projects, user_id, world_name)
```

### From API (REST)

```bash
# Get single project completion
curl http://localhost:5000/api/projects/proj_123/completion \
  -H "Authorization: Bearer $TOKEN"

# Get world projects completion
curl http://localhost:5000/api/projects/world/SurvivalWorld/completion \
  -H "Authorization: Bearer $TOKEN"

# Check recipe requirements
curl http://localhost:5000/api/projects/proj_123/recipe-check \
  -H "Authorization: Bearer $TOKEN"
```

---

## Demo Script

Run the demo to see how everything works:

```bash
python demo_completion_calculator.py
```

Output:
```
============================================================
PROJECT COMPLETION CALCULATOR DEMO
============================================================

📋 PROJECT DETAILS:
  Project: Diamond Pickaxe
  Final Item: diamond_pickaxe
  World: Survival World

📦 INVENTORY:
  - diamond: 2
  - stick: 2
  - oak_planks: 5

🎯 REQUIRED ITEMS:
  - diamond: 3
  - stick: 2

⏳ CALCULATING COMPLETION...

✅ COMPLETION RESULTS:
  Overall Progress: 80.0%
  Total Required: 5 items
  Total Collected: 4 items
  Total Missing: 1 items
  Status: IN_PROGRESS

📊 ITEM BREAKDOWN:
  ✅ diamond:
     Required: 3
     Collected: 2
     Available: 2
     Missing: 1
     Progress: 66.67%
  ✅ stick:
     Required: 2
     Collected: 2
     Available: 2
     Missing: 0
     Progress: 100.0%
```

---

## Status Types

The calculator returns one of three statuses:

| Status | Condition | Color |
|--------|-----------|-------|
| `complete` | All items collected (missing = 0) | 🟢 Green |
| `in_progress` | Some items collected (0 < missing < required) | 🔵 Blue |
| `not_started` | No items collected yet (missing = required) | 🟠 Orange |

---

## Workflow

### For Users

1. **Add Items to Inventory**
   - Use the "📦 World Inventory" section
   - Add items as you collect them in Minecraft

2. **View Project Completion**
   - Dashboard automatically calculates from inventory
   - No manual updates needed
   - See visual progress bars

3. **Expand Item Breakdown**
   - Click "Item Breakdown" to see per-item status
   - Quickly identify what's missing

### For Developers

1. **Initialize Calculator**
   ```python
   calc = ProjectCompletionCalculator()
   ```

2. **Fetch Data**
   ```python
   inventory = calc.get_world_inventory(user_id, world_name)
   ```

3. **Calculate**
   ```python
   completion = calc.calculate_project_completion(project, user_id, world_name)
   ```

4. **Return Results**
   ```python
   return {'completion': completion}
   ```

---

## Files Modified/Created

**New Files:**
- `backend/utils/project_completion.py` - Main calculator class
- `demo_completion_calculator.py` - Demo/test script

**Modified Files:**
- `backend/routes/projects.py` - Added 3 completion endpoints
- `js/dashboard.js` - Added completion fetching and display logic
- `dashboard.html` - (no changes, uses existing structure)

---

## Future Enhancements

- ⭐ Recipe tree expansion (what items are needed to craft required items)
- 📊 Historical tracking (progress over time)
- 🎯 Milestone notifications
- 🔄 Auto-sync with Minecraft world (if connected to server)
- 📈 Statistics and analytics

---

## Troubleshooting

**Completion shows 0%?**
- Check that inventory items have names matching project required items
- Item names should be lowercase (e.g., "diamond" not "Diamond")

**Recipe lookup not working?**
- Ensure minecraft-data library is installed: `pip install -r requirements.txt`
- Check that Minecraft version is supported (1.19.2 recommended)

**Progress not updating?**
- Dashboard updates when you add/modify inventory items
- Refresh page if changes don't appear immediately

---

## API Reference

### GET `/api/projects/<project_id>/completion`

Get calculated completion for a specific project.

**Response:**
```json
{
  "completion": {
    "project_id": "...",
    "project_name": "Diamond Pickaxe",
    "final_item": "diamond_pickaxe",
    "world_name": "Survival World",
    "overall_percent": 80.0,
    "total_required": 5,
    "total_collected": 4,
    "total_missing": 1,
    "items": [...],
    "status": "in_progress"
  }
}
```

### GET `/api/projects/world/<world_name>/completion`

Get completion for all projects in a world.

**Response:**
```json
{
  "world_name": "Survival World",
  "projects": [
    { "overall_percent": 80.0, ... },
    { "overall_percent": 50.0, ... }
  ],
  "count": 2
}
```

### GET `/api/projects/<project_id>/recipe-check`

Check recipe details for a project's final item.

**Response:**
```json
{
  "project_id": "...",
  "final_item": "diamond_pickaxe",
  "recipe_info": {
    "item_name": "diamond_pickaxe",
    "recipes_available": true,
    "recipe_count": 1,
    "requirements": {...},
    "completion": {...}
  }
}
```

---

## Questions?

Refer to the demo script or examine the calculator tests for more examples.
