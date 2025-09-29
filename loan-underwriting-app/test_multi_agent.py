#!/usr/bin/env python3
"""
Test script for multi-agent loan underwriting integration
"""

from agent_bricks_integration import agent_bricks_underwrite

def test_multi_agent_integration():
    """Test the multi-agent loan evaluation system"""
    
    print("🧪 Testing Multi-Agent Loan Underwriting System")
    print("=" * 60)
    
    # Test application data
    test_applications = [
        {
            "applicant_name": "John Doe",
            "age": 35,
            "annual_income": 80000,
            "employment_type": "Full-time",
            "credit_score": 750,
            "loan_amount": 200000,
            "loan_purpose": "Home Purchase",
            "loan_term": 360,
            "down_payment": 40000,
            "debt_to_income_ratio": 25
        },
        {
            "applicant_name": "Jane Smith", 
            "age": 28,
            "annual_income": 45000,
            "employment_type": "Part-time",
            "credit_score": 620,
            "loan_amount": 150000,
            "loan_purpose": "Auto",
            "loan_term": 60,
            "down_payment": 5000,
            "debt_to_income_ratio": 45
        }
    ]
    
    for i, application in enumerate(test_applications, 1):
        print(f"\n🔍 Test Case {i}: {application['applicant_name']}")
        print(f"Credit Score: {application['credit_score']}, Income: ${application['annual_income']:,}, Loan: ${application['loan_amount']:,}")
        print("-" * 40)
        
        try:
            # Call your multi-agent underwriting system
            result = agent_bricks_underwrite(application)
            
            # Display results
            print(f"🎯 Decision: {result['decision'].upper()}")
            print(f"💰 Approved Amount: ${result.get('approved_amount', 0):,}")
            print(f"📊 Interest Rate: {result.get('interest_rate', 0):.2f}%")
            print(f"⚖️ Risk Score: {result.get('risk_score', 0):.0f}")
            print(f"⏱️ Processing Time: {result.get('processing_time', 0):.2f}s")
            print(f"💬 Reasoning: {result.get('reasoning', 'N/A')}")
            
            # Display agent details if available
            if 'agent_details' in result and result['agent_details']:
                print(f"\n🤖 Agent Breakdown:")
                for agent in result['agent_details']:
                    status = "✅" if agent['decision'] == 'approve' else "❌"
                    print(f"   {status} {agent['agent']}: {agent['decision']} ({agent['confidence']:.1f}% confidence)")
                    print(f"      Reasoning: {agent['reasoning']}")
            
            # Validate required fields
            required_fields = ['decision', 'approved_amount', 'interest_rate', 'risk_score', 'reasoning']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"⚠️ Missing fields: {missing_fields}")
            else:
                print("✅ All required fields present")
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 Multi-Agent Integration Test Complete!")
    print("\nNext Steps:")
    print("1. Replace mock agents with your actual agent orchestration code")
    print("2. Update the imports to use your agent modules")
    print("3. Test with your real agent system")
    print("4. Restart the Streamlit app to use your agents")

if __name__ == "__main__":
    test_multi_agent_integration()
