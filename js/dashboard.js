// Only store JWT token in localStorage - all other data from API
const storage = {
    set(key, value) { localStorage.setItem(key, value); },
    get(key) { return localStorage.getItem(key); },
    remove(key) { localStorage.removeItem(key); }
};

// Session state (not persisted to localStorage)
let currentUser = null;
let currentWorlds = [];
let currentWorldId = null;
let minecraftItems = [];  // Will be populated from API

function goToLogin() {
    window.location.href = 'login.html';
}

// Use relative path for production, localhost for development
const DEFAULT_API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : '/api';

function getApiBase() {
    return DEFAULT_API_BASE;
}

async function apiCall(endpoint, method = 'GET', body = null) {
    const token = storage.get('token');
    if (!token) {
        goToLogin();
        return;
    }
    const res = await fetch(`${getApiBase()}${endpoint}`, {
        method,
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        body: body ? JSON.stringify(body) : null
    });
    const data = await res.json();
    if (res.status === 401) {
        logout();
        return;
    }
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
}

// Fetch user profile from API
async function fetchUserProfile() {
    try {
        const data = await apiCall('/auth/profile', 'GET');
        currentUser = data;
        return data;
    } catch (err) {
        console.error('Failed to fetch user profile:', err);
        return null;
    }
}

// Fetch worlds from API (database)
async function fetchWorlds() {
    try {
        const data = await apiCall('/projects/worlds', 'GET');
        currentWorlds = data.worlds || [];
        return currentWorlds;
    } catch (err) {
        console.error('Failed to fetch worlds:', err);
        return [];
    }
}

// Fetch Minecraft items from API
async function fetchMinecraftItems() {
    try {
        const res = await fetch(`${getApiBase()}/items/list`);
        const data = await res.json();
        minecraftItems = data.items || [];
        console.log(`Loaded ${minecraftItems.length} Minecraft items`);
        return minecraftItems;
    } catch (err) {
        console.error('Failed to fetch Minecraft items:', err);
        return [];
    }
}

// Fetch world inventory from API
async function fetchWorldInventory(worldName) {
    try {
        const data = await apiCall(`/inventory/${encodeURIComponent(worldName)}`, 'GET');
        return data.items || [];
    } catch (err) {
        console.error('Failed to fetch world inventory:', err);
        return [];
    }
}

// Get project completion based on inventory (smart version with recipes)
async function getProjectCompletion(projectId) {
    try {
        // Try smart recipe-aware version first
        const data = await apiCall(`/projects/${projectId}/completion/smart`, 'GET');
        return data.completion || null;
    } catch (err) {
        console.error('Failed to fetch smart project completion, falling back to basic:', err);
        try {
            // Fall back to basic version
            const data = await apiCall(`/projects/${projectId}/completion`, 'GET');
            return data.completion || null;
        } catch (err2) {
            console.error('Failed to fetch basic completion:', err2);
            return null;
        }
    }
}

// Get world projects completion (smart version)
async function getWorldProjectsCompletion(worldName) {
    try {
        // For world projects, we'll need to fetch each project's smart completion
        // First get all projects
        const projectsData = await apiCall(`/projects?world_name=${encodeURIComponent(worldName)}`, 'GET');
        const projects = projectsData.projects || [];
        
        if (projects.length === 0) {
            return [];
        }
        
        // Fetch smart completion for each project
        const completions = [];
        for (const project of projects) {
            try {
                const completion = await getProjectCompletion(project._id);
                if (completion) {
                    completions.push(completion);
                }
            } catch (err) {
                console.error(`Failed to get completion for project ${project._id}:`, err);
            }
        }
        
        return completions;
    } catch (err) {
        console.error('Failed to fetch world projects completion:', err);
        return [];
    }
}

// Add item to world inventory
async function addInventoryItem(worldName) {
    const itemSelect = document.getElementById(`invItemName_${worldName}`);
    const quantityInput = document.getElementById(`invQuantity_${worldName}`);
    
    const itemName = itemSelect.value.trim();
    const quantity = parseInt(quantityInput.value);
    
    if (!itemName) {
        alert('Please select an item');
        return;
    }
    
    if (!quantity || quantity < 1) {
        alert('Please enter a valid quantity (at least 1)');
        return;
    }
    
    try {
        await apiCall(`/inventory/${encodeURIComponent(worldName)}/item`, 'POST', {
            item_name: itemName,
            quantity: quantity
        });
        
        // Clear form
        itemSelect.value = '';
        quantityInput.value = '1';
        
        // Refresh inventory display
        await renderWorldTabs();
    } catch (err) {
        alert(`Error adding item: ${err.message}`);
    }
}

// Delete inventory item
async function deleteInventoryItem(worldName, itemId) {
    if (!confirm('Remove this item from inventory?')) return;
    
    try {
        await apiCall(`/inventory/${encodeURIComponent(worldName)}/item/${itemId}`, 'DELETE');
        await renderWorldTabs();
    } catch (err) {
        alert(`Error deleting item: ${err.message}`);
    }
}

// Increment inventory item quantity
async function incrementInventoryItem(worldName, itemName) {
    try {
        await apiCall(`/inventory/${encodeURIComponent(worldName)}/item/${encodeURIComponent(itemName)}/increment`, 'POST', {
            amount: 1
        });
        await renderWorldTabs();
    } catch (err) {
        alert(`Error incrementing item: ${err.message}`);
    }
}

// Decrement inventory item quantity
async function decrementInventoryItem(worldName, itemName) {
    try {
        await apiCall(`/inventory/${encodeURIComponent(worldName)}/item/${encodeURIComponent(itemName)}/decrement`, 'POST', {
            amount: 1
        });
        await renderWorldTabs();
    } catch (err) {
        alert(`Error decrementing item: ${err.message}`);
    }
}

async function renderWorldTabs() {
    const tabButtons = document.getElementById('tabButtons');
    const tabPanels = document.getElementById('tabPanels');
    
    // Fetch worlds from database
    const worlds = await fetchWorlds();
    
    if (worlds.length === 0) {
        currentWorldId = null;
        tabButtons.innerHTML = '';
        tabPanels.innerHTML = '<div class="card"><p>No worlds yet. Add one above to get started.</p></div>';
        return;
    }

    if (!currentWorldId || !worlds.some(w => w.world_name === currentWorldId)) {
        currentWorldId = worlds[0].world_name;
    }
    
    tabButtons.innerHTML = '';
    tabPanels.innerHTML = '';

    // Render each world with its projects
    for (const world of worlds) {
        const btn = document.createElement('button');
        btn.className = 'tab-btn' + (world.world_name === currentWorldId ? ' active' : '');
        btn.dataset.target = world.world_name;
        btn.textContent = world.world_name;
        btn.addEventListener('click', () => {
            currentWorldId = world.world_name;
            renderWorldTabs();
        });
        tabButtons.appendChild(btn);

        const panel = document.createElement('section');
        panel.className = 'tab-panel' + (world.world_name === currentWorldId ? ' active' : '');
        panel.id = world.world_name;
        
        // Fetch projects for this world
        let projectsHTML = '<p>Loading projects...</p>';
        try {
            const projectsData = await apiCall(`/projects?world_name=${encodeURIComponent(world.world_name)}`, 'GET');
            const projects = projectsData.projects || [];
            
            if (projects.length === 0) {
                projectsHTML = '<p style="color: #888;">No projects in this world yet.</p>';
            } else {
                projectsHTML = '<div class="projects-list">';
                
                // Get inventory-based completion for all projects in this world
                const completions = await getWorldProjectsCompletion(world.world_name);
                const completionMap = {};
                completions.forEach(c => {
                    completionMap[c.project_id] = c;
                });
                
                projects.forEach(project => {
                    const completion = completionMap[project._id];
                    
                    let progress = 0;
                    let completedItems = 0;
                    let totalItems = 0;
                    let statusColor = '#888';
                    
                    if (completion) {
                        progress = Math.round(completion.overall_percent);
                        completedItems = completion.total_collected;
                        totalItems = completion.total_required;
                        
                        // Color code by status
                        if (completion.status === 'complete') {
                            statusColor = '#4CAF50'; // Green
                        } else if (completion.status === 'in_progress') {
                            statusColor = '#2196F3'; // Blue
                        } else if (completion.status === 'not_started') {
                            statusColor = '#FF9800'; // Orange
                        }
                    } else {
                        totalItems = project.required_items?.reduce((sum, item) => sum + item.quantity, 0) || 0;
                        completedItems = project.required_items?.reduce((sum, item) => sum + (item.completed || 0), 0) || 0;
                        progress = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;
                    }
                    
                    projectsHTML += `
                        <div class="card" style="margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <h3>${project.project_name}</h3>
                                <button class="btn-danger btn-sm" data-delete-project="${project._id}">Delete</button>
                            </div>
                            <p><strong>Final Item:</strong> ${project.final_item} x${project.required_items && project.required_items.length > 0 ? project.required_items[0].quantity : 1}</p>
                            <p><strong>Status:</strong> ${project.status || 'in_progress'}</p>
                            <div style="margin: 0.5rem 0;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                                    <span style="font-weight: bold; color: ${statusColor};">Progress: ${progress}%</span>
                                    <span style="font-size: 0.9rem; color: #aaa;">${completedItems}/${totalItems} items</span>
                                </div>
                                <div style="background: #373737; border: 2px solid #000; height: 16px; overflow: hidden; box-shadow: inset 2px 2px 0 rgba(0,0,0,0.5);">
                                    <div style="background: #51B551; height: 100%; width: ${progress}%; transition: width 0.3s;"></div>
                                </div>
                            </div>
                            ${completion && completion.items && completion.items.length > 0 ? `
                                <details style="margin-top: 0.5rem; font-size: 0.9rem;">
                                    <summary style="cursor: pointer; color: #aaa;">Item Breakdown</summary>
                                    <div style="margin-top: 0.5rem; padding-left: 1rem;">
                                        ${completion.items.map(item => `
                                            <div style="margin: 0.5rem 0; padding: 0.3rem; background: rgba(255,255,255,0.05); border-radius: 2px;">
                                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
                                                    <span>${item.item_name}</span>
                                                    <span style="color: ${item.missing > 0 ? '#FF9800' : '#4CAF50'}">${item.collected}/${item.required}</span>
                                                </div>
                                                ${item.crafting_notes && item.crafting_notes.length > 0 ? `
                                                    <div style="font-size: 0.85rem; color: #999; margin-left: 0.5rem; padding-top: 0.2rem; border-top: 1px solid rgba(255,255,255,0.1);">
                                                        ${item.crafting_notes.map(note => `<div>${note}</div>`).join('')}
                                                    </div>
                                                ` : ''}
                                            </div>
                                        `).join('')}
                                    </div>
                                </details>
                            ` : ''}
                            <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;"><strong>Created:</strong> ${new Date(project.created_at).toLocaleDateString()}</p>
                            <p style="font-size: 0.8rem; color: #666;"><strong>Project ID:</strong> ${project._id}</p>
                        </div>
                    `;
                });
                projectsHTML += '</div>';
            }
        } catch (err) {
            projectsHTML = `<p style="color: red;">Failed to load projects: ${err.message}</p>`;
        }
        
        // Fetch inventory for this world
        let inventoryHTML = '<p>Loading inventory...</p>';
        try {
            const inventoryItems = await fetchWorldInventory(world.world_name);
            
            if (inventoryItems.length === 0) {
                inventoryHTML = '<p style="color: #888;">No items in inventory yet.</p>';
            } else {
                inventoryHTML = '<div class="inventory-list" style="display: grid; gap: 0.5rem;">';
                inventoryItems.forEach(item => {
                    inventoryHTML += `
                        <div class="inventory-item" style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 4px;">
                            <div style="flex: 1;">
                                <strong>${item.item_name}</strong>
                                <span style="margin-left: 1rem; color: #aaa;">x${item.quantity}</span>
                            </div>
                            <div style="display: flex; gap: 0.5rem;">
                                <button class="btn-sm" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" data-inv-decrement="${item._id}" data-inv-world="${world.world_name}" data-inv-item="${item.item_name}">-</button>
                                <button class="btn-sm" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" data-inv-increment="${item._id}" data-inv-world="${world.world_name}" data-inv-item="${item.item_name}">+</button>
                                <button class="btn-danger btn-sm" style="padding: 0.3rem 0.6rem;" data-inv-delete="${item._id}" data-inv-world="${world.world_name}">Delete</button>
                            </div>
                        </div>
                    `;
                });
                inventoryHTML += '</div>';
            }
        } catch (err) {
            inventoryHTML = `<p style="color: red;">Failed to load inventory: ${err.message}</p>`;
        }
        
        panel.innerHTML = `
            <div style="display: flex; gap: 2rem; margin-bottom: 2rem;">
                <div style="flex: 0 0 auto; min-width: 300px;">
                    <div class="card">
                        <h2>${world.world_name}</h2>
                        <p><strong>Total Projects:</strong> ${world.project_count || 0}</p>
                        <p><strong>Created:</strong> ${world.created_at ? new Date(world.created_at).toLocaleDateString() : 'N/A'}</p>
                        <div class="row">
                            <button class="btn-danger" data-delete="${world.world_name}">Delete this world</button>
                        </div>
                    </div>
                </div>
                <div style="flex: 1; min-width: 300px;">
                    <h3>📦 World Inventory</h3>
                    <div class="card" style="margin-bottom: 1rem;">
                        <div class="inventory-form">
                            <label style="color: var(--muted); font-size: 0.9rem; margin-bottom: 0.3rem; display: block;">Add Item to Inventory</label>
                            <select id="invItemName_${world.world_name}" class="form-input">
                                <option value="" selected>-- Select an item --</option>
                            </select>
                            <input type="number" placeholder="Quantity" id="invQuantity_${world.world_name}" class="form-input" min="1" value="1">
                            <button class="btn-primary" data-add-inventory="${world.world_name}">Add to Inventory</button>
                        </div>
                    </div>
                    <h3>Current Inventory</h3>
                    <div class="card" style="margin-bottom: 1rem; max-height: 280px; overflow-y: auto;">
                        ${inventoryHTML}
                    </div>
                </div>
            </div>
            <hr style="margin: 2rem 0;">
            <h3>Add New Project</h3>
            <div class="card" style="margin-bottom: 2rem;">
                <div class="project-form">
                    <label style="color: var(--muted); font-size: 0.9rem; margin-bottom: 0.3rem; display: block;">Minecraft Item</label>
                    <select id="itemName_${world.world_name}" class="form-input">
                        <option value="" selected>-- Select an item --</option>
                    </select>
                    <input type="number" placeholder="Number of Items" id="itemQuantity_${world.world_name}" class="form-input" min="1" value="1">
                    <button class="btn-primary" data-add-project="${world.world_name}">Add Project</button>
                </div>
            </div>
            <h3>Projects in ${world.world_name}</h3>
            ${projectsHTML}
        `;
        tabPanels.appendChild(panel);
    }

    // Wire delete world buttons after render
    tabPanels.querySelectorAll('[data-delete]').forEach(btn => {
        btn.addEventListener('click', () => deleteWorld(btn.dataset.delete));
    });
    
    // Wire add project buttons
    tabPanels.querySelectorAll('[data-add-project]').forEach(btn => {
        btn.addEventListener('click', () => addProject(btn.dataset.addProject));
    });
    
    // Wire delete project buttons
    tabPanels.querySelectorAll('[data-delete-project]').forEach(btn => {
        btn.addEventListener('click', () => deleteProject(btn.dataset.deleteProject));
    });
    
    // Wire add inventory buttons
    tabPanels.querySelectorAll('[data-add-inventory]').forEach(btn => {
        btn.addEventListener('click', () => addInventoryItem(btn.dataset.addInventory));
    });
    
    // Wire delete inventory buttons
    tabPanels.querySelectorAll('[data-inv-delete]').forEach(btn => {
        btn.addEventListener('click', () => deleteInventoryItem(btn.dataset.invWorld, btn.dataset.invDelete));
    });
    
    // Wire increment inventory buttons
    tabPanels.querySelectorAll('[data-inv-increment]').forEach(btn => {
        btn.addEventListener('click', () => incrementInventoryItem(btn.dataset.invWorld, btn.dataset.invItem));
    });
    
    // Wire decrement inventory buttons
    tabPanels.querySelectorAll('[data-inv-decrement]').forEach(btn => {
        btn.addEventListener('click', () => decrementInventoryItem(btn.dataset.invWorld, btn.dataset.invItem));
    });
    
    // Populate select dropdowns with Minecraft items
    worlds.forEach(world => {
        const select = document.getElementById(`itemName_${world.world_name}`);
        const invSelect = document.getElementById(`invItemName_${world.world_name}`);
        if (select) {
            minecraftItems.forEach(item => {
                const option = document.createElement('option');
                option.value = item;
                option.textContent = item;
                select.appendChild(option);
            });
        }
        if (invSelect) {
            minecraftItems.forEach(item => {
                const option = document.createElement('option');
                option.value = item;
                option.textContent = item;
                invSelect.appendChild(option);
            });
        }
    });
}

async function addProject(worldName) {
    const itemNameSelect = document.getElementById(`itemName_${worldName}`);
    const itemQuantityInput = document.getElementById(`itemQuantity_${worldName}`);
    
    const itemName = itemNameSelect.value.trim();
    const itemQuantity = parseInt(itemQuantityInput.value);
    
    if (!itemName) {
        alert('Please select a Minecraft item');
        return;
    }
    
    if (!itemQuantity || itemQuantity < 1) {
        alert('Please enter a valid quantity (at least 1)');
        return;
    }
    
    // Auto-generate project structure from simple inputs
    const requiredItems = [{
        name: itemName,
        quantity: itemQuantity,
        completed: 0
    }];
    
    try {
        await apiCall('/projects', 'POST', {
            project_name: itemName,
            final_item: itemName,
            required_items: requiredItems,
            world_name: worldName
        });
        
        // Clear form
        itemNameSelect.value = '';
        itemQuantityInput.value = '1';
        
        // Refresh the world tabs to show the new project
        await renderWorldTabs();
    } catch (err) {
        alert(`Error creating project: ${err.message}`);
    }
}

async function deleteProject(projectId) {
    if (!confirm('Delete this project? This will also delete all contributions and activity logs.')) return;
    
    try {
        await apiCall(`/projects/${projectId}`, 'DELETE');
        await renderWorldTabs();
    } catch (err) {
        alert(`Error deleting project: ${err.message}`);
    }
}

async function addWorld() {
    const input = document.getElementById('newWorldName');
    const name = (input.value || '').trim();
    if (!name) {
        alert('World name is required');
        return;
    }
    
    try {
        await apiCall('/projects/worlds', 'POST', { world_name: name });
        input.value = '';
        await renderWorldTabs();
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

async function deleteWorld(worldName) {
    if (!confirm(`Delete world "${worldName}"? This will delete all projects in this world.`)) return;
    
    try {
        await apiCall(`/projects/worlds/${encodeURIComponent(worldName)}`, 'DELETE');
        await renderWorldTabs();
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

async function deleteUser() {
    if (!confirm('Delete your account? This cannot be undone.')) return;
    try {
        const data = await apiCall('/auth/delete', 'DELETE');
        if (!data) {
            logout();
            return;
        }
        logout();
    } catch (err) {
        alert(`Error: ${err.message}`);
        logout();
    }
}

function logout() {
    // Only remove JWT token
    storage.remove('token');
    document.getElementById('status').textContent = 'Disconnected';
    document.getElementById('userInfo').textContent = 'Not logged in';
    goToLogin();
}

(async function init() {
    const token = storage.get('token');
    if (!token) {
        goToLogin();
        return;
    }
    
    document.getElementById('status').textContent = 'Connected';
    
    // Fetch user profile from API
    const user = await fetchUserProfile();
    if (user) {
        document.getElementById('userInfo').textContent = `User: ${user.username || 'unknown'}`;
    } else {
        document.getElementById('userInfo').textContent = 'User: unknown';
    }
    
    // Load Minecraft items for dropdown
    await fetchMinecraftItems();
    
    // Load worlds from database
    await renderWorldTabs();
})();
