#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bottleneck Detector Module

This module identifies performance bottlenecks in the SQL Agent system
based on collected metrics. It follows the mandatory changelog protocol.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/bottleneck_detector.log'
)
logger = logging.getLogger(__name__)

class BottleneckDetector:
    """
    Main class for detecting performance bottlenecks.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the bottleneck detector with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.bottlenecks = []
        
        # Pre-response: Update changelog
        self._update_changelog("Bottleneck detector initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Performance Analysis",
            previous_state="Bottleneck detection not started",
            current_state="Bottleneck detection active",
            changes_made=["Initialized bottleneck detector", "Set up detection rules"],
            files_affected=[
                {"file_path": "scripts/optimization/bottleneck_detector.py", 
                 "change_type": "CREATED", 
                 "impact_level": "MEDIUM"}
            ],
            technical_decisions=[
                "Implemented threshold-based bottleneck detection",
                "Added severity classification for bottlenecks",
                "Integrated with changelog system for protocol compliance"
            ]
        )
        
    def analyze_metrics(self, metrics_file: str, threshold_ms: float = 100.0) -> List[Dict[str, Any]]:
        """
        Analyze performance metrics and identify bottlenecks.
        
        Args:
            metrics_file: Path to the metrics file
            threshold_ms: Threshold in milliseconds to consider as a bottleneck
            
        Returns:
            List of identified bottlenecks
        """
        logger.info(f"Analyzing metrics from {metrics_file}")
        
        try:
            with open(metrics_file, 'r') as f:
                metrics_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading metrics file: {str(e)}")
            return []
            
        bottlenecks = []
        
        # Analyze each metric
        for metric_name, metric_data in metrics_data.get("metrics", {}).items():
            stats = metric_data.get("statistics", {})
            
            # Check if this is a bottleneck (avg > threshold or p95 > threshold*1.5)
            if stats.get("avg", 0) > threshold_ms or stats.get("p95", 0) > threshold_ms * 1.5:
                severity = "HIGH" if stats.get("avg", 0) > threshold_ms * 2 else "MEDIUM"
                
                bottleneck = {
                    "metric": metric_name,
                    "description": metric_data.get("description", ""),
                    "statistics": stats,
                    "severity": severity,
                    "timestamp": datetime.now().isoformat()
                }
                
                bottlenecks.append(bottleneck)
                logger.warning(f"Bottleneck identified: {metric_name} - {severity}")
                
        self.bottlenecks.extend(bottlenecks)
        
        # Update changelog with findings
        if bottlenecks:
            self._update_changelog(
                f"Identified {len(bottlenecks)} performance bottlenecks"
            )
            
        return bottlenecks
        
    def suggest_improvements(self, bottleneck: Dict[str, Any]) -> List[str]:
        """
        Suggest improvements for a specific bottleneck.
        
        Args:
            bottleneck: Bottleneck information
            
        Returns:
            List of suggested improvements
        """
        metric = bottleneck.get("metric", "")
        suggestions = []
        
        # Common improvement suggestions based on metric name patterns
        if "query" in metric.lower():
            suggestions.extend([
                "Optimize SQL query structure",
                "Ensure proper indexing on frequently queried columns",
                "Consider query caching for repetitive queries"
            ])
            
        if "database" in metric.lower() or "db" in metric.lower():
            suggestions.extend([
                "Implement connection pooling",
                "Optimize transaction management",
                "Consider read/write splitting for heavy load"
            ])
            
        if "parse" in metric.lower() or "process" in metric.lower():
            suggestions.extend([
                "Implement more efficient algorithms",
                "Consider parallel processing for large datasets",
                "Optimize memory usage during processing"
            ])
            
        if "render" in metric.lower() or "format" in metric.lower():
            suggestions.extend([
                "Implement lazy loading for large result sets",
                "Optimize JSON serialization",
                "Consider streaming responses for large datasets"
            ])
            
        # Generic suggestions for any bottleneck
        suggestions.extend([
            "Profile the code to identify specific slow sections",
            "Optimize algorithms and data structures",
            "Consider caching frequently accessed data"
        ])
        
        return suggestions
        
    def generate_report(self, output_file: str) -> Dict[str, Any]:
        """
        Generate a report of identified bottlenecks with improvement suggestions.
        
        Args:
            output_file: File to write the report to
            
        Returns:
            Report data
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "bottlenecks": []
        }
        
        for bottleneck in self.bottlenecks:
            suggestions = self.suggest_improvements(bottleneck)
            
            report["bottlenecks"].append({
                "metric": bottleneck["metric"],
                "description": bottleneck["description"],
                "statistics": bottleneck["statistics"],
                "severity": bottleneck["severity"],
                "suggestions": suggestions
            })
            
        report["summary"] = {
            "total_bottlenecks": len(self.bottlenecks),
            "high_severity_bottlenecks": sum(1 for b in self.bottlenecks if b["severity"] == "HIGH"),
            "medium_severity_bottlenecks": sum(1 for b in self.bottlenecks if b["severity"] == "MEDIUM")
        }
        
        # Write report to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Generated bottleneck report: {output_file}")
        
        return report

# Example usage
if __name__ == "__main__":
    detector = BottleneckDetector()
    
    # Create a sample metrics file for demonstration
    sample_metrics = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "query_parsing": {
                "description": "Time to parse natural language into query structure",
                "statistics": {
                    "min": 50.2,
                    "max": 320.5,
                    "avg": 120.3,
                    "median": 115.8,
                    "p95": 250.1,
                    "count": 100
                }
            },
            "database_execution": {
                "description": "Time to execute SQL on database",
                "statistics": {
                    "min": 100.3,
                    "max": 1500.8,
                    "avg": 350.2,
                    "median": 320.5,
                    "p95": 950.3,
                    "count": 100
                }
            }
        }
    }
    
    metrics_file = "logs/sample_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(sample_metrics, f, indent=2)
    
    # Analyze metrics and identify bottlenecks
    bottlenecks = detector.analyze_metrics(metrics_file)
    
    # Generate report
    report = detector.generate_report("logs/bottleneck_report.json")
    print(f"Found {len(bottlenecks)} bottlenecks")
