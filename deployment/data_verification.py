#!/usr/bin/env python
"""
SQL Agent Production Data Verification

This script verifies data integrity and consistency in the production environment
after deployment, ensuring that all data is correctly migrated and accessible.
"""

import os
import sys
import json
import time
import logging
import argparse
import datetime
import sqlite3
from pathlib import Path

# Add parent directory to path to allow imports from the main project
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'data_verification.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('data_verification')

class DataVerifier:
    """Verifies data integrity and consistency in the production environment."""
    
    def __init__(self, config_path, reference_data_path=None):
        """
        Initialize the data verifier.
        
        Args:
            config_path (str): Path to the configuration file
            reference_data_path (str, optional): Path to reference data for comparison
        """
        self.config_path = config_path
        self.config = None
        self.reference_data_path = reference_data_path
        self.verification_results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'passed': True,
            'tests': []
        }
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load the configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    def _connect_to_database(self):
        """
        Connect to the database specified in the configuration.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        try:
            # In a real system, this would use the actual database connection
            # For now, we'll use a SQLite database for demonstration
            db_path = self.config.get('database', {}).get('path', 'sql_agent.db')
            
            # Check if database exists
            if not os.path.exists(db_path):
                logger.error(f"Database file not found: {db_path}")
                return None
            
            conn = sqlite3.connect(db_path)
            logger.info(f"Connected to database: {db_path}")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None
    
    def _add_test_result(self, test_name, passed, details=None):
        """
        Add a test result to the verification results.
        
        Args:
            test_name (str): Name of the test
            passed (bool): Whether the test passed
            details (dict, optional): Additional details about the test
        """
        result = {
            'test_name': test_name,
            'passed': passed,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if details:
            result['details'] = details
        
        self.verification_results['tests'].append(result)
        
        if not passed:
            self.verification_results['passed'] = False
        
        logger.info(f"Test result: {test_name} - {'PASSED' if passed else 'FAILED'}")
        if details:
            logger.info(f"Test details: {details}")
    
    def verify_database_structure(self):
        """
        Verify the database structure.
        
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        logger.info("Verifying database structure...")
        
        conn = self._connect_to_database()
        if not conn:
            self._add_test_result('database_connection', False, {'error': 'Failed to connect to database'})
            return False
        
        try:
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Expected tables
            expected_tables = [
                'queries',
                'results',
                'users',
                'logs',
                'metadata'
            ]
            
            # Check if all expected tables exist
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                self._add_test_result('database_tables', False, {'missing_tables': missing_tables})
                return False
            
            # Check table structure for each table
            for table in expected_tables:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]
                
                # This is a simplified check - in a real system, you would check column types, constraints, etc.
                if not columns:
                    self._add_test_result(f'table_structure_{table}', False, {'error': f'No columns found in table {table}'})
                    return False
                
                logger.info(f"Table {table} has columns: {columns}")
            
            self._add_test_result('database_structure', True, {'tables': tables})
            return True
        except Exception as e:
            logger.error(f"Failed to verify database structure: {e}")
            self._add_test_result('database_structure', False, {'error': str(e)})
            return False
        finally:
            conn.close()
    
    def verify_data_integrity(self):
        """
        Verify data integrity.
        
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        logger.info("Verifying data integrity...")
        
        conn = self._connect_to_database()
        if not conn:
            self._add_test_result('data_integrity', False, {'error': 'Failed to connect to database'})
            return False
        
        try:
            cursor = conn.cursor()
            
            # Check for orphaned records
            # This is a simplified example - in a real system, you would check foreign key constraints
            cursor.execute("SELECT COUNT(*) FROM results WHERE query_id NOT IN (SELECT id FROM queries);")
            orphaned_results = cursor.fetchone()[0]
            
            if orphaned_results > 0:
                self._add_test_result('orphaned_records', False, {'orphaned_results': orphaned_results})
                return False
            
            # Check for duplicate records
            cursor.execute("SELECT id, COUNT(*) FROM queries GROUP BY id HAVING COUNT(*) > 1;")
            duplicate_queries = cursor.fetchall()
            
            if duplicate_queries:
                self._add_test_result('duplicate_records', False, {'duplicate_queries': len(duplicate_queries)})
                return False
            
            self._add_test_result('data_integrity', True)
            return True
        except Exception as e:
            logger.error(f"Failed to verify data integrity: {e}")
            self._add_test_result('data_integrity', False, {'error': str(e)})
            return False
        finally:
            conn.close()
    
    def verify_data_consistency(self):
        """
        Verify data consistency with reference data.
        
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        logger.info("Verifying data consistency...")
        
        # Skip if no reference data is provided
        if not self.reference_data_path:
            logger.info("No reference data provided, skipping data consistency check")
            self._add_test_result('data_consistency', True, {'note': 'No reference data provided'})
            return True
        
        try:
            # Load reference data
            with open(self.reference_data_path, 'r') as f:
                reference_data = json.load(f)
            
            # Connect to database
            conn = self._connect_to_database()
            if not conn:
                self._add_test_result('data_consistency', False, {'error': 'Failed to connect to database'})
                return False
            
            cursor = conn.cursor()
            
            # Compare data counts
            for table, count in reference_data.get('counts', {}).items():
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                actual_count = cursor.fetchone()[0]
                
                if actual_count != count:
                    self._add_test_result(
                        f'data_count_{table}',
                        False,
                        {'expected': count, 'actual': actual_count}
                    )
                    return False
            
            # Compare sample data
            for table, samples in reference_data.get('samples', {}).items():
                for sample in samples:
                    # Build query to find the sample record
                    conditions = []
                    values = []
                    
                    for column, value in sample.items():
                        conditions.append(f"{column} = ?")
                        values.append(value)
                    
                    query = f"SELECT COUNT(*) FROM {table} WHERE {' AND '.join(conditions)};"
                    
                    cursor.execute(query, values)
                    count = cursor.fetchone()[0]
                    
                    if count != 1:
                        self._add_test_result(
                            f'data_sample_{table}',
                            False,
                            {'sample': sample, 'found': count}
                        )
                        return False
            
            self._add_test_result('data_consistency', True)
            return True
        except Exception as e:
            logger.error(f"Failed to verify data consistency: {e}")
            self._add_test_result('data_consistency', False, {'error': str(e)})
            return False
        finally:
            if conn:
                conn.close()
    
    def verify_data_access(self):
        """
        Verify data access permissions.
        
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        logger.info("Verifying data access permissions...")
        
        # This is a simplified example - in a real system, you would check actual permissions
        try:
            # Check if the database file is readable
            db_path = self.config.get('database', {}).get('path', 'sql_agent.db')
            
            if not os.path.exists(db_path):
                self._add_test_result('data_access', False, {'error': f'Database file not found: {db_path}'})
                return False
            
            if not os.access(db_path, os.R_OK):
                self._add_test_result('data_access', False, {'error': f'Database file is not readable: {db_path}'})
                return False
            
            if not os.access(db_path, os.W_OK):
                self._add_test_result('data_access', False, {'error': f'Database file is not writable: {db_path}'})
                return False
            
            self._add_test_result('data_access', True)
            return True
        except Exception as e:
            logger.error(f"Failed to verify data access: {e}")
            self._add_test_result('data_access', False, {'error': str(e)})
            return False
    
    def run_verification(self):
        """
        Run all verification checks.
        
        Returns:
            bool: True if all checks pass, False otherwise
        """
        logger.info("Starting data verification...")
        
        # Run all verification checks
        self.verify_database_structure()
        self.verify_data_integrity()
        self.verify_data_consistency()
        self.verify_data_access()
        
        # Generate report
        report_path = f"logs/data_verification_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        
        try:
            with open(report_path, 'w') as f:
                json.dump(self.verification_results, f, indent=2)
            logger.info(f"Verification report written to {report_path}")
        except Exception as e:
            logger.error(f"Failed to write verification report: {e}")
        
        # Return overall result
        return self.verification_results['passed']

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SQL Agent Data Verification Tool')
    parser.add_argument('--config', default='config/production_config.json',
                        help='Path to configuration file')
    parser.add_argument('--reference-data', help='Path to reference data file')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    # Create data verifier
    verifier = DataVerifier(args.config, args.reference_data)
    
    # Run verification
    success = verifier.run_verification()
    
    sys.exit(0 if success else 1)
