from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime, timedelta
import re
import json
import asyncio
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
import bcrypt
import jwt
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

warnings.filterwarnings('ignore')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(title="Vocal Verse API with Supabase", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

# Initialize Supabase client
supabase: Client = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("Supabase client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")

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

# Security
security = HTTPBearer()

# Data models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool = True

class Product(BaseModel):
    name: str
    quantity: float
    price_per_kg: float
    description: Optional[str] = ""
    category: Optional[str] = "general"
    minimum_stock: Optional[float] = 1.0
    supplier: Optional[str] = ""
    expiry_date: Optional[datetime] = None

class ProductUpdate(BaseModel):
    name: str
    quantity: Optional[float] = None
    price_per_kg: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    minimum_stock: Optional[float] = None
    supplier: Optional[str] = None
    expiry_date: Optional[datetime] = None

class VoiceCommand(BaseModel):
    command: str
    language: Optional[str] = "en"

class InventoryTransaction(BaseModel):
    product_name: str
    transaction_type: str  # 'add', 'remove', 'update'
    quantity_change: float
    price_per_kg: Optional[float] = None
    notes: Optional[str] = ""

class PredictionRequest(BaseModel):
    product_name: str
    days_ahead: Optional[int] = 7

# Authentication functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Use service role to bypass RLS
        service_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        result = service_supabase.table('users').select('*').eq('id', user_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Voice processing function (enhanced)
def process_voice_command(command: str, language: str = "en") -> dict:
    """Process voice command and extract action and product information"""
    command = command.lower().strip()
    
    # Enhanced pattern matching
    patterns = {
        'add': r'add|create|insert|new|stock|purchase|buy',
        'update': r'update|change|modify|edit|adjust',
        'remove': r'remove|delete|del|sell|consume|use',
        'list': r'list|show|display|get all|inventory',
        'search': r'search|find|get|show|check',
        'predict': r'predict|forecast|estimate|suggest|recommend',
        'analyze': r'analyze|analysis|report|stats|statistics'
    }
    
    action = None
    for act, pattern in patterns.items():
        if re.search(pattern, command):
            action = act
            break
    
    if not action:
        return {"action": "unknown", "message": "Command not recognized"}
    
    # Extract product name (expanded list)
    products = [
        'tomato', 'onion', 'potato', 'rice', 'milk', 'sugar', 'banana', 'apple', 'carrot',
        'wheat', 'dal', 'oil', 'salt', 'tea', 'coffee', 'bread', 'eggs', 'chicken', 'mutton',
        'fish', 'spinach', 'cabbage', 'cauliflower', 'beans', 'peas', 'corn', 'garlic',
        'ginger', 'lemon', 'orange', 'mango', 'grapes', 'watermelon', 'cucumber', 'bitter gourd',
        'bottle gourd', 'brinjal', 'okra', 'radish', 'beetroot', 'turnip', 'pumpkin', 'quinoa'
    ]
    
    product_name = None
    for product in products:
        if product in command:
            product_name = product
            break
    
    # If no predefined product found, try to extract from command structure
    if not product_name:
        add_match = re.search(r'(?:add|create|new)\s+(\w+)', command)
        if add_match:
            product_name = add_match.group(1)
    
    # Extract quantity with enhanced patterns
    quantity = None
    
    # Try various quantity patterns (order matters - more specific first)
    qty_patterns = [
        (r'(\d+(?:\.\d+)?)\s*(?:kg|kilo|kilogram|kilos)\b', 1),  # kg - no conversion
        (r'(\d+(?:\.\d+)?)\s*(?:grams?|gr)\b', 0.001),  # grams to kg
        (r'(\d+(?:\.\d+)?)\s*(?:liter|litre|l)\b', 1),  # liters - treat as kg
        (r'(\d+(?:\.\d+)?)\s*(?:piece|pieces|pcs?|units?)\b', 1),  # pieces - treat as kg
        (r'(\d+(?:\.\d+)?)\s+(?:kg|kilo|kilogram)\b', 1),  # space before unit
        (r'(\d+(?:\.\d+)?)\s*(?:quintals?|q)\b', 100),  # quintals to kg
        (r'(\d+(?:\.\d+)?)\s*g\b(?!ram)', 0.001),  # standalone 'g' but not 'gram'
    ]
    
    for pattern, multiplier in qty_patterns:
        qty_match = re.search(pattern, command, re.IGNORECASE)
        if qty_match:
            quantity = float(qty_match.group(1)) * multiplier
            break
    
    # If no quantity found, try to extract any number that might be quantity
    if not quantity:
        # Look for patterns like "2 tomato" or "five kg"
        number_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:' + '|'.join(products) + r')', command)
        if number_match:
            quantity = float(number_match.group(1))
        else:
            # Try word numbers (one, two, etc.)
            word_numbers = {
                'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                'half': 0.5, 'quarter': 0.25
            }
            for word, num in word_numbers.items():
                if word in command:
                    quantity = num
                    break
    
    # Extract price with enhanced patterns
    price = None
    price_patterns = [
        r'₹\s*(\d+(?:\.\d+)?)',  # ₹20 or ₹ 20
        r'(\d+(?:\.\d+)?)\s*₹',  # 20₹
        r'(\d+(?:\.\d+)?)\s*(?:rupees?|rs)\b',  # 20 rupees
        r'at\s+₹?\s*(\d+(?:\.\d+)?)',  # at ₹20 or at 20
        r'(\d+(?:\.\d+)?)\s*(?:per\s+kg|per\s+kilogram)',  # 20 per kg
        r'(?:price|cost)\s*(?:is|of)?\s*₹?\s*(\d+(?:\.\d+)?)',  # price is ₹20
    ]
    
    for pattern in price_patterns:
        price_match = re.search(pattern, command, re.IGNORECASE)
        if price_match:
            price = float(price_match.group(1))
            break
    
    # Extract days for prediction
    days = None
    days_match = re.search(r'(\d+)\s*days?', command)
    if days_match:
        days = int(days_match.group(1))
    
    return {
        "action": action,
        "product_name": product_name,
        "quantity": quantity,
        "price": price,
        "days": days,
        "raw_command": command
    }

# Database operations
async def save_product(product: Product, user_id: str):
    """Save product to Supabase"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        product_data = product.dict()
        product_data['user_id'] = user_id
        product_data['id'] = str(uuid.uuid4())
        product_data['created_at'] = datetime.now().isoformat()
        product_data['updated_at'] = datetime.now().isoformat()
        
        # Use service role to bypass RLS
        service_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        result = service_supabase.table('products').insert(product_data).execute()
        
        # Log transaction
        await log_transaction(
            user_id=user_id,
            product_name=product.name,
            transaction_type='add',
            quantity_change=product.quantity,
            price_per_kg=product.price_per_kg
        )
        
        return result.data[0] if result.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def get_user_products(user_id: str):
    """Get all products for a user"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Use service role to bypass RLS
        service_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        result = service_supabase.table('products').select('*').eq('user_id', user_id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def find_user_product(user_id: str, name: str):
    """Find product by name for a user"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        result = supabase.table('products').select('*').eq('user_id', user_id).ilike('name', f'%{name}%').execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def update_user_product(user_id: str, product_id: str, updates: dict):
    """Update product"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        updates['updated_at'] = datetime.now().isoformat()
        result = supabase.table('products').update(updates).eq('id', product_id).eq('user_id', user_id).execute()
        return len(result.data) > 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def delete_user_product(user_id: str, product_id: str):
    """Delete product"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        result = supabase.table('products').delete().eq('id', product_id).eq('user_id', user_id).execute()
        return len(result.data) > 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def log_transaction(user_id: str, product_name: str, transaction_type: str, 
                         quantity_change: float, price_per_kg: Optional[float] = None, 
                         notes: Optional[str] = ""):
    """Log inventory transaction"""
    if not supabase:
        return
    
    try:
        transaction_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'product_name': product_name,
            'transaction_type': transaction_type,
            'quantity_change': quantity_change,
            'price_per_kg': price_per_kg,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        }
        
        # Use service role to bypass RLS
        service_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        service_supabase.table('inventory_transactions').insert(transaction_data).execute()
    except Exception as e:
        print(f"Failed to log transaction: {e}")

# Analytics and prediction functions
async def get_product_analytics(user_id: str, product_name: str):
    """Get analytics for a specific product"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Get transaction history
        result = supabase.table('inventory_transactions').select('*').eq('user_id', user_id).eq('product_name', product_name).order('created_at').execute()
        transactions = result.data
        
        if not transactions:
            return {"message": "No transaction history found"}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(transactions)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Calculate metrics
        total_added = df[df['transaction_type'] == 'add']['quantity_change'].sum()
        total_removed = df[df['transaction_type'] == 'remove']['quantity_change'].sum()
        current_stock = total_added - total_removed
        
        # Calculate consumption rate (kg per day)
        if len(df) > 1:
            days_span = (df['created_at'].max() - df['created_at'].min()).days
            if days_span > 0:
                consumption_rate = total_removed / days_span
            else:
                consumption_rate = 0
        else:
            consumption_rate = 0
        
        # Price trend
        price_data = df[df['price_per_kg'].notna()]
        avg_price = price_data['price_per_kg'].mean() if not price_data.empty else 0
        
        return {
            "product_name": product_name,
            "current_stock": current_stock,
            "total_added": total_added,
            "total_consumed": total_removed,
            "consumption_rate_per_day": consumption_rate,
            "average_price": avg_price,
            "transaction_count": len(transactions),
            "first_transaction": df['created_at'].min().isoformat(),
            "last_transaction": df['created_at'].max().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

async def predict_stock_depletion(user_id: str, product_name: str, days_ahead: int = 7):
    """Predict when stock will be depleted and suggest reorder"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Get current product info
        product = await find_user_product(user_id, product_name)
        if not product:
            return {"error": "Product not found"}
        
        # Get analytics
        analytics = await get_product_analytics(user_id, product_name)
        
        current_stock = analytics.get('current_stock', 0)
        consumption_rate = analytics.get('consumption_rate_per_day', 0)
        minimum_stock = product.get('minimum_stock', 1.0)
        
        if consumption_rate <= 0:
            return {
                "product_name": product_name,
                "current_stock": current_stock,
                "prediction": "Insufficient data for prediction",
                "recommendation": "Monitor usage patterns"
            }
        
        # Calculate days until depletion
        days_until_depletion = (current_stock - minimum_stock) / consumption_rate
        
        # Generate recommendation
        if days_until_depletion <= days_ahead:
            urgency = "HIGH" if days_until_depletion <= 3 else "MEDIUM"
            suggested_quantity = consumption_rate * 14  # 2 weeks supply
            
            recommendation = {
                "urgency": urgency,
                "message": f"Stock will be low in {days_until_depletion:.1f} days",
                "suggested_reorder_quantity": suggested_quantity,
                "suggested_reorder_date": (datetime.now() + timedelta(days=max(0, days_until_depletion-2))).date().isoformat()
            }
        else:
            recommendation = {
                "urgency": "LOW",
                "message": f"Stock sufficient for {days_until_depletion:.1f} days",
                "suggested_reorder_quantity": 0,
                "suggested_reorder_date": None
            }
        
        return {
            "product_name": product_name,
            "current_stock": current_stock,
            "minimum_stock": minimum_stock,
            "consumption_rate_per_day": consumption_rate,
            "days_until_depletion": days_until_depletion,
            "prediction_for_days": days_ahead,
            "recommendation": recommendation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

async def get_low_stock_alerts(user_id: str):
    """Get all products with low stock alerts"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        products = await get_user_products(user_id)
        alerts = []
        
        for product in products:
            if product['quantity'] <= product.get('minimum_stock', 1.0):
                prediction = await predict_stock_depletion(user_id, product['name'])
                alerts.append({
                    "product": product,
                    "prediction": prediction
                })
        
        return {"alerts": alerts, "count": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert error: {str(e)}")

# API Routes

# Authentication routes
@app.post("/auth/register")
async def register_user(user_data: UserCreate):
    """Register a new user"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Check if user already exists
        existing_user = supabase.table('users').select('*').eq('email', user_data.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        user_record = {
            'id': str(uuid.uuid4()),
            'email': user_data.email,
            'password_hash': hashed_password,
            'full_name': user_data.full_name,
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        # Use service role to bypass RLS for user creation
        service_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        result = service_supabase.table('users').insert(user_record).execute()
        
        if result.data:
            # Create access token
            access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": result.data[0]['id']}, expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": result.data[0]['id'],
                    "email": result.data[0]['email'],
                    "full_name": result.data[0]['full_name']
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
            
    except Exception as e:
        if "Email already registered" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@app.post("/auth/login")
async def login_user(user_data: UserLogin):
    """Login user"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Find user using service role to bypass RLS
        service_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        result = service_supabase.table('users').select('*').eq('email', user_data.email).execute()
        
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user = result.data[0]
        
        # Verify password
        if not verify_password(user_data.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['id']}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user['full_name']
            }
        }
        
    except Exception as e:
        if "Invalid email or password" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user['id'],
        "email": current_user['email'],
        "full_name": current_user['full_name'],
        "created_at": current_user['created_at'],
        "is_active": current_user['is_active']
    }

# Product routes (protected)
@app.get("/")
async def root():
    return {"message": "Vocal Verse API with Supabase is running", "status": "healthy", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(), "supabase_connected": supabase is not None}

@app.post("/voice-command")
async def process_voice(command: VoiceCommand, current_user: dict = Depends(get_current_user)):
    """Process voice command"""
    try:
        result = process_voice_command(command.command, command.language)
        user_id = current_user['id']
        
        if result["action"] == "add" and result["product_name"]:
            # Check if we have all required information
            if result["quantity"] and result["price"]:
                # Add product
                product = Product(
                    name=result["product_name"],
                    quantity=result["quantity"],
                    price_per_kg=result["price"]
                )
                saved_product = await save_product(product, user_id)
                return {
                    "success": True,
                    "message": f"Added {result['quantity']} kg of {result['product_name']} at ₹{result['price']} per kg",
                    "product": saved_product,
                    "parsed_command": result
                }
            else:
                # Handle missing information with helpful message
                missing_info = []
                if not result["quantity"]:
                    missing_info.append("quantity")
                if not result["price"]:
                    missing_info.append("price")
                
                return {
                    "success": False,
                    "message": f"To add {result['product_name']}, please specify the {' and '.join(missing_info)}. Try: 'Add {result['product_name']} 2 kg at ₹20 per kg'",
                    "parsed_command": result,
                    "missing_info": missing_info
                }
        
        elif result["action"] == "list":
            products = await get_user_products(user_id)
            return {
                "success": True,
                "message": f"Found {len(products)} products",
                "products": products,
                "parsed_command": result
            }
        
        elif result["action"] == "search" and result["product_name"]:
            product = await find_user_product(user_id, result["product_name"])
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
        
        elif result["action"] == "predict" and result["product_name"]:
            days = result.get("days", 7)
            prediction = await predict_stock_depletion(user_id, result["product_name"], days)
            return {
                "success": True,
                "message": f"Stock prediction for {result['product_name']}",
                "prediction": prediction,
                "parsed_command": result
            }
        
        elif result["action"] == "analyze":
            if result["product_name"]:
                analytics = await get_product_analytics(user_id, result["product_name"])
                return {
                    "success": True,
                    "message": f"Analytics for {result['product_name']}",
                    "analytics": analytics,
                    "parsed_command": result
                }
            else:
                alerts = await get_low_stock_alerts(user_id)
                return {
                    "success": True,
                    "message": "Inventory analysis",
                    "alerts": alerts,
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
async def get_products(current_user: dict = Depends(get_current_user)):
    """Get all products for current user"""
    try:
        products = await get_user_products(current_user['id'])
        return {"success": True, "products": products}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/products")
async def create_product(product: Product, current_user: dict = Depends(get_current_user)):
    """Create a new product"""
    try:
        saved_product = await save_product(product, current_user['id'])
        return {"success": True, "product": saved_product}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/products/{product_name}")
async def get_product(product_name: str, current_user: dict = Depends(get_current_user)):
    """Get product by name"""
    try:
        product = await find_user_product(current_user['id'], product_name)
        if product:
            return {"success": True, "product": product}
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        return {"success": False, "message": str(e)}

# Analytics routes
@app.get("/analytics/product/{product_name}")
async def get_product_analytics_endpoint(product_name: str, current_user: dict = Depends(get_current_user)):
    """Get analytics for a specific product"""
    try:
        analytics = await get_product_analytics(current_user['id'], product_name)
        return {"success": True, "analytics": analytics}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/analytics/predictions/{product_name}")
async def get_product_prediction(product_name: str, days_ahead: int = 7, current_user: dict = Depends(get_current_user)):
    """Get stock prediction for a product"""
    try:
        prediction = await predict_stock_depletion(current_user['id'], product_name, days_ahead)
        return {"success": True, "prediction": prediction}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/analytics/alerts")
async def get_alerts(current_user: dict = Depends(get_current_user)):
    """Get low stock alerts"""
    try:
        alerts = await get_low_stock_alerts(current_user['id'])
        return {"success": True, "alerts": alerts}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/analytics/dashboard")
async def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """Get dashboard analytics data"""
    try:
        user_id = current_user['id']
        
        # Get all products
        products = await get_user_products(user_id)
        
        # Get low stock alerts
        alerts = await get_low_stock_alerts(user_id)
        
        # Calculate summary statistics
        total_products = len(products)
        total_value = sum(p['quantity'] * p['price_per_kg'] for p in products)
        low_stock_count = alerts['count']
        
        # Get recent transactions
        if supabase:
            recent_transactions = supabase.table('inventory_transactions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
            transactions = recent_transactions.data
        else:
            transactions = []
        
        return {
            "success": True,
            "dashboard": {
                "summary": {
                    "total_products": total_products,
                    "total_inventory_value": total_value,
                    "low_stock_alerts": low_stock_count,
                    "recent_transactions": len(transactions)
                },
                "products": products,
                "alerts": alerts,
                "recent_transactions": transactions
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)