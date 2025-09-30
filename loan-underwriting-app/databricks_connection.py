"""
Databricks Connection and Data Processing Module
"""

import os
import pandas as pd
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabricksManager:
    """Manages Databricks connections and data operations for the loan underwriting system"""
    
    def __init__(self):
        """Initialize Databricks connection configuration"""
        self.config = None
        self.workspace_client = None
        self.sql_connection = None
        
        # Configuration from environment variables
        self.server_hostname = os.getenv("DATABRICKS_SERVER_HOSTNAME")
        self.http_path = os.getenv("DATABRICKS_HTTP_PATH") 
        self.token = os.getenv("DATABRICKS_TOKEN")
        self.catalog = os.getenv("DATABRICKS_CATALOG", "main")
        self.schema = os.getenv("DATABRICKS_SCHEMA", "loan_underwriting")
        
        # Try to detect if running in Databricks environment
        self.is_databricks_environment = self._detect_databricks_environment()
        
        # Initialize credentials
        if self.is_databricks_environment:
            # Running in Databricks - try native authentication first
            try:
                self.config = Config()  # Uses default authentication
                logger.info("✅ Using native Databricks authentication")
                self.credentials_available = True
                
                # If we don't have explicit SQL warehouse path, try to detect or use default
                if not self.http_path:
                    self.http_path = self._detect_sql_warehouse_path()
                    
            except Exception as e:
                logger.warning(f"Native Databricks auth failed: {e}, trying explicit credentials...")
                self.credentials_available = self._try_explicit_credentials()
        else:
            # Not in Databricks environment - require explicit credentials
            self.credentials_available = self._try_explicit_credentials()
    
    def _detect_databricks_environment(self) -> bool:
        """Detect if running in Databricks environment"""
        # Check for Databricks-specific environment variables
        databricks_indicators = [
            "DATABRICKS_RUNTIME_VERSION",
            "DB_CLUSTER_ID", 
            "SPARK_HOME",
            "DATABRICKS_TOKEN",  # Even explicit tokens indicate Databricks env
        ]
        
        for indicator in databricks_indicators:
            if os.getenv(indicator):
                logger.info(f"🔍 Databricks environment detected via {indicator}")
                return True
                
        # Check if we can access Databricks APIs without explicit credentials
        try:
            test_config = Config()
            if test_config.host:  # If Config can detect host, we're in Databricks
                logger.info("🔍 Databricks environment detected via Config auto-detection")
                return True
        except Exception:
            pass
            
        return False
    
    def _detect_sql_warehouse_path(self) -> str:
        """Try to detect an available SQL warehouse"""
        try:
            if self.config:
                client = WorkspaceClient(config=self.config)
                warehouses = list(client.warehouses.list())
                for warehouse in warehouses:
                    if hasattr(warehouse, 'state') and warehouse.state and hasattr(warehouse.state, 'name') and warehouse.state.name == "RUNNING":
                        path = f"/sql/1.0/warehouses/{warehouse.id}"
                        logger.info(f"🔍 Auto-detected SQL warehouse: {path}")
                        return path
                # If no running warehouse, use the first available
                if warehouses:
                    path = f"/sql/1.0/warehouses/{warehouses[0].id}"
                    logger.info(f"🔍 Using first available SQL warehouse: {path}")
                    return path
        except Exception as e:
            logger.warning(f"Could not auto-detect SQL warehouse: {e}")
        
        # Fallback to environment variable or None
        return self.http_path
    
    def _try_explicit_credentials(self) -> bool:
        """Try to use explicit credentials from environment variables"""
        if not all([self.server_hostname, self.http_path, self.token]):
            logger.warning("Missing explicit Databricks credentials. App will run in demo mode.")
            return False
        
        try:
            self.config = Config(
                host=self.server_hostname,
                token=self.token
            )
            logger.info("✅ Databricks configuration initialized with explicit credentials")
            return True
        except Exception as e:
            logger.warning(f"Explicit credentials failed: {e}. Running in demo mode.")
            return False
    
    def get_workspace_client(self) -> WorkspaceClient:
        """Get authenticated Databricks workspace client"""
        if not self.credentials_available:
            raise ValueError("Databricks credentials not configured")
            
        if not self.workspace_client:
            try:
                self.workspace_client = WorkspaceClient(
                    host=self.server_hostname,
                    token=self.token
                )
                logger.info("Databricks workspace client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize workspace client: {e}")
                raise
        return self.workspace_client
    
    def get_sql_connection(self, force_reconnect=False):
        """Get SQL connection for data operations"""
        if not self.credentials_available:
            raise ValueError("Databricks credentials not configured")
            
        if not self.sql_connection or force_reconnect:
            try:
                # Close existing connection if it exists
                if self.sql_connection:
                    try:
                        self.sql_connection.close()
                    except Exception:
                        pass  # Ignore errors when closing
                
                # Try different connection methods for Databricks Apps
                if self.is_databricks_environment:
                    logger.info(f"🔍 DEBUG: Attempting SQL connection in Databricks environment")
                    logger.info(f"🔍 DEBUG: server_hostname={self.server_hostname}")
                    logger.info(f"🔍 DEBUG: http_path={self.http_path}")
                    logger.info(f"🔍 DEBUG: token_available={'Yes' if self.token else 'No'}")
                    
                    # Method 1: Try native connection with auto-detected warehouse
                    try:
                        if not self.http_path:
                            logger.info("🔍 DEBUG: No http_path, attempting auto-detection...")
                            self.http_path = self._detect_sql_warehouse_path()
                            logger.info(f"🔍 DEBUG: Auto-detected http_path={self.http_path}")
                        
                        if self.http_path:
                            logger.info(f"🔍 DEBUG: Trying sql.connect(http_path='{self.http_path}')")
                            self.sql_connection = sql.connect(http_path=self.http_path)
                            logger.info("✅ Databricks SQL connection established using native auth + detected warehouse")
                            return self.sql_connection
                    except Exception as e:
                        logger.warning(f"Native connection with detected warehouse failed: {e}")
                    
                    # Method 2: Try pure native connection
                    try:
                        logger.info("🔍 DEBUG: Trying sql.connect() with no parameters")
                        self.sql_connection = sql.connect()
                        logger.info("✅ Databricks SQL connection established using pure native authentication")
                        return self.sql_connection
                    except Exception as e:
                        logger.warning(f"Pure native SQL connection failed: {e}")
                
                # Method 3: Fallback to explicit credentials
                connection_params = {}
                
                # Use DATABRICKS_HOST if available (common in Databricks Apps)
                host = self.server_hostname or os.getenv("DATABRICKS_HOST")
                if host:
                    # Ensure proper format
                    if not host.startswith('https://'):
                        host = f"https://{host}"
                    connection_params['server_hostname'] = host
                
                if self.http_path:
                    connection_params['http_path'] = self.http_path
                elif self.is_databricks_environment:
                    # Try to auto-detect warehouse again
                    detected_path = self._detect_sql_warehouse_path()
                    if detected_path:
                        connection_params['http_path'] = detected_path
                
                if self.token:
                    connection_params['access_token'] = self.token
                    
                if connection_params:
                    self.sql_connection = sql.connect(**connection_params)
                    logger.info(f"✅ Databricks SQL connection established using explicit credentials: {list(connection_params.keys())}")
                else:
                    raise Exception("No valid connection parameters available")
                
            except Exception as e:
                logger.error(f"Failed to establish SQL connection: {e}")
                raise
        return self.sql_connection
    
    def execute_query(self, query: str, params: Optional[Dict] = None, retry_count: int = 1) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        if not self.credentials_available:
            raise ValueError("Databricks credentials not configured")
        
        for attempt in range(retry_count + 1):
            try:
                connection = self.get_sql_connection(force_reconnect=(attempt > 0))
                with connection.cursor() as cursor:
                    cursor.execute(query, params or {})
                    
                    # Fetch column names
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    
                    # Fetch all results
                    results = cursor.fetchall()
                    
                    # Convert to DataFrame
                    if results and columns:
                        return pd.DataFrame(results, columns=columns)
                    else:
                        return pd.DataFrame()
                        
            except Exception as e:
                error_msg = str(e)
                if "INVALID_STATE" in error_msg or "SessionHandle" in error_msg:
                    if attempt < retry_count:
                        logger.warning(f"Session expired, retrying... (attempt {attempt + 1})")
                        continue
                    else:
                        logger.error(f"Query execution failed after {retry_count + 1} attempts: {e}")
                else:
                    logger.error(f"Query execution failed: {e}")
                raise
    
    def create_schema_if_not_exists(self):
        """Create the loan underwriting schema and tables if they don't exist"""
        try:
            # Create catalog and schema
            create_catalog_query = f"CREATE CATALOG IF NOT EXISTS {self.catalog}"
            create_schema_query = f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{self.schema}"
            
            self.execute_query(create_catalog_query)
            self.execute_query(create_schema_query)
            
            # Create loan applications table
            create_applications_table = f"""
            CREATE TABLE IF NOT EXISTS {self.catalog}.{self.schema}.loan_applications (
                application_id STRING,
                applicant_name STRING,
                age INT,
                annual_income DECIMAL(12,2),
                employment_type STRING,
                credit_score INT,
                loan_amount DECIMAL(12,2),
                loan_purpose STRING,
                loan_term INT,
                down_payment DECIMAL(12,2),
                debt_to_income_ratio DECIMAL(5,2),
                decision STRING,
                decision_reason STRING,
                approved_amount DECIMAL(12,2),
                interest_rate DECIMAL(5,2),
                risk_score DECIMAL(5,2),
                application_timestamp TIMESTAMP,
                processing_time_seconds DECIMAL(8,2)
            ) USING DELTA
            """
            
            # Create loan analytics table
            create_analytics_table = f"""
            CREATE TABLE IF NOT EXISTS {self.catalog}.{self.schema}.loan_analytics (
                date DATE,
                total_applications INT,
                approved_applications INT,
                rejected_applications INT,
                approval_rate DECIMAL(5,2),
                avg_loan_amount DECIMAL(12,2),
                avg_credit_score DECIMAL(5,1),
                avg_processing_time DECIMAL(8,2),
                created_timestamp TIMESTAMP
            ) USING DELTA
            """
            
            self.execute_query(create_applications_table)
            self.execute_query(create_analytics_table)
            
            logger.info("Database schema and tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            raise
    
    def save_loan_application(self, application_data: Dict, decision_result: Dict) -> str:
        """Save loan application and decision to Delta table"""
        try:
            # Generate unique application ID
            application_id = str(uuid.uuid4())
            
            # Prepare data for insertion
            insert_query = f"""
            INSERT INTO {self.catalog}.{self.schema}.loan_applications VALUES (
                %(application_id)s,
                %(applicant_name)s,
                %(age)s,
                %(annual_income)s,
                %(employment_type)s,
                %(credit_score)s,
                %(loan_amount)s,
                %(loan_purpose)s,
                %(loan_term)s,
                %(down_payment)s,
                %(debt_to_income_ratio)s,
                %(decision)s,
                %(decision_reason)s,
                %(approved_amount)s,
                %(interest_rate)s,
                %(risk_score)s,
                %(application_timestamp)s,
                %(processing_time_seconds)s
            )
            """
            
            params = {
                'application_id': application_id,
                'applicant_name': application_data.get('applicant_name'),
                'age': application_data.get('age'),
                'annual_income': application_data.get('annual_income'),
                'employment_type': application_data.get('employment_type'),
                'credit_score': application_data.get('credit_score'),
                'loan_amount': application_data.get('loan_amount'),
                'loan_purpose': application_data.get('loan_purpose'),
                'loan_term': application_data.get('loan_term'),
                'down_payment': application_data.get('down_payment'),
                'debt_to_income_ratio': application_data.get('debt_to_income_ratio'),
                'decision': decision_result.get('decision'),
                'decision_reason': decision_result.get('reasoning', ''),
                'approved_amount': decision_result.get('approved_amount'),
                'interest_rate': decision_result.get('interest_rate'),
                'risk_score': decision_result.get('risk_score'),
                'application_timestamp': datetime.now(timezone.utc),
                'processing_time_seconds': decision_result.get('processing_time', 0)
            }
            
            self.execute_query(insert_query, params)
            logger.info(f"Loan application {application_id} saved successfully")
            
            return application_id
            
        except Exception as e:
            logger.error(f"Failed to save loan application: {e}")
            raise
    
    def get_application_status(self, application_id: str) -> Optional[Dict]:
        """Retrieve application status by ID"""
        try:
            query = f"""
            SELECT * FROM {self.catalog}.{self.schema}.loan_applications 
            WHERE application_id = %(application_id)s
            """
            
            df = self.execute_query(query, {'application_id': application_id})
            
            if not df.empty:
                return df.iloc[0].to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get application status: {e}")
            raise
    
    def get_analytics_data(self) -> Dict:
        """Get analytics data for dashboard"""
        try:
            # Today's applications
            today_query = f"""
            SELECT COUNT(*) as count FROM {self.catalog}.{self.schema}.loan_applications
            WHERE DATE(application_timestamp) = CURRENT_DATE()
            """
            
            # Approval rate (last 30 days)
            approval_rate_query = f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN decision = 'approved' THEN 1 ELSE 0 END) as approved
            FROM {self.catalog}.{self.schema}.loan_applications
            WHERE application_timestamp >= CURRENT_DATE() - INTERVAL 30 DAYS
            """
            
            # Average processing time
            processing_time_query = f"""
            SELECT AVG(processing_time_seconds) as avg_time
            FROM {self.catalog}.{self.schema}.loan_applications
            WHERE application_timestamp >= CURRENT_DATE() - INTERVAL 7 DAYS
            """
            
            # Average credit score
            credit_score_query = f"""
            SELECT AVG(credit_score) as avg_score
            FROM {self.catalog}.{self.schema}.loan_applications
            WHERE application_timestamp >= CURRENT_DATE() - INTERVAL 30 DAYS
            """
            
            today_count = self.execute_query(today_query)
            approval_data = self.execute_query(approval_rate_query)
            processing_time = self.execute_query(processing_time_query)
            credit_score = self.execute_query(credit_score_query)
            
            # Calculate metrics
            today_applications = today_count.iloc[0]['count'] if not today_count.empty else 0
            
            approval_rate = 0
            if not approval_data.empty and approval_data.iloc[0]['total'] > 0:
                approval_rate = (approval_data.iloc[0]['approved'] / approval_data.iloc[0]['total']) * 100
            
            avg_processing_time = processing_time.iloc[0]['avg_time'] if not processing_time.empty and processing_time.iloc[0]['avg_time'] else 0
            avg_credit_score = credit_score.iloc[0]['avg_score'] if not credit_score.empty and credit_score.iloc[0]['avg_score'] else 0
            
            return {
                'today_applications': int(today_applications),
                'approval_rate': round(approval_rate, 1),
                'avg_processing_time': round(float(avg_processing_time), 1),
                'avg_credit_score': round(float(avg_credit_score))
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics data: {e}")
            # Return default values if query fails
            return {
                'today_applications': 0,
                'approval_rate': 0.0,
                'avg_processing_time': 0.0,
                'avg_credit_score': 0
            }
    
    def get_application_trends(self, days: int = 30) -> pd.DataFrame:
        """Get application trends for charting"""
        try:
            query = f"""
            SELECT 
                DATE(application_timestamp) as date,
                COUNT(*) as total_applications,
                SUM(CASE WHEN decision = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN decision = 'rejected' THEN 1 ELSE 0 END) as rejected,
                AVG(loan_amount) as avg_loan_amount,
                AVG(credit_score) as avg_credit_score
            FROM {self.catalog}.{self.schema}.loan_applications
            WHERE application_timestamp >= CURRENT_DATE() - INTERVAL {days} DAYS
            GROUP BY DATE(application_timestamp)
            ORDER BY date
            """
            
            return self.execute_query(query)
            
        except Exception as e:
            logger.error(f"Failed to get application trends: {e}")
            return pd.DataFrame()
    
    def close_connections(self):
        """Close all database connections"""
        try:
            if self.sql_connection:
                self.sql_connection.close()
                logger.info("SQL connection closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

# Global instance - lazy initialization
_databricks_manager = None

def get_databricks_manager():
    """Get the global databricks manager instance (lazy initialization)"""
    global _databricks_manager
    if _databricks_manager is None:
        _databricks_manager = DatabricksManager()
    return _databricks_manager
