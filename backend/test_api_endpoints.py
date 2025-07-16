import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test the enhanced API endpoints"""
    print("=== TESTING ENHANCED API ENDPOINTS ===")
    print()
    
    # Test health check
    print("1. Health Check")
    print("-" * 20)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Status: {response.json()}")
    print()
    
    # Test voice command processing
    print("2. Voice Command Processing")
    print("-" * 30)
    
    voice_commands = [
        {"command": "Add tomato 2 kg at 25 rupees", "language": "en"},
        {"command": "Store onion 1.5 kg ₹30", "language": "en"},
        {"command": "Create apple 3 kg fifty rupees", "language": "en"},
        {"command": "Update tomato price to ₹30", "language": "en"},
        {"command": "Search for apple", "language": "en"},
        {"command": "List all products", "language": "en"},
        {"command": "Remove onion", "language": "en"},
        {"command": "Add tamatar 1 kg ₹25", "language": "en"},  # Hindi name
        {"command": "Update aloo price to ₹30", "language": "en"},  # Hindi name
    ]
    
    for cmd_data in voice_commands:
        print(f"Command: '{cmd_data['command']}'")
        response = requests.post(f"{BASE_URL}/voice-command", json=cmd_data)
        result = response.json()
        
        print(f"  Success: {result.get('success', False)}")
        print(f"  Message: {result.get('message', 'N/A')}")
        
        if 'parsed_command' in result:
            parsed = result['parsed_command']
            print(f"  Parsed Action: {parsed.get('action', 'N/A')}")
            print(f"  Parsed Product: {parsed.get('product_name', 'N/A')}")
            if parsed.get('quantity'):
                print(f"  Parsed Quantity: {parsed.get('quantity')} kg")
            if parsed.get('price'):
                print(f"  Parsed Price: ₹{parsed.get('price')}")
            print(f"  Confidence: {parsed.get('confidence', 0):.2f}")
        
        print()
        time.sleep(0.5)  # Small delay between requests
    
    # Test direct CRUD operations
    print("3. Direct CRUD Operations")
    print("-" * 25)
    
    # Create product
    print("Creating product directly:")
    new_product = {
        "name": "Mango",
        "quantity": 2.0,
        "price_per_kg": 80.0,
        "category": "Fruit"
    }
    response = requests.post(f"{BASE_URL}/products", json=new_product)
    print(f"Create Result: {response.json()}")
    print()
    
    # Get all products
    print("Getting all products:")
    response = requests.get(f"{BASE_URL}/products")
    products_data = response.json()
    print(f"Total products: {len(products_data.get('products', []))}")
    for product in products_data.get('products', []):
        print(f"  - {product['name']}: {product['quantity']} kg at ₹{product['price_per_kg']}/kg")
    print()
    
    # Get specific product
    print("Getting specific product:")
    response = requests.get(f"{BASE_URL}/products/tomato")
    product_data = response.json()
    if product_data.get('success'):
        product = product_data['product']
        print(f"Found: {product['name']} - {product['quantity']} kg at ₹{product['price_per_kg']}/kg")
    else:
        print("Product not found")
    print()
    
    # Update product
    print("Updating product:")
    update_data = {
        "name": "tomato",
        "price_per_kg": 35.0
    }
    response = requests.put(f"{BASE_URL}/products/tomato", json=update_data)
    print(f"Update Result: {response.json()}")
    print()
    
    # Delete product
    print("Deleting product:")
    response = requests.delete(f"{BASE_URL}/products/apple")
    print(f"Delete Result: {response.json()}")
    print()
    
    # Final inventory
    print("Final inventory:")
    response = requests.get(f"{BASE_URL}/products")
    products_data = response.json()
    print(f"Remaining products: {len(products_data.get('products', []))}")
    for product in products_data.get('products', []):
        print(f"  - {product['name']}: {product['quantity']} kg at ₹{product['price_per_kg']}/kg")
    print()
    
    print("4. Advanced Voice Command Testing")
    print("-" * 35)
    
    advanced_commands = [
        "I want to add 2 kg of grapes at 120 rupees per kg",
        "Please update the price of mango to 85 rupees",
        "Can you show me all the products in stock?",
        "What is the stock of tomato?",
        "Remove mango from inventory"
    ]
    
    for cmd in advanced_commands:
        print(f"Command: '{cmd}'")
        response = requests.post(f"{BASE_URL}/voice-command", json={"command": cmd, "language": "en"})
        result = response.json()
        
        print(f"  Success: {result.get('success', False)}")
        print(f"  Message: {result.get('message', 'N/A')}")
        
        if 'parsed_command' in result:
            parsed = result['parsed_command']
            print(f"  Action: {parsed.get('action', 'N/A')}")
            print(f"  Product: {parsed.get('product_name', 'N/A')}")
            print(f"  Confidence: {parsed.get('confidence', 0):.2f}")
        
        print()
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        test_api_endpoints()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the API server.")
        print("Please make sure the FastAPI server is running on http://localhost:8000")
        print("Run: python -m uvicorn server:app --reload")