#!/bin/bash
# Setup script for Loan Underwriting Application

echo "🏦 Setting up Loan Underwriting Application Environment"
echo "=================================================="

# Function to prompt for environment variable
prompt_env_var() {
    local var_name=$1
    local description=$2
    local current_value=$(eval echo \$$var_name)
    
    if [ -n "$current_value" ]; then
        echo "✅ $var_name is already set: ${current_value:0:20}..."
    else
        echo "❓ Please enter $description:"
        read -r user_input
        if [ -n "$user_input" ]; then
            export $var_name="$user_input"
            echo "export $var_name=\"$user_input\"" >> ~/.bashrc
            echo "✅ $var_name set successfully"
        else
            echo "⚠️  $var_name left empty (will use demo mode)"
        fi
    fi
}

echo ""
echo "📡 Configuring Databricks Connection..."
echo "----------------------------------------"

# Databricks configuration
prompt_env_var "DATABRICKS_SERVER_HOSTNAME" "Databricks workspace hostname (e.g., your-workspace.databricks.com)"
prompt_env_var "DATABRICKS_HTTP_PATH" "SQL Warehouse HTTP path (e.g., /sql/1.0/warehouses/abc123def456)"
prompt_env_var "DATABRICKS_TOKEN" "Personal access token"

# Optional Databricks settings
if [ -z "$DATABRICKS_CATALOG" ]; then
    export DATABRICKS_CATALOG="main"
    echo "📝 Using default catalog: main"
fi

if [ -z "$DATABRICKS_SCHEMA" ]; then
    export DATABRICKS_SCHEMA="loan_underwriting"
    echo "📝 Using default schema: loan_underwriting"
fi

echo ""
echo "🤖 Configuring Agent Bricks Integration..."
echo "------------------------------------------"

# Agent Bricks configuration
prompt_env_var "AGENT_BRICKS_ENDPOINT" "Agent Bricks API endpoint URL"
prompt_env_var "AGENT_BRICKS_API_KEY" "Agent Bricks API key"

echo ""
echo "🔧 Application Settings..."
echo "--------------------------"

if [ -z "$DEBUG" ]; then
    export DEBUG="false"
    echo "📝 Debug mode: false"
fi

if [ -z "$LOG_LEVEL" ]; then
    export LOG_LEVEL="INFO"
    echo "📝 Log level: INFO"
fi

echo ""
echo "🧪 Testing Configuration..."
echo "---------------------------"

# Test Python imports
python3 -c "
import sys
try:
    import streamlit
    print('✅ Streamlit imported successfully')
except ImportError as e:
    print('❌ Streamlit import failed:', e)
    sys.exit(1)

try:
    import pandas
    print('✅ Pandas imported successfully')
except ImportError as e:
    print('❌ Pandas import failed:', e)
    sys.exit(1)

try:
    from databricks import sql
    print('✅ Databricks SQL connector imported successfully')
except ImportError as e:
    print('❌ Databricks SQL connector import failed:', e)
    sys.exit(1)

try:
    import plotly
    print('✅ Plotly imported successfully')
except ImportError as e:
    print('❌ Plotly import failed:', e)
    sys.exit(1)

print('🎉 All required packages are available!')
"

# Test Databricks connection if configured
if [ -n "$DATABRICKS_SERVER_HOSTNAME" ] && [ -n "$DATABRICKS_TOKEN" ]; then
    echo "🔍 Testing Databricks connection..."
    python3 -c "
from databricks_connection import databricks_manager
try:
    connection = databricks_manager.get_sql_connection()
    print('✅ Databricks connection successful!')
except Exception as e:
    print('⚠️  Databricks connection failed:', e)
    print('💡 App will run in demo mode')
"
else
    echo "⚠️  Databricks credentials not fully configured - app will run in demo mode"
fi

echo ""
echo "🚀 Setup Complete!"
echo "=================="
echo "To start the application, run:"
echo "streamlit run app.py --server.port 8000"
echo ""
echo "The application will be available at: http://localhost:8000"
echo ""
echo "To reconfigure environment variables, delete ~/.bashrc entries and re-run this script."
