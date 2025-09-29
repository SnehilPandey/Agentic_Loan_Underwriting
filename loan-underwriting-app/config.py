"""
Configuration file for the Loan Underwriting Application
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabricksConfig:
    """Configuration for Databricks connection"""
    host: Optional[str] = None
    http_path: Optional[str] = None
    token: Optional[str] = None
    catalog: str = "main"
    schema: str = "loan_underwriting"
    
    def __post_init__(self):
        # Load from environment variables if not provided
        self.host = self.host or os.getenv("DATABRICKS_SERVER_HOSTNAME")
        self.http_path = self.http_path or os.getenv("DATABRICKS_HTTP_PATH")
        self.token = self.token or os.getenv("DATABRICKS_TOKEN")

@dataclass
class AgentBricksConfig:
    """Configuration for Agent Bricks endpoint"""
    endpoint_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 30
    
    def __post_init__(self):
        self.endpoint_url = self.endpoint_url or os.getenv("AGENT_BRICKS_ENDPOINT")
        self.api_key = self.api_key or os.getenv("AGENT_BRICKS_API_KEY")

@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool = False
    log_level: str = "INFO"
    max_loan_amount: int = 1000000
    min_credit_score: int = 300
    max_credit_score: int = 850
    
    databricks: DatabricksConfig = None
    agent_bricks: AgentBricksConfig = None
    
    def __post_init__(self):
        if self.databricks is None:
            self.databricks = DatabricksConfig()
        if self.agent_bricks is None:
            self.agent_bricks = AgentBricksConfig()
        
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

# Global config instance
config = AppConfig()
