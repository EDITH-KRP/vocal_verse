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

# Enhanced AI voice processing function
def process_voice_command(command: str, language: str = "en") -> dict:
    """
    Enhanced AI processing for voice commands with better accuracy
    Handles commands like "Orange one KG ₹50" or "Add tomato 2 kg at 30 rupees"
    """
    original_command = command
    command = command.lower().strip()
    
    # Enhanced pattern matching for actions
    action_patterns = {
        'add': r'(?:add|create|insert|new|store|put|include)\b',
        'update': r'(?:update|change|modify|edit|alter|adjust)\b',
        'remove': r'(?:remove|delete|del|eliminate|take out)\b',
        'list': r'(?:list|show|display|get all|show all|view all)\b',
        'search': r'(?:search|find|get|show|look for|where is)\b'
    }
    
    # Detect action - if no explicit action word, assume "add" for product + quantity + price pattern
    action = None
    for act, pattern in action_patterns.items():
        if re.search(pattern, command):
            action = act
            break
    
    # If no action detected but we have product + quantity + price pattern, assume "add"
    if not action:
        # Check if command has product + quantity + price structure (including word numbers)
        has_product_pattern = any(product in command for products_list in [
            ['apple', 'banana', 'orange', 'mango', 'grapes', 'watermelon', 'lemon'],
            ['tomato', 'onion', 'potato', 'carrot', 'cabbage', 'cauliflower', 'spinach'],
            ['rice', 'wheat', 'dal', 'oil', 'salt', 'sugar', 'milk', 'eggs', 'chicken']
        ] for product in products_list)
        
        has_quantity_pattern = re.search(r'(?:\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|half|quarter).*(?:kg|kilo|kilogram)', command)
        has_price_pattern = re.search(r'(?:₹|rupees?|rs|\d+.*rupees)', command)
        
        if has_product_pattern and (has_quantity_pattern or has_price_pattern):
            action = "add"
        else:
            return {"action": "unknown", "message": "Command not recognized. Try saying 'Add [product] [quantity] kg at [price] rupees'"}
    
    # Enhanced product extraction
    product_name = None
    quantity = None
    price = None
    
    # Expanded product database with common variations
    products_db = {
        # Fruits
        'apple': ['apple', 'apples'],
        'banana': ['banana', 'bananas'],
        'orange': ['orange', 'oranges'],
        'mango': ['mango', 'mangoes'],
        'grapes': ['grapes', 'grape'],
        'watermelon': ['watermelon', 'water melon'],
        'lemon': ['lemon', 'lemons', 'lime'],
        
        # Vegetables
        'tomato': ['tomato', 'tomatoes'],
        'onion': ['onion', 'onions'],
        'potato': ['potato', 'potatoes', 'aloo'],
        'carrot': ['carrot', 'carrots'],
        'cabbage': ['cabbage'],
        'cauliflower': ['cauliflower', 'gobi'],
        'spinach': ['spinach', 'palak'],
        'brinjal': ['brinjal', 'eggplant', 'baingan'],
        'okra': ['okra', 'bhindi', 'lady finger'],
        'beans': ['beans', 'green beans'],
        'peas': ['peas', 'green peas'],
        'cucumber': ['cucumber'],
        'bitter gourd': ['bitter gourd', 'karela'],
        'bottle gourd': ['bottle gourd', 'lauki'],
        'radish': ['radish', 'mooli'],
        'beetroot': ['beetroot', 'beet'],
        'turnip': ['turnip'],
        'pumpkin': ['pumpkin', 'kaddu'],
        'corn': ['corn', 'maize'],
        'garlic': ['garlic', 'lahsun'],
        'ginger': ['ginger', 'adrak'],
        
        # Staples
        'rice': ['rice', 'basmati', 'jasmine rice'],
        'wheat': ['wheat', 'atta'],
        'dal': ['dal', 'lentils', 'pulses'],
        'oil': ['oil', 'cooking oil', 'mustard oil', 'sunflower oil'],
        'salt': ['salt', 'namak'],
        'sugar': ['sugar', 'cheeni'],
        
        # Dairy & Proteins
        'milk': ['milk', 'doodh'],
        'eggs': ['eggs', 'egg', 'ande'],
        'chicken': ['chicken', 'murgi'],
        'mutton': ['mutton', 'goat meat'],
        'fish': ['fish', 'machli'],
        
        # Others
        'tea': ['tea', 'chai'],
        'coffee': ['coffee'],
        'bread': ['bread', 'pav', 'roti']
    }
    
    # Find product name using enhanced matching
    for standard_name, variations in products_db.items():
        for variation in variations:
            if variation in command:
                product_name = standard_name
                break
        if product_name:
            break
    
    # If no predefined product found, extract first word that could be a product
    if not product_name:
        # Remove action words and common words
        cleaned_command = re.sub(r'\b(?:add|create|insert|new|at|kg|kilo|kilogram|rupees?|rs|₹|one|two|three|four|five|six|seven|eight|nine|ten)\b', '', command)
        words = cleaned_command.split()
        if words:
            # Take the first meaningful word as product name
            for word in words:
                if len(word) > 2 and word.isalpha():
                    product_name = word
                    break
    
    # Enhanced quantity extraction
    # Handle written numbers and digits
    number_words = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'half': 0.5, 'quarter': 0.25
    }
    
    # First try to find word numbers + kg pattern
    for word, num in number_words.items():
        word_patterns = [
            rf'{word}\s*(?:kg|kilo|kilogram)',
            rf'{word}\s+(?:kg|kilo|kilogram)',
        ]
        for pattern in word_patterns:
            if re.search(pattern, command):
                quantity = num
                break
        if quantity is not None:
            break
    
    # If no word number found, try digit + kg pattern
    if quantity is None:
        qty_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:kg|kilo|kilogram|kilos)',
            r'(\d+(?:\.\d+)?)\s*kg',
            r'(\d+)\s*(?:kg|kilo|kilogram)',
        ]
        
        for pattern in qty_patterns:
            qty_match = re.search(pattern, command)
            if qty_match:
                quantity = float(qty_match.group(1))
                break
    
    # Enhanced price extraction with multiple patterns including word numbers
    price_number_words = {
        'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90, 'hundred': 100
    }
    
    # First try word numbers for price
    for word, num in price_number_words.items():
        word_price_patterns = [
            rf'{word}\s*(?:rupees?|rs)',
            rf'at\s+{word}\s*(?:rupees?|rs)?',
            rf'₹\s*{word}',
        ]
        for pattern in word_price_patterns:
            if re.search(pattern, command):
                price = num
                break
        if price is not None:
            break
    
    # If no word price found, try digit patterns
    if price is None:
        price_patterns = [
            r'₹\s*(\d+(?:\.\d+)?)',  # ₹50
            r'(\d+(?:\.\d+)?)\s*₹',  # 50₹
            r'(?:at|for|price|cost)\s+₹?\s*(\d+(?:\.\d+)?)',  # at ₹50, for 50
            r'(?:at|for|price|cost)\s+(\d+(?:\.\d+)?)\s*(?:rupees?|rs)',  # at 50 rupees
            r'(\d+(?:\.\d+)?)\s*(?:rupees?|rs)',  # 50 rupees
            r'(?:price|cost|rate)\s+(?:is\s+)?₹?\s*(\d+(?:\.\d+)?)',  # price is 50
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, command)
            if price_match:
                price = float(price_match.group(1))
                break
    
    # Smart defaults and validation
    if action == "add" and product_name:
        # If quantity not specified, default to 1 kg
        if quantity is None:
            quantity = 1.0
        
        # If price not specified, ask for it
        if price is None:
            return {
                "action": "incomplete",
                "message": f"Please specify the price for {product_name}. Say something like '{product_name} {quantity} kg at 50 rupees'",
                "product_name": product_name,
                "quantity": quantity
            }
    
    # Generate response message
    if action == "add" and product_name and quantity and price:
        message = f"Added {product_name} - {quantity} kg at ₹{price} per kg"
    elif action == "list":
        message = "Showing all products"
    elif action == "search" and product_name:
        message = f"Searching for {product_name}"
    else:
        message = "Command processed"
    
    return {
        "action": action,
        "product_name": product_name,
        "quantity": quantity,
        "price": price,
        "raw_command": original_command,
        "message": message,
        "confidence": calculate_confidence(product_name, quantity, price, action)
    }

def calculate_confidence(product_name, quantity, price, action):
    """Calculate confidence score for the extracted information"""
    confidence = 0.0
    
    if action:
        confidence += 0.3
    if product_name:
        confidence += 0.3
    if quantity:
        confidence += 0.2
    if price:
        confidence += 0.2
    
    return min(confidence, 1.0)

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
    """Enhanced voice command processing with better AI accuracy"""
    try:
        result = process_voice_command(command.command, command.language)
        
        # Handle incomplete commands (missing price)
        if result["action"] == "incomplete":
            return {
                "success": False,
                "message": result["message"],
                "parsed_command": result,
                "confidence": result.get("confidence", 0.5)
            }
        
        # Handle add command with all required information
        if result["action"] == "add" and result["product_name"] and result["quantity"] and result["price"]:
            # Check if product already exists and update or create new
            existing_product = await find_product(result["product_name"])
            
            if existing_product:
                # Update existing product
                updates = {
                    "quantity": existing_product["quantity"] + result["quantity"],
                    "price_per_kg": result["price"]  # Update to new price
                }
                updated = await update_product(result["product_name"], updates)
                return {
                    "success": True,
                    "message": f"Updated {result['product_name']}: added {result['quantity']} kg at ₹{result['price']} per kg. Total: {updates['quantity']} kg",
                    "product": updated,
                    "parsed_command": result,
                    "confidence": result.get("confidence", 1.0),
                    "action_taken": "updated_existing"
                }
            else:
                # Create new product
                product = Product(
                    name=result["product_name"].title(),  # Capitalize first letter
                    quantity=result["quantity"],
                    price_per_kg=result["price"],
                    category="General"  # Default category
                )
                saved_product = await save_product(product)
                return {
                    "success": True,
                    "message": f"Added {result['quantity']} kg of {result['product_name']} at ₹{result['price']} per kg",
                    "product": saved_product,
                    "parsed_command": result,
                    "confidence": result.get("confidence", 1.0),
                    "action_taken": "created_new"
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