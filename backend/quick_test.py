from server import process_voice_command

print("=== ENHANCED VOICE COMMAND PROCESSING WITH MULTI-LANGUAGE SUPPORT ===")
print()

# Test the specific command mentioned
result = process_voice_command('Orange one KG ₹50')
print("Command: 'Orange one KG ₹50'")
print(f"Action: {result.get('action')}")
print(f"Product: {result.get('product_name')}")
print(f"Quantity: {result.get('quantity')}")
print(f"Price: {result.get('price')}")
print(f"Message: {result.get('message')}")
print()

# Test CRUD operations
print("=== CRUD OPERATIONS TESTING ===")
crud_test_cases = [
    # Add operations
    'Add Apple two kg fifty rupees',
    'Create Banana half kg ₹30',
    'Store Tomato 1 kg ₹25',
    
    # Update operations
    'Update tomato price to ₹25',
    'Change apple price to ₹60',
    'Modify banana quantity to 2 kg',
    
    # Search operations
    'Search for apple',
    'Find tomato',
    'Show banana',
    
    # List operations
    'List all products',
    'Show all items',
    
    # Stock operations
    'Stock of apple',
    'How much tomato',
    
    # Delete operations
    'Remove apple',
    'Delete banana',
]

for cmd in crud_test_cases:
    result = process_voice_command(cmd)
    print(f"Command: '{cmd}'")
    print(f"  -> Action: {result.get('action')}")
    print(f"  -> Product: {result.get('product_name')}")
    if result.get('quantity'):
        print(f"  -> Quantity: {result.get('quantity')} kg")
    if result.get('price'):
        print(f"  -> Price: ₹{result.get('price')}")
    print(f"  -> Message: {result.get('message')}")
    print()

print("=== MULTI-LANGUAGE SUPPORT TESTING ===")
# Test multi-language commands (these would work with Google Translate)
multilingual_test_cases = [
    # Hindi commands (examples - would need actual Hindi text)
    'टमाटर एक किलो पचीस रुपये',  # Tomato 1 kg 25 rupees
    'आलू दो किलो तीस रुपये',     # Potato 2 kg 30 rupees
    'सेब आधा किलो चालीस रुपये',  # Apple half kg 40 rupees
    
    # Mixed language commands
    'Add tamatar 1 kg ₹25',
    'Update aloo price to ₹30',
    'Search for pyaz',
]

print("Multi-language commands (with translation):")
for cmd in multilingual_test_cases:
    try:
        result = process_voice_command(cmd)
        print(f"Command: '{cmd}'")
        print(f"  -> Action: {result.get('action')}")
        print(f"  -> Product: {result.get('product_name')}")
        if result.get('quantity'):
            print(f"  -> Quantity: {result.get('quantity')} kg")
        if result.get('price'):
            print(f"  -> Price: ₹{result.get('price')}")
        print(f"  -> Message: {result.get('message')}")
        print()
    except Exception as e:
        print(f"Command: '{cmd}' - Error: {e}")
        print()

print("=== ADVANCED PATTERN TESTING ===")
advanced_test_cases = [
    # Complex sentences
    'I want to add 2 kg of mangoes at 80 rupees per kg',
    'Please update the price of onions to 25 rupees',
    'Can you show me all the vegetables in stock?',
    'Remove oranges from the inventory',
    
    # Price format variations
    'Grapes 1.5 kg Rs 120',
    'Watermelon 3 kg rupees 90',
    'Lemon quarter kg ₹15',
    
    # Regional variations
    'Add gobi 1 kg ₹40',
    'Update bhindi price to ₹35',
    'Search for doodh',
]

for cmd in advanced_test_cases:
    result = process_voice_command(cmd)
    print(f"Command: '{cmd}'")
    print(f"  -> Action: {result.get('action')}")
    print(f"  -> Product: {result.get('product_name')}")
    if result.get('quantity'):
        print(f"  -> Quantity: {result.get('quantity')} kg")
    if result.get('price'):
        print(f"  -> Price: ₹{result.get('price')}")
    print(f"  -> Confidence: {result.get('confidence', 0):.2f}")
    print(f"  -> Message: {result.get('message')}")
    print()