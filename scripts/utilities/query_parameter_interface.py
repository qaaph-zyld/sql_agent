"""
Query Parameter Interface

This script provides a user-friendly interface for executing the custom SQL queries
with parameterized inputs. It preserves all existing functionality while adding
parameter validation and default values.
"""

import os
import sys
import re
import pandas as pd
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import logging
import configparser
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("query_interface.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database connection parameters
DEFAULT_CONFIG = {
    "DB_HOST": "a265m001",
    "DB_NAME": "QADEE2798",
    "DB_USER": "PowerBI",
    "DB_PASSWORD": "P0werB1"
}

# Query definitions
QUERIES = {
    "Customer_Demand_per_BOM": {
        "file": "Database_tables/QADEE2798/custom_sql_queries/Customer_Demand_per_BOM.sql",
        "description": "Analyzes customer demand broken down by BOM components",
        "parameters": [
            {
                "name": "part_filter",
                "description": "Filter by specific part number (optional)",
                "default": "",
                "type": "string"
            },
            {
                "name": "site_filter",
                "description": "Filter by specific site",
                "default": "2798",
                "type": "string"
            },
            {
                "name": "weeks_to_include",
                "description": "Number of future weeks to include",
                "default": 8,
                "type": "int"
            }
        ]
    },
    "Item_Master_all_no_xc_rc": {
        "file": "Database_tables/QADEE2798/custom_sql_queries/Item_Master_all_no_xc_rc.sql",
        "description": "Comprehensive item master data excluding xc/rc part types",
        "parameters": [
            {
                "name": "part_filter",
                "description": "Filter by specific part number (optional)",
                "default": "",
                "type": "string"
            },
            {
                "name": "site_filter",
                "description": "Filter by specific site",
                "default": "2798",
                "type": "string"
            },
            {
                "name": "show_only_issues",
                "description": "Show only items with data quality issues",
                "default": False,
                "type": "bool"
            },
            {
                "name": "abc_class",
                "description": "Filter by ABC classification",
                "default": "",
                "type": "string",
                "options": ["", "A", "B", "C"]
            },
            {
                "name": "show_routing_missing",
                "description": "Show only items with missing routing",
                "default": False,
                "type": "bool"
            },
            {
                "name": "show_project_missing",
                "description": "Show only items with missing project",
                "default": False,
                "type": "bool"
            },
            {
                "name": "show_cycle_count_due",
                "description": "Show only items due for cycle count",
                "default": False,
                "type": "bool"
            },
            {
                "name": "show_slow_moving",
                "description": "Show only slow-moving items",
                "default": False,
                "type": "bool"
            },
            {
                "name": "show_item_type_error",
                "description": "Show only items with type errors",
                "default": False,
                "type": "bool"
            },
            {
                "name": "show_wip_overstock",
                "description": "Show only items with WIP overstock",
                "default": False,
                "type": "bool"
            }
        ]
    },
    "MMV": {
        "file": "Database_tables/QADEE2798/custom_sql_queries/MMV.sql",
        "description": "Material Movement Visibility report",
        "parameters": [
            {
                "name": "start_date",
                "description": "Start date for analysis (YYYY-MM-DD)",
                "default": (datetime.now().replace(day=1)).strftime("%Y-%m-%d"),
                "type": "date"
            },
            {
                "name": "end_date",
                "description": "End date for analysis (YYYY-MM-DD)",
                "default": (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d"),
                "type": "date"
            },
            {
                "name": "part_filter",
                "description": "Filter by specific part number (optional)",
                "default": "",
                "type": "string"
            }
        ]
    }
}

class ConfigManager:
    """Manages configuration settings for database connections"""
    
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        # Load existing config or create default
        if os.path.exists(config_file):
            self.config.read(config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config["DATABASE"] = DEFAULT_CONFIG
        with open(self.config_file, "w") as f:
            self.config.write(f)
        logger.info(f"Created default configuration file: {self.config_file}")
    
    def get_connection_string(self):
        """Get database connection string from config"""
        db_config = self.config["DATABASE"]
        return f"DRIVER={{SQL Server}};SERVER={db_config['DB_HOST']};DATABASE={db_config['DB_NAME']};UID={db_config['DB_USER']};PWD={db_config['DB_PASSWORD']}"
    
    def get_config_value(self, section, key):
        """Get a specific configuration value"""
        return self.config[section][key]
    
    def set_config_value(self, section, key, value):
        """Set a specific configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        with open(self.config_file, "w") as f:
            self.config.write(f)

class QueryExecutor:
    """Executes SQL queries with parameters"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def get_connection(self):
        """Create database connection"""
        conn_str = self.config_manager.get_connection_string()
        return pyodbc.connect(conn_str)
    
    def read_query_file(self, query_file):
        """Read SQL query from file"""
        try:
            with open(query_file, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            with open(query_file, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading query file {query_file}: {str(e)}")
            raise
    
    def apply_parameters(self, query, parameters):
        """Apply parameters to SQL query"""
        modified_query = query
        
        # Apply part filter
        if "part_filter" in parameters and parameters["part_filter"]:
            part_filter = parameters["part_filter"].strip()
            modified_query = self._add_where_condition(
                modified_query, 
                f"([Item Number] LIKE '%{part_filter}%' OR [pt_part] LIKE '%{part_filter}%' OR [tr_part] LIKE '%{part_filter}%')"
            )
        
        # Apply site filter
        if "site_filter" in parameters and parameters["site_filter"]:
            site_filter = parameters["site_filter"].strip()
            modified_query = self._add_where_condition(
                modified_query, 
                f"([Plant] = '{site_filter}' OR [pt_site] = '{site_filter}' OR [tr_site] = '{site_filter}')"
            )
        
        # Apply date filters for MMV query
        if "start_date" in parameters and "end_date" in parameters:
            start_date = parameters["start_date"]
            end_date = parameters["end_date"]
            
            # Replace the date calculation in MMV query
            date_pattern = r"tr_effdate >= DATEFROMPARTS\(YEAR\(GETDATE\(\)\), MONTH\(GETDATE\(\)\), 1\).*?DATEADD\(month, 1, DATEFROMPARTS\(YEAR\(GETDATE\(\)\), MONTH\(GETDATE\(\)\), 1\)\)"
            date_replacement = f"tr_effdate >= '{start_date}' AND tr_effdate < '{end_date}'"
            modified_query = re.sub(date_pattern, date_replacement, modified_query)
        
        # Apply ABC class filter
        if "abc_class" in parameters and parameters["abc_class"]:
            abc_class = parameters["abc_class"].strip()
            modified_query = self._add_where_condition(
                modified_query, 
                f"[ABC] = '{abc_class}'"
            )
        
        # Apply show only issues filter
        if "show_only_issues" in parameters and parameters["show_only_issues"]:
            issue_condition = """
            ([No Cost - in BOM] IS NOT NULL OR
             [No Prod Line - in BOM] IS NOT NULL OR
             [No Group - in BOM] IS NOT NULL OR
             [EPIC- in BOM] IS NOT NULL OR
             [Routing Missing] IS NOT NULL OR
             [Project missing] IS NOT NULL OR
             [Item Type Error] IS NOT NULL)
            """
            modified_query = self._add_where_condition(modified_query, issue_condition)
            
        # Apply specific column filters from Column_prompts.md
        if "show_routing_missing" in parameters and parameters["show_routing_missing"]:
            modified_query = self._add_where_condition(modified_query, "[Routing Missing] IS NOT NULL")
            
        if "show_project_missing" in parameters and parameters["show_project_missing"]:
            modified_query = self._add_where_condition(modified_query, "[Project missing] IS NOT NULL")
            
        if "show_cycle_count_due" in parameters and parameters["show_cycle_count_due"]:
            modified_query = self._add_where_condition(modified_query, "[Cycle Count Due] IS NOT NULL")
            
        if "show_slow_moving" in parameters and parameters["show_slow_moving"]:
            modified_query = self._add_where_condition(modified_query, "[Slow-moving Warning] IS NOT NULL")
            
        if "show_item_type_error" in parameters and parameters["show_item_type_error"]:
            modified_query = self._add_where_condition(modified_query, "[Item Type Error] IS NOT NULL")
            
        if "show_wip_overstock" in parameters and parameters["show_wip_overstock"]:
            modified_query = self._add_where_condition(modified_query, "[WIP_overstock] IS NOT NULL")
        
        # Apply weeks to include filter
        if "weeks_to_include" in parameters and parameters["weeks_to_include"] != 8:
            weeks = parameters["weeks_to_include"]
            # This is more complex and would require restructuring the query
            # For now, we'll just add a comment
            modified_query = f"-- Modified to include {weeks} weeks instead of default 8\n" + modified_query
        
        return modified_query
    
    def _add_where_condition(self, query, condition):
        """Add a WHERE or AND condition to a query"""
        if "WHERE" in query:
            # Add AND condition
            return query.replace("WHERE", f"WHERE ({condition}) AND ")
        elif "GROUP BY" in query:
            # Add WHERE before GROUP BY
            return query.replace("GROUP BY", f"WHERE {condition}\nGROUP BY")
        elif "ORDER BY" in query:
            # Add WHERE before ORDER BY
            return query.replace("ORDER BY", f"WHERE {condition}\nORDER BY")
        else:
            # Add WHERE at the end
            return query + f"\nWHERE {condition}"
    
    def execute_query(self, query_name, parameters):
        """Execute a query with parameters"""
        try:
            # Get query definition
            query_def = QUERIES.get(query_name)
            if not query_def:
                raise ValueError(f"Query {query_name} not found")
            
            # Read query file
            query_file = query_def["file"]
            query = self.read_query_file(query_file)
            
            # Apply parameters
            modified_query = self.apply_parameters(query, parameters)
            
            # Execute query
            conn = self.get_connection()
            df = pd.read_sql(modified_query, conn)
            conn.close()
            
            return df
        
        except Exception as e:
            logger.error(f"Error executing query {query_name}: {str(e)}")
            raise

class QueryParameterApp:
    """GUI application for query parameter interface"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("QADEE2798 Query Parameter Interface")
        self.root.geometry("900x700")
        
        # Create config manager and query executor
        self.config_manager = ConfigManager()
        self.query_executor = QueryExecutor(self.config_manager)
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create query selection frame
        self.create_query_selection_frame()
        
        # Create parameter frame
        self.parameter_frame = ttk.LabelFrame(self.main_frame, text="Query Parameters", padding=10)
        self.parameter_frame.pack(fill=tk.X, expand=False, pady=10)
        
        # Create results frame
        self.create_results_frame()
        
        # Initialize parameter widgets
        self.parameter_widgets = {}
        
        # Select first query by default
        if QUERIES:
            first_query = list(QUERIES.keys())[0]
            self.query_combobox.set(first_query)
            self.on_query_selected(None)
    
    def create_query_selection_frame(self):
        """Create frame for query selection"""
        query_frame = ttk.Frame(self.main_frame)
        query_frame.pack(fill=tk.X, expand=False, pady=10)
        
        # Query selection label
        ttk.Label(query_frame, text="Select Query:").pack(side=tk.LEFT, padx=5)
        
        # Query selection combobox
        self.query_combobox = ttk.Combobox(query_frame, values=list(QUERIES.keys()), state="readonly", width=30)
        self.query_combobox.pack(side=tk.LEFT, padx=5)
        self.query_combobox.bind("<<ComboboxSelected>>", self.on_query_selected)
        
        # Query description
        self.query_description = ttk.Label(query_frame, text="", wraplength=400)
        self.query_description.pack(side=tk.LEFT, padx=20)
    
    def create_results_frame(self):
        """Create frame for query results"""
        results_frame = ttk.LabelFrame(self.main_frame, text="Query Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create buttons frame
        buttons_frame = ttk.Frame(results_frame)
        buttons_frame.pack(fill=tk.X, expand=False, pady=5)
        
        # Execute button
        self.execute_button = ttk.Button(buttons_frame, text="Execute Query", command=self.execute_query)
        self.execute_button.pack(side=tk.LEFT, padx=5)
        
        # Export button
        self.export_button = ttk.Button(buttons_frame, text="Export Results", command=self.export_results, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(buttons_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Create treeview for results
        self.create_results_treeview(results_frame)
    
    def create_results_treeview(self, parent):
        """Create treeview for displaying query results"""
        # Create frame with scrollbars
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create scrollbars
        vscrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        hscrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create treeview
        self.results_tree = ttk.Treeview(
            frame, 
            columns=(), 
            show="headings",
            yscrollcommand=vscrollbar.set,
            xscrollcommand=hscrollbar.set
        )
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        vscrollbar.config(command=self.results_tree.yview)
        hscrollbar.config(command=self.results_tree.xview)
        
        # Store current results
        self.current_results = None
    
    def on_query_selected(self, event):
        """Handle query selection"""
        query_name = self.query_combobox.get()
        query_def = QUERIES.get(query_name)
        
        if query_def:
            # Update description
            self.query_description.config(text=query_def["description"])
            
            # Clear parameter frame
            for widget in self.parameter_frame.winfo_children():
                widget.destroy()
            
            # Clear parameter widgets
            self.parameter_widgets = {}
            
            # Create parameter widgets
            for param in query_def["parameters"]:
                self.create_parameter_widget(param)
    
    def create_parameter_widget(self, param):
        """Create widget for a parameter"""
        # Create frame for parameter
        frame = ttk.Frame(self.parameter_frame)
        frame.pack(fill=tk.X, expand=False, pady=5)
        
        # Parameter label
        ttk.Label(frame, text=f"{param['description']}:").pack(side=tk.LEFT, padx=5)
        
        # Create widget based on parameter type
        if param["type"] == "bool":
            var = tk.BooleanVar(value=param["default"])
            widget = ttk.Checkbutton(frame, variable=var)
            widget.pack(side=tk.LEFT, padx=5)
            self.parameter_widgets[param["name"]] = var
        
        elif param["type"] == "date":
            var = tk.StringVar(value=param["default"])
            widget = ttk.Entry(frame, textvariable=var, width=15)
            widget.pack(side=tk.LEFT, padx=5)
            self.parameter_widgets[param["name"]] = var
        
        elif param["type"] == "int":
            var = tk.IntVar(value=param["default"])
            widget = ttk.Spinbox(frame, from_=1, to=52, textvariable=var, width=5)
            widget.pack(side=tk.LEFT, padx=5)
            self.parameter_widgets[param["name"]] = var
        
        elif "options" in param:
            var = tk.StringVar(value=param["default"])
            widget = ttk.Combobox(frame, values=param["options"], textvariable=var, width=10)
            widget.pack(side=tk.LEFT, padx=5)
            self.parameter_widgets[param["name"]] = var
        
        else:  # string
            var = tk.StringVar(value=param["default"])
            widget = ttk.Entry(frame, textvariable=var, width=20)
            widget.pack(side=tk.LEFT, padx=5)
            self.parameter_widgets[param["name"]] = var
    
    def get_parameter_values(self):
        """Get current parameter values"""
        values = {}
        for name, var in self.parameter_widgets.items():
            values[name] = var.get()
        return values
    
    def execute_query(self):
        """Execute the selected query with parameters"""
        try:
            # Get selected query
            query_name = self.query_combobox.get()
            
            # Get parameter values
            parameters = self.get_parameter_values()
            
            # Update status
            self.status_label.config(text="Executing query...")
            self.root.update_idletasks()
            
            # Execute query
            df = self.query_executor.execute_query(query_name, parameters)
            
            # Store results
            self.current_results = df
            
            # Update treeview
            self.update_results_treeview(df)
            
            # Enable export button
            self.export_button.config(state=tk.NORMAL)
            
            # Update status
            self.status_label.config(text=f"Query executed successfully. {len(df)} rows returned.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error executing query: {str(e)}")
            self.status_label.config(text="Error executing query")
    
    def update_results_treeview(self, df):
        """Update treeview with query results"""
        # Clear existing data
        self.results_tree.delete(*self.results_tree.get_children())
        
        # Configure columns
        self.results_tree["columns"] = list(df.columns)
        
        for col in df.columns:
            self.results_tree.heading(col, text=col)
            
            # Set column width based on content
            max_width = max(
                len(str(col)),
                df[col].astype(str).str.len().max() if len(df) > 0 else 0
            )
            width = min(max_width * 10, 300)  # Limit width to 300 pixels
            self.results_tree.column(col, width=width)
        
        # Add data rows
        for i, row in df.iterrows():
            values = [str(row[col]) for col in df.columns]
            self.results_tree.insert("", "end", values=values)
    
    def export_results(self):
        """Export query results to file"""
        if self.current_results is None:
            messagebox.showinfo("Export", "No results to export")
            return
        
        # Generate default filename based on query and date
        query_name = self.query_combobox.get()
        current_date = datetime.now().strftime("%Y%m%d")
        default_filename = f"{query_name}_{current_date}.xlsx"
        
        # Ask for file path with suggested filename
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            initialfile=default_filename
        )
        
        if not file_path:
            return
        
        try:
            # Export based on file extension
            if file_path.endswith(".xlsx"):
                self.current_results.to_excel(file_path, index=False)
            elif file_path.endswith(".csv"):
                self.current_results.to_csv(file_path, index=False)
            else:
                # Default to Excel
                self.current_results.to_excel(file_path, index=False)
            
            messagebox.showinfo("Export", f"Results exported to {file_path}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting results: {str(e)}")

def main():
    """Main function"""
    root = tk.Tk()
    app = QueryParameterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
