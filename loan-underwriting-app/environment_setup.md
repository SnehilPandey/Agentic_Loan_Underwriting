# Environment Setup Guide

## Required Environment Variables

Set these environment variables before running the application:

### Databricks Configuration
```bash
export DATABRICKS_SERVER_HOSTNAME="your-workspace.databricks.com"
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/your-warehouse-id"  
export DATABRICKS_TOKEN="your-personal-access-token"
export DATABRICKS_CATALOG="main"
export DATABRICKS_SCHEMA="loan_underwriting"
```

### Agent Bricks Configuration  
```bash
export AGENT_BRICKS_ENDPOINT="https://your-agent-bricks-endpoint.com/api/underwrite"
export AGENT_BRICKS_API_KEY="your-agent-bricks-api-key"
```

### Application Configuration
```bash
export DEBUG="false"
export LOG_LEVEL="INFO"
```

## Setup Instructions

1. **Get Databricks Credentials:**
   - Login to your Databricks workspace
   - Go to User Settings → Access Tokens
   - Generate a new personal access token
   - Note your workspace hostname and SQL warehouse HTTP path

2. **Configure Agent Bricks:**
   - Set up your Agent Bricks endpoint URL
   - Obtain API key for authentication

3. **Set Environment Variables:**
   ```bash
   # Option 1: Export in terminal
   export DATABRICKS_SERVER_HOSTNAME="your-values-here"
   
   # Option 2: Create shell script
   source setup_env.sh
   
   # Option 3: Use with Streamlit
   streamlit run app.py --server.port 8000
   ```

## Testing Connection

Run the connection test:
```bash
python -c "from databricks_connection import databricks_manager; databricks_manager.get_sql_connection()"
```
