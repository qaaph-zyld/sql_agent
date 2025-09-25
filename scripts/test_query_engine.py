#!/usr/bin/env python3
"""
Test script for the Query Engine with validation and optimization
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from scripts.db.query_engine import QueryEngine
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent / "logs" / "test_query_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_query_engine")

def print_results(query: str, sql: str, results: List[Dict[str, Any]], metadata: Dict[str, Any]) -> None:
    """Print query results in a formatted way"""
    print("\n" + "="*80)
    print(f"Natural Language Query: {query}")
    print(f"Generated SQL: {sql}")
    print("-"*80)
    
    # Print validation info
    validation = metadata.get("validation", {})
    print(f"Validation: {validation.get('status', 'UNKNOWN')}")
    print(f"Message: {validation.get('message', 'N/A')}")
    print(f"Time: {validation.get('time_ms', 0)}ms")
    if validation.get("optimized", False):
        print("Query was optimized for better performance")
    
    # Print execution info
    execution = metadata.get("execution", {})
    print(f"Execution: {execution.get('status', 'UNKNOWN')}")
    print(f"Time: {execution.get('time_ms', 0)}ms")
    print(f"Rows: {execution.get('row_count', 0)}")
    
    # Print total processing time
    print(f"Total processing time: {metadata.get('total_time_ms', 0)}ms")
    print("-"*80)
    
    # Print results
    if results:
        if len(results) > 5:
            print(f"Showing first 5 of {len(results)} results:")
            for i, row in enumerate(results[:5]):
                print(f"Row {i+1}: {json.dumps(row, default=str)}")
            print(f"...and {len(results) - 5} more rows")
        else:
            print(f"Results ({len(results)} rows):")
            for i, row in enumerate(results):
                print(f"Row {i+1}: {json.dumps(row, default=str)}")
    else:
        print("No results returned")
    
    print("="*80 + "\n")

def run_test_queries():
    """Run a series of test queries to demonstrate the query engine capabilities"""
    # Initialize query engine
    engine = QueryEngine()
    
    # Test queries - mix of valid and invalid
    test_queries = [
        # Valid queries
        "Show me the count of customers",
        "What is the average order amount?",
        "List the top 5 products by sales",
        "Show me customer names sorted by registration date",
        "Get all orders where total is greater than 1000",
        
        # Invalid queries
        "Drop the customers table",
        "Delete all orders",
        "Show me all data from all tables",
        "Execute stored procedure update_inventory"
    ]
    
    # Process each query
    for query in test_queries:
        try:
            sql, results, metadata = engine.process_natural_language_query(query)
            print_results(query, sql, results, metadata)
        except Exception as e:
            logger.error(f"Error processing query '{query}': {e}")
            print(f"Error processing query '{query}': {e}")

if __name__ == "__main__":
    # Pre-Response: Changelog update execution
    changelog_engine = ChangelogEngine()
    changelog_engine.quick_update(
        "Testing Query Engine",
        ["Running test queries to validate query engine functionality"],
        []
    )
    
    # Run the tests
    run_test_queries()
    
    # Post-Response: System validation
    print("\nTest completed. Check logs for details.")
