"""
Unit Testing Framework for SQL Agent

This module provides a comprehensive testing framework for the SQL Agent,
with built-in changelog integration and validation suite compatibility.
It follows the mandatory changelog protocol at all testing stages.
"""

import os
import sys
import json
import time
import logging
import unittest
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Union, Callable

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/test_framework.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestResult:
    """
    Represents the result of a test execution with detailed metrics
    """
    def __init__(self, 
                 test_name: str, 
                 status: bool, 
                 execution_time_ms: float,
                 error_message: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.test_name = test_name
        self.status = status  # True for pass, False for fail
        self.execution_time_ms = execution_time_ms
        self.error_message = error_message
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test result to dictionary"""
        return {
            "test_name": self.test_name,
            "status": "PASS" if self.status else "FAIL",
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        """String representation of test result"""
        status_str = "PASS" if self.status else "FAIL"
        return f"{self.test_name}: {status_str} ({self.execution_time_ms:.2f}ms)"


class TestSuite:
    """
    Test suite that manages and executes tests with changelog integration
    """
    def __init__(self, name: str, output_dir: str = "test_results"):
        self.name = name
        self.tests: List[Tuple[str, Callable, Dict[str, Any]]] = []
        self.results: List[TestResult] = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.changelog_engine = ChangelogEngine()
        
        # Pre-execution changelog update
        self.changelog_engine.quick_update(
            action_summary=f"Initializing test suite: {name}",
            changes=[f"Created test suite {name} with output directory {output_dir}"],
            files=[("CREATE", "scripts/testing/test_framework.py", "Test framework initialization")]
        )
        
        logger.info(f"Test suite '{name}' initialized with output directory: {output_dir}")
    
    def add_test(self, name: str, test_func: Callable, metadata: Dict[str, Any] = None) -> None:
        """
        Add a test to the suite
        
        Args:
            name: Test name
            test_func: Test function to execute
            metadata: Additional test metadata
        """
        self.tests.append((name, test_func, metadata or {}))
        logger.info(f"Added test '{name}' to suite '{self.name}'")
    
    def run_tests(self) -> Dict[str, Any]:
        """
        Run all tests in the suite and generate results
        
        Returns:
            Dictionary with test suite results
        """
        # Pre-execution changelog update
        self.changelog_engine.quick_update(
            action_summary=f"Running test suite: {self.name}",
            changes=[f"Executing {len(self.tests)} tests in suite {self.name}"],
            files=[("MODIFY", "scripts/testing/test_framework.py", "Test suite execution")]
        )
        
        start_time = time.time()
        logger.info(f"Starting test suite '{self.name}' with {len(self.tests)} tests")
        
        self.results = []
        passed_tests = 0
        failed_tests = 0
        
        for name, test_func, metadata in self.tests:
            test_start_time = time.time()
            
            try:
                # Execute test function
                test_func()
                status = True
                error_message = None
                passed_tests += 1
                logger.info(f"Test '{name}' PASSED")
            except Exception as e:
                status = False
                error_message = str(e)
                failed_tests += 1
                logger.error(f"Test '{name}' FAILED: {error_message}")
            
            # Calculate execution time
            execution_time_ms = round((time.time() - test_start_time) * 1000, 2)
            
            # Create test result
            result = TestResult(
                test_name=name,
                status=status,
                execution_time_ms=execution_time_ms,
                error_message=error_message,
                metadata=metadata
            )
            
            self.results.append(result)
        
        # Calculate total execution time
        total_execution_time_ms = round((time.time() - start_time) * 1000, 2)
        
        # Generate summary
        summary = {
            "suite_name": self.name,
            "total_tests": len(self.tests),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": round((passed_tests / len(self.tests)) * 100, 2) if self.tests else 0,
            "total_execution_time_ms": total_execution_time_ms,
            "timestamp": datetime.now().isoformat(),
            "results": [result.to_dict() for result in self.results]
        }
        
        # Save results to file
        results_file = self.output_dir / f"{self.name}_results.json"
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Test suite '{self.name}' completed: {passed_tests}/{len(self.tests)} tests passed")
        logger.info(f"Results saved to {results_file}")
        
        # Post-execution changelog update
        self.changelog_engine.quick_update(
            action_summary=f"Completed test suite: {self.name}",
            changes=[
                f"Executed {len(self.tests)} tests with {passed_tests} passed and {failed_tests} failed",
                f"Pass rate: {summary['pass_rate']}%",
                f"Total execution time: {total_execution_time_ms}ms"
            ],
            files=[
                ("MODIFY", "scripts/testing/test_framework.py", "Test suite execution"),
                ("CREATE", str(results_file), "Test results output")
            ]
        )
        
        return summary


class SQLAgentTestCase(unittest.TestCase):
    """
    Base test case for SQL Agent with changelog integration
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.changelog_engine = ChangelogEngine()
        self.start_time = None
    
    def setUp(self):
        """Set up test case with changelog update"""
        self.start_time = time.time()
        test_name = self.id().split(".")[-1]
        
        # Pre-test changelog update
        self.changelog_engine.quick_update(
            action_summary=f"Starting test: {test_name}",
            changes=[f"Setting up test environment for {test_name}"],
            files=[("READ", "scripts/testing/test_framework.py", "Test case execution")]
        )
        
        logger.info(f"Setting up test: {test_name}")
    
    def tearDown(self):
        """Tear down test case with changelog update"""
        test_name = self.id().split(".")[-1]
        execution_time_ms = round((time.time() - self.start_time) * 1000, 2)
        
        # Post-test changelog update
        self.changelog_engine.quick_update(
            action_summary=f"Completed test: {test_name}",
            changes=[f"Test execution completed in {execution_time_ms}ms"],
            files=[("READ", "scripts/testing/test_framework.py", "Test case completion")]
        )
        
        logger.info(f"Tearing down test: {test_name} (execution time: {execution_time_ms}ms)")


def run_test_suite(test_case_class, suite_name: str = None) -> Dict[str, Any]:
    """
    Run a test suite using a test case class
    
    Args:
        test_case_class: Test case class to run
        suite_name: Optional name for the test suite
        
    Returns:
        Dictionary with test suite results
    """
    if suite_name is None:
        suite_name = test_case_class.__name__
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(test_case_class)
    
    # Create custom test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Initialize changelog engine
    changelog_engine = ChangelogEngine()
    
    # Pre-execution changelog update
    changelog_engine.quick_update(
        action_summary=f"Running test suite: {suite_name}",
        changes=[f"Executing unittest suite {suite_name}"],
        files=[("READ", "scripts/testing/test_framework.py", "Test suite execution")]
    )
    
    # Run tests
    start_time = time.time()
    result = runner.run(suite)
    execution_time_ms = round((time.time() - start_time) * 1000, 2)
    
    # Generate summary
    summary = {
        "suite_name": suite_name,
        "total_tests": result.testsRun,
        "passed_tests": result.testsRun - len(result.failures) - len(result.errors),
        "failed_tests": len(result.failures) + len(result.errors),
        "pass_rate": round(((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100, 2) if result.testsRun else 0,
        "total_execution_time_ms": execution_time_ms,
        "timestamp": datetime.now().isoformat()
    }
    
    # Post-execution changelog update
    changelog_engine.quick_update(
        action_summary=f"Completed test suite: {suite_name}",
        changes=[
            f"Executed {summary['total_tests']} tests with {summary['passed_tests']} passed and {summary['failed_tests']} failed",
            f"Pass rate: {summary['pass_rate']}%",
            f"Total execution time: {summary['total_execution_time_ms']}ms"
        ],
        files=[("READ", "scripts/testing/test_framework.py", "Test suite completion")]
    )
    
    return summary
