from server import process_voice_command

# Test the specific command mentioned
result = process_voice_command('Orange one KG ₹50')
print("Command: 'Orange one KG ₹50'")
print(f"Action: {result.get('action')}")
print(f"Product: {result.get('product_name')}")
print(f"Quantity: {result.get('quantity')}")
print(f"Price: {result.get('price')}")
print(f"Message: {result.get('message')}")
print()

# Test a few more
test_cases = [
    'Apple two kg fifty rupees',
    'Banana half kg ₹30',
    'Tomato 1 kg ₹25'
]

for cmd in test_cases:
    result = process_voice_command(cmd)
    print(f"Command: '{cmd}'")
    print(f"  -> {result.get('product_name')}, {result.get('quantity')} kg, ₹{result.get('price')}")
    print(f"  -> Action: {result.get('action')}")
    print()