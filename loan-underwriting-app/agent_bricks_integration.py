"""
Multi-Agent Loan Underwriting System Implementation
Databricks Agent Bricks Integration
"""

import json
import requests
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

@dataclass
class LoanApplication:
    """Loan application data structure"""
    customer_id: str
    applicant_name: str
    age: int
    annual_income: float
    credit_score: int
    loan_amount: float
    loan_purpose: str
    employment_type: str
    debt_to_income: float
    documents: List[str]

@dataclass
class AgentResponse:
    """Standardized agent response structure"""
    agent_name: str
    status: str
    data: Dict[str, Any]
    confidence: float
    timestamp: datetime

class MultiAgentLoanUnderwriter:
    """
    Multi-Agent Loan Underwriting System Controller
    Coordinates specialist agents for comprehensive loan processing
    """

    def __init__(self, databricks_config: Dict[str, str]):
        self.config = databricks_config
        self.agents = {
            'document_extractor': 'loan-document-extractor',
            'credit_analyzer': 'credit-risk-analyzer', 
            'compliance_checker': 'compliance-checker',
            'decision_maker': 'loan-decision-maker',
            'supervisor': 'multi-agent-loan-supervisor'
        }
        self.processing_results = {}

    def call_agent_endpoint(self, agent_name: str, query: str, context: Dict = None) -> AgentResponse:
        """
        Call individual agent endpoint
        In production, this would use Databricks Agent Bricks API
        """
        # Simulated agent responses for demonstration
        mock_responses = self._get_mock_responses()

        response_data = mock_responses.get(agent_name, {})

        return AgentResponse(
            agent_name=agent_name,
            status="success",
            data=response_data,
            confidence=0.85,
            timestamp=datetime.now()
        )

    def extract_documents(self, documents: List[str]) -> AgentResponse:
        """
        Extract financial information from loan documents
        """
        query = f"Extract financial information from these documents: {documents}"
        return self.call_agent_endpoint('document_extractor', query)

    def analyze_credit_risk(self, financial_data: Dict) -> AgentResponse:
        """
        Analyze credit risk based on extracted financial data
        """
        query = f"Analyze credit risk for applicant with data: {json.dumps(financial_data)}"
        return self.call_agent_endpoint('credit_analyzer', query)

    def check_compliance(self, application_data: Dict) -> AgentResponse:
        """
        Verify regulatory compliance requirements
        """
        query = f"Check compliance for loan application: {json.dumps(application_data)}"
        return self.call_agent_endpoint('compliance_checker', query)

    def make_loan_decision(self, analysis_results: Dict) -> AgentResponse:
        """
        Make final loan approval decision
        """
        query = f"Make loan decision based on analysis: {json.dumps(analysis_results)}"
        return self.call_agent_endpoint('decision_maker', query)

    def process_loan_application(self, application: LoanApplication) -> Dict[str, Any]:
        """
        Process complete loan application through multi-agent workflow
        """
        print(f"\n=== Processing Loan Application: {application.customer_id} ===")

        # Step 1: Document Extraction
        print("Step 1: Extracting document information...")
        doc_response = self.extract_documents(application.documents)
        self.processing_results['document_extraction'] = doc_response
        print(f"  ✓ Extracted: {doc_response.data.get('summary', 'Financial data extracted')}")

        # Step 2: Credit Risk Analysis
        print("Step 2: Analyzing credit risk...")
        credit_data = {
            'credit_score': application.credit_score,
            'annual_income': application.annual_income,
            'debt_to_income': application.debt_to_income,
            'extracted_data': doc_response.data
        }
        credit_response = self.analyze_credit_risk(credit_data)
        self.processing_results['credit_analysis'] = credit_response
        print(f"  ✓ Risk Level: {credit_response.data.get('risk_level', 'Medium')}")

        # Step 3: Compliance Verification
        print("Step 3: Checking regulatory compliance...")
        compliance_data = {
            'application': application.__dict__,
            'extracted_data': doc_response.data
        }
        compliance_response = self.check_compliance(compliance_data)
        self.processing_results['compliance_check'] = compliance_response
        print(f"  ✓ Compliance Status: {compliance_response.data.get('status', 'Passed')}")

        # Step 4: Final Decision
        print("Step 4: Making final loan decision...")
        decision_data = {
            'document_extraction': doc_response.data,
            'credit_analysis': credit_response.data,
            'compliance_check': compliance_response.data,
            'application': application.__dict__
        }
        decision_response = self.make_loan_decision(decision_data)
        self.processing_results['final_decision'] = decision_response
        print(f"  ✓ Decision: {decision_response.data.get('decision', 'Approved')}")

        # Generate comprehensive report
        return self._generate_underwriting_report(application, self.processing_results)

    def _generate_underwriting_report(self, application: LoanApplication, results: Dict) -> Dict[str, Any]:
        """Generate comprehensive underwriting report"""

        decision_data = results['final_decision'].data

        report = {
            'application_id': application.customer_id,
            'applicant_name': application.applicant_name,
            'processing_timestamp': datetime.now().isoformat(),

            # Extracted Information
            'extracted_data': results['document_extraction'].data,

            # Risk Analysis
            'risk_assessment': {
                'risk_level': results['credit_analysis'].data.get('risk_level', 'Medium'),
                'risk_score': results['credit_analysis'].data.get('risk_score', 0.5),
                'key_factors': results['credit_analysis'].data.get('risk_factors', [])
            },

            # Compliance Status  
            'compliance': {
                'status': results['compliance_check'].data.get('status', 'Passed'),
                'issues': results['compliance_check'].data.get('issues', [])
            },

            # Final Decision
            'decision': {
                'status': decision_data.get('decision', 'Approved'),
                'approved_amount': decision_data.get('approved_amount', application.loan_amount),
                'interest_rate': decision_data.get('interest_rate', 5.5),
                'loan_term': decision_data.get('loan_term', 360),
                'conditions': decision_data.get('conditions', []),
                'reasoning': decision_data.get('reasoning', 'Standard approval based on creditworthiness')
            },

            # Processing Metrics
            'processing_metrics': {
                'total_time_seconds': 45,  # Simulated processing time
                'confidence_scores': {
                    'document_extraction': results['document_extraction'].confidence,
                    'credit_analysis': results['credit_analysis'].confidence,
                    'compliance_check': results['compliance_check'].confidence,
                    'final_decision': results['final_decision'].confidence
                }
            }
        }

        return report

    def _get_mock_responses(self) -> Dict[str, Dict]:
        """Mock agent responses for demonstration"""
        return {
            'document_extractor': {
                'summary': 'Financial documents processed successfully',
                'extracted_income': 85000,
                'extracted_assets': 125000,
                'extracted_debts': 15000,
                'employment_verified': True,
                'bank_balance': 45000
            },
            'credit_analyzer': {
                'risk_level': 'Low',
                'risk_score': 0.25,
                'recommended_amount': 280000,
                'recommended_rate': 4.25,
                'risk_factors': ['Stable employment', 'Good credit history', 'Low DTI'],
                'approval_probability': 0.92
            },
            'compliance_checker': {
                'status': 'Passed',
                'issues': [],
                'verified_requirements': [
                    'Identity verification completed',
                    'Income documentation adequate', 
                    'Credit report obtained with consent',
                    'ECOA compliance verified'
                ]
            },
            'decision_maker': {
                'decision': 'Approved',
                'approved_amount': 280000,
                'interest_rate': 4.25,
                'loan_term': 360,
                'conditions': ['Property appraisal required', 'Final employment verification'],
                'reasoning': 'Applicant meets all qualification criteria with strong financial profile'
            }
        }

def agent_bricks_underwrite(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replace this function with your actual Agent Bricks underwriting logic
    
    Args:
        application_data: Dictionary containing loan application data
        
    Returns:
        Dictionary with underwriting decision
    """
    
    start_time = time.time()
    
    # YOUR ACTUAL MULTI-AGENT ORCHESTRATION
    # =====================================
    
    try:
        # Step 1: Initialize your Multi-Agent Loan Underwriter
        databricks_config = {
            'workspace_url': 'https://your-workspace.cloud.databricks.com',
            'token': 'your-databricks-token'
        }
        
        underwriter = MultiAgentLoanUnderwriter(databricks_config)
        
        # Step 2: Convert Streamlit application data to LoanApplication format
        loan_app = LoanApplication(
            customer_id=f"CUST_{int(time.time())}",  # Generate unique ID
            applicant_name=application_data.get('applicant_name', 'Unknown'),
            age=int(application_data.get('age', 30)),
            annual_income=float(application_data.get('annual_income', 0)),
            credit_score=int(application_data.get('credit_score', 650)),
            loan_amount=float(application_data.get('loan_amount', 0)),
            loan_purpose=application_data.get('loan_purpose', 'Personal'),
            employment_type=application_data.get('employment_type', 'Employed'),
            debt_to_income=float(application_data.get('debt_to_income_ratio', 25)) / 100.0,  # Convert % to decimal
            documents=["pay_stub.pdf", "bank_statement.pdf", "tax_return.pdf"]  # Mock documents
        )
        
        print(f"🤖 Processing loan application through multi-agent system...")
        
        # Step 3: Process through your multi-agent workflow
        report = underwriter.process_loan_application(loan_app)
        
        # Step 4: Extract results from your comprehensive report
        decision_data = report['decision']
        risk_data = report['risk_assessment']
        
        # Map to expected format
        final_decision = {
            "status": "approved" if decision_data['status'].lower() == 'approved' else "rejected",
            "amount": decision_data['approved_amount'],
            "rate": decision_data['interest_rate'],
            "reason": decision_data['reasoning']
        }
        
        # Convert risk score (your system uses 0-1 scale, app expects 300-850)
        risk_score_normalized = risk_data['risk_score']  # 0-1 scale
        risk_score = 300 + (risk_score_normalized * 550)  # Convert to 300-850 scale
        
        # Build agent details for UI display
        agent_results = {
            "agent_decisions": [
                {
                    "agent": "document_extractor",
                    "decision": "approve",
                    "confidence": report['processing_metrics']['confidence_scores']['document_extraction'] * 100,
                    "reasoning": report['extracted_data']['summary']
                },
                {
                    "agent": "credit_analyzer", 
                    "decision": "approve" if risk_data['risk_level'].lower() == 'low' else "reject",
                    "confidence": report['processing_metrics']['confidence_scores']['credit_analysis'] * 100,
                    "reasoning": f"Risk level: {risk_data['risk_level']}, Key factors: {', '.join(risk_data['key_factors'])}"
                },
                {
                    "agent": "compliance_checker",
                    "decision": "approve" if report['compliance']['status'] == 'Passed' else "reject", 
                    "confidence": report['processing_metrics']['confidence_scores']['compliance_check'] * 100,
                    "reasoning": f"Compliance: {report['compliance']['status']}"
                },
                {
                    "agent": "decision_maker",
                    "decision": "approve" if decision_data['status'].lower() == 'approved' else "reject",
                    "confidence": report['processing_metrics']['confidence_scores']['final_decision'] * 100,
                    "reasoning": decision_data['reasoning']
                }
            ],
            "final_decision": final_decision,
            "risk_score": risk_score,
            "orchestration_summary": f"Processed by {len(underwriter.agents)} specialist agents",
            "full_report": report  # Include full report for debugging
        }
        
        print(f"✅ Multi-agent processing complete: {decision_data['status']}")
        
    except Exception as e:
        print(f"❌ Multi-agent orchestration failed: {e}")
        # Fallback to simple decision
        risk_score = calculate_risk_score(application_data)
        final_decision = make_underwriting_decision(application_data, risk_score)
        agent_results = {"agent_decisions": [], "full_report": {"error": str(e)}}
    
    # ========================================================
    # END: Replace this section with your Agent Bricks code
    
    processing_time = time.time() - start_time
    
    # Return in the expected format
    result = {
        "decision": final_decision["status"],           # "approved" or "rejected"
        "approved_amount": final_decision.get("amount", 0),
        "interest_rate": final_decision.get("rate", 0),
        "risk_score": risk_score,
        "reasoning": final_decision.get("reason", ""),
        "processing_time": processing_time,
        "agent_details": agent_results.get("agent_decisions", [])  # Include agent details
    }
    
    return result

# Legacy fallback functions (kept for compatibility)

def calculate_interest_rate_fallback(application_data: Dict[str, Any], agent_decisions: list) -> float:
    """Calculate interest rate - fallback function"""
    credit_score = application_data.get('credit_score', 650)
    base_rate = 6.5
    credit_adjustment = (750 - credit_score) * 0.01
    final_rate = base_rate + credit_adjustment
    return max(3.0, min(15.0, round(final_rate, 2)))

def calculate_risk_score(application_data: Dict[str, Any]) -> float:
    """
    Calculate risk score - replace with your Agent Bricks risk calculation
    """
    # TODO: Replace with your Agent Bricks risk calculation
    credit_score = application_data.get('credit_score', 650)
    income = application_data.get('annual_income', 0)
    loan_amount = application_data.get('loan_amount', 0)
    debt_to_income = application_data.get('debt_to_income_ratio', 25)
    
    # Simple risk calculation (replace with your logic)
    base_risk = 700 - credit_score
    income_risk = (loan_amount / income * 100) if income > 0 else 100
    debt_risk = debt_to_income * 2
    
    total_risk = base_risk + income_risk + debt_risk
    return min(max(total_risk, 300), 850)  # Clamp between 300-850

def make_underwriting_decision(application_data: Dict[str, Any], risk_score: float) -> Dict[str, Any]:
    """
    Make underwriting decision - replace with your Agent Bricks decision logic
    """
    # TODO: Replace with your Agent Bricks decision logic
    
    credit_score = application_data.get('credit_score', 650)
    income = application_data.get('annual_income', 0)
    loan_amount = application_data.get('loan_amount', 0)
    debt_to_income = application_data.get('debt_to_income_ratio', 25)
    
    # Your decision criteria here
    if credit_score >= 650 and income >= loan_amount * 0.2 and debt_to_income <= 40:
        return {
            "status": "approved",
            "amount": loan_amount,
            "rate": max(3.5, 8.0 - (credit_score - 600) / 50),
            "reason": f"Approved: Good credit score ({credit_score}), sufficient income, manageable debt ratio ({debt_to_income}%)"
        }
    else:
        reasons = []
        if credit_score < 650:
            reasons.append(f"Credit score too low ({credit_score} < 650)")
        if income < loan_amount * 0.2:
            reasons.append("Insufficient income relative to loan amount")
        if debt_to_income > 40:
            reasons.append(f"High debt-to-income ratio ({debt_to_income}%)")
        
        return {
            "status": "rejected",
            "amount": 0,
            "rate": 0,
            "reason": f"Rejected: {'; '.join(reasons)}"
        }

# Additional helper functions for your Agent Bricks integration
def validate_application_data(application_data: Dict[str, Any]) -> bool:
    """Validate input data format"""
    required_fields = [
        'applicant_name', 'age', 'annual_income', 'employment_type',
        'credit_score', 'loan_amount', 'loan_purpose', 'loan_term'
    ]
    
    for field in required_fields:
        if field not in application_data:
            return False
    
    return True

def format_agent_bricks_response(raw_response: Any) -> Dict[str, Any]:
    """
    Convert your Agent Bricks response format to the expected format
    Customize this based on your Agent Bricks output format
    """
    # TODO: Customize this based on your Agent Bricks response format
    
    # Example conversions:
    if hasattr(raw_response, 'decision'):
        decision = "approved" if raw_response.decision else "rejected"
    elif isinstance(raw_response, dict):
        decision = raw_response.get('decision', 'rejected')
    else:
        decision = str(raw_response).lower()
    
    return {
        "decision": decision,
        "approved_amount": getattr(raw_response, 'amount', 0),
        "interest_rate": getattr(raw_response, 'rate', 0),
        "risk_score": getattr(raw_response, 'risk_score', 0),
        "reasoning": getattr(raw_response, 'reason', ''),
        "processing_time": getattr(raw_response, 'processing_time', 2.0)
    }
