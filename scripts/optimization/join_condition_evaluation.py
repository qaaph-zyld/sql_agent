#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Join Condition Evaluation

This module evaluates SQL join conditions for optimization opportunities.
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
    filename='logs/join_condition_evaluation.log'
)
logger = logging.getLogger(__name__)

class JoinConditionEvaluator:
    """
    Evaluates SQL join conditions for optimization opportunities.
    Implements the mandatory changelog protocol.
    """
    
    def __init__(self):
        """Initialize the join condition evaluator with changelog integration."""
        self.changelog_engine = ChangelogEngine()
        self.evaluations = []
        
        # Pre-response: Update changelog
        self._update_changelog("Join condition evaluator initialization")
        
    def _update_changelog(self, action_summary: str) -> None:
        """Update the changelog following the mandatory protocol."""
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type="Query Accuracy Improvement",
            previous_state="Join condition evaluation not implemented",
            current_state="Join condition evaluation module initialized",
            changes_made=["Initialized join condition evaluator", "Set up evaluation framework"],
            files_affected=[
                {"file_path": "scripts/optimization/join_condition_evaluation.py", 
                 "change_type": "CREATED", 
                 "impact_level": "MEDIUM"}
            ],
            technical_decisions=[
                "Created focused module for join condition evaluation",
                "Implemented condition quality assessment",
                "Added issue detection for common join problems",
                "Integrated with changelog system for protocol compliance"
            ]
        )
    
    def evaluate_condition(self, condition: str, join_type: str = None) -> Dict[str, Any]:
        """
        Evaluate a join condition for optimization opportunities.
        
        Args:
            condition: Join condition string
            join_type: Optional join type for context
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info(f"Evaluating join condition: {condition}")
        
        # Basic evaluation
        evaluation = {
            "condition": condition,
            "join_type": join_type,
            "quality_score": 0,
            "issues": [],
            "recommendations": []
        }
        
        # Evaluate condition quality
        quality_score, issues, recommendations = self._evaluate_quality(condition, join_type)
        
        evaluation["quality_score"] = quality_score
        evaluation["issues"] = issues
        evaluation["recommendations"] = recommendations
        
        # Record evaluation
        self.evaluations.append(evaluation)
        
        # Update changelog
        self._update_changelog(f"Evaluated join condition with quality score {quality_score}")
        
        return evaluation
    
    def _evaluate_quality(self, condition: str, join_type: str = None) -> tuple:
        """
        Evaluate the quality of a join condition.
        
        Args:
            condition: Join condition string
            join_type: Optional join type for context
            
        Returns:
            Tuple of (quality score, issues, recommendations)
        """
        quality_score = 10  # Start with perfect score
        issues = []
        recommendations = []
        
        # Check for empty or missing condition
        if not condition or condition == "NONE":
            quality_score = 0
            issues.append("Missing join condition")
            recommendations.append("Add explicit join condition")
            return quality_score, issues, recommendations
        
        # Check for equality condition (preferred)
        if not re.search(r'=', condition):
            quality_score -= 3
            issues.append("Non-equality join condition")
            recommendations.append("Consider using equality joins when possible")
        
        # Check for functions in condition
        if re.search(r'\w+\s*\(', condition):
            quality_score -= 2
            issues.append("Function in join condition")
            recommendations.append("Move functions to WHERE clause if possible")
        
        # Check for complex conditions
        if re.search(r'\bOR\b', condition, re.IGNORECASE):
            quality_score -= 2
            issues.append("OR operator in join condition")
            recommendations.append("Consider splitting into UNION of simpler joins")
        
        # Check for column name patterns
        if re.search(r'id\s*=\s*\w+\.id', condition, re.IGNORECASE):
            quality_score += 1  # Bonus for joining on ID columns
        
        # Check for join type specific issues
        if join_type:
            join_type_issues = self._check_join_type_issues(condition, join_type)
            issues.extend(join_type_issues["issues"])
            recommendations.extend(join_type_issues["recommendations"])
            quality_score += join_type_issues["score_adjustment"]
        
        # Ensure score is within bounds
        quality_score = max(0, min(10, quality_score))
        
        return quality_score, issues, recommendations
    
    def _check_join_type_issues(self, condition: str, join_type: str) -> Dict[str, Any]:
        """
        Check for issues specific to join types.
        
        Args:
            condition: Join condition string
            join_type: Join type
            
        Returns:
            Dictionary with issues, recommendations, and score adjustment
        """
        result = {
            "issues": [],
            "recommendations": [],
            "score_adjustment": 0
        }
        
        # Convert join type to uppercase for comparison
        join_type = join_type.upper() if join_type else "INNER"
        
        # Check for OUTER JOIN issues
        if "LEFT" in join_type or "RIGHT" in join_type or "FULL" in join_type:
            # Check if OUTER JOIN is actually needed
            if "IS NOT NULL" in condition:
                result["issues"].append("OUTER JOIN with IS NOT NULL check")
                result["recommendations"].append("Consider using INNER JOIN instead")
                result["score_adjustment"] -= 1
        
        # Check for CROSS JOIN issues
        if "CROSS" in join_type:
            if "=" in condition:
                result["issues"].append("CROSS JOIN with equality condition")
                result["recommendations"].append("Use INNER JOIN instead of CROSS JOIN")
                result["score_adjustment"] -= 2
        
        # Check for INNER JOIN issues
        if join_type == "INNER" or join_type == "IMPLICIT":
            if "IS NULL" in condition:
                result["issues"].append("INNER JOIN with NULL check")
                result["recommendations"].append("Consider using LEFT JOIN instead")
                result["score_adjustment"] -= 1
        
        return result
    
    def evaluate_multiple_conditions(self, conditions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate multiple join conditions.
        
        Args:
            conditions: List of dictionaries with condition and optional join_type
            
        Returns:
            List of evaluation results
        """
        results = []
        
        for condition_info in conditions:
            condition = condition_info.get("condition", "")
            join_type = condition_info.get("join_type", None)
            
            evaluation = self.evaluate_condition(condition, join_type)
            results.append(evaluation)
        
        return results
    
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """
        Generate a report of join condition evaluations.
        
        Args:
            output_file: Optional file to write the report to
            
        Returns:
            Report data
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_conditions_evaluated": len(self.evaluations),
            "average_quality_score": self._calculate_average_score(),
            "common_issues": self._identify_common_issues(),
            "evaluations": self.evaluations
        }
        
        # Write report to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Generated join condition evaluation report: {output_file}")
            
            # Update changelog
            self._update_changelog(f"Generated join condition evaluation report for {len(self.evaluations)} conditions")
        
        return report
    
    def _calculate_average_score(self) -> float:
        """Calculate the average quality score of evaluated conditions."""
        if not self.evaluations:
            return 0.0
        
        total_score = sum(eval_result["quality_score"] for eval_result in self.evaluations)
        return total_score / len(self.evaluations)
    
    def _identify_common_issues(self) -> Dict[str, int]:
        """Identify common issues across all evaluations."""
        issue_counts = {}
        
        for evaluation in self.evaluations:
            for issue in evaluation["issues"]:
                if issue not in issue_counts:
                    issue_counts[issue] = 0
                issue_counts[issue] += 1
        
        return issue_counts

# Example usage
if __name__ == "__main__":
    evaluator = JoinConditionEvaluator()
    
    # Sample conditions to evaluate
    sample_conditions = [
        {"condition": "orders.customer_id = customers.id", "join_type": "INNER"},
        {"condition": "UPPER(products.name) = categories.name", "join_type": "LEFT"},
        {"condition": "employees.dept_id = departments.id OR employees.temp_dept_id = departments.id", "join_type": "INNER"}
    ]
    
    # Evaluate conditions
    for condition_info in sample_conditions:
        result = evaluator.evaluate_condition(condition_info["condition"], condition_info["join_type"])
        print(f"Condition: {condition_info['condition']}")
        print(f"Quality Score: {result['quality_score']}/10")
        print(f"Issues: {result['issues']}")
        print(f"Recommendations: {result['recommendations']}")
        print()
    
    # Generate report
    report = evaluator.generate_report("logs/join_condition_evaluation_report.json")
