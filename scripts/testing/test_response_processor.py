"""
Unit Tests for Response Processor

This module contains unit tests for the Response Processor component,
demonstrating the test framework with changelog integration.
"""

import os
import sys
import json
import unittest
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test framework and modules to test
from testing.test_framework import SQLAgentTestCase, run_test_suite
from processing.response_processor import ResponseProcessor
from core.changelog_engine import ChangelogEngine

class TestResponseProcessor(SQLAgentTestCase):
    """Test cases for Response Processor"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        
        # Create test directories
        self.test_output_dir = Path("test_output")
        self.test_viz_dir = Path("test_visualizations")
        self.test_output_dir.mkdir(exist_ok=True)
        self.test_viz_dir.mkdir(exist_ok=True)
        
        # Initialize response processor
        self.processor = ResponseProcessor(
            output_dir=str(self.test_output_dir),
            visualization_dir=str(self.test_viz_dir)
        )
        
        # Create test data
        self.test_data = {
            "data": pd.DataFrame({
                "Category": ["A", "B", "C", "D", "E"],
                "Value": [10, 20, 15, 30, 25]
            }),
            "query": "SELECT Category, Value FROM test_table",
            "execution_time_ms": 45.2,
            "row_count": 5
        }
    
    def test_format_results_table(self):
        """Test formatting results as table"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing table format",
            changes=["Verifying table format functionality"],
            files=[("READ", "scripts/processing/response_processor.py", "Format testing")]
        )
        
        # Response Body: Core functionality delivery
        result = self.processor.format_results(self.test_data, "table")
        
        # Post-Response: System validation
        self.assertIn("formatted_data", result)
        self.assertEqual(result["format"], "table")
        self.assertIsInstance(result["processing_time_ms"], float)
        self.assertIn("Category", result["formatted_data"])
        self.assertIn("Value", result["formatted_data"])
    
    def test_format_results_json(self):
        """Test formatting results as JSON"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing JSON format",
            changes=["Verifying JSON format functionality"],
            files=[("READ", "scripts/processing/response_processor.py", "Format testing")]
        )
        
        # Response Body: Core functionality delivery
        result = self.processor.format_results(self.test_data, "json")
        
        # Post-Response: System validation
        self.assertIn("formatted_data", result)
        self.assertEqual(result["format"], "json")
        
        # Verify JSON is valid
        json_data = json.loads(result["formatted_data"])
        self.assertEqual(len(json_data), 5)
        self.assertIn("Category", json_data[0])
        self.assertIn("Value", json_data[0])
    
    def test_format_results_csv(self):
        """Test formatting results as CSV"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing CSV format",
            changes=["Verifying CSV format functionality"],
            files=[("READ", "scripts/processing/response_processor.py", "Format testing")]
        )
        
        # Response Body: Core functionality delivery
        result = self.processor.format_results(self.test_data, "csv")
        
        # Post-Response: System validation
        self.assertIn("formatted_data", result)
        self.assertEqual(result["format"], "csv")
        self.assertIn("Category,Value", result["formatted_data"])
        
        # Count rows (header + 5 data rows)
        self.assertEqual(result["formatted_data"].count("\n"), 5)
    
    def test_visualize_data_bar(self):
        """Test bar chart visualization"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing bar chart visualization",
            changes=["Verifying bar chart generation"],
            files=[("READ", "scripts/processing/response_processor.py", "Visualization testing")]
        )
        
        # Response Body: Core functionality delivery
        result = self.processor.visualize_data(
            data=self.test_data,
            chart_type="bar",
            x_column="Category",
            y_column="Value",
            title="Test Bar Chart"
        )
        
        # Post-Response: System validation
        self.assertEqual(result["chart_type"], "bar")
        self.assertIn("filepath", result)
        self.assertTrue(os.path.exists(result["filepath"]))
        self.assertIsInstance(result["processing_time_ms"], float)
    
    def test_visualize_data_pie(self):
        """Test pie chart visualization"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing pie chart visualization",
            changes=["Verifying pie chart generation"],
            files=[("READ", "scripts/processing/response_processor.py", "Visualization testing")]
        )
        
        # Response Body: Core functionality delivery
        result = self.processor.visualize_data(
            data=self.test_data,
            chart_type="pie",
            x_column="Category",
            y_column="Value",
            title="Test Pie Chart"
        )
        
        # Post-Response: System validation
        self.assertEqual(result["chart_type"], "pie")
        self.assertIn("filepath", result)
        self.assertTrue(os.path.exists(result["filepath"]))
        self.assertIsInstance(result["processing_time_ms"], float)
    
    def test_save_results(self):
        """Test saving results to file"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing result saving",
            changes=["Verifying file saving functionality"],
            files=[("READ", "scripts/processing/response_processor.py", "Save testing")]
        )
        
        # First format results
        formatted = self.processor.format_results(self.test_data, "json")
        
        # Response Body: Core functionality delivery
        result = self.processor.save_results(
            results=formatted,
            filename="test_save_results",
            output_format="json"
        )
        
        # Post-Response: System validation
        self.assertIn("filepath", result)
        self.assertEqual(result["format"], "json")
        self.assertTrue(os.path.exists(result["filepath"]))
        self.assertIsInstance(result["size_bytes"], int)
        self.assertGreater(result["size_bytes"], 0)
    
    def test_process_query_results(self):
        """Test end-to-end processing"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing end-to-end processing",
            changes=["Verifying complete processing pipeline"],
            files=[("READ", "scripts/processing/response_processor.py", "End-to-end testing")]
        )
        
        # Response Body: Core functionality delivery
        result = self.processor.process_query_results(
            results=self.test_data,
            output_format="markdown",
            visualization=True,
            chart_type="bar",
            save_output=True,
            filename="test_end_to_end"
        )
        
        # Post-Response: System validation
        self.assertIn("formatted_results", result)
        self.assertIn("visualization_results", result)
        self.assertIn("save_results", result)
        self.assertIn("processing_steps", result)
        self.assertEqual(len(result["processing_steps"]), 3)  # format, viz, save
        self.assertIsInstance(result["total_processing_time_ms"], float)
        
        # Verify all steps succeeded
        for step in result["processing_steps"]:
            self.assertEqual(step["status"], "success")
    
    def test_invalid_chart_type(self):
        """Test error handling with invalid chart type"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing error handling",
            changes=["Verifying error recovery for invalid chart type"],
            files=[("READ", "scripts/processing/response_processor.py", "Error handling testing")]
        )
        
        # Response Body: Core functionality delivery with expected error
        result = self.processor.visualize_data(
            data=self.test_data,
            chart_type="invalid_chart_type",
            x_column="Category",
            y_column="Value"
        )
        
        # Post-Response: System validation
        self.assertEqual(result["chart_type"], "bar")  # Should default to bar
        self.assertIn("warning", result)
        self.assertIn("Invalid chart type", result["warning"])
    
    def tearDown(self):
        """Clean up test environment"""
        super().tearDown()
        
        # Error Handling: Recovery protocol activation
        self.changelog_engine.quick_update(
            action_summary="Test cleanup",
            changes=["Cleaning up test environment"],
            files=[("READ", "scripts/testing/test_response_processor.py", "Test cleanup")]
        )


if __name__ == "__main__":
    # Run tests with changelog integration
    results = run_test_suite(TestResponseProcessor, "ResponseProcessorTests")
    
    # Output results
    print(f"\nTest Results Summary:")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Pass Rate: {results['pass_rate']}%")
    print(f"Execution Time: {results['total_execution_time_ms']}ms")
    
    # Update changelog with final test results
    changelog_engine = ChangelogEngine()
    changelog_engine.quick_update(
        action_summary="Completed Response Processor Unit Tests",
        changes=[
            f"Executed {results['total_tests']} tests with {results['passed_tests']} passed and {results['failed_tests']} failed",
            f"Pass rate: {results['pass_rate']}%",
            f"Total execution time: {results['total_execution_time_ms']}ms"
        ],
        files=[
            ("CREATE", "scripts/testing/test_response_processor.py", "Response processor unit tests"),
            ("READ", "scripts/processing/response_processor.py", "Component being tested")
        ]
    )
