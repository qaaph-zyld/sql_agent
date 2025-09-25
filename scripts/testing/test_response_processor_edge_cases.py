"""
Response Processor Edge Case Tests for SQL Agent

This module implements edge case tests for the Response Processor component,
testing boundary conditions, unexpected inputs, and error handling.

RESPONSE_SEQUENCE {
  1. changelog_engine.update_changelog()
  2. execute_edge_case_tests()
  3. validation_suite.run_validation()
  4. workspace_state_sync()
}
"""

import os
import sys
import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from testing.edge_case_test_framework import EdgeCase, EdgeCaseTestCase
from processing.response_processor import ResponseProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/response_processor_edge_case_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ResponseProcessorEdgeCaseTest(EdgeCaseTestCase):
    """Test case for response processor edge cases"""
    
    def setUp(self):
        """Set up response processor edge case test with changelog update"""
        super().setUp()
        
        # Create response processor
        self.response_processor = ResponseProcessor()
        
        # Create test data
        self.test_data = self._create_test_data()
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Setting up response processor edge case test environment",
            changes=["Initializing response processor edge case test case"],
            files=[
                ("READ", "scripts/testing/edge_case_test_framework.py", "Edge case test framework"),
                ("READ", "processing/response_processor.py", "Response processor component")
            ]
        )
    
    def _create_test_data(self):
        """Create test data for edge case tests"""
        test_data = {
            "empty_dataframe": pd.DataFrame(),
            "single_column": pd.DataFrame({"column1": [1, 2, 3]}),
            "single_row": pd.DataFrame({"column1": [1], "column2": [2], "column3": [3]}),
            "normal": pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "category": ["A", "B", "A", "C", "B"],
                "value": [10, 20, 15, 25, 30]
            }),
            "non_numeric": pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "category": ["A", "B", "A", "C", "B"],
                "text_value": ["ten", "twenty", "fifteen", "twenty-five", "thirty"]
            })
        }
        return test_data
    
    def test_format_results_edge_cases(self):
        """Test edge cases for format_results method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing format_results edge cases",
            changes=["Executing edge case tests for format_results method"],
            files=[
                ("READ", "scripts/testing/test_response_processor_edge_cases.py", "Edge case test execution"),
                ("READ", "processing/response_processor.py", "Target component for testing")
            ]
        )
        
        # Define edge cases to test
        edge_cases = [
            EdgeCase(
                name="Empty DataFrame",
                description="Testing behavior with an empty DataFrame",
                category="INPUT",
                test_input={"data": "empty_dataframe", "format_type": "table"},
                expected_behavior="Should handle empty DataFrame gracefully"
            ),
            EdgeCase(
                name="Single Column DataFrame",
                description="Testing behavior with a single column DataFrame",
                category="BOUNDARY",
                test_input={"data": "single_column", "format_type": "table"},
                expected_behavior="Should format single column correctly"
            ),
            EdgeCase(
                name="Invalid Format Type",
                description="Testing behavior with an invalid format type",
                category="ERROR",
                test_input={"data": "normal", "format_type": "invalid_format"},
                expected_behavior="Should reject with appropriate error message"
            )
        ]
        
        # Test each edge case
        results = []
        for edge_case in edge_cases:
            # Define test function for format_results
            def test_format_results(input_data):
                try:
                    # Extract test parameters
                    data_key = input_data["data"]
                    format_type = input_data["format_type"]
                    
                    # Get the test DataFrame
                    df = self.test_data[data_key]
                    
                    # Call format_results
                    formatted_result = self.response_processor.format_results(df, format_type=format_type)
                    
                    # Check if the behavior matches expectations
                    if edge_case.name == "Empty DataFrame":
                        # Should handle empty DataFrame gracefully
                        passed = formatted_result is not None
                        actual_behavior = "Handled empty DataFrame" if passed else "Failed with empty DataFrame"
                        details = f"Result: {formatted_result[:100] if formatted_result else None}"
                    elif edge_case.name == "Invalid Format Type":
                        # Should reject invalid format type
                        passed = formatted_result is None or "error" in str(formatted_result).lower()
                        actual_behavior = "Rejected invalid format type" if passed else "Accepted invalid format type"
                        details = f"Result: {formatted_result[:100] if formatted_result else None}"
                    else:
                        # Should format correctly
                        passed = formatted_result is not None and len(str(formatted_result)) > 0
                        actual_behavior = "Formatted successfully" if passed else "Failed to format"
                        details = f"Result: {formatted_result[:100] if formatted_result else None}"
                    
                    return passed, actual_behavior, details
                    
                except Exception as e:
                    # If formatting raises an exception, check if it's expected
                    if edge_case.name == "Invalid Format Type":
                        # For invalid format, an exception is acceptable
                        passed = True
                        actual_behavior = f"Rejected with exception: {str(e)}"
                        details = f"Exception type: {type(e).__name__}"
                    else:
                        # For others, an exception is not expected
                        passed = False
                        actual_behavior = f"Unexpected exception: {str(e)}"
                        details = f"Exception type: {type(e).__name__}"
                    
                    return passed, actual_behavior, details
            
            # Test the edge case
            result = self.test_edge_case(edge_case, test_format_results)
            results.append(result)
        
        # Save results to file
        results_file = self.output_dir / "format_results_edge_case_results.json"
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed format_results edge case tests",
            changes=[
                f"Executed {len(results)} edge case tests",
                f"Tests passed: {sum(1 for r in results if r.passed)}/{len(results)}"
            ],
            files=[
                ("READ", "scripts/testing/test_response_processor_edge_cases.py", "Edge case test execution"),
                ("CREATE", str(results_file), "Edge case test results")
            ]
        )
        
        return results
    
    def test_create_visualization_edge_cases(self):
        """Test edge cases for create_visualization method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing create_visualization edge cases",
            changes=["Executing edge case tests for create_visualization method"],
            files=[
                ("READ", "scripts/testing/test_response_processor_edge_cases.py", "Edge case test execution"),
                ("READ", "processing/response_processor.py", "Target component for testing")
            ]
        )
        
        # Define edge cases to test
        edge_cases = [
            EdgeCase(
                name="Empty DataFrame Visualization",
                description="Testing visualization with an empty DataFrame",
                category="INPUT",
                test_input={
                    "data": "empty_dataframe", 
                    "chart_type": "bar", 
                    "x_column": "column1", 
                    "y_column": "column2"
                },
                expected_behavior="Should handle empty DataFrame gracefully"
            ),
            EdgeCase(
                name="Invalid Chart Type",
                description="Testing behavior with an invalid chart type",
                category="ERROR",
                test_input={
                    "data": "normal", 
                    "chart_type": "invalid_chart", 
                    "x_column": "category", 
                    "y_column": "value"
                },
                expected_behavior="Should reject with appropriate error message"
            ),
            EdgeCase(
                name="Non-existent Column",
                description="Testing behavior with non-existent column names",
                category="ERROR",
                test_input={
                    "data": "normal", 
                    "chart_type": "bar", 
                    "x_column": "non_existent", 
                    "y_column": "value"
                },
                expected_behavior="Should reject with appropriate error message"
            ),
            EdgeCase(
                name="Non-Numeric Y-Column",
                description="Testing behavior with non-numeric y-column",
                category="INPUT",
                test_input={
                    "data": "non_numeric", 
                    "chart_type": "bar", 
                    "x_column": "category", 
                    "y_column": "text_value"
                },
                expected_behavior="Should handle or reject with appropriate error message"
            )
        ]
        
        # Test each edge case
        results = []
        for edge_case in edge_cases:
            # Define test function for create_visualization
            def test_create_visualization(input_data):
                try:
                    # Extract test parameters
                    data_key = input_data["data"]
                    chart_type = input_data["chart_type"]
                    x_column = input_data["x_column"]
                    y_column = input_data["y_column"]
                    
                    # Get the test DataFrame
                    df = self.test_data[data_key]
                    
                    # Call create_visualization
                    visualization_result = self.response_processor.create_visualization(
                        df, chart_type=chart_type, x_column=x_column, y_column=y_column
                    )
                    
                    # Check if the behavior matches expectations
                    if edge_case.name == "Empty DataFrame Visualization":
                        # Should handle empty DataFrame gracefully
                        passed = visualization_result is None or "error" in str(visualization_result).lower()
                        actual_behavior = "Handled empty DataFrame appropriately" if passed else "Failed with empty DataFrame"
                        details = f"Result: {str(visualization_result)[:100] if visualization_result else None}"
                    elif edge_case.name == "Invalid Chart Type":
                        # Should reject invalid chart type
                        passed = visualization_result is None or "error" in str(visualization_result).lower()
                        actual_behavior = "Rejected invalid chart type" if passed else "Accepted invalid chart type"
                        details = f"Result: {str(visualization_result)[:100] if visualization_result else None}"
                    elif edge_case.name == "Non-existent Column":
                        # Should reject non-existent column
                        passed = visualization_result is None or "error" in str(visualization_result).lower()
                        actual_behavior = "Rejected non-existent column" if passed else "Accepted non-existent column"
                        details = f"Result: {str(visualization_result)[:100] if visualization_result else None}"
                    elif edge_case.name == "Non-Numeric Y-Column":
                        # Should handle or reject non-numeric y-column
                        passed = visualization_result is None or isinstance(visualization_result, str)
                        actual_behavior = "Handled non-numeric y-column appropriately" if passed else "Failed with non-numeric y-column"
                        details = f"Result: {str(visualization_result)[:100] if visualization_result else None}"
                    else:
                        # Default case
                        passed = visualization_result is not None
                        actual_behavior = "Created visualization successfully" if passed else "Failed to create visualization"
                        details = f"Result: {str(visualization_result)[:100] if visualization_result else None}"
                    
                    return passed, actual_behavior, details
                    
                except Exception as e:
                    # If visualization raises an exception, check if it's expected
                    if edge_case.name in ["Empty DataFrame Visualization", "Invalid Chart Type", "Non-existent Column", "Non-Numeric Y-Column"]:
                        # For these cases, an exception might be acceptable
                        passed = True
                        actual_behavior = f"Rejected with exception: {str(e)}"
                        details = f"Exception type: {type(e).__name__}"
                    else:
                        # For others, an exception is not expected
                        passed = False
                        actual_behavior = f"Unexpected exception: {str(e)}"
                        details = f"Exception type: {type(e).__name__}"
                    
                    return passed, actual_behavior, details
            
            # Test the edge case
            result = self.test_edge_case(edge_case, test_create_visualization)
            results.append(result)
        
        # Save results to file
        results_file = self.output_dir / "create_visualization_edge_case_results.json"
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed create_visualization edge case tests",
            changes=[
                f"Executed {len(results)} edge case tests",
                f"Tests passed: {sum(1 for r in results if r.passed)}/{len(results)}"
            ],
            files=[
                ("READ", "scripts/testing/test_response_processor_edge_cases.py", "Edge case test execution"),
                ("CREATE", str(results_file), "Edge case test results")
            ]
        )
        
        return results
    
    def test_save_results_edge_cases(self):
        """Test edge cases for save_results method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing save_results edge cases",
            changes=["Executing edge case tests for save_results method"],
            files=[
                ("READ", "scripts/testing/test_response_processor_edge_cases.py", "Edge case test execution"),
                ("READ", "processing/response_processor.py", "Target component for testing")
            ]
        )
        
        # Create temporary directory for test outputs
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        
        # Define edge cases to test
        edge_cases = [
            EdgeCase(
                name="Empty DataFrame Save",
                description="Testing saving an empty DataFrame",
                category="INPUT",
                test_input={
                    "data": "empty_dataframe", 
                    "file_path": str(temp_dir / "empty.csv"),
                    "format_type": "csv"
                },
                expected_behavior="Should handle empty DataFrame gracefully"
            ),
            EdgeCase(
                name="Invalid File Extension",
                description="Testing behavior with an invalid file extension",
                category="ERROR",
                test_input={
                    "data": "normal", 
                    "file_path": str(temp_dir / "test.invalid"),
                    "format_type": "csv"
                },
                expected_behavior="Should reject with appropriate error message"
            ),
            EdgeCase(
                name="Invalid Directory Path",
                description="Testing behavior with a non-existent directory path",
                category="ERROR",
                test_input={
                    "data": "normal", 
                    "file_path": "/non/existent/path/test.csv",
                    "format_type": "csv"
                },
                expected_behavior="Should reject with appropriate error message"
            ),
            EdgeCase(
                name="Format Type Mismatch",
                description="Testing behavior when format_type doesn't match file extension",
                category="ERROR",
                test_input={
                    "data": "normal", 
                    "file_path": str(temp_dir / "test.json"),
                    "format_type": "csv"
                },
                expected_behavior="Should either adapt or reject with error message"
            )
        ]
        
        # Test each edge case
        results = []
        for edge_case in edge_cases:
            # Define test function for save_results
            def test_save_results(input_data):
                try:
                    # Extract test parameters
                    data_key = input_data["data"]
                    file_path = input_data["file_path"]
                    format_type = input_data["format_type"]
                    
                    # Get the test DataFrame
                    df = self.test_data[data_key]
                    
                    # Call save_results
                    save_result = self.response_processor.save_results(
                        df, file_path=file_path, format_type=format_type
                    )
                    
                    # Check if the behavior matches expectations
                    if edge_case.name == "Empty DataFrame Save":
                        # Should handle empty DataFrame gracefully
                        passed = save_result is not None and os.path.exists(file_path)
                        actual_behavior = "Saved empty DataFrame" if passed else "Failed to save empty DataFrame"
                        details = f"Result: {save_result}, File exists: {os.path.exists(file_path)}"
                    elif edge_case.name == "Invalid File Extension":
                        # Should reject invalid file extension
                        passed = save_result is None or "error" in str(save_result).lower() or not os.path.exists(file_path)
                        actual_behavior = "Rejected invalid file extension" if passed else "Accepted invalid file extension"
                        details = f"Result: {save_result}, File exists: {os.path.exists(file_path)}"
                    elif edge_case.name == "Invalid Directory Path":
                        # Should reject invalid directory path
                        passed = save_result is None or "error" in str(save_result).lower() or not os.path.exists(file_path)
                        actual_behavior = "Rejected invalid directory path" if passed else "Accepted invalid directory path"
                        details = f"Result: {save_result}, File exists: {os.path.exists(file_path)}"
                    elif edge_case.name == "Format Type Mismatch":
                        # Should either adapt or reject format type mismatch
                        passed = (save_result is None or "error" in str(save_result).lower() or 
                                 (os.path.exists(file_path) and save_result is not None))
                        actual_behavior = "Handled format type mismatch appropriately" if passed else "Failed with format type mismatch"
                        details = f"Result: {save_result}, File exists: {os.path.exists(file_path)}"
                    else:
                        # Default case
                        passed = save_result is not None and os.path.exists(file_path)
                        actual_behavior = "Saved results successfully" if passed else "Failed to save results"
                        details = f"Result: {save_result}, File exists: {os.path.exists(file_path)}"
                    
                    return passed, actual_behavior, details
                    
                except Exception as e:
                    # If save_results raises an exception, check if it's expected
                    if edge_case.name in ["Invalid File Extension", "Invalid Directory Path", "Format Type Mismatch"]:
                        # For these cases, an exception might be acceptable
                        passed = True
                        actual_behavior = f"Rejected with exception: {str(e)}"
                        details = f"Exception type: {type(e).__name__}"
                    else:
                        # For others, an exception is not expected
                        passed = False
                        actual_behavior = f"Unexpected exception: {str(e)}"
                        details = f"Exception type: {type(e).__name__}"
                    
                    return passed, actual_behavior, details
            
            # Test the edge case
            result = self.test_edge_case(edge_case, test_save_results)
            results.append(result)
        
        # Save results to file
        results_file = self.output_dir / "save_results_edge_case_results.json"
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed save_results edge case tests",
            changes=[
                f"Executed {len(results)} edge case tests",
                f"Tests passed: {sum(1 for r in results if r.passed)}/{len(results)}"
            ],
            files=[
                ("READ", "scripts/testing/test_response_processor_edge_cases.py", "Edge case test execution"),
                ("CREATE", str(results_file), "Edge case test results")
            ]
        )
        
        return results
    
    def test_all(self):
        """Run all response processor edge case tests"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Running all response processor edge case tests",
            changes=["Executing all edge case tests for response processor"],
            files=[("READ", "scripts/testing/test_response_processor_edge_cases.py", "Edge case test execution")]
        )
        
        # Run tests
        format_results = self.test_format_results_edge_cases()
        visualization_results = self.test_create_visualization_edge_cases()
        save_results = self.test_save_results_edge_cases()
        
        # Combine results
        all_results = format_results + visualization_results + save_results
        
        # Calculate summary statistics
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.passed)
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Log summary
        logger.info(f"Response Processor Edge Case Test Summary:")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed tests: {passed_tests}")
        logger.info(f"Pass rate: {pass_rate:.2f}%")
        
        # Save summary to file
        summary_file = self.output_dir / "response_processor_edge_case_summary.json"
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": pass_rate,
            "format_results_tests": len(format_results),
            "format_results_passed": sum(1 for r in format_results if r.passed),
            "visualization_tests": len(visualization_results),
            "visualization_passed": sum(1 for r in visualization_results if r.passed),
            "save_results_tests": len(save_results),
            "save_results_passed": sum(1 for r in save_results if r.passed)
        }
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed all response processor edge case tests",
            changes=[
                f"Executed {total_tests} edge case tests",
                f"Tests passed: {passed_tests}/{total_tests} ({pass_rate:.2f}%)",
                f"Format results: {sum(1 for r in format_results if r.passed)}/{len(format_results)}",
                f"Visualization: {sum(1 for r in visualization_results if r.passed)}/{len(visualization_results)}",
                f"Save results: {sum(1 for r in save_results if r.passed)}/{len(save_results)}"
            ],
            files=[
                ("READ", "scripts/testing/test_response_processor_edge_cases.py", "Edge case test execution"),
                ("CREATE", str(summary_file), "Edge case test summary")
            ]
        )


if __name__ == "__main__":
    # Create and run the test case
    test_case = ResponseProcessorEdgeCaseTest()
    test_case.setUp()
    test_case.test_all()
    test_case.tearDown()
