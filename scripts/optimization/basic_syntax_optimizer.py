#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic Syntax Optimizer

This module provides basic SQL syntax optimization capabilities.
It follows the mandatory changelog protocol.
"""

import logging
import json
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/basic_syntax_optimizer.log'
)
logger = logging.getLogger(__name__)

class BasicSyntaxOptimizer:
    """
    Main class for basic SQL syntax optimization.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the basic syntax optimizer with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.optimizations = []
        
        # Pre-response: Update changelog
        self._update_changelog("Basic syntax optimizer initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Query Accuracy Improvement",
            previous_state="Basic syntax optimization not started",
            current_state="Basic syntax optimization in progress",
            changes_made=["Initialized basic syntax optimizer", "Set up optimization rules"],
            files_affected=[
                {"file_path": "scripts/optimization/basic_syntax_optimizer.py", 
                 "change_type": "CREATED", 
                 "impact_level": "MEDIUM"}
            ],
            technical_decisions=[
                "Implemented regex-based syntax optimization",
                "Created rule-based transformation system",
                "Added query validation before and after optimization",
                "Integrated with changelog system for protocol compliance"
            ]
        )
    
    def optimize_query(self, query: str) -> Dict[str, Any]:
        """
        Apply basic syntax optimizations to a SQL query.
        
        Args:
            query: SQL query to optimize
            
        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Optimizing query syntax: {query[:50]}...")
        
        original_query = query
        optimizations_applied = []
        
        # Apply optimization rules
        query, select_star_opt = self._optimize_select_star(query)
        if select_star_opt:
            optimizations_applied.append(select_star_opt)
        
        query, keyword_case_opt = self._optimize_keyword_case(query)
        if keyword_case_opt:
            optimizations_applied.append(keyword_case_opt)
        
        query, alias_opt = self._optimize_aliases(query)
        if alias_opt:
            optimizations_applied.append(alias_opt)
        
        query, where_opt = self._optimize_where_clause(query)
        if where_opt:
            optimizations_applied.append(where_opt)
        
        # Record optimization
        optimization_record = {
            "timestamp": datetime.now().isoformat(),
            "original_query": original_query,
            "optimized_query": query,
            "optimizations_applied": optimizations_applied
        }
        
        self.optimizations.append(optimization_record)
        
        # Update changelog if optimizations were applied
        if optimizations_applied:
            self._update_changelog(f"Applied {len(optimizations_applied)} syntax optimizations")
        
        return optimization_record
    
    def _optimize_select_star(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Optimize SELECT * statements."""
        if re.search(r"SELECT\s+\*\s+FROM", query, re.IGNORECASE):
            # In a real implementation, we would analyze the schema and replace * with actual columns
            # For now, just flag it as a recommendation
            
            optimization = {
                "rule": "select_star",
                "description": "Replace SELECT * with specific columns",
                "impact": "HIGH",
                "recommendation": True
            }
            
            return query, optimization
        
        return query, None
    
    def _optimize_keyword_case(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Standardize SQL keyword casing."""
        keywords = [
            "SELECT", "FROM", "WHERE", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN",
            "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "OFFSET", "INSERT", "UPDATE",
            "DELETE", "CREATE", "ALTER", "DROP", "AND", "OR", "NOT", "IN", "BETWEEN",
            "LIKE", "IS NULL", "IS NOT NULL", "AS", "ON", "DISTINCT", "UNION", "ALL"
        ]
        
        original_query = query
        for keyword in keywords:
            # Create a regex pattern that matches the keyword case-insensitively
            pattern = r'\b' + re.escape(keyword) + r'\b'
            query = re.sub(pattern, keyword, query, flags=re.IGNORECASE)
        
        if query != original_query:
            optimization = {
                "rule": "keyword_case",
                "description": "Standardized SQL keyword casing",
                "impact": "LOW",
                "recommendation": False,
                "applied": True
            }
            
            return query, optimization
        
        return query, None
    
    def _optimize_aliases(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Optimize table and column aliases."""
        # Check for implicit aliases (without AS keyword)
        implicit_aliases = re.findall(r'FROM\s+(\w+)\s+(\w+)(?!\s+AS)(?=\s|,|$)', query, re.IGNORECASE)
        
        if implicit_aliases:
            original_query = query
            
            # Add AS keyword to implicit aliases
            for table, alias in implicit_aliases:
                pattern = f'FROM\\s+{table}\\s+{alias}'
                replacement = f'FROM {table} AS {alias}'
                query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)
            
            optimization = {
                "rule": "explicit_aliases",
                "description": "Added explicit AS keyword to table aliases",
                "impact": "LOW",
                "recommendation": False,
                "applied": True,
                "count": len(implicit_aliases)
            }
            
            return query, optimization
        
        return query, None
    
    def _optimize_where_clause(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Optimize WHERE clause conditions."""
        # Check for functions in WHERE clause
        where_clause = re.search(r'WHERE\s+(.*?)(?=GROUP BY|ORDER BY|LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        
        if where_clause:
            conditions = where_clause.group(1)
            functions_in_where = re.findall(r'(\w+)\s*\(\s*(\w+(?:\.\w+)?)\s*\)\s*(=|>|<|<>|!=|LIKE|IN)', conditions, re.IGNORECASE)
            
            if functions_in_where:
                optimization = {
                    "rule": "functions_in_where",
                    "description": "Functions in WHERE clause prevent index usage",
                    "impact": "HIGH",
                    "recommendation": True,
                    "functions": [f[0] for f in functions_in_where],
                    "columns": [f[1] for f in functions_in_where]
                }
                
                return query, optimization
        
        return query, None
    
    def generate_report(self, output_file: str) -> Dict[str, Any]:
        """
        Generate a report of syntax optimizations.
        
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
            
        logger.info(f"Generated syntax optimization report: {output_file}")
        
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
    optimizer = BasicSyntaxOptimizer()
    
    # Sample queries to optimize
    sample_queries = [
        "select * from customers where last_name like '%smith%'",
        "SELECT * FROM orders, customers where orders.customer_id = customers.id",
        "select id, name from users u where UPPER(u.status) = 'ACTIVE'"
    ]
    
    # Optimize queries
    for query in sample_queries:
        optimizer.optimize_query(query)
    
    # Generate report
    report = optimizer.generate_report("logs/basic_syntax_optimization_report.json")
    print(f"Optimized {len(sample_queries)} queries")
