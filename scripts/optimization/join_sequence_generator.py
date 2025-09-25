#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Join Sequence Generator

This module generates an optimized join sequence for SQL queries based on
table dependencies and cardinality estimates.
It follows the mandatory changelog protocol.
"""

import logging
import json
import itertools
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import networkx as nx

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine
# Assuming TableDependencyAnalyzer and CardinalityEstimator might be used for inputs
# from scripts.optimization.table_dependency_analyzer import TableDependencyAnalyzer 
# from scripts.optimization.cardinality_estimator import CardinalityEstimator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/join_sequence_generator.log'
)
logger = logging.getLogger(__name__)

class JoinSequenceGenerator:
    """
    Generates an optimized join sequence using dependency and cardinality information.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the Join Sequence Generator."""
        self.changelog_engine = ChangelogEngine()
        self.generated_sequences = {}
        
        self._update_changelog(
            action_summary="JoinSequenceGenerator initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Generator ready to process join optimization requests",
            changes_made=["Initialized sequence storage"],
            files_affected=[{"file_path": "scripts/optimization/join_sequence_generator.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Will use cost-based approach (initially simple) to evaluate sequences"]
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

    def _estimate_join_cost(self, card1: int, card2: int, intermediate_card: int, join_type: str) -> float:
        """Estimates the cost of a single join operation.
        A simple cost model: sum of input cardinalities + output cardinality.
        More sophisticated models could include I/O, CPU costs, specific join algorithm costs.
        """
        # Basic cost: sum of rows processed by the join operator
        cost = float(card1 + card2 + intermediate_card)
        # Penalize cross joins heavily if not intended
        if join_type.upper() == "CROSS JOIN" and intermediate_card == card1 * card2:
            cost *= 10 # Arbitrary penalty factor
        return cost

    def generate_join_sequence(self, 
                               query_id: str, 
                               tables: List[str], 
                               join_graph: nx.Graph, 
                               cardinality_estimates: Dict[str, int], 
                               join_conditions: Dict[Tuple[str, str], str]) -> Optional[List[Dict[str, Any]]]:
        """Generates an optimized join sequence.
        Args:
            query_id (str): Identifier for the query.
            tables (List[str]): List of table names (or aliases representing them in estimates).
            join_graph (nx.Graph): Graph where nodes are tables and edges are possible joins.
                                   Edges should have 'condition' attribute from TableDependencyAnalyzer.
            cardinality_estimates (Dict[str, int]): Initial cardinality for each table.
                                                 And potentially for intermediate results if pre-calculated.
            join_conditions (Dict[Tuple[str, str], str]): Mapping from (table1, table2) pair to join condition string.
        Returns:
            Optional[List[Dict[str, Any]]]: The recommended sequence of join operations, or None if error.
        """
        if not tables or len(tables) < 2:
            logger.info(f"Query {query_id}: No joins needed for less than 2 tables. Tables: {tables}")
            self.generated_sequences[query_id] = {"tables": tables, "plan": [], "cost": 0.0}
            return []

        # For simplicity, this initial version will use a greedy approach.
        # Start with the smallest table or a table involved in a highly selective join.
        # This is a placeholder for more advanced algorithms (e.g., dynamic programming).

        current_plan = []
        remaining_tables = set(tables)
        current_joined_set = set()
        estimated_intermediate_cardinalities = dict(cardinality_estimates) # Copy initial table cardinalities
        total_estimated_cost = 0.0

        # Select a starting table (e.g., the one with the smallest initial cardinality)
        if not remaining_tables:
             logger.error(f"Query {query_id}: No tables left to start join sequence.")
             return None
        
        start_table = min(remaining_tables, key=lambda t: estimated_intermediate_cardinalities.get(t, float('inf')))
        current_joined_set.add(start_table)
        remaining_tables.remove(start_table)
        current_intermediate_name = start_table # Name of the current intermediate result set
        current_intermediate_card = estimated_intermediate_cardinalities[start_table]

        logger.info(f"Query {query_id}: Starting join sequence with table '{start_table}' (card: {current_intermediate_card})")

        while remaining_tables:
            best_next_join = None
            lowest_cost_for_step = float('inf')
            best_intermediate_card = float('inf')
            
            candidate_joins = []
            # Find all possible next joins from the current_joined_set to remaining_tables
            for table_in_set in current_joined_set:
                for next_table_to_join in remaining_tables:
                    # Check if a direct join edge exists in the provided graph
                    if join_graph.has_edge(table_in_set, next_table_to_join) or join_graph.has_edge(next_table_to_join, table_in_set):
                        edge_data = join_graph.get_edge_data(table_in_set, next_table_to_join) or join_graph.get_edge_data(next_table_to_join, table_in_set)
                        condition = edge_data.get('condition', 'UNKNOWN_CONDITION') # Get condition from graph
                        
                        # Use a placeholder for join type; this should be determined by JoinTypeRecommender or from query
                        # For now, assume INNER JOIN for cost estimation if a condition exists.
                        join_type_for_costing = "INNER JOIN" # This is a simplification
                        
                        # Simulate join and estimate cardinality (requires a call to a cardinality estimator method)
                        # This is a mock call - in a real system, this would use the CardinalityEstimator instance
                        # For now, let's use a very simplified heuristic for intermediate cardinality.
                        # card_next_table = estimated_intermediate_cardinalities.get(next_table_to_join, DEFAULT_TABLE_STATS['default_table']['row_count'])
                        # A more robust way: use the CardinalityEstimator's estimate_join_cardinality method.
                        # For this example, let's assume a fixed selectivity or a simple product reduction.
                        # This part needs proper integration with CardinalityEstimator.
                        # Simplified: product * small_factor or min if PK-FK (which we don't know here directly)
                        card_next_table = estimated_intermediate_cardinalities.get(next_table_to_join, 1000)
                        # Mocked intermediate cardinality for this example
                        # In a real scenario: call self.cardinality_estimator.estimate_join_cardinality(...)
                        temp_intermediate_card = min(current_intermediate_card, card_next_table) # Very naive for PK-FK like joins
                        if "CROSS JOIN" in condition.upper(): # Or if no condition implies cross join
                            temp_intermediate_card = current_intermediate_card * card_next_table
                            join_type_for_costing = "CROSS JOIN"
                        else: # Simplistic reduction for other joins
                            temp_intermediate_card = int(current_intermediate_card * card_next_table * 0.01) # Assume 1% selectivity
                        temp_intermediate_card = max(1, temp_intermediate_card)

                        cost = self._estimate_join_cost(current_intermediate_card, card_next_table, temp_intermediate_card, join_type_for_costing)
                        candidate_joins.append({
                            'from_intermediate': current_intermediate_name,
                            'join_with_table': next_table_to_join,
                            'on_condition': condition,
                            'estimated_cost': cost,
                            'resulting_cardinality': temp_intermediate_card,
                            'join_type': join_type_for_costing # This should be more accurately determined
                        })
            
            if not candidate_joins:
                # This might happen if the graph is disconnected and we've processed one component.
                # Or if the remaining_tables cannot be joined to current_joined_set based on join_graph.
                if remaining_tables:
                    logger.warning(f"Query {query_id}: No join path found from {current_joined_set} to {remaining_tables}. Graph might be disconnected.")
                    # Handle disconnected components: pick a new start_table from remaining_tables
                    # This part makes the greedy algorithm more complex if we want to bridge components optimally.
                    # For now, we'll stop or could start a new join tree if allowed.
                    # Let's assume for now the graph should be connected for a single join sequence.
                    # If it's not, the problem is more about finding optimal plans for each connected component.
                    # This simple greedy approach might fail here or produce sub-optimal results for disconnected graphs.
                    # We can just add remaining tables as cross joins if no other path, or error out.
                    logger.error(f"Query {query_id}: Cannot find next join. Graph may be disconnected or logic incomplete for this case.")
                    # Fallback: add remaining tables as cross joins (highly undesirable but completes the sequence)
                    # This is a poor fallback and should be improved with better graph traversal or error handling.
                    for table_to_cross_join in list(remaining_tables):
                        card_table_to_cross = estimated_intermediate_cardinalities.get(table_to_cross_join, 1000)
                        temp_intermediate_card = current_intermediate_card * card_table_to_cross
                        cost = self._estimate_join_cost(current_intermediate_card, card_table_to_cross, temp_intermediate_card, "CROSS JOIN")
                        op_name = f"{current_intermediate_name}_X_{table_to_cross_join}"
                        current_plan.append({
                            'step': len(current_plan) + 1,
                            'left_input': current_intermediate_name,
                            'right_input': table_to_cross_join,
                            'join_type': 'CROSS JOIN',
                            'condition': 'CROSS JOIN (fallback)',
                            'output_name': op_name,
                            'estimated_rows': temp_intermediate_card,
                            'estimated_cost': cost
                        })
                        total_estimated_cost += cost
                        current_intermediate_name = op_name
                        current_intermediate_card = temp_intermediate_card
                        remaining_tables.remove(table_to_cross_join)
                        current_joined_set.add(table_to_cross_join) # Add to set, though it's a cross join
                        logger.warning(f"Query {query_id}: Fallback - Added {table_to_cross_join} via CROSS JOIN.")
                    break # Exit main while loop after fallback cross joins
                else: # No candidates and no remaining tables, we are done.
                    break

            # Select the best join from candidates (lowest cost)
            best_next_join = min(candidate_joins, key=lambda x: x['estimated_cost'])
            
            # Perform the chosen join
            op_name = f"({best_next_join['from_intermediate']}_{best_next_join['join_with_table']})"
            current_plan.append({
                'step': len(current_plan) + 1,
                'left_input': best_next_join['from_intermediate'],
                'right_input': best_next_join['join_with_table'],
                'join_type': best_next_join['join_type'], # This needs to be accurate
                'condition': best_next_join['on_condition'],
                'output_name': op_name,
                'estimated_rows': best_next_join['resulting_cardinality'],
                'estimated_cost': best_next_join['estimated_cost']
            })
            total_estimated_cost += best_next_join['estimated_cost']
            
            logger.info(f"Query {query_id}: Step {len(current_plan)} - Joining '{best_next_join['from_intermediate']}' with '{best_next_join['join_with_table']}'. Cost: {best_next_join['estimated_cost']:.2f}, OutCard: {best_next_join['resulting_cardinality']}")

            current_intermediate_name = op_name
            current_intermediate_card = best_next_join['resulting_cardinality']
            # Update the set of joined tables and remove from remaining
            current_joined_set.add(best_next_join['join_with_table'])
            remaining_tables.remove(best_next_join['join_with_table'])
        
        self.generated_sequences[query_id] = {
            "query_id": query_id,
            "initial_tables": tables,
            "plan": current_plan,
            "total_estimated_cost": total_estimated_cost,
            "final_estimated_cardinality": current_intermediate_card
        }
        
        self._update_changelog(
            action_summary=f"Generated join sequence for query {query_id} with {len(current_plan)} steps.",
            action_type="Join Optimization",
            previous_state="Inputs (graph, cardinalities) received",
            current_state=f"Join plan generated for {query_id}",
            changes_made=["Applied greedy algorithm for join ordering", "Estimated costs for join steps"],
            files_affected=[{"file_path": "logs/join_sequence_generator.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=["Using a greedy approach based on minimizing immediate step cost", "Simplified cost model and intermediate cardinality estimation for initial version"]
        )
        return current_plan

    def generate_report(self, query_id: str, output_file: str = None) -> Optional[Dict[str, Any]]:
        """Generates a report for the generated join sequence of a query."""
        if query_id not in self.generated_sequences:
            logger.error(f"No join sequence found for query_id: {query_id}")
            return None
            
        report_data = self.generated_sequences[query_id]
        report_data["report_timestamp"] = datetime.now().isoformat()
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report_data, f, indent=4)
                logger.info(f"Generated join sequence report for {query_id} at {output_file}")
            except IOError as e:
                logger.error(f"Failed to write report to {output_file}: {e}")
        
        self._update_changelog(
            action_summary=f"Generated join sequence report for query {query_id}",
            action_type="Report Generation",
            previous_state=f"Join sequence for {query_id} generated",
            current_state=f"Report for {query_id} available",
            changes_made=["Serialized join plan and cost to JSON"],
            files_affected=[{"file_path": output_file if output_file else "N/A", "change_type": "CREATED" if output_file else "NONE", "impact_level": "LOW"}],
            technical_decisions=["Report includes the step-by-step plan and total estimated cost"]
        )
        return report_data

# Example Usage
if __name__ == "__main__":
    generator = JoinSequenceGenerator()

    # Mock data similar to what TableDependencyAnalyzer and CardinalityEstimator would provide
    mock_query_id = "sample_query1"
    mock_tables = ['customers', 'orders', 'order_items', 'products']
    
    # Mock join graph (edges should ideally have 'condition' attribute)
    mock_join_graph = nx.Graph()
    mock_join_graph.add_edge('customers', 'orders', condition='c.id = o.customer_id')
    mock_join_graph.add_edge('orders', 'order_items', condition='o.id = oi.order_id')
    mock_join_graph.add_edge('order_items', 'products', condition='oi.product_id = p.id')

    # Mock initial cardinality estimates for base tables
    mock_cardinalities = {
        'customers': 1000,
        'orders': 5000,
        'order_items': 20000,
        'products': 500
    }
    
    # Mock join conditions (could also be part of graph edge attributes)
    mock_join_conditions = {
        ('customers', 'orders'): 'customers.id = orders.customer_id',
        ('orders', 'order_items'): 'orders.id = order_items.order_id',
        ('order_items', 'products'): 'order_items.product_id = products.id'
    }

    logger.info("--- Running Example 1: Connected Graph ---")
    plan1 = generator.generate_join_sequence(mock_query_id, mock_tables, mock_join_graph, mock_cardinalities, mock_join_conditions)
    if plan1:
        print(f"\nGenerated Join Plan for {mock_query_id}:")
        for step in plan1:
            print(f"  Step {step['step']}: {step['left_input']} JOIN {step['right_input']} ON {step['condition']} -> {step['output_name']} (EstRows: {step['estimated_rows']}, Cost: {step['estimated_cost']:.2f})")
        generator.generate_report(mock_query_id, f"logs/join_sequence_{mock_query_id}.json")
    else:
        print(f"Could not generate plan for {mock_query_id}")

    # Example 2: Disconnected components (initially) - current greedy might struggle or cross join
    mock_query_id_2 = "sample_query_disconnected"
    mock_tables_2 = ['tableA', 'tableB', 'tableC', 'tableD']
    mock_join_graph_2 = nx.Graph()
    mock_join_graph_2.add_edge('tableA', 'tableB', condition='a.id = b.a_id') # Component 1
    mock_join_graph_2.add_edge('tableC', 'tableD', condition='c.id = d.c_id') # Component 2
    mock_cardinalities_2 = {'tableA': 100, 'tableB': 200, 'tableC': 50, 'tableD': 300}
    mock_join_conditions_2 = {
        ('tableA', 'tableB'): 'a.id = b.a_id',
        ('tableC', 'tableD'): 'c.id = d.c_id'
    }
    logger.info("--- Running Example 2: Disconnected Graph (expect fallback or partial plan) ---")
    # Note: The current simple greedy algorithm is not designed to optimally handle disconnected graphs
    # without a final cross join or more sophisticated component connection logic.
    # It will likely process one component and then might cross join the result with the other, or error if no path.
    plan2 = generator.generate_join_sequence(mock_query_id_2, mock_tables_2, mock_join_graph_2, mock_cardinalities_2, mock_join_conditions_2)
    if plan2:
        print(f"\nGenerated Join Plan for {mock_query_id_2}:")
        for step in plan2:
            print(f"  Step {step['step']}: {step['left_input']} JOIN {step['right_input']} ON {step['condition']} -> {step['output_name']} (EstRows: {step['estimated_rows']}, Cost: {step['estimated_cost']:.2f})")
        generator.generate_report(mock_query_id_2, f"logs/join_sequence_{mock_query_id_2}.json")
    else:
        print(f"Could not generate plan for {mock_query_id_2}")

    # Example 3: Single table (no joins)
    mock_query_id_3 = "sample_query_single_table"
    mock_tables_3 = ['singleTable']
    mock_join_graph_3 = nx.Graph()
    mock_join_graph_3.add_node('singleTable')
    mock_cardinalities_3 = {'singleTable': 10000}
    mock_join_conditions_3 = {}
    logger.info("--- Running Example 3: Single Table ---")
    plan3 = generator.generate_join_sequence(mock_query_id_3, mock_tables_3, mock_join_graph_3, mock_cardinalities_3, mock_join_conditions_3)
    if plan3 is not None: # Empty list is a valid plan for single table (no ops)
        print(f"\nGenerated Join Plan for {mock_query_id_3} (should be empty): {plan3}")
        generator.generate_report(mock_query_id_3, f"logs/join_sequence_{mock_query_id_3}.json")

