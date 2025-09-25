#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQL Syntax Optimizer Module

This module optimizes SQL syntax for better performance and readability.
It follows the mandatory changelog protocol.
"""

import logging
import json
import re
from typing import Dict, List, Any
from datetime import datetime

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/sql_syntax_optimizer.log'
)
logger = logging.getLogger(__name__)

class SQLSyntaxOptimizer:
    """
    Main class for optimizing SQL syntax.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the SQL syntax optimizer with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.optimizations = []
        
        # Pre-response: Update changelog
        self._update_changelog("SQL syntax optimizer initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Query Accuracy Improvement",
            previous_state="SQL syntax optimization not started",
            current_state="SQL syntax optimization in progress",
            changes_made=["Initialized SQL syntax optimizer", "Set up optimization rules"],
            files_affected=[
                {"file_path": "scripts/optimization/sql_syntax_optimizer.py", 
                 "change_type": "CREATED", 
                 "impact_level": "HIGH"}
            ],
            technical_decisions=[
                "Implemented regex-based syntax optimization",
                "Added query transformation rules",
                "Created optimization tracking system",
                "Integrated with changelog system for protocol compliance"
            ]
        )
    
    def optimize_query(self, query: str) -> Dict[str, Any]:
        """
        Optimize a SQL query for better performance and readability.
        
        Args:
            query: SQL query to optimize
            
        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Optimizing query: {query[:50]}...")
        
        original_query = query
        optimizations = []
        
        # Apply optimization rules
        query, rule_optimizations = self._apply_optimization_rules(query)
        optimizations.extend(rule_optimizations)
        
        # Record optimization
        optimization_record = {
            "timestamp": datetime.now().isoformat(),
            "original_query": original_query,
            "optimized_query": query,
            "optimizations_applied": optimizations
        }
        
        self.optimizations.append(optimization_record)
        
        # Update changelog if optimizations were applied
        if optimizations:
            self._update_changelog(f"Optimized query with {len(optimizations)} improvements")
        
        return optimization_record
    
    def _apply_optimization_rules(self, query: str) -> tuple:
        """Apply optimization rules to a SQL query."""
        optimizations = []
        
        # Rule 1: Replace SELECT * with specific columns
        if re.search(r'SELECT\s+\*\s+FROM', query, re.IGNORECASE):
            optimizations.append({
                "rule": "avoid_select_star",
                "description": "Replace SELECT * with specific columns",
                "impact": "HIGH",
                "recommendation": True
            })
        
        # Rule 2: Optimize LIKE with leading wildcard
        like_pattern = re.search(r'(WHERE|AND|OR)\s+(\w+)\s+LIKE\s+[\'"]%([^\'"%]+)[\'"]', query, re.IGNORECASE)
        if like_pattern:
            optimizations.append({
                "rule": "optimize_like_wildcard",
                "description": "LIKE with leading wildcard prevents index usage",
                "impact": "HIGH",
                "recommendation": True
            })
        
        # Rule 3: Optimize function in WHERE clause
        function_in_where = re.search(r'WHERE\s+(\w+\([^)]+\))\s*([=><])', query, re.IGNORECASE)
        if function_in_where:
            optimizations.append({
                "rule": "function_in_where",
                "description": "Function in WHERE clause prevents index usage",
                "impact": "MEDIUM",
                "recommendation": True
            })
        
        # Rule 4: Add explicit JOIN type
        implicit_join = re.search(r'FROM\s+(\w+),\s*(\w+)\s+WHERE\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', query, re.IGNORECASE)
        if implicit_join:
            table1 = implicit_join.group(1)
            table2 = implicit_join.group(2)
            col1_table = implicit_join.group(3)
            col1 = implicit_join.group(4)
            col2_table = implicit_join.group(5)
            col2 = implicit_join.group(6)
            
            # Create explicit join syntax
            explicit_join = f"FROM {table1} INNER JOIN {table2} ON {col1_table}.{col1} = {col2_table}.{col2}"
            
            # Replace in query
            new_query = query.replace(implicit_join.group(0), explicit_join)
            
            optimizations.append({
                "rule": "explicit_join_syntax",
                "description": "Replace implicit join with explicit JOIN syntax",
                "impact": "LOW",
                "applied": True
            })
            
            query = new_query
        
        # Rule 5: Standardize case for SQL keywords
        keywords = ["SELECT", "FROM", "WHERE", "JOIN", "AND", "OR", "GROUP BY", "ORDER BY"]
        for keyword in keywords:
            keyword_pattern = re.compile(rf'\b{keyword}\b', re.IGNORECASE)
            if keyword_pattern.search(query):
                query = keyword_pattern.sub(keyword, query)
                
                # Only add this optimization once
                if not any(opt["rule"] == "standardize_keyword_case" for opt in optimizations):
                    optimizations.append({
                        "rule": "standardize_keyword_case",
                        "description": "Standardize SQL keyword case for better readability",
                        "impact": "LOW",
                        "applied": True
                    })
        
        return query, optimizations
    
    def generate_report(self, output_file: str) -> Dict[str, Any]:
        """
        Generate a report of SQL syntax optimizations.
        
        Args:
            output_file: File to write the report to
            
        Returns:
            Report data
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries_optimized": len(self.optimizations),
            "optimizations_by_rule": self._get_optimization_stats(),
            "optimization_details": self.optimizations
        }
        
        # Write report to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Generated SQL syntax optimization report: {output_file}")
        
        # Update changelog
        self._update_changelog(f"Generated optimization report for {len(self.optimizations)} queries")
        
        return report
    
    def _get_optimization_stats(self) -> Dict[str, int]:
        """Get statistics on applied optimization rules."""
        stats = {}
        
        for optimization in self.optimizations:
            for rule in optimization["optimizations_applied"]:
                rule_name = rule["rule"]
                if rule_name not in stats:
                    stats[rule_name] = 0
                stats[rule_name] += 1
        
        return stats

# Example usage
if __name__ == "__main__":
    optimizer = SQLSyntaxOptimizer()
    
    # Sample queries to optimize
    sample_queries = [
        "select * from customers where last_name like '%smith%'",
        "select * from orders, customers where orders.customer_id = customers.id",
        "select * from transactions where upper(status) = 'COMPLETED'",
        "select id, name from users where email = 'test@example.com'"
    ]
    
    # Optimize queries
    for query in sample_queries:
        optimizer.optimize_query(query)
    
    # Generate report
    report = optimizer.generate_report("logs/sql_syntax_optimization_report.json")
    print(f"Optimized {len(sample_queries)} queries")
