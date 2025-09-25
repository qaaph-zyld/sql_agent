#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Index Impact Estimator Module

This module provides functionality to estimate the potential impact (benefits and drawbacks)
of creating a database index.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional

# Configure logging
logger = logging.getLogger(__name__)

class IndexImpactEstimator:
    """
    Estimates the impact of a potential database index.
    """

    def __init__(self, db_connector: Optional[Any] = None, schema_info: Optional[Dict[str, Any]] = None):
        """
        Initializes the IndexImpactEstimator.

        Args:
            db_connector: An optional database connector instance (for future use, e.g., EXPLAIN plans).
            schema_info: An optional dictionary containing schema information (e.g., table sizes, column cardinalities).
        """
        self.db_connector = db_connector
        self.schema_info = schema_info if schema_info else {}
        logger.info("IndexImpactEstimator initialized.")

    def estimate_impact(
        self,
        table_name: str,
        index_columns: List[str],
        query_patterns: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[float, str, Dict[str, Any]]:
        """
        Estimates the impact of a given index on a table, considering query patterns.

        Args:
            table_name (str): The name of the table the index would be on.
            index_columns (List[str]): A list of column names included in the index.
            query_patterns (Optional[List[Dict[str, Any]]]): A list of query patterns that might benefit
                                                            or be affected by this index. Each pattern could specify
                                                            type (SELECT, UPDATE), involved columns, clauses (WHERE, JOIN, ORDER BY).

        Returns:
            Tuple[float, str, Dict[str, Any]]:
                - score (float): A numeric score representing the estimated impact. 
                                 Positive for beneficial, negative for detrimental. Higher absolute value means stronger impact.
                - assessment (str): A qualitative assessment (e.g., "High positive impact", "Moderate overhead").
                - details (Dict[str, Any]): A dictionary containing breakdown of contributing factors.
        """
        if not table_name or not index_columns:
            logger.warning("Table name and index columns must be provided for impact estimation.")
            return 0.0, "Insufficient data", {"error": "Table name and index columns are required."}

        score = 0.0
        positive_factors = []
        negative_factors = []

        # Heuristic 1: Number of columns in index (more columns can mean more overhead for writes/storage)
        # but also better for covering queries.
        # For simplicity, let's penalize very wide indexes slightly.
        if len(index_columns) > 3:
            score -= (len(index_columns) - 3) * 0.5
            negative_factors.append(f"Index has {len(index_columns)} columns (potential overhead for wide index).")
        elif len(index_columns) == 1:
            positive_factors.append(f"Single-column index on '{index_columns[0]}'.")
        else:
            positive_factors.append(f"Composite index with {len(index_columns)} columns.")

        # Heuristic 2: Query pattern analysis (simplified)
        # This would be more sophisticated with actual query analysis data.
        # For now, a placeholder for how query patterns might influence the score.
        if query_patterns:
            for pattern in query_patterns:
                # Example: If index columns are used in WHERE clauses of frequent SELECTs
                if pattern.get("type") == "SELECT" and pattern.get("clause") == "WHERE":
                    used_in_where = any(col in pattern.get("columns", []) for col in index_columns)
                    if used_in_where:
                        score += 1.0 # Arbitrary positive score
                        positive_factors.append(f"Index columns used in WHERE clause of a SELECT pattern.")
                
                # Example: If index is on a table that's frequently updated (potential write overhead)
                if pattern.get("type") in ["UPDATE", "INSERT", "DELETE"] and pattern.get("table") == table_name:
                    score -= 0.5 # Arbitrary negative score for updates on indexed table
                    negative_factors.append(f"Index on frequently modified table '{table_name}'.")

        # Heuristic 3: Table size (row count)
        table_stats = self.schema_info.get("tables", {}).get(table_name, {})
        row_count = table_stats.get("row_count") # Could be None if not available

        if row_count is not None:
            if row_count < 1000:
                score -= 0.5  # Less benefit for very small tables
                negative_factors.append(f"Table '{table_name}' is small ({row_count} rows), index benefit may be limited.")
            elif row_count > 1000000: # Large table
                # For large tables, a good index can be very beneficial, but a bad one can be costly.
                # This factor's contribution could be refined based on selectivity, etc.
                # For now, let's assume a generally positive lean if other factors are good.
                score += 0.5 
                positive_factors.append(f"Table '{table_name}' is large ({row_count} rows), a good index can be impactful.")
        else:
            negative_factors.append(f"Row count for table '{table_name}' not available in schema_info.")

        assessment = "Neutral impact"
        if score > 1.5:
            assessment = "High positive impact"
        elif score > 0.5:
            assessment = "Moderate positive impact"
        elif score < -1.5:
            assessment = "High potential overhead"
        elif score < -0.5:
            assessment = "Moderate potential overhead"
        
        details = {
            "final_score": score,
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "index_definition": {"table": table_name, "columns": index_columns}
        }

        logger.info(f"Estimated impact for index on {table_name}({', '.join(index_columns)}): Score={score}, Assessment='{assessment}'")
        return score, assessment, details

if __name__ == '__main__':
    # Basic configuration for logging (if run directly)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Mock schema_info for testing
    mock_schema_info_for_estimator = {
        "tables": {
            "Users": {"row_count": 500},
            "Orders": {"row_count": 1500000},
            "Products": {"row_count": 10000},
            "Inventory": {"row_count": 200000} # No explicit update pattern for Inventory in ex4, so size matters
        }
    }
    estimator = IndexImpactEstimator(schema_info=mock_schema_info_for_estimator)

    # Example 1: Simple index, no query patterns
    score1, assessment1, details1 = estimator.estimate_impact("Users", ["username"])
    print(f"\nExample 1: Index Users(username)")
    print(f"  Score: {score1}, Assessment: {assessment1}")
    print(f"  Details: {details1}")

    # Example 2: Composite index, with some mock query patterns
    mock_patterns = [
        {"type": "SELECT", "table": "Orders", "clause": "WHERE", "columns": ["customer_id", "order_date"]},
        {"type": "SELECT", "table": "Orders", "clause": "ORDER BY", "columns": ["order_date"]},
        {"type": "UPDATE", "table": "Orders"} # Frequent updates to Orders table
    ]
    score2, assessment2, details2 = estimator.estimate_impact("Orders", ["customer_id", "order_date"], query_patterns=mock_patterns)
    print(f"\nExample 2: Index Orders(customer_id, order_date)")
    print(f"  Score: {score2}, Assessment: {assessment2}")
    print(f"  Details: {details2}")

    # Example 3: Wide index
    score3, assessment3, details3 = estimator.estimate_impact("Products", ["name", "category", "supplier_id", "price", "description"])
    print(f"\nExample 3: Wide Index Products(name, category, supplier_id, price, description)")
    print(f"  Score: {score3}, Assessment: {assessment3}")
    print(f"  Details: {details3}")

    # Example 4: Index on a table assumed to be frequently updated by one of the patterns
    score4, assessment4, details4 = estimator.estimate_impact("Inventory", ["product_id"], query_patterns=[{"type": "UPDATE", "table": "Inventory"}])
    print(f"\nExample 4: Index Inventory(product_id) with updates")
    print(f"  Score: {score4}, Assessment: {assessment4}")
    print(f"  Details: {details4}")

