"""
Vercel Serverless Function Entry Point for CraftChain API
"""
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app import app

# Vercel handler - this is the entry point for the serverless function
def handler(request, context):
    return app(request, context)

# Export the Flask app for Vercel
# Vercel will automatically detect this and use it
app = app
