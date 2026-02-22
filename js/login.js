const storage = {
    set(key, value) { localStorage.setItem(key, value); },
    get(key) { return localStorage.getItem(key); },
    remove(key) { localStorage.removeItem(key); }
};

// Use relative path for production, localhost for development
const DEFAULT_API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : '/api';

function getApiBase() {
    return (storage.get('api_base') || DEFAULT_API_BASE).replace(/\/$/, '');
}

async function apiCall(endpoint, method = 'POST', body = null) {
    const res = await fetch(`${getApiBase()}${endpoint}`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : null
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
}

function goToDashboard() {
    window.location.href = 'dashboard.html';
}

function goToSignup() {
    window.location.href = 'signup.html';
}

// Handle form submission
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');
    const submitBtn = document.getElementById('submitBtn');
    
    // Reset error messages
    usernameError.style.display = 'none';
    passwordError.style.display = 'none';
    
    // Validation
    let hasError = false;
    
    if (!username) {
        usernameError.textContent = 'Invalid Username!';
        usernameError.style.display = 'block';
        hasError = true;
    }
    
    if (!password) {
        passwordError.textContent = 'Missing Pass!';
        passwordError.style.display = 'block';
        hasError = true;
    }
    
    if (hasError) return;
    
    // Disable button and show loading state
    submitBtn.classList.add('disabled');
    submitBtn.textContent = 'Loading...';
    submitBtn.disabled = true;
    
    try {
        const data = await apiCall('/auth/login', 'POST', { 
            username: username, 
            user_id: username, 
            password: password 
        });
        
        // Only store JWT token - user data fetched from server
        storage.set('token', data.token);
        
        // Redirect to dashboard
        goToDashboard();
    } catch (err) {
        // Show error message
        passwordError.textContent = `Error: ${err.message}`;
        passwordError.style.display = 'block';
        
        // Re-enable button
        submitBtn.classList.remove('disabled');
        submitBtn.textContent = 'Login';
        submitBtn.disabled = false;
    }
});

// Auto-redirect if already logged in
(function init() {
    if (storage.get('token')) {
        goToDashboard();
    }
})();
