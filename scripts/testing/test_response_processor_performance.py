"""
Performance Tests for Response Processor

This module contains performance tests for the SQL Agent's Response Processor,
measuring the performance of formatting, visualization, and saving operations.

RESPONSE_SEQUENCE {
  1. changelog_engine.update_changelog()
  2. execute_performance_tests()
  3. validation_suite.run_validation()
  4. workspace_state_sync()
}
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from core.changelog_engine import ChangelogEngine
from processing.response_processor import ResponseProcessor
from testing.performance_test_framework import PerformanceTestCase, PerformanceTestSuite, benchmark_function

class ResponseProcessorPerformanceTest(PerformanceTestCase):
    """
    Performance tests for the Response Processor component
    """
    def setUp(self):
        """Set up performance test with changelog update"""
        super().setUp()
        
        # Create test directories
        self.test_dir = Path("test_data/performance")
        self.test_dir.mkdir(exist_ok=True, parents=True)
        self.output_dir = Path("test_output/performance")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create test data
        self.small_data = pd.DataFrame({
            "id": range(1, 101),
            "value": [i * 2 for i in range(1, 101)],
            "category": ["A" if i % 3 == 0 else "B" if i % 3 == 1 else "C" for i in range(1, 101)]
        })
        
        self.medium_data = pd.DataFrame({
            "id": range(1, 1001),
            "value": [i * 2 for i in range(1, 1001)],
            "category": ["A" if i % 3 == 0 else "B" if i % 3 == 1 else "C" for i in range(1, 1001)]
        })
        
        # Create response processor
        self.response_processor = ResponseProcessor(output_dir=str(self.output_dir))
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Setting up response processor performance test environment",
            changes=[
                "Created test data directory and sample data",
                "Initialized response processor with test output directory"
            ],
            files=[
                ("CREATE", str(self.test_dir), "Test data directory"),
                ("CREATE", str(self.output_dir), "Test output directory"),
                ("READ", "scripts/testing/test_response_processor_performance.py", "Performance test setup")
            ]
        )
    
    def test_format_results_performance(self):
        """Test the performance of format_results method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing format_results performance",
            changes=["Measuring performance of different format types with various data sizes"],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
        
        # Test small data with table format
        metrics_small_table = self.measure_performance("ResponseProcessor", "format_results_small_table")
        metrics_small_table.start_measurement()
        self.response_processor.format_results(self.small_data, format_type="table")
        metrics_small_table.end_measurement()
        
        # Test small data with JSON format
        metrics_small_json = self.measure_performance("ResponseProcessor", "format_results_small_json")
        metrics_small_json.start_measurement()
        self.response_processor.format_results(self.small_data, format_type="json")
        metrics_small_json.end_measurement()
        
        # Test medium data with table format
        metrics_medium_table = self.measure_performance("ResponseProcessor", "format_results_medium_table")
        metrics_medium_table.start_measurement()
        self.response_processor.format_results(self.medium_data, format_type="table")
        metrics_medium_table.end_measurement()
        
        # Test medium data with JSON format
        metrics_medium_json = self.measure_performance("ResponseProcessor", "format_results_medium_json")
        metrics_medium_json.start_measurement()
        self.response_processor.format_results(self.medium_data, format_type="json")
        metrics_medium_json.end_measurement()
        
        # Assert performance meets thresholds
        self.assertPerformance("ResponseProcessor", "format_results_small_table", 
                              execution_time_threshold_ms=100)
        self.assertPerformance("ResponseProcessor", "format_results_small_json", 
                              execution_time_threshold_ms=100)
        self.assertPerformance("ResponseProcessor", "format_results_medium_table", 
                              execution_time_threshold_ms=500)
        self.assertPerformance("ResponseProcessor", "format_results_medium_json", 
                              execution_time_threshold_ms=500)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed format_results performance test",
            changes=[
                "Measured performance of format_results with different formats and data sizes",
                "All performance metrics within acceptable thresholds"
            ],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
    
    def test_create_visualization_performance(self):
        """Test the performance of create_visualization method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing create_visualization performance",
            changes=["Measuring performance of different chart types with various data sizes"],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
        
        # Test small data with bar chart
        metrics_small_bar = self.measure_performance("ResponseProcessor", "create_visualization_small_bar")
        metrics_small_bar.start_measurement()
        self.response_processor.create_visualization(
            self.small_data, 
            chart_type="bar",
            x_column="category",
            y_column="value",
            title="Small Data Bar Chart"
        )
        metrics_small_bar.end_measurement()
        
        # Test small data with line chart
        metrics_small_line = self.measure_performance("ResponseProcessor", "create_visualization_small_line")
        metrics_small_line.start_measurement()
        self.response_processor.create_visualization(
            self.small_data, 
            chart_type="line",
            x_column="id",
            y_column="value",
            title="Small Data Line Chart"
        )
        metrics_small_line.end_measurement()
        
        # Test medium data with bar chart
        metrics_medium_bar = self.measure_performance("ResponseProcessor", "create_visualization_medium_bar")
        metrics_medium_bar.start_measurement()
        self.response_processor.create_visualization(
            self.medium_data, 
            chart_type="bar",
            x_column="category",
            y_column="value",
            title="Medium Data Bar Chart"
        )
        metrics_medium_bar.end_measurement()
        
        # Test medium data with line chart
        metrics_medium_line = self.measure_performance("ResponseProcessor", "create_visualization_medium_line")
        metrics_medium_line.start_measurement()
        self.response_processor.create_visualization(
            self.medium_data, 
            chart_type="line",
            x_column="id",
            y_column="value",
            title="Medium Data Line Chart"
        )
        metrics_medium_line.end_measurement()
        
        # Assert performance meets thresholds
        self.assertPerformance("ResponseProcessor", "create_visualization_small_bar", 
                              execution_time_threshold_ms=500)
        self.assertPerformance("ResponseProcessor", "create_visualization_small_line", 
                              execution_time_threshold_ms=500)
        self.assertPerformance("ResponseProcessor", "create_visualization_medium_bar", 
                              execution_time_threshold_ms=1000)
        self.assertPerformance("ResponseProcessor", "create_visualization_medium_line", 
                              execution_time_threshold_ms=1000)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed create_visualization performance test",
            changes=[
                "Measured performance of create_visualization with different chart types and data sizes",
                "All performance metrics within acceptable thresholds"
            ],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
    
    def test_save_results_performance(self):
        """Test the performance of save_results method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing save_results performance",
            changes=["Measuring performance of different file formats with various data sizes"],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
        
        # Test small data with JSON format
        metrics_small_json = self.measure_performance("ResponseProcessor", "save_results_small_json")
        metrics_small_json.start_measurement()
        self.response_processor.save_results(
            self.small_data,
            filename="small_data_json",
            format_type="json"
        )
        metrics_small_json.end_measurement()
        
        # Test small data with CSV format
        metrics_small_csv = self.measure_performance("ResponseProcessor", "save_results_small_csv")
        metrics_small_csv.start_measurement()
        self.response_processor.save_results(
            self.small_data,
            filename="small_data_csv",
            format_type="csv"
        )
        metrics_small_csv.end_measurement()
        
        # Test medium data with JSON format
        metrics_medium_json = self.measure_performance("ResponseProcessor", "save_results_medium_json")
        metrics_medium_json.start_measurement()
        self.response_processor.save_results(
            self.medium_data,
            filename="medium_data_json",
            format_type="json"
        )
        metrics_medium_json.end_measurement()
        
        # Test medium data with CSV format
        metrics_medium_csv = self.measure_performance("ResponseProcessor", "save_results_medium_csv")
        metrics_medium_csv.start_measurement()
        self.response_processor.save_results(
            self.medium_data,
            filename="medium_data_csv",
            format_type="csv"
        )
        metrics_medium_csv.end_measurement()
        
        # Assert performance meets thresholds
        self.assertPerformance("ResponseProcessor", "save_results_small_json", 
                              execution_time_threshold_ms=200)
        self.assertPerformance("ResponseProcessor", "save_results_small_csv", 
                              execution_time_threshold_ms=200)
        self.assertPerformance("ResponseProcessor", "save_results_medium_json", 
                              execution_time_threshold_ms=500)
        self.assertPerformance("ResponseProcessor", "save_results_medium_csv", 
                              execution_time_threshold_ms=500)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed save_results performance test",
            changes=[
                "Measured performance of save_results with different file formats and data sizes",
                "All performance metrics within acceptable thresholds"
            ],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
    
    def test_process_query_results_performance(self):
        """Test the performance of process_query_results method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing process_query_results performance",
            changes=["Measuring performance of end-to-end processing with various data sizes"],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
        
        # Test small data with full processing
        metrics_small = self.measure_performance("ResponseProcessor", "process_query_results_small")
        metrics_small.start_measurement()
        self.response_processor.process_query_results(
            self.small_data,
            format_type="table",
            chart_type="bar",
            x_column="category",
            y_column="value",
            title="Small Data Processing",
            filename="small_data_full",
            save_format="json"
        )
        metrics_small.end_measurement()
        
        # Test medium data with full processing
        metrics_medium = self.measure_performance("ResponseProcessor", "process_query_results_medium")
        metrics_medium.start_measurement()
        self.response_processor.process_query_results(
            self.medium_data,
            format_type="table",
            chart_type="bar",
            x_column="category",
            y_column="value",
            title="Medium Data Processing",
            filename="medium_data_full",
            save_format="json"
        )
        metrics_medium.end_measurement()
        
        # Assert performance meets thresholds
        self.assertPerformance("ResponseProcessor", "process_query_results_small", 
                              execution_time_threshold_ms=1000)
        self.assertPerformance("ResponseProcessor", "process_query_results_medium", 
                              execution_time_threshold_ms=2000)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed process_query_results performance test",
            changes=[
                "Measured performance of process_query_results with different data sizes",
                "All performance metrics within acceptable thresholds"
            ],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
    
    def test_benchmark_function_usage(self):
        """Test the usage of the benchmark_function utility"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing benchmark_function utility",
            changes=["Demonstrating the usage of benchmark_function for quick performance measurements"],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
        
        # Use benchmark_function to measure performance
        benchmark_result = benchmark_function(
            self.response_processor.format_results,
            self.small_data,
            format_type="json"
        )
        
        # Extract performance data
        performance_data = benchmark_result["performance"]
        
        # Log performance data
        self.changelog_engine.quick_update(
            action_summary="Completed benchmark_function test",
            changes=[
                f"Measured format_results performance using benchmark_function",
                f"Execution time: {performance_data['execution_time_ms']}ms"
            ],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
        )
    
    def tearDown(self):
        """Clean up test environment with changelog update"""
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Cleaning up response processor performance test environment",
            changes=["Completed performance tests for response processor"],
            files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test cleanup")]
        )
        
        super().tearDown()


def run_performance_tests():
    """Run all performance tests for response processor"""
    # Create changelog engine
    changelog_engine = ChangelogEngine()
    
    # Pre-Response: Changelog update execution
    changelog_engine.quick_update(
        action_summary="Running response processor performance tests",
        changes=["Executing performance tests for response processor"],
        files=[("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution")]
    )
    
    # Create test suite
    suite = PerformanceTestSuite(
        name="ResponseProcessorPerformance",
        output_dir="test_output/performance"
    )
    
    # Add test cases
    import unittest
    test_loader = unittest.TestLoader()
    test_cases = test_loader.loadTestsFromTestCase(ResponseProcessorPerformanceTest)
    
    for test_case in test_cases:
        suite.add_test_case(test_case)
    
    # Run tests
    results = suite.run_tests()
    
    # Post-Response: System validation
    changelog_engine.quick_update(
        action_summary="Completed response processor performance tests",
        changes=[
            f"Executed {results['total_tests']} performance tests",
            f"Pass rate: {results['pass_rate']}%",
            f"Total execution time: {results['total_execution_time_ms']}ms"
        ],
        files=[
            ("READ", "scripts/testing/test_response_processor_performance.py", "Performance test execution"),
            ("CREATE", f"test_output/performance/ResponseProcessorPerformance_results.json", "Performance test results")
        ]
    )
    
    return results


if __name__ == "__main__":
    run_performance_tests()
