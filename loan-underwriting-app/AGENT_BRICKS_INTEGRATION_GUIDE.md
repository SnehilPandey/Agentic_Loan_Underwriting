# 🤖 Agent Bricks Integration Guide

This guide shows you how to integrate your Agent Bricks loan underwriting code with your Streamlit application.

## 🎯 **Integration Options**

### **Option 1: Direct Python Code Integration (Recommended)**
If you have Agent Bricks as Python code/functions/classes.

### **Option 2: HTTP API Integration**
If you have Agent Bricks deployed as a web service/API endpoint.

### **Option 3: Databricks Workspace Integration**
If your Agent Bricks is deployed in Databricks as a job/model endpoint.

---

## 🛠️ **Option 1: Direct Python Code Integration**

### **Step 1: Add Your Agent Bricks Code**

Edit `agent_bricks_integration.py` and replace the placeholder functions with your actual code:

```python
# In agent_bricks_integration.py
def agent_bricks_underwrite(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """Replace this with your actual Agent Bricks code"""
    
    # YOUR AGENT BRICKS CODE GOES HERE
    # ================================
    
    # Example patterns:
    
    # Pattern A: If you have a class-based system
    from your_agent_bricks.underwriter import LoanUnderwriter
    underwriter = LoanUnderwriter()
    result = underwriter.evaluate(application_data)
    
    # Pattern B: If you have function-based system  
    from your_agent_bricks.core import evaluate_loan
    result = evaluate_loan(application_data)
    
    # Pattern C: If you have ML model
    from your_agent_bricks.model import LoanModel
    model = LoanModel.load()
    prediction = model.predict(application_data)
    result = format_prediction(prediction)
    
    # Return in expected format
    return {
        "decision": result.decision,        # "approved" or "rejected"
        "approved_amount": result.amount,   # Dollar amount
        "interest_rate": result.rate,      # Percentage
        "risk_score": result.risk,         # Risk score
        "reasoning": result.explanation,   # Human-readable explanation
        "processing_time": processing_time # Time taken
    }
```

### **Step 2: Configure Environment**

Set the direct integration flag:
```bash
export USE_DIRECT_AGENT_BRICKS="true"
```

Or use the provided script:
```bash
# Edit databricks_env.sh and set:
export USE_DIRECT_AGENT_BRICKS="true"
```

### **Step 3: Test Integration**

```bash
./start_app.sh
```

Visit http://localhost:8001 and submit a loan application. You should see:
- "🤖 Using Agent Bricks Direct Integration" message
- Your Agent Bricks code processing the application
- Results saved to Databricks

---

## 🌐 **Option 2: HTTP API Integration**

### **Step 1: Configure API Endpoint**

Edit `databricks_env.sh`:
```bash
# Uncomment and configure these lines:
export AGENT_BRICKS_ENDPOINT="https://your-agent-bricks-api.com/underwrite"
export AGENT_BRICKS_API_KEY="your-api-key"

# Set this to false for HTTP API mode
export USE_DIRECT_AGENT_BRICKS="false"
```

### **Step 2: API Contract**

Your Agent Bricks API should accept POST requests with this format:

**Request:**
```json
{
    "applicant_name": "John Doe",
    "age": 35,
    "annual_income": 75000,
    "employment_type": "Full-time", 
    "credit_score": 720,
    "loan_amount": 250000,
    "loan_purpose": "Home Purchase",
    "loan_term": 360,
    "down_payment": 50000,
    "debt_to_income_ratio": 28
}
```

**Response:**
```json
{
    "decision": "approved",
    "approved_amount": 250000,
    "interest_rate": 4.25,
    "risk_score": 652,
    "reasoning": "Good credit score, sufficient income, manageable debt ratio",
    "processing_time": 2.3
}
```

---

## 🔧 **Option 3: Databricks Integration**

### **Step 1: Deploy Agent Bricks to Databricks**

Deploy your Agent Bricks code as:
- **Model Endpoint**: For ML-based underwriting
- **Job**: For batch or triggered processing
- **Function**: Using Databricks Functions

### **Step 2: Configure Endpoint**

```bash
# For Databricks model endpoints
export AGENT_BRICKS_ENDPOINT="https://your-workspace.databricks.com/model/your-model/invocations"
export AGENT_BRICKS_API_KEY="your-databricks-token"
```

---

## 🧪 **Testing Your Integration**

### **Test Script**

Create a test to verify your integration:

```python
# test_agent_bricks.py
from agent_bricks_integration import agent_bricks_underwrite

# Test application
test_application = {
    "applicant_name": "Test User",
    "age": 30,
    "annual_income": 80000,
    "employment_type": "Full-time",
    "credit_score": 750,
    "loan_amount": 200000,
    "loan_purpose": "Home Purchase", 
    "loan_term": 360,
    "down_payment": 40000,
    "debt_to_income_ratio": 25
}

# Test your Agent Bricks
result = agent_bricks_underwrite(test_application)
print("Agent Bricks Result:", result)

# Verify format
required_fields = ['decision', 'approved_amount', 'interest_rate', 'risk_score', 'reasoning']
for field in required_fields:
    if field not in result:
        print(f"❌ Missing field: {field}")
    else:
        print(f"✅ Found field: {field} = {result[field]}")
```

Run the test:
```bash
cd loan-underwriting-app
python test_agent_bricks.py
```

### **Integration Verification Checklist**

- [ ] Agent Bricks code returns expected format
- [ ] Decision logic works correctly  
- [ ] Error handling gracefully falls back to mock
- [ ] Processing time is reasonable (< 30 seconds)
- [ ] Results are saved to Databricks
- [ ] UI displays results correctly

---

## 🔍 **Debugging Integration Issues**

### **Common Issues & Solutions**

**1. Import Error**
```
ImportError: No module named 'your_agent_bricks'
```
**Solution**: Ensure your Agent Bricks code is in the Python path or install as a package.

**2. Format Error**
```
KeyError: 'decision'
```
**Solution**: Check that your Agent Bricks returns all required fields.

**3. Performance Issues**
```
Request timeout after 30s
```
**Solution**: Optimize your Agent Bricks processing or increase timeout.

### **Debug Mode**

Enable debug logging by adding to your environment:
```bash
export DEBUG="true"
export LOG_LEVEL="DEBUG"
```

### **View Logs**

Monitor the Streamlit application logs for integration messages:
- "🤖 Using Agent Bricks Direct Integration" - Direct mode active
- "🌐 Calling Agent Bricks API" - HTTP API mode active  
- "🔄 No Agent Bricks endpoint configured" - Using mock mode

---

## 🚀 **Advanced Integration Patterns**

### **A/B Testing Multiple Models**

```python
def agent_bricks_underwrite(application_data):
    model_version = os.getenv("AGENT_BRICKS_MODEL_VERSION", "v1")
    
    if model_version == "v1":
        return underwrite_model_v1(application_data)
    elif model_version == "v2":
        return underwrite_model_v2(application_data)
    else:
        return underwrite_ensemble(application_data)
```

### **Feature Flags**

```python
def agent_bricks_underwrite(application_data):
    # Enable/disable specific features
    use_credit_bureau = os.getenv("USE_CREDIT_BUREAU", "true") == "true"
    use_ml_model = os.getenv("USE_ML_MODEL", "false") == "true"
    
    if use_ml_model:
        return ml_based_underwriting(application_data)
    else:
        return rule_based_underwriting(application_data)
```

### **Multi-Stage Processing**

```python
def agent_bricks_underwrite(application_data):
    # Stage 1: Data validation
    if not validate_application(application_data):
        return rejection_response("Invalid application data")
    
    # Stage 2: Risk assessment
    risk_score = calculate_risk(application_data)
    
    # Stage 3: Decision making
    decision = make_decision(application_data, risk_score)
    
    # Stage 4: Post-processing
    return format_response(decision, risk_score)
```

---

## 📞 **Need Help?**

1. **Check the application logs** for integration messages
2. **Test with the mock system first** to ensure UI works
3. **Use the test script** to debug your Agent Bricks code
4. **Start simple** - get basic integration working, then add complexity

## 🎉 **Integration Complete!**

Once integrated, your application will:
- ✅ Use your real Agent Bricks underwriting logic
- ✅ Store results in Databricks Unity Catalog
- ✅ Display professional loan decisions
- ✅ Generate decision letters with your logic
- ✅ Provide real-time analytics on your decisions

**Ready to integrate? Edit `agent_bricks_integration.py` with your code and restart the app!**
