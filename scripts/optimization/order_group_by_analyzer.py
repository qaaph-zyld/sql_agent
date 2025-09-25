#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ORDER BY / GROUP BY Clause Column Analyzer

This module extracts columns specifically mentioned within ORDER BY and GROUP BY clauses
of a SQL query. It follows the mandatory changelog protocol.
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
    filename='logs/order_group_by_analyzer.log'
)
logger = logging.getLogger(__name__)

class OrderGroupByAnalyzer:
    """
    Extracts column mentions from ORDER BY and GROUP BY clauses of SQL queries.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the OrderGroupByAnalyzer."""
        self.changelog_engine = ChangelogEngine()
        self._update_changelog(
            action_summary="OrderGroupByAnalyzer initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Analyzer ready to process ORDER BY/GROUP BY clauses",
            changes_made=["Initialized internal state"],
            files_affected=[{"file_path": "scripts/optimization/order_group_by_analyzer.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Will use regex-based parsing for clause content and column extraction"]
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

    def _extract_clause_content(self, sql_query: str, clause_keyword: str) -> Optional[str]:
        """Isolates the content of a specific clause (e.g., ORDER BY, GROUP BY) from a SQL query.
        Stops before other major clauses or end of query.
        """
        # Pattern: \bCLAUSE_KEYWORD\b (content) (?:NEXT_MAJOR_CLAUSE_OR_END)
        # Next major clauses: HAVING, LIMIT, OFFSET, FETCH, WINDOW, FOR, UNION, or end of query/semicolon.
        pattern = fr'\b{clause_keyword}\b(.*?)(?:\bHAVING\b|\bLIMIT\b|\bOFFSET\b|\bFETCH\b|\bWINDOW\b|\bFOR\b|\bUNION\b|;|$)'
        match = re.search(pattern, sql_query, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            logger.info(f"Extracted {clause_keyword} content: {content[:200]}...")
            return content
        else:
            logger.info(f"No {clause_keyword} clause found in the query.")
            return None

    def _extract_columns_from_clause_content(self, clause_content: str) -> Set[str]:
        """Extracts column names from the content of an ORDER BY or GROUP BY clause."""
        if not clause_content:
            return set()

        identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*\b'
        # Keywords/tokens in ORDER BY/GROUP BY that are not columns (e.g., ASC, DESC, NULLS FIRST/LAST)
        # Also, common aggregate functions if they appear (though typically it's the alias in ORDER BY)
        non_column_tokens = {
            'ASC', 'DESC', 'NULLS', 'FIRST', 'LAST',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX' # Less likely raw in GROUP BY, but aliases are common
        }

        potential_columns = set()
        # Split by comma, as columns in these clauses are comma-separated
        parts = clause_content.split(',')
        for part in parts:
            part = part.strip()
            # Try to find the main identifier, ignoring ASC/DESC etc.
            # This simple approach takes the first identifier-like token.
            match = re.match(identifier_pattern, part)
            if match:
                mention = match.group(0)
                # Check if it's followed by an opening parenthesis (likely a function call)
                # This check needs to be on `part` not just `mention` if `part` contains more than the mention.
                # A more robust way: check if the full `part` looks like `FUNC(...)`
                if '(' in part and part.endswith(')'):
                    # If it's a known aggregate function, skip. Otherwise, it could be a UDF or complex expression.
                    # For simplicity, if it looks like a function call, we skip it here assuming it's an expression.
                    # This means `ORDER BY my_func(column)` would not extract `column` directly here, but `my_func(column)` as a whole.
                    # If the goal is to get `column` from `my_func(column)`, a deeper parse of `part` is needed.
                    # For now, we are interested in the item being ordered/grouped by.
                    if mention.upper() in non_column_tokens: # e.g. COUNT(...) 
                        continue
                    # else: it's potentially an expression or UDF like my_func(col) or col + 1. We take the whole 'part' or 'mention'.
                    # Let's assume for now we are interested in the direct identifiers.

                if mention.upper() not in non_column_tokens:
                    if not mention.isdigit():
                        potential_columns.add(mention)
        return potential_columns

    def analyze_order_by_clause(self, query_id: str, sql_query: str) -> Set[str]:
        """Extracts columns from the ORDER BY clause."""
        logger.info(f"Query {query_id}: Analyzing ORDER BY clause.")
        clause_content = self._extract_clause_content(sql_query, 'ORDER BY')
        columns = self._extract_columns_from_clause_content(clause_content)
        self._log_and_update_changelog(query_id, 'ORDER BY', columns, clause_content is not None)
        return columns

    def analyze_group_by_clause(self, query_id: str, sql_query: str) -> Set[str]:
        """Extracts columns from the GROUP BY clause."""
        logger.info(f"Query {query_id}: Analyzing GROUP BY clause.")
        clause_content = self._extract_clause_content(sql_query, 'GROUP BY')
        columns = self._extract_columns_from_clause_content(clause_content)
        self._log_and_update_changelog(query_id, 'GROUP BY', columns, clause_content is not None)
        return columns

    def _log_and_update_changelog(self, query_id: str, clause_type: str, columns: Set[str], clause_found: bool):
        if not clause_found:
            action_summary = f"No {clause_type} clause found for query {query_id}"
            current_state = f"No {clause_type} columns identified"
            changes = [f"Identified absence of {clause_type} clause"]
            tech_decisions = [f"Query does not contain a {clause_type} clause for analysis"]
        else:
            action_summary = f"Extracted {len(columns)} columns from {clause_type} clause of query {query_id}"
            current_state = f"Columns from {clause_type} clause identified"
            changes = [f"Applied regex for column identification within {clause_type} clause", "Filtered out keywords"]
            tech_decisions = [f"Focused regex on {clause_type} clause content. Limitations for complex expressions."]
        
        logger.info(f"Query {query_id}: Extracted {len(columns)} columns from {clause_type} clause: {columns}")
        self._update_changelog(
            action_summary=action_summary,
            action_type="Data Extraction",
            previous_state=f"{clause_type} clause content isolated or determined absent",
            current_state=current_state,
            changes_made=changes,
            files_affected=[{"file_path": "logs/order_group_by_analyzer.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=tech_decisions
        )

    def generate_report(self, query_id: str, order_by_columns: Set[str], group_by_columns: Set[str], output_file: str = None) -> Dict[str, Any]:
        """Generates a report for the extracted ORDER BY and GROUP BY columns."""
        report_data = {
            "query_id": query_id,
            "order_by_columns": sorted(list(order_by_columns)),
            "group_by_columns": sorted(list(group_by_columns)),
            "analysis_timestamp": datetime.now().isoformat(),
            "method": "Regex-based ORDER BY/GROUP BY clause analysis (Initial Version)"
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report_data, f, indent=4)
                logger.info(f"Generated ORDER BY/GROUP BY column report for {query_id} at {output_file}")
            except IOError as e:
                logger.error(f"Failed to write ORDER BY/GROUP BY report to {output_file}: {e}")
        
        self._update_changelog(
            action_summary=f"Generated ORDER BY/GROUP BY column report for query {query_id}",
            action_type="Report Generation",
            previous_state=f"ORDER BY/GROUP BY columns analyzed for {query_id}",
            current_state=f"Report for {query_id} available",
            changes_made=["Serialized extracted columns to JSON"],
            files_affected=[{"file_path": output_file if output_file else "N/A", "change_type": "CREATED" if output_file else "NONE", "impact_level": "LOW"}],
            technical_decisions=["Report includes lists of extracted ORDER BY and GROUP BY columns and timestamp"]
        )
        return report_data

# Example Usage
if __name__ == "__main__":
    analyzer = OrderGroupByAnalyzer()
    
    test_query_id_1 = "test_og_q1"
    test_sql_1 = """
    SELECT department_id, COUNT(*) AS num_employees, SUM(salary) AS total_salary
    FROM employees
    WHERE hire_date > '2020-01-01'
    GROUP BY department_id, location_id
    ORDER BY total_salary DESC, department_id ASC NULLS LAST;
    """
    
    print(f"--- Analyzing Query: {test_query_id_1} ---")
    orderby_cols_1 = analyzer.analyze_order_by_clause(test_query_id_1, test_sql_1)
    groupby_cols_1 = analyzer.analyze_group_by_clause(test_query_id_1, test_sql_1)
    print(f"ORDER BY Columns: {orderby_cols_1}")
    print(f"GROUP BY Columns: {groupby_cols_1}")
    analyzer.generate_report(test_query_id_1, orderby_cols_1, groupby_cols_1, f"logs/orderby_groupby_{test_query_id_1}.json")

    test_query_id_2 = "test_og_q2_no_clauses"
    test_sql_2 = "SELECT name FROM products WHERE category = 'Toys';"
    print(f"\n--- Analyzing Query: {test_query_id_2} ---")
    orderby_cols_2 = analyzer.analyze_order_by_clause(test_query_id_2, test_sql_2)
    groupby_cols_2 = analyzer.analyze_group_by_clause(test_query_id_2, test_sql_2)
    print(f"ORDER BY Columns: {orderby_cols_2}")
    print(f"GROUP BY Columns: {groupby_cols_2}")
    analyzer.generate_report(test_query_id_2, orderby_cols_2, groupby_cols_2, f"logs/orderby_groupby_{test_query_id_2}.json")

    test_query_id_3 = "test_og_q3_expressions"
    # Note: Current simple extraction might pick up 'YEAR' or 'MONTH' if not careful with function parsing.
    # The current _extract_columns_from_clause_content is basic.
    test_sql_3 = "SELECT YEAR(order_date) AS ord_year, COUNT(order_id) FROM orders GROUP BY YEAR(order_date), MONTH(order_date) ORDER BY ord_year DESC, COUNT(order_id) ASC;"
    print(f"\n--- Analyzing Query: {test_query_id_3} ---")
    orderby_cols_3 = analyzer.analyze_order_by_clause(test_query_id_3, test_sql_3)
    groupby_cols_3 = analyzer.analyze_group_by_clause(test_query_id_3, test_sql_3)
    print(f"ORDER BY Columns: {orderby_cols_3}") # Expects 'ord_year', 'COUNT(order_id)' or similar based on regex
    print(f"GROUP BY Columns: {groupby_cols_3}") # Expects 'YEAR(order_date)', 'MONTH(order_date)' or similar
    analyzer.generate_report(test_query_id_3, orderby_cols_3, groupby_cols_3, f"logs/orderby_groupby_{test_query_id_3}.json")

