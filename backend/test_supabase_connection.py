#!/usr/bin/env python3
"""
Test Supabase connection and create schema if needed
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def test_connection():
    """Test Supabase connection"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Test basic connection
        print("🔗 Testing Supabase connection...")
        
        print("✅ Supabase client created successfully!")
        
        # Check if our tables exist
        print("\n📋 Checking if tables exist...")
        
        tables_to_check = ['users', 'products', 'inventory_transactions', 'voice_commands', 'stock_alerts']
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' does not exist or has issues: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

def create_schema():
    """Create the database schema"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        print("\n🔧 Creating database schema...")
        
        # Read the schema file
        with open('supabase_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema (note: this might not work directly with supabase-py)
        # You'll need to run this in the Supabase SQL Editor
        print("⚠️  Please run the following SQL in your Supabase SQL Editor:")
        print("=" * 60)
        print(schema_sql[:500] + "...")
        print("=" * 60)
        print("📖 Full schema is in 'supabase_schema.sql' file")
        
    except Exception as e:
        print(f"❌ Error reading schema: {str(e)}")

if __name__ == "__main__":
    print("🚀 Supabase Connection Test")
    print("=" * 40)
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Missing environment variables!")
        print("Please check your .env file has:")
        print("- SUPABASE_URL")
        print("- SUPABASE_SERVICE_ROLE_KEY")
        exit(1)
    
    print(f"🌐 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 Service Key: {SUPABASE_SERVICE_ROLE_KEY[:20]}...")
    
    if test_connection():
        print("\n🎉 Connection test passed!")
        print("\n💡 If tables don't exist, please:")
        print("1. Go to your Supabase dashboard")
        print("2. Open the SQL Editor")
        print("3. Copy and run the content of 'supabase_schema.sql'")
    else:
        print("\n❌ Connection test failed!")
        print("Please check your Supabase credentials and try again.")