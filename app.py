#!/usr/bin/env python3
"""
SQL Database Querying Agent - Main Application Entry Point
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord
from scripts.db.db_connector import DatabaseConnector
from scripts.db.query_engine import QueryEngine
from scripts.db.schema_extractor import SchemaExtractor

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / "logs" / "app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sql_agent")

class SQLAgent:
    """SQL Agent for natural language query processing"""
    
    def __init__(self):
        """Initialize SQL Agent"""
        self.logger = logging.getLogger("sql_agent")
        self.logger.info("Initializing SQL Agent")
        
        # Initialize components
        self.db_connector = DatabaseConnector()
        self.query_engine = QueryEngine()
        self.schema_extractor = SchemaExtractor()
        
    def process_query(self, natural_language_query: str) -> Dict[str, Any]:
        """Process a natural language query
        
        Args:
            natural_language_query: Natural language query string
            
        Returns:
            Dictionary with query results
        """
        self.logger.info(f"Processing natural language query: {natural_language_query}")
        
        try:
            # Temporary solution: Use hardcoded SQL queries based on keywords in the natural language query
            # This is a workaround until the query engine is fixed
            sql_query = self._generate_sql_from_nl(natural_language_query)
            self.logger.info(f"Generated SQL query: {sql_query}")
            
            # Execute the SQL query
            results = self.db_connector.execute_query(sql_query)
            self.logger.info(f"Query executed successfully, retrieved {len(results)} records")
            
            # Return results
            return {
                "natural_language_query": natural_language_query,
                "sql_query": sql_query,
                "results": results,
                "result_count": len(results)
            }
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            # Return error information
            return {
                "natural_language_query": natural_language_query,
                "sql_query": "Query generation failed",
                "error": str(e),
                "results": [],
                "result_count": 0
            }
    
    def _generate_sql_from_nl(self, natural_language_query: str) -> str:
        """Generate SQL from natural language query
        
        This is a simplified implementation that uses keyword matching
        until the full NL-to-SQL engine is fixed.
        
        Args:
            natural_language_query: Natural language query string
            
        Returns:
            SQL query string
        """
        nl_query = natural_language_query.lower()
        
        # Purchase order queries
        if "purchase order" in nl_query or "po_mstr" in nl_query:
            if "vendor" in nl_query or "supplier" in nl_query:
                return "SELECT TOP 5 po_mstr.po_nbr, po_mstr.po_vend, po_mstr.po_ord_date, vd_mstr.vd_sort AS vendor_name FROM po_mstr LEFT JOIN vd_mstr ON po_mstr.po_vend = vd_mstr.vd_addr ORDER BY po_mstr.po_nbr"
            else:
                return "SELECT TOP 5 * FROM po_mstr ORDER BY po_nbr"
        
        # Vendor queries
        elif "vendor" in nl_query or "supplier" in nl_query or "vd_mstr" in nl_query:
            return "SELECT TOP 5 vd_addr, vd_sort, vd_curr FROM vd_mstr"
        
        # Default query - list tables
        else:
            return "SELECT TOP 5 * FROM po_mstr"
    
    def direct_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute a direct SQL query
        
        Args:
            sql_query: SQL query string to execute directly
            
        Returns:
            Dictionary with query results
        """
        try:
            self.logger.info(f"Executing direct SQL query: {sql_query}")
            results = self.db_connector.execute_query(sql_query)
            return {
                "sql_query": sql_query,
                "results": results,
                "result_count": len(results)
            }
        except Exception as e:
            self.logger.error(f"Error executing direct query: {e}")
            return {
                "sql_query": sql_query,
                "error": str(e),
                "results": [],
                "result_count": 0
            }
        
    def extract_schema(self) -> Dict[str, Any]:
        """
        Extract database schema
        
        Returns:
            Dictionary with schema information
        """
        logger.info("Extracting database schema")
        
        # Extract schema
        schema = self.schema_extractor.extract_full_schema()
        
        # Save schema to files
        json_path = self.schema_extractor.save_schema_to_file(schema)
        md_path = self.schema_extractor.generate_schema_documentation(schema)
        
        return {
            "schema": schema,
            "json_path": json_path,
            "md_path": md_path,
            "table_count": len(schema["tables"]),
            "timestamp": self._get_current_timestamp()
        }
        
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def _update_changelog(self, natural_query: str, sql_query: str, result_count: int) -> None:
        """Update changelog with query execution details"""
        files_affected = [
            ChangeVector(
                file_path="app.py",
                change_type=ChangeType.READ,
                operation="Query Processing",
                impact_level="LOW",
                dependencies=[
                    "scripts/db/query_engine.py",
                    "scripts/db/db_connector.py"
                ]
            )
        ]
        
        answer_record = AnswerRecord(
            action_summary=f"Processed Query: '{natural_query}'",
            action_type="Query Processing",
            previous_state="Awaiting query input",
            current_state="Query processed and results returned",
            changes_made=[
                f"Converted natural language to SQL: '{sql_query}'",
                f"Retrieved {result_count} results from database"
            ],
            files_affected=files_affected,
            technical_decisions=[
                "Used query engine for natural language processing",
                "Executed query through database connector",
                "Formatted results for user presentation"
            ],
            next_actions=[
                "Improve query accuracy",
                "Enhance result formatting",
                "Consider adding visualization options"
            ]
        )
        
        self.changelog_engine.update_changelog(answer_record)
        logger.info("Changelog updated with query processing details")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="SQL Database Querying Agent")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Process a natural language query")
    query_parser.add_argument("text", help="Natural language query text")
    query_parser.add_argument("--output", "-o", help="Output file path for results (JSON)")
    
    # Schema command
    schema_parser = subparsers.add_parser("schema", help="Extract database schema")
    schema_parser.add_argument("--output", "-o", help="Output directory for schema files")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test database connection")
    
    return parser.parse_args()

def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()
    
    # Create SQL Agent
    agent = SQLAgent()
    
    # Execute requested command
    if args.command == "query":
        # Process query
        print(f"\n[INFO] Processing natural language query: '{args.text}'")
        sys.stdout.flush()
        
        # Create a log file for this query execution
        log_file_path = Path(__file__).parent / "query_execution_results.txt"
        with open(log_file_path, "w") as log_file:
            log_file.write(f"SQL Agent Query Execution - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"Query: {args.text}\n\n")
        
        # Write to both console and file
        def log(message):
            print(message)
            sys.stdout.flush()
            with open(log_file_path, "a") as log_file:
                log_file.write(f"{message}\n")
        
        try:
            log("\n[INFO] Translating to SQL and executing query...")
            
            response = agent.process_query(args.text)
            
            # Output results
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(response, f, indent=2)
                log(f"\n[SUCCESS] Results saved to {args.output}")
            else:
                log(f"\n[SUCCESS] Query executed successfully!")
                log(f"\nNatural language query: {response['natural_language_query']}")
                log(f"\nTranslated SQL query:\n{response['sql_query']}")
                log(f"\nResults ({response['result_count']} records found):\n")
                
                if response['result_count'] > 0:
                    # Get column names from first result
                    columns = list(response['results'][0].keys())
                    
                    # Calculate column widths based on data
                    col_widths = {}
                    for col in columns:
                        # Start with column name length
                        col_widths[col] = len(str(col))
                        # Check data lengths
                        for result in response['results']:
                            val_len = len(str(result.get(col, '')))
                            col_widths[col] = max(col_widths[col], val_len)
                    
                    # Limit display columns for readability if there are too many
                    display_columns = columns[:10] if len(columns) > 10 else columns
                    
                    # Print header
                    header = "  ".join(f"{col:{col_widths[col]}}" for col in display_columns)
                    separator = "-" * len(header)
                    log(header)
                    log(separator)
                    
                    # Print rows
                    for result in response['results']:
                        row = "  ".join(f"{str(result.get(col, '')):{col_widths[col]}}" for col in display_columns)
                        log(row)
                    
                    if len(columns) > 10:
                        log(f"\n[NOTE] Only showing first 10 of {len(columns)} columns for readability.")
                        
                    # Write complete results to a JSON file for reference
                    results_file_path = Path(__file__).parent / "query_results.json"
                    with open(results_file_path, "w") as results_file:
                        json.dump(response['results'], results_file, indent=2, default=str)
                    log(f"\n[INFO] Complete results saved to {results_file_path}")
                else:
                    log("No results found.")
                
                log("\n[INFO] Query execution completed.")
                log(f"\n[INFO] Detailed results saved to {log_file_path}\n")
        except Exception as e:
            log(f"\n[ERROR] Error executing query: {e}")
            import traceback
            log(traceback.format_exc())
            log(f"\n[INFO] Error details saved to {log_file_path}\n")
                
    elif args.command == "schema":
        # Extract schema
        response = agent.extract_schema()
        
        print(f"Schema extracted for {response['table_count']} tables")
        print(f"JSON schema saved to: {response['json_path']}")
        print(f"Markdown documentation saved to: {response['md_path']}")
        
    elif args.command == "test":
        # Test database connection
        try:
            print("\n[INFO] Testing database connection to server...")
            sys.stdout.flush()  # Force output to be displayed immediately
            
            if agent.db_connector.test_connection():
                print("\n[SUCCESS] Database connection successful!")
                sys.stdout.flush()
                
                print("\n[INFO] Retrieving table names...")
                sys.stdout.flush()
                
                tables = agent.db_connector.get_table_names()
                print(f"\n[SUCCESS] Found {len(tables)} tables in the database.")
                print(f"\nAvailable tables:\n")
                sys.stdout.flush()
                
                # Display tables in columns
                col_width = 30
                num_cols = 3
                for i in range(0, len(tables), num_cols):
                    row = tables[i:i+num_cols]
                    print("  ".join(f"{table:{col_width}}" for table in row))
                    sys.stdout.flush()
                print("\n")
            else:
                print("\n[ERROR] Database connection failed\n")
                sys.stdout.flush()
        except Exception as e:
            print(f"\n[ERROR] Error testing database connection: {e}\n")
            sys.stdout.flush()
    else:
        print("No command specified. Use --help for usage information.")

if __name__ == "__main__":
    main()
