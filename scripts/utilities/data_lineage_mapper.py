"""
Data Lineage Mapper

This script creates comprehensive data lineage documentation by analyzing
table relationships and business processes in the QADEE2798 database.

It preserves all existing database documentation while adding data lineage
information as a layered enhancement.
"""

import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_lineage.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database documentation directory
DB_DOCS_DIR = os.path.join("Database_tables", "QADEE2798")

# Business process definitions
BUSINESS_PROCESSES = {
    "inventory_management": {
        "name": "Inventory Management",
        "description": "Tracks inventory levels, movements, and adjustments",
        "tables": ["15", "tr_hist"],
        "flows": [
            {"from": "tr_hist", "to": "15", "description": "Inventory transactions update inventory levels"}
        ]
    },
    "sales_order_processing": {
        "name": "Sales Order Processing",
        "description": "Manages sales orders from creation to fulfillment",
        "tables": ["so_mstr", "sod_det", "15", "tr_hist", "ad_mstr"],
        "flows": [
            {"from": "so_mstr", "to": "sod_det", "description": "Sales order header to detail"},
            {"from": "sod_det", "to": "tr_hist", "description": "Sales order fulfillment creates transactions"},
            {"from": "tr_hist", "to": "15", "description": "Transactions update inventory levels"},
            {"from": "ad_mstr", "to": "so_mstr", "description": "Customer information for sales orders"}
        ]
    },
    "purchase_order_processing": {
        "name": "Purchase Order Processing",
        "description": "Manages purchase orders from creation to receipt",
        "tables": ["po_mstr", "pod_det", "15", "tr_hist", "vd_mstr"],
        "flows": [
            {"from": "po_mstr", "to": "pod_det", "description": "Purchase order header to detail"},
            {"from": "pod_det", "to": "tr_hist", "description": "Purchase order receipt creates transactions"},
            {"from": "tr_hist", "to": "15", "description": "Transactions update inventory levels"},
            {"from": "vd_mstr", "to": "po_mstr", "description": "Vendor information for purchase orders"}
        ]
    },
    "production_scheduling": {
        "name": "Production Scheduling",
        "description": "Manages production schedules and work orders",
        "tables": ["sch_mstr", "active_schd_det", "sct_det", "15", "tr_hist", "pt_mstr"],
        "flows": [
            {"from": "sch_mstr", "to": "active_schd_det", "description": "Schedule header to active detail"},
            {"from": "active_schd_det", "to": "sct_det", "description": "Schedule execution creates transactions"},
            {"from": "sct_det", "to": "tr_hist", "description": "Schedule transactions update history"},
            {"from": "tr_hist", "to": "15", "description": "Transactions update inventory levels"},
            {"from": "pt_mstr", "to": "sch_mstr", "description": "Part information for scheduling"}
        ]
    },
    "serial_tracking": {
        "name": "Serial Number Tracking",
        "description": "Tracks serialized items throughout their lifecycle",
        "tables": ["ser_item_detail", "ser_active_picked", "serh_hist", "tr_hist"],
        "flows": [
            {"from": "ser_item_detail", "to": "ser_active_picked", "description": "Serial items to picked status"},
            {"from": "ser_active_picked", "to": "serh_hist", "description": "Active serials to history"},
            {"from": "serh_hist", "to": "tr_hist", "description": "Serial history linked to transactions"}
        ]
    },
    "shipping_and_logistics": {
        "name": "Shipping and Logistics",
        "description": "Manages shipping, loads, and deliveries",
        "tables": ["ld_det", "so_mstr", "sod_det", "tr_hist", "ad_mstr"],
        "flows": [
            {"from": "so_mstr", "to": "ld_det", "description": "Sales orders to load details"},
            {"from": "sod_det", "to": "ld_det", "description": "Sales order lines to load details"},
            {"from": "ld_det", "to": "tr_hist", "description": "Load shipment creates transactions"},
            {"from": "ad_mstr", "to": "ld_det", "description": "Address information for shipping"}
        ]
    }
}

def load_relationships():
    """
    Load relationship information from CSV file
    
    Returns:
        DataFrame containing relationship information
    """
    logger.info("Loading relationship information...")
    
    # Path to relationships CSV file
    csv_path = os.path.join(DB_DOCS_DIR, "inferred_relationships.csv")
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} relationships from {csv_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading relationships: {str(e)}")
    
    logger.warning(f"Relationships file not found: {csv_path}")
    return pd.DataFrame(columns=['table1', 'column1', 'table2', 'column2', 'confidence'])

def create_data_flow_diagram(process_id, process_info, output_path):
    """
    Create a data flow diagram for a specific business process
    
    Args:
        process_id: ID of the business process
        process_info: Dictionary containing process information
        output_path: Path to save the diagram
    """
    logger.info(f"Creating data flow diagram for {process_info['name']}...")
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes (tables)
    for table in process_info['tables']:
        G.add_node(table)
    
    # Add edges (flows)
    for flow in process_info['flows']:
        if flow['from'] in process_info['tables'] and flow['to'] in process_info['tables']:
            G.add_edge(
                flow['from'], 
                flow['to'],
                label=flow['description']
            )
    
    # Create figure
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # Draw nodes with different colors based on node type
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=2.0, alpha=0.7, edge_color='blue',
                          arrows=True, arrowsize=15)
    
    # Add edge labels
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Add title
    plt.title(f"Data Flow: {process_info['name']}")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Data flow diagram saved to {output_path}")

def create_master_data_flow_diagram(output_path):
    """
    Create a master data flow diagram showing all business processes
    
    Args:
        output_path: Path to save the diagram
    """
    logger.info("Creating master data flow diagram...")
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Collect all tables and flows
    all_tables = set()
    all_flows = []
    
    for process_id, process_info in BUSINESS_PROCESSES.items():
        all_tables.update(process_info['tables'])
        all_flows.extend(process_info['flows'])
    
    # Add nodes (tables)
    for table in all_tables:
        G.add_node(table)
    
    # Add edges (flows)
    for flow in all_flows:
        if flow['from'] in all_tables and flow['to'] in all_tables:
            # Check if edge already exists
            if G.has_edge(flow['from'], flow['to']):
                # Append to existing label
                G[flow['from']][flow['to']]['label'] += f"; {flow['description']}"
            else:
                G.add_edge(
                    flow['from'], 
                    flow['to'],
                    label=flow['description']
                )
    
    # Create figure
    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.6, edge_color='blue',
                          arrows=True, arrowsize=12)
    
    # Add edge labels (shortened for readability)
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        label = d['label']
        if len(label) > 30:
            label = label[:27] + "..."
        edge_labels[(u, v)] = label
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    
    # Add title
    plt.title("Master Data Flow Diagram")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Master data flow diagram saved to {output_path}")

def create_data_lineage_documentation():
    """
    Create comprehensive data lineage documentation
    """
    logger.info("Creating data lineage documentation...")
    
    # Path to data lineage documentation file
    lineage_path = os.path.join(DB_DOCS_DIR, "data_lineage.md")
    
    # Create documentation content
    lineage_content = "# QADEE2798 Data Lineage Documentation\n\n"
    lineage_content += "This document provides comprehensive data lineage information for the QADEE2798 database.\n\n"
    
    # Add master data flow diagram reference
    lineage_content += "## Master Data Flow Diagram\n\n"
    lineage_content += "![Master Data Flow Diagram](master_data_flow.png)\n\n"
    
    # Add business processes section
    lineage_content += "## Business Processes\n\n"
    
    for process_id, process_info in BUSINESS_PROCESSES.items():
        lineage_content += f"### {process_info['name']}\n\n"
        lineage_content += f"{process_info['description']}\n\n"
        
        # Add process diagram reference
        lineage_content += f"![{process_info['name']} Data Flow](data_flow_{process_id}.png)\n\n"
        
        # Add tables involved
        lineage_content += "#### Tables Involved\n\n"
        for table in process_info['tables']:
            lineage_content += f"- [{table}](dbo.{table}/{table}_field_names.md): "
            
            # Add table description based on our predefined descriptions
            table_descriptions = {
                "15": "Inventory Master - Contains inventory quantities and status information",
                "active_schd_det": "Active Schedule Details - Contains active schedule information",
                "ad_mstr": "Address Master - Contains address information for customers and vendors",
                "ld_det": "Load Details - Contains details about shipment loads",
                "pckc_mstr": "Pick Confirmation Master - Contains information about pick confirmations",
                "po_mstr": "Purchase Order Master - Contains header information for purchase orders",
                "pod_det": "Purchase Order Detail - Contains line item details for purchase orders",
                "ps_mstr": "Product Structure Master - Contains bill of materials information",
                "pt_mstr": "Part Master - Contains part information including costs and classifications",
                "sch_mstr": "Schedule Master - Contains header information for production schedules",
                "sct_det": "Schedule Transaction Detail - Contains transaction details for schedules",
                "ser_active_picked": "Serial Active Picked - Contains information about picked serialized items",
                "ser_item_detail": "Serial Item Detail - Contains details about serialized items",
                "serh_hist": "Serial History - Contains historical information about serialized items",
                "so_mstr": "Sales Order Master - Contains header information for sales orders",
                "sod_det": "Sales Order Detail - Contains line item details for sales orders",
                "tr_hist": "Transaction History - Contains historical transaction information",
                "vd_mstr": "Vendor Master - Contains vendor information"
            }
            
            lineage_content += f"{table_descriptions.get(table, 'No description available')}\n"
        
        # Add data flows
        lineage_content += "\n#### Data Flows\n\n"
        lineage_content += "| Source Table | Target Table | Description |\n"
        lineage_content += "|--------------|--------------|-------------|\n"
        
        for flow in process_info['flows']:
            source = flow['from']
            target = flow['to']
            description = flow['description']
            
            lineage_content += f"| [{source}](dbo.{source}/{source}_field_names.md) | [{target}](dbo.{target}/{target}_field_names.md) | {description} |\n"
        
        # Add example query
        lineage_content += "\n#### Example Query\n\n"
        lineage_content += "```sql\n"
        
        # Generate a query based on the process
        if process_id == "inventory_management":
            lineage_content += "-- Inventory Management Query Example\n"
            lineage_content += "SELECT \n"
            lineage_content += "    i.in_part AS 'Part Number',\n"
            lineage_content += "    i.in_site AS 'Site',\n"
            lineage_content += "    i.in_qty_oh AS 'On Hand Qty',\n"
            lineage_content += "    t.tr_date AS 'Last Transaction Date',\n"
            lineage_content += "    t.tr_type AS 'Transaction Type',\n"
            lineage_content += "    t.tr_qty_loc AS 'Transaction Qty'\n"
            lineage_content += "FROM \n"
            lineage_content += "    [QADEE2798].[dbo].[15] i\n"
            lineage_content += "LEFT JOIN \n"
            lineage_content += "    [QADEE2798].[dbo].[tr_hist] t ON i.in_part = t.tr_part AND i.in_site = t.tr_site\n"
            lineage_content += "WHERE \n"
            lineage_content += "    i.in_part = 'PART_NUMBER'\n"
            lineage_content += "ORDER BY \n"
            lineage_content += "    t.tr_date DESC\n"
        elif process_id == "sales_order_processing":
            lineage_content += "-- Sales Order Processing Query Example\n"
            lineage_content += "SELECT \n"
            lineage_content += "    so.so_nbr AS 'Order Number',\n"
            lineage_content += "    so.so_cust AS 'Customer',\n"
            lineage_content += "    ad.ad_name AS 'Customer Name',\n"
            lineage_content += "    so.so_ord_date AS 'Order Date',\n"
            lineage_content += "    sod.sod_part AS 'Part Number',\n"
            lineage_content += "    sod.sod_qty_ord AS 'Ordered Qty',\n"
            lineage_content += "    i.in_qty_oh AS 'On Hand Qty',\n"
            lineage_content += "    t.tr_date AS 'Transaction Date'\n"
            lineage_content += "FROM \n"
            lineage_content += "    [QADEE2798].[dbo].[so_mstr] so\n"
            lineage_content += "JOIN \n"
            lineage_content += "    [QADEE2798].[dbo].[sod_det] sod ON so.so_nbr = sod.sod_nbr\n"
            lineage_content += "LEFT JOIN \n"
            lineage_content += "    [QADEE2798].[dbo].[ad_mstr] ad ON so.so_cust = ad.ad_addr\n"
            lineage_content += "LEFT JOIN \n"
            lineage_content += "    [QADEE2798].[dbo].[15] i ON sod.sod_part = i.in_part\n"
            lineage_content += "LEFT JOIN \n"
            lineage_content += "    [QADEE2798].[dbo].[tr_hist] t ON sod.sod_part = t.tr_part AND t.tr_nbr = so.so_nbr\n"
            lineage_content += "WHERE \n"
            lineage_content += "    so.so_nbr = 'ORDER_NUMBER'\n"
        else:
            lineage_content += f"-- {process_info['name']} Query Example\n"
            lineage_content += "SELECT * FROM "
            lineage_content += " JOIN ".join([f"[QADEE2798].[dbo].[{table}]" for table in process_info['tables'][:2]])
            lineage_content += "\nWHERE 1=1\n"
        
        lineage_content += "```\n\n"
    
    # Add table lineage section
    lineage_content += "## Table Lineage\n\n"
    
    # Group flows by table
    table_flows = defaultdict(list)
    
    for process_id, process_info in BUSINESS_PROCESSES.items():
        for flow in process_info['flows']:
            source = flow['from']
            target = flow['to']
            description = flow['description']
            process_name = process_info['name']
            
            table_flows[source].append({
                "target": target,
                "description": description,
                "process": process_name
            })
            
            table_flows[target].append({
                "source": source,
                "description": description,
                "process": process_name
            })
    
    # Add table lineage information
    for table in sorted(table_flows.keys()):
        lineage_content += f"### {table}\n\n"
        
        # Add incoming flows
        incoming = [flow for flow in table_flows[table] if 'source' in flow]
        if incoming:
            lineage_content += "#### Incoming Data\n\n"
            lineage_content += "| Source Table | Process | Description |\n"
            lineage_content += "|--------------|---------|-------------|\n"
            
            for flow in incoming:
                source = flow['source']
                process = flow['process']
                description = flow['description']
                
                lineage_content += f"| [{source}](dbo.{source}/{source}_field_names.md) | {process} | {description} |\n"
        
        # Add outgoing flows
        outgoing = [flow for flow in table_flows[table] if 'target' in flow]
        if outgoing:
            lineage_content += "\n#### Outgoing Data\n\n"
            lineage_content += "| Target Table | Process | Description |\n"
            lineage_content += "|--------------|---------|-------------|\n"
            
            for flow in outgoing:
                target = flow['target']
                process = flow['process']
                description = flow['description']
                
                lineage_content += f"| [{target}](dbo.{target}/{target}_field_names.md) | {process} | {description} |\n"
        
        lineage_content += "\n"
    
    # Write documentation to file
    with open(lineage_path, 'w', encoding='utf-8') as f:
        f.write(lineage_content)
    
    logger.info(f"Data lineage documentation saved to {lineage_path}")

def main():
    """Main function to create data lineage documentation"""
    # Create output directory if it doesn't exist
    os.makedirs(DB_DOCS_DIR, exist_ok=True)
    
    # Load relationship information
    relationships_df = load_relationships()
    
    # Create data flow diagrams for each business process
    for process_id, process_info in BUSINESS_PROCESSES.items():
        diagram_path = os.path.join(DB_DOCS_DIR, f"data_flow_{process_id}.png")
        create_data_flow_diagram(process_id, process_info, diagram_path)
    
    # Create master data flow diagram
    master_diagram_path = os.path.join(DB_DOCS_DIR, "master_data_flow.png")
    create_master_data_flow_diagram(master_diagram_path)
    
    # Create data lineage documentation
    create_data_lineage_documentation()
    
    logger.info("Data lineage mapping complete!")

if __name__ == "__main__":
    main()
