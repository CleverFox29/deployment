# CraftChain - Minecraft Project Completion Calculator

A web application that helps Minecraft players set crafting goals and automatically track completion progress based on their world inventory.

## Overview

CraftChain is a full-stack application built for the Noobathon hackathon that enables Minecraft players to:
- Create projects with crafting goals
- Automatically calculate completion percentages based on world inventory
- Track required items vs collected items
- View activity logs and contribution history
- Manage multiple worlds and projects
- Set up enchantment goals and track progress

## Features

✅ **Automatic Completion Calculation** - Compares required items against world inventory  
✅ **Per-Item Breakdown** - Shows required vs collected quantities with color-coded progress  
✅ **Multi-Project Management** - Create and track multiple projects per world  
✅ **World Hierarchy** - Organize projects by Minecraft worlds  
✅ **Activity Logging** - Track all changes and contributions  
✅ **Recipe Library** - Integration with Minecraft recipes database  
✅ **User Authentication** - Secure login and account management  
✅ **Visual Progress Bars** - See completion status at a glance  

## Prerequisites

- **Python 3.8+**
- **MongoDB Account** (free tier at mongodb.com)
- **Node.js** (optional, for frontend dependencies)
- **A web browser** (modern browser recommended)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd N-Cubed
```

### 2. Create a Python Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

That's it! No database configuration needed for testing.

### Optional: Use Your Own MongoDB
To use your own MongoDB instead of the pre-configured one:
1. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` with your MongoDB credentials:
   ```
   MONGODB_URI=mongodb+srv://your_username:your_password@cluster0.xxx.mongodb.net/?appName=Cluster0
   SECRET_KEY=your-secret-key-change-this-in-production
   API_PORT=5000
   API_HOST=0.0.0.0
   FLASK_DEBUG=True
   CLEAR_DB_TOKEN=your-admin-token-here
   ```
3. Get MongoDB URI from [mongodb.com](https://mongodb.com)

## Running the Application

### Quick Start (No MongoDB Setup Required)
The application comes with a pre-configured MongoDB database. Just run:

```bash
python -m backend.app
```

The API and frontend will start on `http://localhost:5000`

### Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

The frontend (index.html) will load automatically along with all CSS and JavaScript assets.

### Using Your Own MongoDB (Optional)
If you want to use your own MongoDB instance:
1. Create a `.env` file in the root directory
2. Add your MongoDB URI: `MONGODB_URI=mongodb+srv://...`
3. Run the app - it will use your database instead

## Project Structure

```
N-Cubed/
├── backend/                    # Flask API server
│   ├── app.py                 # Main Flask application
│   ├── db.py                  # MongoDB connection and initialization
│   ├── models/
│   │   └── models.py          # Database models
│   ├── routes/                # API endpoints
│   │   ├── auth.py            # User authentication
│   │   ├── projects.py        # Project management
│   │   ├── items.py           # Item/recipe management
│   │   ├── inventory.py       # World inventory
│   │   ├── contributions.py   # Contributions tracking
│   │   ├── activity.py        # Activity logs
│   │   ├── admin.py           # Admin utilities
│   │   └── __init__.py
│   ├── items/                 # Minecraft items and recipes
│   │   ├── recipes.py         # Recipe expansion logic
│   │   └── main.py
│   └── utils/
│       ├── auth.py            # JWT and auth utilities
│       └── project_completion.py  # Completion calculation logic
├── frontend/                  # Frontend assets
│   ├── css/
│   └── js/
├── css/                       # Stylesheets
├── js/                        # JavaScript files
├── index.html                 # Main page
├── login.html                 # Login page
├── signup.html                # Signup page
├── dashboard.html             # Dashboard
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Create new user account
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /me` - Get current user info

### Projects (`/api/projects`)
- `GET /` - List all user projects
- `POST /` - Create new project
- `GET /<project_id>` - Get project details
- `PUT /<project_id>` - Update project
- `DELETE /<project_id>` - Delete project
- `GET /<project_id>/completion` - Get completion status

### Items (`/api/items`)
- `GET /recipes` - Get available recipes
- `GET /search` - Search items by name
- `GET /expand` - Expand items into recipes

### Inventory (`/api/inventory`)
- `GET /<world_name>` - Get world inventory
- `POST /<world_name>/items` - Add item to inventory
- `PUT /<world_name>/items/<item_name>` - Update item quantity
- `DELETE /<world_name>/items/<item_name>` - Remove item

### Activity (`/api/activity`)
- `GET /` - Get activity feed
- `GET /user/<user_id>` - Get user activity

### Admin (`/api/admin`)
- `POST /clear-db` - Clear database (requires token)

## Database Structure

### Collections

**users** - User account information
- Username, password hash, role, creation date

**user_folders** - User's world hierarchy
- Associates users with their worlds

**projects** - Crafting projects
- Project name, final item, owner, world, required items

**inventory** - World inventory items
- Item name, quantity, world name

**contributions** - User contributions to projects
- User ID, project ID, item, quantity

**activity_log** - Activity feed
- User actions and changes

**enchantments** - Enchantment tracking
- Enchantment types and levels

See [DATABASE_STRUCTURE.md](./backend/DATABASE_STRUCTURE.md) for detailed schema.

## Troubleshooting

### Port Already in Use
Change the API port in `.env`:
```
API_PORT=5001
```
Then run the app again.

### Module Not Found Errors
Ensure virtual environment is activated and dependencies installed:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### CORS Errors
The backend is configured to accept requests from the frontend. If issues persist, check `backend/app.py` CORS configuration.

### Database Issues
If the pre-configured MongoDB database is unavailable, create your own:
1. Create `.env` file with your MongoDB URI (see Installation section)
2. Restart the application

## Development

### Adding New API Endpoints
1. Create a new route file in `backend/routes/`
2. Define your Blueprint
3. Register it in `backend/app.py`

### Modifying Database Models
Update `backend/models/models.py` and ensure MongoDB collections exist via `backend/db.py`

### Testing
Run test files included:
```bash
python test_smart_completion.py
python test_recipe_expansion.py
python demo_completion_calculator.py
```

## Contributing

This project was built as part of the Noobathon hackathon. For contributions or questions, please reach out to the development team.

## License

This project is submitted for Noobathon hackathon evaluation.

## Contact

For questions or issues, please contact the CraftChain development team.

---

**Last Updated:** February 2026
