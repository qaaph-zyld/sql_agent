#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WHERE Clause Column Extractor

This module extracts columns specifically mentioned within the WHERE clause of a SQL query.
It follows the mandatory changelog protocol.
"""

import logging
import json
import re
from typing import Dict, List, Any, Set
from datetime import datetime

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine
# Potentially use ColumnMentionExtractor to pre-process or as a utility
# from scripts.optimization.column_mention_extraction import ColumnMentionExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/where_clause_column_extractor.log'
)
logger = logging.getLogger(__name__)

class WhereClauseColumnExtractor:
    """
    Extracts column mentions specifically from the WHERE clause of SQL queries.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the WhereClauseColumnExtractor."""
        self.changelog_engine = ChangelogEngine()
        # self.general_column_extractor = ColumnMentionExtractor() # If needed for pre-filtering
        self._update_changelog(
            action_summary="WhereClauseColumnExtractor initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Extractor ready to process WHERE clauses",
            changes_made=["Initialized internal state"],
            files_affected=[{"file_path": "scripts/optimization/where_clause_column_extractor.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Will use regex-based parsing focused on WHERE clause content"]
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

    def _extract_where_clause_content(self, sql_query: str) -> Optional[str]:
        """Isolates the content of the WHERE clause from a SQL query.
        This is a simplified regex approach and might not handle all complex SQL structures,
        especially those with subqueries having their own WHERE clauses.
        """
        # Regex to find WHERE clause, attempting to stop before GROUP BY, ORDER BY, HAVING, LIMIT, UNION, or end of query.
        # This needs to be robust enough for various query endings.
        # Using re.IGNORECASE for 'WHERE'
        match = re.search(r'\bWHERE\b(.*?)(?:\bGROUP BY\b|\bORDER BY\b|\bHAVING\b|\bLIMIT\b|\bUNION\b|\bWINDOW\b|\bFETCH\b|\bOFFSET\b|\bFOR\b|$)', 
                          sql_query, re.IGNORECASE | re.DOTALL)
        if match:
            # Further refinement: handle cases where a subquery with its own WHERE clause might be captured.
            # This simple regex takes everything until the next major keyword or end of string.
            # A more sophisticated parser would build an AST to correctly isolate the main WHERE clause.
            where_content = match.group(1).strip()
            logger.info(f"Extracted WHERE clause content: {where_content[:200]}...") # Log snippet
            return where_content
        else:
            logger.info("No WHERE clause found in the query.")
            return None

    def extract_columns_from_where_clause(self, query_id: str, sql_query: str) -> Set[str]:
        """Extracts all unique column mentions from the WHERE clause of a SQL query.

        Args:
            query_id (str): An identifier for the query.
            sql_query (str): The SQL query string.

        Returns:
            Set[str]: A set of unique column names mentioned in the WHERE clause.
        """
        logger.info(f"Query {query_id}: Starting WHERE clause column extraction.")
        
        where_content = self._extract_where_clause_content(sql_query)
        if not where_content:
            self._update_changelog(
                action_summary=f"No WHERE clause found for query {query_id}",
                action_type="Data Extraction",
                previous_state="Query received",
                current_state="No WHERE clause columns identified",
                changes_made=["Identified absence of WHERE clause"],
                files_affected=[{"file_path": "logs/where_clause_column_extractor.log", "change_type": "APPENDED", "impact_level": "LOW"}],
                technical_decisions=["Query does not contain a WHERE clause for analysis"]
            )
            return set()

        # Re-use or adapt the identifier pattern from ColumnMentionExtractor
        # This pattern finds words, possibly qualified with dots (e.g., table.column)
        identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*\b'
        sql_keywords_for_where_clause = {
            # Keywords common in WHERE clauses that are not columns
            'AND', 'OR', 'NOT', 'NULL', 'IS', 'IN', 'LIKE', 'BETWEEN', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
            'ANY', 'ALL', 'SOME', 'TRUE', 'FALSE'
            # Common functions often used in WHERE clauses (can be extended)
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ABS', 'ROUND', 'CAST', 'SUBSTRING', 'TRIM', 'LENGTH',
            'DATE', 'YEAR', 'MONTH', 'DAY', 'NOW', 'CURRENT_DATE', 'CURRENT_TIMESTAMP'
        }

        potential_columns = set()
        for match in re.finditer(identifier_pattern, where_content):
            mention = match.group(0)
            
            # Check if it's followed by an opening parenthesis (likely a function call)
            if match.end() < len(where_content) and where_content[match.end():].lstrip().startswith('('):
                # If it's a known function keyword, skip it. Otherwise, it might be a user-defined function using a column.
                # For simplicity, if it looks like a function call, we skip it, but this could be refined.
                # if mention.upper() in sql_keywords_for_where_clause: # Only skip known functions
                continue # Skip all function-like calls for now
            
            # Avoid SQL keywords specific to WHERE clause context
            if mention.upper() not in sql_keywords_for_where_clause:
                # Further checks: avoid numeric literals, string literals (already handled by \b in regex for words)
                if not mention.isdigit(): # Simple check for purely numeric identifiers
                    potential_columns.add(mention)
        
        logger.info(f"Query {query_id}: Extracted {len(potential_columns)} potential columns from WHERE clause: {potential_columns}")
        
        self._update_changelog(
            action_summary=f"Extracted {len(potential_columns)} columns from WHERE clause of query {query_id}",
            action_type="Data Extraction",
            previous_state="WHERE clause content isolated",
            current_state="Columns from WHERE clause identified",
            changes_made=["Applied regex for column identification within WHERE clause", "Filtered out keywords and function calls"],
            files_affected=[{"file_path": "logs/where_clause_column_extractor.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=["Focused regex on WHERE clause content. Limitations exist for very complex nested conditions or UDFs."]
        )
        return potential_columns

    def generate_report(self, query_id: str, columns: Set[str], output_file: str = None) -> Dict[str, Any]:
        """Generates a report for the extracted WHERE clause columns of a query."""
        report_data = {
            "query_id": query_id,
            "where_clause_columns": sorted(list(columns)),
            "extraction_timestamp": datetime.now().isoformat(),
            "method": "Regex-based WHERE clause column extraction (Initial Version)"
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report_data, f, indent=4)
                logger.info(f"Generated WHERE clause column report for {query_id} at {output_file}")
            except IOError as e:
                logger.error(f"Failed to write WHERE column report to {output_file}: {e}")
        
        self._update_changelog(
            action_summary=f"Generated WHERE clause column report for query {query_id}",
            action_type="Report Generation",
            previous_state=f"WHERE clause columns extracted for {query_id}",
            current_state=f"Report for {query_id} available",
            changes_made=["Serialized extracted WHERE clause columns to JSON"],
            files_affected=[{"file_path": output_file if output_file else "N/A", "change_type": "CREATED" if output_file else "NONE", "impact_level": "LOW"}],
            technical_decisions=["Report includes list of extracted WHERE clause columns and timestamp"]
        )
        return report_data

# Example Usage
if __name__ == "__main__":
    extractor = WhereClauseColumnExtractor()
    
    test_query_id_1 = "test_wc_q1"
    test_sql_1 = """
    SELECT 
        c.customer_id, c.first_name, o.order_date
    FROM customers c JOIN orders o ON c.customer_id = o.customer_id
    WHERE 
        c.registration_date > '2023-01-01' AND 
        (o.status = 'SHIPPED' OR o.total_amount > 1000) AND
        c.country IN ('USA', 'Canada') AND
        NOT (c.email IS NULL) AND
        EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.order_id AND oi.quantity > 5)
    GROUP BY c.customer_id, c.first_name, o.order_date
    ORDER BY o.order_date DESC;
    """
    
    where_cols_1 = extractor.extract_columns_from_where_clause(test_query_id_1, test_sql_1)
    print(f"\nExtracted WHERE clause columns for query '{test_query_id_1}':")
    for col in sorted(list(where_cols_1)):
        print(f"  - {col}")
    extractor.generate_report(test_query_id_1, where_cols_1, f"logs/where_columns_{test_query_id_1}.json")

    test_query_id_2 = "test_wc_q2_no_where"
    test_sql_2 = "SELECT name, age FROM users;"
    where_cols_2 = extractor.extract_columns_from_where_clause(test_query_id_2, test_sql_2)
    print(f"\nExtracted WHERE clause columns for query '{test_query_id_2}': {where_cols_2}")
    extractor.generate_report(test_query_id_2, where_cols_2, f"logs/where_columns_{test_query_id_2}.json")

    test_query_id_3 = "test_wc_q3_simple"
    test_sql_3 = "SELECT product_name FROM products WHERE category_id = 10 AND price < 50.00 AND is_active = TRUE"
    where_cols_3 = extractor.extract_columns_from_where_clause(test_query_id_3, test_sql_3)
    print(f"\nExtracted WHERE clause columns for query '{test_query_id_3}':")
    for col in sorted(list(where_cols_3)):
        print(f"  - {col}")
    extractor.generate_report(test_query_id_3, where_cols_3, f"logs/where_columns_{test_query_id_3}.json")

    test_query_id_4 = "test_wc_q4_functions"
    test_sql_4 = "SELECT id FROM logs WHERE DATE(log_timestamp) = CURRENT_DATE AND severity_level > get_threshold(department_id)"
    where_cols_4 = extractor.extract_columns_from_where_clause(test_query_id_4, test_sql_4)
    print(f"\nExtracted WHERE clause columns for query '{test_query_id_4}':")
    for col in sorted(list(where_cols_4)):
        print(f"  - {col}")
    extractor.generate_report(test_query_id_4, where_cols_4, f"logs/where_columns_{test_query_id_4}.json")

