#!/bin/bash
# Quick Start Script for Loan Underwriting Application

echo "🏦 Starting Loan Underwriting Application..."
echo "==========================================="

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "../myenv" ]; then
    source ../myenv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Load Databricks environment
if [ -f "databricks_env.sh" ]; then
    source databricks_env.sh
else
    echo "⚠️  Databricks credentials not found - running in demo mode"
fi

# Check if port is available
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8001 is in use. Trying port 8002..."
    PORT=8002
else
    PORT=8001
fi

echo ""
echo "🚀 Launching application on port $PORT..."
echo "📱 Access URL: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start Streamlit
streamlit run app.py --server.port $PORT --browser.gatherUsageStats false
