const storage = {
    set(key, value) { localStorage.setItem(key, value); },
    get(key) { return localStorage.getItem(key); },
    remove(key) { localStorage.removeItem(key); }
};

const DEFAULT_API_BASE = 'http://localhost:5000/api';

function getApiBase() {
    return (storage.get('api_base') || DEFAULT_API_BASE).replace(/\/$/, '');
}

function goToLogin() {
    window.location.href = 'login.html';
}

function goToDashboard() {
    window.location.href = 'dashboard.html';
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

// Handle form submission
document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');
    const confirmError = document.getElementById('confirmError');
    const submitBtn = document.getElementById('submitBtn');
    
    // Reset error messages
    usernameError.style.display = 'none';
    passwordError.style.display = 'none';
    confirmError.style.display = 'none';
    
    // Validation
    let hasError = false;
    
    if (!username || username.length < 4) {
        usernameError.textContent = 'Username must be at least 4 characters!';
        usernameError.style.display = 'block';
        hasError = true;
    }
    
    if (!password) {
        passwordError.textContent = 'Missing Pass!';
        passwordError.style.display = 'block';
        hasError = true;
    }
    
    if (password !== confirmPassword) {
        confirmError.textContent = "Passwords don't match!";
        confirmError.style.display = 'block';
        hasError = true;
    }
    
    if (hasError) return;
    
    // Disable button and show loading state
    submitBtn.classList.add('disabled');
    submitBtn.textContent = 'Loading...';
    submitBtn.disabled = true;
    
    try {
        const data = await apiCall('/auth/signup', 'POST', { 
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
        submitBtn.textContent = 'Sign Up';
        submitBtn.disabled = false;
    }
});

// Auto-redirect if already logged in
(function init() {
    if (storage.get('token')) {
        goToDashboard();
    }
})();
