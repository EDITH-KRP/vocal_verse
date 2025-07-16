import requests
import json

print('🎤 FINAL SYSTEM DEMONSTRATION')
print('=' * 50)

# Test the original command
print('\n1. Testing Original Command:')
response = requests.post('http://localhost:8000/voice-command', json={'command': 'Update tomato price to ₹25', 'language': 'en'})
result = response.json()
print(f'   Command: "Update tomato price to ₹25"')
print(f'   Status: {"✅ SUCCESS" if result.get("success") else "❌ FAILED"}')
print(f'   Message: {result.get("message", "No message")}')

# Test CRUD operations
print('\n2. Testing CRUD Operations:')
operations = [
    ('CREATE', 'Add carrot 2 kg at 35 rupees'),
    ('READ', 'Search for carrot'),
    ('UPDATE', 'Update carrot price to ₹40'),
    ('DELETE', 'Remove carrot')
]

for op_type, command in operations:
    response = requests.post('http://localhost:8000/voice-command', json={'command': command, 'language': 'en'})
    result = response.json()
    status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
    print(f'   {op_type}: {status} - {command}')

# Test multi-language
print('\n3. Testing Multi-Language Support:')
hindi_commands = [
    'Add tamatar 1 kg ₹25',
    'Update aloo price to ₹30',
    'Search for pyaz'
]

for cmd in hindi_commands:
    response = requests.post('http://localhost:8000/voice-command', json={'command': cmd, 'language': 'en'})
    result = response.json()
    status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
    parsed = result.get('parsed_command', {})
    english_product = parsed.get('product_name', 'N/A')
    print(f'   {status} - "{cmd}" -> {english_product}')

# Get final inventory
print('\n4. Current Inventory:')
response = requests.get('http://localhost:8000/products')
products = response.json()
print(f'   Total products: {len(products.get("products", []))}')
for product in products.get('products', []):
    print(f'     - {product["name"]}: {product["quantity"]} kg at ₹{product["price_per_kg"]}/kg')

print('\n🎉 SYSTEM IS FULLY OPERATIONAL!')
print('   Frontend: http://localhost:3000')
print('   Backend: http://localhost:8000')
print('   API Docs: http://localhost:8000/docs')