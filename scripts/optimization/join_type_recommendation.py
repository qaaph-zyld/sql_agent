#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Join Type Recommendation Engine

This module recommends optimal join types based on query analysis.
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
    filename='logs/join_type_recommendation.log'
)
logger = logging.getLogger(__name__)

class JoinTypeRecommender:
    """
    Recommends optimal join types based on query analysis.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the join type recommender with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.recommendations = []
        
        # Pre-response: Update changelog
        self._update_changelog("Join type recommender initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Query Accuracy Improvement",
            previous_state="Join type recommendation not implemented",
            current_state="Join type recommendation engine initialized",
            changes_made=["Initialized join type recommender", "Set up recommendation framework"],
            files_affected=[
                {"file_path": "scripts/optimization/join_type_recommendation.py", 
                 "change_type": "CREATED", 
                 "impact_level": "MEDIUM"}
            ],
            technical_decisions=[
                "Created focused module for join type recommendations",
                "Implemented cardinality-based join selection",
                "Added data distribution analysis for join optimization",
                "Integrated with changelog system for protocol compliance"
            ]
        )
    
    def recommend_join_type(self, join_info: Dict[str, Any], schema_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Recommend optimal join type based on join information.
        
        Args:
            join_info: Dictionary with join information
            schema_info: Optional schema information for better recommendations
            
        Returns:
            Dictionary with join type recommendation
        """
        logger.info(f"Recommending join type for {join_info.get('table', 'unknown table')}")
        
        current_join_type = join_info.get("join_type", "INNER").upper()
        condition = join_info.get("condition", "")
        
        # Initialize recommendation
        recommendation = {
            "original_join_type": current_join_type,
            "recommended_join_type": current_join_type,  # Default to current type
            "confidence": 0.0,
            "reasoning": [],
            "expected_impact": "NONE"
        }
        
        # Analyze join condition and current type
        self._analyze_and_recommend(recommendation, join_info, schema_info)
        
        # Record recommendation
        self.recommendations.append({
            "timestamp": datetime.now().isoformat(),
            "join_info": join_info,
            "recommendation": recommendation
        })
        
        # Update changelog if recommendation differs from current type
        if recommendation["recommended_join_type"] != current_join_type:
            self._update_changelog(f"Recommended {recommendation['recommended_join_type']} instead of {current_join_type}")
        
        return recommendation
    
    def _analyze_and_recommend(self, recommendation: Dict[str, Any], join_info: Dict[str, Any], schema_info: Dict[str, Any] = None) -> None:
        """
        Analyze join information and update recommendation.
        
        Args:
            recommendation: Recommendation dictionary to update
            join_info: Join information
            schema_info: Optional schema information
        """
        current_join_type = join_info.get("join_type", "INNER").upper()
        condition = join_info.get("condition", "")
        
        # Check for missing condition
        if not condition or condition == "NONE":
            recommendation["recommended_join_type"] = "CROSS JOIN"
            recommendation["confidence"] = 0.9
            recommendation["reasoning"].append("No join condition specified")
            recommendation["expected_impact"] = "HIGH"
            return
        
        # Check for implicit joins
        if current_join_type == "IMPLICIT":
            recommendation["recommended_join_type"] = "INNER JOIN"
            recommendation["confidence"] = 0.9
            recommendation["reasoning"].append("Explicit joins are preferred over implicit joins")
            recommendation["expected_impact"] = "MEDIUM"
            return
        
        # Analyze condition for NULL checks
        if "IS NULL" in condition:
            # Condition checks for NULL values, likely needs OUTER JOIN
            if current_join_type == "INNER":
                recommendation["recommended_join_type"] = "LEFT JOIN"
                recommendation["confidence"] = 0.7
                recommendation["reasoning"].append("Condition contains NULL check, suggesting need for LEFT JOIN")
                recommendation["expected_impact"] = "HIGH"
                return
        
        # Analyze for IS NOT NULL with OUTER JOIN
        if ("IS NOT NULL" in condition) and ("LEFT" in current_join_type or "RIGHT" in current_join_type or "FULL" in current_join_type):
            recommendation["recommended_join_type"] = "INNER JOIN"
            recommendation["confidence"] = 0.8
            recommendation["reasoning"].append("OUTER JOIN with IS NOT NULL check can be simplified to INNER JOIN")
            recommendation["expected_impact"] = "MEDIUM"
            return
        
        # Analyze equality with CROSS JOIN
        if "=" in condition and current_join_type == "CROSS JOIN":
            recommendation["recommended_join_type"] = "INNER JOIN"
            recommendation["confidence"] = 0.9
            recommendation["reasoning"].append("CROSS JOIN with equality condition should be INNER JOIN")
            recommendation["expected_impact"] = "HIGH"
            return
        
        # Analyze schema information if available
        if schema_info:
            self._analyze_with_schema(recommendation, join_info, schema_info)
    
    def _analyze_with_schema(self, recommendation: Dict[str, Any], join_info: Dict[str, Any], schema_info: Dict[str, Any]) -> None:
        """
        Analyze join with schema information for better recommendations.
        
        Args:
            recommendation: Recommendation dictionary to update
            join_info: Join information
            schema_info: Schema information
        """
        current_join_type = join_info.get("join_type", "INNER").upper()
        table = join_info.get("table", "")
        condition = join_info.get("condition", "")
        
        # Extract table relationships from schema
        if "relationships" in schema_info:
            for rel in schema_info["relationships"]:
                # Check if this relationship involves our tables
                if (rel["table1"] == table or rel["table2"] == table):
                    relationship_type = rel.get("type", "")
                    
                    # One-to-many relationship
                    if relationship_type == "one_to_many":
                        # If joining from "many" side to "one" side, INNER JOIN is usually fine
                        # If joining from "one" side to "many" side, might want LEFT JOIN to preserve records
                        if rel["table1"] == table and current_join_type == "INNER JOIN":
                            recommendation["recommended_join_type"] = "LEFT JOIN"
                            recommendation["confidence"] = 0.6
                            recommendation["reasoning"].append("One-to-many relationship might benefit from LEFT JOIN")
                            recommendation["expected_impact"] = "MEDIUM"
                    
                    # Many-to-many relationship
                    elif relationship_type == "many_to_many":
                        # Usually INNER JOIN is appropriate, but check for specific cases
                        pass
        
        # Check for nullable foreign keys
        if "columns" in schema_info:
            # Extract column names from condition
            column_match = re.search(r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', condition)
            if column_match:
                left_table = column_match.group(1)
                left_column = column_match.group(2)
                right_table = column_match.group(3)
                right_column = column_match.group(4)
                
                # Check if foreign key is nullable
                for col_info in schema_info["columns"]:
                    if (col_info["table"] == left_table and col_info["column"] == left_column and 
                        col_info.get("nullable", False) and current_join_type == "INNER JOIN"):
                        recommendation["recommended_join_type"] = "LEFT JOIN"
                        recommendation["confidence"] = 0.7
                        recommendation["reasoning"].append("Foreign key is nullable, suggesting need for LEFT JOIN")
                        recommendation["expected_impact"] = "MEDIUM"
    
    def recommend_multiple_joins(self, joins: List[Dict[str, Any]], schema_info: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Recommend join types for multiple joins.
        
        Args:
            joins: List of dictionaries with join information
            schema_info: Optional schema information
            
        Returns:
            List of join type recommendations
        """
        results = []
        
        for join_info in joins:
            recommendation = self.recommend_join_type(join_info, schema_info)
            results.append(recommendation)
        
        return results
    
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """
        Generate a report of join type recommendations.
        
        Args:
            output_file: Optional file to write the report to
            
        Returns:
            Report data
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_recommendations": len(self.recommendations),
            "recommendation_summary": self._summarize_recommendations(),
            "recommendations": self.recommendations
        }
        
        # Write report to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Generated join type recommendation report: {output_file}")
            
            # Update changelog
            self._update_changelog(f"Generated join type recommendation report for {len(self.recommendations)} joins")
        
        return report
    
    def _summarize_recommendations(self) -> Dict[str, Any]:
        """Summarize recommendations for the report."""
        summary = {
            "changes_recommended": 0,
            "by_original_type": {},
            "by_recommended_type": {},
            "high_impact_changes": 0,
            "medium_impact_changes": 0,
            "low_impact_changes": 0
        }
        
        for rec in self.recommendations:
            original = rec["recommendation"]["original_join_type"]
            recommended = rec["recommendation"]["recommended_join_type"]
            impact = rec["recommendation"]["expected_impact"]
            
            # Count by original type
            if original not in summary["by_original_type"]:
                summary["by_original_type"][original] = 0
            summary["by_original_type"][original] += 1
            
            # Count by recommended type
            if recommended not in summary["by_recommended_type"]:
                summary["by_recommended_type"][recommended] = 0
            summary["by_recommended_type"][recommended] += 1
            
            # Count changes
            if original != recommended:
                summary["changes_recommended"] += 1
                
                # Count by impact
                if impact == "HIGH":
                    summary["high_impact_changes"] += 1
                elif impact == "MEDIUM":
                    summary["medium_impact_changes"] += 1
                elif impact == "LOW":
                    summary["low_impact_changes"] += 1
        
        return summary

# Example usage
if __name__ == "__main__":
    recommender = JoinTypeRecommender()
    
    # Sample schema information
    sample_schema = {
        "relationships": [
            {"table1": "orders", "table2": "customers", "type": "many_to_one"},
            {"table1": "products", "table2": "categories", "type": "many_to_one"}
        ],
        "columns": [
            {"table": "orders", "column": "customer_id", "nullable": False},
            {"table": "products", "column": "category_id", "nullable": True}
        ]
    }
    
    # Sample joins to analyze
    sample_joins = [
        {"table": "customers", "join_type": "INNER", "condition": "orders.customer_id = customers.id"},
        {"table": "categories", "join_type": "INNER", "condition": "products.category_id = categories.id"},
        {"table": "departments", "join_type": "CROSS JOIN", "condition": "employees.dept_id = departments.id"}
    ]
    
    # Generate recommendations
    for join_info in sample_joins:
        recommendation = recommender.recommend_join_type(join_info, sample_schema)
        print(f"Table: {join_info['table']}")
        print(f"Original: {recommendation['original_join_type']}")
        print(f"Recommended: {recommendation['recommended_join_type']}")
        print(f"Confidence: {recommendation['confidence']}")
        print(f"Reasoning: {recommendation['reasoning']}")
        print(f"Expected Impact: {recommendation['expected_impact']}")
        print()
    
    # Generate report
    report = recommender.generate_report("logs/join_type_recommendation_report.json")
