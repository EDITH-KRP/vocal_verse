from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
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

# --- Translation Support (googletrans) ---
# The 'googletrans' library can be unstable. If translation fails,
# consider using a more robust official API for production use.
try:
    from googletrans import Translator
    from langdetect import detect
    TRANSLATION_ENABLED = True
    print("✅ Translation libraries loaded successfully. Translation is enabled.")
except ImportError:
    TRANSLATION_ENABLED = False
    print("⚠️ Translation libraries (googletrans, langdetect) not found. Running in fallback mode without translation.")

# --- Environment Variables ---
# Load environment variables from a .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded.")
except ImportError:
    pass

# --- FastAPI App Initialization ---
app = FastAPI(title="Vocal Verse API")

# --- CORS (Cross-Origin Resource Sharing) ---
# Allows frontend applications from any origin to access this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory Storage ---
# This will act as our database for now.
# NOTE: This data is not persistent and will be lost when the server restarts.
# You should replace these with your Supabase logic.
products_store = []
analytics_store = []
suggestions_store = []
user_behavior_store = []
market_trends_store = []

# --- Gemini AI Initialization ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini AI initialized successfully.")
    except ImportError:
        model = None
        print("⚠️ 'google.generativeai' not installed. Using fallback parsing.")
else:
    model = None
    print("⚠️ Gemini API key not found. Using fallback parsing.")

# --- Translator Initialization ---
if TRANSLATION_ENABLED:
    translator = Translator()

# --- Helper Functions for Translation ---
def detect_language(text: str) -> str:
    """Detects the language of the input text."""
    if not TRANSLATION_ENABLED:
        return 'en'
    try:
        return detect(text)
    except Exception as e:
        print(f"🧐 Language detection failed: {e}. Defaulting to English.")
        return 'en'

def translate_to_english(text: str) -> str:
    """Translates text to English if it's in another language."""
    if not TRANSLATION_ENABLED:
        return text
    try:
        if detect_language(text) == 'en':
            return text
        result = translator.translate(text, dest='en')
        print(f"🌍 Translated '{text}' to '{result.text}'")
        return result.text
    except Exception as e:
        print(f"❌ Translation error: {e}. Returning original text.")
        return text

def get_multilingual_product_mapping():
    """Returns a dictionary mapping product names across different languages."""
    return {
        'apple': ['apple', 'apples', 'seb', 'सेब'],
        'banana': ['banana', 'bananas', 'kela', 'केला'],
        'orange': ['orange', 'oranges', 'santra', 'संतरा', 'narangi', 'नारंगी'],
        'mango': ['mango', 'mangoes', 'aam', 'आम'],
        'grapes': ['grapes', 'grape', 'angur', 'अंगूर'],
        'watermelon': ['watermelon', 'water melon', 'tarbooj', 'तरबूज'],
        'lemon': ['lemon', 'lemons', 'lime', 'nimbu', 'नीम्बू'],
        'tomato': ['tomato', 'tomatoes', 'tamatar', 'टमाटर'],
        'onion': ['onion', 'onions', 'pyaz', 'प्याज'],
        'potato': ['potato', 'potatoes', 'aloo', 'आलू'],
        'carrot': ['carrot', 'carrots', 'gajar', 'गाजर'],
        'cabbage': ['cabbage', 'patta gobi', 'पत्ता गोभी'],
        'cauliflower': ['cauliflower', 'gobi', 'गोभी', 'phool gobi', 'फूल गोभी'],
        'spinach': ['spinach', 'palak', 'पालक'],
        'brinjal': ['brinjal', 'eggplant', 'baingan', 'बैंगन'],
        'okra': ['okra', 'bhindi', 'भिंडी', 'lady finger'],
        'beans': ['beans', 'green beans', 'sem', 'सेम'],
        'peas': ['peas', 'green peas', 'matar', 'मटर'],
        'cucumber': ['cucumber', 'kheera', 'खीरा'],
        'bitter gourd': ['bitter gourd', 'karela', 'करेला'],
        'bottle gourd': ['bottle gourd', 'lauki', 'लौकी'],
        'radish': ['radish', 'mooli', 'मूली'],
        'beetroot': ['beetroot', 'beet', 'chukandar', 'चुकंदर'],
        'turnip': ['turnip', 'shalgam', 'शलगम'],
        'pumpkin': ['pumpkin', 'kaddu', 'कद्दू'],
        'corn': ['corn', 'maize', 'bhutta', 'भुट्टा'],
        'garlic': ['garlic', 'lahsun', 'लहसुन'],
        'ginger': ['ginger', 'adrak', 'अदरक'],
        'rice': ['rice', 'basmati', 'jasmine rice', 'chawal', 'चावल'],
        'wheat': ['wheat', 'atta', 'gehun', 'गेहूं'],
        'dal': ['dal', 'lentils', 'pulses', 'दाल'],
        'oil': ['oil', 'cooking oil', 'mustard oil', 'sunflower oil', 'tel', 'तेल'],
        'salt': ['salt', 'namak', 'नमक'],
        'sugar': ['sugar', 'cheeni', 'चीनी'],
        'milk': ['milk', 'doodh', 'दूध'],
        'eggs': ['eggs', 'egg', 'ande', 'अंडे'],
        'chicken': ['chicken', 'murgi', 'मुर्गी'],
        'mutton': ['mutton', 'goat meat', 'bakra', 'बकरा'],
        'fish': ['fish', 'machli', 'मछली'],
        'tea': ['tea', 'chai', 'चाय'],
        'coffee': ['coffee', 'कॉफी'],
        'bread': ['bread', 'pav', 'roti', 'रोटी', 'ब्रेड']
    }

# --- Pydantic Data Models ---
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

# --- Voice Processing Logic ---
def process_voice_command(command: str, language: str = "en") -> dict:
    """Processes a voice command to extract product details."""
    original_command = command
    translated_command = translate_to_english(command)
    command = translated_command.lower().strip()

    action_patterns = {
        'add': r'(?:add|create|insert|new|store|put|include|daal|daalna|जोड़)\b',
        'update': r'(?:update|change|modify|edit|alter|adjust|badal|बदल|price.*to|set.*price)\b',
        'remove': r'(?:remove|delete|del|eliminate|take out|hata|हटा|nikaal|निकाल)\b',
        'list': r'(?:list|show|display|get all|show all|view all|sabhi|सभी|dikha|दिखा)\b',
        'search': r'(?:search|find|get|show|look for|where is|dhund|ढूंढ|kaha|कहा)\b',
        'stock': r'(?:stock|inventory|quantity|kitna|कितना|total|balance)\b'
    }

    action = None
    for act, pattern in action_patterns.items():
        if re.search(pattern, command):
            action = act
            break

    product_name, quantity, price = None, None, None
    products_db = get_multilingual_product_mapping()

    for standard_name, variations in products_db.items():
        for variation in variations:
            if variation in command:
                product_name = standard_name
                break
        if product_name:
            break

    qty_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilo|kilogram|kilos)', command)
    if qty_match:
        quantity = float(qty_match.group(1))

    price_match = re.search(r'₹\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:rs|rupees?)', command)
    if price_match:
        price = float(price_match.group(1) or price_match.group(2))

    if not action and product_name and (quantity or price):
        action = "add"
    
    if action == "add" and not price:
        return {"action": "incomplete", "message": f"Please specify the price for {product_name}."}

    return {
        "action": action or "unknown",
        "product_name": product_name,
        "quantity": quantity,
        "price": price,
        "raw_command": original_command,
        "message": "Command processed."
    }

# --- Database Operations (Using In-Memory Store) ---
# TODO: Replace the logic in these functions with your Supabase client calls.
async def save_product(product: Product):
    """Saves a product to the in-memory store."""
    product_dict = product.dict()
    product_dict['_id'] = str(uuid.uuid4())
    product_dict['created_at'] = datetime.now()
    products_store.append(product_dict)
    print(f"📦 Product '{product.name}' saved to in-memory store.")
    return product_dict

async def get_all_products():
    """Gets all products from the in-memory store."""
    print("📦 Fetching all products from in-memory store.")
    return products_store

async def find_product(name: str):
    """Finds a product by name in the in-memory store."""
    for product in products_store:
        if name.lower() in product['name'].lower():
            print(f"📦 Found product '{name}' in in-memory store.")
            return product
    return None

async def update_product(name: str, updates: dict):
    """Updates a product in the in-memory store."""
    for product in products_store:
        if name.lower() in product['name'].lower():
            product.update(updates)
            print(f"📦 Product '{name}' updated in in-memory store.")
            return True
    return False

async def delete_product(name: str):
    """Deletes a product from the in-memory store."""
    for i, product in enumerate(products_store):
        if name.lower() in product['name'].lower():
            products_store.pop(i)
            print(f"📦 Product '{name}' deleted from in-memory store.")
            return True
    return False

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "Vocal Verse API is running", "status": "healthy"}

@app.post("/voice-command")
async def process_voice(command: VoiceCommand):
    """Processes a voice command to manage inventory."""
    try:
        result = process_voice_command(command.command, command.language)
        action = result.get("action")
        product_name = result.get("product_name")

        if action == "add" and product_name:
            # Logic to add or update a product
            existing_product = await find_product(product_name)
            if existing_product:
                updates = {
                    "quantity": existing_product["quantity"] + result["quantity"],
                    "price_per_kg": result["price"]
                }
                await update_product(product_name, updates)
                return {"success": True, "message": f"Updated {product_name}."}
            else:
                new_product = Product(
                    name=product_name.title(),
                    quantity=result["quantity"],
                    price_per_kg=result["price"]
                )
                await save_product(new_product)
                return {"success": True, "message": f"Added {product_name}."}

        elif action == "list":
            products = await get_all_products()
            return {"success": True, "products": products}

        elif action == "remove" and product_name:
            deleted = await delete_product(product_name)
            if deleted:
                return {"success": True, "message": f"Deleted {product_name}."}
            else:
                raise HTTPException(status_code=404, detail="Product not found.")

        else:
            return {"success": False, "message": "Command not recognized.", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products", response_model=List[dict])
async def get_products():
    """Gets all products."""
    return await get_all_products()

# --- Application Startup ---
@app.on_event("startup")
async def startup_event():
    """Initializes the application."""
    print("🚀 Starting Vocal Verse API...")
    print("✅ API is ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)