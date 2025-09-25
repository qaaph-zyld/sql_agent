#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Column Mention Extraction

This module extracts all column mentions from a SQL query.
It follows the mandatory changelog protocol.
"""

import logging
import json
import re
from typing import Dict, List, Any, Set
from datetime import datetime

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/column_mention_extraction.log'
)
logger = logging.getLogger(__name__)

class ColumnMentionExtractor:
    """
    Extracts column mentions from SQL queries.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the Column Mention Extractor."""
        self.changelog_engine = ChangelogEngine()
        self._update_changelog(
            action_summary="ColumnMentionExtractor initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Extractor ready to process queries for column mentions",
            changes_made=["Initialized internal state"],
            files_affected=[{"file_path": "scripts/optimization/column_mention_extraction.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Will use regex-based parsing for initial implementation"]
        )
        
    def _update_changelog(self, action_summary: str, action_type: str, previous_state: str, current_state: str, changes_made: List[str], files_affected: List[Dict[str, str]], technical_decisions: List[str]) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type=action_type,
            previous_state=previous_state,
            current_state=current_state,
            changes_made=changes_made,
            files_affected=files_affected,
            technical_decisions=technical_decisions
        )

    def extract_columns(self, query_id: str, sql_query: str) -> Set[str]:
        """Extracts all unique column mentions from a SQL query.

        Args:
            query_id (str): An identifier for the query.
            sql_query (str): The SQL query string.

        Returns:
            Set[str]: A set of unique column names mentioned in the query.
                      Column names can be simple (e.g., 'col1') or qualified (e.g., 'table1.col1').
        """
        logger.info(f"Query {query_id}: Starting column extraction.")
        
        sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'ON', 'GROUP', 'BY', 'ORDER', 'AS',
            'AND', 'OR', 'NOT', 'NULL', 'IS', 'IN', 'LIKE', 'BETWEEN', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
            'CREATE', 'TABLE', 'INSERT', 'UPDATE', 'DELETE', 'ALTER', 'DROP', 'INDEX', 'VIEW', 'WITH', 'HAVING',
            'LIMIT', 'OFFSET', 'UNION', 'ALL', 'DISTINCT', 'SET', 'VALUES', 'DEFAULT', 'PRIMARY', 'KEY', 'FOREIGN',
            'REFERENCES', 'CONSTRAINT', 'ASC', 'DESC', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ABS', 'ROUND', 'CAST',
            'DATE', 'YEAR', 'MONTH', 'DAY', 'TIMESTAMP', 'INTERVAL'
        }

        # Regex to find identifiers: words, possibly qualified with dots (e.g., table.column)
        # This will capture table names, column names, aliases, etc.
        # It also captures function names if not careful, so we filter those.
        identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*\b'
        
        potential_mentions = set()
        # Normalize query: remove comments, convert to a consistent case for keyword matching (optional)
        # For simplicity, we are not doing extensive pre-processing here.

        for match in re.finditer(identifier_pattern, sql_query):
            mention = match.group(0)
            
            # Check if it's followed by an opening parenthesis (likely a function call)
            # Ensure there's a character after the match to check
            if match.end() < len(sql_query) and sql_query[match.end():].lstrip().startswith('('):
                continue # Skip function calls like COUNT(column) or my_func(arg)
            
            # Check if it's an alias defined with AS (e.g. COUNT(*) AS total_orders - skip 'total_orders' if it's an alias for an expression)
            # This is tricky with regex alone. A simple check might be if the preceding non-whitespace word is 'AS'.
            # This is a very basic check and can be fooled.
            preceding_text = sql_query[:match.start()].rstrip()
            if preceding_text.upper().endswith(' AS'):
                 # This could be an alias for an expression or a column. 
                 # If it's an alias for a simple column (e.g. col1 AS c1), c1 is a valid mention.
                 # If it's an alias for an expression (e.g. COUNT(*) AS total), total is not a direct column mention.
                 # For now, we'll be conservative and include it, but this needs refinement.
                 pass # Let it be added, can be filtered later if needed based on context.

            if mention.upper() not in sql_keywords:
                potential_mentions.add(mention)
        
        logger.info(f"Query {query_id}: Extracted {len(potential_mentions)} potential column mentions: {potential_mentions}")
        
        self._update_changelog(
            action_summary=f"Extracted {len(potential_mentions)} column mentions from query {query_id}",
            action_type="Data Extraction",
            previous_state="Query received",
            current_state="Column mentions identified",
            changes_made=["Applied regex for column identification", "Filtered out common SQL keywords and function calls"],
            files_affected=[{"file_path": "logs/column_mention_extraction.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=["Using regex for initial column extraction, acknowledging limitations. Further parsing improvements may be needed."]
        )
        return potential_mentions

    def generate_report(self, query_id: str, columns: Set[str], output_file: str = None) -> Dict[str, Any]:
        """Generates a report for the extracted columns of a query."""
        report_data = {
            "query_id": query_id,
            "extracted_columns": sorted(list(columns)),
            "extraction_timestamp": datetime.now().isoformat(),
            "method": "Regex-based extraction (Initial Version)"
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report_data, f, indent=4)
                logger.info(f"Generated column mention report for {query_id} at {output_file}")
            except IOError as e:
                logger.error(f"Failed to write column report to {output_file}: {e}")
        
        self._update_changelog(
            action_summary=f"Generated column mention report for query {query_id}",
            action_type="Report Generation",
            previous_state=f"Columns extracted for {query_id}",
            current_state=f"Report for {query_id} available",
            changes_made=["Serialized extracted columns to JSON"],
            files_affected=[{"file_path": output_file if output_file else "N/A", "change_type": "CREATED" if output_file else "NONE", "impact_level": "LOW"}],
            technical_decisions=["Report includes list of extracted columns and timestamp"]
        )
        return report_data

# Example Usage
if __name__ == "__main__":
    extractor = ColumnMentionExtractor()
    
    test_query_id = "test_q1"
    test_sql = """
    SELECT 
        c.customer_id, 
        c.first_name, 
        c.last_name, 
        COUNT(o.order_id) AS total_orders,
        SUM(oi.quantity * oi.unit_price) AS total_spent
    FROM 
        customers c
    JOIN 
        orders o ON c.customer_id = o.customer_id
    LEFT JOIN 
        order_items oi ON o.order_id = oi.order_id
    WHERE 
        c.registration_date > '2023-01-01' AND c.status = 'ACTIVE'
    GROUP BY 
        c.customer_id, c.first_name, c.last_name
    ORDER BY 
        total_spent DESC, c.last_name ASC;
    """
    
    extracted_cols = extractor.extract_columns(test_query_id, test_sql)
    print(f"\nExtracted columns for query '{test_query_id}':")
    for col in sorted(list(extracted_cols)):
        print(f"  - {col}")
    extractor.generate_report(test_query_id, extracted_cols, f"logs/column_mentions_{test_query_id}.json")

    test_query_id_2 = "test_q2_simple"
    test_sql_2 = "SELECT name, age FROM users WHERE city = 'New York'"
    extracted_cols_2 = extractor.extract_columns(test_query_id_2, test_sql_2)
    print(f"\nExtracted columns for query '{test_query_id_2}':")
    for col in sorted(list(extracted_cols_2)):
        print(f"  - {col}")
    extractor.generate_report(test_query_id_2, extracted_cols_2, f"logs/column_mentions_{test_query_id_2}.json")

    test_query_id_3 = "test_q3_functions_and_keywords"
    test_sql_3 = "SELECT COUNT(*) as num, MAX(salary) FROM employees WHERE department_id IN (10, 20)"
    extracted_cols_3 = extractor.extract_columns(test_query_id_3, test_sql_3)
    print(f"\nExtracted columns for query '{test_query_id_3}':")
    for col in sorted(list(extracted_cols_3)):
        print(f"  - {col}")
    extractor.generate_report(test_query_id_3, extracted_cols_3, f"logs/column_mentions_{test_query_id_3}.json")

