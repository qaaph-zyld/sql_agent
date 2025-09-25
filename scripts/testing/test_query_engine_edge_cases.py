"""
Query Engine Edge Case Tests for SQL Agent

This module implements edge case tests for the Query Engine component,
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
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from testing.edge_case_test_framework import EdgeCase, EdgeCaseTestCase
from query.query_engine import QueryEngine
from query.enhanced_query_engine import EnhancedQueryEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/query_engine_edge_case_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class QueryEngineEdgeCaseTest(EdgeCaseTestCase):
    """Test case for query engine edge cases"""
    
    def setUp(self):
        """Set up query engine edge case test with changelog update"""
        super().setUp()
        
        # Create query engines
        self.query_engine = QueryEngine()
        self.enhanced_query_engine = EnhancedQueryEngine()
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Setting up query engine edge case test environment",
            changes=["Initializing query engine edge case test case"],
            files=[
                ("READ", "scripts/testing/edge_case_test_framework.py", "Edge case test framework"),
                ("READ", "query/query_engine.py", "Query engine component"),
                ("READ", "query/enhanced_query_engine.py", "Enhanced query engine component")
            ]
        )
    
    def test_basic_query_engine_edge_cases(self):
        """Test edge cases for the basic query engine"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing basic query engine edge cases",
            changes=["Executing edge case tests for basic query engine"],
            files=[
                ("READ", "scripts/testing/test_query_engine_edge_cases.py", "Edge case test execution"),
                ("READ", "query/query_engine.py", "Target component for testing")
            ]
        )
        
        # Define edge cases to test
        edge_cases = [
            EdgeCase(
                name="Empty Query",
                description="Testing behavior with an empty query string",
                category="INPUT",
                test_input="",
                expected_behavior="Should reject with appropriate error message"
            ),
            EdgeCase(
                name="Extremely Long Query",
                description="Testing behavior with an extremely long query",
                category="BOUNDARY",
                test_input="SELECT " + ", ".join([f"column_{i}" for i in range(1000)]) + " FROM table",
                expected_behavior="Should handle or reject with appropriate error message"
            ),
            EdgeCase(
                name="Invalid SQL Syntax",
                description="Testing behavior with invalid SQL syntax",
                category="ERROR",
                test_input="SELECT * FORM users",  # Intentional typo: FORM instead of FROM
                expected_behavior="Should reject with syntax error message"
            ),
            EdgeCase(
                name="Non-SQL Input",
                description="Testing behavior with non-SQL input",
                category="INPUT",
                test_input="This is not a SQL query at all",
                expected_behavior="Should reject with appropriate error message"
            ),
            EdgeCase(
                name="Query with Comments",
                description="Testing behavior with SQL comments",
                category="INPUT",
                test_input="SELECT * FROM users -- This is a comment",
                expected_behavior="Should handle comments correctly"
            ),
            EdgeCase(
                name="Query with Unicode Characters",
                description="Testing behavior with Unicode characters",
                category="INPUT",
                test_input="SELECT * FROM users WHERE name = 'José' AND city = 'São Paulo'",
                expected_behavior="Should handle Unicode characters correctly"
            ),
            EdgeCase(
                name="Multiple Statements",
                description="Testing behavior with multiple SQL statements",
                category="SECURITY",
                test_input="SELECT * FROM users; DROP TABLE users;",
                expected_behavior="Should reject multiple statements for security"
            ),
            EdgeCase(
                name="Complex Nested Query",
                description="Testing behavior with deeply nested queries",
                category="COMPLEXITY",
                test_input="SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM users) AS t1) AS t2) AS t3",
                expected_behavior="Should handle nested queries correctly"
            )
        ]
        
        # Test each edge case
        results = []
        for edge_case in edge_cases:
            # Define test function for query engine
            def test_query_engine(input_query):
                try:
                    # Attempt to validate the query
                    validation_result = self.query_engine.validate_query(input_query)
                    
                    # Check if the behavior matches expectations
                    if edge_case.name == "Empty Query" or edge_case.name == "Non-SQL Input":
                        # These should be rejected
                        passed = not validation_result
                        actual_behavior = "Rejected invalid input" if not validation_result else "Accepted invalid input"
                        details = f"Validation result: {validation_result}"
                    elif edge_case.name == "Invalid SQL Syntax":
                        # This should be rejected
                        passed = not validation_result
                        actual_behavior = "Rejected invalid syntax" if not validation_result else "Accepted invalid syntax"
                        details = f"Validation result: {validation_result}"
                    elif edge_case.name == "Multiple Statements":
                        # This should be rejected for security
                        passed = not validation_result
                        actual_behavior = "Rejected multiple statements" if not validation_result else "Accepted multiple statements"
                        details = f"Validation result: {validation_result}"
                    else:
                        # These should be handled
                        passed = validation_result
                        actual_behavior = "Accepted valid query" if validation_result else "Rejected valid query"
                        details = f"Validation result: {validation_result}"
                    
                    return passed, actual_behavior, details
                    
                except Exception as e:
                    # If validation raises an exception, check if it's expected
                    if edge_case.name in ["Empty Query", "Non-SQL Input", "Invalid SQL Syntax", "Multiple Statements"]:
                        # For these, an exception is acceptable
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
            result = self.test_edge_case(edge_case, test_query_engine)
            results.append(result)
        
        # Save results to file
        results_file = self.output_dir / "basic_query_engine_edge_case_results.json"
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed basic query engine edge case tests",
            changes=[
                f"Executed {len(results)} edge case tests",
                f"Tests passed: {sum(1 for r in results if r.passed)}/{len(results)}"
            ],
            files=[
                ("READ", "scripts/testing/test_query_engine_edge_cases.py", "Edge case test execution"),
                ("CREATE", str(results_file), "Edge case test results")
            ]
        )
        
        return results
    
    def test_enhanced_query_engine_edge_cases(self):
        """Test edge cases for the enhanced query engine"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing enhanced query engine edge cases",
            changes=["Executing edge case tests for enhanced query engine"],
            files=[
                ("READ", "scripts/testing/test_query_engine_edge_cases.py", "Edge case test execution"),
                ("READ", "query/enhanced_query_engine.py", "Target component for testing")
            ]
        )
        
        # Define edge cases to test
        edge_cases = [
            EdgeCase(
                name="Empty Natural Language Query",
                description="Testing behavior with an empty natural language query",
                category="INPUT",
                test_input="",
                expected_behavior="Should reject with appropriate error message"
            ),
            EdgeCase(
                name="Very Short Query",
                description="Testing behavior with a very short query",
                category="INPUT",
                test_input="users",
                expected_behavior="Should request more information or generate a basic query"
            ),
            EdgeCase(
                name="Ambiguous Query",
                description="Testing behavior with an ambiguous query",
                category="INPUT",
                test_input="show me everything",
                expected_behavior="Should request clarification or generate a reasonable default query"
            ),
            EdgeCase(
                name="Query with Unknown Entity",
                description="Testing behavior with reference to unknown entity",
                category="ERROR",
                test_input="show me all data from the nonexistent_table",
                expected_behavior="Should reject with appropriate error about unknown entity"
            ),
            EdgeCase(
                name="Complex Natural Language Query",
                description="Testing behavior with a complex natural language query",
                category="COMPLEXITY",
                test_input="Show me the top 5 users who made the most purchases in the last month, grouped by country, and sorted by total amount spent",
                expected_behavior="Should generate appropriate SQL or reject with clear explanation"
            ),
            EdgeCase(
                name="Query with Special Characters",
                description="Testing behavior with special characters in natural language query",
                category="INPUT",
                test_input="Find users where name contains 'O'Reilly' or 'Smith-Jones'",
                expected_behavior="Should handle special characters correctly"
            )
        ]
        
        # Test each edge case
        results = []
        for edge_case in edge_cases:
            # Define test function for enhanced query engine
            def test_enhanced_query_engine(input_query):
                try:
                    # Attempt to generate a query
                    generated_query = self.enhanced_query_engine.generate_query(input_query)
                    
                    # Check if the behavior matches expectations
                    if edge_case.name == "Empty Natural Language Query":
                        # This should be rejected
                        passed = generated_query is None or generated_query == ""
                        actual_behavior = "Rejected empty query" if passed else "Generated query from empty input"
                        details = f"Generated query: {generated_query}"
                    elif edge_case.name == "Query with Unknown Entity":
                        # This should be rejected or handled gracefully
                        passed = generated_query is None or "error" in str(generated_query).lower() or "unknown" in str(generated_query).lower()
                        actual_behavior = "Handled unknown entity appropriately" if passed else "Failed to handle unknown entity"
                        details = f"Generated query: {generated_query}"
                    else:
                        # These should generate a query
                        passed = generated_query is not None and len(str(generated_query)) > 0
                        actual_behavior = "Generated SQL query successfully" if passed else "Failed to generate query"
                        details = f"Generated query: {generated_query}"
                    
                    return passed, actual_behavior, details
                    
                except Exception as e:
                    # If generation raises an exception, check if it's expected
                    if edge_case.name in ["Empty Natural Language Query", "Query with Unknown Entity"]:
                        # For these, an exception might be expected
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
            result = self.test_edge_case(edge_case, test_enhanced_query_engine)
            results.append(result)
        
        # Save results to file
        results_file = self.output_dir / "enhanced_query_engine_edge_case_results.json"
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed enhanced query engine edge case tests",
            changes=[
                f"Executed {len(results)} edge case tests",
                f"Tests passed: {sum(1 for r in results if r.passed)}/{len(results)}"
            ],
            files=[
                ("READ", "scripts/testing/test_query_engine_edge_cases.py", "Edge case test execution"),
                ("CREATE", str(results_file), "Edge case test results")
            ]
        )
        
        return results
    
    def test_all(self):
        """Run all query engine edge case tests"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Running all query engine edge case tests",
            changes=["Executing all edge case tests for query engines"],
            files=[("READ", "scripts/testing/test_query_engine_edge_cases.py", "Edge case test execution")]
        )
        
        # Run all tests
        basic_results = self.test_basic_query_engine_edge_cases()
        enhanced_results = self.test_enhanced_query_engine_edge_cases()
        
        # Combine results
        all_results = basic_results + enhanced_results
        
        # Calculate summary statistics
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.passed)
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Log summary
        logger.info(f"Query Engine Edge Case Test Summary:")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed tests: {passed_tests}")
        logger.info(f"Pass rate: {pass_rate:.2f}%")
        
        # Save summary to file
        summary_file = self.output_dir / "query_engine_edge_case_summary.json"
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": pass_rate,
            "basic_engine_tests": len(basic_results),
            "basic_engine_passed": sum(1 for r in basic_results if r.passed),
            "enhanced_engine_tests": len(enhanced_results),
            "enhanced_engine_passed": sum(1 for r in enhanced_results if r.passed)
        }
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed all query engine edge case tests",
            changes=[
                f"Executed {total_tests} edge case tests",
                f"Tests passed: {passed_tests}/{total_tests} ({pass_rate:.2f}%)",
                f"Basic engine: {sum(1 for r in basic_results if r.passed)}/{len(basic_results)}",
                f"Enhanced engine: {sum(1 for r in enhanced_results if r.passed)}/{len(enhanced_results)}"
            ],
            files=[
                ("READ", "scripts/testing/test_query_engine_edge_cases.py", "Edge case test execution"),
                ("CREATE", str(summary_file), "Edge case test summary")
            ]
        )


if __name__ == "__main__":
    # Create and run the test case
    test_case = QueryEngineEdgeCaseTest()
    test_case.setUp()
    test_case.test_all()
    test_case.tearDown()
