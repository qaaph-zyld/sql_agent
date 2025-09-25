"""
Custom Query Analyzer

This script analyzes custom SQL queries to extract additional information about
table relationships, business processes, and data flows in the QADEE2798 database.
It enhances the existing database documentation with insights from custom queries.
"""

import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import logging
from pathlib import Path
import sqlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("custom_query_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database documentation directory
DB_DOCS_DIR = os.path.join("Database_tables", "QADEE2798")
CUSTOM_QUERIES_DIR = os.path.join(DB_DOCS_DIR, "custom_sql_queries")

def extract_tables_from_query(sql_query):
    """
    Extract table names from a SQL query
    
    Args:
        sql_query: SQL query string
        
    Returns:
        List of table names
    """
    # Parse the SQL query
    parsed = sqlparse.parse(sql_query)
    
    # Extract table names using regex
    tables = []
    
    # Pattern for table names in FROM and JOIN clauses
    from_pattern = r'FROM\s+\[?(\w+)\]?\.\[?(\w+)\]?\.\[?(\w+)\]?'
    join_pattern = r'JOIN\s+\[?(\w+)\]?\.\[?(\w+)\]?\.\[?(\w+)\]?'
    
    # Find all matches
    from_matches = re.finditer(from_pattern, sql_query, re.IGNORECASE)
    join_matches = re.finditer(join_pattern, sql_query, re.IGNORECASE)
    
    # Extract table names from FROM clauses
    for match in from_matches:
        if match.group(3):
            tables.append(match.group(3))
    
    # Extract table names from JOIN clauses
    for match in join_matches:
        if match.group(3):
            tables.append(match.group(3))
    
    # Remove duplicates
    tables = list(set(tables))
    
    return tables

def extract_relationships_from_query(sql_query):
    """
    Extract table relationships from a SQL query
    
    Args:
        sql_query: SQL query string
        
    Returns:
        List of relationships (source_table, target_table, join_condition)
    """
    # Parse the SQL query
    parsed = sqlparse.parse(sql_query)
    
    # Extract join conditions using regex
    relationships = []
    
    # Pattern for join conditions
    join_pattern = r'JOIN\s+\[?(\w+)\]?\.\[?(\w+)\]?\.\[?(\w+)\]?\s+(?:AS\s+(\w+))?\s+ON\s+(.+?)(?:WHERE|GROUP BY|ORDER BY|JOIN|UNION|$)'
    
    # Find all matches
    join_matches = re.finditer(join_pattern, sql_query, re.IGNORECASE | re.DOTALL)
    
    # Extract relationships from join conditions
    for match in join_matches:
        target_table = match.group(3)
        join_condition = match.group(5).strip()
        
        # Extract source table from join condition
        source_tables = []
        table_pattern = r'\[?(\w+)\]?\.\[?(\w+)\]?'
        for table_match in re.finditer(table_pattern, join_condition):
            if table_match.group(1) and table_match.group(1) != target_table:
                source_tables.append(table_match.group(1))
        
        # Add relationships
        for source_table in source_tables:
            relationships.append((source_table, target_table, join_condition))
    
    return relationships

def analyze_custom_queries():
    """
    Analyze custom SQL queries to extract additional information
    
    Returns:
        Dictionary containing analysis results
    """
    logger.info("Analyzing custom SQL queries...")
    
    # Check if custom queries directory exists
    if not os.path.exists(CUSTOM_QUERIES_DIR):
        logger.warning(f"Custom queries directory not found: {CUSTOM_QUERIES_DIR}")
        return {}
    
    # Get all SQL files in the custom queries directory
    sql_files = [f for f in os.listdir(CUSTOM_QUERIES_DIR) if f.endswith('.sql')]
    
    if not sql_files:
        logger.warning(f"No SQL files found in {CUSTOM_QUERIES_DIR}")
        return {}
    
    # Initialize analysis results
    analysis_results = {
        "queries": {},
        "tables": {},
        "relationships": [],
        "business_processes": {}
    }
    
    # Process each SQL file
    for sql_file in sql_files:
        logger.info(f"Analyzing query: {sql_file}")
        
        # Read SQL query
        with open(os.path.join(CUSTOM_QUERIES_DIR, sql_file), 'r', encoding='utf-8') as f:
            sql_query = f.read()
        
        # Extract query name (file name without extension)
        query_name = os.path.splitext(sql_file)[0]
        
        # Extract tables
        tables = extract_tables_from_query(sql_query)
        
        # Extract relationships
        relationships = extract_relationships_from_query(sql_query)
        
        # Determine business process based on tables and query name
        business_process = determine_business_process(query_name, tables)
        
        # Add query analysis to results
        analysis_results["queries"][query_name] = {
            "name": query_name,
            "tables": tables,
            "relationships": relationships,
            "business_process": business_process
        }
        
        # Update tables information
        for table in tables:
            if table not in analysis_results["tables"]:
                analysis_results["tables"][table] = {
                    "queries": []
                }
            analysis_results["tables"][table]["queries"].append(query_name)
        
        # Update relationships
        for relationship in relationships:
            source_table, target_table, join_condition = relationship
            analysis_results["relationships"].append({
                "source_table": source_table,
                "target_table": target_table,
                "join_condition": join_condition,
                "query": query_name
            })
        
        # Update business processes
        if business_process:
            if business_process not in analysis_results["business_processes"]:
                analysis_results["business_processes"][business_process] = {
                    "queries": [],
                    "tables": set()
                }
            analysis_results["business_processes"][business_process]["queries"].append(query_name)
            analysis_results["business_processes"][business_process]["tables"].update(tables)
    
    # Convert sets to lists for JSON serialization
    for process in analysis_results["business_processes"]:
        analysis_results["business_processes"][process]["tables"] = list(
            analysis_results["business_processes"][process]["tables"]
        )
    
    logger.info(f"Analyzed {len(sql_files)} custom SQL queries")
    
    return analysis_results

def determine_business_process(query_name, tables):
    """
    Determine the business process based on query name and tables
    
    Args:
        query_name: Name of the query
        tables: List of tables used in the query
        
    Returns:
        Business process name
    """
    # Define keywords for business processes
    business_processes = {
        "inventory_management": ["inventory", "stock", "15", "tr_hist"],
        "sales_order_processing": ["sales", "order", "customer", "so_mstr", "sod_det"],
        "purchase_order_processing": ["purchase", "vendor", "po_mstr", "pod_det"],
        "production_scheduling": ["production", "schedule", "sch_mstr", "active_schd_det"],
        "bom_management": ["bom", "bill of materials", "ps_mstr"],
        "demand_planning": ["demand", "forecast", "planning"],
        "item_master": ["item", "master", "pt_mstr"]
    }
    
    # Check query name for keywords
    query_name_lower = query_name.lower()
    for process, keywords in business_processes.items():
        for keyword in keywords:
            if keyword.lower() in query_name_lower:
                return process
    
    # Check tables for process determination
    process_tables = {
        "inventory_management": ["15", "tr_hist", "ld_det"],
        "sales_order_processing": ["so_mstr", "sod_det"],
        "purchase_order_processing": ["po_mstr", "pod_det"],
        "production_scheduling": ["sch_mstr", "active_schd_det", "sct_det"],
        "bom_management": ["ps_mstr"],
        "demand_planning": ["sch_mstr", "sod_det"],
        "item_master": ["pt_mstr"]
    }
    
    # Count matches for each process
    process_matches = {}
    for process, process_table_list in process_tables.items():
        matches = sum(1 for table in tables if table in process_table_list)
        if matches > 0:
            process_matches[process] = matches
    
    # Return process with most matches
    if process_matches:
        return max(process_matches.items(), key=lambda x: x[1])[0]
    
    # Default to "custom_process" if no match found
    return "custom_process"

def create_custom_query_documentation():
    """
    Create documentation for custom SQL queries
    """
    logger.info("Creating custom query documentation...")
    
    # Analyze custom queries
    analysis_results = analyze_custom_queries()
    
    if not analysis_results:
        logger.warning("No analysis results to document")
        return
    
    # Create custom queries directory if it doesn't exist
    os.makedirs(CUSTOM_QUERIES_DIR, exist_ok=True)
    
    # Create documentation file
    doc_path = os.path.join(DB_DOCS_DIR, "custom_queries.md")
    
    # Generate documentation content
    doc_content = "# Custom SQL Queries Documentation\n\n"
    doc_content += "This document provides documentation for custom SQL queries used with the QADEE2798 database.\n\n"
    
    # Add table of contents
    doc_content += "## Table of Contents\n\n"
    doc_content += "- [Queries](#queries)\n"
    for query_name in analysis_results["queries"]:
        doc_content += f"  - [{query_name}](#query-{query_name.lower().replace(' ', '-')})\n"
    doc_content += "- [Business Processes](#business-processes)\n"
    for process in analysis_results["business_processes"]:
        doc_content += f"  - [{process.replace('_', ' ').title()}](#process-{process.lower().replace('_', '-')})\n"
    
    # Add queries section
    doc_content += "\n## Queries\n\n"
    
    for query_name, query_info in analysis_results["queries"].items():
        doc_content += f"### {query_name} <a name=\"query-{query_name.lower().replace(' ', '-')}\"></a>\n\n"
        
        # Add business process
        doc_content += f"**Business Process:** {query_info['business_process'].replace('_', ' ').title()}\n\n"
        
        # Add tables used
        doc_content += "**Tables Used:**\n\n"
        for table in query_info["tables"]:
            doc_content += f"- [{table}](dbo.{table}/{table}_field_names.md)\n"
        
        # Add relationships
        if query_info["relationships"]:
            doc_content += "\n**Relationships:**\n\n"
            doc_content += "| Source Table | Target Table | Join Condition |\n"
            doc_content += "|--------------|--------------|----------------|\n"
            
            for relationship in query_info["relationships"]:
                source_table, target_table, join_condition = relationship
                # Truncate join condition if too long
                if len(join_condition) > 50:
                    join_condition = join_condition[:47] + "..."
                
                doc_content += f"| [{source_table}](dbo.{source_table}/{source_table}_field_names.md) | [{target_table}](dbo.{target_table}/{target_table}_field_names.md) | `{join_condition}` |\n"
        
        # Add SQL file reference
        doc_content += f"\n[View SQL File](custom_sql_queries/{query_name}.sql)\n\n"
    
    # Add business processes section
    doc_content += "\n## Business Processes\n\n"
    
    for process, process_info in analysis_results["business_processes"].items():
        doc_content += f"### {process.replace('_', ' ').title()} <a name=\"process-{process.lower().replace('_', '-')}\"></a>\n\n"
        
        # Add queries
        doc_content += "**Queries:**\n\n"
        for query in process_info["queries"]:
            doc_content += f"- [{query}](#query-{query.lower().replace(' ', '-')})\n"
        
        # Add tables
        doc_content += "\n**Tables:**\n\n"
        for table in process_info["tables"]:
            doc_content += f"- [{table}](dbo.{table}/{table}_field_names.md)\n"
        
        doc_content += "\n"
    
    # Write documentation to file
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    logger.info(f"Custom query documentation saved to {doc_path}")
    
    # Save analysis results as JSON
    json_path = os.path.join(DB_DOCS_DIR, "custom_query_analysis.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2)
    
    logger.info(f"Custom query analysis saved to {json_path}")

def create_custom_query_diagram():
    """
    Create diagram for custom SQL queries
    """
    logger.info("Creating custom query diagram...")
    
    # Load analysis results
    json_path = os.path.join(DB_DOCS_DIR, "custom_query_analysis.json")
    
    if not os.path.exists(json_path):
        logger.warning(f"Analysis results not found: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        analysis_results = json.load(f)
    
    # Create graph
    G = nx.DiGraph()
    
    # Add nodes for tables
    for table in analysis_results["tables"]:
        G.add_node(table, type='table')
    
    # Add nodes for queries
    for query_name in analysis_results["queries"]:
        G.add_node(query_name, type='query')
    
    # Add edges for table usage
    for query_name, query_info in analysis_results["queries"].items():
        for table in query_info["tables"]:
            G.add_edge(query_name, table, type='uses')
    
    # Add edges for relationships
    for relationship in analysis_results["relationships"]:
        source_table = relationship["source_table"]
        target_table = relationship["target_table"]
        G.add_edge(source_table, target_table, type='joins')
    
    # Create figure
    plt.figure(figsize=(16, 12))
    
    # Use spring layout
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # Draw nodes with different colors based on node type
    table_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'table']
    query_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'query']
    
    nx.draw_networkx_nodes(G, pos, nodelist=table_nodes, node_color='lightblue', 
                          node_size=2000, alpha=0.8, label='Tables')
    nx.draw_networkx_nodes(G, pos, nodelist=query_nodes, node_color='lightgreen', 
                          node_size=2000, alpha=0.8, label='Queries')
    
    # Draw edges with different colors based on edge type
    uses_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'uses']
    joins_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'joins']
    
    nx.draw_networkx_edges(G, pos, edgelist=uses_edges, width=1.5, alpha=0.6, 
                          edge_color='green', arrows=True, arrowsize=15, label='Uses')
    nx.draw_networkx_edges(G, pos, edgelist=joins_edges, width=1.5, alpha=0.6, 
                          edge_color='blue', arrows=True, arrowsize=15, label='Joins')
    
    # Add labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Add legend
    plt.legend()
    
    # Add title
    plt.title("Custom SQL Queries and Table Relationships")
    plt.tight_layout()
    
    # Save figure
    diagram_path = os.path.join(DB_DOCS_DIR, "custom_query_diagram.png")
    plt.savefig(diagram_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Custom query diagram saved to {diagram_path}")

def update_data_lineage_documentation():
    """
    Update data lineage documentation with custom query information
    """
    logger.info("Updating data lineage documentation...")
    
    # Load analysis results
    json_path = os.path.join(DB_DOCS_DIR, "custom_query_analysis.json")
    
    if not os.path.exists(json_path):
        logger.warning(f"Analysis results not found: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        analysis_results = json.load(f)
    
    # Path to data lineage documentation
    lineage_path = os.path.join(DB_DOCS_DIR, "data_lineage.md")
    
    if not os.path.exists(lineage_path):
        logger.warning(f"Data lineage documentation not found: {lineage_path}")
        return
    
    # Read existing documentation
    with open(lineage_path, 'r', encoding='utf-8') as f:
        lineage_content = f.read()
    
    # Add custom queries section if it doesn't exist
    if "## Custom SQL Queries" not in lineage_content:
        custom_queries_section = "\n## Custom SQL Queries\n\n"
        custom_queries_section += "The following custom SQL queries provide additional insights into data flows and relationships:\n\n"
        
        # Add query information
        for query_name, query_info in analysis_results["queries"].items():
            custom_queries_section += f"### {query_name}\n\n"
            custom_queries_section += f"**Business Process:** {query_info['business_process'].replace('_', ' ').title()}\n\n"
            
            # Add tables used
            custom_queries_section += "**Tables Used:**\n\n"
            for table in query_info["tables"]:
                custom_queries_section += f"- [{table}](dbo.{table}/{table}_field_names.md)\n"
            
            # Add relationships
            if query_info["relationships"]:
                custom_queries_section += "\n**Relationships:**\n\n"
                for relationship in query_info["relationships"]:
                    source_table, target_table, join_condition = relationship
                    custom_queries_section += f"- [{source_table}](dbo.{source_table}/{source_table}_field_names.md) → [{target_table}](dbo.{target_table}/{target_table}_field_names.md)\n"
            
            custom_queries_section += f"\n[View SQL File](custom_sql_queries/{query_name}.sql)\n\n"
        
        # Add diagram reference
        custom_queries_section += "### Custom Query Diagram\n\n"
        custom_queries_section += "![Custom SQL Queries and Table Relationships](custom_query_diagram.png)\n\n"
        
        # Add custom queries section to documentation
        lineage_content += custom_queries_section
        
        # Write updated documentation
        with open(lineage_path, 'w', encoding='utf-8') as f:
            f.write(lineage_content)
        
        logger.info(f"Updated data lineage documentation with custom query information")

def update_dashboard():
    """
    Update dashboard with custom query information
    """
    logger.info("Updating dashboard...")
    
    # Path to dashboard HTML file
    dashboard_path = os.path.join(DB_DOCS_DIR, "dashboard", "index.html")
    
    if not os.path.exists(dashboard_path):
        logger.warning(f"Dashboard HTML not found: {dashboard_path}")
        return
    
    # Read existing HTML
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Check if custom queries section already exists
    if "Custom Queries" in html_content:
        logger.info("Custom queries section already exists in dashboard")
        return
    
    # Add custom queries to navigation
    nav_pattern = r'<div class="nav-category">Tables</div>'
    nav_replacement = '<div class="nav-category">Custom Queries</div>\n            <div class="nav-item" data-target="custom-queries">Custom Queries</div>\n            \n            <div class="nav-category">Tables</div>'
    
    html_content = re.sub(nav_pattern, nav_replacement, html_content)
    
    # Add custom queries section
    content_pattern = r'<div id="performance" class="content-section" style="display: none;">'
    content_replacement = '<div id="custom-queries" class="content-section" style="display: none;">\n                <div class="header">\n                    <h1>Custom SQL Queries</h1>\n                    <p>Custom SQL queries providing additional insights into data flows and relationships.</p>\n                </div>\n                \n                <div class="card">\n                    <h2>Custom Query Diagram</h2>\n                    <div class="diagram-container">\n                        <img src="images/custom_query_diagram.png" alt="Custom SQL Queries and Table Relationships">\n                    </div>\n                </div>\n                \n                <div class="card">\n                    <h2>Query Documentation</h2>\n                    <p>For detailed documentation of custom SQL queries, see the <a href="../custom_queries.md">Custom Queries Documentation</a>.</p>\n                </div>\n            </div>\n            \n            <div id="performance" class="content-section" style="display: none;">'
    
    html_content = re.sub(content_pattern, content_replacement, html_content)
    
    # Copy custom query diagram to dashboard images directory
    diagram_path = os.path.join(DB_DOCS_DIR, "custom_query_diagram.png")
    dashboard_images_dir = os.path.join(DB_DOCS_DIR, "dashboard", "images")
    
    if os.path.exists(diagram_path) and os.path.exists(dashboard_images_dir):
        import shutil
        shutil.copy(diagram_path, os.path.join(dashboard_images_dir, "custom_query_diagram.png"))
    
    # Write updated HTML
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"Updated dashboard with custom query information")

def main():
    """Main function to analyze custom SQL queries and update documentation"""
    # Create custom query documentation
    create_custom_query_documentation()
    
    # Create custom query diagram
    create_custom_query_diagram()
    
    # Update data lineage documentation
    update_data_lineage_documentation()
    
    # Update dashboard
    update_dashboard()
    
    logger.info("Custom query analysis complete!")

if __name__ == "__main__":
    main()
