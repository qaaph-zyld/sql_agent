"""
Data Quality Reports - Core Module

This module provides the core functionality for generating data quality reports.
It includes the base classes and utilities used by all report modules.
"""

import os
import sys
import pandas as pd
import pyodbc
import logging
from datetime import datetime, timedelta
import configparser
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_quality.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database connection parameters
DEFAULT_CONFIG = {
    "DB_HOST": "a265m001",
    "DB_NAME": "QADEE2798",
    "DB_USER": "PowerBI",
    "DB_PASSWORD": "P0werB1"
}

class ConfigManager:
    """Manages configuration settings for database connections"""
    
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        # Load existing config or create default
        if os.path.exists(config_file):
            self.config.read(config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config["DATABASE"] = DEFAULT_CONFIG
        with open(self.config_file, "w") as f:
            self.config.write(f)
        logger.info(f"Created default configuration file: {self.config_file}")
    
    def get_connection_string(self):
        """Get database connection string from config"""
        db_config = self.config["DATABASE"]
        return f"DRIVER={{SQL Server}};SERVER={db_config['DB_HOST']};DATABASE={db_config['DB_NAME']};UID={db_config['DB_USER']};PWD={db_config['DB_PASSWORD']}"
    
    def get_config_value(self, section, key):
        """Get a specific configuration value"""
        return self.config[section][key]
    
    def set_config_value(self, section, key, value):
        """Set a specific configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        with open(self.config_file, "w") as f:
            self.config.write(f)

class DataQualityReport:
    """Base class for data quality reports"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.report_date = datetime.now().strftime("%Y-%m-%d")
        self.output_dir = "reports"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def get_connection(self):
        """Create database connection"""
        conn_str = self.config_manager.get_connection_string()
        return pyodbc.connect(conn_str)
    
    def read_query_file(self, query_file):
        """Read SQL query from file"""
        try:
            with open(query_file, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            with open(query_file, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading query file {query_file}: {str(e)}")
            raise
    
    def execute_query(self, query):
        """Execute a SQL query and return results as DataFrame"""
        try:
            conn = self.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def generate_report(self):
        """Generate report - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement generate_report()")
    
    def export_to_excel(self, df, filename):
        """Export DataFrame to Excel"""
        output_path = os.path.join(self.output_dir, filename)
        df.to_excel(output_path, index=False)
        logger.info(f"Exported report to {output_path}")
        return output_path
    
    def export_to_csv(self, df, filename):
        """Export DataFrame to CSV"""
        output_path = os.path.join(self.output_dir, filename)
        df.to_csv(output_path, index=False)
        logger.info(f"Exported report to {output_path}")
        return output_path
    
    def save_metadata(self, metadata, filename):
        """Save metadata to JSON file"""
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        logger.info(f"Saved metadata to {output_path}")
        return output_path
    
    def load_metadata(self, filename):
        """Load metadata from JSON file"""
        input_path = os.path.join(self.output_dir, filename)
        if os.path.exists(input_path):
            with open(input_path, 'r') as f:
                return json.load(f)
        return None
    
    def get_historical_data(self, report_type, days=30):
        """Get historical data for trend analysis"""
        historical_data = []
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Iterate through dates
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            metadata_file = f"{report_type}_metadata_{date_str}.json"
            
            metadata = self.load_metadata(metadata_file)
            if metadata:
                metadata['date'] = date_str
                historical_data.append(metadata)
            
            current_date += timedelta(days=1)
        
        return historical_data
