# 🏦 Loan Underwriting System

A modern loan underwriting application powered by **Databricks Agent Bricks** and built with **Streamlit**.

## Features

- 📋 **Interactive Loan Application Form** - Complete borrower information capture
- 🤖 **AI-Powered Underwriting** - Automated decision making via Agent Bricks
- 📊 **Real-time Analytics Dashboard** - Application metrics and trends
- 🔍 **Application Status Tracking** - Check loan application progress
- 💾 **Data Storage** - Integration with Databricks Unity Catalog

## Quick Start

### 🚀 **FASTEST WAY TO START:**
```bash
./start_app.sh
```
*This script handles everything automatically!*

### Prerequisites
- Python 3.11+ ✅ **READY**
- Virtual environment ✅ **CONFIGURED** 
- Databricks workspace ✅ **CONNECTED**
- Dependencies installed ✅ **COMPLETE**

### Installation & Setup

1. **Option 1 - Quick Launch (Recommended):**
   ```bash
   ./start_app.sh
   ```

2. **Option 2 - Manual Setup:**
   ```bash
   # First-time setup: Create your environment file
   cp databricks_env.sh.template databricks_env.sh
   # Edit databricks_env.sh with your actual credentials
   
   # Load environment
   source databricks_env.sh
   
   # Activate virtual environment  
   source ../myenv/bin/activate
   
   # Start application
   streamlit run app.py --server.port 8001
   ```

3. **Option 3 - Interactive Setup:**
   ```bash
   ./setup_environment.sh
   ```

## Application Structure

```
loan-underwriting-app/
├── app.py                      # Enhanced Streamlit application
├── agent_bricks_integration.py # Multi-agent underwriting system
├── databricks_connection.py    # Database integration module
├── config.py                   # Application configuration
├── requirements.txt            # Python dependencies
├── start_app.sh               # Quick launch script ⚡
├── databricks_env.sh.template # Environment template (SAFE) 📋
├── setup_environment.sh       # Interactive setup guide
├── app.yaml                   # Deployment configuration
├── deployment.yaml            # Kubernetes deployment
├── environment_setup.md       # Setup documentation
├── .streamlit/
│   └── config.toml           # UI theming
└── README.md                 # This file

🔒 SECURITY: databricks_env.sh (with real credentials) is excluded via .gitignore
```

## Configuration

The app uses environment variables for configuration:

- **DATABRICKS_SERVER_HOSTNAME** - Your Databricks workspace URL
- **DATABRICKS_HTTP_PATH** - SQL Warehouse HTTP path  
- **DATABRICKS_TOKEN** - Personal access token
- **AGENT_BRICKS_ENDPOINT** - Agent Bricks API endpoint
- **AGENT_BRICKS_API_KEY** - Agent Bricks authentication key

## Usage

### 1. New Loan Application
- Fill out the borrower information form
- Submit for automated underwriting decision
- View approval/rejection with reasoning

### 2. Application Status
- Track existing applications by ID
- View processing status and updates

### 3. Analytics Dashboard  
- Monitor application volume and trends
- View approval rates and processing times
- Analyze risk metrics

## Databricks Integration

This app integrates with:
- **Unity Catalog** - For data storage and governance
- **SQL Warehouses** - For data processing
- **Agent Bricks** - For AI-powered underwriting decisions

## Customization

Edit `config.py` to modify:
- Loan amount limits
- Credit score ranges
- Processing timeouts
- Debug settings

## Security

🔐 **Credential Protection:**
- `databricks_env.sh` with real credentials is **git-ignored**
- Use `databricks_env.sh.template` as a safe starting point
- Never commit files containing API keys or tokens

🛡️ **Application Security:**
- Environment-based configuration
- Secure token handling
- CORS protection
- Input validation

⚠️ **Important:** Always copy the template and add your real credentials:
```bash
cp databricks_env.sh.template databricks_env.sh
# Edit databricks_env.sh with your actual values
```

## Support

For issues or questions:
1. Check Databricks documentation
2. Review Agent Bricks API docs
3. Verify environment configuration
