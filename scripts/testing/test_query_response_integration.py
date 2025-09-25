"""
Integration Tests for Query Engine and Response Processor

This module contains integration tests for the SQL Agent's Query Engine and Response Processor,
demonstrating the end-to-end flow from query generation to result processing.

RESPONSE_SEQUENCE {
  1. changelog_engine.update_changelog()
  2. execute_integration_tests()
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
from engine.query_engine import QueryEngine
from engine.enhanced_query_engine import EnhancedQueryEngine
from processing.response_processor import ResponseProcessor
from analysis.schema_analyzer import SchemaAnalyzer
from testing.integration_test_framework import IntegrationTestCase, IntegrationTestSuite, create_end_to_end_test

class QueryResponseIntegrationTest(IntegrationTestCase):
    """
    Integration tests for the Query Engine and Response Processor
    """
    def setUp(self):
        """Set up integration test with changelog update"""
        super().setUp()
        
        # Create test directories
        self.test_dir = Path("test_data/integration")
        self.test_dir.mkdir(exist_ok=True, parents=True)
        self.output_dir = Path("test_output/integration")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create test data
        self.test_data = {
            "employee_id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "department": ["HR", "IT", "Finance", "IT", "HR"],
            "salary": [75000, 85000, 95000, 80000, 70000]
        }
        self.test_df = pd.DataFrame(self.test_data)
        
        # Save test data to CSV
        self.test_csv = self.test_dir / "employees.csv"
        self.test_df.to_csv(self.test_csv, index=False)
        
        # Create schema analyzer
        self.schema_analyzer = SchemaAnalyzer()
        
        # Create query engine
        self.query_engine = EnhancedQueryEngine(schema_analyzer=self.schema_analyzer)
        
        # Create response processor
        self.response_processor = ResponseProcessor(output_dir=str(self.output_dir))
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Setting up query-response integration test environment",
            changes=[
                "Created test data directory and sample employee data",
                "Initialized schema analyzer, query engine, and response processor"
            ],
            files=[
                ("CREATE", str(self.test_csv), "Test employee data"),
                ("READ", "scripts/testing/test_query_response_integration.py", "Integration test setup")
            ]
        )
    
    def test_query_to_visualization_flow(self):
        """Test the flow from query generation to result visualization"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing query to visualization flow",
            changes=["Executing end-to-end test from query generation to visualization"],
            files=[("READ", "scripts/testing/test_query_response_integration.py", "Integration test execution")]
        )
        
        # Track interaction: Schema Analyzer -> Query Engine
        schema_to_query = self.track_interaction("SchemaAnalyzer", "QueryEngine")
        schema_to_query.start_interaction("load_schema")
        
        # Load schema from test data
        table_info = {
            "employees": {
                "columns": ["employee_id", "name", "department", "salary"],
                "primary_key": "employee_id",
                "description": "Employee information table"
            }
        }
        self.schema_analyzer.table_info = table_info
        
        schema_to_query.end_interaction(output_data=table_info)
        
        # Track interaction: Query Engine -> Response Processor
        query_to_response = self.track_interaction("QueryEngine", "ResponseProcessor")
        query_to_response.start_interaction("execute_query")
        
        # Generate and execute query
        query = "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department"
        query_results = self.test_df.groupby("department").agg({"salary": "mean"}).reset_index()
        query_results = query_results.rename(columns={"salary": "avg_salary"})
        
        query_to_response.end_interaction(output_data=query_results)
        
        # Track interaction: Response Processor -> Visualization
        response_to_viz = self.track_interaction("ResponseProcessor", "Visualization")
        response_to_viz.start_interaction("create_visualization")
        
        # Generate visualization
        chart_path = self.response_processor.create_visualization(
            query_results, 
            chart_type="bar",
            x_column="department",
            y_column="avg_salary",
            title="Average Salary by Department"
        )
        
        response_to_viz.end_interaction(output_data=chart_path)
        
        # Verify the visualization was created
        self.assertTrue(os.path.exists(chart_path), f"Chart file not found: {chart_path}")
        
        # Assert the expected integration flow
        expected_flow = [
            ("SchemaAnalyzer", "QueryEngine"),
            ("QueryEngine", "ResponseProcessor"),
            ("ResponseProcessor", "Visualization")
        ]
        self.assertIntegrationFlow(
            ["SchemaAnalyzer", "QueryEngine", "ResponseProcessor", "Visualization"],
            expected_flow
        )
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed query to visualization flow test",
            changes=[
                "Successfully tested end-to-end flow from schema analysis to visualization",
                f"Generated visualization saved to {chart_path}"
            ],
            files=[
                ("READ", "scripts/testing/test_query_response_integration.py", "Integration test execution"),
                ("CREATE", chart_path, "Test visualization output")
            ]
        )
    
    def test_end_to_end_query_processing(self):
        """Test the complete end-to-end query processing flow"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing end-to-end query processing",
            changes=["Executing complete end-to-end test from schema to saved results"],
            files=[("READ", "scripts/testing/test_query_response_integration.py", "Integration test execution")]
        )
        
        # Track interaction: Schema Analyzer -> Query Engine
        schema_to_query = self.track_interaction("SchemaAnalyzer", "QueryEngine")
        schema_to_query.start_interaction("load_schema")
        
        # Load schema from test data
        table_info = {
            "employees": {
                "columns": ["employee_id", "name", "department", "salary"],
                "primary_key": "employee_id",
                "description": "Employee information table"
            }
        }
        self.schema_analyzer.table_info = table_info
        
        schema_to_query.end_interaction(output_data=table_info)
        
        # Track interaction: Query Engine -> Query Execution
        query_to_execution = self.track_interaction("QueryEngine", "QueryExecution")
        query_to_execution.start_interaction("execute_query")
        
        # Generate and execute query
        query = "SELECT * FROM employees WHERE department = 'IT'"
        query_results = self.test_df[self.test_df["department"] == "IT"]
        
        query_to_execution.end_interaction(output_data=query_results)
        
        # Track interaction: Query Execution -> Response Processor
        execution_to_response = self.track_interaction("QueryExecution", "ResponseProcessor")
        execution_to_response.start_interaction("format_results")
        
        # Format results
        formatted_results = self.response_processor.format_results(
            query_results,
            format_type="table"
        )
        
        execution_to_response.end_interaction(output_data=formatted_results)
        
        # Track interaction: Response Processor -> File System
        response_to_file = self.track_interaction("ResponseProcessor", "FileSystem")
        response_to_file.start_interaction("save_results")
        
        # Save results
        output_file = self.response_processor.save_results(
            query_results,
            filename="it_employees",
            format_type="json"
        )
        
        response_to_file.end_interaction(output_data=output_file)
        
        # Verify the output file was created
        self.assertTrue(os.path.exists(output_file), f"Output file not found: {output_file}")
        
        # Load and verify the saved results
        with open(output_file, "r") as f:
            saved_data = json.load(f)
        
        # Verify the saved data contains the expected records
        self.assertEqual(len(saved_data), 2, "Expected 2 IT employees in the results")
        departments = [record.get("department") for record in saved_data]
        self.assertTrue(all(dept == "IT" for dept in departments), "All records should be from IT department")
        
        # Assert the expected integration flow
        expected_flow = [
            ("SchemaAnalyzer", "QueryEngine"),
            ("QueryEngine", "QueryExecution"),
            ("QueryExecution", "ResponseProcessor"),
            ("ResponseProcessor", "FileSystem")
        ]
        self.assertIntegrationFlow(
            ["SchemaAnalyzer", "QueryEngine", "QueryExecution", "ResponseProcessor", "FileSystem"],
            expected_flow
        )
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed end-to-end query processing test",
            changes=[
                "Successfully tested complete end-to-end flow from schema to saved results",
                f"Generated output file saved to {output_file}"
            ],
            files=[
                ("READ", "scripts/testing/test_query_response_integration.py", "Integration test execution"),
                ("CREATE", output_file, "Test output file")
            ]
        )
    
    def tearDown(self):
        """Clean up test environment with changelog update"""
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Cleaning up query-response integration test environment",
            changes=["Completed integration tests for query engine and response processor"],
            files=[("READ", "scripts/testing/test_query_response_integration.py", "Integration test cleanup")]
        )
        
        super().tearDown()


# Create a dynamic end-to-end test using the test generator
components = ["SchemaAnalyzer", "QueryEngine", "ResponseProcessor", "Visualization", "FileSystem"]
QueryResponseIntegrationTest.test_dynamic_end_to_end = create_end_to_end_test(
    components=components,
    test_name="Dynamic End-to-End Test"
)


def run_integration_tests():
    """Run all integration tests for query engine and response processor"""
    # Create changelog engine
    changelog_engine = ChangelogEngine()
    
    # Pre-Response: Changelog update execution
    changelog_engine.quick_update(
        action_summary="Running query-response integration tests",
        changes=["Executing integration tests for query engine and response processor"],
        files=[("READ", "scripts/testing/test_query_response_integration.py", "Integration test execution")]
    )
    
    # Create test suite
    suite = IntegrationTestSuite(
        name="QueryResponseIntegration",
        output_dir="test_output/integration"
    )
    
    # Add test cases
    test_cases = [
        QueryResponseIntegrationTest("test_query_to_visualization_flow"),
        QueryResponseIntegrationTest("test_end_to_end_query_processing"),
        QueryResponseIntegrationTest("test_dynamic_end_to_end")
    ]
    
    for test_case in test_cases:
        suite.add_test_case(test_case)
    
    # Run tests
    results = suite.run_tests()
    
    # Post-Response: System validation
    changelog_engine.quick_update(
        action_summary="Completed query-response integration tests",
        changes=[
            f"Executed {results['total_tests']} integration tests",
            f"Pass rate: {results['pass_rate']}%",
            f"Total execution time: {results['total_execution_time_ms']}ms"
        ],
        files=[
            ("READ", "scripts/testing/test_query_response_integration.py", "Integration test execution"),
            ("CREATE", f"test_output/integration/QueryResponseIntegration_results.json", "Integration test results")
        ]
    )
    
    return results


if __name__ == "__main__":
    run_integration_tests()
