"""
Test script for the Schema Analyzer component.

This script demonstrates the enhanced schema analyzer with:
1. Table structure extraction
2. Relationship analysis
3. Query pattern analysis
4. Performance recommendation extraction
5. Changelog integration

Usage:
    python test_schema_analyzer.py
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import schema analyzer
from scripts.analysis.schema_analyzer import SchemaAnalyzer

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('schema_analyzer_test.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to test schema analyzer"""
    # Pre-Response: Changelog update execution
    logger.info("Starting schema analyzer test")
    start_time = time.time()
    
    # Get database directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    database_dir = project_dir / "Database_tables" / "QADEE2798"
    
    if not database_dir.exists():
        logger.error(f"Database directory not found: {database_dir}")
        return
        
    logger.info(f"Using database directory: {database_dir}")
    
    # Initialize schema analyzer
    analyzer = SchemaAnalyzer(str(database_dir))
    
    # Analyze schema
    logger.info("Analyzing schema...")
    schema_info = analyzer.analyze_schema()
    
    # Save results to file
    output_file = project_dir / "schema_analysis_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema_info, f, indent=2)
        
    logger.info(f"Schema analysis results saved to {output_file}")
    
    # Print summary
    print("\n" + "="*50)
    print(f"Schema Analysis Summary for {schema_info['database_name']}")
    print("="*50)
    print(f"Tables found: {schema_info['table_count']}")
    print(f"Relationships identified: {len(schema_info['relationships'])}")
    print(f"Query patterns analyzed:")
    print(f"  - Common joins: {len(schema_info['query_patterns']['common_joins'])}")
    print(f"  - Common filters: {len(schema_info['query_patterns']['common_filters'])}")
    print(f"  - Common aggregations: {len(schema_info['query_patterns']['common_aggregations'])}")
    print(f"Performance recommendations: {len(schema_info['performance_recommendations'])}")
    print(f"Execution time: {schema_info['execution_time_ms']:.2f} ms")
    print(f"Detailed results saved to: {output_file}")
    print("="*50)
    
    # Calculate total execution time
    execution_time = time.time() - start_time
    logger.info(f"Schema analyzer test completed in {execution_time:.2f} seconds")
    
    # Return success
    return True

if __name__ == "__main__":
    main()
