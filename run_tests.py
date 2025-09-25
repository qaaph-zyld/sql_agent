"""
Test Runner for SQL Agent

This script runs all unit tests for the SQL Agent project,
following the mandatory changelog protocol at each step.

RESPONSE_SEQUENCE {
  1. changelog_engine.update_changelog()
  2. execute_tests()
  3. validation_suite.run_validation()
  4. workspace_state_sync()
}
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/test_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import required modules
from scripts.core.changelog_engine import ChangelogEngine
from scripts.testing.test_framework import run_test_suite
from scripts.testing.test_response_processor import TestResponseProcessor
from scripts.testing.test_query_response_integration import run_integration_tests

# Import edge case test modules
from scripts.testing.test_query_engine_edge_cases import QueryEngineEdgeCaseTest
from scripts.testing.test_response_processor_edge_cases import ResponseProcessorEdgeCaseTest

# Import performance test modules
from scripts.testing.test_query_engine_performance import QueryEnginePerformanceTest, run_performance_tests as run_query_engine_performance_tests
from scripts.testing.test_response_processor_performance import ResponseProcessorPerformanceTest, run_performance_tests as run_response_processor_performance_tests

# Import security test modules
from scripts.testing.test_query_engine_security import QueryEngineSecurityTest, run_security_tests as run_query_engine_security_tests
from scripts.testing.test_response_processor_security import ResponseProcessorSecurityTest, run_security_tests as run_response_processor_security_tests

class TestRunner:
    """
    Test runner with changelog integration and validation
    """
    def __init__(self):
        """Initialize test runner"""
        self.changelog_engine = ChangelogEngine()
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        self.start_time = None
        self.test_results = {}
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Initializing test runner",
            changes=["Setting up test environment", "Preparing to run unit tests"],
            files=[("CREATE", "run_tests.py", "Test runner initialization")]
        )
        
        logger.info("Test runner initialized")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test suites
        
        Returns:
            Dictionary with combined test results
        """
        self.start_time = time.time()
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Running all test suites",
            changes=["Executing all unit and integration test suites"],
            files=[("MODIFY", "run_tests.py", "Test execution")]
        )
        
        logger.info("Running all test suites")
        
        # List of unit test suites to run
        test_suites = [
            ("ResponseProcessor", TestResponseProcessor),
            # Edge case test suites
            ("QueryEngineEdgeCases", QueryEngineEdgeCaseTest),
            ("ResponseProcessorEdgeCases", ResponseProcessorEdgeCaseTest),
            # Performance test suites
            ("QueryEnginePerformance", QueryEnginePerformanceTest),
            ("ResponseProcessorPerformance", ResponseProcessorPerformanceTest),
            # Security test suites
            ("QueryEngineSecurity", QueryEngineSecurityTest),
            ("ResponseProcessorSecurity", ResponseProcessorSecurityTest)
        ]
        
        # Run each unit test suite
        for suite_name, test_class in test_suites:
            logger.info(f"Running unit test suite: {suite_name}")
            self.test_results[suite_name] = run_test_suite(test_class, suite_name)
        
        # Run integration tests
        logger.info("Running integration tests")
        integration_results = run_integration_tests()
        self.test_results["Integration"] = integration_results
        
        # Calculate total execution time
        total_execution_time_ms = round((time.time() - self.start_time) * 1000, 2)
        
        # Aggregate results
        total_tests = sum(suite["total_tests"] for suite in self.test_results.values())
        passed_tests = sum(suite["passed_tests"] for suite in self.test_results.values())
        failed_tests = sum(suite["failed_tests"] for suite in self.test_results.values())
        pass_rate = round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0
        
        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_suites": len(test_suites),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": pass_rate,
            "total_execution_time_ms": total_execution_time_ms,
            "suite_results": self.test_results
        }
        
        # Save summary to file
        summary_file = self.results_dir / "test_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"All test suites completed: {passed_tests}/{total_tests} tests passed ({pass_rate}%)")
        logger.info(f"Total execution time: {total_execution_time_ms}ms")
        logger.info(f"Summary saved to {summary_file}")
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed all test suites",
            changes=[
                f"Executed {total_tests} tests across {len(test_suites)} test suites",
                f"Pass rate: {pass_rate}%",
                f"Total execution time: {total_execution_time_ms}ms"
            ],
            files=[
                ("MODIFY", "run_tests.py", "Test execution"),
                ("CREATE", str(summary_file), "Test results summary")
            ]
        )
        
        return summary
    
    def validate_results(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate test results against quality gates
        
        Args:
            summary: Test results summary
            
        Returns:
            Validation results
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Validating test results",
            changes=["Checking test results against quality gates"],
            files=[("MODIFY", "run_tests.py", "Results validation")]
        )
        
        logger.info("Validating test results against quality gates")
        
        # Define quality gates
        quality_gates = {
            "min_pass_rate": 90.0,  # Minimum acceptable pass rate
            "max_execution_time_ms": 5000.0,  # Maximum acceptable execution time
            "structural_integrity": True  # Require structural integrity
        }
        
        # Validate against quality gates
        validation = {
            "timestamp": datetime.now().isoformat(),
            "pass_rate_threshold_met": summary["pass_rate"] >= quality_gates["min_pass_rate"],
            "performance_threshold_met": summary["total_execution_time_ms"] <= quality_gates["max_execution_time_ms"],
            "structural_integrity": True,  # Assume true initially
            "issues": []
        }
        
        # Check for issues
        if not validation["pass_rate_threshold_met"]:
            validation["issues"].append(
                f"Pass rate ({summary['pass_rate']}%) below threshold ({quality_gates['min_pass_rate']}%)"
            )
        
        if not validation["performance_threshold_met"]:
            validation["issues"].append(
                f"Execution time ({summary['total_execution_time_ms']}ms) exceeds threshold ({quality_gates['max_execution_time_ms']}ms)"
            )
        
        # Check structural integrity
        for suite_name, suite_results in summary["suite_results"].items():
            if "total_tests" not in suite_results or "passed_tests" not in suite_results:
                validation["structural_integrity"] = False
                validation["issues"].append(f"Suite '{suite_name}' missing required result fields")
        
        # Overall validation status
        validation["passed"] = (
            validation["pass_rate_threshold_met"] and 
            validation["performance_threshold_met"] and 
            validation["structural_integrity"]
        )
        
        # Save validation results
        validation_file = self.results_dir / "validation_results.json"
        with open(validation_file, "w") as f:
            json.dump(validation, f, indent=2)
        
        logger.info(f"Validation completed: {'PASSED' if validation['passed'] else 'FAILED'}")
        if validation["issues"]:
            for issue in validation["issues"]:
                logger.warning(f"Validation issue: {issue}")
        
        logger.info(f"Validation results saved to {validation_file}")
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed test results validation",
            changes=[
                f"Validation status: {'PASSED' if validation['passed'] else 'FAILED'}",
                f"Issues found: {len(validation['issues'])}"
            ],
            files=[
                ("MODIFY", "run_tests.py", "Results validation"),
                ("CREATE", str(validation_file), "Validation results")
            ]
        )
        
        return validation
    
    def update_workspace_structure(self) -> None:
        """
        Update workspace structure documentation
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Updating workspace structure",
            changes=["Synchronizing workspace structure documentation"],
            files=[("MODIFY", "workspace_structure_complete.md", "Structure update")]
        )
        
        logger.info("Updating workspace structure documentation")
        
        try:
            # Run the workspace structure update script
            from scripts.core.update_workspace_structure import update_workspace_structure
            start_time = time.time()
            update_workspace_structure()
            execution_time_ms = round((time.time() - start_time) * 1000, 2)
            
            logger.info(f"Workspace structure updated in {execution_time_ms}ms")
            
            # Post-Response: System validation
            self.changelog_engine.quick_update(
                action_summary="Completed workspace structure update",
                changes=[f"Workspace structure documentation synchronized in {execution_time_ms}ms"],
                files=[("MODIFY", "workspace_structure_complete.md", "Structure update")]
            )
        except Exception as e:
            logger.error(f"Error updating workspace structure: {str(e)}")
            
            # Error Handling: Recovery protocol activation
            self.changelog_engine.quick_update(
                action_summary="Failed to update workspace structure",
                changes=[f"Error updating workspace structure: {str(e)}"],
                files=[("READ", "workspace_structure_complete.md", "Structure update attempt")]
            )


def main():
    """Main function to run all tests"""
    try:
        # Create test runner
        runner = TestRunner()
        
        # Run all tests
        summary = runner.run_all_tests()
        
        # Validate results
        validation = runner.validate_results(summary)
        
        # Update workspace structure
        runner.update_workspace_structure()
        
        # Print final summary
        print("\n=== Test Execution Summary ===")
        print(f"Total Test Suites: {summary['total_suites']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Pass Rate: {summary['pass_rate']}%")
        print(f"Execution Time: {summary['total_execution_time_ms']}ms")
        print("\n=== Validation Results ===")
        print(f"Validation Status: {'PASSED' if validation['passed'] else 'FAILED'}")
        if validation["issues"]:
            print("Validation Issues:")
            for issue in validation["issues"]:
                print(f"  - {issue}")
        
        return 0 if validation["passed"] else 1
    
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        
        # Error Handling: Recovery protocol activation
        changelog_engine = ChangelogEngine()
        changelog_engine.quick_update(
            action_summary="Test execution error",
            changes=[f"Error running tests: {str(e)}"],
            files=[("READ", "run_tests.py", "Error recovery")]
        )
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
