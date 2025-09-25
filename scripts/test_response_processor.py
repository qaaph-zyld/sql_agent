"""
Test script for Response Processor

This script demonstrates the functionality of the ResponseProcessor class,
including result formatting, visualization, and saving capabilities.
It follows the mandatory changelog protocol at each step.
"""

import os
import sys
import json
import time
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from processing.response_processor import ResponseProcessor
from core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/test_response_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main test function to demonstrate ResponseProcessor functionality
    """
    # Initialize changelog engine for test script
    changelog_engine = ChangelogEngine()
    changelog_engine.quick_update(
        action_summary="Testing Response Processor",
        changes=["Running comprehensive tests for response processor"],
        files=[("READ", "scripts/processing/response_processor.py", "Testing response processor functionality")]
    )
    
    logger.info("Starting Response Processor tests")
    start_time = time.time()
    
    # Create test output directories
    output_dir = Path("test_output")
    visualization_dir = Path("test_visualizations")
    output_dir.mkdir(exist_ok=True)
    visualization_dir.mkdir(exist_ok=True)
    
    # Initialize ResponseProcessor
    processor = ResponseProcessor(
        output_dir=str(output_dir),
        visualization_dir=str(visualization_dir)
    )
    
    # Create test data
    test_data = {
        "data": pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Sales": [1000, 1200, 900, 1500, 1800, 1300],
            "Expenses": [800, 850, 900, 950, 1000, 1050],
            "Profit": [200, 350, 0, 550, 800, 250]
        }),
        "query": "SELECT Month, Sales, Expenses, Profit FROM monthly_data",
        "execution_time_ms": 120.5,
        "row_count": 6
    }
    
    # Test 1: Format results in different formats
    logger.info("Test 1: Formatting results in different formats")
    formats = ["table", "json", "csv", "markdown", "html"]
    formatting_results = {}
    
    for fmt in formats:
        logger.info(f"Testing {fmt} format")
        result = processor.format_results(test_data, fmt)
        formatting_results[fmt] = result
        logger.info(f"Format {fmt} processing time: {result['processing_time_ms']}ms")
    
    # Save formatting test results
    with open(output_dir / "formatting_test_results.json", "w") as f:
        json.dump({k: {"format": v["format"], "processing_time_ms": v["processing_time_ms"]} 
                  for k, v in formatting_results.items()}, f, indent=2)
    
    # Test 2: Visualization capabilities
    logger.info("Test 2: Testing visualization capabilities")
    chart_types = ["bar", "line", "pie", "scatter", "histogram"]
    visualization_results = {}
    
    for chart in chart_types:
        logger.info(f"Testing {chart} chart")
        result = processor.visualize_data(
            data=test_data,
            chart_type=chart,
            x_column="Month",
            y_column="Sales",
            title=f"Monthly Sales - {chart.capitalize()} Chart"
        )
        visualization_results[chart] = result
        logger.info(f"Chart {chart} saved to {result['filepath']}")
    
    # Save visualization test results
    with open(output_dir / "visualization_test_results.json", "w") as f:
        json.dump({k: {"chart_type": v["chart_type"], "filepath": v["filepath"], "processing_time_ms": v["processing_time_ms"]} 
                  for k, v in visualization_results.items()}, f, indent=2)
    
    # Test 3: Saving results to files
    logger.info("Test 3: Testing save capabilities")
    save_results = {}
    
    for fmt in formats:
        logger.info(f"Testing saving in {fmt} format")
        result = processor.save_results(
            results=formatting_results[fmt],
            filename=f"test_save_{fmt}",
            output_format=fmt
        )
        save_results[fmt] = result
        logger.info(f"Results saved to {result['filepath']}")
    
    # Save save test results
    with open(output_dir / "save_test_results.json", "w") as f:
        json.dump({k: {"format": v["format"], "filepath": v["filepath"], "size_bytes": v["size_bytes"]} 
                  for k, v in save_results.items()}, f, indent=2)
    
    # Test 4: End-to-end processing
    logger.info("Test 4: Testing end-to-end processing")
    end_to_end_results = {}
    
    for fmt in formats:
        for chart in chart_types[:2]:  # Test with first two chart types only
            logger.info(f"Testing end-to-end processing with {fmt} format and {chart} chart")
            result = processor.process_query_results(
                results=test_data,
                output_format=fmt,
                visualization=True,
                chart_type=chart,
                save_output=True,
                filename=f"end_to_end_{fmt}_{chart}"
            )
            end_to_end_results[f"{fmt}_{chart}"] = result
            logger.info(f"End-to-end processing completed in {result['total_processing_time_ms']}ms")
    
    # Save end-to-end test results
    with open(output_dir / "end_to_end_test_results.json", "w") as f:
        json.dump({k: {"total_processing_time_ms": v["total_processing_time_ms"], "steps": len(v["processing_steps"])} 
                  for k, v in end_to_end_results.items()}, f, indent=2)
    
    # Generate test summary
    total_time = round((time.time() - start_time) * 1000, 2)
    test_summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": 4,
        "formats_tested": formats,
        "charts_tested": chart_types,
        "total_processing_time_ms": total_time,
        "test_results": {
            "formatting": len(formatting_results),
            "visualization": len(visualization_results),
            "saving": len(save_results),
            "end_to_end": len(end_to_end_results)
        }
    }
    
    # Save test summary
    with open(output_dir / "test_summary.json", "w") as f:
        json.dump(test_summary, f, indent=2)
    
    logger.info(f"All tests completed in {total_time}ms")
    logger.info(f"Test results saved to {output_dir}")
    
    # Update changelog with test completion
    changelog_engine.quick_update(
        action_summary="Completed Response Processor Testing",
        changes=[
            "Tested formatting capabilities with multiple formats",
            "Tested visualization capabilities with multiple chart types",
            "Tested saving capabilities with multiple formats",
            "Tested end-to-end processing with various combinations"
        ],
        files=[
            ("CREATE", "scripts/test_response_processor.py", "Response processor test implementation"),
            ("CREATE", "test_output/test_summary.json", "Test results summary")
        ]
    )
    
    return test_summary

if __name__ == "__main__":
    main()
