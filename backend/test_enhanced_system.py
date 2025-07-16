import asyncio
from server import (
    process_voice_command, 
    save_product, 
    find_product, 
    update_product, 
    delete_product,
    get_all_products,
    Product,
    test_mongodb_connection
)

async def test_enhanced_crud_system():
    """Test the enhanced CRUD system with voice commands"""
    print("=== ENHANCED VOICE COMMAND SYSTEM WITH FULL CRUD OPERATIONS ===")
    print()
    
    # Initialize MongoDB connection
    await test_mongodb_connection()
    
    print("1. TESTING VOICE COMMAND PROCESSING")
    print("=" * 50)
    
    # Test adding products with voice commands
    voice_commands = [
        "Add tomato 2 kg at 25 rupees",
        "Store onion 1.5 kg ₹30",
        "Create apple 3 kg fifty rupees",
        "Add potato 2.5 kg ₹20",
        "Store banana 1 kg ₹40"
    ]
    
    print("Adding products via voice commands:")
    for cmd in voice_commands:
        result = process_voice_command(cmd)
        print(f"Command: '{cmd}'")
        print(f"  -> Parsed: {result['product_name']}, {result['quantity']} kg, ₹{result['price']}")
        print(f"  -> Action: {result['action']}")
        print()
    
    print("2. TESTING DIRECT CRUD OPERATIONS")
    print("=" * 50)
    
    # Test direct CRUD operations
    print("Adding products directly:")
    
    # Create products
    products_to_add = [
        Product(name="Mango", quantity=2.0, price_per_kg=80.0, category="Fruit"),
        Product(name="Carrot", quantity=1.5, price_per_kg=35.0, category="Vegetable"),
        Product(name="Rice", quantity=5.0, price_per_kg=45.0, category="Grain")
    ]
    
    for product in products_to_add:
        saved = await save_product(product)
        print(f"Added: {product.name} - {product.quantity} kg at ₹{product.price_per_kg}")
    
    print()
    
    # Test READ operations
    print("Reading all products:")
    all_products = await get_all_products()
    print(f"Total products in system: {len(all_products)}")
    for product in all_products:
        print(f"  - {product['name']}: {product['quantity']} kg at ₹{product['price_per_kg']}/kg")
    
    print()
    
    # Test SEARCH operations
    print("Searching for specific products:")
    search_terms = ["tomato", "rice", "apple"]
    for term in search_terms:
        found = await find_product(term)
        if found:
            print(f"Found {term}: {found['name']} - {found['quantity']} kg at ₹{found['price_per_kg']}/kg")
        else:
            print(f"Product '{term}' not found")
    
    print()
    
    # Test UPDATE operations
    print("Updating product prices:")
    updates = [
        ("tomato", {"price_per_kg": 28.0}),
        ("apple", {"price_per_kg": 55.0}),
        ("rice", {"quantity": 10.0, "price_per_kg": 42.0})
    ]
    
    for product_name, update_data in updates:
        updated = await update_product(product_name, update_data)
        if updated:
            print(f"Updated {product_name}: {update_data}")
        else:
            print(f"Failed to update {product_name}")
    
    print()
    
    # Test voice command updates
    print("Testing voice command updates:")
    update_commands = [
        "Update tomato price to ₹25",
        "Change apple price to ₹60",
        "Modify banana quantity to 2 kg"
    ]
    
    for cmd in update_commands:
        result = process_voice_command(cmd)
        print(f"Command: '{cmd}'")
        print(f"  -> Action: {result['action']}")
        print(f"  -> Product: {result['product_name']}")
        if result.get('price'):
            print(f"  -> New Price: ₹{result['price']}")
        if result.get('quantity'):
            print(f"  -> New Quantity: {result['quantity']} kg")
    
    print()
    
    # Test DELETE operations
    print("Deleting products:")
    products_to_delete = ["banana", "onion"]
    
    for product_name in products_to_delete:
        deleted = await delete_product(product_name)
        if deleted:
            print(f"Deleted: {product_name}")
        else:
            print(f"Failed to delete: {product_name}")
    
    print()
    
    # Test voice command delete
    print("Testing voice command delete:")
    delete_commands = [
        "Remove apple",
        "Delete potato"
    ]
    
    for cmd in delete_commands:
        result = process_voice_command(cmd)
        print(f"Command: '{cmd}'")
        print(f"  -> Action: {result['action']}")
        print(f"  -> Product: {result['product_name']}")
    
    print()
    
    # Final inventory check
    print("Final inventory:")
    final_products = await get_all_products()
    print(f"Remaining products: {len(final_products)}")
    for product in final_products:
        print(f"  - {product['name']}: {product['quantity']} kg at ₹{product['price_per_kg']}/kg")
    
    print()
    
    print("3. TESTING MULTI-LANGUAGE SUPPORT")
    print("=" * 50)
    
    # Test regional language product names
    regional_commands = [
        "Add tamatar 1 kg ₹25",  # Hindi name for tomato
        "Update aloo price to ₹30",  # Hindi name for potato  
        "Search for pyaz",  # Hindi name for onion
        "Add gobi 1 kg ₹40",  # Hindi name for cauliflower
        "Update bhindi price to ₹35",  # Hindi name for okra
        "Search for doodh",  # Hindi name for milk
    ]
    
    print("Testing regional language commands:")
    for cmd in regional_commands:
        result = process_voice_command(cmd)
        print(f"Command: '{cmd}'")
        print(f"  -> Action: {result['action']}")
        print(f"  -> Product: {result['product_name']}")
        if result.get('price'):
            print(f"  -> Price: ₹{result['price']}")
        if result.get('quantity'):
            print(f"  -> Quantity: {result['quantity']} kg")
        print()
    
    print("4. TESTING ADVANCED PATTERNS")
    print("=" * 50)
    
    advanced_commands = [
        "I want to add 2 kg of mangoes at 80 rupees per kg",
        "Please update the price of onions to 25 rupees",
        "Can you show me all the vegetables in stock?",
        "Remove oranges from the inventory",
        "What is the stock of rice?",
        "How much tomato do we have?"
    ]
    
    print("Testing advanced natural language patterns:")
    for cmd in advanced_commands:
        result = process_voice_command(cmd)
        print(f"Command: '{cmd}'")
        print(f"  -> Action: {result.get('action', 'N/A')}")
        print(f"  -> Product: {result.get('product_name', 'N/A')}")
        if result.get('price'):
            print(f"  -> Price: ₹{result['price']}")
        if result.get('quantity'):
            print(f"  -> Quantity: {result['quantity']} kg")
        print(f"  -> Confidence: {result.get('confidence', 0):.2f}")
        print()

if __name__ == "__main__":
    asyncio.run(test_enhanced_crud_system())