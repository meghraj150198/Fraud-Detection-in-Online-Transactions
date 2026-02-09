#!/bin/bash

# Fraud Detection Dashboard - Startup Script
# This script starts the Streamlit dashboard for fraud detection

echo "🚀 Starting Fraud Detection Dashboard..."
echo ""

# Check if Python virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not detected"
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if required dependencies are installed
echo "📦 Checking dependencies..."
python -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Streamlit..."
    pip install -q streamlit plotly
fi

# Check if required data files exist
echo "📋 Checking data files..."
if [ ! -f "sales_with_fraud_indicators.csv" ]; then
    echo "❌ Error: sales_with_fraud_indicators.csv not found"
    echo "   Please run the feature engineering pipeline first"
    exit 1
fi

if [ ! -d "fraud_system_output" ]; then
    echo "⚠️ Warning: fraud_system_output directory not found"
    echo "   Running integration pipeline to generate scored data..."
    python fraud_system_integration.py > /dev/null 2>&1
fi

# Start the dashboard
echo ""
echo "✅ All checks passed!"
echo ""
echo "🎉 Dashboard is launching..."
echo "📊 Open your browser and navigate to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Run streamlit
streamlit run dashboard.py --logger.level=error

# Cleanup on exit
echo ""
echo "👋 Dashboard stopped"
