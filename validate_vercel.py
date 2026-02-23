"""
Vercel Deployment Validation Script
Run this before deploying to Vercel to ensure everything is configured correctly
"""
import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a required file exists"""
    path = Path(file_path)
    if path.exists():
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description} missing: {file_path}")
        return False

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = ['MONGODB_URI', 'SECRET_KEY']
    missing = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✓ Environment variable set: {var}")
        else:
            print(f"⚠ Environment variable not set: {var} (will need to set in Vercel)")
            missing.append(var)
    
    return len(missing) == 0

def check_vercel_config():
    """Validate vercel.json configuration"""
    import json
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        print("✓ vercel.json is valid JSON")
        
        # Check required fields
        if 'builds' in config and 'routes' in config:
            print("✓ vercel.json has required 'builds' and 'routes' sections")
            return True
        else:
            print("✗ vercel.json missing required sections")
            return False
    except FileNotFoundError:
        print("✗ vercel.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ vercel.json has invalid JSON: {e}")
        return False

def check_api_structure():
    """Check if API directory structure is correct"""
    api_index = Path('api/index.py')
    if api_index.exists():
        print("✓ API entry point exists: api/index.py")
        
        # Check if it imports from backend
        with open(api_index, 'r') as f:
            content = f.read()
            if 'from backend.app import app' in content:
                print("✓ API entry point imports Flask app correctly")
                return True
            else:
                print("✗ API entry point doesn't import Flask app")
                return False
    else:
        print("✗ API entry point missing: api/index.py")
        return False

def check_requirements():
    """Check if requirements.txt has all necessary packages"""
    required_packages = ['Flask', 'pymongo', 'flask-cors', 'bcrypt', 'PyJWT']
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read().lower()
        
        missing = []
        for package in required_packages:
            if package.lower() in content:
                print(f"✓ Package found: {package}")
            else:
                print(f"✗ Package missing: {package}")
                missing.append(package)
        
        return len(missing) == 0
    except FileNotFoundError:
        print("✗ requirements.txt not found")
        return False

def check_static_files():
    """Check if main HTML files exist"""
    files = ['index.html', 'dashboard.html', 'login.html', 'signup.html']
    all_exist = True
    
    for file in files:
        if Path(file).exists():
            print(f"✓ Static file exists: {file}")
        else:
            print(f"⚠ Static file missing: {file} (optional)")
    
    return all_exist

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("Vercel Deployment Validation")
    print("=" * 60)
    print()
    
    checks = []
    
    print("1. Checking Required Files")
    print("-" * 40)
    checks.append(check_file_exists('vercel.json', 'Vercel config'))
    checks.append(check_file_exists('api/index.py', 'API entry point'))
    checks.append(check_file_exists('backend/app.py', 'Flask app'))
    checks.append(check_file_exists('backend/db.py', 'Database module'))
    checks.append(check_file_exists('requirements.txt', 'Requirements'))
    print()
    
    print("2. Validating Vercel Configuration")
    print("-" * 40)
    checks.append(check_vercel_config())
    print()
    
    print("3. Checking API Structure")
    print("-" * 40)
    checks.append(check_api_structure())
    print()
    
    print("4. Validating Requirements")
    print("-" * 40)
    checks.append(check_requirements())
    print()
    
    print("5. Checking Static Files")
    print("-" * 40)
    check_static_files()  # Not critical, so not added to checks
    print()
    
    print("6. Checking Environment Variables")
    print("-" * 40)
    check_env_vars()  # Not critical here, needed in Vercel
    print()
    
    print("=" * 60)
    if all(checks):
        print("✓ All critical checks passed!")
        print("✓ Your project is ready for Vercel deployment")
        print()
        print("Next steps:")
        print("1. Push your code to Git repository")
        print("2. Import project in Vercel dashboard")
        print("3. Set environment variables (MONGODB_URI, SECRET_KEY)")
        print("4. Deploy!")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("See VERCEL_DEPLOYMENT.md for detailed instructions")
        return 1

if __name__ == '__main__':
    sys.exit(main())
