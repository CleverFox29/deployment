/**
 * CraftChain Frontend - Main Application
 * 
 * IMPORTANT: All user data is fetched from server and stored in memory only.
 * Only the JWT token is persisted in localStorage.
 * User data (currentUser, currentProject) is session-only and cleared on page refresh.
 */

// Global state - Session only (not persisted to localStorage)
let currentUser = null;  // Fetched from server via token
let currentProject = null;  // Fetched from server

// Page Navigation
function navigateTo(pageName) {
    // Hide all pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.style.display = 'none');
    
    // Show selected page
    const page = document.getElementById(pageName);
    if (page) {
        page.style.display = 'block';
        
        // Load data based on page
        if (pageName === 'dashboard') {
            loadDashboard();
        } else if (pageName === 'projects') {
            loadProjects();
        } else if (pageName === 'profile') {
            loadProfile();
        }
    }
    
    // Update navbar
    updateNavbar();
}

// Update navigation bar based on auth status
function updateNavbar() {
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const profileLink = document.getElementById('profileLink');
    
    if (TokenManager.isAuthenticated()) {
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'block';
        profileLink.style.display = 'block';
    } else {
        loginBtn.style.display = 'block';
        logoutBtn.style.display = 'none';
        profileLink.style.display = 'none';
    }
}

// ===== Authentication =====
async function login() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    const errorMsg = document.getElementById('loginError');
    
    if (!email || !password) {
        errorMsg.textContent = 'Please enter email and password';
        return;
    }
    
    try {
        const result = await AuthAPI.login(email, password);
        currentUser = result;
        errorMsg.textContent = '';
        document.getElementById('loginEmail').value = '';
        document.getElementById('loginPassword').value = '';
        navigateTo('dashboard');
    } catch (error) {
        errorMsg.textContent = error.message;
    }
}

async function signup() {
    const username = document.getElementById('signupUsername').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const errorMsg = document.getElementById('signupError');
    
    if (!username || !email || !password) {
        errorMsg.textContent = 'Please fill all fields';
        return;
    }
    
    try {
        const result = await AuthAPI.signup(username, email, password);
        currentUser = result;
        errorMsg.textContent = '';
        document.getElementById('signupUsername').value = '';
        document.getElementById('signupEmail').value = '';
        document.getElementById('signupPassword').value = '';
        navigateTo('dashboard');
    } catch (error) {
        errorMsg.textContent = error.message;
    }
}

function logout() {
    // Only remove token - no user data stored locally
    TokenManager.removeToken();
    currentUser = null;
    currentProject = null;
    navigateTo('login');
}

// ===== Auth Tab Switching =====
function switchAuthTab(tabName) {
    // Hide all auth forms
    const forms = document.querySelectorAll('.auth-form');
    forms.forEach(form => form.classList.remove('active'));
    
    // Show selected form
    document.getElementById(tabName).classList.add('active');
    
    // Update tab buttons
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    event.target.classList.add('active');
}

// ===== Dashboard =====
async function loadDashboard() {
    try {
        // Ensure we have current user info (fetched from server via token)
        if (!currentUser) {
            currentUser = await AuthAPI.getCurrentUser();
        }
        
        const result = await ProjectsAPI.getAll();
        const projects = result.projects || [];
        
        // Update stats
        document.getElementById('activeProjectsCount').textContent = projects.length;
        
        // Load all contributions for user
        try {
            const contribResult = await ContributionsAPI.getByUser(currentUser.user_id);
            const contributions = contribResult.contributions || [];
            document.getElementById('totalContributionsCount').textContent = contributions.length;
            
            // Count completed items
            let completedCount = 0;
            for (const contrib of contributions) {
                completedCount += contrib.quantity;
            }
            document.getElementById('itemsCompletedCount').textContent = completedCount;
        } catch (e) {
            console.log('Could not load contributions');
        }
        
        // Display projects
        const projectsList = document.getElementById('projectsList');
        
        if (projects.length === 0) {
            projectsList.innerHTML = '<p class="placeholder">No projects yet. Create one to get started!</p>';
            return;
        }
        
        projectsList.innerHTML = projects.map(project => `
            <div class="project-card" onclick="viewProject('${project._id}')">
                <h3>${project.project_name}</h3>
                <p>Final Item: <strong>${project.final_item}</strong></p>
                <div class="project-progress">
                    <div class="project-progress-bar">
                        <div class="project-progress-fill" style="width: ${project.progress || 0}%"></div>
                    </div>
                    <small>${Math.round(project.progress || 0)}% complete</small>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ===== Projects =====
async function loadProjects() {
    try {
        // Ensure we have current user info (fetched from server via token)
        if (!currentUser) {
            currentUser = await AuthAPI.getCurrentUser();
        }
        
        const result = await ProjectsAPI.getAll();
        const projects = result.projects || [];
        
        const projectsList = document.getElementById('allProjectsList');
        
        if (projects.length === 0) {
            projectsList.innerHTML = '<p class="placeholder">No projects. Create one to get started!</p>';
            return;
        }
        
        projectsList.innerHTML = projects.map(project => `
            <div class="project-card" onclick="viewProject('${project._id}')">
                <h3>${project.project_name}</h3>
                <p>Final Item: <strong>${project.final_item}</strong></p>
                <p>Owner: ${project.owner_id === currentUser.user_id ? 'You' : 'Someone'}</p>
                <div class="project-progress">
                    <div class="project-progress-bar">
                        <div class="project-progress-fill" style="width: ${project.progress || 0}%"></div>
                    </div>
                    <small>${Math.round(project.progress || 0)}% complete</small>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

async function createProject() {
    const projectName = document.getElementById('projectName').value.trim();
    const finalItem = document.getElementById('finalItem').value.trim();
    const errorMsg = document.getElementById('createProjectError');
    
    if (!projectName || !finalItem) {
        errorMsg.textContent = 'Please enter project name and final item';
        return;
    }
    
    // Get required items
    const itemGroups = document.querySelectorAll('#requiredItemsList .item-input-group');
    const requiredItems = [];
    
    for (const group of itemGroups) {
        const name = group.querySelector('.item-name').value.trim();
        const quantity = parseInt(group.querySelector('.item-quantity').value);
        
        if (!name || !quantity) {
            errorMsg.textContent = 'Please fill all item fields';
            return;
        }
        
        requiredItems.push({
            name: name,
            quantity: quantity,
            completed: 0
        });
    }
    
    if (requiredItems.length === 0) {
        errorMsg.textContent = 'Please add at least one item';
        return;
    }
    
    try {
        await ProjectsAPI.create(projectName, finalItem, requiredItems);
        
        // Clear form
        document.getElementById('projectName').value = '';
        document.getElementById('finalItem').value = '';
        document.getElementById('requiredItemsList').innerHTML = `
            <div class="item-input-group">
                <input type="text" placeholder="Item name" class="item-name input">
                <input type="number" placeholder="Quantity" min="1" class="item-quantity input">
                <button onclick="removeItemInput(this)" class="btn btn-danger">Remove</button>
            </div>
        `;
        errorMsg.textContent = '';
        
        // Navigate to projects
        navigateTo('dashboard');
    } catch (error) {
        errorMsg.textContent = error.message;
    }
}

function addItemInput() {
    const list = document.getElementById('requiredItemsList');
    const newItem = document.createElement('div');
    newItem.className = 'item-input-group';
    newItem.innerHTML = `
        <input type="text" placeholder="Item name" class="item-name input">
        <input type="number" placeholder="Quantity" min="1" class="item-quantity input">
        <button onclick="removeItemInput(this)" class="btn btn-danger">Remove</button>
    `;
    list.appendChild(newItem);
}

function removeItemInput(button) {
    button.parentElement.remove();
}

async function viewProject(projectId) {
    try {
        const result = await ProjectsAPI.getById(projectId);
        currentProject = result.project;
        
        // Update UI
        document.getElementById('projectTitle').textContent = currentProject.project_name;
        document.getElementById('projectStatus').textContent = `Status: ${currentProject.status}`;
        
        // Update progress
        const progress = ProjectsAPI.getProgress(projectId);
        loadProjectProgress(projectId);
        
        // Load items
        loadProjectItems();
        
        // Load activity
        loadProjectActivity(projectId);
        
        // Update contribution dropdown
        updateContributionDropdown();
        
        navigateTo('projectDetails');
    } catch (error) {
        console.error('Error loading project:', error);
    }
}

async function loadProjectProgress(projectId) {
    try {
        const result = await ProjectsAPI.getProgress(projectId);
        const percent = result.progress_percent || 0;
        
        document.getElementById('progressFill').style.width = percent + '%';
        document.getElementById('progressFill').textContent = Math.round(percent) + '%';
        document.getElementById('progressText').textContent = `${Math.round(percent)}% Complete (${result.total_completed}/${result.total_required} items)`;
    } catch (error) {
        console.error('Error loading progress:', error);
    }
}

function loadProjectItems() {
    if (!currentProject) return;
    
    const items = currentProject.required_items || [];
    const itemsList = document.getElementById('itemsList');
    
    itemsList.innerHTML = items.map(item => {
        const percent = item.quantity > 0 ? (item.completed / item.quantity * 100) : 0;
        const isBottleneck = item.completed < item.quantity;
        
        return `
            <div class="item ${isBottleneck ? 'bottleneck-item' : ''}">
                <div class="item-name">
                    ${item.name}
                    ${isBottleneck ? '<span class="bottleneck-badge">Blocking</span>' : ''}
                </div>
                <div class="item-progress">
                    ${item.completed}/${item.quantity} completed
                </div>
                <div class="item-progress-bar">
                    <div class="item-progress-fill" style="width: ${percent}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

function updateContributionDropdown() {
    if (!currentProject) return;
    
    const items = currentProject.required_items || [];
    const dropdown = document.getElementById('contributionItem');
    
    dropdown.innerHTML = '<option value="">Select an item...</option>' + 
        items.map(item => `<option value="${item.name}">${item.name}</option>`).join('');
}

async function addContribution() {
    const itemName = document.getElementById('contributionItem').value;
    const quantity = document.getElementById('contributionQuantity').value;
    const type = document.getElementById('contributionType').value;
    const errorMsg = document.getElementById('contributionError');
    
    if (!itemName || !quantity) {
        errorMsg.textContent = 'Please select item and quantity';
        return;
    }
    
    try {
        await ContributionsAPI.add(currentProject._id, itemName, quantity, type);
        
        // Clear form
        document.getElementById('contributionItem').value = '';
        document.getElementById('contributionQuantity').value = '';
        document.getElementById('contributionType').value = 'collected';
        errorMsg.textContent = '';
        
        // Reload project data
        viewProject(currentProject._id);
    } catch (error) {
        errorMsg.textContent = error.message;
    }
}

async function loadProjectActivity(projectId) {
    try {
        const result = await ActivityAPI.getProjectActivity(projectId, 20);
        const activities = result.activities || [];
        
        const activityFeed = document.getElementById('activityFeed');
        
        if (activities.length === 0) {
            activityFeed.innerHTML = '<p class="placeholder">No activities yet</p>';
            return;
        }
        
        activityFeed.innerHTML = activities.map(activity => {
            const date = new Date(activity.created_at);
            const timeStr = date.toLocaleString();
            
            return `
                <div class="activity-item">
                    <div><span class="activity-user">${activity.user_id}</span> - ${activity.action}</div>
                    <div class="activity-description">${activity.description || ''}</div>
                    <div class="activity-time">${timeStr}</div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading activity:', error);
    }
}

// ===== Profile =====
async function loadProfile() {
    try {
        const result = await AuthAPI.getProfile();
        const profileInfo = document.getElementById('profileInfo');
        
        profileInfo.innerHTML = `
            <div class="profile-field">
                <div class="profile-label">User ID</div>
                <div class="profile-value">${result.user_id}</div>
            </div>
            <div class="profile-field">
                <div class="profile-label">Username</div>
                <div class="profile-value">${result.username}</div>
            </div>
            <div class="profile-field">
                <div class="profile-label">Email</div>
                <div class="profile-value">${result.email}</div>
            </div>
            <div class="profile-field">
                <div class="profile-label">Role</div>
                <div class="profile-value">${result.role}</div>
            </div>
            <div class="profile-field">
                <div class="profile-label">Member Since</div>
                <div class="profile-value">${new Date(result.created_at).toLocaleDateString()}</div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// ===== Initialization =====
function initializeApp() {
    updateNavbar();
    
    if (TokenManager.isAuthenticated()) {
        navigateTo('dashboard');
    } else {
        navigateTo('login');
    }
    
    // Test API connection
    testConnection().then(connected => {
        if (!connected) {
            console.warn('API Server not reachable. Make sure Flask is running on localhost:5000');
        }
    });
}

// Start app when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);
