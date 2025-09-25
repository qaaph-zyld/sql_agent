#!/usr/bin/env python3
"""
Database Connector - Utilities for database connection and interaction
"""

import os
import json
from pathlib import Path
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from sql_agent.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord
from sql_agent.core import exceptions as core_exceptions

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent.parent / "logs" / "db_connector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db_connector")

class DatabaseConnector:
    """Database connection and interaction utilities"""
    
    def __init__(self):
        """Initialize database connector"""
        load_dotenv()
        self.changelog_engine = ChangelogEngine()
        self.config = self._load_database_config()
        self.connection_string = self._get_connection_string()
        self.engine = self._create_engine()
        
    def _load_database_config(self) -> Dict[str, Any]:
        """Load database configuration from file"""
        config_path = Path(__file__).parent.parent.parent / "config" / "database.json"
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    logger.info("Database configuration loaded successfully")
                    return config
            else:
                # Try loading from mock if real config doesn't exist
                mock_config_path = Path(__file__).parent.parent.parent / "config" / "database_mock.json"
                if mock_config_path.exists():
                    with open(mock_config_path, 'r') as f:
                        config = json.load(f)
                        logger.info("Mock database configuration loaded")
                        return config
                else:
                    err_msg = f"Database configuration file not found at {config_path} or {mock_config_path}"
                    logger.error(err_msg)
                    raise core_exceptions.ConfigurationError(err_msg)
        except json.JSONDecodeError as e:
            err_msg = f"Error parsing database configuration file: {e}"
            logger.error(err_msg)
            raise core_exceptions.ConfigurationError(err_msg)
    
    def _get_connection_string(self) -> str:
        """Create connection string from configuration"""
        try:
            conn = self.config.get('connection', {})
            driver = conn.get('driver', 'mssql+pymssql')
            server = conn.get('server')
            database = conn.get('database')
            username = conn.get('username')
            password = conn.get('password')
            port = conn.get('port', 1433)
            
            if not all([server, database, username, password]):
                # Fall back to environment variables if config is incomplete
                logger.warning("Incomplete database configuration, falling back to environment variables")
                db_host = os.getenv('DB_HOST')
                db_name = os.getenv('DB_NAME')
                db_user = os.getenv('DB_USER')
                db_password = os.getenv('DB_PASSWORD')
                
                if not all([db_host, db_name, db_user, db_password]):
                    err_msg = "Missing database connection details in both config file and environment variables"
                    logger.error(err_msg)
                    raise core_exceptions.ConfigurationError(err_msg)
                    
                return f"mssql+pymssql://{db_user}:{db_password}@{db_host}/{db_name}"
            
            # Use configuration from file
            connection_string = f"{driver}://{username}:{password}@{server}:{port}/{database}"
            logger.info(f"Connection string created for server: {server}, database: {database}")
            return connection_string
            
        except Exception as e:
            err_msg = f"Error creating connection string: {e}"
            logger.error(err_msg)
            raise core_exceptions.ConfigurationError(err_msg)
        
    def _create_engine(self) -> sa.engine.Engine:
        """Create SQLAlchemy engine"""
        try:
            engine = create_engine(self.connection_string)
            logger.info("Database engine created successfully")
            return engine
        except sa.exc.SQLAlchemyError as e:
            err_msg = f"Error creating database engine due to SQLAlchemy issue: {e}"
            logger.error(err_msg)
            raise core_exceptions.ConfigurationError(err_msg)
        except Exception as e: # Catch any other unexpected error
            err_msg = f"An unexpected error occurred while creating database engine: {e}"
            logger.error(err_msg)
            raise core_exceptions.ConfigurationError(err_msg)
            
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except sa.exc.SQLAlchemyError as e:
            logger.error(f"Database connection test failed due to SQLAlchemy error: {e}")
            return False
        except Exception as e: # Catch any other unexpected error during test
            logger.error(f"Database connection test failed due to unexpected error: {e}")
            return False
            
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dictionaries"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                rows = result.fetchall()
                
                # Convert to list of dictionaries
                columns = result.keys()
                results = [dict(zip(columns, row)) for row in rows]
                
                logger.info(f"Query executed successfully, returned {len(results)} rows")
                return results
        except sa.exc.SQLAlchemyError as e:
            err_msg = f"Database query execution failed due to SQLAlchemy error: {e}"
            logger.error(err_msg)
            raise core_exceptions.DatabaseConnectionError(err_msg)
        except Exception as e: # Catch any other unexpected error during execution
            err_msg = f"An unexpected error occurred during query execution: {e}"
            logger.error(err_msg)
            raise core_exceptions.DatabaseConnectionError(err_msg)
            
    def get_table_names(self) -> List[str]:
        """Get list of all tables in the database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"))
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"Retrieved {len(tables)} table names")
                return tables
        except sa.exc.SQLAlchemyError as e:
            err_msg = f"Error getting table names due to SQLAlchemy error: {e}"
            logger.error(err_msg)
            raise core_exceptions.DatabaseConnectionError(err_msg)
        except Exception as e: # Catch any other unexpected error
            err_msg = f"An unexpected error occurred while getting table names: {e}"
            logger.error(err_msg)
            raise core_exceptions.DatabaseConnectionError(err_msg)
            
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a specific table"""
        try:
            query = """
            SELECT 
                COLUMN_NAME, 
                DATA_TYPE, 
                CHARACTER_MAXIMUM_LENGTH, 
                IS_NULLABLE, 
                COLUMN_DEFAULT
            FROM 
                INFORMATION_SCHEMA.COLUMNS 
            WHERE 
                TABLE_NAME = :table_name
            ORDER BY 
                ORDINAL_POSITION
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"table_name": table_name})
                columns = [dict(zip(result.keys(), row)) for row in result.fetchall()]
                logger.info(f"Retrieved schema for table {table_name}, {len(columns)} columns")
                return columns
        except sa.exc.SQLAlchemyError as e:
            err_msg = f"Error getting schema for table {table_name} due to SQLAlchemy error: {e}"
            logger.error(err_msg)
            raise core_exceptions.DatabaseConnectionError(err_msg)
        except Exception as e: # Catch any other unexpected error
            err_msg = f"An unexpected error occurred while getting schema for table {table_name}: {e}"
            logger.error(err_msg)
            raise core_exceptions.DatabaseConnectionError(err_msg)
            
    def update_changelog(self, action_summary: str, changes_made: List[str], files_affected: List[ChangeVector]) -> None:
        """Update changelog with database operations"""
        answer_record = AnswerRecord(
            action_summary=action_summary,
            action_type="Database Operation",
            previous_state="Previous database state",
            current_state="Updated database state",
            changes_made=changes_made,
            files_affected=files_affected,
            technical_decisions=[
                "Used SQLAlchemy for database interaction",
                "Implemented proper error handling",
                "Logged all database operations"
            ],
            next_actions=[
                "Verify data integrity",
                "Update documentation if schema changed",
                "Consider performance optimization if needed"
            ]
        )
        
        self.changelog_engine.update_changelog(answer_record)
        logger.info("Changelog updated with database operation")

if __name__ == "__main__":
    # Simple test of the database connector
    connector = DatabaseConnector()
    if connector.test_connection():
        print("Database connection successful")
        print(f"Available tables: {connector.get_table_names()}")
    else:
        print("Database connection failed")
