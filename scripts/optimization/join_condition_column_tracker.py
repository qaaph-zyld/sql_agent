#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JOIN Condition Column Tracker

This module extracts columns specifically mentioned within JOIN conditions (ON clauses)
_of a SQL query. It follows the mandatory changelog protocol.
"""

import logging
import json
import re
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/join_condition_column_tracker.log'
)
logger = logging.getLogger(__name__)

class JoinConditionColumnTracker:
    """
    Extracts column mentions specifically from JOIN ON clauses of SQL queries.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the JoinConditionColumnTracker."""
        self.changelog_engine = ChangelogEngine()
        self._update_changelog(
            action_summary="JoinConditionColumnTracker initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Tracker ready to process JOIN conditions",
            changes_made=["Initialized internal state"],
            files_affected=[{"file_path": "scripts/optimization/join_condition_column_tracker.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Will use regex-based parsing focused on JOIN ON clause content"]
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

    def _extract_join_on_clauses_content(self, sql_query: str) -> List[str]:
        """Isolates the content of JOIN ON clauses from a SQL query.
        This regex approach aims to find 'JOIN table ON condition' patterns.
        It might struggle with very complex nested joins or non-standard syntax.
        """
        # Regex to find 'JOIN ... ON ...' clauses. Captures the condition part.
        # It tries to handle different types of JOINs (INNER, LEFT, RIGHT, FULL).
        # The (.*?) for the condition is non-greedy.
        # We need to be careful about the end of the condition (e.g., before WHERE, another JOIN, GROUP BY, etc.)
        # This regex is a starting point and will likely need refinement.
        pattern = r'\b(?:INNER\s+|LEFT\s+(?:OUTER\s+)?|RIGHT\s+(?:OUTER\s+)?|FULL\s+(?:OUTER\s+)?|CROSS\s+)?JOIN\s+.*?\bON\b(.*?)(?=\bWHERE\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bHAVING\b|\bLIMIT\b|\bUNION\b|\bJOIN\b|\bWINDOW\b|\bFETCH\b|\bOFFSET\b|\bFOR\b|;|$)'
        matches = re.finditer(pattern, sql_query, re.IGNORECASE | re.DOTALL)
        
        on_clauses_content = []
        for match in matches:
            condition_content = match.group(1).strip()
            if condition_content:
                logger.info(f"Extracted JOIN ON clause content: {condition_content[:200]}...")
                on_clauses_content.append(condition_content)
        
        if not on_clauses_content:
            logger.info("No JOIN ON clauses found in the query.")
            
        return on_clauses_content

    def extract_columns_from_join_conditions(self, query_id: str, sql_query: str) -> Set[str]:
        """Extracts all unique column mentions from JOIN ON conditions of a SQL query.

        Args:
            query_id (str): An identifier for the query.
            sql_query (str): The SQL query string.

        Returns:
            Set[str]: A set of unique column names mentioned in JOIN ON conditions.
        """
        logger.info(f"Query {query_id}: Starting JOIN condition column extraction.")
        
        join_on_contents = self._extract_join_on_clauses_content(sql_query)
        if not join_on_contents:
            self._update_changelog(
                action_summary=f"No JOIN ON clauses found for query {query_id}",
                action_type="Data Extraction",
                previous_state="Query received",
                current_state="No JOIN ON clause columns identified",
                changes_made=["Identified absence of JOIN ON clauses"],
                files_affected=[{"file_path": "logs/join_condition_column_tracker.log", "change_type": "APPENDED", "impact_level": "LOW"}],
                technical_decisions=["Query does not contain JOIN ON clauses for analysis"]
            )
            return set()

        identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*\b'
        # Keywords/functions common in JOIN ON clauses that are not columns themselves
        # (e.g., operators like =, <, >, AND, OR; functions if any are used in joins)
        sql_keywords_for_join_conditions = {
            'AND', 'OR', 'NOT', 'NULL', 'IS', 'IN', 'LIKE', 'BETWEEN', 'EXISTS',
            'USING' # Though USING(...) implies columns, the keyword itself isn't a column.
            # Common functions (less common directly in ON conditions but possible)
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ABS', 'ROUND', 'CAST', 'SUBSTRING', 'TRIM', 'LENGTH',
            'DATE', 'YEAR', 'MONTH', 'DAY', 'NOW', 'CURRENT_DATE', 'CURRENT_TIMESTAMP'
        }

        potential_columns = set()
        for content_block in join_on_contents:
            for match in re.finditer(identifier_pattern, content_block):
                mention = match.group(0)
                
                # Check if it's followed by an opening parenthesis (likely a function call)
                if match.end() < len(content_block) and content_block[match.end():].lstrip().startswith('('):
                    continue # Skip function-like calls
                
                if mention.upper() not in sql_keywords_for_join_conditions:
                    if not mention.isdigit(): # Avoid pure numbers
                        potential_columns.add(mention)
        
        logger.info(f"Query {query_id}: Extracted {len(potential_columns)} potential columns from JOIN conditions: {potential_columns}")
        
        self._update_changelog(
            action_summary=f"Extracted {len(potential_columns)} columns from JOIN conditions of query {query_id}",
            action_type="Data Extraction",
            previous_state="JOIN ON clause content isolated",
            current_state="Columns from JOIN ON clauses identified",
            changes_made=["Applied regex for column identification within JOIN ON clauses", "Filtered out keywords and function calls"],
            files_affected=[{"file_path": "logs/join_condition_column_tracker.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=["Focused regex on JOIN ON clause content. Limitations for complex syntax or non-standard JOINs."]
        )
        return potential_columns

    def generate_report(self, query_id: str, columns: Set[str], output_file: str = None) -> Dict[str, Any]:
        """Generates a report for the extracted JOIN condition columns of a query."""
        report_data = {
            "query_id": query_id,
            "join_condition_columns": sorted(list(columns)),
            "extraction_timestamp": datetime.now().isoformat(),
            "method": "Regex-based JOIN ON clause column extraction (Initial Version)"
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report_data, f, indent=4)
                logger.info(f"Generated JOIN condition column report for {query_id} at {output_file}")
            except IOError as e:
                logger.error(f"Failed to write JOIN column report to {output_file}: {e}")
        
        self._update_changelog(
            action_summary=f"Generated JOIN condition column report for query {query_id}",
            action_type="Report Generation",
            previous_state=f"JOIN condition columns extracted for {query_id}",
            current_state=f"Report for {query_id} available",
            changes_made=["Serialized extracted JOIN condition columns to JSON"],
            files_affected=[{"file_path": output_file if output_file else "N/A", "change_type": "CREATED" if output_file else "NONE", "impact_level": "LOW"}],
            technical_decisions=["Report includes list of extracted JOIN columns and timestamp"]
        )
        return report_data

# Example Usage
if __name__ == "__main__":
    tracker = JoinConditionColumnTracker()
    
    test_query_id_1 = "test_join_q1"
    test_sql_1 = """
    SELECT c.name, o.order_date, p.product_name
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id AND o.order_date > '2023-01-01'
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id AND p.category = 'Electronics'
    WHERE c.status = 'ACTIVE'
    """
    
    join_cols_1 = tracker.extract_columns_from_join_conditions(test_query_id_1, test_sql_1)
    print(f"\nExtracted JOIN condition columns for query '{test_query_id_1}':")
    for col in sorted(list(join_cols_1)):
        print(f"  - {col}")
    tracker.generate_report(test_query_id_1, join_cols_1, f"logs/join_columns_{test_query_id_1}.json")

    test_query_id_2 = "test_join_q2_no_on_clause"
    test_sql_2 = "SELECT * FROM table1 CROSS JOIN table2 WHERE table1.id = 10;"
    join_cols_2 = tracker.extract_columns_from_join_conditions(test_query_id_2, test_sql_2)
    print(f"\nExtracted JOIN condition columns for query '{test_query_id_2}': {join_cols_2}")
    tracker.generate_report(test_query_id_2, join_cols_2, f"logs/join_columns_{test_query_id_2}.json")

    test_query_id_3 = "test_join_q3_multiple_conditions"
    test_sql_3 = """
    SELECT e.name, d.department_name, p.project_name
    FROM employees e
    JOIN departments d ON e.department_id = d.id AND d.location_id = 100
    LEFT JOIN employee_projects ep ON e.employee_id = ep.emp_id
    JOIN projects p ON ep.project_code = p.code AND p.status = 'IN_PROGRESS' AND e.hire_date < p.start_date
    """
    join_cols_3 = tracker.extract_columns_from_join_conditions(test_query_id_3, test_sql_3)
    print(f"\nExtracted JOIN condition columns for query '{test_query_id_3}':")
    for col in sorted(list(join_cols_3)):
        print(f"  - {col}")
    tracker.generate_report(test_query_id_3, join_cols_3, f"logs/join_columns_{test_query_id_3}.json")

    test_query_id_4 = "test_join_q4_using_clause_not_handled_by_on_regex"
    test_sql_4 = "SELECT a.val, b.val FROM table_a a JOIN table_b b USING (id, common_column) WHERE a.type = 'X';"
    # Current regex for ON clauses won't pick up USING. This is a known limitation.
    join_cols_4 = tracker.extract_columns_from_join_conditions(test_query_id_4, test_sql_4)
    print(f"\nExtracted JOIN condition columns for query '{test_query_id_4}' (expect empty for ON, USING not parsed): {join_cols_4}")
    tracker.generate_report(test_query_id_4, join_cols_4, f"logs/join_columns_{test_query_id_4}.json")

