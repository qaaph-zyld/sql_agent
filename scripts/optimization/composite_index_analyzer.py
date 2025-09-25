#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Composite Index Analyzer

This module analyzes patterns of co-occurring columns in query clauses
to identify potential candidates for composite (multi-column) indexes.
It follows the mandatory changelog protocol.
"""

import logging
import json
from typing import Dict, List, Any, Set, Tuple, Optional
from datetime import datetime
from collections import defaultdict, Counter

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/composite_index_analyzer.log'
)
logger = logging.getLogger(__name__)

class CompositeIndexAnalyzer:
    """
    Identifies potential composite indexes based on co-occurrence of columns.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the CompositeIndexAnalyzer."""
        self.changelog_engine = ChangelogEngine()
        self._update_changelog(
            action_summary="CompositeIndexAnalyzer initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Analyzer ready to identify composite index candidates",
            changes_made=["Initialized internal state"],
            files_affected=[{"file_path": "scripts/optimization/composite_index_analyzer.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Will use heuristics based on co-occurrence of columns in WHERE and JOIN clauses, considering column order and selectivity (future)"]
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

    def _find_cooccurring_columns(self, query_id: str, sql_query: str, 
                                  where_columns_ordered: Optional[List[List[str]]] = None,
                                  join_conditions_ordered: Optional[List[List[Tuple[str, str]]]] = None) -> List[Tuple[str, ...]]:
        """Identifies sets of columns that frequently appear together in clauses.
        This is a simplified initial approach. More sophisticated parsing of the SQL query
        would be needed to accurately determine the order and grouping of conditions.

        Args:
            query_id (str): Identifier for the SQL query.
            sql_query (str): The SQL query string (for context, future parsing).
            where_columns_ordered (Optional[List[List[str]]]): 
                A list of column groups from WHERE clauses, preserving order within each AND-connected group.
                Example: For WHERE col1 = x AND col2 = y OR col3 = z, this might be [['col1', 'col2'], ['col3']].
                This requires a more sophisticated parser than currently implemented in WhereClauseColumnExtractor.
                For now, we might pass a flat list of where_columns and look for common pairs/triplets.
            join_conditions_ordered (Optional[List[List[Tuple[str, str]]]]):
                A list of column pairs from JOIN ON conditions, preserving order.
                Example: For JOIN t1 ON t1.a = t2.b AND t1.c = t2.d, this might be [[('t1.a', 't2.b'), ('t1.c', 't2.d')]].

        Returns:
            List[Tuple[str, ...]]: A list of tuples, each representing a potential composite index (ordered columns).
        """
        logger.info(f"Query {query_id}: Searching for co-occurring columns for composite indexes.")
        potential_composites = []
        
        # Placeholder: For now, this is highly simplified. 
        # A real implementation needs to parse the query structure to find true co-occurrences.
        # Example: if where_columns_ordered is available and represents ANDed groups:
        if where_columns_ordered:
            for group in where_columns_ordered:
                if len(group) > 1:
                    # Consider prefixes for composite indexes, e.g., (col1), (col1, col2), (col1, col2, col3)
                    for i in range(1, len(group) + 1):
                        composite_candidate = tuple(group[:i])
                        if len(composite_candidate) > 1: # Only interested in multi-column
                            potential_composites.append(composite_candidate)
                            logger.info(f"Query {query_id}: Found potential WHERE composite: {composite_candidate}")

        # Example for JOIN conditions (if structured input is available)
        # This would typically involve columns from the *same table* in a multi-part JOIN key, 
        # or columns used in a JOIN that also appear in a subsequent WHERE/ORDER BY.
        # For now, let's assume join_conditions_ordered gives pairs like [('t1.a', 't2.b'), ('t1.c', 't2.d')]
        # A composite index on (t1.a, t1.c) might be useful if these are often queried together.
        # This part needs significant refinement based on actual SQL parsing capabilities.

        # Simplified: If we only have flat sets of columns from previous analyzers:
        # This is too naive as it doesn't respect AND/OR logic or structure.
        # For a slightly better approach, one might count pairs of columns appearing in the same query's WHERE clauses.

        if not potential_composites:
            logger.info(f"Query {query_id}: No obvious co-occurring column patterns found with current basic analysis.")
        
        # Deduplicate while preserving order (if multiple identical tuples were added)
        # This is not strictly necessary if logic above avoids duplicates, but good for safety.
        # Using dict.fromkeys to keep order for Python 3.7+
        return list(dict.fromkeys(potential_composites))

    def recommend_composite_indexes(self, query_id: str, sql_query: str,
                                    where_columns: Set[str], 
                                    join_columns: Set[str],
                                    # Future: Pass structured column data from parsers
                                    # where_columns_ordered: Optional[List[List[str]]] = None,
                                    # join_conditions_ordered: Optional[List[List[Tuple[str, str]]]] = None 
                                    ) -> List[Dict[str, Any]]:
        """
        Recommends composite indexes based on co-occurring columns.

        Args:
            query_id (str): Identifier for the SQL query.
            sql_query (str): The SQL query string itself for context.
            where_columns (Set[str]): Columns from WHERE clauses (flat set for now).
            join_columns (Set[str]): Columns from JOIN clauses (flat set for now).

        Returns:
            List[Dict[str, Any]]: List of recommended composite indexes.
        """
        logger.info(f"Query {query_id}: Starting composite index recommendation.")
        recommendations = []

        # --- THIS IS A MAJOR PLACEHOLDER --- 
        # The _find_cooccurring_columns method needs to be much more sophisticated.
        # For this initial version, we'll simulate finding one or two simple patterns
        # if specific columns are present, to demonstrate structure.
        
        # Simulate finding an ordered group from a WHERE clause if we had a better parser
        # Example: WHERE users.status = 'active' AND users.registration_date > '2023-01-01'
        # This would ideally come from a parser as [['users.status', 'users.registration_date']]
        simulated_where_groups = []
        if 'users.status' in where_columns and 'users.registration_date' in where_columns:
            simulated_where_groups.append(['users.status', 'users.registration_date'])
        if 'orders.customer_id' in where_columns and 'orders.order_date' in where_columns:
            simulated_where_groups.append(['orders.customer_id', 'orders.order_date'])

        cooccurring_column_tuples = self._find_cooccurring_columns(query_id, sql_query, 
                                                                 where_columns_ordered=simulated_where_groups)

        for col_tuple in cooccurring_column_tuples:
            if not col_tuple or len(col_tuple) < 2: # Ensure it's a multi-column tuple
                continue

            # Assume the first column's table is the table for the index
            # This needs robust parsing of column names like 'table.column'
            first_col_parts = col_tuple[0].split('.')
            table_name = first_col_parts[0] if len(first_col_parts) > 1 else "<unknown_table>"
            
            # Ensure all columns in the tuple belong to the same table for a simple composite index
            # This is a simplification; cross-table analysis is much more complex.
            is_single_table_composite = True
            for col in col_tuple:
                if not col.startswith(table_name + '.'):
                    is_single_table_composite = False # Or try to infer table if not prefixed
                    # For now, skip if tables don't match the first column's table easily
                    # This check is very basic.
                    current_col_table = col.split('.')[0] if '.' in col else None
                    if current_col_table != table_name:
                        is_single_table_composite = False
                        break
            
            if not is_single_table_composite and table_name != "<unknown_table>":
                logger.warning(f"Query {query_id}: Skipping composite candidate {col_tuple} as columns might span multiple tables or table cannot be determined consistently for all columns.")
                continue
            
            column_names_for_index = [col.split('.')[1] if '.' in col else col for col in col_tuple]
            index_name_suggestion = f"idx_{table_name}_comp_{'_'.join(column_names_for_index)}"
            sql_command_suggestion = f"CREATE INDEX {index_name_suggestion} ON {table_name}({', '.join(column_names_for_index)});"
            
            recommendation = {
                "columns": list(col_tuple),
                "table_name": table_name,
                "reason": f"Columns {', '.join(col_tuple)} frequently co-occur in query conditions.",
                "score": 50 * len(col_tuple), # Basic score based on number of columns
                "suggestion_type": "CREATE COMPOSITE INDEX",
                "index_name_suggestion": index_name_suggestion,
                "sql_command_suggestion": sql_command_suggestion
            }
            recommendations.append(recommendation)

        logger.info(f"Query {query_id}: Generated {len(recommendations)} composite index recommendations.")
        self._update_changelog(
            action_summary=f"Generated {len(recommendations)} composite index recommendations for query {query_id}",
            action_type="Composite Index Recommendation",
            previous_state="Co-occurring column patterns identified (or simulated)",
            current_state="Composite index recommendations available",
            changes_made=["Applied heuristics to co-occurring column data", "Generated CREATE INDEX statements for suitable composite indexes"],
            files_affected=[{"file_path": "logs/composite_index_analyzer.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=["Initial recommendations based on simulated co-occurrence in WHERE clauses. Requires significant improvement in SQL parsing for accurate co-occurrence detection and column ordering."]
        )
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)

    def generate_report(self, query_id: str, recommendations: List[Dict[str, Any]], output_file: str = None) -> Dict[str, Any]:
        """Generates a report for the recommended composite indexes."""
        report_data = {
            "query_id": query_id,
            "composite_index_recommendations": recommendations,
            "recommendation_timestamp": datetime.now().isoformat(),
            "method": "Heuristic-based Composite Index Analyzer (Initial Placeholder Version)"
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report_data, f, indent=4)
                logger.info(f"Generated composite index recommendation report for {query_id} at {output_file}")
            except IOError as e:
                logger.error(f"Failed to write composite index report to {output_file}: {e}")
        
        self._update_changelog(
            action_summary=f"Generated composite index recommendation report for query {query_id}",
            action_type="Report Generation",
            previous_state=f"Composite index recommendations generated for {query_id}",
            current_state=f"Report for {query_id} available",
            changes_made=["Serialized composite index recommendations to JSON"],
            files_affected=[{"file_path": output_file if output_file else "N/A", "change_type": "CREATED" if output_file else "NONE", "impact_level": "LOW"}],
            technical_decisions=["Report includes list of recommended composite indexes, reasons, scores, and suggested SQL commands. Current version is highly placeholder."]
        )
        return report_data

# Example Usage
if __name__ == "__main__":
    analyzer = CompositeIndexAnalyzer()
    
    query_id_1 = "sample_query_for_composite_001"
    # Simulate flat sets of columns from previous analyzers
    where_cols_1 = {'users.status', 'users.registration_date', 'users.city', 'orders.customer_id', 'orders.order_date'}
    join_cols_1 = {'users.id', 'orders.user_id'}
    sql_query_1 = "SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE users.status = 'A' AND users.registration_date > '2023-01-01' AND orders.customer_id = 123 AND orders.order_date < NOW();"

    print(f"--- Recommending composite indexes for Query: {query_id_1} ---")
    # In a real scenario, more structured input would be passed to recommend_composite_indexes
    # For now, it uses simulated co-occurrence detection inside the method.
    recommendations1 = analyzer.recommend_composite_indexes(query_id_1, sql_query_1, where_cols_1, join_cols_1)
    
    if recommendations1:
        print(f"\nRecommended composite indexes for '{query_id_1}':")
        for rec in recommendations1:
            print(f"  - Columns: {rec['columns']}, Table: {rec['table_name']}, Score: {rec['score']}")
            print(f"    Reason: {rec['reason']}")
            print(f"    Suggested SQL: {rec['sql_command_suggestion']}")
    else:
        print(f"No composite index recommendations for '{query_id_1}' with current basic analysis.")
    analyzer.generate_report(query_id_1, recommendations1, f"logs/composite_index_recommendations_{query_id_1}.json")

    query_id_2 = "query_no_obvious_composite"
    where_cols_2 = {'products.name'}
    join_cols_2 = set()
    sql_query_2 = "SELECT * FROM products WHERE products.name LIKE '%gizmo%';"
    print(f"\n--- Recommending composite indexes for Query: {query_id_2} ---")
    recommendations2 = analyzer.recommend_composite_indexes(query_id_2, sql_query_2, where_cols_2, join_cols_2)
    if recommendations2:
        print(f"\nRecommended composite indexes for '{query_id_2}':")
        for rec in recommendations2:
            print(f"  - Columns: {rec['columns']}")
    else:
        print(f"No composite index recommendations for '{query_id_2}' with current basic analysis.")
    analyzer.generate_report(query_id_2, recommendations2, f"logs/composite_index_recommendations_{query_id_2}.json")

