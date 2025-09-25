"""
Interactive Database Documentation Dashboard Generator

This script creates an HTML-based interactive dashboard for the QADEE2798 database
documentation, integrating all components into a single navigable interface.
"""

import os
import re
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dashboard_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database documentation directory
DB_DOCS_DIR = os.path.join("Database_tables", "QADEE2798")
DASHBOARD_DIR = os.path.join(DB_DOCS_DIR, "dashboard")

def create_dashboard_structure():
    """Create the dashboard directory structure"""
    logger.info("Creating dashboard directory structure...")
    
    # Create dashboard directory
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    
    # Create subdirectories
    os.makedirs(os.path.join(DASHBOARD_DIR, "css"), exist_ok=True)
    os.makedirs(os.path.join(DASHBOARD_DIR, "js"), exist_ok=True)
    os.makedirs(os.path.join(DASHBOARD_DIR, "images"), exist_ok=True)
    
    # Copy images
    for image_file in os.listdir(DB_DOCS_DIR):
        if image_file.endswith(".png"):
            shutil.copy(
                os.path.join(DB_DOCS_DIR, image_file),
                os.path.join(DASHBOARD_DIR, "images", image_file)
            )
    
    logger.info("Dashboard structure created")

def create_css():
    """Create CSS for the dashboard"""
    logger.info("Creating CSS...")
    
    css_content = """
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f5f5f5;
        color: #333;
    }
    
    .container {
        display: flex;
        min-height: 100vh;
    }
    
    .sidebar {
        width: 250px;
        background-color: #2c3e50;
        color: #ecf0f1;
        padding: 20px 0;
        overflow-y: auto;
        position: fixed;
        height: 100%;
    }
    
    .content {
        flex: 1;
        padding: 20px;
        margin-left: 250px;
    }
    
    .header {
        background-color: #3498db;
        color: white;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 5px;
    }
    
    .card {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .nav-item {
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .nav-item:hover {
        background-color: #34495e;
    }
    
    .nav-item.active {
        background-color: #3498db;
    }
    
    .nav-category {
        font-weight: bold;
        padding: 15px 20px 5px;
        color: #3498db;
        border-bottom: 1px solid #34495e;
        margin-top: 10px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    
    table, th, td {
        border: 1px solid #ddd;
    }
    
    th, td {
        padding: 12px;
        text-align: left;
    }
    
    th {
        background-color: #3498db;
        color: white;
    }
    
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    
    .search-box {
        padding: 10px;
        margin: 10px 20px;
        width: calc(100% - 40px);
        border: 1px solid #34495e;
        border-radius: 5px;
        background-color: #34495e;
        color: white;
    }
    
    .search-box::placeholder {
        color: #bdc3c7;
    }
    
    .tab-container {
        display: flex;
        border-bottom: 1px solid #ddd;
        margin-bottom: 20px;
    }
    
    .tab {
        padding: 10px 20px;
        cursor: pointer;
        background-color: #f2f2f2;
        border: 1px solid #ddd;
        border-bottom: none;
        margin-right: 5px;
        border-radius: 5px 5px 0 0;
    }
    
    .tab.active {
        background-color: white;
        border-bottom: 1px solid white;
    }
    
    .tab-content {
        display: none;
    }
    
    .tab-content.active {
        display: block;
    }
    
    pre {
        background-color: #f8f8f8;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
    }
    
    code {
        font-family: 'Courier New', Courier, monospace;
    }
    
    .diagram-container {
        text-align: center;
        margin: 20px 0;
    }
    
    .diagram-container img {
        max-width: 100%;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    """
    
    # Write CSS to file
    with open(os.path.join(DASHBOARD_DIR, "css", "style.css"), "w") as f:
        f.write(css_content)
    
    logger.info("CSS created")

def create_javascript():
    """Create JavaScript for the dashboard"""
    logger.info("Creating JavaScript...")
    
    js_content = """
    document.addEventListener('DOMContentLoaded', function() {
        // Navigation
        const navItems = document.querySelectorAll('.nav-item');
        const contentSections = document.querySelectorAll('.content-section');
        
        navItems.forEach(item => {
            item.addEventListener('click', function() {
                const target = this.getAttribute('data-target');
                
                // Hide all content sections
                contentSections.forEach(section => {
                    section.style.display = 'none';
                });
                
                // Remove active class from all nav items
                navItems.forEach(navItem => {
                    navItem.classList.remove('active');
                });
                
                // Show target content and mark nav item as active
                document.getElementById(target).style.display = 'block';
                this.classList.add('active');
                
                // Update URL hash
                window.location.hash = target;
            });
        });
        
        // Handle tabs
        const tabs = document.querySelectorAll('.tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabContainer = this.parentElement;
                const contentContainer = tabContainer.nextElementSibling;
                const tabTarget = this.getAttribute('data-tab');
                
                // Remove active class from all tabs in this container
                tabContainer.querySelectorAll('.tab').forEach(t => {
                    t.classList.remove('active');
                });
                
                // Hide all tab content in this container
                contentContainer.querySelectorAll('.tab-content').forEach(c => {
                    c.classList.remove('active');
                });
                
                // Activate selected tab and content
                this.classList.add('active');
                contentContainer.querySelector(`#${tabTarget}`).classList.add('active');
            });
        });
        
        // Search functionality
        const searchBox = document.getElementById('search');
        searchBox.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            if (searchTerm.length < 2) {
                navItems.forEach(item => {
                    item.style.display = 'block';
                });
                return;
            }
            
            navItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
        
        // Handle URL hash on page load
        if (window.location.hash) {
            const targetId = window.location.hash.substring(1);
            const targetNav = document.querySelector(`.nav-item[data-target="${targetId}"]`);
            if (targetNav) {
                targetNav.click();
            } else {
                // Default to first nav item
                navItems[0].click();
            }
        } else {
            // Default to first nav item
            navItems[0].click();
        }
    });
    """
    
    # Write JavaScript to file
    with open(os.path.join(DASHBOARD_DIR, "js", "script.js"), "w") as f:
        f.write(js_content)
    
    logger.info("JavaScript created")

def collect_table_info():
    """Collect information about all tables"""
    logger.info("Collecting table information...")
    
    tables = []
    
    # Get all table directories
    for item in os.listdir(DB_DOCS_DIR):
        table_dir = os.path.join(DB_DOCS_DIR, item)
        if os.path.isdir(table_dir) and item.startswith("dbo."):
            table_name = item.replace("dbo.", "")
            
            # Check for field names markdown file
            field_names_file = os.path.join(table_dir, f"{table_name}_field_names.md")
            if os.path.exists(field_names_file):
                # Extract table description and fields
                with open(field_names_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Extract description
                description = "No description available"
                desc_match = re.search(r"## Description\s+(.+?)(?=\n\n|\n##|$)", content, re.DOTALL)
                if desc_match:
                    description = desc_match.group(1).strip()
                
                # Extract fields
                fields = []
                field_pattern = r"\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(Yes|No)\s*\|\s*(Yes|No)\s*\|\s*(Yes|No)\s*\|\s*(.+?)\s*\|"
                for match in re.finditer(field_pattern, content):
                    fields.append({
                        "name": match.group(1),
                        "type": match.group(2),
                        "primary_key": match.group(3) == "Yes",
                        "foreign_key": match.group(4) == "Yes",
                        "nullable": match.group(5) == "Yes",
                        "description": match.group(6).strip()
                    })
                
                # Check for SQL file
                sql_file = os.path.join(table_dir, f"{table_name}.sql")
                sql_query = ""
                if os.path.exists(sql_file):
                    with open(sql_file, "r", encoding="utf-8") as f:
                        sql_query = f.read()
                
                tables.append({
                    "name": table_name,
                    "description": description,
                    "fields": fields,
                    "sql_query": sql_query
                })
    
    logger.info(f"Collected information for {len(tables)} tables")
    return tables

def generate_dashboard_html(tables):
    """Generate the main dashboard HTML"""
    logger.info("Generating dashboard HTML...")
    
    # Read markdown files
    data_lineage_md = ""
    if os.path.exists(os.path.join(DB_DOCS_DIR, "data_lineage.md")):
        with open(os.path.join(DB_DOCS_DIR, "data_lineage.md"), "r", encoding="utf-8") as f:
            data_lineage_md = f.read()
    
    data_dictionary_md = ""
    if os.path.exists(os.path.join(DB_DOCS_DIR, "data_dictionary.md")):
        with open(os.path.join(DB_DOCS_DIR, "data_dictionary.md"), "r", encoding="utf-8") as f:
            data_dictionary_md = f.read()
    
    performance_md = ""
    if os.path.exists(os.path.join(DB_DOCS_DIR, "performance_recommendations.md")):
        with open(os.path.join(DB_DOCS_DIR, "performance_recommendations.md"), "r", encoding="utf-8") as f:
            performance_md = f.read()
    
    query_templates_md = ""
    if os.path.exists(os.path.join(DB_DOCS_DIR, "query_builder_templates.md")):
        with open(os.path.join(DB_DOCS_DIR, "query_builder_templates.md"), "r", encoding="utf-8") as f:
            query_templates_md = f.read()
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QADEE2798 Database Documentation</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2 style="text-align: center; padding: 0 10px;">QADEE2798</h2>
            <input type="text" id="search" class="search-box" placeholder="Search...">
            
            <div class="nav-category">Overview</div>
            <div class="nav-item" data-target="dashboard">Dashboard</div>
            <div class="nav-item" data-target="data-lineage">Data Lineage</div>
            <div class="nav-item" data-target="data-dictionary">Data Dictionary</div>
            <div class="nav-item" data-target="query-templates">Query Templates</div>
            <div class="nav-item" data-target="performance">Performance</div>
            
            <div class="nav-category">Tables</div>
"""
    
    # Add table navigation items
    for table in sorted(tables, key=lambda x: x["name"]):
        html += f'            <div class="nav-item" data-target="table-{table["name"]}">{table["name"]}</div>\n'
    
    html += """
        </div>
        
        <div class="content">
            <!-- Dashboard Section -->
            <div id="dashboard" class="content-section">
                <div class="header">
                    <h1>QADEE2798 Database Documentation</h1>
                    <p>Comprehensive documentation and mapping of the QADEE2798 database structure, relationships, and usage.</p>
                </div>
                
                <div class="card">
                    <h2>Database Overview</h2>
                    <p>This dashboard provides access to comprehensive documentation for the QADEE2798 database, including:</p>
                    <ul>
                        <li><strong>Data Lineage:</strong> Visual representation of data flow between tables</li>
                        <li><strong>Data Dictionary:</strong> Detailed information about tables and fields</li>
                        <li><strong>Query Templates:</strong> Ready-to-use query templates for common operations</li>
                        <li><strong>Performance Recommendations:</strong> Guidelines for optimizing database performance</li>
                        <li><strong>Table Documentation:</strong> Detailed information about each table</li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>Database Structure</h2>
                    <div class="diagram-container">
                        <img src="images/master_data_flow.png" alt="Database Structure">
                    </div>
                </div>
                
                <div class="card">
                    <h2>Key Business Processes</h2>
                    <div class="tab-container">
                        <div class="tab active" data-tab="inventory-process">Inventory</div>
                        <div class="tab" data-tab="sales-process">Sales</div>
                        <div class="tab" data-tab="purchase-process">Purchasing</div>
                        <div class="tab" data-tab="production-process">Production</div>
                        <div class="tab" data-tab="shipping-process">Shipping</div>
                    </div>
                    <div>
                        <div id="inventory-process" class="tab-content active">
                            <h3>Inventory Management</h3>
                            <p>Tracks and manages inventory levels, movements, and adjustments</p>
                            <div class="diagram-container">
                                <img src="images/data_flow_inventory_management.png" alt="Inventory Management">
                            </div>
                        </div>
                        <div id="sales-process" class="tab-content">
                            <h3>Sales Order Processing</h3>
                            <p>Manages sales orders from creation to fulfillment</p>
                            <div class="diagram-container">
                                <img src="images/data_flow_sales_order_processing.png" alt="Sales Order Processing">
                            </div>
                        </div>
                        <div id="purchase-process" class="tab-content">
                            <h3>Purchase Order Processing</h3>
                            <p>Manages purchase orders from creation to receipt</p>
                            <div class="diagram-container">
                                <img src="images/data_flow_purchase_order_processing.png" alt="Purchase Order Processing">
                            </div>
                        </div>
                        <div id="production-process" class="tab-content">
                            <h3>Production Scheduling</h3>
                            <p>Manages production schedules and work orders</p>
                            <div class="diagram-container">
                                <img src="images/data_flow_production_scheduling.png" alt="Production Scheduling">
                            </div>
                        </div>
                        <div id="shipping-process" class="tab-content">
                            <h3>Shipping and Logistics</h3>
                            <p>Manages shipping, loads, and deliveries</p>
                            <div class="diagram-container">
                                <img src="images/data_flow_shipping_and_logistics.png" alt="Shipping and Logistics">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Data Lineage Section -->
            <div id="data-lineage" class="content-section" style="display: none;">
                <div class="header">
                    <h1>Data Lineage</h1>
                    <p>Visual representation of data flow between tables in the QADEE2798 database.</p>
                </div>
                
                <div class="card">
                    <div class="markdown-content">
                        <!-- Convert markdown to HTML here -->
                        {data_lineage_md.replace('![', '![alt text](images/').replace('](', ' "title")(').replace('.png)', '.png">')}
                    </div>
                </div>
            </div>
            
            <!-- Data Dictionary Section -->
            <div id="data-dictionary" class="content-section" style="display: none;">
                <div class="header">
                    <h1>Data Dictionary</h1>
                    <p>Comprehensive information about tables and fields in the QADEE2798 database.</p>
                </div>
                
                <div class="card">
                    <div class="markdown-content">
                        <!-- Convert markdown to HTML here -->
                        {data_dictionary_md}
                    </div>
                </div>
            </div>
            
            <!-- Query Templates Section -->
            <div id="query-templates" class="content-section" style="display: none;">
                <div class="header">
                    <h1>Query Templates</h1>
                    <p>Ready-to-use query templates for common database operations.</p>
                </div>
                
                <div class="card">
                    <div class="markdown-content">
                        <!-- Convert markdown to HTML here -->
                        {query_templates_md}
                    </div>
                </div>
            </div>
            
            <!-- Performance Section -->
            <div id="performance" class="content-section" style="display: none;">
                <div class="header">
                    <h1>Performance Recommendations</h1>
                    <p>Guidelines for optimizing database performance.</p>
                </div>
                
                <div class="card">
                    <div class="markdown-content">
                        <!-- Convert markdown to HTML here -->
                        {performance_md}
                    </div>
                </div>
            </div>
"""
    
    # Add table sections
    for table in tables:
        html += f"""
            <!-- {table["name"]} Table Section -->
            <div id="table-{table["name"]}" class="content-section" style="display: none;">
                <div class="header">
                    <h1>{table["name"]}</h1>
                    <p>{table["description"]}</p>
                </div>
                
                <div class="card">
                    <h2>Fields</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Field Name</th>
                                <th>Data Type</th>
                                <th>Primary Key</th>
                                <th>Foreign Key</th>
                                <th>Nullable</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
"""
        
        for field in table["fields"]:
            html += f"""
                            <tr>
                                <td>{field["name"]}</td>
                                <td>{field["type"]}</td>
                                <td>{"Yes" if field["primary_key"] else "No"}</td>
                                <td>{"Yes" if field["foreign_key"] else "No"}</td>
                                <td>{"Yes" if field["nullable"] else "No"}</td>
                                <td>{field["description"]}</td>
                            </tr>
"""
        
        html += """
                        </tbody>
                    </table>
                </div>
"""
        
        if table["sql_query"]:
            html += f"""
                <div class="card">
                    <h2>Example Query</h2>
                    <pre><code>{table["sql_query"]}</code></pre>
                </div>
"""
        
        html += """
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <script src="js/script.js"></script>
</body>
</html>
"""
    
    # Write HTML to file
    with open(os.path.join(DASHBOARD_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    
    logger.info("Dashboard HTML generated")

def main():
    """Main function to generate the interactive dashboard"""
    logger.info("Starting dashboard generation...")
    
    # Create dashboard structure
    create_dashboard_structure()
    
    # Create CSS and JavaScript
    create_css()
    create_javascript()
    
    # Collect table information
    tables = collect_table_info()
    
    # Generate dashboard HTML
    generate_dashboard_html(tables)
    
    logger.info(f"Dashboard generation complete! Open {os.path.join(DASHBOARD_DIR, 'index.html')} to view.")

if __name__ == "__main__":
    main()
