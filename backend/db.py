"""
MongoDB Database Connection & Collection Management

Database Structure: User → World → Project Hierarchy
------------------------------------------------------
CraftChain stores data in a hierarchical structure:

1. USERS (users collection)
   - Each user has a unique _id
   
2. USER FOLDERS (user_folders_collection)
   - Stores user's folder hierarchy including worlds
   - Each user has one folder document with their worlds list
   
3. WORLDS (stored in user_folders_collection)
   - Each user can have multiple worlds (e.g., "Survival", "Creative")
   - Worlds are explicitly created and stored in folder hierarchy
   - Empty worlds can exist (without projects)
   
4. PROJECTS (projects collection)
   - Each project belongs to ONE user (owner_id)
   - Each project belongs to ONE world (world_name)
   - Projects contain crafting goals and required items

Storage Example in MongoDB:
---------------------------
user_folders collection:
{
  "_id": ObjectId("..."),
  "user_id": "user123",
  "worlds": [
    { "name": "Survival", "created_at": ISODate("...") },
    { "name": "Creative", "created_at": ISODate("...") }
  ],
  "created_at": ISODate("...")
}

projects collection:
{
  "_id": ObjectId("..."),
  "owner_id": "user123",           // Links to user
  "world_name": "Survival",        // Links to world in user's folder
  "project_name": "Diamond Pickaxe",
  "final_item": "diamond_pickaxe",
  "required_items": [...],
  ...
}

Query Examples:
--------------
- Get user's folder: user_folders_collection.find_one({user_id: 'user123'})
- Get all worlds for user: folder['worlds']
- Get projects in world: projects_collection.find({owner_id: 'user123', world_name: 'Survival'})

IMPORTANT: Use folder hierarchy to find what worlds the user has.
           Worlds are stored in user_folders_collection.
"""
import os
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

# Connection URI - can be read from .env or use default
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://cleverfox2305:ncubed333@cluster0.zvtbmvc.mongodb.net/?appName=Cluster0"
)

# Create MongoDB Client
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

# Database and Collections
db = client.craftchain

# Collections
users_collection = db.users
projects_collection = db.projects
contributions_collection = db.contributions
enchantments_collection = db.enchantments
enchanted_items_collection = db.enchanted_items
activity_log_collection = db.activity_log  # For activity feed
user_folders_collection = db.user_folders  # Simple per-user folder metadata
inventory_collection = db.inventory  # World inventory items


def ensure_user_folder(user_id: str) -> None:
    """Ensure a simple metadata folder document exists for the user."""
    now = datetime.utcnow()
    user_folders_collection.update_one(
        {'user_id': user_id},
        {
            '$setOnInsert': {
                'user_id': user_id,
                'worlds': [],  # Stores world hierarchy
                'created_at': now,
            }
        },
        upsert=True,
    )


def ensure_world_folder(user_id: str, world_name: str) -> bool:
    """Create a world entry in user's folder if it doesn't exist."""
    ensure_user_folder(user_id)
    result = user_folders_collection.update_one(
        {'user_id': user_id, 'worlds.name': {'$ne': world_name}},
        {
            '$push': {
                'worlds': {
                    'name': world_name,
                    'created_at': datetime.utcnow(),
                }
            }
        },
    )
    return result.modified_count > 0


def get_user_worlds(user_id: str) -> list:
    """
    Get all worlds for a user from their folder hierarchy.
    Uses user_folders_collection to find worlds.
    """
    user_folder = user_folders_collection.find_one({'user_id': user_id})
    if user_folder:
        return user_folder.get('worlds', [])
    return []


def get_world_projects(user_id: str, world_name: str) -> list:
    """Get all projects for a specific world."""
    return list(projects_collection.find({
        'owner_id': user_id,
        'world_name': world_name
    }).sort('created_at', -1))


def get_user_hierarchy(user_id: str) -> dict:
    """
    Get complete User → Worlds → Projects hierarchy from database.
    Returns the hierarchical structure stored in MongoDB.
    """
    # Get all projects for user (owned or collaborated)
    projects = list(projects_collection.find({
        '$or': [
            {'owner_id': user_id},
            {'collaborators': user_id}
        ]
    }).sort([('world_name', 1), ('created_at', -1)]))
    
    # Group projects by world
    hierarchy = {}
    for project in projects:
        world_name = project.get('world_name', 'Unknown')
        if world_name not in hierarchy:
            hierarchy[world_name] = []
        hierarchy[world_name].append(project)
    
    return {
        'user_id': user_id,
        'worlds': [
            {
                'world_name': world,
                'project_count': len(projects),
                'projects': projects
            }
            for world, projects in hierarchy.items()
        ],
        'total_worlds': len(hierarchy),
        'total_projects': len(projects)
    }


def verify_hierarchy_storage() -> dict:
    """
    Verify that the database properly stores the User → World → Project hierarchy.
    Returns statistics about the hierarchical structure.
    """
    stats = {
        'total_users': users_collection.count_documents({}),
        'total_projects': projects_collection.count_documents({}),
        'total_worlds': len(projects_collection.distinct('world_name')),
        'sample_structure': []
    }
    
    # Get sample of users and their hierarchies
    sample_users = list(users_collection.find().limit(3))
    for user in sample_users:
        user_id = str(user['_id'])
        worlds = projects_collection.distinct('world_name', {'owner_id': user_id})
        
        user_structure = {
            'username': user.get('username'),
            'user_id': user_id,
            'worlds': []
        }
        
        for world in worlds:
            project_count = projects_collection.count_documents({
                'owner_id': user_id,
                'world_name': world
            })
            project_names = [
                p['project_name'] 
                for p in projects_collection.find(
                    {'owner_id': user_id, 'world_name': world}
                ).limit(5)
            ]
            user_structure['worlds'].append({
                'world_name': world,
                'project_count': project_count,
                'sample_projects': project_names
            })
        
        stats['sample_structure'].append(user_structure)
    
    return stats


def drop_user_folder(user_id: str) -> None:
    """Remove the user's folder metadata document."""
    user_folders_collection.delete_one({'user_id': user_id})


def create_world(user_id: str, world_name: str) -> dict:
    """Create a new world in user's folder hierarchy."""
    world_name = world_name.strip()
    if not world_name:
        raise ValueError("World name cannot be empty")
    
    ensure_user_folder(user_id)
    
    # Check if world already exists
    user_folder = user_folders_collection.find_one({
        'user_id': user_id,
        'worlds.name': world_name
    })
    
    if user_folder:
        raise ValueError(f"World '{world_name}' already exists")
    
    # Add world to user's folder
    world_entry = {
        'name': world_name,
        'created_at': datetime.utcnow(),
    }
    
    user_folders_collection.update_one(
        {'user_id': user_id},
        {'$push': {'worlds': world_entry}}
    )
    
    return world_entry


def delete_world(user_id: str, world_name: str) -> bool:
    """
    Delete a world from user's folder hierarchy.
    Cascade deletes all projects in the world, their contributions, and activity logs.
    """
    # Find all projects in this world
    projects_in_world = list(projects_collection.find({
        'owner_id': user_id,
        'world_name': world_name
    }))
    
    # Delete contributions and activity logs for each project
    for project in projects_in_world:
        project_id = str(project['_id'])
        
        # Delete contributions
        contributions_collection.delete_many({
            'project_id': project_id
        })
        
        # Delete activity logs
        activity_log_collection.delete_many({
            'project_id': project_id
        })
    
    # Delete all projects in this world
    projects_collection.delete_many({
        'owner_id': user_id,
        'world_name': world_name
    })
    
    # Delete world from user's folder
    result = user_folders_collection.update_one(
        {'user_id': user_id},
        {'$pull': {'worlds': {'name': world_name}}}
    )
    
    return result.modified_count > 0


def clear_database():
    """Remove all documents from every application collection."""
    collections = {
        "users": users_collection,
        "projects": projects_collection,
        "contributions": contributions_collection,
        "enchantments": enchantments_collection,
        "enchanted_items": enchanted_items_collection,
        "activity_log": activity_log_collection,
    }

    result = {}
    for name, collection in collections.items():
        try:
            delete_result = collection.delete_many({})
            result[name] = delete_result.deleted_count
        except Exception as exc:  # Best-effort; record failure per collection
            result[name] = f"error: {exc}"
    return result

# Test connection
def test_connection():
    """Test MongoDB connection"""
    try:
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB!")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        return False

# Create indexes for better query performance
def create_indexes():
    """Create database indexes for hierarchical User → World → Project structure"""
    try:
        # Users
        # Email index removed - authentication is username-only
        users_collection.create_index("username", unique=True)
        
        # Projects - Hierarchical indexes for User → World → Project structure
        projects_collection.create_index("owner_id")
        projects_collection.create_index("world_name")
        projects_collection.create_index([("owner_id", 1), ("world_name", 1)])  # User → World lookup
        projects_collection.create_index([("owner_id", 1), ("world_name", 1), ("created_at", -1)])  # Sorted projects in world
        projects_collection.create_index("collaborators")  # For shared projects
        projects_collection.create_index("created_at")
        
        # Contributions
        contributions_collection.create_index("project_id")
        contributions_collection.create_index("user_id")
        contributions_collection.create_index([("project_id", 1), ("user_id", 1)])
        contributions_collection.create_index("created_at")
        
        # Activity Log
        activity_log_collection.create_index("project_id")
        activity_log_collection.create_index("created_at")
        
        # User Folders - for world metadata
        user_folders_collection.create_index("user_id", unique=True)
        
        print("✓ Database indexes created successfully!")
        print("  - User → World → Project hierarchy indexes enabled")
    except Exception as e:
        print(f"✗ Error creating indexes: {e}")

# Initialize database on startup
def init_db():
    """Initialize database connection and indexes"""
    if test_connection():
        create_indexes()
        return True
    return False

if __name__ == "__main__":
    init_db()