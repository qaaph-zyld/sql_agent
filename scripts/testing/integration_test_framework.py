"""
Integration Testing Framework for SQL Agent

This module provides a comprehensive integration testing framework for the SQL Agent project,
following the mandatory changelog protocol for all testing operations.

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
from testing.test_framework import SQLAgentTestCase, TestSuite

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/integration_tests.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegrationTestResult:
    """
    Represents the result of an integration test with detailed metrics
    and component interaction data
    """
    def __init__(self, 
                 test_name: str, 
                 status: bool, 
                 execution_time_ms: float,
                 components_tested: List[str],
                 data_flow: List[Dict[str, Any]],
                 error_message: Optional[str] = None):
        self.test_name = test_name
        self.status = status  # True for pass, False for fail
        self.execution_time_ms = execution_time_ms
        self.components_tested = components_tested
        self.data_flow = data_flow
        self.error_message = error_message
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert integration test result to dictionary"""
        return {
            "test_name": self.test_name,
            "status": "PASS" if self.status else "FAIL",
            "execution_time_ms": self.execution_time_ms,
            "components_tested": self.components_tested,
            "data_flow": self.data_flow,
            "error_message": self.error_message,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        """String representation of integration test result"""
        status_str = "PASS" if self.status else "FAIL"
        return f"{self.test_name}: {status_str} ({self.execution_time_ms:.2f}ms) - Components: {', '.join(self.components_tested)}"


class ComponentInteraction:
    """
    Tracks and records interactions between components during integration testing
    """
    def __init__(self, source_component: str, target_component: str):
        self.source_component = source_component
        self.target_component = target_component
        self.interactions = []
        self.start_time = None
    
    def start_interaction(self, operation: str, input_data: Any = None) -> None:
        """Start tracking an interaction between components"""
        self.start_time = time.time()
        
        logger.info(f"Starting interaction: {self.source_component} -> {self.target_component} ({operation})")
    
    def end_interaction(self, output_data: Any = None, status: bool = True, error: str = None) -> Dict[str, Any]:
        """End tracking an interaction and record the details"""
        if self.start_time is None:
            raise ValueError("Interaction was not started")
        
        execution_time_ms = round((time.time() - self.start_time) * 1000, 2)
        
        interaction = {
            "source": self.source_component,
            "target": self.target_component,
            "execution_time_ms": execution_time_ms,
            "status": "SUCCESS" if status else "FAILURE",
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        self.interactions.append(interaction)
        
        logger.info(f"Completed interaction: {self.source_component} -> {self.target_component} "
                   f"({interaction['status']}, {execution_time_ms}ms)")
        
        return interaction


class IntegrationTestCase(SQLAgentTestCase):
    """
    Base test case for SQL Agent integration tests with changelog integration
    """
    def setUp(self):
        """Set up integration test case with changelog update"""
        super().setUp()
        self.component_interactions = []
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary=f"Setting up integration test: {self._testMethodName}",
            changes=[f"Initializing integration test environment for {self._testMethodName}"],
            files=[("READ", "scripts/testing/integration_test_framework.py", "Integration test setup")]
        )
        
        logger.info(f"Setting up integration test: {self._testMethodName}")
    
    def track_interaction(self, source_component: str, target_component: str) -> ComponentInteraction:
        """Create and track a new component interaction"""
        interaction = ComponentInteraction(source_component, target_component)
        self.component_interactions.append(interaction)
        return interaction
    
    def assertIntegrationFlow(self, components: List[str], expected_flow: List[Tuple[str, str]]) -> None:
        """
        Assert that the integration flow between components matches the expected flow
        
        Args:
            components: List of components involved in the integration test
            expected_flow: List of expected component interactions as (source, target) tuples
        """
        # Check that all components are present
        for component in components:
            self.assertIn(component, [interaction.source_component for interaction in self.component_interactions] + 
                         [interaction.target_component for interaction in self.component_interactions],
                         f"Component '{component}' not found in integration flow")
        
        # Check that all expected interactions occurred
        for source, target in expected_flow:
            self.assertTrue(any(interaction.source_component == source and interaction.target_component == target
                              for interaction in self.component_interactions),
                          f"Expected interaction '{source}' -> '{target}' not found")
    
    def tearDown(self):
        """Tear down integration test case with changelog update"""
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary=f"Completed integration test: {self._testMethodName}",
            changes=[
                f"Test execution completed with {len(self.component_interactions)} component interactions",
                f"Components tested: {', '.join(set([interaction.source_component for interaction in self.component_interactions] + [interaction.target_component for interaction in self.component_interactions]))}"
            ],
            files=[("READ", "scripts/testing/integration_test_framework.py", "Integration test completion")]
        )
        
        super().tearDown()


class IntegrationTestSuite:
    """
    Test suite for integration tests with detailed component interaction tracking
    """
    def __init__(self, name: str, output_dir: str = "integration_test_results"):
        self.name = name
        self.tests: List[unittest.TestCase] = []
        self.results: List[IntegrationTestResult] = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.changelog_engine = ChangelogEngine()
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary=f"Initializing integration test suite: {name}",
            changes=[f"Created integration test suite {name} with output directory {output_dir}"],
            files=[("CREATE", "scripts/testing/integration_test_framework.py", "Integration test suite initialization")]
        )
        
        logger.info(f"Integration test suite '{name}' initialized with output directory: {output_dir}")
    
    def add_test_case(self, test_case: unittest.TestCase) -> None:
        """Add a test case to the suite"""
        self.tests.append(test_case)
        logger.info(f"Added test case {test_case.__class__.__name__}.{test_case._testMethodName} to suite '{self.name}'")
    
    def run_tests(self) -> Dict[str, Any]:
        """
        Run all integration tests in the suite and generate results
        
        Returns:
            Dictionary with test suite results
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary=f"Running integration test suite: {self.name}",
            changes=[f"Executing {len(self.tests)} integration tests in suite {self.name}"],
            files=[("MODIFY", "scripts/testing/integration_test_framework.py", "Integration test suite execution")]
        )
        
        start_time = time.time()
        logger.info(f"Starting integration test suite '{self.name}' with {len(self.tests)} tests")
        
        # Create test suite
        suite = unittest.TestSuite()
        for test in self.tests:
            suite.addTest(test)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Calculate total execution time
        total_execution_time_ms = round((time.time() - start_time) * 1000, 2)
        
        # Generate summary
        summary = {
            "suite_name": self.name,
            "total_tests": result.testsRun,
            "passed_tests": result.testsRun - len(result.failures) - len(result.errors),
            "failed_tests": len(result.failures) + len(result.errors),
            "pass_rate": round(((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100, 2) if result.testsRun else 0,
            "total_execution_time_ms": total_execution_time_ms,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save results to file
        results_file = self.output_dir / f"{self.name}_results.json"
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Integration test suite '{self.name}' completed: {summary['passed_tests']}/{summary['total_tests']} tests passed")
        logger.info(f"Results saved to {results_file}")
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary=f"Completed integration test suite: {self.name}",
            changes=[
                f"Executed {summary['total_tests']} tests with {summary['passed_tests']} passed and {summary['failed_tests']} failed",
                f"Pass rate: {summary['pass_rate']}%",
                f"Total execution time: {summary['total_execution_time_ms']}ms"
            ],
            files=[
                ("MODIFY", "scripts/testing/integration_test_framework.py", "Integration test suite execution"),
                ("CREATE", str(results_file), "Integration test results output")
            ]
        )
        
        return summary


def create_end_to_end_test(components: List[str], test_name: str) -> Callable:
    """
    Create an end-to-end integration test function that tests
    the interaction between multiple components
    
    Args:
        components: List of components to test
        test_name: Name of the test
        
    Returns:
        Test function
    """
    def test_function(self):
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary=f"Running end-to-end test: {test_name}",
            changes=[f"Testing interaction between components: {', '.join(components)}"],
            files=[("READ", "scripts/testing/integration_test_framework.py", "End-to-end test execution")]
        )
        
        logger.info(f"Running end-to-end test: {test_name}")
        
        # Track interactions between components
        for i in range(len(components) - 1):
            source = components[i]
            target = components[i + 1]
            
            interaction = self.track_interaction(source, target)
            interaction.start_interaction("data_transfer")
            
            # Simulate interaction between components
            time.sleep(0.1)  # Simulate processing time
            
            interaction.end_interaction(status=True)
        
        # Assert that all expected interactions occurred
        expected_flow = [(components[i], components[i + 1]) for i in range(len(components) - 1)]
        self.assertIntegrationFlow(components, expected_flow)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary=f"Completed end-to-end test: {test_name}",
            changes=[f"Successfully tested interaction between components: {', '.join(components)}"],
            files=[("READ", "scripts/testing/integration_test_framework.py", "End-to-end test completion")]
        )
    
    return test_function
