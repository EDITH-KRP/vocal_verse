from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime, timedelta
import re
import math
import json
import asyncio
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection with fallback
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = None
db = None

# In-memory storage fallback
products_store = []

# Analytics and AI suggestions storage
analytics_store = []
suggestions_store = []
user_behavior_store = []
market_trends_store = []

# Initialize Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        print("Gemini AI initialized successfully")
    except ImportError:
        model = None
        print("google-generativeai not installed, using fallback parsing")
else:
    model = None
    print("Gemini API key not found, using fallback parsing")

# Test MongoDB connection at startup
async def test_mongodb_connection():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client.voice_catalog
        # Test the connection
        await client.admin.command('ping')
        print("MongoDB connection successful")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Using in-memory storage for testing")
        client = None
        db = None
        return False

# Basic data models
class Product(BaseModel):
    name: str
    quantity: float
    price_per_kg: float
    description: Optional[str] = ""
    category: Optional[str] = "general"

class ProductUpdate(BaseModel):
    name: str
    quantity: Optional[float] = None
    price_per_kg: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None

class VoiceCommand(BaseModel):
    command: str
    language: Optional[str] = "en"

class AnalyticsData(BaseModel):
    product_name: str
    action: str
    quantity: Optional[float] = None
    price: Optional[float] = None
    timestamp: Optional[datetime] = None

# Basic voice processing function
def process_voice_command(command: str, language: str = "en") -> dict:
    """
    Process voice command and extract action and product information
    """
    command = command.lower().strip()
    
    # Simple pattern matching for basic commands
    patterns = {
        'add': r'add|create|insert|new',
        'update': r'update|change|modify|edit',
        'remove': r'remove|delete|del',
        'list': r'list|show|display|get all',
        'search': r'search|find|get|show'
    }
    
    action = None
    for act, pattern in patterns.items():
        if re.search(pattern, command):
            action = act
            break
    
    if not action:
        return {"action": "unknown", "message": "Command not recognized"}
    
    # Extract product name (simplified)
    product_name = None
    quantity = None
    price = None
    
    # Look for common product names (expanded list)
    products = [
        'tomato', 'onion', 'potato', 'rice', 'milk', 'sugar', 'banana', 'apple', 'carrot',
        'wheat', 'dal', 'oil', 'salt', 'tea', 'coffee', 'bread', 'eggs', 'chicken', 'mutton',
        'fish', 'spinach', 'cabbage', 'cauliflower', 'beans', 'peas', 'corn', 'garlic',
        'ginger', 'lemon', 'orange', 'mango', 'grapes', 'watermelon', 'cucumber', 'bitter gourd',
        'bottle gourd', 'brinjal', 'okra', 'radish', 'beetroot', 'turnip', 'pumpkin'
    ]
    
    # Try to find product name in command
    for product in products:
        if product in command:
            product_name = product
            break
    
    # If no predefined product found, try to extract from command structure
    if not product_name:
        # Look for "add [product_name] [quantity]" pattern
        add_match = re.search(r'add\s+(\w+)\s+\d+', command)
        if add_match:
            product_name = add_match.group(1)
    
    # Extract quantity
    qty_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilo|kilogram)', command)
    if qty_match:
        quantity = float(qty_match.group(1))
    
    # Extract price (look for patterns like "at 35 rupees" or "₹35")
    price_match = re.search(r'(?:at\s+(\d+(?:\.\d+)?)\s*(?:rupees?|rs|₹)|₹\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:rupees?|rs))', command)
    if price_match:
        price = float(price_match.group(1) or price_match.group(2) or price_match.group(3))
    
    return {
        "action": action,
        "product_name": product_name,
        "quantity": quantity,
        "price": price,
        "raw_command": command
    }

# Database operations
async def save_product(product: Product):
    """Save product to MongoDB or in-memory storage"""
    if db:
        try:
            product_dict = product.dict()
            product_dict['_id'] = str(uuid.uuid4())
            product_dict['created_at'] = datetime.now()
            await db.products.insert_one(product_dict)
            return product_dict
        except Exception as e:
            print(f"MongoDB save error: {e}")
    
    # Fallback to in-memory storage
    product_dict = product.dict()
    product_dict['_id'] = str(uuid.uuid4())
    product_dict['created_at'] = datetime.now()
    products_store.append(product_dict)
    return product_dict

async def get_all_products():
    """Get all products from MongoDB or in-memory storage"""
    if db:
        try:
            cursor = db.products.find({})
            products = []
            async for doc in cursor:
                doc['_id'] = str(doc['_id'])
                products.append(doc)
            return products
        except Exception as e:
            print(f"MongoDB get error: {e}")
    
    # Fallback to in-memory storage
    return products_store

async def find_product(name: str):
    """Find product by name"""
    if db:
        try:
            doc = await db.products.find_one({"name": {"$regex": name, "$options": "i"}})
            if doc:
                doc['_id'] = str(doc['_id'])
                return doc
        except Exception as e:
            print(f"MongoDB find error: {e}")
    
    # Fallback to in-memory storage
    for product in products_store:
        if name.lower() in product['name'].lower():
            return product
    return None

async def update_product(name: str, updates: dict):
    """Update product"""
    if db:
        try:
            result = await db.products.update_one(
                {"name": {"$regex": name, "$options": "i"}},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"MongoDB update error: {e}")
    
    # Fallback to in-memory storage
    for product in products_store:
        if name.lower() in product['name'].lower():
            product.update(updates)
            return True
    return False

async def delete_product(name: str):
    """Delete product"""
    if db:
        try:
            result = await db.products.delete_one({"name": {"$regex": name, "$options": "i"}})
            return result.deleted_count > 0
        except Exception as e:
            print(f"MongoDB delete error: {e}")
    
    # Fallback to in-memory storage
    for i, product in enumerate(products_store):
        if name.lower() in product['name'].lower():
            products_store.pop(i)
            return True
    return False

# API Routes
@app.get("/")
async def root():
    return {"message": "Vocal Verse API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/voice-command")
async def process_voice(command: VoiceCommand):
    """Process voice command"""
    try:
        result = process_voice_command(command.command, command.language)
        
        if result["action"] == "add" and result["product_name"] and result["quantity"] and result["price"]:
            # Add product
            product = Product(
                name=result["product_name"],
                quantity=result["quantity"],
                price_per_kg=result["price"]
            )
            saved_product = await save_product(product)
            return {
                "success": True,
                "message": f"Added {result['quantity']} kg of {result['product_name']} at ₹{result['price']} per kg",
                "product": saved_product,
                "parsed_command": result
            }
        
        elif result["action"] == "list":
            products = await get_all_products()
            return {
                "success": True,
                "message": f"Found {len(products)} products",
                "products": products,
                "parsed_command": result
            }
        
        elif result["action"] == "search" and result["product_name"]:
            product = await find_product(result["product_name"])
            if product:
                return {
                    "success": True,
                    "message": f"Found product: {product['name']}",
                    "product": product,
                    "parsed_command": result
                }
            else:
                return {
                    "success": False,
                    "message": f"Product '{result['product_name']}' not found",
                    "parsed_command": result
                }
        
        else:
            return {
                "success": False,
                "message": "Command not fully recognized or missing required information",
                "parsed_command": result
            }
    
    except Exception as e:
        print(f"Error processing voice command: {e}")
        return {
            "success": False,
            "message": f"Error processing command: {str(e)}"
        }

@app.get("/products")
async def get_products():
    """Get all products"""
    try:
        products = await get_all_products()
        return {"success": True, "products": products}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/products")
async def create_product(product: Product):
    """Create a new product"""
    try:
        saved_product = await save_product(product)
        return {"success": True, "product": saved_product}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/products/{product_name}")
async def get_product(product_name: str):
    """Get product by name"""
    try:
        product = await find_product(product_name)
        if product:
            return {"success": True, "product": product}
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.put("/products/{product_name}")
async def update_product_endpoint(product_name: str, updates: ProductUpdate):
    """Update product"""
    try:
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        updated = await update_product(product_name, update_data)
        if updated:
            return {"success": True, "message": f"Product '{product_name}' updated"}
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.delete("/products/{product_name}")
async def delete_product_endpoint(product_name: str):
    """Delete product"""
    try:
        deleted = await delete_product(product_name)
        if deleted:
            return {"success": True, "message": f"Product '{product_name}' deleted"}
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    print("Starting Vocal Verse API...")
    await test_mongodb_connection()
    print("API is ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)