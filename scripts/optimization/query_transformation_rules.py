#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Query Transformation Rules

This module provides SQL query transformation rules for optimization.
It follows the mandatory changelog protocol.
"""

import logging
import json
import re
from typing import Dict, List, Any, Tuple, Callable
from datetime import datetime

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/query_transformation.log'
)
logger = logging.getLogger(__name__)

class QueryTransformationRules:
    """
    Main class for SQL query transformation rules.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the query transformation rules with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.rules = {}
        self.transformations = []
        
        # Register default rules
        self._register_default_rules()
        
        # Pre-response: Update changelog
        self._update_changelog("Query transformation rules initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Query Accuracy Improvement",
            previous_state="Query transformation rules not defined",
            current_state="Query transformation rules initialized",
            changes_made=["Initialized query transformation rules", "Registered default transformation rules"],
            files_affected=[
                {"file_path": "scripts/optimization/query_transformation_rules.py", 
                 "change_type": "CREATED", 
                 "impact_level": "MEDIUM"}
            ],
            technical_decisions=[
                "Implemented rule-based transformation system",
                "Created pluggable rule architecture",
                "Added transformation tracking and validation",
                "Integrated with changelog system for protocol compliance"
            ]
        )
    
    def _register_default_rules(self) -> None:
        """Register default transformation rules."""
        # Convert implicit joins to explicit joins
        self.register_rule(
            name="implicit_to_explicit_join",
            description="Convert implicit joins to explicit JOIN syntax",
            impact="MEDIUM",
            transform_func=self._transform_implicit_joins
        )
        
        # Convert LIKE with leading wildcard to alternative
        self.register_rule(
            name="optimize_like_wildcards",
            description="Optimize LIKE with leading wildcards",
            impact="HIGH",
            transform_func=self._transform_like_wildcards
        )
        
        # Move functions in WHERE to the right side
        self.register_rule(
            name="optimize_where_functions",
            description="Move functions in WHERE clause to right side of comparison",
            impact="HIGH",
            transform_func=self._transform_where_functions
        )
        
        # Simplify redundant conditions
        self.register_rule(
            name="simplify_conditions",
            description="Simplify redundant WHERE conditions",
            impact="MEDIUM",
            transform_func=self._transform_redundant_conditions
        )
        
        # Convert subqueries to joins when possible
        self.register_rule(
            name="subquery_to_join",
            description="Convert simple subqueries to JOINs",
            impact="HIGH",
            transform_func=self._transform_subqueries
        )
    
    def register_rule(self, name: str, description: str, impact: str, transform_func: Callable) -> None:
        """
        Register a new transformation rule.
        
        Args:
            name: Unique name for the rule
            description: Description of the rule
            impact: Impact level (HIGH, MEDIUM, LOW)
            transform_func: Function that implements the transformation
        """
        logger.info(f"Registering transformation rule: {name}")
        
        self.rules[name] = {
            "description": description,
            "impact": impact,
            "transform_func": transform_func,
            "applications": 0
        }
    
    def apply_rules(self, query: str, rules_to_apply: List[str] = None) -> Dict[str, Any]:
        """
        Apply transformation rules to a SQL query.
        
        Args:
            query: SQL query to transform
            rules_to_apply: Optional list of rule names to apply (default: all rules)
            
        Returns:
            Dictionary with transformation results
        """
        logger.info(f"Applying transformation rules to query: {query[:50]}...")
        
        original_query = query
        applied_rules = []
        
        # Determine which rules to apply
        if rules_to_apply is None:
            rules_to_apply = list(self.rules.keys())
        
        # Apply each rule
        for rule_name in rules_to_apply:
            if rule_name in self.rules:
                rule = self.rules[rule_name]
                transform_func = rule["transform_func"]
                
                # Apply transformation
                query, applied = transform_func(query)
                
                if applied:
                    # Record application
                    self.rules[rule_name]["applications"] += 1
                    
                    # Add to applied rules
                    applied_rules.append({
                        "rule": rule_name,
                        "description": rule["description"],
                        "impact": rule["impact"]
                    })
        
        # Record transformation
        transformation_record = {
            "timestamp": datetime.now().isoformat(),
            "original_query": original_query,
            "transformed_query": query,
            "rules_applied": applied_rules
        }
        
        self.transformations.append(transformation_record)
        
        # Update changelog if rules were applied
        if applied_rules:
            self._update_changelog(f"Applied {len(applied_rules)} transformation rules")
        
        return transformation_record
    
    def _transform_implicit_joins(self, query: str) -> Tuple[str, bool]:
        """
        Transform implicit joins to explicit JOIN syntax.
        
        Args:
            query: SQL query to transform
            
        Returns:
            Tuple of (transformed query, whether transformation was applied)
        """
        # Pattern for FROM table1, table2 WHERE table1.col = table2.col
        implicit_join_pattern = re.compile(
            r'FROM\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?,\s*(\w+)(?:\s+(?:AS\s+)?(\w+))?\s+WHERE\s+(.*?)(?=GROUP BY|ORDER BY|LIMIT|$)',
            re.IGNORECASE | re.DOTALL
        )
        
        match = implicit_join_pattern.search(query)
        if not match:
            return query, False
        
        # Extract tables and aliases
        table1 = match.group(1)
        alias1 = match.group(2) if match.group(2) else table1
        table2 = match.group(3)
        alias2 = match.group(4) if match.group(4) else table2
        where_clause = match.group(5)
        
        # Look for join condition in WHERE clause
        join_condition_pattern = re.compile(
            rf'({alias1}\.(\w+)\s*=\s*{alias2}\.(\w+))|({alias2}\.(\w+)\s*=\s*{alias1}\.(\w+))',
            re.IGNORECASE
        )
        
        join_match = join_condition_pattern.search(where_clause)
        if not join_match:
            return query, False
        
        # Extract join condition
        if join_match.group(1):  # First pattern matched
            join_condition = join_match.group(1)
            remaining_where = where_clause.replace(join_condition, "").strip()
        else:  # Second pattern matched
            join_condition = join_match.group(4)
            remaining_where = where_clause.replace(join_condition, "").strip()
        
        # Clean up WHERE clause
        if remaining_where.startswith("AND "):
            remaining_where = remaining_where[4:]
        elif remaining_where.endswith(" AND"):
            remaining_where = remaining_where[:-4]
        
        # Build new query with explicit JOIN
        from_clause = f"FROM {table1}"
        if alias1 != table1:
            from_clause += f" AS {alias1}"
        
        join_clause = f" INNER JOIN {table2}"
        if alias2 != table2:
            join_clause += f" AS {alias2}"
        join_clause += f" ON {join_condition}"
        
        where_clause = f" WHERE {remaining_where}" if remaining_where else ""
        
        # Replace the FROM and WHERE clauses
        new_query = re.sub(
            r'FROM\s+\w+(?:\s+(?:AS\s+)?\w+)?,\s*\w+(?:\s+(?:AS\s+)?\w+)?\s+WHERE\s+.*?(?=GROUP BY|ORDER BY|LIMIT|$)',
            f"{from_clause}{join_clause}{where_clause}",
            query,
            flags=re.IGNORECASE | re.DOTALL
        )
        
        return new_query, True
    
    def _transform_like_wildcards(self, query: str) -> Tuple[str, bool]:
        """
        Transform LIKE with leading wildcards to alternatives.
        This is a recommendation-only transformation.
        
        Args:
            query: SQL query to transform
            
        Returns:
            Tuple of (transformed query, whether transformation was applied)
        """
        # Look for LIKE '%...%' or LIKE '%...'
        like_pattern = re.compile(r'(\w+(?:\.\w+)?)\s+LIKE\s+[\'"]%', re.IGNORECASE)
        
        if like_pattern.search(query):
            # Add a comment with recommendation
            if not "/* RECOMMENDATION:" in query:
                query = f"/* RECOMMENDATION: Consider using full-text search instead of LIKE with leading wildcards */\n{query}"
            return query, True
        
        return query, False
    
    def _transform_where_functions(self, query: str) -> Tuple[str, bool]:
        """
        Transform functions in WHERE clause to improve index usage.
        
        Args:
            query: SQL query to transform
            
        Returns:
            Tuple of (transformed query, whether transformation was applied)
        """
        # Pattern for function(column) = value
        func_pattern = re.compile(
            r'WHERE\s+(?:.*?AND\s+)*(\w+)\s*\(\s*(\w+(?:\.\w+)?)\s*\)\s*=\s*([\'"]?\w+[\'"]?)',
            re.IGNORECASE
        )
        
        match = func_pattern.search(query)
        if not match:
            return query, False
        
        # Extract function, column, and value
        func_name = match.group(1)
        column = match.group(2)
        value = match.group(3)
        
        # Transform to column = inverse_function(value)
        # This is just a recommendation as we don't know the inverse function
        if not "/* RECOMMENDATION:" in query:
            query = f"/* RECOMMENDATION: Move function to right side: {column} = inverse_{func_name}({value}) */\n{query}"
        
        return query, True
    
    def _transform_redundant_conditions(self, query: str) -> Tuple[str, bool]:
        """
        Transform redundant conditions in WHERE clause.
        
        Args:
            query: SQL query to transform
            
        Returns:
            Tuple of (transformed query, whether transformation was applied)
        """
        # Pattern for x = x
        self_equality_pattern = re.compile(r'(\w+(?:\.\w+)?)\s*=\s*\1', re.IGNORECASE)
        
        match = self_equality_pattern.search(query)
        if not match:
            return query, False
        
        # Replace x = x with 1 = 1
        query = self_equality_pattern.sub('1 = 1', query)
        
        # Pattern for WHERE 1 = 1 AND ...
        redundant_true_pattern = re.compile(r'WHERE\s+1\s*=\s*1\s+AND\s+', re.IGNORECASE)
        query = redundant_true_pattern.sub('WHERE ', query)
        
        return query, True
    
    def _transform_subqueries(self, query: str) -> Tuple[str, bool]:
        """
        Transform simple subqueries to JOINs when possible.
        This is a recommendation-only transformation.
        
        Args:
            query: SQL query to transform
            
        Returns:
            Tuple of (transformed query, whether transformation was applied)
        """
        # Pattern for simple IN subquery
        in_subquery_pattern = re.compile(
            r'(\w+(?:\.\w+)?)\s+IN\s+\(\s*SELECT\s+(\w+(?:\.\w+)?)\s+FROM\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?\s*(?:WHERE\s+(.*?))?\)',
            re.IGNORECASE | re.DOTALL
        )
        
        match = in_subquery_pattern.search(query)
        if not match:
            return query, False
        
        # Add a comment with recommendation
        if not "/* RECOMMENDATION:" in query:
            query = f"/* RECOMMENDATION: Consider replacing IN subquery with JOIN */\n{query}"
        
        return query, True
    
    def generate_report(self, output_file: str) -> Dict[str, Any]:
        """
        Generate a report of query transformations.
        
        Args:
            output_file: File to write the report to
            
        Returns:
            Report data
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries_transformed": len(self.transformations),
            "rules_by_applications": self._get_rule_stats(),
            "transformation_details": self.transformations
        }
        
        # Write report to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Generated query transformation report: {output_file}")
        
        # Update changelog
        self._update_changelog(f"Generated transformation report for {len(self.transformations)} queries")
        
        return report
    
    def _get_rule_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics on applied rules."""
        stats = {}
        
        for rule_name, rule_info in self.rules.items():
            stats[rule_name] = {
                "description": rule_info["description"],
                "impact": rule_info["impact"],
                "applications": rule_info["applications"]
            }
        
        return stats

# Example usage
if __name__ == "__main__":
    transformer = QueryTransformationRules()
    
    # Sample queries to transform
    sample_queries = [
        "SELECT * FROM orders, customers WHERE orders.customer_id = customers.id AND orders.total > 100",
        "SELECT * FROM products WHERE UPPER(name) = 'LAPTOP'",
        "SELECT * FROM users WHERE user_id IN (SELECT user_id FROM orders WHERE total > 1000)",
        "SELECT * FROM employees WHERE department_id = department_id"
    ]
    
    # Apply transformations
    for query in sample_queries:
        result = transformer.apply_rules(query)
        print(f"Original: {result['original_query']}")
        print(f"Transformed: {result['transformed_query']}")
        print(f"Rules applied: {[r['rule'] for r in result['rules_applied']]}\n")
    
    # Generate report
    report = transformer.generate_report("logs/query_transformation_report.json")
    print(f"Transformed {len(sample_queries)} queries")
