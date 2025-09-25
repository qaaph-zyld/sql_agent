"""
Response Processor Module for SQL Agent

This module handles the formatting, customization, and visualization of SQL query results.
It provides a flexible framework for transforming raw query results into various output formats
and visualizations based on user preferences and query characteristics.

The module integrates with the changelog system following the mandatory protocol:
- Pre-Response: Changelog update execution
- Response Body: Core functionality delivery
- Post-Response: System validation
- Error Handling: Recovery protocol activation
"""

import os
import sys
import json
import time
import logging
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Union, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/response_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResponseProcessor:
    """
    Handles the processing, formatting, and visualization of SQL query results.
    
    This class provides methods for transforming raw query results into various
    output formats and visualizations based on user preferences and query characteristics.
    It integrates with the changelog system to maintain a record of all processing operations.
    """
    
    def __init__(self, output_dir: str = "output", visualization_dir: str = "visualizations"):
        """
        Initialize the ResponseProcessor with output directories and changelog integration.
        
        Args:
            output_dir: Directory for storing formatted output files
            visualization_dir: Directory for storing generated visualizations
        """
        logger.info("Initializing ResponseProcessor")
        
        # Initialize changelog engine
        self.changelog_engine = ChangelogEngine()
        
        # Record initialization in changelog
        self.changelog_engine.quick_update(
            action_summary="Initializing ResponseProcessor",
            changes=["Setting up output directories", "Configuring formatting options"],
            files=[("CREATE", "scripts/processing/response_processor.py", "Response processor initialization")]
        )
        
        # Set up output directories
        self.output_dir = Path(output_dir)
        self.visualization_dir = Path(visualization_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.visualization_dir.mkdir(exist_ok=True)
        
        # Initialize formatting options
        self.formatting_options = {
            "default_format": "table",
            "available_formats": ["table", "json", "csv", "markdown", "html"],
            "date_format": "%Y-%m-%d",
            "number_format": "{:.2f}",
            "max_rows": 1000,
            "truncate_large_values": True,
            "max_value_length": 100
        }
        
        # Initialize visualization options
        self.visualization_options = {
            "default_chart": "bar",
            "available_charts": ["bar", "line", "pie", "scatter", "histogram"],
            "figure_size": (10, 6),
            "dpi": 100,
            "color_scheme": "tableau10",
            "include_grid": True,
            "include_title": True,
            "include_legend": True
        }
        
        logger.info(f"ResponseProcessor initialized with output_dir={output_dir}, visualization_dir={visualization_dir}")
    
    def format_results(self, results: Dict[str, Any], output_format: str = None) -> Dict[str, Any]:
        """
        Format query results according to specified format and options.
        
        Args:
            results: Dictionary containing query results and metadata
            output_format: Desired output format (table, json, csv, markdown, html)
            
        Returns:
            Dictionary containing formatted results and metadata
        """
        # Update changelog before processing
        self.changelog_engine.quick_update(
            action_summary="Formatting query results",
            changes=[f"Converting results to {output_format or self.formatting_options['default_format']} format"],
            files=[("MODIFY", "scripts/processing/response_processor.py", "Result formatting")]
        )
        
        start_time = time.time()
        logger.info(f"Formatting results to {output_format or self.formatting_options['default_format']}")
        
        # Use default format if none specified
        if not output_format:
            output_format = self.formatting_options["default_format"]
        
        # Ensure output format is valid
        if output_format not in self.formatting_options["available_formats"]:
            logger.warning(f"Invalid output format: {output_format}. Using default format.")
            output_format = self.formatting_options["default_format"]
        
        # Convert results to pandas DataFrame if not already
        if "data" not in results:
            logger.error("No data found in results dictionary")
            return {"error": "No data found in results"}
        
        data = results["data"]
        if not isinstance(data, pd.DataFrame):
            try:
                # Convert list of dictionaries to DataFrame
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    df = pd.DataFrame(data)
                # Convert dictionary of lists to DataFrame
                elif isinstance(data, dict) and all(isinstance(item, list) for item in data.values()):
                    df = pd.DataFrame(data)
                else:
                    logger.error("Unsupported data format for conversion to DataFrame")
                    return {"error": "Unsupported data format"}
            except Exception as e:
                logger.error(f"Error converting data to DataFrame: {str(e)}")
                return {"error": f"Error formatting results: {str(e)}"}
        else:
            df = data
        
        # Apply formatting based on output format
        formatted_data = None
        if output_format == "table":
            formatted_data = df.to_string(index=False)
        elif output_format == "json":
            formatted_data = df.to_json(orient="records")
        elif output_format == "csv":
            formatted_data = df.to_csv(index=False)
        elif output_format == "markdown":
            formatted_data = df.to_markdown(index=False)
        elif output_format == "html":
            formatted_data = df.to_html(index=False)
        
        # Prepare response with metadata
        response = {
            "formatted_data": formatted_data,
            "format": output_format,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "processing_time_ms": round((time.time() - start_time) * 1000, 2),
            "original_results": results
        }
        
        logger.info(f"Results formatted successfully in {response['processing_time_ms']}ms")
        return response
    
    def visualize_data(self, data: Union[Dict[str, Any], pd.DataFrame], chart_type: str = None, 
                      title: str = None, x_column: str = None, y_column: str = None, 
                      filename: str = None) -> Dict[str, Any]:
        """
        Generate visualizations from query results.
        
        Args:
            data: Query results as DataFrame or dictionary with 'data' key
            chart_type: Type of chart to generate (bar, line, pie, scatter, histogram)
            title: Chart title
            x_column: Column to use for x-axis
            y_column: Column to use for y-axis
            filename: Output filename for the visualization
            
        Returns:
            Dictionary containing visualization metadata and file path
        """
        # Update changelog before processing
        self.changelog_engine.quick_update(
            action_summary="Generating data visualization",
            changes=[f"Creating {chart_type or self.visualization_options['default_chart']} chart"],
            files=[("MODIFY", "scripts/processing/response_processor.py", "Data visualization")]
        )
        
        start_time = time.time()
        logger.info(f"Generating {chart_type or self.visualization_options['default_chart']} visualization")
        
        # Use default chart type if none specified
        if not chart_type:
            chart_type = self.visualization_options["default_chart"]
        
        # Ensure chart type is valid
        if chart_type not in self.visualization_options["available_charts"]:
            logger.warning(f"Invalid chart type: {chart_type}. Using default chart.")
            chart_type = self.visualization_options["default_chart"]
        
        # Extract DataFrame from input
        if isinstance(data, dict) and "data" in data:
            if isinstance(data["data"], pd.DataFrame):
                df = data["data"]
            else:
                try:
                    df = pd.DataFrame(data["data"])
                except Exception as e:
                    logger.error(f"Error converting data to DataFrame: {str(e)}")
                    return {"error": f"Error creating visualization: {str(e)}"}
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                logger.error(f"Error converting data to DataFrame: {str(e)}")
                return {"error": f"Error creating visualization: {str(e)}"}
        
        # Ensure we have data to visualize
        if df.empty:
            logger.error("No data to visualize")
            return {"error": "No data to visualize"}
        
        # Determine columns to use for visualization
        columns = list(df.columns)
        if not x_column and len(columns) > 0:
            x_column = columns[0]
        if not y_column and len(columns) > 1:
            y_column = columns[1]
        elif not y_column and len(columns) == 1:
            y_column = columns[0]
            
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{chart_type}_chart_{timestamp}.png"
        
        # Create visualization directory if it doesn't exist
        self.visualization_dir.mkdir(exist_ok=True)
        filepath = self.visualization_dir / filename
        
        # Set up the figure
        plt.figure(figsize=self.visualization_options["figure_size"], dpi=self.visualization_options["dpi"])
        
        # Generate the visualization based on chart type
        try:
            if chart_type == "bar":
                self._create_bar_chart(df, x_column, y_column, title)
            elif chart_type == "line":
                self._create_line_chart(df, x_column, y_column, title)
            elif chart_type == "pie":
                self._create_pie_chart(df, x_column, y_column, title)
            elif chart_type == "scatter":
                self._create_scatter_chart(df, x_column, y_column, title)
            elif chart_type == "histogram":
                self._create_histogram_chart(df, y_column, title)
            
            # Save the figure
            plt.tight_layout()
            plt.savefig(filepath)
            plt.close()
            
            logger.info(f"Visualization saved to {filepath}")
            
            # Prepare response with metadata
            response = {
                "chart_type": chart_type,
                "filepath": str(filepath),
                "x_column": x_column,
                "y_column": y_column,
                "title": title,
                "row_count": len(df),
                "processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating visualization: {str(e)}")
            return {"error": f"Error creating visualization: {str(e)}"}
    
    def _create_bar_chart(self, df: pd.DataFrame, x_column: str, y_column: str, title: str = None):
        """
        Create a bar chart visualization.
        """
        ax = df.plot(kind="bar", x=x_column, y=y_column)
        if title:
            plt.title(title)
        else:
            plt.title(f"{y_column} by {x_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        if self.visualization_options["include_grid"]:
            plt.grid(True, alpha=0.3)
        
    def _create_line_chart(self, df: pd.DataFrame, x_column: str, y_column: str, title: str = None):
        """
        Create a line chart visualization.
        """
        ax = df.plot(kind="line", x=x_column, y=y_column)
        if title:
            plt.title(title)
        else:
            plt.title(f"{y_column} over {x_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        if self.visualization_options["include_grid"]:
            plt.grid(True, alpha=0.3)
    
    def _create_pie_chart(self, df: pd.DataFrame, x_column: str, y_column: str, title: str = None):
        """
        Create a pie chart visualization.
        """
        df.plot(kind="pie", y=y_column, labels=df[x_column], autopct="%1.1f%%")
        if title:
            plt.title(title)
        else:
            plt.title(f"Distribution of {y_column}")
        plt.ylabel("")
        
    def _create_scatter_chart(self, df: pd.DataFrame, x_column: str, y_column: str, title: str = None):
        """
        Create a scatter plot visualization.
        """
        ax = df.plot(kind="scatter", x=x_column, y=y_column)
        if title:
            plt.title(title)
        else:
            plt.title(f"{y_column} vs {x_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        if self.visualization_options["include_grid"]:
            plt.grid(True, alpha=0.3)
            
    def _create_histogram_chart(self, df: pd.DataFrame, column: str, title: str = None):
        """
        Create a histogram visualization.
        """
        ax = df[column].plot(kind="hist", bins=10)
        if title:
            plt.title(title)
        else:
            plt.title(f"Distribution of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        if self.visualization_options["include_grid"]:
            plt.grid(True, alpha=0.3)
    
    def save_results(self, results: Dict[str, Any], filename: str = None, output_format: str = None) -> Dict[str, Any]:
        """
        Save formatted results to a file.
        
        Args:
            results: Dictionary containing query results and metadata
            filename: Output filename (without extension)
            output_format: Output format (json, csv, markdown, html)
            
        Returns:
            Dictionary containing save operation metadata
        """
        # Update changelog before processing
        self.changelog_engine.quick_update(
            action_summary="Saving query results",
            changes=[f"Saving results to {output_format or self.formatting_options['default_format']} file"],
            files=[("MODIFY", "scripts/processing/response_processor.py", "Result saving")]
        )
        
        start_time = time.time()
        
        # Use default format if none specified
        if not output_format:
            output_format = self.formatting_options["default_format"]
        
        # Ensure output format is valid
        if output_format not in self.formatting_options["available_formats"]:
            logger.warning(f"Invalid output format: {output_format}. Using default format.")
            output_format = self.formatting_options["default_format"]
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"query_results_{timestamp}"
        
        # Add extension based on format if not already present
        if output_format == "json" and not filename.endswith(".json"):
            filename = f"{filename}.json"
        elif output_format == "csv" and not filename.endswith(".csv"):
            filename = f"{filename}.csv"
        elif output_format == "markdown" and not filename.endswith(".md"):
            filename = f"{filename}.md"
        elif output_format == "html" and not filename.endswith(".html"):
            filename = f"{filename}.html"
        elif output_format == "table" and not filename.endswith(".txt"):
            filename = f"{filename}.txt"
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        filepath = self.output_dir / filename
        
        # Format results if not already formatted
        if "formatted_data" not in results:
            formatted_results = self.format_results(results, output_format)
            formatted_data = formatted_results["formatted_data"]
        else:
            formatted_data = results["formatted_data"]
        
        # Save the formatted data to file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(formatted_data)
            
            logger.info(f"Results saved to {filepath}")
            
            # Prepare response with metadata
            response = {
                "filepath": str(filepath),
                "format": output_format,
                "size_bytes": os.path.getsize(filepath),
                "processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            return {"error": f"Error saving results: {str(e)}"}
    
    def process_query_results(self, results: Dict[str, Any], output_format: str = None, 
                            visualization: bool = False, chart_type: str = None,
                            save_output: bool = False, filename: str = None) -> Dict[str, Any]:
        """
        Process query results end-to-end with formatting, visualization, and saving.
        
        This method integrates all the response processing capabilities in a single call,
        following the mandatory changelog protocol at each step.
        
        Args:
            results: Dictionary containing query results and metadata
            output_format: Desired output format
            visualization: Whether to generate visualizations
            chart_type: Type of chart to generate
            save_output: Whether to save results to file
            filename: Output filename
            
        Returns:
            Dictionary containing processing results and metadata
        """
        # Update changelog before processing
        self.changelog_engine.quick_update(
            action_summary="Processing query results end-to-end",
            changes=["Formatting results", "Generating visualizations", "Saving output"],
            files=[("MODIFY", "scripts/processing/response_processor.py", "End-to-end processing")]
        )
        
        start_time = time.time()
        logger.info("Starting end-to-end query result processing")
        
        response = {
            "original_results": results,
            "processing_steps": []
        }
        
        # Step 1: Format results
        try:
            formatted_results = self.format_results(results, output_format)
            response["formatted_results"] = formatted_results
            response["processing_steps"].append({
                "step": "format",
                "status": "success",
                "format": formatted_results["format"],
                "processing_time_ms": formatted_results["processing_time_ms"]
            })
        except Exception as e:
            logger.error(f"Error formatting results: {str(e)}")
            response["processing_steps"].append({
                "step": "format",
                "status": "error",
                "error": str(e)
            })
            return response
        
        # Step 2: Generate visualizations if requested
        if visualization:
            try:
                # Determine columns to use for visualization
                if "columns" in formatted_results and len(formatted_results["columns"]) > 0:
                    x_column = formatted_results["columns"][0]
                    y_column = formatted_results["columns"][1] if len(formatted_results["columns"]) > 1 else formatted_results["columns"][0]
                else:
                    x_column = None
                    y_column = None
                
                visualization_results = self.visualize_data(
                    data=results,
                    chart_type=chart_type,
                    x_column=x_column,
                    y_column=y_column,
                    filename=filename
                )
                
                response["visualization_results"] = visualization_results
                response["processing_steps"].append({
                    "step": "visualization",
                    "status": "success",
                    "chart_type": visualization_results["chart_type"],
                    "filepath": visualization_results["filepath"],
                    "processing_time_ms": visualization_results["processing_time_ms"]
                })
            except Exception as e:
                logger.error(f"Error generating visualization: {str(e)}")
                response["processing_steps"].append({
                    "step": "visualization",
                    "status": "error",
                    "error": str(e)
                })
        
        # Step 3: Save results if requested
        if save_output:
            try:
                save_results = self.save_results(
                    results=formatted_results,
                    filename=filename,
                    output_format=output_format
                )
                
                response["save_results"] = save_results
                response["processing_steps"].append({
                    "step": "save",
                    "status": "success",
                    "filepath": save_results["filepath"],
                    "format": save_results["format"],
                    "processing_time_ms": save_results["processing_time_ms"]
                })
            except Exception as e:
                logger.error(f"Error saving results: {str(e)}")
                response["processing_steps"].append({
                    "step": "save",
                    "status": "error",
                    "error": str(e)
                })
        
        # Calculate total processing time
        response["total_processing_time_ms"] = round((time.time() - start_time) * 1000, 2)
        logger.info(f"End-to-end processing completed in {response['total_processing_time_ms']}ms")
        
        return response
