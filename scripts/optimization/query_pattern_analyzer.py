#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Query Pattern Analyzer Module

This module analyzes SQL query patterns to identify optimization opportunities.
It follows the mandatory changelog protocol.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import Counter

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/query_pattern_analyzer.log'
)
logger = logging.getLogger(__name__)

class QueryPatternAnalyzer:
    """
    Main class for analyzing SQL query patterns.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the query pattern analyzer with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.patterns = {}
        self.query_history = []
        
        # Pre-response: Update changelog
        self._update_changelog("Query pattern analyzer initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """
        Update the changelog following the mandatory protocol.
        
        Args:
            action_summary: Summary of the action being performed
        """
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Query Accuracy Improvement",
            previous_state="Query pattern analysis not started",
            current_state="Query pattern analysis in progress",
            changes_made=["Initialized query pattern analyzer", "Set up pattern recognition framework"],
            files_affected=[
                {"file_path": "scripts/optimization/query_pattern_analyzer.py", 
                 "change_type": "CREATED", 
                 "impact_level": "HIGH"}
            ],
            technical_decisions=[
                "Implemented regex-based pattern recognition",
                "Added frequency analysis for query patterns",
                "Created optimization suggestion system based on patterns",
                "Integrated with changelog system for protocol compliance"
            ]
        )
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a single SQL query for patterns.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing query: {query[:50]}...")
        
        # Store query in history
        self.query_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query
        })
        
        # Identify patterns in the query
        patterns = self._identify_patterns(query)
        
        # Update pattern statistics
        for pattern_name, pattern_data in patterns.items():
            if pattern_name not in self.patterns:
                self.patterns[pattern_name] = {
                    "count": 0,
                    "examples": []
                }
            
            self.patterns[pattern_name]["count"] += 1
            if len(self.patterns[pattern_name]["examples"]) < 5:  # Store up to 5 examples
                self.patterns[pattern_name]["examples"].append({
                    "query": query,
                    "details": pattern_data
                })
        
        # Generate analysis result
        analysis = {
            "query": query,
            "patterns_identified": list(patterns.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis
    
    def _identify_patterns(self, query: str) -> Dict[str, Any]:
        """
        Identify patterns in a SQL query.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            Dictionary of identified patterns
        """
        patterns = {}
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*\s+FROM', query, re.IGNORECASE):
            patterns["select_all"] = {
                "description": "Using SELECT * instead of specific columns",
                "optimization_potential": "HIGH",
                "suggestion": "Specify only needed columns to reduce data transfer"
            }
        
        # Check for missing WHERE clause
        if not re.search(r'WHERE', query, re.IGNORECASE) and re.search(r'FROM\s+\w+', query, re.IGNORECASE):
            patterns["missing_where"] = {
                "description": "Query without WHERE clause",
                "optimization_potential": "HIGH",
                "suggestion": "Add WHERE clause to filter results and reduce data transfer"
            }
        
        # Check for LIKE with leading wildcard
        if re.search(r'LIKE\s+[\'"]%', query, re.IGNORECASE):
            patterns["like_leading_wildcard"] = {
                "description": "LIKE with leading wildcard",
                "optimization_potential": "HIGH",
                "suggestion": "Avoid leading wildcards as they prevent index usage"
            }
        
        # Check for functions in WHERE clause
        if re.search(r'WHERE\s+\w+\([^)]*\)', query, re.IGNORECASE):
            patterns["function_in_where"] = {
                "description": "Function applied to column in WHERE clause",
                "optimization_potential": "MEDIUM",
                "suggestion": "Move function to right side of comparison to allow index usage"
            }
        
        # Check for multiple joins
        join_count = len(re.findall(r'JOIN', query, re.IGNORECASE))
        if join_count > 2:
            patterns["multiple_joins"] = {
                "description": f"Query with {join_count} joins",
                "optimization_potential": "MEDIUM",
                "suggestion": "Review join order and ensure proper indexing"
            }
        
        # Check for ORDER BY on non-indexed column (simplified check)
        if re.search(r'ORDER BY', query, re.IGNORECASE):
            patterns["order_by"] = {
                "description": "ORDER BY clause present",
                "optimization_potential": "LOW",
                "suggestion": "Ensure ORDER BY columns are indexed"
            }
        
        # Check for GROUP BY
        if re.search(r'GROUP BY', query, re.IGNORECASE):
            patterns["group_by"] = {
                "description": "GROUP BY clause present",
                "optimization_potential": "LOW",
                "suggestion": "Ensure GROUP BY columns are indexed"
            }
        
        # Check for subqueries
        if re.search(r'\(\s*SELECT', query, re.IGNORECASE):
            patterns["subquery"] = {
                "description": "Subquery present",
                "optimization_potential": "MEDIUM",
                "suggestion": "Consider replacing with JOIN if possible"
            }
        
        return patterns
    
    def analyze_query_batch(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze a batch of SQL queries for patterns.
        
        Args:
            queries: List of SQL queries to analyze
            
        Returns:
            List of analysis results
        """
        logger.info(f"Analyzing batch of {len(queries)} queries")
        
        results = []
        for query in queries:
            results.append(self.analyze_query(query))
        
        # Update changelog
        self._update_changelog(f"Analyzed batch of {len(queries)} queries")
        
        return results
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on identified patterns.
        
        Returns:
            Dictionary with pattern statistics
        """
        stats = {
            "total_queries_analyzed": len(self.query_history),
            "patterns": {}
        }
        
        for pattern_name, pattern_data in self.patterns.items():
            stats["patterns"][pattern_name] = {
                "count": pattern_data["count"],
                "percentage": (pattern_data["count"] / len(self.query_history)) * 100 if self.query_history else 0
            }
        
        return stats
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get optimization recommendations based on identified patterns.
        
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Sort patterns by frequency
        sorted_patterns = sorted(
            self.patterns.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        for pattern_name, pattern_data in sorted_patterns:
            # Only recommend if pattern occurs frequently enough
            if pattern_data["count"] >= 3 or (self.query_history and pattern_data["count"] / len(self.query_history) > 0.1):
                example = pattern_data["examples"][0]["query"] if pattern_data["examples"] else ""
                
                if pattern_name == "select_all":
                    recommendations.append({
                        "pattern": "SELECT *",
                        "frequency": pattern_data["count"],
                        "recommendation": "Replace SELECT * with specific columns",
                        "example": example,
                        "priority": "HIGH"
                    })
                
                elif pattern_name == "like_leading_wildcard":
                    recommendations.append({
                        "pattern": "LIKE with leading wildcard",
                        "frequency": pattern_data["count"],
                        "recommendation": "Avoid LIKE '%value' patterns, use full-text search instead",
                        "example": example,
                        "priority": "HIGH"
                    })
                
                elif pattern_name == "function_in_where":
                    recommendations.append({
                        "pattern": "Function in WHERE clause",
                        "frequency": pattern_data["count"],
                        "recommendation": "Move functions to right side of comparison",
                        "example": example,
                        "priority": "MEDIUM"
                    })
                
                elif pattern_name == "multiple_joins":
                    recommendations.append({
                        "pattern": "Multiple joins",
                        "frequency": pattern_data["count"],
                        "recommendation": "Review join order and ensure proper indexing",
                        "example": example,
                        "priority": "MEDIUM"
                    })
                
                elif pattern_name == "subquery":
                    recommendations.append({
                        "pattern": "Subqueries",
                        "frequency": pattern_data["count"],
                        "recommendation": "Consider replacing with JOIN operations",
                        "example": example,
                        "priority": "MEDIUM"
                    })
        
        # Update changelog
        self._update_changelog(f"Generated {len(recommendations)} optimization recommendations")
        
        return recommendations
    
    def generate_analysis_report(self, output_file: str) -> Dict[str, Any]:
        """
        Generate a report of query pattern analysis.
        
        Args:
            output_file: File to write the report to
            
        Returns:
            Report data
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries_analyzed": len(self.query_history),
            "pattern_statistics": self.get_pattern_statistics(),
            "optimization_recommendations": self.get_optimization_recommendations()
        }
        
        # Write report to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Generated query pattern analysis report: {output_file}")
        
        # Update changelog
        self._update_changelog(f"Generated query pattern analysis report")
        
        return report

# Example usage
if __name__ == "__main__":
    analyzer = QueryPatternAnalyzer()
    
    # Sample queries to analyze
    sample_queries = [
        "SELECT * FROM customers WHERE last_name LIKE '%smith%'",
        "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id JOIN products ON orders.product_id = products.id WHERE YEAR(order_date) = 2023",
        "SELECT * FROM transactions WHERE UPPER(status) = 'COMPLETED' ORDER BY transaction_date",
        "SELECT id, name FROM users WHERE UPPER(email) = 'TEST@EXAMPLE.COM'",
        "SELECT * FROM products",
        "SELECT COUNT(*) FROM orders GROUP BY customer_id",
        "SELECT * FROM orders WHERE id IN (SELECT order_id FROM order_items WHERE product_id = 123)"
    ]
    
    # Analyze queries
    for query in sample_queries:
        analyzer.analyze_query(query)
    
    # Generate report
    report = analyzer.generate_analysis_report("logs/query_pattern_analysis_report.json")
    print(f"Analyzed {len(sample_queries)} queries and identified {len(analyzer.patterns)} patterns")
