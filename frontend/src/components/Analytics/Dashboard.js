import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import './Dashboard.css';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [predictions, setPredictions] = useState({});

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/analytics/dashboard`);
      if (response.data.success) {
        setDashboardData(response.data.dashboard);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadProductPrediction = async (productName) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/analytics/predictions/${productName}`);
      if (response.data.success) {
        setPredictions(prev => ({
          ...prev,
          [productName]: response.data.prediction
        }));
      }
    } catch (error) {
      console.error('Failed to load prediction:', error);
      toast.error('Failed to load prediction');
    }
  };

  const handleProductSelect = (productName) => {
    setSelectedProduct(productName);
    if (!predictions[productName]) {
      loadProductPrediction(productName);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="dashboard-error">
        <p>Failed to load dashboard data</p>
        <button onClick={loadDashboardData}>Retry</button>
      </div>
    );
  }

  const { summary, products, alerts, recent_transactions } = dashboardData;

  // Prepare chart data
  const categoryData = products.reduce((acc, product) => {
    const category = product.category || 'general';
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  const pieChartData = Object.entries(categoryData).map(([category, count]) => ({
    name: category,
    value: count
  }));

  const stockLevels = products.map(product => ({
    name: product.name,
    current: product.quantity,
    minimum: product.minimum_stock || 1,
    value: product.quantity * product.price_per_kg
  }));

  const transactionData = recent_transactions
    .slice(0, 7)
    .reverse()
    .map(transaction => ({
      date: format(new Date(transaction.created_at), 'MM/dd'),
      quantity: transaction.quantity_change,
      type: transaction.transaction_type
    }));

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📊 Analytics Dashboard</h1>
        <button onClick={loadDashboardData} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-icon">📦</div>
          <div className="card-content">
            <h3>Total Products</h3>
            <p className="card-value">{summary.total_products}</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="card-icon">💰</div>
          <div className="card-content">
            <h3>Inventory Value</h3>
            <p className="card-value">₹{summary.total_inventory_value.toFixed(2)}</p>
          </div>
        </div>
        
        <div className="summary-card alert-card">
          <div className="card-icon">⚠️</div>
          <div className="card-content">
            <h3>Low Stock Alerts</h3>
            <p className="card-value">{summary.low_stock_alerts}</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="card-icon">📈</div>
          <div className="card-content">
            <h3>Recent Transactions</h3>
            <p className="card-value">{summary.recent_transactions}</p>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-container">
          <h3>Product Categories</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Stock Levels vs Minimum Stock</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stockLevels}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="current" fill="#8884d8" name="Current Stock" />
              <Bar dataKey="minimum" fill="#ff7300" name="Minimum Stock" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Transactions Chart */}
      <div className="chart-container full-width">
        <h3>Recent Transaction Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={transactionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="quantity" stroke="#8884d8" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Alerts Section */}
      {alerts.count > 0 && (
        <div className="alerts-section">
          <h3>🚨 Low Stock Alerts</h3>
          <div className="alerts-grid">
            {alerts.alerts.map((alert, index) => (
              <div key={index} className="alert-card-item">
                <div className="alert-header">
                  <h4>{alert.product.name}</h4>
                  <span className={`urgency-badge ${alert.prediction.recommendation?.urgency?.toLowerCase()}`}>
                    {alert.prediction.recommendation?.urgency || 'LOW'}
                  </span>
                </div>
                <div className="alert-details">
                  <p><strong>Current Stock:</strong> {alert.product.quantity} kg</p>
                  <p><strong>Minimum Stock:</strong> {alert.product.minimum_stock} kg</p>
                  {alert.prediction.recommendation && (
                    <p><strong>Suggestion:</strong> {alert.prediction.recommendation.message}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Product Predictions */}
      <div className="predictions-section">
        <h3>📈 Stock Predictions</h3>
        <div className="product-selector">
          <select 
            value={selectedProduct} 
            onChange={(e) => handleProductSelect(e.target.value)}
          >
            <option value="">Select a product for prediction</option>
            {products.map(product => (
              <option key={product.id} value={product.name}>
                {product.name}
              </option>
            ))}
          </select>
        </div>

        {selectedProduct && predictions[selectedProduct] && (
          <div className="prediction-result">
            <h4>Prediction for {selectedProduct}</h4>
            <div className="prediction-details">
              <div className="prediction-item">
                <span>Current Stock:</span>
                <span>{predictions[selectedProduct].current_stock} kg</span>
              </div>
              <div className="prediction-item">
                <span>Consumption Rate:</span>
                <span>{predictions[selectedProduct].consumption_rate_per_day.toFixed(2)} kg/day</span>
              </div>
              <div className="prediction-item">
                <span>Days Until Low Stock:</span>
                <span>{predictions[selectedProduct].days_until_depletion.toFixed(1)} days</span>
              </div>
              {predictions[selectedProduct].recommendation && (
                <div className="recommendation">
                  <h5>Recommendation:</h5>
                  <p>{predictions[selectedProduct].recommendation.message}</p>
                  {predictions[selectedProduct].recommendation.suggested_reorder_quantity > 0 && (
                    <p><strong>Suggested Reorder:</strong> {predictions[selectedProduct].recommendation.suggested_reorder_quantity.toFixed(1)} kg</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;