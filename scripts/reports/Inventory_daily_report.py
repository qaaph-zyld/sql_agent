#!/usr/bin/env python3
"""
Inventory Daily Report Generator
-------------------------------
Automatically generates inventory reports based on specified SQL queries.
Runs daily at 9:00 AM via scheduler to provide inventory status reports.

This module handles:
1. SQL query execution from file
2. Data processing and transformation
3. Excel report generation
4. Email notification
5. Comprehensive error handling and logging
"""

import os
import sys
import logging
import datetime
import configparser
import traceback
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

import pandas as pd
import pyodbc  # For SQL Server connection

# Configure logging with rotation
class CustomLogFormatter(logging.Formatter):
    """Custom log formatter with color support for console output"""
    
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[91m\033[1m',  # Bold Red
        'RESET': '\033[0m'    # Reset
    }
    
    def format(self, record):
        log_message = super().format(record)
        if sys.stdout.isatty():  # Only apply colors when output is a terminal
            level_name = record.levelname
            if level_name in self.COLORS:
                return f"{self.COLORS[level_name]}{log_message}{self.COLORS['RESET']}"
        return log_message

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
log_file = logs_dir / f"inventory_report_{datetime.datetime.now().strftime('%Y%m%d')}.log"
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler(sys.stdout)
console_formatter = CustomLogFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger('inventory_report')

class ConfigManager:
    """Handles configuration loading from config file with validation."""
    
    def __init__(self, config_path="config/config.ini"):
        """
        Initialize configuration manager.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config = configparser.ConfigParser()
        self.config_path = config_path
        self._load_config()
        
    def _load_config(self):
        """Load and validate configuration from file."""
        if not os.path.exists(self.config_path):
            logger.error(f"Configuration file not found: {self.config_path}")
            self._create_default_config()
            logger.info(f"Default configuration created at: {self.config_path}")
            sys.exit(1)
        
        try:
            self.config.read(self.config_path)
            logger.info("Configuration loaded successfully")
            self._validate_config()
        except configparser.Error as e:
            logger.error(f"Error parsing configuration file: {str(e)}")
            sys.exit(1)
    
    def _validate_config(self):
        """Validate required configuration sections and options."""
        required_sections = ['DATABASE', 'REPORTS', 'EMAIL']
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required configuration section: {section}")
                sys.exit(1)
        
        # Validate database configuration
        db_required = ['server', 'database']
        for option in db_required:
            if option not in self.config['DATABASE']:
                logger.error(f"Missing required database configuration option: {option}")
                sys.exit(1)
        
        # Validate report configuration
        if 'output_dir' not in self.config['REPORTS']:
            logger.error("Missing required report output directory configuration")
            sys.exit(1)
    
    def _create_default_config(self):
        """Create a default configuration file."""
        self.config['DATABASE'] = {
            'server': 'your_server_name',
            'database': 'your_database_name',
            'username': 'your_username',
            'password': 'your_password',
            'driver': '{ODBC Driver 17 for SQL Server}',
            'trusted_connection': 'no',
            'encrypt': 'no',
            'timeout': '30'
        }
        
        self.config['EMAIL'] = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': '587',
            'sender': 'reports@example.com',
            'recipients': 'user1@example.com,user2@example.com',
            'subject': 'Daily Inventory Report - {date}',
            'body': 'Please find attached the daily inventory report.',
            'use_ssl': 'false',
            'use_tls': 'true',
            'username': '',
            'password': ''
        }
        
        self.config['REPORTS'] = {
            'output_dir': './reports',
            'filename_template': 'inventory_report_{date}.xlsx',
            'include_timestamp': 'true',
            'sheet_name': 'Inventory Report',
            'excel_engine': 'xlsxwriter'
        }
        
        self.config['SCHEDULING'] = {
            'schedule_time': '09:00',
            'run_weekends': 'false',
            'retry_on_failure': 'true',
            'retry_count': '3',
            'retry_delay': '300'
        }
        
        with open(self.config_path, 'w') as f:
            self.config.write(f)
    
    def get_db_config(self):
        """Return database configuration dictionary."""
        return dict(self.config['DATABASE'])
    
    def get_email_config(self):
        """Return email configuration dictionary."""
        return dict(self.config['EMAIL'])
    
    def get_report_config(self):
        """Return report configuration dictionary."""
        return dict(self.config['REPORTS'])
    
    def get_scheduling_config(self):
        """Return scheduling configuration dictionary."""
        if 'SCHEDULING' in self.config:
            return dict(self.config['SCHEDULING'])
        return {
            'schedule_time': '09:00',
            'run_weekends': 'false',
            'retry_on_failure': 'true',
            'retry_count': '3',
            'retry_delay': '300'
        }


class DatabaseConnector:
    """Handles database connections and query execution with error handling."""
    
    def __init__(self, config):
        """
        Initialize database connector.
        
        Args:
            config (dict): Database configuration dictionary
        """
        self.config = config
        self.conn = None
    
    def connect(self):
        """
        Establish database connection with retry logic.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                # Build connection string based on authentication type
                if self.config.get('trusted_connection', 'no').lower() == 'yes':
                    connection_string = (
                        f"DRIVER={self.config['driver']};"
                        f"SERVER={self.config['server']};"
                        f"DATABASE={self.config['database']};"
                        f"Trusted_Connection=yes;"
                    )
                    
                    if 'encrypt' in self.config:
                        connection_string += f"Encrypt={self.config['encrypt']};"
                else:
                    connection_string = (
                        f"DRIVER={self.config['driver']};"
                        f"SERVER={self.config['server']};"
                        f"DATABASE={self.config['database']};"
                        f"UID={self.config['username']};"
                        f"PWD={self.config['password']};"
                    )
                    
                    if 'encrypt' in self.config:
                        connection_string += f"Encrypt={self.config['encrypt']};"
                
                # Add timeout if specified
                if 'timeout' in self.config:
                    connection_string += f"Connection Timeout={self.config['timeout']};"
                
                self.conn = pyodbc.connect(connection_string)
                logger.info("Database connection established successfully")
                return True
            
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                logger.warning(f"Database connection attempt {retry_count} failed: {error_msg}")
                
                if retry_count >= max_retries:
                    logger.error(f"Database connection failed after {max_retries} attempts: {error_msg}")
                    return False
                
                # Wait before retrying (exponential backoff)
                import time
                time.sleep(2 ** retry_count)
    
    def execute_query(self, query, params=None):
        """
        Execute SQL query and return results as DataFrame.
        
        Args:
            query (str): SQL query to execute
            params (dict, optional): Parameters for the query
            
        Returns:
            pandas.DataFrame: Query results or None if execution failed
        """
        if not self.conn:
            if not self.connect():
                return None
        
        try:
            start_time = datetime.datetime.now()
            logger.info(f"Executing SQL query at {start_time.strftime('%H:%M:%S')}...")
            
            # Handle parameterized queries if params provided
            if params:
                # Replace parameters in query
                for param_name, param_value in params.items():
                    placeholder = f"{{{param_name}}}"
                    query = query.replace(placeholder, str(param_value))
            
            # Execute query and fetch results
            df = pd.read_sql(query, self.conn)
            
            end_time = datetime.datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info(f"Query executed successfully in {execution_time:.2f} seconds. Retrieved {len(df)} rows.")
            return df
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            logger.debug(f"Query that failed: {query[:1000]}...")  # Log first 1000 chars of query
            logger.debug(traceback.format_exc())
            return None
    
    def close(self):
        """Close database connection."""
        if self.conn:
            try:
                self.conn.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database connection: {str(e)}")


class DataProcessor:
    """Processes and transforms data from query results."""
    
    @staticmethod
    def process_data(df):
        """
        Process and transform data from query results.
        
        Args:
            df (pandas.DataFrame): Input DataFrame
            
        Returns:
            pandas.DataFrame: Processed DataFrame
        """
        if df is None or df.empty:
            logger.warning("No data to process")
            return df
        
        try:
            # Make a copy to avoid modifying the original DataFrame
            processed_df = df.copy()
            
            # Handle missing values
            processed_df = processed_df.fillna('')
            
            # Convert date columns to proper format if they exist
            date_columns = [col for col in processed_df.columns if 'date' in col.lower()]
            for col in date_columns:
                if col in processed_df.columns:
                    try:
                        processed_df[col] = pd.to_datetime(processed_df[col], errors='coerce')
                        processed_df[col] = processed_df[col].dt.strftime('%Y-%m-%d')
                    except Exception as e:
                        logger.warning(f"Failed to convert {col} to date format: {str(e)}")
            
            # Format numeric columns
            numeric_columns = ['Total Qty Nettable', 'Total Qty Nonet', 'Total Inv', 'Last_ISSUE', 'Last_REC', 'Last_CC']
            for col in numeric_columns:
                if col in processed_df.columns:
                    try:
                        processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
                        processed_df[col] = processed_df[col].fillna(0).astype(int)
                    except Exception as e:
                        logger.warning(f"Failed to convert {col} to numeric format: {str(e)}")
            
            # Format currency columns with 5 decimal places and no $ sign
            currency_columns = ['Standard Cost', 'Material Cost', 'LBO', 'COGS', 'CMAT', 'Total CMAT', 'Total COGS', 
                               'WH_Value', 'WIP_Value', 'EXLPICK_Value']
            for col in currency_columns:
                if col in processed_df.columns:
                    try:
                        processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
                        processed_df[col] = processed_df[col].fillna(0)
                        # Format with 5 decimal places, no $ sign
                        processed_df[col] = processed_df[col].round(5)
                    except Exception as e:
                        logger.warning(f"Failed to format {col} as currency: {str(e)}")
            
            logger.info(f"Data processing completed: {len(processed_df)} rows processed")
            return processed_df
            
        except Exception as e:
            logger.error(f"Data processing failed: {str(e)}")
            logger.debug(traceback.format_exc())
            return df  # Return original DataFrame if processing fails

    @staticmethod
    def apply_filters(df):
        """
        Apply various filters to create multiple filtered DataFrames.
        
        Args:
            df (pandas.DataFrame): Input DataFrame
            
        Returns:
            dict: Dictionary of filtered DataFrames with sheet names as keys
        """
        if df is None or df.empty:
            logger.warning("No data to filter")
            return {"Main Report": df}
        
        try:
            # Create a copy of the original DataFrame to avoid modifying it
            main_df = df.copy()
            
            # List of columns to keep in filtered sheets (except Main Report)
            keep_columns = [
                'Plant', 'Item Number', 'Standard Cost', 'Material Cost', 'LBO', 
                'Item Description', 'pt_desc2', 'Prod Line', 'Group', 'pt_part_type', 
                'Item Number Status', 'Date added', 'ABC', 'pt_cyc_int', 'Safety Stock', 
                'Safety Time', 'Item Planner', 'Item Supplier', 'Routing', 'Net weight', 
                'pt_net_wt_um', 'Item Type', 'Project', 'FG/SFG/RM', 'Operation', 
                'Total Qty Nettable', 'Total Qty Nonet', 'Total Inv', 'Last_ISSUE', 
                'Last_REC', 'Last_CC', 'Obsolete', 'Total CMAT', 'Total COGS', 'New',
                'WH_Qty', 'WIP_Qty', 'EXLPICK_Qty', 'WH_Value', 'WIP_Value', 'EXLPICK_Value',
                'WIP_minimum', 'WIP_maximum', 'WIP_overstock', 'WIP_overstock_Value',
                'avg_ISS-WO_CW_-1', 'avg_ISS-WO_CW_-2', 'avg_ISS-WO_CW_-3', 'avg_ISS-WO_CW_-4'
            ]
            
            # Add the 'New' column for recently added items
            today = datetime.datetime.now().date()
            main_df['New'] = ''
            
            # Handle 'Date added' column for the 'New' calculation
            if 'Date added' in main_df.columns:
                try:
                    # Try to convert the column to datetime
                    # First, make a copy to avoid modifying the original
                    date_added_col = main_df['Date added'].copy()
                    
                    # Try to convert to datetime
                    date_added_col = pd.to_datetime(date_added_col, errors='coerce')
                    
                    # Find items added less than 30 days ago
                    for idx, date_val in enumerate(date_added_col):
                        if pd.notna(date_val):
                            days_since = (today - date_val.date()).days
                            if days_since < 30:
                                main_df.loc[idx, 'New'] = f"Added {days_since} days ago"
                except Exception as e:
                    logger.warning(f"Failed to process 'Date added' column: {str(e)}")
            
            # Create filtered DataFrames with proper error handling
            filtered_dfs = {"Main Report": main_df}
            
            # Filter 1: Non-Active Items
            try:
                if 'Obsolete' in main_df.columns:
                    filtered_df = main_df[main_df['Obsolete'] != 'Active'].copy()
                    # Keep only specified columns for filtered sheets
                    filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                    # Drop duplicates for filtered sheets
                    filtered_df = filtered_df.drop_duplicates()
                    filtered_dfs["Non-Active Items"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create 'Non-Active Items' filter: {str(e)}")
            
            # Filter 2: Cycle Count Due
            try:
                if 'pt_cyc_int' in main_df.columns and 'Last_CC' in main_df.columns:
                    filtered_df = main_df[
                        pd.to_numeric(main_df['pt_cyc_int'], errors='coerce') - 
                        pd.to_numeric(main_df['Last_CC'], errors='coerce') < 5
                    ].copy()
                    # Keep only specified columns for filtered sheets
                    filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                    # Drop duplicates for filtered sheets
                    filtered_df = filtered_df.drop_duplicates()
                    filtered_dfs["Cycle Count Due"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create 'Cycle Count Due' filter: {str(e)}")
            
            # Filter 3: Issue 80-90 Days
            try:
                if 'Last_ISSUE' in main_df.columns:
                    filtered_df = main_df[
                        (pd.to_numeric(main_df['Last_ISSUE'], errors='coerce') > 80) & 
                        (pd.to_numeric(main_df['Last_ISSUE'], errors='coerce') < 90)
                    ].copy()
                    # Keep only specified columns for filtered sheets
                    filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                    # Drop duplicates for filtered sheets
                    filtered_df = filtered_df.drop_duplicates()
                    filtered_dfs["Issue 80-90 Days"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create 'Issue 80-90 Days' filter: {str(e)}")
            
            # Filter 4: FG-SFG Operation Check
            try:
                if 'FG/SFG/RM' in main_df.columns and 'Operation' in main_df.columns:
                    filtered_df = main_df[
                        ((main_df['FG/SFG/RM'] == 'FG') | (main_df['FG/SFG/RM'] == 'SFG')) & 
                        ((main_df['Operation'] != '30') & (main_df['Operation'] != '999'))
                    ].copy()
                    # Keep only specified columns for filtered sheets
                    filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                    # Drop duplicates for filtered sheets
                    filtered_df = filtered_df.drop_duplicates()
                    filtered_dfs["FG-SFG Operation Check"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create 'FG-SFG Operation Check' filter: {str(e)}")
            
            # Filter 5: Empty Project
            try:
                if 'Project' in main_df.columns and 'FG/SFG/RM' in main_df.columns:
                    filtered_df = main_df[
                        (main_df['Project'] == '') & (main_df['FG/SFG/RM'] != 'No BOM')
                    ].copy()
                    # Keep only specified columns for filtered sheets
                    filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                    # Drop duplicates for filtered sheets
                    filtered_df = filtered_df.drop_duplicates()
                    filtered_dfs["Empty Project"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create 'Empty Project' filter: {str(e)}")
            
            # Filter 6: Type Mismatch
            try:
                if 'Item Type' in main_df.columns and 'FG/SFG/RM' in main_df.columns:
                    filtered_df = main_df[
                        main_df['Item Type'] != main_df['FG/SFG/RM']
                    ].copy()
                    # Keep only specified columns for filtered sheets
                    filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                    # Drop duplicates for filtered sheets
                    filtered_df = filtered_df.drop_duplicates()
                    filtered_dfs["Type Mismatch"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create 'Type Mismatch' filter: {str(e)}")
            
            # Filter 7: Recently Added
            try:
                filtered_df = main_df[main_df['New'] != ''].copy()
                # Keep only specified columns for filtered sheets
                filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                # Drop duplicates for filtered sheets
                filtered_df = filtered_df.drop_duplicates()
                filtered_dfs["Recently Added"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create 'Recently Added' filter: {str(e)}")
            
            # Filter 8: 0000-F000
            try:
                if 'Prod Line' in main_df.columns and 'Group' in main_df.columns:
                    filtered_df = main_df[
                        (main_df['Prod Line'] == '0000') | (main_df['Group'] == 'F000')
                    ].copy()
                    # Keep only specified columns for filtered sheets
                    filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                    # Drop duplicates for filtered sheets
                    filtered_df = filtered_df.drop_duplicates()
                    filtered_dfs["0000-F000"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create '0000-F000' filter: {str(e)}")
            
            # Filter 9: No BOM Items
            try:
                if 'FG/SFG/RM' in main_df.columns:
                    filtered_df = main_df[main_df['FG/SFG/RM'] == 'No BOM'].copy()
                    # Keep only specified columns for filtered sheets
                    filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                    # Drop duplicates for filtered sheets
                    filtered_df = filtered_df.drop_duplicates()
                    filtered_dfs["No BOM Items"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create 'No BOM Items' filter: {str(e)}")
            
            # Filter 10: WIP Overstock
            try:
                if 'WIP_overstock' in main_df.columns:
                    # Convert WIP_overstock to numeric before filtering
                    main_df['WIP_overstock_numeric'] = pd.to_numeric(main_df['WIP_overstock'], errors='coerce')
                    filtered_df = main_df[main_df['WIP_overstock_numeric'].notna()].copy()
                    # Keep only specified columns for filtered sheets
                    filtered_df = filtered_df[[col for col in keep_columns if col in filtered_df.columns]]
                    # Drop duplicates for filtered sheets
                    filtered_df = filtered_df.drop_duplicates()
                    filtered_dfs["WIP Overstock"] = filtered_df
            except Exception as e:
                logger.warning(f"Failed to create 'WIP Overstock' filter: {str(e)}")
                logger.debug(traceback.format_exc())
            
            logger.info(f"Created {len(filtered_dfs)} filtered datasets")
            return filtered_dfs
            
        except Exception as e:
            logger.error(f"Filtering failed: {str(e)}")
            logger.debug(traceback.format_exc())
            return {"Main Report": df}  # Return original DataFrame if filtering fails


class ReportGenerator:
    """Generates Excel reports from query results with formatting."""
    
    def __init__(self, config):
        """
        Initialize report generator.
        
        Args:
            config (dict): Report configuration dictionary
        """
        self.config = config
        self.output_dir = Path(self.config['output_dir'])
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_report(self, df, report_name=None, params=None):
        """
        Generate Excel report from DataFrame with formatting.
        
        Args:
            df (pandas.DataFrame): Data to include in report
            report_name (str, optional): Custom report name
            params (dict, optional): Additional parameters for report
            
        Returns:
            pathlib.Path: Path to generated report or None if generation failed
        """
        if df is None or df.empty:
            logger.warning("No data available for report generation")
            return None
            
        try:
            # Generate filename with date and optional timestamp
            date_str = datetime.datetime.now().strftime('%Y%m%d')
            time_str = datetime.datetime.now().strftime('%H%M%S')
            
            if report_name:
                if self.config.get('include_timestamp', 'true').lower() == 'true':
                    filename = f"{report_name}_{date_str}_{time_str}.xlsx"
                else:
                    filename = f"{report_name}_{date_str}.xlsx"
            else:
                template = self.config['filename_template']
                if '{date}' in template:
                    filename = template.format(date=date_str)
                else:
                    filename = template
                
                if self.config.get('include_timestamp', 'true').lower() == 'true':
                    # Insert timestamp before extension
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{time_str}{ext}"
                
            output_path = self.output_dir / filename
            
            # Get Excel engine from config
            excel_engine = self.config.get('excel_engine', 'xlsxwriter')
            
            # Create a Pandas Excel writer
            writer = pd.ExcelWriter(output_path, engine=excel_engine)
            
            # Get sheet name from config
            sheet_name = self.config.get('sheet_name', 'Inventory Report')
            if report_name:
                sheet_name = report_name
            
            # Convert the DataFrame to an Excel object
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Apply formatting if using xlsxwriter
            if excel_engine == 'xlsxwriter':
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                
                # Define formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
                number_format = workbook.add_format({'num_format': '#,##0.00'})
                
                # Apply header format
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Apply conditional formatting for specific columns
                # Example: Highlight negative values in red
                for i, col in enumerate(df.columns):
                    if col.lower() in ['qty_oh', 'in_qty_oh', 'ld_qty_oh'] or 'quantity' in col.lower():
                        worksheet.conditional_format(1, i, len(df), i, {
                            'type': 'cell',
                            'criteria': '<',
                            'value': 0,
                            'format': workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                        })
                
                # Auto-adjust columns' width
                for i, col in enumerate(df.columns):
                    # Calculate column width based on content
                    max_len = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    ) + 2
                    # Cap width at 50 characters to prevent excessive width
                    worksheet.set_column(i, i, min(max_len, 50))
                
                # Add report metadata
                row = len(df) + 2
                worksheet.write(row, 0, f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Add filter to header row
                worksheet.autofilter(0, 0, 0, len(df.columns) - 1)
                
                # Freeze the header row
                worksheet.freeze_panes(1, 0)
            
            # Close the Pandas Excel writer and output the Excel file
            writer.close()
            
            logger.info(f"Report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def generate_multi_sheet_report(self, dataframes_dict, params=None):
        """
        Generate Excel report with multiple sheets from a dictionary of DataFrames.
        
        Args:
            dataframes_dict (dict): Dictionary of DataFrames with sheet names as keys
            params (dict, optional): Additional parameters for report
            
        Returns:
            pathlib.Path: Path to generated report or None if generation failed
        """
        if not dataframes_dict:
            logger.warning("No data available for report generation")
            return None
            
        try:
            # Generate filename with date and timestamp
            date_str = datetime.datetime.now().strftime('%Y%m%d')
            time_str = datetime.datetime.now().strftime('%H%M%S')
            
            template = self.config['filename_template']
            if '{date}' in template:
                filename = template.format(date=date_str)
            else:
                filename = template
                
            if self.config.get('include_timestamp', 'true').lower() == 'true':
                # Insert timestamp before extension
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{time_str}{ext}"
                
            output_path = self.output_dir / filename
            
            # Get Excel engine from config
            excel_engine = self.config.get('excel_engine', 'xlsxwriter')
            
            # Create a Pandas Excel writer
            writer = pd.ExcelWriter(output_path, engine=excel_engine)
            
            # Define formats if using xlsxwriter
            header_format = None
            if excel_engine == 'xlsxwriter':
                workbook = writer.book
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
            
            # Write each DataFrame to a separate sheet
            for sheet_name, df in dataframes_dict.items():
                if df is None or df.empty:
                    logger.warning(f"No data for sheet: {sheet_name}")
                    continue
                    
                # Write DataFrame to sheet
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Apply formatting if using xlsxwriter
                if excel_engine == 'xlsxwriter':
                    worksheet = writer.sheets[sheet_name]
                    
                    # Apply header format
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    # Apply conditional formatting for specific columns
                    for i, col in enumerate(df.columns):
                        if col.lower() in ['qty_oh', 'in_qty_oh', 'ld_qty_oh'] or 'quantity' in col.lower():
                            worksheet.conditional_format(1, i, len(df), i, {
                                'type': 'cell',
                                'criteria': '<',
                                'value': 0,
                                'format': workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                            })
                    
                    # Auto-adjust columns' width
                    for i, col in enumerate(df.columns):
                        # Calculate column width based on content
                        max_len = max(
                            df[col].astype(str).apply(len).max(),
                            len(col)
                        ) + 2
                        # Cap width at 50 characters to prevent excessive width
                        worksheet.set_column(i, i, min(max_len, 50))
                    
                    # Add filter to header row
                    worksheet.autofilter(0, 0, 0, len(df.columns) - 1)
                    
                    # Freeze the header row
                    worksheet.freeze_panes(1, 0)
            
            # Add report metadata to the first sheet
            if excel_engine == 'xlsxwriter' and dataframes_dict:
                first_sheet_name = next(iter(dataframes_dict))
                worksheet = writer.sheets[first_sheet_name]
                df = dataframes_dict[first_sheet_name]
                row = len(df) + 2
                worksheet.write(row, 0, f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Close the Pandas Excel writer and output the Excel file
            writer.close()
            
            logger.info(f"Multi-sheet report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Multi-sheet report generation failed: {str(e)}")
            logger.debug(traceback.format_exc())
            return None


class EmailSender:
    """Handles email notifications with report attachments and error handling."""
    
    def __init__(self, config):
        """
        Initialize email sender.
        
        Args:
            config (dict): Email configuration dictionary
        """
        self.config = config
    
    def send_report(self, report_path):
        """
        Send email with report attachment.
        
        Args:
            report_path (pathlib.Path): Path to the report file
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not report_path or not os.path.exists(report_path):
            logger.error("Report file not found")
            return False
            
        try:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
            subject = self.config['subject'].format(date=date_str)
            body = self.config['body']
            sender = self.config['sender']
            recipients = self.config['recipients'].split(',')
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject
            msg.attach(MIMEText(body))
            
            # Attach report
            with open(report_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(report_path)}'
            )
            msg.attach(part)
            
            # Determine SSL/TLS settings
            use_ssl = self.config.get('use_ssl', 'false').lower() == 'true'
            use_tls = self.config.get('use_tls', 'true').lower() == 'true'
            
            # Send email
            if use_ssl:
                smtp = smtplib.SMTP_SSL(self.config['smtp_server'], int(self.config['smtp_port']))
            else:
                smtp = smtplib.SMTP(self.config['smtp_server'], int(self.config['smtp_port']))
            
            if use_tls:
                smtp.starttls()
            
            # Authenticate if username and password provided
            if self.config.get('username') and self.config.get('password'):
                smtp.login(self.config['username'], self.config['password'])
            
            smtp.sendmail(sender, recipients, msg.as_string())
            smtp.quit()
            
            logger.info(f"Email sent successfully to: {', '.join(recipients)}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            logger.debug(traceback.format_exc())
            return False


class InventoryReportManager:
    """Main class that orchestrates the entire reporting process with error handling."""
    
    def __init__(self, config_path=None):
        """
        Initialize inventory report manager.
        
        Args:
            config_path (str, optional): Path to configuration file
        """
        self.config_manager = ConfigManager(config_path) if config_path else ConfigManager()
        self.db_config = self.config_manager.get_db_config()
        self.email_config = self.config_manager.get_email_config()
        self.report_config = self.config_manager.get_report_config()
        
        self.db_connector = DatabaseConnector(self.db_config)
        self.data_processor = DataProcessor()
        self.report_generator = ReportGenerator(self.report_config)
        self.email_sender = EmailSender(self.email_config)
    
    def run(self, query_file=None, query_string=None, params=None, send_email=True):
        """
        Run the inventory report process with comprehensive error handling.
        
        Args:
            query_file (str, optional): Path to SQL query file
            query_string (str, optional): SQL query string
            params (dict, optional): Parameters for SQL query
            send_email (bool, optional): Whether to send email notification
            
        Returns:
            bool: True if process completed successfully, False otherwise
        """
        logger.info("Starting inventory report generation process")
        report_path = None
        
        try:
            # Load query from file or use provided query string
            if query_file and os.path.exists(query_file):
                with open(query_file, 'r') as f:
                    query = f.read()
                    logger.info(f"Query loaded from file: {query_file}")
            elif query_string:
                query = query_string
                logger.info("Using provided query string")
            else:
                logger.error("No query provided. Please specify a query file or query string.")
                return False
            
            # Execute query
            df = self.db_connector.execute_query(query, params)
            if df is None:
                logger.error("Query execution failed. Aborting report generation.")
                return False
            
            # Process data
            processed_df = self.data_processor.process_data(df)
            
            # Apply filters to create multiple DataFrames
            filtered_dfs = self.data_processor.apply_filters(processed_df)
            
            # Generate a multi-sheet report
            report_path = self.report_generator.generate_multi_sheet_report(filtered_dfs, params=params)
            if report_path is None:
                logger.error("Report generation failed. Aborting email sending.")
                return False
            
            # Send email if requested
            if send_email:
                email_sent = self.email_sender.send_report(report_path)
                if not email_sent:
                    logger.warning("Email notification failed, but report was generated.")
            
            # Close database connection
            self.db_connector.close()
            
            logger.info("Inventory report process completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Inventory report process failed: {str(e)}")
            logger.debug(traceback.format_exc())
            
            # Close database connection if open
            if hasattr(self, 'db_connector'):
                self.db_connector.close()
                
            return False
    
    def run_item_parameters_report(self, send_email=True):
        """
        Run the item parameters report generation process using the Item_Parameters query.
        
        Args:
            send_email (bool, optional): Whether to send email notification
            
        Returns:
            bool: True if process completed successfully, False otherwise
        """
        try:
            logger.info("Starting item parameters report generation process")
            
            # Use the Item_Parameters query file
            query_file = os.path.join(self.config_manager.config['REPORTS']['query_dir'], 'Item_Parameters.sql')
            
            # Run the report generation process with the Item_Parameters query
            return self.run(query_file=query_file, send_email=send_email)
            
        except Exception as e:
            logger.error(f"Item parameters report generation failed: {str(e)}")
            logger.debug(traceback.format_exc())
            return False


def main():
    """Main function to run the inventory report with command-line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate inventory reports from SQL queries.')
    parser.add_argument('--query-file', '-f', help='Path to SQL query file', default='sql_queries/Inventory.sql')
    parser.add_argument('--query', '-q', help='SQL query string')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--no-email', action='store_true', help='Skip sending email notification')
    parser.add_argument('--params', '-p', help='JSON string of parameters for the query')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Parse parameters if provided
    params = None
    if args.params:
        import json
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse parameters JSON: {str(e)}")
            sys.exit(1)
    
    # Initialize report manager with config if provided
    manager = InventoryReportManager(args.config)
    
    # Run the report generation process
    success = manager.run(
        query_file=args.query_file,
        query_string=args.query,
        params=params,
        send_email=not args.no_email
    )
    
    if success:
        logger.info("Report generation completed successfully")
        sys.exit(0)
    else:
        logger.error("Report generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()