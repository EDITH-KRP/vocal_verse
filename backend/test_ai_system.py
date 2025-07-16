#!/usr/bin/env python3
"""
AI Inventory Management System Demo Script

This script demonstrates the enhanced features of the AI inventory management system:
1. Smart product merging with price averaging
2. Voice command processing with AI
3. Analytics and trend analysis
4. AI-powered suggestions
5. Automatic background processing
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import time

API_BASE_URL = "http://localhost:8000/api"

async def test_voice_commands():
    """Test voice command processing with smart merging"""
    
    print("🎙️  Testing Voice Command Processing with Smart Merging")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Add initial tomato stock
        print("\n1. Adding initial tomato stock...")
        command1 = {
            "command": "add 5 kg tomato at 50 rupees",
            "language": "en"
        }
        
        async with session.post(f"{API_BASE_URL}/voice-command", json=command1) as response:
            result1 = await response.json()
            print(f"   Result: {result1.get('message', 'No message')}")
            print(f"   Action: {result1.get('action', 'No action')}")
            print(f"   Quantity: {result1.get('quantity', 0)} kg")
            print(f"   Price: ₹{result1.get('price_per_kg', 0)}/kg")
        
        # Test 2: Add more tomato stock (should merge with price averaging)
        print("\n2. Adding more tomato stock (should merge with price averaging)...")
        command2 = {
            "command": "add 3 kg tomato at 60 rupees",
            "language": "en"
        }
        
        async with session.post(f"{API_BASE_URL}/voice-command", json=command2) as response:
            result2 = await response.json()
            print(f"   Result: {result2.get('message', 'No message')}")
            print(f"   Action: {result2.get('action', 'No action')}")
            print(f"   Total Quantity: {result2.get('quantity', 0)} kg")
            print(f"   Averaged Price: ₹{result2.get('price_per_kg', 0)}/kg")
            print(f"   Expected Average: ₹{((5*50) + (3*60)) / (5+3):.2f}/kg")
        
        # Test 3: Hindi voice command
        print("\n3. Testing Hindi voice command...")
        command3 = {
            "command": "2 किलो प्याज 40 रुपये में जोड़ो",
            "language": "hi"
        }
        
        async with session.post(f"{API_BASE_URL}/voice-command", json=command3) as response:
            result3 = await response.json()
            print(f"   Result: {result3.get('message', 'No message')}")
            print(f"   Action: {result3.get('action', 'No action')}")
        
        # Test 4: Kannada voice command
        print("\n4. Testing Kannada voice command...")
        command4 = {
            "command": "1 ಕಿಲೋ ಅಕ್ಕಿ 80 ರೂಪಾಯಿ ಸೇರಿಸಿ",
            "language": "kn"
        }
        
        async with session.post(f"{API_BASE_URL}/voice-command", json=command4) as response:
            result4 = await response.json()
            print(f"   Result: {result4.get('message', 'No message')}")
            print(f"   Action: {result4.get('action', 'No action')}")

async def test_analytics_dashboard():
    """Test analytics dashboard"""
    
    print("\n📊 Testing Analytics Dashboard")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/analytics/dashboard") as response:
            dashboard = await response.json()
            
            print("\n📈 Dashboard Summary:")
            summary = dashboard.get('summary', {})
            print(f"   Total Products: {summary.get('total_products', 0)}")
            print(f"   Total Inventory Value: ₹{summary.get('total_inventory_value', 0)}")
            print(f"   Low Stock Alerts: {summary.get('low_stock_alerts', 0)}")
            print(f"   Total Transactions: {summary.get('total_transactions', 0)}")
            
            print("\n🔥 Top Products:")
            top_products = dashboard.get('top_products', {})
            for product, quantity in list(top_products.items())[:3]:
                print(f"   {product}: {quantity} kg added")
            
            print("\n🌐 Language Usage:")
            lang_stats = dashboard.get('language_usage', {})
            for lang, count in lang_stats.items():
                lang_names = {'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada', 'ta': 'Tamil', 'te': 'Telugu'}
                print(f"   {lang_names.get(lang, lang)}: {count} commands")

async def test_ai_suggestions():
    """Test AI-powered suggestions"""
    
    print("\n🤖 Testing AI-Powered Suggestions")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Force generate new suggestions
        async with session.get(f"{API_BASE_URL}/suggestions?force_regenerate=true") as response:
            suggestions_data = await response.json()
            
            suggestions = suggestions_data.get('suggestions', [])
            high_priority = suggestions_data.get('high_priority', [])
            action_required = suggestions_data.get('action_required', [])
            
            print(f"\n💡 Total Suggestions: {len(suggestions)}")
            print(f"🔥 High Priority: {len(high_priority)}")
            print(f"⚠️  Action Required: {len(action_required)}")
            
            print("\n📋 Recent Suggestions:")
            for i, suggestion in enumerate(suggestions[:5], 1):
                priority_emoji = "🔥" if suggestion.get('priority', 0) >= 4 else "⚠️" if suggestion.get('priority', 0) >= 3 else "💡"
                print(f"   {i}. {priority_emoji} {suggestion.get('message', 'No message')}")
                if suggestion.get('suggested_action'):
                    print(f"      Suggested Action: {suggestion['suggested_action']}")
                print(f"      Priority: {suggestion.get('priority', 0)}/5")
                print()

async def test_trend_analysis():
    """Test trend analysis"""
    
    print("\n📈 Testing Trend Analysis")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/analytics/trends") as response:
            trends_data = await response.json()
            
            trends = trends_data.get('trends', [])
            
            if trends:
                print(f"\n🔍 Found {len(trends)} trends:")
                for trend in trends:
                    trend_emoji = {
                        'price_increase': '📈',
                        'price_decrease': '📉',
                        'demand_increase': '🔥',
                        'demand_decrease': '❄️'
                    }.get(trend.get('trend_type', ''), '📊')
                    
                    print(f"   {trend_emoji} {trend.get('product_name', 'Unknown')}: {trend.get('trend_type', 'Unknown')}")
                    print(f"      Confidence: {trend.get('confidence', 0):.0%}")
                    if trend.get('predicted_value'):
                        print(f"      Predicted Value: ₹{trend['predicted_value']:.2f}")
                    print()
            else:
                print("\n📊 No significant trends detected yet (need more data)")

async def test_suggestion_execution():
    """Test automatic suggestion execution"""
    
    print("\n🚀 Testing Suggestion Execution")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Get suggestions with actions
        async with session.get(f"{API_BASE_URL}/suggestions") as response:
            suggestions_data = await response.json()
            
            action_required = suggestions_data.get('action_required', [])
            
            if action_required:
                suggestion = action_required[0]  # Take first actionable suggestion
                suggestion_id = suggestion.get('id')
                
                print(f"\n🎯 Executing suggestion: {suggestion.get('message', 'No message')}")
                print(f"   Action: {suggestion.get('suggested_action', 'No action')}")
                
                # Execute the suggestion
                async with session.post(f"{API_BASE_URL}/suggestions/{suggestion_id}/execute") as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"   ✅ Execution successful!")
                        print(f"   Result: {result.get('message', 'No message')}")
                    else:
                        error = await response.json()
                        print(f"   ❌ Execution failed: {error.get('detail', 'Unknown error')}")
            else:
                print("\n📝 No actionable suggestions available")

async def demo_multilingual_capabilities():
    """Demonstrate multilingual voice command processing"""
    
    print("\n🌍 Testing Multilingual Capabilities")
    print("=" * 60)
    
    test_commands = [
        {"command": "5 kg ಆಲೂಗಡ್ಡೆ 30 ರೂಪಾಯಿ ಸೇರಿಸಿ", "language": "kn", "description": "Add 5 kg potato at ₹30 (Kannada)"},
        {"command": "3 கிலோ தக்காளி 45 ரூபாய் சேர்", "language": "ta", "description": "Add 3 kg tomato at ₹45 (Tamil)"},
        {"command": "2 కిలో ఉల్లిపాయ 35 రూపాయలు చేర్చు", "language": "te", "description": "Add 2 kg onion at ₹35 (Telugu)"},
        {"command": "1 किलो चावल 60 रुपये में जोड़ो", "language": "hi", "description": "Add 1 kg rice at ₹60 (Hindi)"}
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test in enumerate(test_commands, 1):
            print(f"\n{i}. {test['description']}")
            print(f"   Command: \"{test['command']}\"")
            
            async with session.post(f"{API_BASE_URL}/voice-command", json=test) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Success: {result.get('message', 'No message')}")
                    if result.get('action') == 'merged':
                        print(f"   🔄 Product merged with existing stock")
                else:
                    error = await response.json()
                    print(f"   ❌ Error: {error.get('detail', 'Unknown error')}")

async def main():
    """Main demo function"""
    
    print("🎯 AI-Powered Voice Inventory Management System Demo")
    print("=" * 80)
    print("This demo showcases the enhanced features:")
    print("• Smart product merging with price averaging")
    print("• AI-powered voice command processing")
    print("• Real-time analytics and trend analysis")
    print("• Multilingual support (English, Hindi, Kannada, Tamil, Telugu)")
    print("• Automated AI suggestions and execution")
    print("• Background data analytics")
    print("=" * 80)
    
    try:
        # Test all features
        await test_voice_commands()
        await asyncio.sleep(2)
        
        await demo_multilingual_capabilities()
        await asyncio.sleep(2)
        
        await test_analytics_dashboard()
        await asyncio.sleep(2)
        
        await test_ai_suggestions()
        await asyncio.sleep(2)
        
        await test_trend_analysis()
        await asyncio.sleep(2)
        
        await test_suggestion_execution()
        
        print("\n🎉 Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ Smart product merging with weighted price averaging")
        print("✅ Multilingual voice command processing")
        print("✅ Real-time AI suggestions")
        print("✅ Trend analysis with statistical confidence")
        print("✅ Automated suggestion execution")
        print("✅ Comprehensive analytics dashboard")
        
    except aiohttp.ClientConnectorError:
        print("\n❌ Error: Could not connect to the API server.")
        print("Please make sure the FastAPI server is running on http://localhost:8000")
        print("Run: python backend/server.py")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())#!/usr/bin/env python3
"""
AI Inventory Management System Demo Script

This script demonstrates the enhanced features of the AI inventory management system:
1. Smart product merging with price averaging
2. Voice command processing with AI
3. Analytics and trend analysis
4. AI-powered suggestions
5. Automatic background processing
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import time

API_BASE_URL = "http://localhost:8000/api"

async def test_voice_commands():
    """Test voice command processing with smart merging"""
    
    print("🎙️  Testing Voice Command Processing with Smart Merging")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Add initial tomato stock
        print("\n1. Adding initial tomato stock...")
        command1 = {
            "command": "add 5 kg tomato at 50 rupees",
            "language": "en"
        }
        
        async with session.post(f"{API_BASE_URL}/voice-command", json=command1) as response:
            result1 = await response.json()
            print(f"   Result: {result1.get('message', 'No message')}")
            print(f"   Action: {result1.get('action', 'No action')}")
            print(f"   Quantity: {result1.get('quantity', 0)} kg")
            print(f"   Price: ₹{result1.get('price_per_kg', 0)}/kg")
        
        # Test 2: Add more tomato stock (should merge with price averaging)
        print("\n2. Adding more tomato stock (should merge with price averaging)...")
        command2 = {
            "command": "add 3 kg tomato at 60 rupees",
            "language": "en"
        }
        
        async with session.post(f"{API_BASE_URL}/voice-command", json=command2) as response:
            result2 = await response.json()
            print(f"   Result: {result2.get('message', 'No message')}")
            print(f"   Action: {result2.get('action', 'No action')}")
            print(f"   Total Quantity: {result2.get('quantity', 0)} kg")
            print(f"   Averaged Price: ₹{result2.get('price_per_kg', 0)}/kg")
            print(f"   Expected Average: ₹{((5*50) + (3*60)) / (5+3):.2f}/kg")
        
        # Test 3: Hindi voice command
        print("\n3. Testing Hindi voice command...")
        command3 = {
            "command": "2 किलो प्याज 40 रुपये में जोड़ो",
            "language": "hi"
        }
        
        async with session.post(f"{API_BASE_URL}/voice-command", json=command3) as response:
            result3 = await response.json()
            print(f"   Result: {result3.get('message', 'No message')}")
            print(f"   Action: {result3.get('action', 'No action')}")
        
        # Test 4: Kannada voice command
        print("\n4. Testing Kannada voice command...")
        command4 = {
            "command": "1 ಕಿಲೋ ಅಕ್ಕಿ 80 ರೂಪಾಯಿ ಸೇರಿಸಿ",
            "language": "kn"
        }
        
        async with session.post(f"{API_BASE_URL}/voice-command", json=command4) as response:
            result4 = await response.json()
            print(f"   Result: {result4.get('message', 'No message')}")
            print(f"   Action: {result4.get('action', 'No action')}")

async def test_analytics_dashboard():
    """Test analytics dashboard"""
    
    print("\n📊 Testing Analytics Dashboard")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/analytics/dashboard") as response:
            dashboard = await response.json()
            
            print("\n📈 Dashboard Summary:")
            summary = dashboard.get('summary', {})
            print(f"   Total Products: {summary.get('total_products', 0)}")
            print(f"   Total Inventory Value: ₹{summary.get('total_inventory_value', 0)}")
            print(f"   Low Stock Alerts: {summary.get('low_stock_alerts', 0)}")
            print(f"   Total Transactions: {summary.get('total_transactions', 0)}")
            
            print("\n🔥 Top Products:")
            top_products = dashboard.get('top_products', {})
            for product, quantity in list(top_products.items())[:3]:
                print(f"   {product}: {quantity} kg added")
            
            print("\n🌐 Language Usage:")
            lang_stats = dashboard.get('language_usage', {})
            for lang, count in lang_stats.items():
                lang_names = {'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada', 'ta': 'Tamil', 'te': 'Telugu'}
                print(f"   {lang_names.get(lang, lang)}: {count} commands")

async def test_ai_suggestions():
    """Test AI-powered suggestions"""
    
    print("\n🤖 Testing AI-Powered Suggestions")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Force generate new suggestions
        async with session.get(f"{API_BASE_URL}/suggestions?force_regenerate=true") as response:
            suggestions_data = await response.json()
            
            suggestions = suggestions_data.get('suggestions', [])
            high_priority = suggestions_data.get('high_priority', [])
            action_required = suggestions_data.get('action_required', [])
            
            print(f"\n💡 Total Suggestions: {len(suggestions)}")
            print(f"🔥 High Priority: {len(high_priority)}")
            print(f"⚠️  Action Required: {len(action_required)}")
            
            print("\n📋 Recent Suggestions:")
            for i, suggestion in enumerate(suggestions[:5], 1):
                priority_emoji = "🔥" if suggestion.get('priority', 0) >= 4 else "⚠️" if suggestion.get('priority', 0) >= 3 else "💡"
                print(f"   {i}. {priority_emoji} {suggestion.get('message', 'No message')}")
                if suggestion.get('suggested_action'):
                    print(f"      Suggested Action: {suggestion['suggested_action']}")
                print(f"      Priority: {suggestion.get('priority', 0)}/5")
                print()

async def test_trend_analysis():
    """Test trend analysis"""
    
    print("\n📈 Testing Trend Analysis")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/analytics/trends") as response:
            trends_data = await response.json()
            
            trends = trends_data.get('trends', [])
            
            if trends:
                print(f"\n🔍 Found {len(trends)} trends:")
                for trend in trends:
                    trend_emoji = {
                        'price_increase': '📈',
                        'price_decrease': '📉',
                        'demand_increase': '🔥',
                        'demand_decrease': '❄️'
                    }.get(trend.get('trend_type', ''), '📊')
                    
                    print(f"   {trend_emoji} {trend.get('product_name', 'Unknown')}: {trend.get('trend_type', 'Unknown')}")
                    print(f"      Confidence: {trend.get('confidence', 0):.0%}")
                    if trend.get('predicted_value'):
                        print(f"      Predicted Value: ₹{trend['predicted_value']:.2f}")
                    print()
            else:
                print("\n📊 No significant trends detected yet (need more data)")

async def test_suggestion_execution():
    """Test automatic suggestion execution"""
    
    print("\n🚀 Testing Suggestion Execution")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Get suggestions with actions
        async with session.get(f"{API_BASE_URL}/suggestions") as response:
            suggestions_data = await response.json()
            
            action_required = suggestions_data.get('action_required', [])
            
            if action_required:
                suggestion = action_required[0]  # Take first actionable suggestion
                suggestion_id = suggestion.get('id')
                
                print(f"\n🎯 Executing suggestion: {suggestion.get('message', 'No message')}")
                print(f"   Action: {suggestion.get('suggested_action', 'No action')}")
                
                # Execute the suggestion
                async with session.post(f"{API_BASE_URL}/suggestions/{suggestion_id}/execute") as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"   ✅ Execution successful!")
                        print(f"   Result: {result.get('message', 'No message')}")
                    else:
                        error = await response.json()
                        print(f"   ❌ Execution failed: {error.get('detail', 'Unknown error')}")
            else:
                print("\n📝 No actionable suggestions available")

async def demo_multilingual_capabilities():
    """Demonstrate multilingual voice command processing"""
    
    print("\n🌍 Testing Multilingual Capabilities")
    print("=" * 60)
    
    test_commands = [
        {"command": "5 kg ಆಲೂಗಡ್ಡೆ 30 ರೂಪಾಯಿ ಸೇರಿಸಿ", "language": "kn", "description": "Add 5 kg potato at ₹30 (Kannada)"},
        {"command": "3 கிலோ தக்காளி 45 ரூபாய் சேர்", "language": "ta", "description": "Add 3 kg tomato at ₹45 (Tamil)"},
        {"command": "2 కిలో ఉల్లిపాయ 35 రూపాయలు చేర్చు", "language": "te", "description": "Add 2 kg onion at ₹35 (Telugu)"},
        {"command": "1 किलो चावल 60 रुपये में जोड़ो", "language": "hi", "description": "Add 1 kg rice at ₹60 (Hindi)"}
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test in enumerate(test_commands, 1):
            print(f"\n{i}. {test['description']}")
            print(f"   Command: \"{test['command']}\"")
            
            async with session.post(f"{API_BASE_URL}/voice-command", json=test) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Success: {result.get('message', 'No message')}")
                    if result.get('action') == 'merged':
                        print(f"   🔄 Product merged with existing stock")
                else:
                    error = await response.json()
                    print(f"   ❌ Error: {error.get('detail', 'Unknown error')}")

async def main():
    """Main demo function"""
    
    print("🎯 AI-Powered Voice Inventory Management System Demo")
    print("=" * 80)
    print("This demo showcases the enhanced features:")
    print("• Smart product merging with price averaging")
    print("• AI-powered voice command processing")
    print("• Real-time analytics and trend analysis")
    print("• Multilingual support (English, Hindi, Kannada, Tamil, Telugu)")
    print("• Automated AI suggestions and execution")
    print("• Background data analytics")
    print("=" * 80)
    
    try:
        # Test all features
        await test_voice_commands()
        await asyncio.sleep(2)
        
        await demo_multilingual_capabilities()
        await asyncio.sleep(2)
        
        await test_analytics_dashboard()
        await asyncio.sleep(2)
        
        await test_ai_suggestions()
        await asyncio.sleep(2)
        
        await test_trend_analysis()
        await asyncio.sleep(2)
        
        await test_suggestion_execution()
        
        print("\n🎉 Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ Smart product merging with weighted price averaging")
        print("✅ Multilingual voice command processing")
        print("✅ Real-time AI suggestions")
        print("✅ Trend analysis with statistical confidence")
        print("✅ Automated suggestion execution")
        print("✅ Comprehensive analytics dashboard")
        
    except aiohttp.ClientConnectorError:
        print("\n❌ Error: Could not connect to the API server.")
        print("Please make sure the FastAPI server is running on http://localhost:8000")
        print("Run: python backend/server.py")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())