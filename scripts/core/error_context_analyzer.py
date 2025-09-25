#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Error Context Analyzer Module

This module provides utilities to analyze the context of an error,
collecting information that can be used for troubleshooting or logging.
It follows the mandatory changelog protocol.
"""

import logging
import inspect
import traceback
from typing import Dict, Any, Optional, List, Tuple

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine
from scripts.core.error_handler import SQLAgentError # To access error_code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/error_context_analyzer.log'
)
logger = logging.getLogger(__name__)

class ErrorContextAnalyzer:
    """
    Analyzes and collects contextual information surrounding an error.
    """
    def __init__(self, changelog_engine: ChangelogEngine):
        self.changelog_engine = changelog_engine
        logger.info("ErrorContextAnalyzer initialized.")
        self._update_changelog(
            action_summary="ErrorContextAnalyzer initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Analyzer ready to collect error context.",
            changes_made=["Initialized internal state."],
            files_affected=[{"file_path": "scripts/core/error_context_analyzer.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Established a basic structure for error context analysis. Placed in core due to directory creation issues."]
        )

    def _update_changelog(self, action_summary: str, action_type: str, previous_state: str, current_state: str, changes_made: List[str], files_affected: List[Dict[str, str]], technical_decisions: List[str]) -> None:
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type=action_type,
            previous_state=previous_state,
            current_state=current_state,
            changes_made=changes_made,
            files_affected=files_affected,
            technical_decisions=technical_decisions
        )

    def _get_error_details(self, error: Exception) -> Dict[str, Any]:
        """Extracts basic details from the error object."""
        details = {
            'error_type': error.__class__.__name__,
            'error_message': str(error),
            'error_code': getattr(error, 'error_code', 'N/A') if isinstance(error, SQLAgentError) else 'N/A'
        }
        return details

    def _get_call_stack_summary(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves a summary of the current call stack, excluding this method."""
        stack_summary = []
        try:
            frames = traceback.extract_stack(limit=limit + 2) 
            relevant_frames = frames[:-2] if len(frames) > 2 else frames

            for frame in reversed(relevant_frames):
                stack_summary.append({
                    'file': frame.filename,
                    'line': frame.lineno,
                    'function': frame.name,
                    'code_context': frame.line 
                })
        except Exception as e:
            logger.warning(f"Could not retrieve full call stack summary: {e}")
            stack_summary.append({'error': 'Failed to retrieve call stack details.'})
        return stack_summary

    def analyze_context(self, error: Exception, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes the context of a given error.

        Args:
            error (Exception): The error object.
            additional_context (Optional[Dict[str, Any]]): 
                Any other relevant information (e.g., user inputs, system state).

        Returns:
            Dict[str, Any]: A dictionary containing the analyzed error context.
        """
        logger.info(f"Analyzing context for error: {error.__class__.__name__}")
        
        context_report = {
            'error_details': self._get_error_details(error),
            'call_stack_summary': self._get_call_stack_summary(),
            'additional_context': additional_context or {}
        }

        log_context_summary = {
            'error_type': context_report['error_details']['error_type'],
            'error_message': context_report['error_details']['error_message'],
            'origin_function': context_report['call_stack_summary'][0]['function'] if context_report['call_stack_summary'] else 'N/A',
            'origin_file': context_report['call_stack_summary'][0]['file'] if context_report['call_stack_summary'] else 'N/A',
            'has_additional_context': bool(additional_context)
        }
        logger.info(f"Error context analysis summary: {log_context_summary}")

        self._update_changelog(
            action_summary=f"Error context analyzed for {error.__class__.__name__}",
            action_type="Error Analysis",
            previous_state="Error occurred",
            current_state="Error context collected",
            changes_made=[
                f"Collected details for error: {context_report['error_details']}",
                f"Call stack summary (first entry): {context_report['call_stack_summary'][0] if context_report['call_stack_summary'] else 'N/A'}",
                f"Additional context keys: {list(additional_context.keys()) if additional_context else 'None'}"
            ],
            files_affected=[{"file_path": "logs/error_context_analyzer.log", "change_type": "APPENDED", "impact_level": "LOW"}],
            technical_decisions=["Captured error details, call stack, and provided additional context."]
        )
        return context_report

# Example Usage:
if __name__ == "__main__":
    class DummyChangelogEngine:
        def update_changelog(self, **kwargs):
            print(f"CHANGELOG_UPDATE (ErrorContextAnalyzer): {kwargs.get('action_summary')}")

    changelog_engine_instance = DummyChangelogEngine()
    context_analyzer = ErrorContextAnalyzer(changelog_engine_instance)

    def sample_function_that_errors():
        try:
            x = 1 / 0
        except ZeroDivisionError as e:
            current_operation_context = {
                'user_id': 'test_user_123',
                'input_values': {'dividend': 1, 'divisor': 0},
                'module_version': '1.0.2'
            }
            print(f"\n--- Analyzing error in sample_function_that_errors ---")
            report = context_analyzer.analyze_context(e, additional_context=current_operation_context)
            print("Context Analysis Report:")
            import json
            print(json.dumps(report, indent=2))

    def another_function():
        try:
            raise SQLAgentError("Failed to connect to database.", error_code="DB_CONN_005")
        except SQLAgentError as e:
            print(f"\n--- Analyzing error in another_function ---")
            report = context_analyzer.analyze_context(e, additional_context={'attempted_host': 'db.example.com'})
            print("Context Analysis Report:")
            import json
            print(json.dumps(report, indent=2))

    sample_function_that_errors()
    another_function()

    print("\n--- Error Context Analyzer Demonstration Complete ---")
