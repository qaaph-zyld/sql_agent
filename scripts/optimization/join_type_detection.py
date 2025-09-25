#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Join Type Detection Module

This module detects SQL join types in queries.
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
    filename='logs/join_type_detection.log'
)
logger = logging.getLogger(__name__)

class JoinTypeDetector:
    """
    Detects SQL join types in queries.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the join type detector with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.detected_joins = []
        
        # Pre-response: Update changelog
        self._update_changelog("Join type detector initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Query Accuracy Improvement",
            previous_state="Join type detection not implemented",
            current_state="Join type detection module initialized",
            changes_made=["Initialized join type detector", "Set up detection framework"],
            files_affected=[
                {"file_path": "scripts/optimization/join_type_detection.py", 
                 "change_type": "CREATED", 
                 "impact_level": "MEDIUM"}
            ],
            technical_decisions=[
                "Created focused module for join detection only",
                "Used regex-based pattern matching",
                "Implemented explicit and implicit join detection",
                "Integrated with changelog system for protocol compliance"
            ]
        )
    
    def detect_joins(self, query: str) -> List[Dict[str, Any]]:
        """
        Detect joins in a SQL query.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            List of dictionaries with join information
        """
        logger.info(f"Detecting joins in query: {query[:50]}...")
        
        joins = []
        
        # Extract explicit joins (JOIN keyword)
        explicit_joins = self._extract_explicit_joins(query)
        joins.extend(explicit_joins)
        
        # Extract implicit joins (comma-separated tables)
        implicit_joins = self._extract_implicit_joins(query)
        joins.extend(implicit_joins)
        
        # Record detection
        detection_record = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "joins_detected": len(joins)
        }
        
        self.detected_joins.append(detection_record)
        
        # Update changelog if joins were found
        if joins:
            self._update_changelog(f"Detected {len(joins)} joins in query")
        
        return joins
    
    def _extract_explicit_joins(self, query: str) -> List[Dict[str, Any]]:
        """
        Extract explicit joins from a SQL query.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            List of dictionaries with explicit join information
        """
        joins = []
        
        # Pattern for explicit joins
        join_pattern = re.compile(
            r'(INNER|LEFT|RIGHT|FULL|CROSS|OUTER)?\s*JOIN\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?\s+ON\s+(.+?)(?=(?:INNER|LEFT|RIGHT|FULL|CROSS|OUTER)?\s*JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$)',
            re.IGNORECASE | re.DOTALL
        )
        
        for match in join_pattern.finditer(query):
            join_type = match.group(1).upper() if match.group(1) else "INNER"
            table_name = match.group(2)
            table_alias = match.group(3) if match.group(3) else table_name
            join_condition = match.group(4).strip()
            
            joins.append({
                "join_type": join_type,
                "table": table_name,
                "alias": table_alias,
                "condition": join_condition,
                "is_explicit": True
            })
        
        return joins
    
    def _extract_implicit_joins(self, query: str) -> List[Dict[str, Any]]:
        """
        Extract implicit joins from a SQL query.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            List of dictionaries with implicit join information
        """
        joins = []
        
        # Extract FROM clause
        from_clause = re.search(r'FROM\s+(.*?)(?=\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if not from_clause:
            return joins
        
        tables_text = from_clause.group(1)
        
        # Check for comma-separated tables
        if ',' not in tables_text:
            return joins
        
        # Parse tables and aliases
        tables = []
        for table_item in tables_text.split(','):
            table_item = table_item.strip()
            
            # Extract table name and alias
            table_parts = table_item.split()
            table_name = table_parts[0]
            
            if len(table_parts) > 1 and table_parts[1].upper() == 'AS' and len(table_parts) > 2:
                table_alias = table_parts[2]
            elif len(table_parts) > 1:
                table_alias = table_parts[1]
            else:
                table_alias = table_name
            
            tables.append({
                "name": table_name,
                "alias": table_alias
            })
        
        # Need at least two tables for a join
        if len(tables) < 2:
            return joins
        
        # Look for join conditions in WHERE clause
        where_clause = re.search(r'WHERE\s+(.*?)(?=\s+GROUP|\s+ORDER|\s+LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if not where_clause:
            # Implicit join without conditions
            for i in range(1, len(tables)):
                joins.append({
                    "join_type": "IMPLICIT",
                    "table": tables[i]["name"],
                    "alias": tables[i]["alias"],
                    "condition": "NONE",
                    "is_explicit": False,
                    "left_table": tables[0]["name"],
                    "left_alias": tables[0]["alias"]
                })
            return joins
        
        where_conditions = where_clause.group(1).split('AND')
        
        # Find equality conditions between tables
        for condition in where_conditions:
            condition = condition.strip()
            
            # Look for table1.col = table2.col pattern
            equality_match = re.search(r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', condition)
            if not equality_match:
                continue
                
            left_table_alias = equality_match.group(1)
            left_column = equality_match.group(2)
            right_table_alias = equality_match.group(3)
            right_column = equality_match.group(4)
            
            # Find the tables in our list
            left_table_info = next((t for t in tables if t["alias"] == left_table_alias), None)
            right_table_info = next((t for t in tables if t["alias"] == right_table_alias), None)
            
            if left_table_info and right_table_info:
                joins.append({
                    "join_type": "IMPLICIT",
                    "table": right_table_info["name"],
                    "alias": right_table_info["alias"],
                    "condition": condition,
                    "is_explicit": False,
                    "left_table": left_table_info["name"],
                    "left_alias": left_table_info["alias"]
                })
        
        return joins
    
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """
        Generate a report of detected joins.
        
        Args:
            output_file: Optional file to write the report to
            
        Returns:
            Report data
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries_analyzed": len(self.detected_joins),
            "detection_summary": self._get_detection_stats()
        }
        
        # Write report to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Generated join detection report: {output_file}")
            
            # Update changelog
            self._update_changelog(f"Generated join detection report for {len(self.detected_joins)} queries")
        
        return report
    
    def _get_detection_stats(self) -> Dict[str, Any]:
        """Get statistics on detected joins."""
        stats = {
            "explicit_joins": 0,
            "implicit_joins": 0,
            "join_types": {}
        }
        
        for detection in self.detected_joins:
            for join in detection.get("joins", []):
                if join.get("is_explicit", False):
                    stats["explicit_joins"] += 1
                    
                    # Count join types
                    join_type = join.get("join_type", "UNKNOWN")
                    if join_type not in stats["join_types"]:
                        stats["join_types"][join_type] = 0
                    stats["join_types"][join_type] += 1
                else:
                    stats["implicit_joins"] += 1
        
        return stats

# Example usage
if __name__ == "__main__":
    detector = JoinTypeDetector()
    
    # Sample queries to analyze
    sample_queries = [
        "SELECT * FROM orders INNER JOIN customers ON orders.customer_id = customers.id",
        "SELECT * FROM products, categories WHERE products.category_id = categories.id",
        "SELECT * FROM employees LEFT JOIN departments ON employees.dept_id = departments.id"
    ]
    
    # Detect joins
    for query in sample_queries:
        joins = detector.detect_joins(query)
        print(f"Query: {query}")
        print(f"Joins detected: {len(joins)}")
        for join in joins:
            print(f"  Type: {join['join_type']}, Table: {join['table']}")
        print()
    
    # Generate report
    report = detector.generate_report("logs/join_detection_report.json")
