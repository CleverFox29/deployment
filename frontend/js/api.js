/**
 * API Client for CraftChain
 * 
 * IMPORTANT: All data is fetched from server database only.
 * - NO localStorage for user data, worlds, or projects
 * - Only JWT token is stored in localStorage for authentication
 * - Worlds are stored in user's folder hierarchy (user_folders_collection)
 * - Projects are stored in projects collection
 * 
 * For local development: API_BASE_URL uses localhost:5000
 * For remote: Update API_BASE_URL to your computer's IP (e.g., http://192.168.1.5:5000/api)
 * Or set window.API_BASE_URL before loading this script
 */

// Auto-detect API URL
// - If on localhost, use localhost
// - Otherwise, use remote IP (update this if needed)
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:5000/api'
  : (window.API_BASE_URL || 'http://192.168.1.5:5000/api'); // Change 192.168.1.5 to your computer's IP

// Token management - Only stores JWT token, all user data fetched from server
const TokenManager = {
    getToken() {
        return localStorage.getItem('craftchain_token');
    },
    
    setToken(token) {
        localStorage.setItem('craftchain_token', token);
    },
    
    removeToken() {
        localStorage.removeItem('craftchain_token');
    },
    
    isAuthenticated() {
        return !!this.getToken();
    },
    
    // Get user ID from server via token validation (no local storage)
    async getUserId() {
        const profile = await AuthAPI.getProfile();
        return profile.user_id;
    }
};

// API Helper
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    const token = TokenManager.getToken();
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || `HTTP ${response.status}`);
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Authentication API - All user data fetched from server, nothing stored locally
const AuthAPI = {
    async signup(username, password) {
        const result = await apiCall('/auth/signup', 'POST', {
            username,
            password
        });
        // Only store token, not user data
        TokenManager.setToken(result.token);
        return result;
    },
    
    async login(username, password) {
        const result = await apiCall('/auth/login', 'POST', {
            username,
            password
        });
        // Only store token, not user data
        TokenManager.setToken(result.token);
        return result;
    },
    
    async getProfile() {
        return await apiCall('/auth/profile', 'GET');
    },
    
    // Get current user info from token (server-side validation)
    async getCurrentUser() {
        return await apiCall('/auth/me', 'GET');
    }
};

// Projects API
const ProjectsAPI = {
    async create(projectName, finalItem, requiredItems, worldName) {
        return await apiCall('/projects', 'POST', {
            project_name: projectName,
            final_item: finalItem,
            required_items: requiredItems,
            world_name: worldName
        });
    },
    
    async getAll(worldName = null) {
        const url = worldName ? `/projects?world_name=${encodeURIComponent(worldName)}` : '/projects';
        return await apiCall(url, 'GET');
    },
    
    async getById(projectId) {
        return await apiCall(`/projects/${projectId}`, 'GET');
    },
    
    async update(projectId, data) {
        return await apiCall(`/projects/${projectId}`, 'PUT', data);
    },
    
    async delete(projectId) {
        return await apiCall(`/projects/${projectId}`, 'DELETE');
    },
    
    async addCollaborator(projectId, collaboratorId) {
        return await apiCall(`/projects/${projectId}/add-collaborator`, 'POST', {
            collaborator_id: collaboratorId
        });
    },
    
    async getProgress(projectId) {
        return await apiCall(`/projects/${projectId}/progress`, 'GET');
    },
    
    // Worlds are loaded from user's folder hierarchy in database
    async listWorlds() {
        // Fetches worlds from user_folders_collection
        return await apiCall('/projects/worlds', 'GET');
    },
    
    async createWorld(worldName) {
        // Creates a new world in user's folder hierarchy
        return await apiCall('/projects/worlds', 'POST', {
            world_name: worldName
        });
    },
    
    async deleteWorld(worldName) {
        // Deletes a world from user's folder hierarchy
        return await apiCall(`/projects/worlds/${encodeURIComponent(worldName)}`, 'DELETE');
    },
    
    async getHierarchy() {
        // Fetches complete User → Worlds → Projects hierarchy from database
        return await apiCall('/projects/hierarchy', 'GET');
    }
};

// Contributions API
const ContributionsAPI = {
    async add(projectId, itemName, quantity, contributionType) {
        return await apiCall('/contributions', 'POST', {
            project_id: projectId,
            item_name: itemName,
            quantity: parseInt(quantity),
            contribution_type: contributionType
        });
    },
    
    async getByProject(projectId) {
        return await apiCall(`/contributions/project/${projectId}`, 'GET');
    },
    
    async getByUser(userId) {
        return await apiCall(`/contributions/user/${userId}`, 'GET');
    },
    
    async delete(contributionId) {
        return await apiCall(`/contributions/${contributionId}`, 'DELETE');
    }
};

// Activity API
const ActivityAPI = {
    async getProjectActivity(projectId, limit = 50) {
        return await apiCall(`/activity/project/${projectId}?limit=${limit}`, 'GET');
    },
    
    async getProjectStats(projectId) {
        return await apiCall(`/activity/project/${projectId}/stats`, 'GET');
    },
    
    async getProjectMilestones(projectId) {
        return await apiCall(`/activity/milestones/${projectId}`, 'GET');
    }
};

// Admin API
const AdminAPI = {
    async verifyHierarchy() {
        return await apiCall('/admin/verify-hierarchy', 'GET');
    },
    
    async getMyHierarchy() {
        return await apiCall('/admin/my-hierarchy', 'GET');
    }
};

// Utility
async function testConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}
