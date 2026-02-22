#!/usr/bin/env python3
"""
Pre-Deployment Validation Script for Railway
Checks if your environment is properly configured before deployment
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_status(message, status):
    """Print status with color-coded emoji"""
    emoji = "✅" if status else "❌"
    print(f"{emoji} {message}")
    return status

def check_env_var(var_name, required=True):
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    if value:
        # Mask sensitive values
        if 'URI' in var_name or 'KEY' in var_name or 'TOKEN' in var_name:
            display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
        else:
            display_value = value
        return print_status(f"{var_name}: {display_value}", True)
    else:
        status_text = "REQUIRED" if required else "OPTIONAL"
        return print_status(f"{var_name}: Not set ({status_text})", not required)

def check_file_exists(filename):
    """Check if a file exists"""
    exists = os.path.exists(filename)
    return print_status(f"File exists: {filename}", exists)

def check_mongodb_uri_format():
    """Validate MongoDB URI format"""
    uri = os.getenv('MONGODB_URI')
    if not uri:
        return False
    
    valid = uri.startswith('mongodb://') or uri.startswith('mongodb+srv://')
    return print_status("MongoDB URI format valid", valid)

def check_secret_key_strength():
    """Check if SECRET_KEY is strong enough"""
    key = os.getenv('SECRET_KEY')
    if not key:
        return False
    
    # Should be at least 32 characters
    strong = len(key) >= 32
    if not strong:
        print_status(f"SECRET_KEY length: {len(key)} chars (recommend 32+)", False)
    else:
        print_status(f"SECRET_KEY length: {len(key)} chars", True)
    return strong

def main():
    print("=" * 60)
    print("Railway Deployment - Environment Validation")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Required Environment Variables
    print("📋 Required Environment Variables:")
    all_checks_passed &= check_env_var('MONGODB_URI', required=True)
    all_checks_passed &= check_mongodb_uri_format()
    all_checks_passed &= check_env_var('SECRET_KEY', required=True)
    all_checks_passed &= check_secret_key_strength()
    print()
    
    # Optional Environment Variables
    print("📋 Optional Environment Variables:")
    check_env_var('FLASK_ENV', required=False)
    check_env_var('FLASK_DEBUG', required=False)
    check_env_var('ALLOWED_ORIGINS', required=False)
    check_env_var('CLEAR_DB_TOKEN', required=False)
    print()
    
    # Required Files
    print("📁 Required Files:")
    all_checks_passed &= check_file_exists('Procfile')
    all_checks_passed &= check_file_exists('requirements.txt')
    all_checks_passed &= check_file_exists('runtime.txt')
    all_checks_passed &= check_file_exists('railway.json')
    all_checks_passed &= check_file_exists('backend/app.py')
    all_checks_passed &= check_file_exists('backend/db.py')
    print()
    
    # Check .env file status
    print("🔒 Security Check:")
    env_exists = os.path.exists('.env')
    gitignore_exists = os.path.exists('.gitignore')
    
    if env_exists and gitignore_exists:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            env_ignored = '.env' in gitignore_content
            print_status(".env file is in .gitignore", env_ignored)
            if not env_ignored:
                print("⚠️  WARNING: .env file should be in .gitignore!")
                all_checks_passed = False
    print()
    
    # Python Dependencies
    print("📦 Python Dependencies:")
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            has_gunicorn = 'gunicorn' in requirements.lower()
            has_flask = 'flask' in requirements.lower()
            has_pymongo = 'pymongo' in requirements.lower()
            
            all_checks_passed &= print_status("gunicorn in requirements.txt", has_gunicorn)
            all_checks_passed &= print_status("flask in requirements.txt", has_flask)
            all_checks_passed &= print_status("pymongo in requirements.txt", has_pymongo)
    except FileNotFoundError:
        print_status("requirements.txt readable", False)
        all_checks_passed = False
    print()
    
    # Summary
    print("=" * 60)
    if all_checks_passed:
        print("✅ All required checks passed!")
        print("🚀 Your application is ready for Railway deployment")
        print()
        print("Next steps:")
        print("1. Push your code to GitHub")
        print("2. Create a new project on Railway")
        print("3. Connect your GitHub repository")
        print("4. Set environment variables in Railway dashboard")
        print("5. Railway will automatically deploy")
        return 0
    else:
        print("❌ Some checks failed")
        print("⚠️  Please fix the issues above before deploying")
        print()
        print("Quick fixes:")
        print("- Generate SECRET_KEY: python -c \"import secrets; print(secrets.token_hex(32))\"")
        print("- Set MONGODB_URI in .env file")
        print("- Ensure all required files are present")
        return 1

if __name__ == '__main__':
    sys.exit(main())
