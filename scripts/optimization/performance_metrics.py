#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Performance Metrics Module

This module provides tools for collecting and analyzing performance metrics
in the SQL Agent system. It follows the mandatory changelog protocol.
"""

import time
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
    filename='logs/performance_metrics.log'
)
logger = logging.getLogger(__name__)

class PerformanceMetric:
    """Class for tracking a single performance metric."""
    
    def __init__(self, name: str, description: str = ""):
        """Initialize a performance metric."""
        self.name = name
        self.description = description
        self.values = []
        self.start_time = None
        
    def start(self) -> None:
        """Start timing the metric."""
        self.start_time = time.time()
        
    def stop(self) -> float:
        """Stop timing and record the duration."""
        if self.start_time is None:
            raise ValueError("Metric timing was not started")
        
        duration_ms = (time.time() - self.start_time) * 1000
        self.values.append(duration_ms)
        self.start_time = None
        return duration_ms
        
    def get_statistics(self) -> Dict[str, float]:
        """Calculate statistics for the recorded values."""
        if not self.values:
            return {
                "min": 0, "max": 0, "avg": 0, 
                "median": 0, "p95": 0, "count": 0
            }
            
        sorted_values = sorted(self.values)
        n = len(sorted_values)
        
        return {
            "min": min(self.values),
            "max": max(self.values),
            "avg": sum(self.values) / n,
            "median": sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2,
            "p95": sorted_values[int(n * 0.95)] if n > 20 else max(self.values),
            "count": n
        }

class PerformanceTracker:
    """
    Main class for tracking performance metrics.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the performance tracker with changelog integration."""
        self.metrics = {}
        self.changelog_engine = ChangelogEngine()
        
        # Pre-response: Update changelog
        self._update_changelog("Performance tracker initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Performance Analysis",
            previous_state="Performance tracking not started",
            current_state="Performance tracking active",
            changes_made=["Initialized performance tracker", "Set up metrics collection"],
            files_affected=[
                {"file_path": "scripts/optimization/performance_metrics.py", 
                 "change_type": "CREATED", 
                 "impact_level": "MEDIUM"}
            ],
            technical_decisions=[
                "Implemented statistical analysis for performance metrics",
                "Integrated with changelog system for protocol compliance"
            ]
        )
        
    def create_metric(self, name: str, description: str = "") -> PerformanceMetric:
        """Create a new performance metric."""
        metric = PerformanceMetric(name, description)
        self.metrics[name] = metric
        return metric
        
    def get_metric(self, name: str) -> Optional[PerformanceMetric]:
        """Get a performance metric by name."""
        return self.metrics.get(name)
        
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """Generate a performance report from collected metrics."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        for name, metric in self.metrics.items():
            report["metrics"][name] = {
                "description": metric.description,
                "statistics": metric.get_statistics()
            }
            
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
                
        return report

# Example usage
if __name__ == "__main__":
    tracker = PerformanceTracker()
    
    # Create some metrics
    query_metric = tracker.create_metric("query_generation", "Time to generate SQL query")
    response_metric = tracker.create_metric("response_formatting", "Time to format query response")
    
    # Simulate some measurements
    for i in range(10):
        query_metric.start()
        time.sleep(0.05)  # Simulate work
        query_metric.stop()
        
        response_metric.start()
        time.sleep(0.03)  # Simulate work
        response_metric.stop()
        
    # Generate report
    report = tracker.generate_report("logs/performance_report.json")
    print(json.dumps(report, indent=2))
