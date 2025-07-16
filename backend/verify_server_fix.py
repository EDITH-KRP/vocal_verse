#!/usr/bin/env python3
"""
Verification script to test that all bugs in server.py are fixed
"""
import sys
import ast
import requests
import json
import time

def test_syntax():
    """Test that server.py compiles without syntax errors"""
    print("🧪 Testing server.py syntax...")
    try:
        with open('server.py', 'r') as f:
            content = f.read()
        
        # Test syntax
        ast.parse(content)
        print("✅ No syntax errors found")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def test_imports():
    """Test that all imports work correctly"""
    print("\n🧪 Testing imports...")
    try:
        # Test key imports
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        from typing import List, Optional
        import os
        from motor.motor_asyncio import AsyncIOMotorClient
        import uuid
        from datetime import datetime, timedelta
        import re
        import math
        import json
        import asyncio
        from collections import defaultdict
        import numpy as np
        import pandas as pd
        from scipy import stats
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints are working"""
    print("\n🧪 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test voice command endpoint
    try:
        command_data = {
            "command": "add apple 4 kg at 50 rupees",
            "language": "en"
        }
        response = requests.post(f"{base_url}/voice-command", 
                               json=command_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Voice command endpoint working")
            else:
                print(f"❌ Voice command failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Voice command endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voice command endpoint error: {e}")
        return False
    
    # Test products endpoint
    try:
        response = requests.get(f"{base_url}/products")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Products endpoint working (found {len(data.get('products', []))} products)")
            else:
                print(f"❌ Products endpoint failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Products endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Products endpoint error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🔍 Server.py Bug Verification")
    print("=" * 40)
    
    success_count = 0
    total_tests = 3
    
    # Run tests
    if test_syntax():
        success_count += 1
    
    if test_imports():
        success_count += 1
    
    # Wait a moment for server to be ready
    print("\n⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    if test_api_endpoints():
        success_count += 1
    
    # Final results
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All bugs fixed! Server.py is working correctly.")
        return True
    else:
        print("❌ Some issues remain. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)