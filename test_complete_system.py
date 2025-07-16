#!/usr/bin/env python3
"""
Complete system test for Vocal Verse with Supabase
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_system():
    print("🚀 Testing Complete Vocal Verse System")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed - Supabase connected: {data.get('supabase_connected')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: User login
    print("\n2. Testing user login...")
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("✅ Login successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test 3: List products
    print("\n3. Testing product listing...")
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Products listed - Found {len(data.get('products', []))} products")
        else:
            print(f"❌ Product listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Product listing error: {e}")
        return False
    
    # Test 4: Voice command - Add product
    print("\n4. Testing voice command (Add product)...")
    try:
        voice_data = {
            "command": "Add rice 10 kg at 50 rupees",
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/voice-command", json=voice_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Voice command successful: {data.get('message')}")
            else:
                print(f"❌ Voice command failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Voice command failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Voice command error: {e}")
        return False
    
    # Test 5: Voice command - List products
    print("\n5. Testing voice command (List products)...")
    try:
        voice_data = {
            "command": "List all products",
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/voice-command", json=voice_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Voice command successful: {data.get('message')}")
            else:
                print(f"❌ Voice command failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Voice command failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voice command error: {e}")
        return False
    
    # Test 6: Analytics endpoint
    print("\n6. Testing analytics...")
    try:
        response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics working - Total products: {data.get('summary', {}).get('total_products', 0)}")
        else:
            print(f"❌ Analytics failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return False
    
    print("\n🎉 All tests passed! Your Vocal Verse system is working perfectly!")
    print("\n📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    test_system()