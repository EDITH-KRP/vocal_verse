-- Supabase SQL Schema for Vocal Verse Application

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    quantity DECIMAL(10,3) NOT NULL DEFAULT 0,
    price_per_kg DECIMAL(10,2) NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'general',
    minimum_stock DECIMAL(10,3) DEFAULT 1.0,
    supplier VARCHAR(255),
    expiry_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory transactions table for tracking all changes
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_name VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- 'add', 'remove', 'update'
    quantity_change DECIMAL(10,3) NOT NULL,
    price_per_kg DECIMAL(10,2),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Voice commands log table
CREATE TABLE IF NOT EXISTS voice_commands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    command_text TEXT NOT NULL,
    parsed_action VARCHAR(50),
    parsed_product VARCHAR(255),
    parsed_quantity DECIMAL(10,3),
    parsed_price DECIMAL(10,2),
    success BOOLEAN DEFAULT FALSE,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_key VARCHAR(100) NOT NULL,
    preference_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, preference_key)
);

-- Stock alerts table
CREATE TABLE IF NOT EXISTS stock_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL, -- 'low_stock', 'expiry_warning', 'reorder_suggestion'
    alert_message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market trends table (for future price predictions)
CREATE TABLE IF NOT EXISTS market_trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_name VARCHAR(255) NOT NULL,
    region VARCHAR(100) DEFAULT 'general',
    average_price DECIMAL(10,2) NOT NULL,
    price_trend VARCHAR(20), -- 'increasing', 'decreasing', 'stable'
    data_source VARCHAR(100),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_quantity ON products(quantity);

CREATE INDEX IF NOT EXISTS idx_inventory_transactions_user_id ON inventory_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_product_name ON inventory_transactions(product_name);
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_created_at ON inventory_transactions(created_at);

CREATE INDEX IF NOT EXISTS idx_voice_commands_user_id ON voice_commands(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_commands_created_at ON voice_commands(created_at);

CREATE INDEX IF NOT EXISTS idx_stock_alerts_user_id ON stock_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_stock_alerts_is_read ON stock_alerts(is_read);

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_commands ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_alerts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- RLS Policies for products table
CREATE POLICY "Users can view own products" ON products
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own products" ON products
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own products" ON products
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete own products" ON products
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- RLS Policies for inventory_transactions table
CREATE POLICY "Users can view own transactions" ON inventory_transactions
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own transactions" ON inventory_transactions
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- RLS Policies for voice_commands table
CREATE POLICY "Users can view own voice commands" ON voice_commands
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own voice commands" ON voice_commands
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- RLS Policies for user_preferences table
CREATE POLICY "Users can manage own preferences" ON user_preferences
    FOR ALL USING (auth.uid()::text = user_id::text);

-- RLS Policies for stock_alerts table
CREATE POLICY "Users can view own alerts" ON stock_alerts
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own alerts" ON stock_alerts
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically create stock alerts
CREATE OR REPLACE FUNCTION check_low_stock()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if stock is below minimum
    IF NEW.quantity <= NEW.minimum_stock THEN
        INSERT INTO stock_alerts (user_id, product_name, alert_type, alert_message)
        VALUES (
            NEW.user_id,
            NEW.name,
            'low_stock',
            'Stock for ' || NEW.name || ' is running low (' || NEW.quantity || ' kg remaining)'
        );
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for low stock alerts
CREATE TRIGGER trigger_check_low_stock
    AFTER UPDATE OF quantity ON products
    FOR EACH ROW
    EXECUTE FUNCTION check_low_stock();

-- Sample data (optional - remove in production)
-- INSERT INTO users (email, password_hash, full_name) VALUES 
-- ('demo@example.com', '$2b$12$example_hash', 'Demo User');

-- Views for analytics
CREATE OR REPLACE VIEW product_analytics AS
SELECT 
    p.user_id,
    p.name as product_name,
    p.quantity as current_stock,
    p.price_per_kg as current_price,
    p.minimum_stock,
    p.category,
    COALESCE(SUM(CASE WHEN it.transaction_type = 'add' THEN it.quantity_change ELSE 0 END), 0) as total_added,
    COALESCE(SUM(CASE WHEN it.transaction_type = 'remove' THEN it.quantity_change ELSE 0 END), 0) as total_consumed,
    COUNT(it.id) as transaction_count,
    MIN(it.created_at) as first_transaction,
    MAX(it.created_at) as last_transaction
FROM products p
LEFT JOIN inventory_transactions it ON p.name = it.product_name AND p.user_id = it.user_id
GROUP BY p.user_id, p.id, p.name, p.quantity, p.price_per_kg, p.minimum_stock, p.category;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT SELECT ON product_analytics TO authenticated;