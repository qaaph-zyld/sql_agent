"""
Performance Testing Framework for SQL Agent

This module provides a comprehensive performance testing framework for the SQL Agent project,
following the mandatory changelog protocol for all testing operations.

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
import time
import logging
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Union, Callable

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from core.changelog_engine import ChangelogEngine
from testing.test_framework import SQLAgentTestCase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/performance_tests.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """
    Collects and analyzes performance metrics for SQL Agent components
    """
    def __init__(self, component_name: str, operation_name: str):
        self.component_name = component_name
        self.operation_name = operation_name
        self.execution_times = []
        self.memory_usage = []
        self.start_time = None
        self.end_time = None
        self.current_memory = None
    
    def start_measurement(self) -> None:
        """Start performance measurement"""
        self.start_time = time.time()
        
        # Simulate memory measurement (would use actual memory profiling in production)
        self.current_memory = 0
        
        logger.info(f"Starting performance measurement for {self.component_name}.{self.operation_name}")
    
    def end_measurement(self) -> Dict[str, Any]:
        """
        End performance measurement and record metrics
        
        Returns:
            Dictionary with performance metrics
        """
        if self.start_time is None:
            raise ValueError("Measurement was not started")
        
        self.end_time = time.time()
        execution_time_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.execution_times.append(execution_time_ms)
        
        # Simulate memory measurement (would use actual memory profiling in production)
        self.current_memory = 1024  # Simulated 1KB memory usage
        self.memory_usage.append(self.current_memory)
        
        logger.info(f"Completed performance measurement for {self.component_name}.{self.operation_name}: {execution_time_ms}ms")
        
        return {
            "component": self.component_name,
            "operation": self.operation_name,
            "execution_time_ms": execution_time_ms,
            "memory_usage_kb": self.current_memory,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate performance statistics
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.execution_times:
            return {
                "component": self.component_name,
                "operation": self.operation_name,
                "samples": 0,
                "error": "No measurements recorded"
            }
        
        stats = {
            "component": self.component_name,
            "operation": self.operation_name,
            "samples": len(self.execution_times),
            "execution_time_ms": {
                "min": min(self.execution_times),
                "max": max(self.execution_times),
                "mean": statistics.mean(self.execution_times),
                "median": statistics.median(self.execution_times),
                "stdev": statistics.stdev(self.execution_times) if len(self.execution_times) > 1 else 0
            },
            "memory_usage_kb": {
                "min": min(self.memory_usage),
                "max": max(self.memory_usage),
                "mean": statistics.mean(self.memory_usage),
                "median": statistics.median(self.memory_usage),
                "stdev": statistics.stdev(self.memory_usage) if len(self.memory_usage) > 1 else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return stats


class PerformanceBenchmark:
    """
    Defines performance benchmarks and thresholds for SQL Agent components
    """
    def __init__(self, component_name: str, operation_name: str):
        self.component_name = component_name
        self.operation_name = operation_name
        self.execution_time_threshold_ms = 1000.0  # Default 1 second threshold
        self.memory_usage_threshold_kb = 10240  # Default 10MB threshold
    
    def set_thresholds(self, execution_time_ms: float = None, memory_usage_kb: float = None) -> None:
        """Set performance thresholds"""
        if execution_time_ms is not None:
            self.execution_time_threshold_ms = execution_time_ms
        
        if memory_usage_kb is not None:
            self.memory_usage_threshold_kb = memory_usage_kb
        
        logger.info(f"Set performance thresholds for {self.component_name}.{self.operation_name}: "
                   f"execution_time={self.execution_time_threshold_ms}ms, "
                   f"memory_usage={self.memory_usage_threshold_kb}KB")
    
    def validate_metrics(self, metrics: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate performance metrics against thresholds
        
        Args:
            metrics: Performance metrics to validate
            
        Returns:
            Tuple of (passed, issues)
        """
        passed = True
        issues = []
        
        # Check execution time
        if metrics["execution_time_ms"]["mean"] > self.execution_time_threshold_ms:
            passed = False
            issues.append(
                f"Execution time ({metrics['execution_time_ms']['mean']}ms) exceeds threshold "
                f"({self.execution_time_threshold_ms}ms)"
            )
        
        # Check memory usage
        if metrics["memory_usage_kb"]["mean"] > self.memory_usage_threshold_kb:
            passed = False
            issues.append(
                f"Memory usage ({metrics['memory_usage_kb']['mean']}KB) exceeds threshold "
                f"({self.memory_usage_threshold_kb}KB)"
            )
        
        return passed, issues


class PerformanceTestCase(SQLAgentTestCase):
    """
    Base test case for SQL Agent performance tests with changelog integration
    """
    def setUp(self):
        """Set up performance test case with changelog update"""
        super().setUp()
        self.performance_metrics = {}
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary=f"Setting up performance test: {self._testMethodName}",
            changes=[f"Initializing performance test environment for {self._testMethodName}"],
            files=[("READ", "scripts/testing/performance_test_framework.py", "Performance test setup")]
        )
        
        logger.info(f"Setting up performance test: {self._testMethodName}")
    
    def measure_performance(self, component_name: str, operation_name: str) -> PerformanceMetrics:
        """
        Create and track performance metrics for a component operation
        
        Args:
            component_name: Name of the component being tested
            operation_name: Name of the operation being tested
            
        Returns:
            PerformanceMetrics object for tracking
        """
        key = f"{component_name}.{operation_name}"
        if key not in self.performance_metrics:
            self.performance_metrics[key] = PerformanceMetrics(component_name, operation_name)
        
        return self.performance_metrics[key]
    
    def assertPerformance(self, component_name: str, operation_name: str, 
                         execution_time_threshold_ms: float = None,
                         memory_usage_threshold_kb: float = None) -> None:
        """
        Assert that performance metrics meet the specified thresholds
        
        Args:
            component_name: Name of the component being tested
            operation_name: Name of the operation being tested
            execution_time_threshold_ms: Maximum acceptable execution time in milliseconds
            memory_usage_threshold_kb: Maximum acceptable memory usage in kilobytes
        """
        key = f"{component_name}.{operation_name}"
        if key not in self.performance_metrics:
            self.fail(f"No performance metrics recorded for {key}")
        
        metrics = self.performance_metrics[key]
        stats = metrics.get_statistics()
        
        # Create benchmark
        benchmark = PerformanceBenchmark(component_name, operation_name)
        if execution_time_threshold_ms is not None:
            benchmark.set_thresholds(execution_time_ms=execution_time_threshold_ms,
                                    memory_usage_kb=memory_usage_threshold_kb)
        
        # Validate metrics
        passed, issues = benchmark.validate_metrics(stats)
        
        # Assert performance
        if not passed:
            self.fail(f"Performance test failed: {'; '.join(issues)}")
    
    def tearDown(self):
        """Tear down performance test case with changelog update"""
        # Collect all performance statistics
        all_stats = {}
        for key, metrics in self.performance_metrics.items():
            all_stats[key] = metrics.get_statistics()
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary=f"Completed performance test: {self._testMethodName}",
            changes=[
                f"Test execution completed with {len(self.performance_metrics)} performance measurements",
                f"Components tested: {', '.join(set(metrics.component_name for metrics in self.performance_metrics.values()))}"
            ],
            files=[("READ", "scripts/testing/performance_test_framework.py", "Performance test completion")]
        )
        
        super().tearDown()


class PerformanceTestSuite:
    """
    Test suite for performance tests with detailed metrics collection
    """
    def __init__(self, name: str, output_dir: str = "performance_test_results"):
        self.name = name
        self.tests: List[unittest.TestCase] = []
        self.results: Dict[str, Any] = {}
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.changelog_engine = ChangelogEngine()
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary=f"Initializing performance test suite: {name}",
            changes=[f"Created performance test suite {name} with output directory {output_dir}"],
            files=[("CREATE", "scripts/testing/performance_test_framework.py", "Performance test suite initialization")]
        )
        
        logger.info(f"Performance test suite '{name}' initialized with output directory: {output_dir}")
    
    def add_test_case(self, test_case: unittest.TestCase) -> None:
        """Add a test case to the suite"""
        self.tests.append(test_case)
        logger.info(f"Added test case {test_case.__class__.__name__}.{test_case._testMethodName} to suite '{self.name}'")
    
    def run_tests(self) -> Dict[str, Any]:
        """
        Run all performance tests in the suite and generate results
        
        Returns:
            Dictionary with test suite results
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary=f"Running performance test suite: {self.name}",
            changes=[f"Executing {len(self.tests)} performance tests in suite {self.name}"],
            files=[("MODIFY", "scripts/testing/performance_test_framework.py", "Performance test suite execution")]
        )
        
        start_time = time.time()
        logger.info(f"Starting performance test suite '{self.name}' with {len(self.tests)} tests")
        
        # Create test suite
        import unittest
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
        
        logger.info(f"Performance test suite '{self.name}' completed: {summary['passed_tests']}/{summary['total_tests']} tests passed")
        logger.info(f"Results saved to {results_file}")
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary=f"Completed performance test suite: {self.name}",
            changes=[
                f"Executed {summary['total_tests']} tests with {summary['passed_tests']} passed and {summary['failed_tests']} failed",
                f"Pass rate: {summary['pass_rate']}%",
                f"Total execution time: {summary['total_execution_time_ms']}ms"
            ],
            files=[
                ("MODIFY", "scripts/testing/performance_test_framework.py", "Performance test suite execution"),
                ("CREATE", str(results_file), "Performance test results output")
            ]
        )
        
        return summary


def benchmark_function(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Benchmark a function's performance
    
    Args:
        func: Function to benchmark
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Dictionary with performance metrics
    """
    # Create changelog engine
    changelog_engine = ChangelogEngine()
    
    # Pre-Response: Changelog update execution
    changelog_engine.quick_update(
        action_summary=f"Benchmarking function: {func.__name__}",
        changes=[f"Measuring performance of function {func.__name__}"],
        files=[("READ", "scripts/testing/performance_test_framework.py", "Function benchmarking")]
    )
    
    # Measure performance
    metrics = PerformanceMetrics(func.__module__, func.__name__)
    metrics.start_measurement()
    
    # Execute function
    result = func(*args, **kwargs)
    
    # End measurement
    performance_data = metrics.end_measurement()
    
    # Post-Response: System validation
    changelog_engine.quick_update(
        action_summary=f"Completed benchmarking function: {func.__name__}",
        changes=[f"Function executed in {performance_data['execution_time_ms']}ms"],
        files=[("READ", "scripts/testing/performance_test_framework.py", "Function benchmarking")]
    )
    
    return {
        "result": result,
        "performance": performance_data
    }
