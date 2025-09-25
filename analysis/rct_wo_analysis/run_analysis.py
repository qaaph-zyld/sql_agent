#!/usr/bin/env python3
"""
Script to test database connection and run RCT-WO analysis
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('analysis.log')
    ]
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test database connection with provided credentials"""
    try:
        logger.info("Testing database connection...")
        
        # Connection parameters
        server = 'a265m001'
        database = 'QADEE2798'
        username = 'PowerBI'
        password = 'P0werB1'
        
        # Create connection string
        connection_string = f'mssql+pymssql://{username}:{password}@{server}/{database}'
        
        # Test connection
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            result = conn.execute("SELECT @@VERSION")
            version = result.scalar()
            logger.info(f"Successfully connected to SQL Server: {version}")
            
            # Check if tables exist
            tables = pd.read_sql(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME IN ('tr_hist', 'pt_mstr')",
                conn
            )
            logger.info(f"Found tables: {tables['TABLE_NAME'].tolist()}")
            
            # Check row counts
            row_counts = {}
            for table in ['tr_hist', 'pt_mstr']:
                count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {table}", conn)['cnt'].iloc[0]
                row_counts[table] = count
            logger.info(f"Row counts: {row_counts}")
            
            return True
            
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False

def run_analysis():
    """Run the RCT-WO analysis"""
    try:
        logger.info("Starting RCT-WO analysis...")
        
        # Set up environment
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from generate_report import main as run_report
        
        # Run the report
        result = run_report()
        if result == 0:
            logger.info("Analysis completed successfully!")
            return True
        else:
            logger.error("Analysis failed with errors")
            return False
            
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        return False

if __name__ == "__main__":
    print("=== RCT-WO Analysis Runner ===\n")
    
    # Test connection first
    if not test_connection():
        print("\n❌ Database connection failed. Please check your credentials and try again.")
        sys.exit(1)
    
    print("\n✅ Database connection successful!")
    
    # Run the analysis
    print("\nStarting analysis...")
    if run_analysis():
        print("\n✅ Analysis completed successfully!")
        print("Check the 'output' directory for results.")
    else:
        print("\n❌ Analysis failed. Check the logs for details.")
        sys.exit(1)
