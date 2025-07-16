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
import google.generativeai as genai
from dotenv import load_dotenv
import json
import asyncio
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')
import asyncio
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await test_mongodb_connection()
    # Start background AI suggestion generation
    asyncio.create_task(periodic_ai_suggestions())

async def periodic_ai_suggestions():
    """Background task to generate AI suggestions periodically"""
    while True:
        try:
            await asyncio.sleep(300)  # Wait 5 minutes
            await generate_ai_suggestions()
            print("🤖 AI suggestions generated automatically")
        except Exception as e:
            print(f"Error in periodic AI suggestions: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error

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
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    print("Gemini AI initialized successfully")
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

# Translation dictionaries for regional languages
TRANSLATION_DICT = {
    'hi': {  # Hindi
        'जोड़ो': 'add', 'एड': 'add', 'डालो': 'add',
        'अपडेट': 'update', 'बदलो': 'update', 'चेंज': 'update',
        'हटाओ': 'remove', 'निकालो': 'remove',
        'डिलीट': 'delete', 'मिटाओ': 'delete',
        'लिस्ट': 'list', 'दिखाओ': 'list', 'बताओ': 'list',
        'किलो': 'kg', 'केजी': 'kg',
        'रुपये': 'rupees', 'रुपया': 'rupees',
        'टमाटर': 'tomato', 'प्याज': 'onion', 'केला': 'banana',
        'आलू': 'potato', 'गाजर': 'carrot', 'चावल': 'rice',
        'दाल': 'dal', 'दूध': 'milk', 'चीनी': 'sugar',
        'कीमत': 'price', 'दाम': 'price', 'रेट': 'rate'
    },
    'kn': {  # Kannada
        'ಸೇರಿಸಿ': 'add', 'ಹಾಕಿ': 'add', 'ಸೇರಿಸು': 'add',
        'ಅಪ್ಡೇಟ್': 'update', 'ಬದಲಾಯಿಸಿ': 'update',
        'ತೆಗೆದುಹಾಕಿ': 'remove', 'ತೆಗೆ': 'remove',
        'ಅಳಿಸಿ': 'delete', 'ಡಿಲೀಟ್': 'delete',
        'ಲಿಸ್ಟ್': 'list', 'ತೋರಿಸಿ': 'list',
        'ಕಿಲೋ': 'kg', 'ಕೆಜಿ': 'kg',
        'ರೂಪಾಯಿ': 'rupees', 'ರೂಪಾಯಿಗಳು': 'rupees',
        'ಟೊಮೇಟೊ': 'tomato', 'ಈರುಳ್ಳಿ': 'onion', 'ಬಾಳೆಹಣ್ಣು': 'banana',
        'ಆಲೂಗಡ್ಡೆ': 'potato', 'ಅಕ್ಕಿ': 'rice', 'ಹಾಲು': 'milk',
        'ಬೆಲೆ': 'price', 'ದರ': 'rate'
    },
    'ta': {  # Tamil
        'சேர்': 'add', 'போடு': 'add', 'சேர்க்க': 'add',
        'மாற்று': 'update', 'அப்டேட்': 'update',
        'எடு': 'remove', 'நீக்கு': 'remove',
        'நீக்கு': 'delete', 'அழி': 'delete',
        'பட்டியல்': 'list', 'காட்டு': 'list',
        'கிலோ': 'kg', 'கேஜி': 'kg',
        'ரூபாய்': 'rupees', 'ரூபா': 'rupees',
        'தக்காளி': 'tomato', 'வெங்காயம்': 'onion', 'வாழைப்பழம்': 'banana',
        'உருளைக்கிழங்கு': 'potato', 'அரிசி': 'rice', 'பால்': 'milk',
        'விலை': 'price', 'ரேட்': 'rate'
    },
    'te': {  # Telugu
        'చేర్చు': 'add', 'పెట్టు': 'add', 'యాడ్': 'add',
        'అప్డేట్': 'update', 'మార్చు': 'update',
        'తీసివేయి': 'remove', 'తీసేయి': 'remove',
        'తొలగించు': 'delete', 'డిలీట్': 'delete',
        'లిస్ట్': 'list', 'చూపించు': 'list',
        'కిలో': 'kg', 'కేజీ': 'kg',
        'రూపాయలు': 'rupees', 'రూపాయి': 'rupees',
        'టమాట': 'tomato', 'ఉల్లిపాయ': 'onion', 'అరటిపండు': 'banana',
        'బంగాళాదుంప': 'potato', 'అన్నం': 'rice', 'పాలు': 'milk',
        'ధర': 'price', 'రేట్': 'rate'
    }
}

# Response messages in different languages
RESPONSE_MESSAGES = {
    'en': {
        'product_added': 'Product {product} {quantity} kg added at ₹{price} per kg',
        'price_updated': 'Price updated for {product} to ₹{price} per kg',
        'quantity_removed': 'Removed {quantity} kg of {product}',
        'product_deleted': 'Product {product} deleted',
        'low_stock': 'Low stock alert',
        'products_listed': 'You have {count} products in inventory'
    },
    'hi': {
        'product_added': '{product} {quantity} किलो ₹{price} दर से जोड़ा गया',
        'price_updated': '{product} की कीमत ₹{price} अपडेट की गई',
        'quantity_removed': '{product} से {quantity} किलो हटाया गया',
        'product_deleted': '{product} डिलीट किया गया',
        'low_stock': 'कम स्टॉक अलर्ट',
        'products_listed': 'आपके पास {count} उत्पाद हैं'
    },
    'kn': {
        'product_added': '{product} {quantity} ಕಿಲೋ ₹{price} ದರದಲ್ಲಿ ಸೇರಿಸಲಾಗಿದೆ',
        'price_updated': '{product} ಬೆಲೆ ₹{price} ಅಪ್ಡೇಟ್ ಮಾಡಲಾಗಿದೆ',
        'quantity_removed': '{product} ನಿಂದ {quantity} ಕಿಲೋ ತೆಗೆದುಹಾಕಲಾಗಿದೆ',
        'product_deleted': '{product} ಅಳಿಸಲಾಗಿದೆ',
        'low_stock': 'ಕಡಿಮೆ ಸ್ಟಾಕ್ ಎಚ್ಚರಿಕೆ',
        'products_listed': 'ನಿಮ್ಮ ಬಳಿ {count} ಉತ್ಪಾದನೆಗಳಿವೆ'
    },
    'ta': {
        'product_added': '{product} {quantity} கிலோ ₹{price} விலையில் சேர்க்கப்பட்டது',
        'price_updated': '{product} விலை ₹{price} அப்டேட் செய்யப்பட்டது',
        'quantity_removed': '{product} இல் இருந்து {quantity} கிலோ எடுக்கப்பட்டது',
        'product_deleted': '{product} நீக்கப்பட்டது',
        'low_stock': 'குறைந்த பங்கு எச்சரிக்கை',
        'products_listed': 'உங்களிடம் {count} பொருட்கள் உள்ளன'
    },
    'te': {
        'product_added': '{product} {quantity} కిలో ₹{price} రేటుతో చేర్చబడింది',
        'price_updated': '{product} ధర ₹{price} అప్డేట్ చేయబడింది',
        'quantity_removed': '{product} నుండి {quantity} కిలో తీసివేయబడింది',
        'product_deleted': '{product} తొలగించబడింది',
        'low_stock': 'తక్కువ స్టాక్ హెచ్చరిక',
        'products_listed': 'మీకు {count} ఉత్పత్తులు ఉన్నాయి'
    }
}

# Pydantic models
class Product(BaseModel):
    id: str
    name: str
    quantity: float  # in kg
    price_per_kg: float  # price per kg
    description: Optional[str] = ""
    category: Optional[str] = "General"
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

class ProductCreate(BaseModel):
    name: str
    quantity: float
    price_per_kg: float
    description: Optional[str] = ""
    category: Optional[str] = "General"

class ProductUpdate(BaseModel):
    quantity: Optional[float] = None
    price_per_kg: Optional[float] = None
    description: Optional[str] = None

class VoiceCommand(BaseModel):
    command: str
    language: Optional[str] = "en"

class AnalyticsData(BaseModel):
    product_name: str
    action: str
    quantity: Optional[float] = None
    price: Optional[float] = None
    timestamp: datetime
    language: str

class AIsuggestion(BaseModel):
    id: str
    type: str  # 'reorder', 'price_alert', 'trend', 'optimization'
    product_name: Optional[str] = None
    message: str
    priority: int  # 1-5 (5 being highest)
    created_at: datetime
    expires_at: Optional[datetime] = None
    action_required: bool = False
    suggested_action: Optional[str] = None
    
class MarketTrend(BaseModel):
    product_name: str
    trend_type: str  # 'price_increase', 'price_decrease', 'demand_increase', 'demand_decrease'
    confidence: float  # 0-1
    predicted_value: Optional[float] = None
    time_period: str  # 'daily', 'weekly', 'monthly'
    created_at: datetime

# Helper functions
def translate_regional_to_english(text: str, language: str) -> str:
    """Translate regional language text to English using dictionary"""
    if language == 'en' or language not in TRANSLATION_DICT:
        return text
    
    translation_dict = TRANSLATION_DICT[language]
    translated_text = text.lower()
    
    # Replace each regional word with English equivalent
    for regional_word, english_word in translation_dict.items():
        translated_text = translated_text.replace(regional_word, english_word)
    
    print(f"Translation: {text} ({language}) -> {translated_text}")
    return translated_text

def calculate_price_breakdown(price_per_kg: float):
    """Calculate price breakdown for different quantities"""
    breakdown = {
        "1kg": price_per_kg,
        "half_kg": math.ceil(price_per_kg / 2),
        "quarter_kg": math.ceil(price_per_kg / 4)
    }
    return breakdown

def is_low_stock(quantity: float) -> bool:
    """Check if product is low in stock"""
    return quantity <= 2.0

async def log_analytics_data(product_name: str, action: str, quantity: float = None, price: float = None, language: str = "en"):
    """Log analytics data for AI analysis"""
    analytics_data = {
        "id": str(uuid.uuid4()),
        "product_name": product_name,
        "action": action,
        "quantity": quantity,
        "price": price,
        "timestamp": datetime.utcnow(),
        "language": language
    }
    
    if db is not None:
        await db.analytics.insert_one(analytics_data)
    else:
        analytics_store.append(analytics_data)

async def calculate_price_average(existing_price: float, existing_quantity: float, new_price: float, new_quantity: float) -> float:
    """Calculate weighted average price when merging products"""
    total_value = (existing_price * existing_quantity) + (new_price * new_quantity)
    total_quantity = existing_quantity + new_quantity
    return round(total_value / total_quantity, 2) if total_quantity > 0 else existing_price

async def analyze_product_trends(product_name: str = None):
    """Analyze product trends using AI"""
    try:
        analytics_data = []
        
        if db is not None:
            query = {"product_name": product_name} if product_name else {}
            async for record in db.analytics.find(query).sort("timestamp", -1).limit(100):
                analytics_data.append(record)
        else:
            if product_name:
                analytics_data = [r for r in analytics_store if r["product_name"] == product_name][-100:]
            else:
                analytics_data = analytics_store[-100:]
        
        if not analytics_data:
            return []
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(analytics_data)
        trends = []
        
        if len(df) > 5:  # Need minimum data for trend analysis
            # Group by product and analyze trends
            for product in df['product_name'].unique():
                product_data = df[df['product_name'] == product].copy()
                
                # Price trend analysis
                price_data = product_data[product_data['price'].notna()]
                if len(price_data) > 2:
                    prices = price_data['price'].values
                    x = np.arange(len(prices))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, prices)
                    
                    if abs(r_value) > 0.5 and p_value < 0.05:  # Significant trend
                        trend_type = 'price_increase' if slope > 0 else 'price_decrease'
                        confidence = abs(r_value)
                        predicted_value = slope * len(prices) + intercept
                        
                        trends.append({
                            "product_name": product,
                            "trend_type": trend_type,
                            "confidence": confidence,
                            "predicted_value": predicted_value,
                            "time_period": "daily",
                            "created_at": datetime.utcnow()
                        })
                
                # Quantity trend analysis
                quantity_data = product_data[product_data['quantity'].notna()]
                if len(quantity_data) > 2:
                    quantities = quantity_data['quantity'].values
                    x = np.arange(len(quantities))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, quantities)
                    
                    if abs(r_value) > 0.5 and p_value < 0.05:  # Significant trend
                        trend_type = 'demand_increase' if slope < 0 else 'demand_decrease'  # Negative slope means more consumption
                        confidence = abs(r_value)
                        
                        trends.append({
                            "product_name": product,
                            "trend_type": trend_type,
                            "confidence": confidence,
                            "time_period": "daily",
                            "created_at": datetime.utcnow()
                        })
        
        return trends
        
    except Exception as e:
        print(f"Error analyzing trends: {e}")
        return []

async def generate_ai_suggestions():
    """Generate AI-powered suggestions based on inventory data and trends"""
    suggestions = []
    
    try:
        # Get current products
        products = []
        if db is not None:
            async for product in db.products.find({}):
                products.append(product)
        else:
            products = products_store
        
        # Get trends
        trends = await analyze_product_trends()
        
        # Generate suggestions based on stock levels
        for product in products:
            # Low stock suggestion
            if is_low_stock(product["quantity"]):
                suggestion = {
                    "id": str(uuid.uuid4()),
                    "type": "reorder",
                    "product_name": product["name"],
                    "message": f"⚠️ Low stock alert: {product['display_name']} only has {product['quantity']} kg left. Consider reordering.",
                    "priority": 4,
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + timedelta(days=7),
                    "action_required": True,
                    "suggested_action": f"add 10 kg {product['display_name']}"
                }
                suggestions.append(suggestion)
            
            # Price optimization suggestions
            if product["price_per_kg"] > 100:  # High-priced items
                suggestion = {
                    "id": str(uuid.uuid4()),
                    "type": "price_alert",
                    "product_name": product["name"],
                    "message": f"💰 Price Alert: {product['display_name']} is priced at ₹{product['price_per_kg']}/kg. Monitor market rates for optimization.",
                    "priority": 2,
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + timedelta(days=3),
                    "action_required": False,
                    "suggested_action": None
                }
                suggestions.append(suggestion)
        
        # Generate suggestions based on trends
        for trend in trends:
            if trend["confidence"] > 0.7:
                if trend["trend_type"] == "price_increase, smart_merge: bool = True":
                    suggestion = {
                        "id": str(uuid.uuid4()),
                        "type": "trend",
                        "product_name": trend["product_name"],
                        "message": f"📈 Trend Alert: {trend['product_name']} prices are trending upward (confidence: {trend['confidence']:.0%}). Consider buying now.",
                        "priority": 3,
                        "created_at": datetime.utcnow(),
                        "expires_at": datetime.utcnow() + timedelta(days=5),
                        "action_required": False,
                        "suggested_action": f"add 5 kg {trend['product_name']}"
                    }
                    suggestions.append(suggestion)
                
                elif trend["trend_type"] == "demand_increase":
                    suggestion = {
                        "id": str(uuid.uuid4()),
                        "type": "trend",
                        "product_name": trend["product_name"],
                        "message": f"🔥 Demand Alert: {trend['product_name']} consumption is increasing (confidence: {trend['confidence']:.0%}). Stock up!",
                        "priority": 4,
                        "created_at": datetime.utcnow(),
                        "expires_at": datetime.utcnow() + timedelta(days=5),
                        "action_required": True,
                        "suggested_action": f"add 10 kg {trend['product_name']}"
                    }
                    suggestions.append(suggestion)
        
        # AI-powered optimization suggestions using Gemini
        if model and len(products) > 0:
            try:
                products_summary = []
                for p in products[:10]:  # Limit to top 10 for prompt
                    products_summary.append({
                        "name": p["display_name"],
                        "quantity": p["quantity"],
                        "price": p["price_per_kg"],
                        "category": p.get("category", "General")
                    })
                
                prompt = f"""
                As an AI inventory management expert, analyze this inventory data and provide 2-3 specific optimization suggestions:
                
                Products: {json.dumps(products_summary, indent=2)}
                
                Consider:
                1. Product mix optimization
                2. Seasonal recommendations
                3. Cost efficiency
                4. Storage optimization
                
                Return suggestions in this JSON format:
                [
                    {{
                        "type": "optimization",
                        "message": "specific suggestion text",
                        "priority": 1-5,
                        "suggested_action": "specific action or null"
                    }}
                ]
                """
                
                response = model.generate_content(prompt)
                ai_suggestions_text = response.text.strip()
                
                # Clean and parse AI response
                if ai_suggestions_text.startswith('```json'):
                    ai_suggestions_text = ai_suggestions_text[7:]
                if ai_suggestions_text.endswith('```'):
                    ai_suggestions_text = ai_suggestions_text[:-3]
                
                ai_suggestions = json.loads(ai_suggestions_text)
                
                for ai_sug in ai_suggestions:
                    suggestion = {
                        "id": str(uuid.uuid4()),
                        "type": ai_sug["type"],
                        "product_name": None,
                        "message": f"🤖 AI Insight: {ai_sug['message']}",
                        "priority": ai_sug["priority"],
                        "created_at": datetime.utcnow(),
                        "expires_at": datetime.utcnow() + timedelta(days=7),
                        "action_required": ai_sug.get("suggested_action") is not None,
                        "suggested_action": ai_sug.get("suggested_action")
                    }
                    suggestions.append(suggestion)
                    
            except Exception as e:
                print(f"AI suggestions error: {e}")
        
        # Store suggestions
        if db is not None:
            if suggestions:
                await db.suggestions.insert_many(suggestions)
        else:
            suggestions_store.extend(suggestions)
        
        return suggestions
        
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return []

async def smart_product_merge(product_name: str, new_quantity: float, new_price: float, description: str = "", category: str = "Grocery"):
    """Smart product merging with price averaging"""
    product_name_lower = product_name.lower()
    
    if db is not None:
        existing_product = await db.products.find_one({"name": product_name_lower})
        if existing_product:
            # Calculate new averaged price
            averaged_price = await calculate_price_average(
                existing_product["price_per_kg"], 
                existing_product["quantity"],
                new_price, 
                new_quantity
            )
            
            # Update existing product
            new_total_quantity = existing_product["quantity"] + new_quantity
            update_data = {
                "quantity": new_total_quantity,
                "price_per_kg": averaged_price,
                "updated_at": datetime.utcnow()
            }
            
            if description and description != existing_product.get("description", ""):
                update_data["description"] = f"{existing_product.get('description', '')} | {description}".strip(" |")
            
            await db.products.update_one(
                {"name": product_name_lower},
                {"$set": update_data}
            )
            
            updated_product = await db.products.find_one({"name": product_name_lower})
            return updated_product, True  # True indicates it was merged
        else:
            return None, False  # Product doesn't exist
    else:
        # Use in-memory storage
        existing_product = next((p for p in products_store if p["name"] == product_name_lower), None)
        if existing_product:
            # Calculate new averaged price
            averaged_price = await calculate_price_average(
                existing_product["price_per_kg"], 
                existing_product["quantity"],
                new_price, 
                new_quantity
            )
            
            # Update existing product
            existing_product["quantity"] += new_quantity
            existing_product["price_per_kg"] = averaged_price
            existing_product["updated_at"] = datetime.utcnow()
            
            if description and description != existing_product.get("description", ""):
                existing_product["description"] = f"{existing_product.get('description', '')} | {description}".strip(" |")
            
            return existing_product, True  # True indicates it was merged
        else:
            return None, False  # Product doesn't exist

async def parse_voice_command_with_gemini(command: str, language: str = "en"):
    """Parse voice command using Gemini AI for better multilingual understanding"""
    if not model:
        # Fallback to regex-based parsing if Gemini is not available
        return parse_voice_command_fallback(command, language)
    
    try:
        # Create a detailed prompt for Gemini AI
        prompt = f"""
        You are an AI assistant for inventory management. Parse the following voice command and extract the action and parameters.
        
        Command: "{command}"
        Language: {language}
        
        The command could be for:
        1. ADD product: "add 5 kg tomato at 50" or "5 किलो टमाटर 50 रुपये में जोड़ो"
        2. UPDATE price: "update tomato price to 60" or "टमाटर का दाम 60 करो"
        3. REMOVE quantity: "remove 2 kg onions" or "2 किलो प्याज़ निकालो"
        4. DELETE product: "delete tomato" or "टमाटर डिलीट करो"
        5. LIST products: "list all products" or "सभी चीज़ें दिखाओ"
        
        Return ONLY a JSON object with this exact format:
        {{
            "action": "add|update_price|remove|delete|list|unknown",
            "product": "product_name",
            "quantity": number_or_null,
            "price": number_or_null
        }}
        
        Rules:
        - Convert all regional language product names to English (e.g., टमाटर->tomato, प्याज़->onion)
        - Extract numbers correctly regardless of language
        - Use lowercase for product names
        - If unclear, set action to "unknown"
        """
        
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Clean up the response and parse JSON
        if result.startswith('```json'):
            result = result[7:]
        if result.endswith('```'):
            result = result[:-3]
        result = result.strip()
        
        parsed = json.loads(result)
        
        # Validate the parsed result
        if parsed.get("action") in ["add", "update_price", "remove", "delete", "list"]:
            return parsed
        else:
            return {"action": "unknown", "command": command, "language": language}
            
    except Exception as e:
        print(f"Gemini AI parsing error: {e}")
        # Fallback to regex-based parsing
        return parse_voice_command_fallback(command, language)

def parse_voice_command_fallback(command: str, language: str = "en"):
    """Fallback parse voice command and extract action, product, quantity, price"""
    # First translate regional language to English
    translated_command = translate_regional_to_english(command, language)
    command_lower = translated_command.lower().strip()
    
    # Enhanced pattern matching for better regional language support
    # Add product patterns - more flexible
    add_patterns = [
        r"add\s+(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(?:at\s+)?₹?(\d+(?:\.\d+)?)",
        r"add\s+(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(\d+(?:\.\d+)?)\s*rupees?",
        r"add\s+(\d+(?:\.\d+)?)\s*(?:kg\s+)?(.+?)\s+(?:at\s+)?₹?(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(?:at\s+)?₹?(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(\d+(?:\.\d+)?)\s*rupees?",
        r"(\d+(?:\.\d+)?)\s+(.+?)\s+(\d+(?:\.\d+)?)\s*rupees?",
        r"(\d+(?:\.\d+)?)\s+(.+?)\s+₹?(\d+(?:\.\d+)?)"
    ]
    
    for pattern in add_patterns:
        match = re.search(pattern, command_lower)
        if match:
            try:
                quantity = float(match.group(1))
                product_name = match.group(2).strip()
                price = float(match.group(3))
                
                # Clean product name - remove common words and extra spaces
                product_name = re.sub(r'\b(?:add|at|rupees?|kg|కిలో|किलो|ಕಿಲೋ|கிலோ|রূপা|ரூபா|రూపాయ|ರೂಪಾಯಿ|रुपये)\b', '', product_name).strip()
                product_name = ' '.join(product_name.split())  # Remove extra spaces
                
                return {
                    "action": "add",
                    "product": product_name,
                    "quantity": quantity,
                    "price": price
                }
            except (ValueError, IndexError):
                continue
    
    # Update price patterns - enhanced
    update_price_patterns = [
        r"update\s+(.+?)\s+price\s+to\s+₹?(\d+(?:\.\d+)?)",
        r"change\s+(.+?)\s+price\s+to\s+₹?(\d+(?:\.\d+)?)",
        r"(.+?)\s+price\s+₹?(\d+(?:\.\d+)?)",
        r"(.+?)\s+rate\s+₹?(\d+(?:\.\d+)?)",
        r"(.+?)\s+₹?(\d+(?:\.\d+)?)\s*rupees?\s+update",
        r"(.+?)\s+₹?(\d+(?:\.\d+)?)\s*update"
    ]
    
    for pattern in update_price_patterns:
        match = re.search(pattern, command_lower)
        if match:
            try:
                product_name = match.group(1).strip()
                price = float(match.group(2))
                
                # Clean product name - remove common words and extra spaces
                product_name = re.sub(r'\b(?:update|change|price|rate|rupees?|రూపా|ரூபா|රூপা|ರೂಪಾಯಿ|रुपये|अपडेट|करो)\b', '', product_name).strip()
                product_name = ' '.join(product_name.split())  # Remove extra spaces
                
                return {
                    "action": "update_price",
                    "product": product_name,
                    "price": price
                }
            except (ValueError, IndexError):
                continue
    
    # Remove quantity patterns
    remove_patterns = [
        r"remove\s+(\d+(?:\.\d+)?)\s*kg\s+(.+)",
        r"take\s+out\s+(\d+(?:\.\d+)?)\s*kg\s+(.+)",
        r"(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s*remove"
    ]
    
    for pattern in remove_patterns:
        match = re.search(pattern, command_lower)
        if match:
            try:
                quantity = float(match.group(1))
                product_name = match.group(2).strip()
                return {
                    "action": "remove",
                    "product": product_name,
                    "quantity": quantity
                }
            except (ValueError, IndexError):
                continue
    
    # Delete product patterns
    delete_patterns = [
        r"delete\s+(.+)",
        r"remove\s+(.+)\s+completely",
        r"(.+?)\s*delete"
    ]
    
    for pattern in delete_patterns:
        match = re.search(pattern, command_lower)
        if match:
            product_name = match.group(1).strip()
            return {
                "action": "delete",
                "product": product_name
            }
    
    # List products patterns
    if re.search(r"list\s+(?:all\s+)?products?", command_lower):
        return {"action": "list"}
    
    return {
        "action": "unknown", 
        "command": command, 
        "translated": translated_command,
        "language": language
    }

def format_product_response(product: dict, language: str = "en"):
    """Format product response with breakdown and language support"""
    breakdown = calculate_price_breakdown(product["price_per_kg"])
    
    response = {
        "product": product["name"],
        "quantity": product["quantity"],
        "price_per_kg": product["price_per_kg"],
        "breakdown": breakdown,
        "description": product.get("description", ""),
        "category": product.get("category", "General"),
        "tags": product.get("tags", []),
        "low_stock": is_low_stock(product["quantity"]),
        "language": language
    }
    
    # Add language-specific message
    if language in RESPONSE_MESSAGES:
        messages = RESPONSE_MESSAGES[language]
        response["message"] = messages["product_added"].format(
            product=product["name"],
            quantity=product["quantity"],
            price=product["price_per_kg"]
        )
        
        if response["low_stock"]:
            response["message"] += f" - {messages['low_stock']}"
    
    return response

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "voice_catalog"}

@app.post("/api/products")
async def create_product(product: ProductCreate, smart_merge: bool = True):
    """Add a new product to inventory with smart merging capability with smart merging capability"""
    try:
        # Try smart merge first if enabled
        if smart_merge:
            merged_product, was_merged = await smart_product_merge(
                product.name, 
                product.quantity, 
                product.price_per_kg,
                product.description,
                product.category
            )
            
            if was_merged:
                # Log analytics for merge
                await log_analytics_data(
                    product_name=product.name.lower(),
                    action="merge_add",
                    quantity=product.quantity,
                    price=product.price_per_kg
                )
                
                result = format_product_response(merged_product)
                result["action"] = "merged"
                result["message"] = f"✅ Merged {product.quantity} kg of {product.name} with existing stock. New total: {merged_product['quantity']} kg at ₹{merged_product['price_per_kg']}/kg (averaged price)"
                return result
        
        # Create new product if not merged
        # Try smart merge first if enabled
        if smart_merge:
                merged_product, was_merged = await smart_product_merge(
                product.name, 
                product.quantity, 
                product.price_per_kg,
                product.description,
                product.category
            )
            
            if was_merged:
                # Log analytics for merge
                await log_analytics_data(
                    product_name=product.name.lower(),
                    action="merge_add",
                    quantity=product.quantity,
                    price=product.price_per_kg
                )
                
                
            # Log analytics for new product
            await log_analytics_data(
                product_name=product.name.lower(),
                action="add",
                quantity=product.quantity,
                price=product.price_per_kg
            )
            
            result = format_product_response(product_data)
            result["action"] = "created"
            return result
                result["action"] = "merged"
                result["message"] = f"✅ Merged {product.quantity} kg of {product.name} with existing stock. New total: {merged_product['quantity']} kg at ₹{merged_product['price_per_kg']}/kg (averaged price)"
                return result
        
        # Create new product if not merged
        if db is not None:
            if not smart_merge:
     and smart_merge is False
            if not smart_merge:
                existing = await db.products.find_one({"name": product.name.lower()})
                    if existing:
                        raise HTTPException(status_code=400, detail="Product already exists")
            
            product_data = {
                "id": str(uuid.uuid4()),
                "name": product.name.lower(),
                "display_name": product.name,
                "quantity": product.quantity,
                "price_per_kg": product.price_per_kg,
                "description": product.description,
                "category": product.category,
                "tags": [product.name.lower(), product.category.lower()],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db.products.insert_one(product_data)
            
            # Log analytics for new product
            await log_analytics_data(
                product_name=product.name.lower(),
                action="add",
                quantity=product.quantity,
                price=product.price_per_kg
            )
            
            result = format_product_response(product_data)
            result["action"] = "created"
            return result
        else:
            # Use in-memory storage
            if not smart_merge:
                existing = next((p for p in products_store if p["name"] == product.name.lower()), None)
                if existing:
                    raise HTTPException(status_code=400, detail="Product already exists")
            
            product_data = {
                "id": str(uuid.uuid4()),
                "name": product.name.lower(),
                "display_name": product.name,
                "quantity": product.quantity,
                "price_per_kg": product.price_per_kg,
                "description": product.description,
                "category": product.category,
                "tags": [product.name.lower(), product.category.lower()],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            products_store.append(product_data)
            
            # Log analytics for new product
            await log_analytics_data(
                product_name=product.name.lower(),
                action="add",
                quantity=product.quantity,
                price=product.price_per_kg
            )
            
            result = format_product_response(product_data)
            result["action"] = "created"
            return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products")
async def list_products():
    """List all products with stock alerts"""
    try:
        products = []
        if db is not None:
            async for product in db.products.find({}):
                product_response = format_product_response(product)
                products.append(product_response)
        else:
            # Use in-memory storage
            for product in products_store:
                product_response = format_product_response(product)
                products.append(product_response)
        
        # Add stock alerts
        low_stock_products = [p for p in products if p["low_stock"]]
        
        return {
            "products": products,
            "total_products": len(products),
            "low_stock_alerts": low_stock_products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/products/{product_name}")
async def update_product(product_name: str, update: ProductUpdate):
    """Update product quantity or price"""
    try:
        if db is not None:
            product = await db.products.find_one({"name": product_name.lower()})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            update_data = {"updated_at": datetime.utcnow()}
            if update.quantity is not None:
                update_data["quantity"] = update.quantity
            if update.price_per_kg is not None:
                update_data["price_per_kg"] = update.price_per_kg
            if update.description is not None:
                update_data["description"] = update.description
            
            await db.products.update_one(
                {"name": product_name.lower()},
                {"$set": update_data}
            )
            
            updated_product = await db.products.find_one({"name": product_name.lower()})
            return format_product_response(updated_product)
        else:
            # Use in-memory storage
            product = next((p for p in products_store if p["name"] == product_name.lower()), None)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Always use smart merge for voice commands
            product["updated_at"] = datetime.utcnow()
            if update.quantity is not None:
                product["quantity"] = update.quantity
            if update.price_per_kg is not None:
                product["price_per_kg"] = update.price_per_kg
            if update.description is not None:
                product["description"] = update.description
            
            return format_product_response(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_name}")
async def delete_product(product_name: str):
    """Delete a product from inventory"""
    try:
        if db is not None:
            
            # Log analytics
            await log_analytics_data(
                product_name=parsed["product"],
                action="price_update",
                price=parsed["price"],
                language=command.language
            )
            
            result = await db.products.delete_one({"name": product_name.lower()})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Product not found")
            return {"message": f"Product '{product_name}' deleted successfully"}
        else:
            # Use in-memory storage
            product = next((p for p in products_store if p["name"] == product_name.lower()), None)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            products_store.remove(product)
            return {"message": f"Product '{product_name}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice-command")
async def process_voice_command(command: VoiceCommand):
    """Process voice command and execute corresponding action with AI enhancements"""
    try:
        parsed = await parse_voice_command_with_gemini(command.command, command.language)
                
                # Log analytics
                await log_analytics_data(
                    product_name=parsed["product"],
                    action="remove",
                    quantity=parsed["quantity"],
                    language=command.language
                )
                
        
        if parsed["action"] == "add":
            product_data = ProductCreate(
                name=parsed["product"],
                quantity=parsed["quantity"],
                price_per_kg=parsed["price"],
                description=f"Fresh {parsed['product']} perfect for cooking.",
                category="Grocery"
            )
            # Always use smart merge for voice commands
            result = await create_product(product_data, smart_merge=True)
            result["language"] = command.language
            
            # Log user behavior for AI learning
            await log_analytics_data(
                product_name=parsed["product"],
                action="voice_add",
                quantity=parsed["quantity"],
                price=parsed["price"],
                language=command.language
            )
            
            # Generate AI suggestions after adding product
            asyncio.create_task(generate_ai_suggestions())
            
            return result
        
                # Log analytics
                await log_analytics_data(
                    product_name=parsed["product"],
                    action="remove",
                    quantity=parsed["quantity"],
                    language=command.language
                )
                
                return result
        
        elif parsed["action"] == "delete":
            result = await delete_product(parsed["product"])
            result["language"] = command.language
            
            # Log analytics
            await log_analytics_data(
                product_name=parsed["product"],
                action="delete",
                language=command.language
            )
            
            return result
        
        elif parsed["action"] == "list":
            result = await list_products()
            result["language"] = command.language
            
            # Log analytics
            await log_analytics_data(
                product_name="all",
                action="list",
                language=command.language
            )
            
            return result
        
        else:
            # AI-powered command understanding
            suggestions = await generate_ai_suggestions()
            relevant_suggestions = [s for s in suggestions if s.get("action_required")][:3]
            
            return {
                "error": "Command not understood",
                "parsed_command": parsed,
                "suggestion": "Try commands like 'add 5 kg tomato at ₹50' or 'list all products'",
                "language": command.language,
                "ai_suggestions": relevant_suggestions
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/trends")
async def get_trends(product_name: Optional[str] = None):
    """Get product trends and analytics"""
    try:
        trends = await analyze_product_trends(product_name)
        return {
            "trends": trends,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suggestions")
async def get_ai_suggestions(force_regenerate: bool = False):
    """Get AI-powered suggestions"""
    try:
        if force_regenerate:
            suggestions = await generate_ai_suggestions()
        else:
            # Get existing suggestions first
            suggestions = []
            if db is not None:
                async for sug in db.suggestions.find({"expires_at": {"$gt": datetime.utcnow()}}).sort("priority", -1):
                    suggestions.append(sug)
            else:
                suggestions = [s for s in suggestions_store if s.get("expires_at", datetime.utcnow()) > datetime.utcnow()]
            
            # Generate new ones if no valid suggestions exist
            if not suggestions:
                suggestions = await generate_ai_suggestions()
        
        return {
            "suggestions": suggestions,
            "total": len(suggestions),
            "high_priority": [s for s in suggestions if s.get("priority", 0) >= 4],
            "action_required": [s for s in suggestions if s.get("action_required", False)]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    try:
        # Get products
        products = []
        if db is not None:
            async for product in db.products.find({}):
                products.append(product)
        else:
            products = products_store
        
        # Get analytics data
        analytics_data = []
        if db is not None:
            async for record in db.analytics.find({}).sort("timestamp", -1).limit(100):
                analytics_data.append(record)
        else:
            analytics_data = analytics_store[-100:]
        
        # Calculate key metrics
        total_products = len(products)
        total_value = sum(p["quantity"] * p["price_per_kg"] for p in products)
        low_stock_count = len([p for p in products if is_low_stock(p["quantity"])])
        
        # Most added products
        product_additions = defaultdict(int)
        for record in analytics_data:
            if record["action"] in ["add", "merge_add", "voice_add"]:
                product_additions[record["product_name"]] += record.get("quantity", 0)
        
        top_products = sorted(product_additions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Price trends
        price_changes = []
        for record in analytics_data:
            if record["action"] == "price_update" and record.get("price"):
                price_changes.append({
                    "product": record["product_name"],
                    "price": record["price"],
                    "timestamp": record["timestamp"]
                })
        
        # Language usage stats
        language_stats = defaultdict(int)
        for record in analytics_data:
            language_stats[record.get("language", "en")] += 1
        
        return {
            "summary": {
                "total_products": total_products,
                "total_inventory_value": round(total_value, 2),
                "low_stock_alerts": low_stock_count,
                "total_transactions": len(analytics_data)
            },
            "top_products": dict(top_products),
            "recent_price_changes": price_changes[-10:],
            "language_usage": dict(language_stats),
            "trends": await analyze_product_trends(),
            "suggestions_count": len(await generate_ai_suggestions()) if not suggestions_store else len(suggestions_store)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suggestions/{suggestion_id}/execute")
async def execute_suggestion(suggestion_id: str):
    """Execute an AI suggestion automatically"""
    try:
        # Find the suggestion
        suggestion = None
        if db is not None:
            suggestion = await db.suggestions.find_one({"id": suggestion_id})
        else:
            suggestion = next((s for s in suggestions_store if s["id"] == suggestion_id), None)
        
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        if not suggestion.get("suggested_action"):
            raise HTTPException(status_code=400, detail="No executable action for this suggestion")
        
        # Execute the suggested action
        suggested_action = suggestion["suggested_action"]
        voice_command = VoiceCommand(command=suggested_action, language="en")
        result = await process_voice_command(voice_command)
        
        # Mark suggestion as executed
        if db is not None:
            await db.suggestions.update_one(
                {"id": suggestion_id},
                {"$set": {"executed": True, "executed_at": datetime.utcnow()}}
            )
        else:
            for s in suggestions_store:
                if s["id"] == suggestion_id:
                    s["executed"] = True
                    s["executed_at"] = datetime.utcnow()
                    break
        
        return {
            "message": "Suggestion executed successfully",
            "suggestion": suggestion,
            "execution_result": result
        }
        elif parsed["action"] == "update_price":
            update_data = ProductUpdate(price_per_kg=parsed["price"])
            result = await update_product(parsed["product"], update_data)
            result["language"] = command.language
            
            # Log analytics
            await log_analytics_data(
                product_name=parsed["product"],
                action="price_update",
                price=parsed["price"],
                language=command.language
            )
            
            return result
        
        elif parsed["action"] == "remove":
            if db is not None:
                product = await db.products.find_one({"name": parsed["product"].lower()})
                if not product:
                    raise HTTPException(status_code=404, detail="Product not found")
                
                new_quantity = max(0, product["quantity"] - parsed["quantity"])
                update_data = ProductUpdate(quantity=new_quantity)
                result = await update_product(parsed["product"], update_data)
                result["language"] = command.language
                
                # Log analytics
                await log_analytics_data(
                    product_name=parsed["product"],
                    action="remove",
                    quantity=parsed["quantity"],
                    language=command.language
                )
                
                return result
            else:
                # Use in-memory storage
                product = next((p for p in products_store if p["name"] == parsed["product"].lower()), None)
                if not product:
                    raise HTTPException(status_code=404, detail="Product not found")
                
                new_quantity = max(0, product["quantity"] - parsed["quantity"])
                update_data = ProductUpdate(quantity=new_quantity)
                result = await update_product(parsed["product"], update_data)
                result["language"] = command.language
                
                # Log analytics
                await log_analytics_data(
                    product_name=parsed["product"],
                    action="remove",
                    quantity=parsed["quantity"],
                    language=command.language
                )
                
                return result
        
        elif parsed["action"] == "delete":
            result = await delete_product(parsed["product"])
            result["language"] = command.language
            
            # Log analytics
            await log_analytics_data(
                product_name=parsed["product"],
                action="delete",
                language=command.language
            )
            
            return result
        
        elif parsed["action"] == "list":
            result = await list_products()
            result["language"] = command.language
            
            # Log analytics
            await log_analytics_data(
                product_name="all",
                action="list",
                language=command.language
            )
            
            return result
        
        else:
            # AI-powered command understanding
            suggestions = await generate_ai_suggestions()
            relevant_suggestions = [s for s in suggestions if s.get("action_required")][:3]
            
            return {
                "error": "Command not understood",
                "parsed_command": parsed,
                "suggestion": "Try commands like 'add 5 kg tomato at ₹50' or 'list all products'",
                "language": command.language,
                "ai_suggestions": relevant_suggestions
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/trends")
async def get_trends(product_name: Optional[str] = None):
    """Get product trends and analytics"""
    try:
        trends = await analyze_product_trends(product_name)
        return {
            "trends": trends,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suggestions")
async def get_ai_suggestions(force_regenerate: bool = False):
    """Get AI-powered suggestions"""
    try:
        if force_regenerate:
            suggestions = await generate_ai_suggestions()
        else:
            # Get existing suggestions first
            suggestions = []
            if db is not None:
                async for sug in db.suggestions.find({"expires_at": {"$gt": datetime.utcnow()}}).sort("priority", -1):
                    suggestions.append(sug)
            else:
                suggestions = [s for s in suggestions_store if s.get("expires_at", datetime.utcnow()) > datetime.utcnow()]
            
            # Generate new ones if no valid suggestions exist
            if not suggestions:
                suggestions = await generate_ai_suggestions()
        
        return {
            "suggestions": suggestions,
            "total": len(suggestions),
            "high_priority": [s for s in suggestions if s.get("priority", 0) >= 4],
            "action_required": [s for s in suggestions if s.get("action_required", False)]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    try:
        # Get products
        products = []
        if db is not None:
            async for product in db.products.find({}):
                products.append(product)
        else:
            products = products_store
        
        # Get analytics data
        analytics_data = []
        if db is not None:
            async for record in db.analytics.find({}).sort("timestamp", -1).limit(100):
                analytics_data.append(record)
        else:
            analytics_data = analytics_store[-100:]
        
        # Calculate key metrics
        total_products = len(products)
        total_value = sum(p["quantity"] * p["price_per_kg"] for p in products)
        low_stock_count = len([p for p in products if is_low_stock(p["quantity"])])
        
        # Most added products
        product_additions = defaultdict(int)
        for record in analytics_data:
            if record["action"] in ["add", "merge_add", "voice_add"]:
                product_additions[record["product_name"]] += record.get("quantity", 0)
        
        top_products = sorted(product_additions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Price trends
        price_changes = []
        for record in analytics_data:
            if record["action"] == "price_update" and record.get("price"):
                price_changes.append({
                    "product": record["product_name"],
                    "price": record["price"],
                    "timestamp": record["timestamp"]
                })
        
        # Language usage stats
        language_stats = defaultdict(int)
        for record in analytics_data:
            language_stats[record.get("language", "en")] += 1
        
        return {
            "summary": {
                "total_products": total_products,
                "total_inventory_value": round(total_value, 2),
                "low_stock_alerts": low_stock_count,
                "total_transactions": len(analytics_data)
            },
            "top_products": dict(top_products),
            "recent_price_changes": price_changes[-10:],
            "language_usage": dict(language_stats),
            "trends": await analyze_product_trends(),
            "suggestions_count": len(await generate_ai_suggestions()) if not suggestions_store else len(suggestions_store)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suggestions/{suggestion_id}/execute")
async def execute_suggestion(suggestion_id: str):
    """Execute an AI suggestion automatically"""
    try:
        # Find the suggestion
        suggestion = None
        if db is not None:
            suggestion = await db.suggestions.find_one({"id": suggestion_id})
        else:
            suggestion = next((s for s in suggestions_store if s["id"] == suggestion_id), None)
        
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        if not suggestion.get("suggested_action"):
            raise HTTPException(status_code=400, detail="No executable action for this suggestion")
        
        # Execute the suggested action
        suggested_action = suggestion["suggested_action"]
        voice_command = VoiceCommand(command=suggested_action, language="en")
        result = await process_voice_command(voice_command)
        
        # Mark suggestion as executed
        if db is not None:
            await db.suggestions.update_one(
                {"id": suggestion_id},
                {"$set": {"executed": True, "executed_at": datetime.utcnow()}}
            )
        else:
            for s in suggestions_store:
                if s["id"] == suggestion_id:
                    s["executed"] = True
                    s["executed_at"] = datetime.utcnow()
                    break
        
        return {
            "message": "Suggestion executed successfully",
            "suggestion": suggestion,
            "execution_result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)