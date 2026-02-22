# CraftChain Database Structure

## Hierarchical Storage: User → World → Project

CraftChain uses **MongoDB** to store data in a hierarchical structure where each user can have multiple worlds, and each world can contain multiple projects.

---

## 📊 Database Collections

### 1. **users** Collection
Stores user account information.

```json
{
  "_id": ObjectId("65f1a2b3c4d5e6f7g8h9i0j1"),
  "username": "steve123",
  "password_hash": "$2b$12$...",
  "role": "player",
  "created_at": ISODate("2026-02-22T10:00:00Z")
}
```

---

### 2. **user_folders** Collection
Stores user's folder hierarchy including worlds.

```json
{
  "_id": ObjectId("65f1a2b3c4d5e6f7g8h9i0j9"),
  "user_id": "65f1a2b3c4d5e6f7g8h9i0j1",
  "worlds": [
    {
      "name": "Survival World",
      "created_at": ISODate("2026-02-22T09:00:00Z")
    },
    {
      "name": "Creative Build",
      "created_at": ISODate("2026-02-22T11:00:00Z")
    }
  ],
  "created_at": ISODate("2026-02-22T09:00:00Z")
}
```

**Key Points:**
- Worlds are stored in the user's folder document
- Each user has ONE folder document
- Worlds can exist independently (even without projects)
- Use folder hierarchy to find what worlds the user has

---

### 3. **projects** Collection
Stores projects with hierarchical structure via `owner_id` and `world_name` fields.

```json
{
  "_id": ObjectId("65f1a2b3c4d5e6f7g8h9i0j2"),
  "project_name": "Diamond Pickaxe",
  "final_item": "diamond_pickaxe",
  "owner_id": "65f1a2b3c4d5e6f7g8h9i0j1",  // Links to user
  "world_name": "Survival World",           // Links to world in user's folder
  "required_items": [
    {"name": "Diamond", "quantity": 3, "completed": 2},
    {"name": "Stick", "quantity": 2, "completed": 2}
  ],
  "collaborators": ["65f1a2b3c4d5e6f7g8h9i0j1"],
  "status": "active",
  "created_at": ISODate("2026-02-22T10:30:00Z"),
  "updated_at": ISODate("2026-02-22T12:00:00Z")
}
```

**Key Fields for Hierarchy:**
- `owner_id`: Links project to a specific user
- `world_name`: Links project to a world in user's folder hierarchy (must exist in user_folders)

---

### 4. **contributions** Collection
Tracks item contributions to projects.

```json
{
  "_id": ObjectId("65f1a2b3c4d5e6f7g8h9i0j3"),
  "project_id": "65f1a2b3c4d5e6f7g8h9i0j2",
  "user_id": "65f1a2b3c4d5e6f7g8h9i0j1",
  "item_name": "Diamond",
  "quantity": 2,
  "contribution_type": "collected",
  "created_at": ISODate("2026-02-22T11:00:00Z"),
  "verified": false
}
```

---

## 🔍 How the Hierarchy Works

### Structure Visualization

```
User: steve123 (ID: 65f1a2b3...)
├── Folder Document (user_folders)
│   ├── World: "Survival World" (stored in folder)
│   └── World: "Creative Build" (stored in folder)
│
└── Projects (projects collection)
    ├── Project: "Diamond Pickaxe" (world_name: "Survival World")
    ├── Project: "Beacon" (world_name: "Survival World")
    ├── Project: "Netherite Armor" (world_name: "Survival World")
    ├── Project: "Castle" (world_name: "Creative Build")
    └── Project: "Redstone Farm" (world_name: "Creative Build")
```

**IMPORTANT:** Worlds are stored in user_folders_collection. Use the folder hierarchy to find what worlds the user has.

### Database Storage

**user_folders_collection:**
```javascript
// User's folder document
{
  user_id: "65f1a2b3...",
  worlds: [
    { name: "Survival World", created_at: ISODate("...") },
    { name: "Creative Build", created_at: ISODate("...") }
  ],
  created_at: ISODate("...")
}
```

**projects_collection:**
```javascript
// Project 1
{ owner_id: "65f1a2b3...", world_name: "Survival World", project_name: "Diamond Pickaxe" }

// Project 2
{ owner_id: "65f1a2b3...", world_name: "Survival World", project_name: "Beacon" }

// Project 3
{ owner_id: "65f1a2b3...", world_name: "Survival World", project_name: "Netherite Armor" }

// Project 4
{ owner_id: "65f1a2b3...", world_name: "Creative Build", project_name: "Castle" }

// Project 5
{ owner_id: "65f1a2b3...", world_name: "Creative Build", project_name: "Redstone Farm" }
```

---

## 📝 Query Examples

### Get user's folder:
```python
user_folder = user_folders_collection.find_one({'user_id': user_id})
```

### Get all worlds for a user:
```python
worlds = user_folder.get('worlds', [])
# Returns: [
#   { "name": "Survival World", "created_at": ... },
#   { "name": "Creative Build", "created_at": ... }
# ]
```

### Get all projects in a specific world:
```python
projects = projects_collection.find({
    'owner_id': user_id,
    'world_name': 'Survival World'
}).sort('created_at', -1)
```

### Create a new world:
```python
user_folders_collection.update_one(
    {'user_id': user_id},
    {'$push': {'worlds': {'name': world_name, 'created_at': datetime.utcnow()}}}
)
```

### Get complete hierarchy:
```python
hierarchy = get_user_hierarchy(user_id)
# Returns organized structure:
# {
#   'user_id': '...',
#   'worlds': [
#     {
#       'world_name': 'Survival World',
#       'created_at': '...',
#       'projects': [...]
#     },
#     {
#       'world_name': 'Creative Build',
#       'created_at': '...',
#       'projects': [...]
#     }
#   ]
# }
```

---

## 🔑 Database Indexes

Optimized indexes for hierarchical queries:

```python
# Single field indexes
projects.create_index("owner_id")
projects.create_index("world_name")

# Compound indexes for User → World hierarchy
projects.create_index([("owner_id", 1), ("world_name", 1)])
projects.create_index([("owner_id", 1), ("world_name", 1), ("created_at", -1)])
```

These indexes make hierarchy queries extremely fast, even with millions of projects.

---

## 🛠️ API Endpoints

### Create World (Stores in user_folders_collection)
```http
POST /api/projects/worlds
Authorization: Bearer <token>
Content-Type: application/json

{
  "world_name": "Survival World"
}
```

### List Worlds (From user_folders_collection)
```http
GET /api/projects/worlds
Authorization: Bearer <token>
```

### Delete World (From user_folders_collection)
```http
DELETE /api/projects/worlds/Survival%20World
Authorization: Bearer <token>
```

### Create Project (Stores in projects_collection)
```http
POST /api/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_name": "Diamond Pickaxe",
  "final_item": "diamond_pickaxe",
  "world_name": "Survival World",
  "required_items": [...]
}
```

### Get User's Hierarchy (From Both Collections)
```http
GET /api/projects/hierarchy
Authorization: Bearer <token>
```

### Get Projects in a World
```http
GET /api/projects?world_name=Survival%20World
Authorization: Bearer <token>
```

### Verify Database Structure
```http
GET /api/admin/verify-hierarchy
```

---

## ✅ Data Persistence Guarantee

1. **All data is stored in MongoDB Atlas cloud database**
2. **No client-side storage** (except JWT token for authentication)
3. **Worlds are stored in user_folders_collection** - Use folder hierarchy to find user's worlds
4. **Projects are stored in projects_collection** - Linked to worlds via world_name field
5. **Hierarchical structure maintained via two collections:**
   - user_folders: stores worlds
   - projects: stores projects with world_name references
6. **Database indexes ensure fast hierarchical queries**
7. **Worlds can exist independently** - Empty worlds are allowed
8. **No localStorage or sessionStorage for user data, worlds, or projects**
9. **World management:**
   - Create worlds explicitly via POST /api/projects/worlds
   - Delete empty worlds via DELETE /api/projects/worlds/{name}
   - Cannot delete worlds that have projects

---

## 🧪 Testing the Structure

You can verify the database structure is working by:

1. **Create a user** via `/api/auth/signup`
2. **Create projects in different worlds**:
   - Project in "Survival" world
   - Project in "Creative" world
3. **Query the hierarchy** via `/api/projects/hierarchy`
4. **Verify in MongoDB Atlas** - check the `projects` collection

The database will show all projects with their `owner_id` and `world_name` fields, demonstrating the hierarchical storage.
