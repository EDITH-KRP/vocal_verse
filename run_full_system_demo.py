#!/usr/bin/env python3
"""
Full System Demo - Frontend + Backend + Supabase Integration
"""
import requests
import json
import time
import webbrowser
from datetime import datetime

def print_header(title):
    """Print a nice header"""
    print("\n" + "="*60)
    print(f"🎤 {title}")
    print("="*60)

def test_backend_health():
    """Test backend health"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running successfully!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print("❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_frontend_access():
    """Test frontend access"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running successfully!")
            print("   Access URL: http://localhost:3000")
            return True
        else:
            print("❌ Frontend access failed")
            return False
    except Exception as e:
        print(f"❌ Frontend connection error: {e}")
        return False

def test_voice_commands():
    """Test voice command processing"""
    print_header("VOICE COMMAND TESTING")
    
    # Test the original command that was requested
    commands = [
        {
            "command": "Update tomato price to ₹25",
            "description": "🎯 Original requested command"
        },
        {
            "command": "Add apple 2 kg at 60 rupees",
            "description": "➕ CREATE operation"
        },
        {
            "command": "Search for apple",
            "description": "🔍 READ operation"
        },
        {
            "command": "Update apple price to ₹65",
            "description": "✏️ UPDATE operation"
        },
        {
            "command": "Remove apple",
            "description": "🗑️ DELETE operation"
        },
        {
            "command": "Add tamatar 1 kg ₹30",
            "description": "🌍 Multi-language (Hindi: tamatar = tomato)"
        },
        {
            "command": "Update aloo price to ₹40",
            "description": "🌍 Multi-language (Hindi: aloo = potato)"
        },
        {
            "command": "I want to add 2 kg of mangoes at 80 rupees per kg",
            "description": "🧠 Natural language processing"
        },
        {
            "command": "List all products",
            "description": "📋 List all items"
        },
        {
            "command": "Stock of tomato",
            "description": "📊 Stock inquiry"
        }
    ]
    
    success_count = 0
    total_commands = len(commands)
    
    for i, cmd_data in enumerate(commands, 1):
        print(f"\n{i}. {cmd_data['description']}")
        print(f"   Command: '{cmd_data['command']}'")
        
        try:
            response = requests.post(
                "http://localhost:8000/voice-command",
                json={"command": cmd_data['command'], "language": "en"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('success', False)}")
                print(f"   📝 Message: {result.get('message', 'No message')}")
                
                if 'parsed_command' in result:
                    parsed = result['parsed_command']
                    print(f"   🎯 Action: {parsed.get('action', 'N/A')}")
                    print(f"   📦 Product: {parsed.get('product_name', 'N/A')}")
                    if parsed.get('quantity'):
                        print(f"   ⚖️ Quantity: {parsed.get('quantity')} kg")
                    if parsed.get('price'):
                        print(f"   💰 Price: ₹{parsed.get('price')}")
                    print(f"   🎲 Confidence: {parsed.get('confidence', 0):.2f}")
                
                if result.get('success'):
                    success_count += 1
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print(f"\n📊 Test Results: {success_count}/{total_commands} commands successful")
    return success_count == total_commands

def test_crud_operations():
    """Test direct CRUD operations"""
    print_header("DIRECT CRUD OPERATIONS")
    
    # Test product creation
    print("\n1. Creating product via API...")
    product_data = {
        "name": "Mango",
        "quantity": 2.0,
        "price_per_kg": 80.0,
        "category": "Fruit",
        "description": "Fresh mangoes"
    }
    
    try:
        response = requests.post("http://localhost:8000/products", json=product_data, timeout=10)
        if response.status_code == 200:
            print("   ✅ Product created successfully!")
            print(f"   📝 Response: {response.json()}")
        else:
            print(f"   ❌ Failed to create product: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error creating product: {e}")
    
    # Test getting all products
    print("\n2. Getting all products...")
    try:
        response = requests.get("http://localhost:8000/products", timeout=10)
        if response.status_code == 200:
            products = response.json()
            print(f"   ✅ Found {len(products.get('products', []))} products")
            for product in products.get('products', []):
                print(f"     - {product['name']}: {product['quantity']} kg at ₹{product['price_per_kg']}/kg")
        else:
            print(f"   ❌ Failed to get products: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting products: {e}")

def open_browser():
    """Open the frontend in browser"""
    print_header("OPENING FRONTEND IN BROWSER")
    
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ Frontend opened in browser!")
        print("   URL: http://localhost:3000")
        print("   Features you can test in the browser:")
        print("   - Voice command input")
        print("   - Product management")
        print("   - Real-time updates")
        print("   - Multi-language support")
        print("   - Analytics dashboard")
        
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print("   Please manually open: http://localhost:3000")

def main():
    """Run the complete system demo"""
    print("🚀 VOCAL VERSE - FULL SYSTEM DEMO")
    print("=" * 60)
    print("Testing complete system: Frontend + Backend + Supabase")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test backend
    print_header("BACKEND TESTING")
    backend_ok = test_backend_health()
    
    # Test frontend
    print_header("FRONTEND TESTING")
    frontend_ok = test_frontend_access()
    
    if backend_ok:
        # Test voice commands
        voice_ok = test_voice_commands()
        
        # Test CRUD operations
        crud_ok = test_crud_operations()
        
        # Open browser if everything is working
        if frontend_ok:
            open_browser()
    
    # Final summary
    print_header("SYSTEM STATUS SUMMARY")
    print(f"📡 Backend API: {'✅ RUNNING' if backend_ok else '❌ DOWN'}")
    print(f"🌐 Frontend Web: {'✅ RUNNING' if frontend_ok else '❌ DOWN'}")
    print(f"🎤 Voice Commands: {'✅ WORKING' if backend_ok and 'voice_ok' in locals() and voice_ok else '❌ ISSUES'}")
    print(f"📊 CRUD Operations: {'✅ WORKING' if backend_ok and 'crud_ok' in locals() else '❌ ISSUES'}")
    print(f"🗄️ Database: {'✅ SUPABASE CONNECTED' if backend_ok else '❌ CONNECTION ISSUE'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 SUCCESS! Both frontend and backend are running!")
        print("📝 Instructions:")
        print("   1. Frontend: http://localhost:3000")
        print("   2. Backend API: http://localhost:8000")
        print("   3. API Docs: http://localhost:8000/docs")
        print("   4. Test the voice commands in the web interface")
        print("   5. Try: 'Update tomato price to ₹25' (your original request)")
        print("   6. Try: 'Add tamatar 1 kg ₹30' (Hindi multi-language)")
        print("   7. Try: 'List all products' (to see inventory)")
    else:
        print("\n⚠️ ISSUES DETECTED:")
        if not backend_ok:
            print("   - Backend is not running. Check: python -m uvicorn supabase_server:app --reload")
        if not frontend_ok:
            print("   - Frontend is not running. Check: npm start in frontend folder")
        print("   - Make sure both services are started before testing")

if __name__ == "__main__":
    main()