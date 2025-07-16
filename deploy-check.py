#!/usr/bin/env python3
"""
Pre-deployment check script for AI Voice Inventory Management System
Verifies all components are ready for Vercel deployment.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a required file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (MISSING)")
        return False

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = ['GEMINI_API_KEY', 'MONGO_URL']
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ Environment variable: {var}")
        else:
            print(f"❌ Environment variable: {var} (NOT SET)")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def check_dependencies():
    """Check if all required dependencies are available"""
    print("\n🔍 Checking Python dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'motor', 'pymongo', 
        'dotenv', 'pandas', 'numpy', 'scipy',
        'google.generativeai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('python_dotenv')
            else:
                __import__(package)
            print(f"✅ Python package: {package}")
        except ImportError:
            print(f"❌ Python package: {package} (NOT INSTALLED)")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_frontend_build():
    """Check if frontend can build successfully"""
    print("\n🏗️  Checking frontend build...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    package_json_path = frontend_dir / "package.json"
    if not package_json_path.exists():
        print("❌ Frontend package.json not found")
        return False
    
    print("✅ Frontend structure looks good")
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️  Node modules not installed. Run: cd frontend && npm install")
        return False
    
    print("✅ Node modules installed")
    return True

def check_vercel_config():
    """Check Vercel configuration"""
    print("\n⚙️  Checking Vercel configuration...")
    
    # Check vercel.json
    if not check_file_exists("vercel.json", "Vercel config"):
        return False
    
    # Check requirements.txt in root
    if not check_file_exists("requirements.txt", "Root requirements.txt"):
        return False
    
    # Check API directory
    if not check_file_exists("api/index.py", "API entry point"):
        return False
    
    return True

def run_basic_tests():
    """Run basic functionality tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test basic imports
        import fastapi
        import uvicorn
        print("✅ FastAPI imports successfully")
        
        # Test environment loading
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Environment loading works")
        except:
            print("⚠️  python-dotenv not available, but that's OK")
        
        return True
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        return False

def main():
    """Main deployment check function"""
    print("🚀 AI Voice Inventory Management System - Deployment Check")
    print("=" * 60)
    
    checks = []
    
    # File structure checks
    print("\n📁 Checking file structure...")
    checks.append(check_file_exists("backend/server.py", "Backend server"))
    checks.append(check_file_exists("frontend/src/App.js", "Frontend app"))
    checks.append(check_file_exists("frontend/package.json", "Frontend package.json"))
    checks.append(check_file_exists("backend/requirements.txt", "Backend requirements"))
    
    # Vercel configuration
    checks.append(check_vercel_config())
    
    # Environment variables
    print("\n🔐 Checking environment variables...")
    checks.append(check_env_vars())
    
    # Dependencies
    checks.append(check_dependencies())
    
    # Frontend build
    checks.append(check_frontend_build())
    
    # Basic tests
    checks.append(run_basic_tests())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT READINESS SUMMARY")
    print("=" * 60)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"🎉 ALL CHECKS PASSED ({passed}/{total})")
        print("\n✅ Your project is ready for Vercel deployment!")
        print("\nNext steps:")
        print("1. Push your code to Git repository")
        print("2. Connect repository to Vercel")
        print("3. Set environment variables in Vercel dashboard")
        print("4. Deploy!")
        
        return True
    else:
        print(f"⚠️  SOME CHECKS FAILED ({passed}/{total})")
        print("\n❌ Please fix the issues above before deploying.")
        
        if not os.getenv('GEMINI_API_KEY'):
            print("\n💡 To set environment variables:")
            print("   Create a .env file with:")
            print("   GEMINI_API_KEY=your_api_key")
            print("   MONGO_URL=your_mongodb_url")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)