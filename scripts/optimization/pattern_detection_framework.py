#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pattern Detection Framework

This module provides the core framework for detecting patterns in SQL queries.
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
    filename='logs/pattern_detection.log'
)
logger = logging.getLogger(__name__)

class PatternDetector:
    """
    Main class for detecting patterns in SQL queries.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the pattern detector with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.patterns = {}
        
        # Pre-response: Update changelog
        self._update_changelog("Pattern detector initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Query Accuracy Improvement",
            previous_state="Pattern detection not started",
            current_state="Pattern detection framework initialized",
            changes_made=["Created pattern detection framework", "Set up pattern registry"],
            files_affected=[
                {"file_path": "scripts/optimization/pattern_detection_framework.py", 
                 "change_type": "CREATED", 
                 "impact_level": "MEDIUM"}
            ],
            technical_decisions=[
                "Implemented modular pattern detection system",
                "Used regex-based pattern matching for flexibility",
                "Created pattern registry for extensibility",
                "Integrated with changelog system for protocol compliance"
            ]
        )
    
    def register_pattern(self, pattern_name: str, pattern_regex: str, description: str, impact: str = "MEDIUM") -> None:
        """
        Register a new SQL pattern to detect.
        
        Args:
            pattern_name: Unique name for the pattern
            pattern_regex: Regular expression to match the pattern
            description: Description of the pattern
            impact: Impact level (HIGH, MEDIUM, LOW)
        """
        logger.info(f"Registering pattern: {pattern_name}")
        
        self.patterns[pattern_name] = {
            "regex": pattern_regex,
            "description": description,
            "impact": impact,
            "matches": 0
        }
        
        # Update changelog
        self._update_changelog(f"Registered pattern: {pattern_name}")
    
    def detect_patterns(self, query: str) -> Dict[str, Any]:
        """
        Detect registered patterns in a SQL query.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            Dictionary with detected patterns
        """
        logger.info(f"Detecting patterns in query: {query[:50]}...")
        
        detected = {}
        
        for pattern_name, pattern_info in self.patterns.items():
            pattern_regex = pattern_info["regex"]
            matches = re.findall(pattern_regex, query, re.IGNORECASE)
            
            if matches:
                self.patterns[pattern_name]["matches"] += len(matches)
                detected[pattern_name] = {
                    "count": len(matches),
                    "matches": matches[:5],  # Limit to first 5 matches
                    "description": pattern_info["description"],
                    "impact": pattern_info["impact"]
                }
        
        return detected
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for all registered patterns.
        
        Returns:
            Dictionary with pattern statistics
        """
        stats = {}
        
        for pattern_name, pattern_info in self.patterns.items():
            stats[pattern_name] = {
                "description": pattern_info["description"],
                "impact": pattern_info["impact"],
                "matches": pattern_info["matches"]
            }
        
        return stats
    
    def generate_report(self, output_file: str) -> Dict[str, Any]:
        """
        Generate a report of pattern detection statistics.
        
        Args:
            output_file: File to write the report to
            
        Returns:
            Report data
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "patterns_registered": len(self.patterns),
            "pattern_statistics": self.get_pattern_statistics()
        }
        
        # Write report to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Generated pattern detection report: {output_file}")
        
        # Update changelog
        self._update_changelog(f"Generated pattern detection report")
        
        return report

# Register common SQL patterns
def register_common_patterns(detector: PatternDetector) -> None:
    """Register common SQL patterns to detect."""
    
    # SELECT * pattern
    detector.register_pattern(
        pattern_name="select_all",
        pattern_regex=r"SELECT\s+\*\s+FROM",
        description="Using SELECT * instead of specific columns",
        impact="HIGH"
    )
    
    # LIKE with leading wildcard
    detector.register_pattern(
        pattern_name="like_leading_wildcard",
        pattern_regex=r"LIKE\s+['\"]%",
        description="LIKE with leading wildcard prevents index usage",
        impact="HIGH"
    )
    
    # Function in WHERE clause
    detector.register_pattern(
        pattern_name="function_in_where",
        pattern_regex=r"WHERE\s+\w+\([^)]*\)",
        description="Function in WHERE clause prevents index usage",
        impact="MEDIUM"
    )
    
    # Implicit joins
    detector.register_pattern(
        pattern_name="implicit_join",
        pattern_regex=r"FROM\s+\w+\s*,\s*\w+\s+WHERE",
        description="Implicit join syntax instead of explicit JOIN",
        impact="MEDIUM"
    )
    
    # Missing WHERE clause
    detector.register_pattern(
        pattern_name="missing_where",
        pattern_regex=r"FROM\s+\w+(?!\s+WHERE|\s+JOIN)",
        description="Query without WHERE clause may return too many rows",
        impact="HIGH"
    )

# Example usage
if __name__ == "__main__":
    detector = PatternDetector()
    
    # Register common patterns
    register_common_patterns(detector)
    
    # Sample queries to analyze
    sample_queries = [
        "SELECT * FROM customers WHERE last_name LIKE '%smith%'",
        "SELECT * FROM orders, customers WHERE orders.customer_id = customers.id",
        "SELECT * FROM transactions WHERE UPPER(status) = 'COMPLETED'",
        "SELECT id, name FROM users"
    ]
    
    # Detect patterns
    for query in sample_queries:
        patterns = detector.detect_patterns(query)
        print(f"Query: {query[:30]}...")
        print(f"Detected patterns: {list(patterns.keys())}")
    
    # Generate report
    report = detector.generate_report("logs/pattern_detection_report.json")
    print(f"Registered {len(detector.patterns)} patterns")
