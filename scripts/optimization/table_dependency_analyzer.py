#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Table Dependency Analyzer

This module analyzes table dependencies in SQL queries to optimize join ordering.
It follows the mandatory changelog protocol.
"""

import logging
import json
import re
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
import networkx as nx

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/table_dependency_analyzer.log'
)
logger = logging.getLogger(__name__)

class TableDependencyAnalyzer:
    """
    Analyzes table dependencies in SQL queries to optimize join ordering.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the table dependency analyzer with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.dependency_graphs = {}
        self.query_tables_info = {}
        
        self._update_changelog(
            action_summary="TableDependencyAnalyzer initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Analyzer ready for queries",
            changes_made=["Initialized dependency graph storage"],
            files_affected=[{"file_path": "scripts/optimization/table_dependency_analyzer.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Using networkx for graph representation of dependencies"]
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

    def _extract_tables_and_aliases(self, sql_query: str) -> Dict[str, str]:
        """Extracts tables and their aliases from FROM and JOIN clauses."""
        tables_with_aliases = {}
        # Regex to find tables and aliases in FROM and JOIN clauses
        # Supports 'table_name alias', 'table_name AS alias', 'table_name'
        pattern = re.compile(
            r'\b(?:FROM|JOIN)\s+([\w.]+)(?:\s+AS\s+|\s+)([\w]+)|\b(?:FROM|JOIN)\s+([\w.]+)(?!\s*\()',
            re.IGNORECASE
        )
        matches = pattern.findall(sql_query)
        for match in matches:
            if match[0] and match[1]: # table_name alias / table_name AS alias
                tables_with_aliases[match[1]] = match[0]
            elif match[2]: # table_name (no alias)
                table_name = match[2]
                # Use table name as alias if no alias is present
                if '.' in table_name: # schema.table
                    actual_name = table_name.split('.')[-1]
                    tables_with_aliases[actual_name] = table_name
                else:
                    tables_with_aliases[table_name] = table_name
        logger.info(f"Extracted tables and aliases: {tables_with_aliases}")
        return tables_with_aliases

    def _extract_join_conditions(self, sql_query: str, tables_with_aliases: Dict[str, str]) -> List[Tuple[str, str, str]]:
        """Extracts join conditions from WHERE and ON clauses."""
        join_conditions = [] 
        # Regex to find join conditions like 'alias1.column = alias2.column'
        # This is a simplified regex and might need to be more robust for complex queries
        pattern = re.compile(r'([\w]+)\.([\w]+)\s*=\s*([\w]+)\.([\w]+)', re.IGNORECASE)
        matches = pattern.findall(sql_query)
        for match in matches:
            alias1, col1, alias2, col2 = match
            if alias1 in tables_with_aliases and alias2 in tables_with_aliases:
                # Ensure we are linking actual table names if aliases are used
                table1 = tables_with_aliases[alias1]
                table2 = tables_with_aliases[alias2]
                if table1 != table2: # Avoid self-joins for this basic dependency analysis
                    join_conditions.append((table1, table2, f"{alias1}.{col1} = {alias2}.{col2}"))
        logger.info(f"Extracted join conditions: {join_conditions}")
        return join_conditions

    def analyze_query(self, query_id: str, sql_query: str) -> None:
        """Analyzes a SQL query to build a table dependency graph."""
        logger.info(f"Analyzing query_id: {query_id}")
        tables_with_aliases = self._extract_tables_and_aliases(sql_query)
        join_conditions = self._extract_join_conditions(sql_query, tables_with_aliases)
        
        self.query_tables_info[query_id] = {
            'aliases': tables_with_aliases,
            'tables': list(set(tables_with_aliases.values())),
            'join_conditions': join_conditions
        }
        
        graph = nx.Graph()
        for table_alias, table_name in tables_with_aliases.items():
            graph.add_node(table_name) # Use actual table name for nodes
            
        for table1, table2, condition_detail in join_conditions:
            graph.add_edge(table1, table2, condition=condition_detail)
            
        self.dependency_graphs[query_id] = graph
        logger.info(f"Built dependency graph for query_id {query_id}: Nodes={graph.nodes()}, Edges={graph.edges(data=True)}")
        
        self._update_changelog(
            action_summary=f"Analyzed query {query_id} and built dependency graph",
            action_type="Query Analysis",
            previous_state="Analyzer idle or processing other queries",
            current_state=f"Dependency graph for {query_id} created",
            changes_made=["Parsed SQL for tables and joins", "Constructed graph representation"],
            files_affected=[{"file_path": "logs/table_dependency_analyzer.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=["Used regex for table/join extraction (acknowledging limitations)", "Represented dependencies as an undirected graph"]
        )

    def get_join_order_recommendation(self, query_id: str) -> List[str]:
        """Recommends a join order based on the dependency graph.
           This is a simplified example; real-world scenarios need cardinality, costs, etc.
        """
        if query_id not in self.dependency_graphs:
            logger.error(f"No dependency graph found for query_id: {query_id}")
            return []
            
        graph = self.dependency_graphs[query_id]
        if not graph.nodes():
            logger.info(f"Graph for {query_id} has no nodes.")
            return []
        if not graph.edges():
            logger.info(f"Graph for {query_id} has nodes but no edges (no explicit joins found or single table).")
            return list(graph.nodes()) # Return the single table if no joins

        # Simple strategy: Start with the node with the most connections (naive)
        # A more robust strategy would involve cardinality estimation, cost models, etc.
        # For a connected graph, a traversal (like BFS or DFS) can give an order.
        # If the graph is not connected (multiple join groups), process each component.
        
        ordered_tables = []
        visited_edges = set()
        
        # Prioritize tables involved in more join conditions first (simple heuristic)
        # This doesn't guarantee optimality but provides a starting point.
        sorted_nodes = sorted(graph.degree, key=lambda item: item[1], reverse=True)
        
        if not sorted_nodes:
            return []

        # Start traversal from a high-degree node
        # This is a placeholder for a more sophisticated algorithm
        # For now, let's try a BFS-like approach to get a sequence
        start_node = sorted_nodes[0][0]
        queue = [(start_node, None)] # (current_node, joined_from_node)
        visited_nodes = {start_node}
        processed_joins = []

        temp_ordered_tables = [start_node]

        while queue:
            current_table, _ = queue.pop(0)
            for neighbor in graph.neighbors(current_table):
                if neighbor not in visited_nodes:
                    visited_nodes.add(neighbor)
                    temp_ordered_tables.append(neighbor)
                    queue.append((neighbor, current_table))
                    # Find the edge detail
                    edge_data = graph.get_edge_data(current_table, neighbor)
                    if edge_data:
                        processed_joins.append(f"{current_table} JOIN {neighbor} ON {edge_data.get('condition', 'condition_unavailable')}")
        
        # This is a very naive ordering. True join ordering is NP-hard.
        # We are just returning a sequence of tables based on BFS traversal.
        logger.info(f"Recommended join order for {query_id}: {temp_ordered_tables}")
        logger.info(f"Processed joins in order for {query_id}: {processed_joins}")
        
        # Store this naive order for reporting
        self.query_tables_info[query_id]['naive_join_order'] = temp_ordered_tables
        self.query_tables_info[query_id]['processed_join_sequence'] = processed_joins

        return temp_ordered_tables

    def generate_report(self, query_id: str, output_file: str = None) -> Dict[str, Any]:
        """Generates a report for the analyzed query."""
        if query_id not in self.dependency_graphs or query_id not in self.query_tables_info:
            logger.error(f"No analysis data found for query_id: {query_id}")
            return {}
            
        graph = self.dependency_graphs[query_id]
        query_info = self.query_tables_info[query_id]
        
        report = {
            "query_id": query_id,
            "timestamp": datetime.now().isoformat(),
            "tables_involved": query_info.get('tables', []) ,
            "aliases_used": query_info.get('aliases', {}),
            "join_conditions_found": query_info.get('join_conditions', []),
            "dependency_graph": {
                "nodes": list(graph.nodes()),
                "edges": list(graph.edges(data=True))
            },
            "naive_join_order_recommendation": query_info.get('naive_join_order', [])
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=4)
                logger.info(f"Generated report for {query_id} at {output_file}")
            except IOError as e:
                logger.error(f"Failed to write report to {output_file}: {e}")
        
        self._update_changelog(
            action_summary=f"Generated dependency report for query {query_id}",
            action_type="Report Generation",
            previous_state=f"Analysis complete for {query_id}",
            current_state=f"Report for {query_id} available",
            changes_made=["Serialized analysis data to JSON format"],
            files_affected=[{"file_path": output_file if output_file else "N/A", "change_type": "CREATED" if output_file else "NONE", "impact_level": "LOW"}],
            technical_decisions=["Report includes graph structure and naive join order"]
        )
        return report

# Example usage
if __name__ == "__main__":
    analyzer = TableDependencyAnalyzer()
    
    sample_query_1 = """
    SELECT c.name, o.order_date, p.product_name
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    WHERE c.city = 'New York';
    """
    analyzer.analyze_query("query1", sample_query_1)
    recommended_order_1 = analyzer.get_join_order_recommendation("query1")
    print(f"Recommended join order for query1: {recommended_order_1}")
    analyzer.generate_report("query1", "logs/dependency_report_query1.json")

    sample_query_2 = """
    SELECT e.name, d.department_name, m.name AS manager_name
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    LEFT JOIN employees m ON e.manager_id = m.id;
    """
    analyzer.analyze_query("query2", sample_query_2)
    recommended_order_2 = analyzer.get_join_order_recommendation("query2")
    print(f"Recommended join order for query2: {recommended_order_2}")
    analyzer.generate_report("query2", "logs/dependency_report_query2.json")

    sample_query_3 = "SELECT * FROM single_table;"
    analyzer.analyze_query("query3", sample_query_3)
    recommended_order_3 = analyzer.get_join_order_recommendation("query3")
    print(f"Recommended join order for query3: {recommended_order_3}")
    analyzer.generate_report("query3", "logs/dependency_report_query3.json")

    sample_query_4 = "SELECT t1.*, t2.* FROM table1 t1, table2 t2 WHERE t1.id = t2.t1_id AND t2.value > 100;"
    analyzer.analyze_query("query4", sample_query_4)
    recommended_order_4 = analyzer.get_join_order_recommendation("query4")
    print(f"Recommended join order for query4: {recommended_order_4}")
    analyzer.generate_report("query4", "logs/dependency_report_query4.json")

    # Query with schema.table format
    sample_query_5 = """
    SELECT u.username, p.profile_data
    FROM app_schema.users u
    JOIN app_schema.profiles p ON u.user_id = p.user_id
    WHERE u.status = 'active';
    """
    analyzer.analyze_query("query5", sample_query_5)
    recommended_order_5 = analyzer.get_join_order_recommendation("query5")
    print(f"Recommended join order for query5: {recommended_order_5}")
    analyzer.generate_report("query5", "logs/dependency_report_query5.json")
