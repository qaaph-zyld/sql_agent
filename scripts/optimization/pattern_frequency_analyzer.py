#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pattern Frequency Analyzer

This module analyzes the frequency of SQL patterns and provides insights.
It follows the mandatory changelog protocol.
"""

import logging
import json
from typing import Dict, List, Any
from datetime import datetime
from collections import Counter

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine
from scripts.optimization.pattern_detection_framework import PatternDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/pattern_frequency.log'
)
logger = logging.getLogger(__name__)

class PatternFrequencyAnalyzer:
    """
    Main class for analyzing SQL pattern frequencies.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self, pattern_detector: PatternDetector = None):
        """
        Initialize the pattern frequency analyzer with changelog integration.
        
        Args:
            pattern_detector: Optional PatternDetector instance to use
        """
        self.changelog_engine = ChangelogEngine()
        self.pattern_detector = pattern_detector or PatternDetector()
        self.query_history = []
        self.pattern_frequencies = Counter()
        self.query_pattern_map = {}  # Maps query hashes to patterns
        
        # Pre-response: Update changelog
        self._update_changelog("Pattern frequency analyzer initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Query Accuracy Improvement",
            previous_state="Pattern frequency analysis not started",
            current_state="Pattern frequency analysis in progress",
            changes_made=["Initialized pattern frequency analyzer", "Set up frequency tracking"],
            files_affected=[
                {"file_path": "scripts/optimization/pattern_frequency_analyzer.py", 
                 "change_type": "CREATED", 
                 "impact_level": "MEDIUM"}
            ],
            technical_decisions=[
                "Implemented frequency-based pattern analysis",
                "Added historical trend tracking",
                "Created pattern impact assessment",
                "Integrated with changelog system for protocol compliance"
            ]
        )
    
    def analyze_query(self, query: str, query_id: str = None) -> Dict[str, Any]:
        """
        Analyze a SQL query for pattern frequencies.
        
        Args:
            query: SQL query to analyze
            query_id: Optional identifier for the query
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing pattern frequency in query: {query[:50]}...")
        
        # Generate query ID if not provided
        if not query_id:
            import hashlib
            query_id = hashlib.md5(query.encode()).hexdigest()
        
        # Detect patterns
        detected_patterns = self.pattern_detector.detect_patterns(query)
        
        # Update pattern frequencies
        for pattern_name in detected_patterns:
            self.pattern_frequencies[pattern_name] += 1
        
        # Store query and patterns
        query_entry = {
            "query_id": query_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "patterns": list(detected_patterns.keys())
        }
        
        self.query_history.append(query_entry)
        self.query_pattern_map[query_id] = detected_patterns
        
        return {
            "query_id": query_id,
            "patterns_detected": detected_patterns,
            "pattern_counts": dict(self.pattern_frequencies)
        }
    
    def analyze_query_batch(self, queries: List[str]) -> Dict[str, Any]:
        """
        Analyze a batch of SQL queries for pattern frequencies.
        
        Args:
            queries: List of SQL queries to analyze
            
        Returns:
            Dictionary with aggregated analysis results
        """
        logger.info(f"Analyzing pattern frequency in batch of {len(queries)} queries")
        
        results = []
        for query in queries:
            result = self.analyze_query(query)
            results.append(result)
        
        # Update changelog
        self._update_changelog(f"Analyzed pattern frequency in batch of {len(queries)} queries")
        
        return {
            "batch_size": len(queries),
            "results": results,
            "pattern_frequencies": dict(self.pattern_frequencies)
        }
    
    def get_most_frequent_patterns(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most frequent patterns.
        
        Args:
            limit: Maximum number of patterns to return
            
        Returns:
            List of most frequent patterns with counts
        """
        most_common = self.pattern_frequencies.most_common(limit)
        
        result = []
        for pattern_name, count in most_common:
            pattern_info = self.pattern_detector.patterns.get(pattern_name, {})
            result.append({
                "pattern": pattern_name,
                "count": count,
                "description": pattern_info.get("description", ""),
                "impact": pattern_info.get("impact", "MEDIUM")
            })
        
        return result
    
    def get_high_impact_patterns(self) -> List[Dict[str, Any]]:
        """
        Get patterns with high impact.
        
        Returns:
            List of high impact patterns with counts
        """
        high_impact = []
        
        for pattern_name, count in self.pattern_frequencies.items():
            pattern_info = self.pattern_detector.patterns.get(pattern_name, {})
            if pattern_info.get("impact") == "HIGH":
                high_impact.append({
                    "pattern": pattern_name,
                    "count": count,
                    "description": pattern_info.get("description", ""),
                    "impact": "HIGH"
                })
        
        # Sort by frequency (highest first)
        high_impact.sort(key=lambda x: x["count"], reverse=True)
        
        return high_impact
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on pattern frequencies.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Get high impact patterns
        high_impact = self.get_high_impact_patterns()
        
        # Generate recommendations for high impact patterns
        for pattern in high_impact:
            if pattern["pattern"] == "select_all":
                recommendations.append({
                    "pattern": "select_all",
                    "frequency": pattern["count"],
                    "recommendation": "Replace SELECT * with specific columns",
                    "priority": "HIGH",
                    "benefit": "Reduces data transfer and improves performance"
                })
            
            elif pattern["pattern"] == "like_leading_wildcard":
                recommendations.append({
                    "pattern": "like_leading_wildcard",
                    "frequency": pattern["count"],
                    "recommendation": "Avoid LIKE '%value' patterns, use full-text search instead",
                    "priority": "HIGH",
                    "benefit": "Allows index usage and improves query performance"
                })
            
            elif pattern["pattern"] == "missing_where":
                recommendations.append({
                    "pattern": "missing_where",
                    "frequency": pattern["count"],
                    "recommendation": "Add WHERE clauses to filter results",
                    "priority": "HIGH",
                    "benefit": "Reduces data transfer and processing time"
                })
        
        # Get medium impact patterns
        for pattern_name, count in self.pattern_frequencies.items():
            pattern_info = self.pattern_detector.patterns.get(pattern_name, {})
            if pattern_info.get("impact") == "MEDIUM":
                if pattern_name == "function_in_where":
                    recommendations.append({
                        "pattern": "function_in_where",
                        "frequency": count,
                        "recommendation": "Move functions to right side of comparison",
                        "priority": "MEDIUM",
                        "benefit": "Allows index usage on columns"
                    })
                
                elif pattern_name == "implicit_join":
                    recommendations.append({
                        "pattern": "implicit_join",
                        "frequency": count,
                        "recommendation": "Use explicit JOIN syntax instead of comma-separated tables",
                        "priority": "MEDIUM",
                        "benefit": "Improves query readability and maintainability"
                    })
        
        return recommendations
    
    def generate_report(self, output_file: str) -> Dict[str, Any]:
        """
        Generate a report of pattern frequency analysis.
        
        Args:
            output_file: File to write the report to
            
        Returns:
            Report data
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "queries_analyzed": len(self.query_history),
            "pattern_frequencies": dict(self.pattern_frequencies),
            "most_frequent_patterns": self.get_most_frequent_patterns(),
            "high_impact_patterns": self.get_high_impact_patterns(),
            "recommendations": self.generate_recommendations()
        }
        
        # Write report to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Generated pattern frequency analysis report: {output_file}")
        
        # Update changelog
        self._update_changelog(f"Generated pattern frequency analysis report")
        
        return report

# Example usage
if __name__ == "__main__":
    from scripts.optimization.pattern_detection_framework import PatternDetector, register_common_patterns
    
    # Initialize pattern detector and register common patterns
    detector = PatternDetector()
    register_common_patterns(detector)
    
    # Initialize frequency analyzer
    analyzer = PatternFrequencyAnalyzer(detector)
    
    # Sample queries to analyze
    sample_queries = [
        "SELECT * FROM customers WHERE last_name LIKE '%smith%'",
        "SELECT * FROM orders, customers WHERE orders.customer_id = customers.id",
        "SELECT * FROM transactions WHERE UPPER(status) = 'COMPLETED'",
        "SELECT id, name FROM users",
        "SELECT * FROM products",
        "SELECT * FROM customers WHERE last_name LIKE '%jones%'"
    ]
    
    # Analyze queries
    analyzer.analyze_query_batch(sample_queries)
    
    # Generate report
    report = analyzer.generate_report("logs/pattern_frequency_report.json")
    print(f"Analyzed {len(sample_queries)} queries and found {len(analyzer.pattern_frequencies)} pattern types")
