#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Single-Column Index Recommender

This module analyzes column usage statistics from various query parts
(WHERE, JOIN, ORDER BY, GROUP BY) to recommend single-column indexes.
It follows the mandatory changelog protocol.
"""

import logging
import json
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/single_column_index_recommender.log'
)
logger = logging.getLogger(__name__)

class SingleColumnIndexRecommender:
    """
    Recommends single-column indexes based on analyzed column usage patterns.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the SingleColumnIndexRecommender."""
        self.changelog_engine = ChangelogEngine()
        self._update_changelog(
            action_summary="SingleColumnIndexRecommender initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Recommender ready to process column usage data",
            changes_made=["Initialized internal state"],
            files_affected=[{"file_path": "scripts/optimization/single_column_index_recommender.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Will use heuristics based on WHERE, JOIN, ORDER BY, GROUP BY column frequencies and types"]
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

    def _evaluate_column_for_index(self, column_name: str, usage_context: Dict[str, Any]) -> Tuple[bool, str, int]:
        """Evaluates a single column's potential for indexing based on usage context.
        
        Args:
            column_name (str): The name of the column (e.g., 'table.column').
            usage_context (Dict[str, Any]): Information about how the column is used,
                                           e.g., {'in_where': True, 'in_join': False, 
                                                  'in_order_by': True, 'cardinality': 'high' (optional)}
        
        Returns:
            Tuple[bool, str, int]: (should_index, reason, score)
                                    Score can be a simple heuristic value.
        """
        # Basic heuristic: Columns in WHERE, JOIN, ORDER BY, or GROUP BY are good candidates.
        # This will be expanded with more sophisticated rules.
        score = 0
        reasons = []

        if usage_context.get('in_where_clause'):
            score += 30
            reasons.append("Used in WHERE clause")
        if usage_context.get('in_join_condition'):
            score += 25 # JOIN columns are often good candidates
            reasons.append("Used in JOIN condition")
        if usage_context.get('in_order_by_clause'):
            score += 20
            reasons.append("Used in ORDER BY clause")
        if usage_context.get('in_group_by_clause'):
            score += 15
            reasons.append("Used in GROUP BY clause")
        
        # Placeholder for cardinality check - high cardinality columns in WHERE might be less selective
        # but good for JOINs/ORDER BY. Low cardinality good for some WHEREs.
        # if usage_context.get('cardinality') == 'low' and usage_context.get('in_where_clause'):
        #     score += 5
        #     reasons.append("Low cardinality and used in WHERE")

        should_index = score > 0
        reason_summary = ", ".join(reasons) if reasons else "Not frequently used in key clauses"
        
        logger.info(f"Evaluated column '{column_name}': Score={score}, Reason='{reason_summary}', ShouldIndex={should_index}")
        return should_index, reason_summary, score

    def recommend_indexes(self, query_id: str, 
                          where_columns: Set[str], 
                          join_columns: Set[str], 
                          orderby_columns: Set[str], 
                          groupby_columns: Set[str],
                          all_mentioned_columns: Set[str] = None) -> List[Dict[str, Any]]:
        """Recommends single-column indexes based on aggregated column usage.

        Args:
            query_id (str): Identifier for the SQL query.
            where_columns (Set[str]): Columns found in WHERE clauses.
            join_columns (Set[str]): Columns found in JOIN ON conditions.
            orderby_columns (Set[str]): Columns found in ORDER BY clauses.
            groupby_columns (Set[str]): Columns found in GROUP BY clauses.
            all_mentioned_columns (Set[str], optional): All columns mentioned in the query.
                                                       Used to ensure we consider all relevant columns.

        Returns:
            List[Dict[str, Any]]: A list of recommended indexes, each a dict with
                                  {'column_name': str, 'reason': str, 'score': int, 'suggestion': str}.
        """
        logger.info(f"Query {query_id}: Starting single-column index recommendation.")
        recommendations = []
        
        # Consolidate all columns that have appeared in critical clauses
        candidate_columns = where_columns.union(join_columns).union(orderby_columns).union(groupby_columns)
        if all_mentioned_columns:
            candidate_columns = candidate_columns.union(all_mentioned_columns) # Ensure all are considered

        if not candidate_columns:
            logger.info(f"Query {query_id}: No candidate columns found for index recommendation.")
            self._update_changelog(
                action_summary=f"No index recommendations for query {query_id} due to no candidate columns",
                action_type="Index Recommendation", previous_state="Column usage data received",
                current_state="No recommendations made",
                changes_made=["Determined no columns met criteria for single-column indexing"],
                files_affected=[{"file_path": "logs/single_column_index_recommender.log", "change_type": "APPENDED", "impact_level": "LOW"}],
                technical_decisions=["No columns appeared in WHERE, JOIN, ORDER BY, or GROUP BY clauses."]
            )
            return []

        for col_name in sorted(list(candidate_columns)):
            usage_ctx = {
                'in_where_clause': col_name in where_columns,
                'in_join_condition': col_name in join_columns,
                'in_order_by_clause': col_name in orderby_columns,
                'in_group_by_clause': col_name in groupby_columns
                # 'cardinality': get_cardinality_for_column(col_name) # Placeholder for future integration
            }
            
            should_index, reason, score = self._evaluate_column_for_index(col_name, usage_ctx)
            
            if should_index:
                # Assuming column_name might be 'table.column' or just 'column'
                # For simplicity, if it contains '.', assume it's table.column
                table_name = col_name.split('.')[0] if '.' in col_name else "<unknown_table>"
                actual_col_name = col_name.split('.')[1] if '.' in col_name else col_name
                
                recommendation = {
                    "column_name": col_name,
                    "table_name": table_name,
                    "reason": reason,
                    "score": score,
                    "suggestion_type": "CREATE INDEX",
                    "index_name_suggestion": f"idx_{table_name}_{actual_col_name}",
                    "sql_command_suggestion": f"CREATE INDEX idx_{table_name}_{actual_col_name} ON {table_name}({actual_col_name});"
                }
                recommendations.append(recommendation)
        
        logger.info(f"Query {query_id}: Generated {len(recommendations)} single-column index recommendations.")
        self._update_changelog(
            action_summary=f"Generated {len(recommendations)} single-column index recommendations for query {query_id}",
            action_type="Index Recommendation",
            previous_state="Column usage data processed",
            current_state="Index recommendations available",
            changes_made=["Applied heuristics to column usage data", "Generated CREATE INDEX statements for suitable columns"],
            files_affected=[{"file_path": "logs/single_column_index_recommender.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=["Recommendations based on presence in key clauses (WHERE, JOIN, ORDER BY, GROUP BY). Score reflects importance."]
        )
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)

    def generate_report(self, query_id: str, recommendations: List[Dict[str, Any]], output_file: str = None) -> Dict[str, Any]:
        """Generates a report for the recommended single-column indexes."""
        report_data = {
            "query_id": query_id,
            "index_recommendations": recommendations,
            "recommendation_timestamp": datetime.now().isoformat(),
            "method": "Heuristic-based Single-Column Index Recommender (Initial Version)"
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report_data, f, indent=4)
                logger.info(f"Generated single-column index recommendation report for {query_id} at {output_file}")
            except IOError as e:
                logger.error(f"Failed to write index recommendation report to {output_file}: {e}")
        
        self._update_changelog(
            action_summary=f"Generated index recommendation report for query {query_id}",
            action_type="Report Generation",
            previous_state=f"Index recommendations generated for {query_id}",
            current_state=f"Report for {query_id} available",
            changes_made=["Serialized index recommendations to JSON"],
            files_affected=[{"file_path": output_file if output_file else "N/A", "change_type": "CREATED" if output_file else "NONE", "impact_level": "LOW"}],
            technical_decisions=["Report includes list of recommended indexes, reasons, scores, and suggested SQL commands"]
        )
        return report_data

# Example Usage
if __name__ == "__main__":
    recommender = SingleColumnIndexRecommender()
    
    # Sample data (simulating output from previous analyzer modules)
    query_id_1 = "sample_query_001"
    where_cols = {'users.status', 'orders.order_date'}
    join_cols = {'users.id', 'orders.user_id', 'order_items.order_id', 'products.id'}
    orderby_cols = {'orders.order_date', 'users.name'}
    groupby_cols = {'products.category'}
    all_ment_cols = where_cols.union(join_cols).union(orderby_cols).union(groupby_cols).union({'products.price', 'users.email'})

    print(f"--- Recommending indexes for Query: {query_id_1} ---")
    recommendations1 = recommender.recommend_indexes(
        query_id_1, 
        where_columns=where_cols,
        join_columns=join_cols,
        orderby_columns=orderby_cols,
        groupby_columns=groupby_cols,
        all_mentioned_columns=all_ment_cols
    )
    
    if recommendations1:
        print(f"\nRecommended single-column indexes for '{query_id_1}':")
        for rec in recommendations1:
            print(f"  - Column: {rec['column_name']}, Score: {rec['score']}, Reason: {rec['reason']}")
            print(f"    Suggested SQL: {rec['sql_command_suggestion']}")
    else:
        print(f"No single-column index recommendations for '{query_id_1}'.")
    recommender.generate_report(query_id_1, recommendations1, f"logs/index_recommendations_{query_id_1}.json")

    query_id_2 = "simple_select_no_filter"
    print(f"\n--- Recommending indexes for Query: {query_id_2} ---")
    recommendations2 = recommender.recommend_indexes(
        query_id_2,
        where_columns=set(),
        join_columns=set(),
        orderby_columns=set(),
        groupby_columns=set(),
        all_mentioned_columns={'customers.name', 'customers.email'}
    )
    if recommendations2:
        print(f"\nRecommended single-column indexes for '{query_id_2}':")
        for rec in recommendations2:
            print(f"  - Column: {rec['column_name']}, Score: {rec['score']}, Reason: {rec['reason']}")
    else:
        print(f"No single-column index recommendations for '{query_id_2}'.")
    recommender.generate_report(query_id_2, recommendations2, f"logs/index_recommendations_{query_id_2}.json")

