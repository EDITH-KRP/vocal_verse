#!/usr/bin/env python3
"""
Test script for enhanced AI voice command processing
Tests various voice command patterns to ensure accuracy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import process_voice_command

def test_voice_commands():
    """Test various voice command patterns"""
    
    test_cases = [
        # Basic add commands
        "Orange one KG ₹50",
        "Add tomato 2 kg at 30 rupees",
        "Apple 1.5 kg ₹80",
        "Banana two kg 40 rupees",
        "Add onion 3 kg at ₹25",
        
        # Different price formats
        "Potato 5 kg ₹20",
        "Rice 10 kg at 60 rupees",
        "Milk 2 kg for ₹45",
        "Sugar 1 kg price 35 rupees",
        "Oil half kg ₹120",
        
        # Without explicit "add"
        "Carrot 2 kg ₹40",
        "Chicken 1 kg ₹200",
        "Fish 1.5 kg ₹150",
        
        # List and search commands
        "List all products",
        "Show all items",
        "Search for tomato",
        "Find apple",
        
        # Update commands
        "Update tomato price to 35 rupees",
        "Change onion price to ₹30",
        
        # Remove commands
        "Remove tomato",
        "Delete apple",
        
        # Edge cases
        "Bitter gourd 1 kg ₹60",
        "Green beans 2 kg at 45 rupees",
        "Bottle gourd half kg ₹25",
        
        # Incomplete commands
        "Add tomato 2 kg",  # Missing price
        "Orange ₹50",       # Missing quantity
        "Add something",    # Missing everything
    ]
    
    print("🧪 Testing Enhanced AI Voice Command Processing")
    print("=" * 60)
    
    for i, command in enumerate(test_cases, 1):
        print(f"\n{i:2d}. Testing: '{command}'")
        result = process_voice_command(command)
        
        print(f"    Action: {result.get('action', 'None')}")
        print(f"    Product: {result.get('product_name', 'None')}")
        print(f"    Quantity: {result.get('quantity', 'None')} kg")
        print(f"    Price: ₹{result.get('price', 'None')}")
        print(f"    Confidence: {result.get('confidence', 0):.2f}")
        print(f"    Message: {result.get('message', 'None')}")
        
        # Highlight successful extractions
        if result.get('action') == 'add' and result.get('product_name') and result.get('quantity') and result.get('price'):
            print("    ✅ COMPLETE - All information extracted successfully!")
        elif result.get('action') == 'incomplete':
            print("    ⚠️  INCOMPLETE - Missing information")
        elif result.get('action') in ['list', 'search', 'update', 'remove']:
            print("    ✅ VALID - Command recognized")
        else:
            print("    ❌ FAILED - Command not properly processed")

def test_specific_patterns():
    """Test specific patterns mentioned in the request"""
    
    print("\n\n🎯 Testing Specific Patterns")
    print("=" * 40)
    
    specific_tests = [
        "Orange one KG ₹50",
        "orange 1 kg 50 rupees",
        "ORANGE ONE KILOGRAM FIFTY RUPEES",
        "Add orange one kg at fifty rupees",
    ]
    
    for command in specific_tests:
        print(f"\nTesting: '{command}'")
        result = process_voice_command(command)
        
        expected_product = "orange"
        expected_quantity = 1.0
        expected_price = 50.0
        
        success = (
            result.get('product_name') == expected_product and
            result.get('quantity') == expected_quantity and
            result.get('price') == expected_price
        )
        
        print(f"Expected: {expected_product}, {expected_quantity} kg, ₹{expected_price}")
        print(f"Got: {result.get('product_name')}, {result.get('quantity')} kg, ₹{result.get('price')}")
        print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")

if __name__ == "__main__":
    test_voice_commands()
    test_specific_patterns()
    
    print("\n\n🎉 Testing Complete!")
    print("The enhanced AI should now accurately extract:")
    print("- Product names (with expanded database)")
    print("- Quantities (digits and word numbers)")
    print("- Prices (multiple formats)")
    print("- Actions (explicit or inferred)")