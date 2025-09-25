#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cardinality Estimator

This module estimates the number of rows (cardinality) for tables and
intermediate results in SQL queries. It's a key component for query optimization,
particularly for join ordering.
It follows the mandatory changelog protocol.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/cardinality_estimator.log'
)
logger = logging.getLogger(__name__)

# Placeholder for database statistics/metadata
# In a real system, this would be fetched from the database's system catalog
# or a dedicated statistics manager.
DEFAULT_TABLE_STATS = {
    "customers": {"row_count": 1000000, "avg_row_size": 150},
    "orders": {"row_count": 5000000, "avg_row_size": 100},
    "order_items": {"row_count": 20000000, "avg_row_size": 50},
    "products": {"row_count": 50000, "avg_row_size": 200},
    "employees": {"row_count": 10000, "avg_row_size": 180},
    "departments": {"row_count": 100, "avg_row_size": 80},
    "default_table": {"row_count": 100000, "avg_row_size": 100} # Fallback
}

# Default selectivity factors for common operations
# These are heuristics and can be refined with more sophisticated methods.
DEFAULT_SELECTIVITY = {
    "equality_unique": 0.0001,  # e.g., WHERE id = <value> (on unique key)
    "equality_non_unique": 0.1, # e.g., WHERE status = <value>
    "range_small": 0.05,        # e.g., WHERE date BETWEEN X AND Y (small range)
    "range_large": 0.3,         # e.g., WHERE amount > X (large range)
    "like_prefix": 0.05,        # e.g., WHERE name LIKE 'prefix%'
    "like_suffix_infix": 0.2,   # e.g., WHERE name LIKE '%suffix' or '%infix%'
    "default_filter": 0.25      # Fallback selectivity for unknown filters
}

class CardinalityEstimator:
    """
    Estimates cardinality for SQL query components.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self, table_stats: Optional[Dict[str, Dict[str, Union[int, float]]]] = None):
        """Initialize the cardinality estimator."""
        self.changelog_engine = ChangelogEngine()
        self.table_stats = table_stats if table_stats else DEFAULT_TABLE_STATS
        self.estimations = {}
        
        self._update_changelog(
            action_summary="CardinalityEstimator initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Estimator ready for queries",
            changes_made=["Initialized with default table statistics and selectivity factors"],
            files_affected=[{"file_path": "scripts/optimization/cardinality_estimator.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Using heuristic-based selectivity for initial implementation", "Allowing custom table statistics"]
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

    def get_table_cardinality(self, table_name: str) -> int:
        """Get the base cardinality (row count) for a table."""
        # Normalize table name (e.g., schema.table -> table)
        normalized_name = table_name.split('.')[-1].lower()
        stats = self.table_stats.get(normalized_name, self.table_stats["default_table"])
        return stats.get("row_count", self.table_stats["default_table"]["row_count"])

    def estimate_selectivity(self, filter_condition: str, table_name: str) -> float:
        """Estimate the selectivity of a filter condition.
           This is a highly simplified heuristic approach.
        Args:
            filter_condition (str): The filter condition string (e.g., "age > 30", "status = 'active'").
            table_name (str): The name of the table the filter applies to.
        Returns:
            float: Estimated selectivity (0.0 to 1.0).
        """
        condition_lower = filter_condition.lower()
        
        # Basic equality on a unique key (heuristic: assume column name 'id' or 'pk')
        if re.search(r'\b(?:id|pk)\b\s*=\s*\S+', condition_lower):
            # More accurately, check if it's a primary/unique key for that table
            # For now, a simple heuristic
            base_card = self.get_table_cardinality(table_name)
            return 1.0 / base_card if base_card > 0 else DEFAULT_SELECTIVITY["equality_unique"]
        
        if '=' in condition_lower:
            return DEFAULT_SELECTIVITY["equality_non_unique"]
        if '>' in condition_lower or '<' in condition_lower:
            # Could differentiate between small/large range based on constants or column stats
            return DEFAULT_SELECTIVITY["range_small"] 
        if 'like' in condition_lower:
            if condition_lower.endswith("%"):
                return DEFAULT_SELECTIVITY["like_prefix"]
            else:
                return DEFAULT_SELECTIVITY["like_suffix_infix"]
        if 'between' in condition_lower:
            return DEFAULT_SELECTIVITY["range_small"]
        if 'in (' in condition_lower:
            # Count items in IN list, relate to distinct values in column
            num_items = condition_lower.count(',') + 1
            return min(1.0, num_items * DEFAULT_SELECTIVITY["equality_non_unique"])
            
        return DEFAULT_SELECTIVITY["default_filter"]

    def estimate_filter_cardinality(self, table_name: str, filter_conditions: List[str]) -> int:
        """Estimate cardinality after applying filter conditions."""
        base_cardinality = self.get_table_cardinality(table_name)
        cumulative_selectivity = 1.0
        
        # Assume independence of filter conditions for simplicity
        for condition in filter_conditions:
            selectivity = self.estimate_selectivity(condition, table_name)
            cumulative_selectivity *= selectivity
            
        estimated_card = int(base_cardinality * cumulative_selectivity)
        logger.info(f"Estimating filter cardinality for {table_name}: base={base_cardinality}, filters={filter_conditions}, selectivity={cumulative_selectivity:.4f}, estimated={estimated_card}")
        return max(1, estimated_card) # Cardinality is at least 1

    def estimate_join_cardinality(self, card1: int, card2: int, join_type: str, join_condition: str, 
                                  table1_name: str, table2_name: str) -> int:
        """Estimate cardinality of a join operation.
           This is a simplified model.
        Args:
            card1 (int): Cardinality of the first table/intermediate result.
            card2 (int): Cardinality of the second table/intermediate result.
            join_type (str): Type of join (e.g., INNER, LEFT, RIGHT, FULL, CROSS).
            join_condition (str): The join condition string.
            table1_name (str): Name of the first table in the join.
            table2_name (str): Name of the second table in the join.
        Returns:
            int: Estimated cardinality of the join result.
        """
        join_type_upper = join_type.upper()
        
        if join_type_upper == "CROSS JOIN" or not join_condition:
            return card1 * card2

        # For simplicity, assume join condition is on foreign key to primary key (many-to-one)
        # Selectivity of join: 1 / max(distinct_values(PK_col_T1), distinct_values(PK_col_T2))
        # If PK from T1 joins FK from T2, then each row in T2 matches on average 1 row in T1.
        # Result size is roughly card(T2) if T2 is the 'many' side.
        # This requires column-level statistics (distinct values, histograms) which we don't have yet.
        
        # Simplified heuristic for INNER JOIN:
        # Assume one table is 'smaller' (e.g., dimension) and other is 'larger' (e.g., fact)
        # The result size is often bounded by the smaller of the two inputs, or a fraction of the larger.
        # Or, if it's a PK-FK join, it's often card(FK_table).
        # Let's use a very rough heuristic: min(card1, card2) for many-to-one, or a fraction of product for many-to-many.

        # Heuristic: Assume join selectivity factor (e.g., 0.1 for typical non-unique joins)
        # This is a placeholder for a more sophisticated model using distinct value counts.
        join_selectivity_factor = 0.01 # Highly dependent on actual data and schema
        
        # Try to infer PK-FK relationship based on typical naming (e.g., table1.id = table2.table1_id)
        pk_fk_match = re.search(fr'{re.escape(table1_name)}\.id\s*=\s*{re.escape(table2_name)}\.{re.escape(table1_name)}_id', join_condition, re.IGNORECASE) or \
                      re.search(fr'{re.escape(table2_name)}\.id\s*=\s*{re.escape(table1_name)}\.{re.escape(table2_name)}_id', join_condition, re.IGNORECASE)
        
        estimated_card = 0
        if join_type_upper == "INNER JOIN":
            if pk_fk_match: # Likely PK-FK join
                # If table1.id = table2.table1_id, then card is likely card2
                # If table2.id = table1.table2_id, then card is likely card1
                # This is still a simplification as it doesn't account for unmatched rows.
                # Let's assume the cardinality of the table with the foreign key.
                if f"{table1_name}.id" in join_condition.lower(): # table1 is PK side
                    estimated_card = card2
                else: # table2 is PK side
                    estimated_card = card1
            else: # Non-PK-FK or more complex join
                estimated_card = int(card1 * card2 * join_selectivity_factor)
        elif join_type_upper == "LEFT JOIN":
            # At least card1 rows, potentially more if one-to-many from left to right
            # Simplified: card1 + (card2 * join_selectivity_factor if not PK-FK on right)
            estimated_card = card1 # Base for LEFT JOIN
            if not pk_fk_match or f"{table2_name}.id" in join_condition.lower(): # if right table is not joined on its PK
                 estimated_card = int(card1 + card1 * (card2 / self.get_table_cardinality(table2_name) if self.get_table_cardinality(table2_name) > 0 else 1) * 0.1) # small growth factor
        elif join_type_upper == "RIGHT JOIN":
            estimated_card = card2
            if not pk_fk_match or f"{table1_name}.id" in join_condition.lower():
                 estimated_card = int(card2 + card2 * (card1 / self.get_table_cardinality(table1_name) if self.get_table_cardinality(table1_name) > 0 else 1) * 0.1)
        elif join_type_upper == "FULL JOIN":
            # Max of left and right join estimates (very rough)
            est_left = int(card1 + card1 * (card2 / self.get_table_cardinality(table2_name) if self.get_table_cardinality(table2_name) > 0 else 1) * 0.1)
            est_right = int(card2 + card2 * (card1 / self.get_table_cardinality(table1_name) if self.get_table_cardinality(table1_name) > 0 else 1) * 0.1)
            estimated_card = max(est_left, est_right, int(card1 * card2 * join_selectivity_factor))
        else:
            estimated_card = card1 * card2 # Fallback to cross product size

        logger.info(f"Estimating join: {table1_name}({card1}) {join_type} {table2_name}({card2}) ON {join_condition} -> Estimated: {max(1, estimated_card)}")
        return max(1, estimated_card) # Cardinality is at least 1

    def estimate_query_plan_cardinality(self, query_plan: List[Dict[str, Any]]) -> Dict[str, int]:
        """Estimate cardinality for each step in a simplified query plan.
        A query plan step could be: 
        {'type': 'scan', 'table': 'customers', 'filters': ['age > 30']}
        {'type': 'join', 'left_input_ref': 'step1_id', 'right_input_ref': 'step2_id', 
         'join_type': 'INNER', 'condition': 't1.id = t2.customer_id', 'left_table_name':'customers', 'right_table_name':'orders'}
        """
        step_cardinalities = {}
        
        for i, step in enumerate(query_plan):
            step_id = step.get('id', f"step_{i}")
            step_type = step.get('type')
            estimated_card = 0
            
            if step_type == 'scan':
                table_name = step['table']
                filters = step.get('filters', [])
                estimated_card = self.estimate_filter_cardinality(table_name, filters)
            elif step_type == 'join':
                left_ref = step['left_input_ref']
                right_ref = step['right_input_ref']
                card1 = step_cardinalities.get(left_ref, self.table_stats["default_table"]["row_count"])
                card2 = step_cardinalities.get(right_ref, self.table_stats["default_table"]["row_count"])
                join_type = step['join_type']
                condition = step['condition']
                left_table_name = step['left_table_name'] # Name of original table for left input
                right_table_name = step['right_table_name'] # Name of original table for right input
                estimated_card = self.estimate_join_cardinality(card1, card2, join_type, condition, left_table_name, right_table_name)
            else:
                logger.warning(f"Unknown step type: {step_type} in query plan. Cannot estimate.")
                estimated_card = self.table_stats["default_table"]["row_count"] # Fallback
                
            step_cardinalities[step_id] = estimated_card
            self.estimations[step_id] = {
                "step_info": step,
                "estimated_cardinality": estimated_card,
                "timestamp": datetime.now().isoformat()
            }
            
        self._update_changelog(
            action_summary=f"Estimated cardinalities for a query plan with {len(query_plan)} steps",
            action_type="Cardinality Estimation",
            previous_state="Estimator idle or processing other plans",
            current_state=f"Cardinalities estimated for plan",
            changes_made=["Processed each plan step", "Applied filter and join estimation logic"],
            files_affected=[{"file_path": "logs/cardinality_estimator.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=["Iterative estimation through plan steps", "Storing intermediate results"]
        )
        return step_cardinalities

    def generate_report(self, query_id: str, output_file: str = None) -> Dict[str, Any]:
        """Generates a report of all estimations made for a query or plan."""
        # This report structure might need to be adapted based on how estimations are grouped (e.g., per query_id)
        # For now, it reports all stored estimations.
        report = {
            "report_id": query_id, # Assuming query_id is used to group estimations
            "timestamp": datetime.now().isoformat(),
            "table_statistics_used": self.table_stats,
            "default_selectivity_factors": DEFAULT_SELECTIVITY,
            "estimations": self.estimations # This will grow with each call to estimate_query_plan_cardinality
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=4)
                logger.info(f"Generated cardinality estimation report for {query_id} at {output_file}")
            except IOError as e:
                logger.error(f"Failed to write report to {output_file}: {e}")
        
        self._update_changelog(
            action_summary=f"Generated cardinality report for {query_id}",
            action_type="Report Generation",
            previous_state="Estimations complete",
            current_state=f"Report for {query_id} available",
            changes_made=["Serialized estimation data to JSON"],
            files_affected=[{"file_path": output_file if output_file else "N/A", "change_type": "CREATED" if output_file else "NONE", "impact_level": "LOW"}],
            technical_decisions=["Report includes inputs (stats, selectivity) and outputs (estimations)"]
        )
        return report

# Example Usage
if __name__ == "__main__":
    estimator = CardinalityEstimator()

    # Example 1: Filter estimation
    print(f"Customers table cardinality: {estimator.get_table_cardinality('customers')}")
    est_card_filter = estimator.estimate_filter_cardinality('customers', ["country = 'USA'", "age > 30"])
    print(f"Estimated cardinality for filtered customers: {est_card_filter}")

    # Example 2: Join estimation
    card_orders = estimator.get_table_cardinality('orders')
    card_customers = estimator.get_table_cardinality('customers')
    est_card_join = estimator.estimate_join_cardinality(
        card_customers, card_orders, 
        'INNER JOIN', 'customers.id = orders.customer_id',
        'customers', 'orders'
    )
    print(f"Estimated cardinality for customers INNER JOIN orders: {est_card_join}")

    # Example 3: Query Plan Estimation
    sample_plan = [
        {'id': 'scan_cust', 'type': 'scan', 'table': 'customers', 'filters': ["zip_code LIKE '90%'"], 'table_name': 'customers'},
        {'id': 'scan_orders', 'type': 'scan', 'table': 'orders', 'filters': [], 'table_name': 'orders'},
        {'id': 'join_cust_orders', 'type': 'join', 
         'left_input_ref': 'scan_cust', 'right_input_ref': 'scan_orders', 
         'join_type': 'INNER', 'condition': 'customers.id = orders.customer_id',
         'left_table_name': 'customers', 'right_table_name': 'orders'},
        {'id': 'scan_items', 'type': 'scan', 'table': 'order_items', 'filters': [], 'table_name': 'order_items'},
        {'id': 'join_all', 'type': 'join', 
         'left_input_ref': 'join_cust_orders', 'right_input_ref': 'scan_items',
         'join_type': 'LEFT JOIN', 'condition': 'orders.id = order_items.order_id',
         'left_table_name': 'orders', # This should ideally be the alias/name from previous step
         'right_table_name': 'order_items'}
    ]
    
    plan_cardinalities = estimator.estimate_query_plan_cardinality(sample_plan)
    print("\nQuery Plan Cardinality Estimations:")
    for step_id, card in plan_cardinalities.items():
        print(f"  Step '{step_id}': Estimated Cardinality = {card}")
        
    estimator.generate_report("sample_query_plan_1", "logs/cardinality_report_plan1.json")

    # Example with a table not in default stats
    print(f"\nUnknown table cardinality: {estimator.get_table_cardinality('unknown_table')}")
    est_card_unknown_filter = estimator.estimate_filter_cardinality('unknown_table', ["col1 = 'X'"])
    print(f"Estimated cardinality for filtered unknown_table: {est_card_unknown_filter}")
