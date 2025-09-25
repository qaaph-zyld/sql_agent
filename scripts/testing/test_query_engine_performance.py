"""
Performance Tests for Query Engine

This module contains performance tests for the SQL Agent's Query Engine,
measuring the performance of query generation, validation, and execution operations.

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
from query.enhanced_query_engine import EnhancedQueryEngine
from query.query_engine import QueryEngine
from testing.performance_test_framework import PerformanceTestCase, PerformanceTestSuite, benchmark_function

class QueryEnginePerformanceTest(PerformanceTestCase):
    """
    Performance tests for the Query Engine component
    """
    def setUp(self):
        """Set up performance test with changelog update"""
        super().setUp()
        
        # Create test directories
        self.test_dir = Path("test_data/performance")
        self.test_dir.mkdir(exist_ok=True, parents=True)
        
        # Create test data
        self.simple_queries = [
            "SELECT * FROM customers",
            "SELECT id, name FROM products WHERE price > 100",
            "SELECT order_id, customer_id, total FROM orders WHERE date > '2023-01-01'",
            "SELECT c.name, o.total FROM customers c JOIN orders o ON c.id = o.customer_id"
        ]
        
        self.complex_queries = [
            "SELECT c.name, COUNT(o.id) as order_count, SUM(o.total) as total_spent FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.name HAVING COUNT(o.id) > 5 ORDER BY total_spent DESC",
            "SELECT p.category, AVG(p.price) as avg_price, COUNT(DISTINCT o.customer_id) as customer_count FROM products p JOIN order_items oi ON p.id = oi.product_id JOIN orders o ON o.id = oi.order_id WHERE p.price > 50 GROUP BY p.category ORDER BY customer_count DESC",
            "SELECT EXTRACT(MONTH FROM o.date) as month, p.category, SUM(oi.quantity * p.price) as revenue FROM orders o JOIN order_items oi ON o.id = oi.order_id JOIN products p ON p.id = oi.product_id WHERE o.date BETWEEN '2023-01-01' AND '2023-12-31' GROUP BY month, p.category ORDER BY month, revenue DESC",
            "WITH customer_spending AS (SELECT o.customer_id, SUM(o.total) as total_spent FROM orders o WHERE o.date > '2023-01-01' GROUP BY o.customer_id) SELECT c.name, cs.total_spent, RANK() OVER (ORDER BY cs.total_spent DESC) as spending_rank FROM customers c JOIN customer_spending cs ON c.id = cs.customer_id WHERE cs.total_spent > 1000 ORDER BY spending_rank"
        ]
        
        self.nl_queries = [
            "Show me all customers",
            "Find products that cost more than $100",
            "Get orders placed after January 1, 2023",
            "Show customer names and their order totals"
        ]
        
        self.complex_nl_queries = [
            "Show me customers who placed more than 5 orders and their total spending",
            "What's the average price of products by category and how many customers bought from each category?",
            "Calculate monthly revenue by product category for 2023",
            "Rank customers by their spending since January 2023 who spent more than $1000"
        ]
        
        # Create query engines
        self.query_engine = QueryEngine()
        self.enhanced_query_engine = EnhancedQueryEngine()
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Setting up query engine performance test environment",
            changes=[
                "Created test data directory and sample queries",
                "Initialized query engines for performance testing"
            ],
            files=[
                ("CREATE", str(self.test_dir), "Test data directory"),
                ("READ", "scripts/testing/test_query_engine_performance.py", "Performance test setup")
            ]
        )
    
    def test_query_validation_performance(self):
        """Test the performance of query validation method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing query validation performance",
            changes=["Measuring performance of query validation with various query complexities"],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
        
        # Test simple queries validation
        metrics_simple = self.measure_performance("QueryEngine", "validate_query_simple")
        metrics_simple.start_measurement()
        for query in self.simple_queries:
            self.query_engine.validate_query(query)
        metrics_simple.end_measurement()
        
        # Test complex queries validation
        metrics_complex = self.measure_performance("QueryEngine", "validate_query_complex")
        metrics_complex.start_measurement()
        for query in self.complex_queries:
            self.query_engine.validate_query(query)
        metrics_complex.end_measurement()
        
        # Assert performance meets thresholds
        self.assertPerformance("QueryEngine", "validate_query_simple", 
                              execution_time_threshold_ms=200)
        self.assertPerformance("QueryEngine", "validate_query_complex", 
                              execution_time_threshold_ms=500)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed query validation performance test",
            changes=[
                "Measured performance of query validation with different query complexities",
                "All performance metrics within acceptable thresholds"
            ],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
    
    def test_query_generation_performance(self):
        """Test the performance of query generation method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing query generation performance",
            changes=["Measuring performance of query generation with various natural language queries"],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
        
        # Test simple natural language queries
        metrics_simple_nl = self.measure_performance("EnhancedQueryEngine", "generate_query_simple_nl")
        metrics_simple_nl.start_measurement()
        for nl_query in self.nl_queries:
            self.enhanced_query_engine.generate_query(nl_query)
        metrics_simple_nl.end_measurement()
        
        # Test complex natural language queries
        metrics_complex_nl = self.measure_performance("EnhancedQueryEngine", "generate_query_complex_nl")
        metrics_complex_nl.start_measurement()
        for nl_query in self.complex_nl_queries:
            self.enhanced_query_engine.generate_query(nl_query)
        metrics_complex_nl.end_measurement()
        
        # Assert performance meets thresholds
        self.assertPerformance("EnhancedQueryEngine", "generate_query_simple_nl", 
                              execution_time_threshold_ms=500)
        self.assertPerformance("EnhancedQueryEngine", "generate_query_complex_nl", 
                              execution_time_threshold_ms=1000)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed query generation performance test",
            changes=[
                "Measured performance of query generation with different natural language query complexities",
                "All performance metrics within acceptable thresholds"
            ],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
    
    def test_query_optimization_performance(self):
        """Test the performance of query optimization method"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing query optimization performance",
            changes=["Measuring performance of query optimization with various query complexities"],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
        
        # Test simple queries optimization
        metrics_simple_opt = self.measure_performance("EnhancedQueryEngine", "optimize_query_simple")
        metrics_simple_opt.start_measurement()
        for query in self.simple_queries:
            self.enhanced_query_engine.optimize_query(query)
        metrics_simple_opt.end_measurement()
        
        # Test complex queries optimization
        metrics_complex_opt = self.measure_performance("EnhancedQueryEngine", "optimize_query_complex")
        metrics_complex_opt.start_measurement()
        for query in self.complex_queries:
            self.enhanced_query_engine.optimize_query(query)
        metrics_complex_opt.end_measurement()
        
        # Assert performance meets thresholds
        self.assertPerformance("EnhancedQueryEngine", "optimize_query_simple", 
                              execution_time_threshold_ms=300)
        self.assertPerformance("EnhancedQueryEngine", "optimize_query_complex", 
                              execution_time_threshold_ms=800)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed query optimization performance test",
            changes=[
                "Measured performance of query optimization with different query complexities",
                "All performance metrics within acceptable thresholds"
            ],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
    
    def test_end_to_end_query_processing_performance(self):
        """Test the performance of end-to-end query processing"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing end-to-end query processing performance",
            changes=["Measuring performance of complete query processing pipeline"],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
        
        # Test simple natural language queries end-to-end
        metrics_simple_e2e = self.measure_performance("EnhancedQueryEngine", "process_query_simple_e2e")
        metrics_simple_e2e.start_measurement()
        for nl_query in self.nl_queries:
            # Generate SQL query from natural language
            sql_query = self.enhanced_query_engine.generate_query(nl_query)
            # Validate the query
            self.enhanced_query_engine.validate_query(sql_query)
            # Optimize the query
            optimized_query = self.enhanced_query_engine.optimize_query(sql_query)
        metrics_simple_e2e.end_measurement()
        
        # Test complex natural language queries end-to-end
        metrics_complex_e2e = self.measure_performance("EnhancedQueryEngine", "process_query_complex_e2e")
        metrics_complex_e2e.start_measurement()
        for nl_query in self.complex_nl_queries:
            # Generate SQL query from natural language
            sql_query = self.enhanced_query_engine.generate_query(nl_query)
            # Validate the query
            self.enhanced_query_engine.validate_query(sql_query)
            # Optimize the query
            optimized_query = self.enhanced_query_engine.optimize_query(sql_query)
        metrics_complex_e2e.end_measurement()
        
        # Assert performance meets thresholds
        self.assertPerformance("EnhancedQueryEngine", "process_query_simple_e2e", 
                              execution_time_threshold_ms=1000)
        self.assertPerformance("EnhancedQueryEngine", "process_query_complex_e2e", 
                              execution_time_threshold_ms=2000)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed end-to-end query processing performance test",
            changes=[
                "Measured performance of complete query processing pipeline with different query complexities",
                "All performance metrics within acceptable thresholds"
            ],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
    
    def test_benchmark_function_usage(self):
        """Test the usage of the benchmark_function utility"""
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing benchmark_function utility for query engine",
            changes=["Demonstrating the usage of benchmark_function for quick performance measurements"],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
        
        # Use benchmark_function to measure performance
        benchmark_result = benchmark_function(
            self.query_engine.validate_query,
            self.simple_queries[0]
        )
        
        # Extract performance data
        performance_data = benchmark_result["performance"]
        
        # Log performance data
        self.changelog_engine.quick_update(
            action_summary="Completed benchmark_function test for query engine",
            changes=[
                f"Measured validate_query performance using benchmark_function",
                f"Execution time: {performance_data['execution_time_ms']}ms"
            ],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
        )
    
    def tearDown(self):
        """Clean up test environment with changelog update"""
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Cleaning up query engine performance test environment",
            changes=["Completed performance tests for query engine"],
            files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test cleanup")]
        )
        
        super().tearDown()


def run_performance_tests():
    """Run all performance tests for query engine"""
    # Create changelog engine
    changelog_engine = ChangelogEngine()
    
    # Pre-Response: Changelog update execution
    changelog_engine.quick_update(
        action_summary="Running query engine performance tests",
        changes=["Executing performance tests for query engine"],
        files=[("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution")]
    )
    
    # Create test suite
    suite = PerformanceTestSuite(
        name="QueryEnginePerformance",
        output_dir="test_output/performance"
    )
    
    # Add test cases
    import unittest
    test_loader = unittest.TestLoader()
    test_cases = test_loader.loadTestsFromTestCase(QueryEnginePerformanceTest)
    
    for test_case in test_cases:
        suite.add_test_case(test_case)
    
    # Run tests
    results = suite.run_tests()
    
    # Post-Response: System validation
    changelog_engine.quick_update(
        action_summary="Completed query engine performance tests",
        changes=[
            f"Executed {results['total_tests']} performance tests",
            f"Pass rate: {results['pass_rate']}%",
            f"Total execution time: {results['total_execution_time_ms']}ms"
        ],
        files=[
            ("READ", "scripts/testing/test_query_engine_performance.py", "Performance test execution"),
            ("CREATE", f"test_output/performance/QueryEnginePerformance_results.json", "Performance test results")
        ]
    )
    
    return results


if __name__ == "__main__":
    run_performance_tests()
