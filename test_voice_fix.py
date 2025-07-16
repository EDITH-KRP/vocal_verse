#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from supabase_server import process_voice_command

def test_voice_commands():
    """Test voice command processing"""
    
    print("🎤 Testing Voice Command Processing")
    print("=" * 50)
    
    # Test commands with different completeness levels
    test_commands = [
        # Complete commands
        "Add tomato 2 kg at ₹20 per kilogram",
        "Add apple 1 kg at ₹50 per kg",
        "Add onion 3 kg at ₹30 per kilogram",
        
        # Missing quantity (your specific case)
        "Add tomato ₹20 per kilogram",
        "Add apple ₹50 per kg",
        
        # Missing price
        "Add tomato 2 kg",
        "Add apple 1 kg",
        
        # Missing both
        "Add tomato",
        "Add apple",
        
        # Different formats
        "Add 2 tomato at ₹20",
        "Add two kg apple at ₹50",
        "Add half kg onion at ₹30",
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. Testing: '{command}'")
        try:
            result = process_voice_command(command, "en")
            print(f"   Action: {result.get('action', 'None')}")
            print(f"   Product: {result.get('product_name', 'None')}")
            print(f"   Quantity: {result.get('quantity', 'None')} kg")
            print(f"   Price: ₹{result.get('price', 'None')}")
            
            # Check completeness
            if result.get('action') == 'add' and result.get('product_name'):
                if result.get('quantity') and result.get('price'):
                    print("   ✅ COMPLETE - Ready to process")
                else:
                    missing = []
                    if not result.get('quantity'):
                        missing.append("quantity")
                    if not result.get('price'):
                        missing.append("price")
                    print(f"   ⚠️  INCOMPLETE - Missing: {', '.join(missing)}")
            else:
                print("   ❌ FAILED - Action or product not recognized")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    test_voice_commands()