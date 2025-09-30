import streamlit as st
import pandas as pd
import requests
import json
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import our Databricks connection module
from databricks_connection import get_databricks_manager

# Utility function to get databricks manager safely
def get_db_manager():
    """Get databricks manager safely"""
    return get_databricks_manager()

def call_agent_bricks_endpoint(application_data):
    """Call your Agent Bricks underwriting system"""
    import os
    
    # Check if using direct Python integration
    use_direct = os.getenv("USE_DIRECT_AGENT_BRICKS", "false").lower() == "true"
    
    if use_direct:
        # Use direct Agent Bricks Python integration
        try:
            from agent_bricks_integration import agent_bricks_underwrite
            st.info("🤖 Using Agent Bricks Direct Integration")
            return agent_bricks_underwrite(application_data)
        except ImportError as e:
            st.warning(f"Could not import Agent Bricks module: {e}. Using mock.")
            return create_mock_underwriting_decision(application_data)
        except Exception as e:
            st.error(f"Agent Bricks processing error: {e}")
            return create_mock_underwriting_decision(application_data)
    
    # Use HTTP API integration
    endpoint_url = os.getenv("AGENT_BRICKS_ENDPOINT")
    api_key = os.getenv("AGENT_BRICKS_API_KEY")
    
    if not endpoint_url:
        st.info("🔄 No Agent Bricks endpoint configured - using mock decision engine")
        return create_mock_underwriting_decision(application_data)
    
    try:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["Content-Type"] = "application/json"
        
        st.info(f"🌐 Calling Agent Bricks API: {endpoint_url}")
        start_time = time.time()
        response = requests.post(endpoint_url, json=application_data, headers=headers, timeout=30)
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            result['processing_time'] = processing_time
            return result
        else:
            st.error(f"Agent Bricks API error: {response.status_code}")
            return create_mock_underwriting_decision(application_data)
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not connect to Agent Bricks endpoint: {e}")
        return create_mock_underwriting_decision(application_data)

def create_mock_underwriting_decision(application_data):
    """Create a mock underwriting decision for demo purposes"""
    credit_score = application_data.get('credit_score', 650)
    income = application_data.get('annual_income', 0)
    loan_amount = application_data.get('loan_amount', 0)
    debt_to_income = application_data.get('debt_to_income_ratio', 25)
    
    # Simple decision logic for demo
    risk_score = 700 - credit_score + (debt_to_income * 2) + (loan_amount / income * 100 if income > 0 else 100)
    
    if credit_score >= 650 and income >= loan_amount * 0.2 and debt_to_income <= 40:
        decision = "approved"
        approved_amount = loan_amount
        interest_rate = max(3.5, 8.0 - (credit_score - 600) / 50)
        reasoning = f"Good credit score ({credit_score}), sufficient income, manageable debt ratio"
    else:
        decision = "rejected"
        approved_amount = 0
        interest_rate = None
        reasons = []
        if credit_score < 650:
            reasons.append(f"Credit score too low ({credit_score} < 650)")
        if income < loan_amount * 0.2:
            reasons.append("Insufficient income relative to loan amount")
        if debt_to_income > 40:
            reasons.append(f"High debt-to-income ratio ({debt_to_income}%)")
        reasoning = "; ".join(reasons)
    
    return {
        "decision": decision,
        "approved_amount": approved_amount,
        "interest_rate": interest_rate,
        "risk_score": risk_score,
        "reasoning": reasoning,
        "processing_time": 2.3
    }

@st.cache_resource
def initialize_databricks():
    """Initialize Databricks connection and create schema"""
    try:
        databricks_manager = get_db_manager()
        if not databricks_manager.credentials_available:
            if hasattr(databricks_manager, 'is_databricks_environment') and databricks_manager.is_databricks_environment:
                st.warning("⚠️ Databricks environment detected but connection failed - running in demo mode")
                st.info("💡 This may be due to missing SQL warehouse configuration or permissions")
            else:
                st.warning("⚠️ Databricks credentials not configured - running in demo mode")
                st.info("💡 To connect to Databricks, set environment variables: DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN")
            return False
        
        databricks_manager.create_schema_if_not_exists()
        st.success("✅ Databricks connection initialized successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Databricks connection failed: {e}")
        st.info("💡 The app will continue in demo mode. Check your environment variables.")
        return False

def main():
    st.set_page_config(
        page_title="Loan Underwriting System", 
        page_icon="🏦",
        layout="wide"
    )
    
    st.title("🏦 Loan Underwriting System")
    st.markdown("Powered by Databricks Agent Bricks")
    
    # Initialize Databricks connection
    databricks_connected = initialize_databricks()
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["New Application", "Check Status", "Analytics"])
    
    with tab1:
        st.header("Submit Loan Application")
        st.info("📝 Fill out the form below to get instant loan decision from our AI agents. Fields marked with * are required.")
        
        # Application form
        col1, col2 = st.columns(2)
        
        with col1:
            applicant_name = st.text_input("Full Name *", placeholder="Enter your full name")
            age = st.number_input("Age *", min_value=18, max_value=100, value=30)
            income = st.number_input("Annual Income ($) *", min_value=1, max_value=10000000, value=50000, step=1000)
            employment_type = st.selectbox("Employment Type", 
                                         ["Full-time", "Part-time", "Self-employed", "Unemployed"])
            credit_score = st.number_input("Credit Score *", min_value=300, max_value=850, value=650, step=10)
        
        with col2:
            loan_amount = st.number_input("Loan Amount ($) *", min_value=1000, max_value=10000000, value=25000, step=1000)
            loan_purpose = st.selectbox("Loan Purpose", 
                                      ["Home Purchase", "Auto", "Personal", "Business", "Education"])
            loan_term = st.selectbox("Loan Term (months)", [12, 24, 36, 48, 60, 120, 240, 360])
            down_payment = st.number_input("Down Payment ($)", min_value=0, value=0, step=1000)
            debt_to_income = st.slider("Debt-to-Income Ratio (%)", 0, 100, 25)
        
        if st.button("Submit Application", type="primary"):
            # Comprehensive validation
            validation_errors = []
            
            if not applicant_name or applicant_name.strip() == "":
                validation_errors.append("Full Name is required")
            if age < 18:
                validation_errors.append("Age must be 18 or older")
            if income <= 0:
                validation_errors.append("Annual Income must be greater than 0")
            if credit_score < 300 or credit_score > 850:
                validation_errors.append("Credit Score must be between 300 and 850")
            if loan_amount < 1000:
                validation_errors.append("Loan Amount must be at least $1,000")
            
            if validation_errors:
                st.error("Please fix the following errors:")
                for error in validation_errors:
                    st.error(f"• {error}")
            else:
                # Prepare application data
                application_data = {
                    "applicant_name": applicant_name,
                    "age": age,
                    "annual_income": income,
                    "employment_type": employment_type,
                    "credit_score": credit_score,
                    "loan_amount": loan_amount,
                    "loan_purpose": loan_purpose,
                    "loan_term": loan_term,
                    "down_payment": down_payment,
                    "debt_to_income_ratio": debt_to_income
                }
                
                # Call Agent Bricks for underwriting decision
                with st.spinner("Processing application..."):
                    try:
                        result = call_agent_bricks_endpoint(application_data)
                        
                        # Save to Databricks if connected
                        application_id = None
                        if databricks_connected:
                            try:
                                application_id = get_db_manager().save_loan_application(application_data, result)
                                st.success(f"📝 Application saved with ID: `{application_id}`")
                            except Exception as e:
                                st.warning(f"Could not save to database: {e}")
                        
                        # Display results
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            if result.get("decision") == "approved":
                                st.success("🎉 Congratulations! Your loan has been APPROVED")
                                
                                # Create metrics display
                                metric_col1, metric_col2, metric_col3 = st.columns(3)
                                with metric_col1:
                                    st.metric("Approved Amount", f"${result.get('approved_amount', loan_amount):,}")
                                with metric_col2:
                                    st.metric("Interest Rate", f"{result.get('interest_rate', 'TBD'):.2f}%")
                                with metric_col3:
                                    st.metric("Risk Score", f"{result.get('risk_score', 'N/A'):.0f}")
                                    
                            else:
                                st.error("❌ Unfortunately, your loan application has been REJECTED")
                                st.metric("Risk Score", f"{result.get('risk_score', 'N/A'):.0f}")
                        
                        with col2:
                            # Processing time and application ID
                            st.metric("Processing Time", f"{result.get('processing_time', 0):.1f}s")
                            if application_id:
                                st.text("Application ID:")
                                st.code(application_id)
                        
                        # Show reasoning
                        if result.get("reasoning"):
                            st.markdown("**Decision Reasoning:**")
                            st.info(result["reasoning"])
                        
                        # Download decision letter
                        if st.button("📄 Download Decision Letter"):
                            decision_letter = generate_decision_letter(application_data, result, application_id)
                            st.download_button(
                                label="📥 Download PDF",
                                data=decision_letter,
                                file_name=f"loan_decision_{application_id or 'demo'}.txt",
                                mime="text/plain"
                            )
                        
                    except Exception as e:
                        st.error(f"Error processing application: {str(e)}")
            else:
                st.error("Please fill in all required fields")
    
    with tab2:
        st.header("Check Application Status")
        
        application_id = st.text_input("Enter Application ID", placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000")
        
        if st.button("🔍 Check Status", type="primary"):
            if not application_id:
                st.error("Please enter an application ID")
            elif not databricks_connected:
                st.warning("Database connection required for status checking")
            else:
                with st.spinner("Looking up application..."):
                    try:
                        status_data = get_db_manager().get_application_status(application_id)
                        
                        if status_data:
                            st.success("✅ Application Found!")
                            
                            # Display application info
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("📋 Application Details")
                                st.write(f"**Applicant:** {status_data['applicant_name']}")
                                st.write(f"**Loan Amount:** ${status_data['loan_amount']:,}")
                                st.write(f"**Loan Purpose:** {status_data['loan_purpose']}")
                                st.write(f"**Submitted:** {status_data['application_timestamp']}")
                            
                            with col2:
                                st.subheader("📊 Decision Details")
                                decision = status_data['decision']
                                if decision == 'approved':
                                    st.success(f"✅ Status: {decision.upper()}")
                                    st.write(f"**Approved Amount:** ${status_data.get('approved_amount', 0):,}")
                                    st.write(f"**Interest Rate:** {status_data.get('interest_rate', 'N/A'):.2f}%")
                                else:
                                    st.error(f"❌ Status: {decision.upper()}")
                                
                                st.write(f"**Risk Score:** {status_data.get('risk_score', 'N/A'):.0f}")
                                st.write(f"**Processing Time:** {status_data.get('processing_time_seconds', 'N/A'):.1f}s")
                            
                            # Decision reasoning
                            if status_data.get('decision_reason'):
                                st.markdown("**Decision Reasoning:**")
                                st.info(status_data['decision_reason'])
                        else:
                            st.error("❌ Application not found. Please check the application ID.")
                            
                    except Exception as e:
                        st.error(f"Error retrieving application status: {e}")
        
        # Recent applications (if connected)
        if databricks_connected:
            st.markdown("---")
            st.subheader("📋 Recent Applications")
            try:
                # Query recent applications
                db_manager = get_db_manager()
                recent_query = f"""
                SELECT application_id, applicant_name, decision, application_timestamp, loan_amount
                FROM {db_manager.catalog}.{db_manager.schema}.loan_applications
                ORDER BY application_timestamp DESC
                LIMIT 10
                """
                recent_df = db_manager.execute_query(recent_query)
                
                if not recent_df.empty:
                    st.dataframe(
                        recent_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "application_id": "Application ID",
                            "applicant_name": "Applicant",
                            "decision": "Decision", 
                            "application_timestamp": "Submitted",
                            "loan_amount": st.column_config.NumberColumn("Loan Amount", format="$%d")
                        }
                    )
                else:
                    st.info("No applications found.")
            except Exception as e:
                st.warning(f"Could not load recent applications: {e}")
    
    with tab3:
        st.header("📊 Underwriting Analytics")
        
        if databricks_connected:
            # Get real analytics data
            try:
                db_manager = get_db_manager()
                analytics_data = db_manager.get_analytics_data()
                trends_data = db_manager.get_application_trends(days=30)
                
                # Metrics dashboard
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Applications Today", analytics_data['today_applications'], "📈")
                with col2:
                    st.metric("Approval Rate", f"{analytics_data['approval_rate']:.1f}%", "📊")
                with col3:
                    st.metric("Avg Processing Time", f"{analytics_data['avg_processing_time']:.1f}s", "⚡")
                with col4:
                    st.metric("Avg Credit Score", f"{analytics_data['avg_credit_score']}", "📋")
                
                # Charts section
                if not trends_data.empty:
                    st.markdown("### 📈 Application Trends (Last 30 Days)")
                    
                    # Create two columns for charts
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        # Applications over time
                        fig_apps = px.line(
                            trends_data, 
                            x='date', 
                            y=['total_applications', 'approved', 'rejected'],
                            title="Daily Applications",
                            labels={'value': 'Count', 'variable': 'Status'}
                        )
                        fig_apps.update_layout(height=400)
                        st.plotly_chart(fig_apps, use_container_width=True)
                    
                    with chart_col2:
                        # Average loan amounts
                        fig_amounts = px.bar(
                            trends_data,
                            x='date',
                            y='avg_loan_amount',
                            title="Average Loan Amount by Day",
                            labels={'avg_loan_amount': 'Amount ($)'}
                        )
                        fig_amounts.update_layout(height=400)
                        st.plotly_chart(fig_amounts, use_container_width=True)
                    
                    # Credit score distribution
                    if len(trends_data) > 0:
                        st.markdown("### 📊 Credit Score Trends")
                        fig_credit = px.line(
                            trends_data,
                            x='date',
                            y='avg_credit_score',
                            title="Average Credit Score Over Time"
                        )
                        fig_credit.update_layout(height=300)
                        st.plotly_chart(fig_credit, use_container_width=True)
                
                # Data table
                st.markdown("### 📋 Detailed Trends Data")
                if not trends_data.empty:
                    st.dataframe(
                        trends_data,
                        use_container_width=True,
                        column_config={
                            "date": "Date",
                            "total_applications": "Total Apps",
                            "approved": "Approved", 
                            "rejected": "Rejected",
                            "avg_loan_amount": st.column_config.NumberColumn("Avg Loan Amount", format="$%d"),
                            "avg_credit_score": st.column_config.NumberColumn("Avg Credit Score", format="%.0f")
                        }
                    )
                else:
                    st.info("No trend data available yet. Submit some applications to see analytics!")
                
            except Exception as e:
                st.error(f"Error loading analytics: {e}")
                # Fallback to demo metrics
                show_demo_analytics()
        else:
            st.warning("📡 Connect to Databricks to view real-time analytics")
            show_demo_analytics()

def show_demo_analytics():
    """Show demo analytics when Databricks is not connected"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Applications Today", "23", "5")
    with col2:
        st.metric("Approval Rate", "68%", "2%")
    with col3:
        st.metric("Avg Processing Time", "2.3s", "-0.3s")
    with col4:
        st.metric("Avg Credit Score", "650", "12")
    
    st.info("💡 Demo data shown. Connect to Databricks for real analytics.")

def generate_decision_letter(application_data, result, application_id):
    """Generate a text decision letter"""
    decision = result.get('decision', 'pending')
    timestamp = datetime.now().strftime("%B %d, %Y")
    
    letter = f"""
LOAN DECISION LETTER
{timestamp}

Application ID: {application_id or 'N/A'}

Dear {application_data.get('applicant_name', 'Applicant')},

Thank you for your loan application submitted on {timestamp}.

APPLICATION DETAILS:
- Requested Amount: ${application_data.get('loan_amount', 0):,}
- Loan Purpose: {application_data.get('loan_purpose', 'N/A')}
- Loan Term: {application_data.get('loan_term', 0)} months

DECISION: {decision.upper()}
"""
    
    if decision == 'approved':
        letter += f"""
APPROVED TERMS:
- Approved Amount: ${result.get('approved_amount', 0):,}
- Interest Rate: {result.get('interest_rate', 0):.2f}%
- Risk Assessment Score: {result.get('risk_score', 0):.0f}

NEXT STEPS:
1. You will receive loan documents within 2-3 business days
2. Please review and sign all documents
3. Funds will be disbursed upon completion of documentation

"""
    else:
        letter += f"""
REASON FOR DECLINE:
{result.get('reasoning', 'Standard underwriting criteria not met')}

We appreciate your interest and encourage you to reapply in the future.
"""
    
    letter += f"""
If you have any questions, please contact our customer service team.

Sincerely,
Loan Underwriting Department
Processing Time: {result.get('processing_time', 0):.1f} seconds
"""
    
    return letter

if __name__ == "__main__":
    main()
