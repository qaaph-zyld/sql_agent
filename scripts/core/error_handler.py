#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Detailed Error Message System Module

This module provides a centralized system for handling errors, logging them,
and generating user-friendly and technical error messages.
It follows the mandatory changelog protocol.
"""

import logging
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine
from scripts.core.error_context_analyzer import ErrorContextAnalyzer
from scripts.core.solution_suggestion_engine import SolutionSuggestionEngine # Added import

# Configure logging for the error handler module itself
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/error_handler.log' # Dedicated log for error handler operations
)
logger = logging.getLogger(__name__)

# --- Custom Exception Classes ---
class SQLAgentError(Exception):
    """Base class for custom exceptions in the SQL Agent project."""
    DEFAULT_ERROR_CODE = "AGT_000"  # Default Agent Error

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code or self.DEFAULT_ERROR_CODE
        self.message = message

class ConfigurationError(SQLAgentError):
    """For errors related to application configuration."""
    DEFAULT_ERROR_CODE = "CFG_001"  # Configuration Error

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code=error_code or self.DEFAULT_ERROR_CODE)

class SQLParsingError(SQLAgentError):
    """For errors encountered during SQL parsing or validation."""
    DEFAULT_ERROR_CODE = "SQL_001"  # SQL Parsing Error

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code=error_code or self.DEFAULT_ERROR_CODE)

class DataProcessingError(SQLAgentError):
    """For errors during data manipulation, analysis, or transformation."""
    DEFAULT_ERROR_CODE = "DTP_001"  # Data Processing Error

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code=error_code or self.DEFAULT_ERROR_CODE)

class UIInteractionError(SQLAgentError):
    """For errors related to backend logic supporting UI interactions."""
    DEFAULT_ERROR_CODE = "UIX_001"  # UI Interaction Error

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code=error_code or self.DEFAULT_ERROR_CODE)

class ExternalServiceError(SQLAgentError):
    """For errors when interacting with external services like databases or APIs."""
    DEFAULT_ERROR_CODE = "EXT_001"  # External Service Error

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code=error_code or self.DEFAULT_ERROR_CODE)

class FileOperationError(SQLAgentError):
    """For errors related to file system operations."""
    DEFAULT_ERROR_CODE = "FIO_001"  # File Operation Error

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code=error_code or self.DEFAULT_ERROR_CODE)

# --- ErrorHandler Class ---
class ErrorHandler:
    """
    Centralized error handling, logging, and message generation.
    """
    def __init__(self, 
                 changelog_engine: ChangelogEngine, 
                 app_logger: Optional[logging.Logger] = None, 
                 context_analyzer: Optional[ErrorContextAnalyzer] = None,
                 suggestion_engine: Optional[SolutionSuggestionEngine] = None): # Added suggestion_engine
        self.changelog_engine = changelog_engine
        self.app_logger = app_logger if app_logger else logger
        self.context_analyzer = context_analyzer if context_analyzer else ErrorContextAnalyzer(changelog_engine)
        self.suggestion_engine = suggestion_engine if suggestion_engine else SolutionSuggestionEngine(changelog_engine) # Initialize if not provided
        logger.info("ErrorHandler initialized with ErrorContextAnalyzer and SolutionSuggestionEngine.")

    def _generate_error_id(self) -> str:
        """Generates a unique error ID."""
        return str(uuid.uuid4())

    def _get_user_friendly_message(self, error: Exception) -> str:
        """Generates a more user-friendly and actionable message based on the error type."""
        user_msg_prefix = "We're sorry, but an error occurred."
        default_suggestion = "Please try your action again. If the problem continues, please contact support for assistance."

        if isinstance(error, SQLAgentError):
            # Use the specific message from SQLAgentError if it's informative and not just the class name.
            specific_detail = error.message if error.message and error.message != type(error).__name__ else ""
            if specific_detail:
                specific_detail = f"({specific_detail})"

            if isinstance(error, ConfigurationError):
                return (
                    f"{user_msg_prefix} There's an issue with the application's configuration. {specific_detail} "
                    f"The application might not function correctly. "
                    f"Please inform your system administrator or check settings if accessible."
                )
            elif isinstance(error, SQLParsingError):
                return (
                    f"{user_msg_prefix} There was a problem understanding the SQL query. {specific_detail} "
                    f"Please review your query's syntax. {default_suggestion}"
                )
            elif isinstance(error, DataProcessingError):
                return (
                    f"{user_msg_prefix} An issue occurred while processing data. {specific_detail} "
                    f"This might affect the results. {default_suggestion}"
                )
            elif isinstance(error, UIInteractionError):
                return (
                    f"{user_msg_prefix} An unexpected problem occurred with a user interface operation. {specific_detail} "
                    f"{default_suggestion}"
                )
            elif isinstance(error, ExternalServiceError):
                return (
                    f"{user_msg_prefix} The application could not communicate with an external service (e.g., database). {specific_detail} "
                    f"Please check your network and try again. If the issue persists, the service might be temporarily down."
                )
            elif isinstance(error, FileOperationError):
                return (
                    f"{user_msg_prefix} The application had trouble accessing a necessary file. {specific_detail} "
                    f"This could be due to permissions or a missing file. {default_suggestion}"
                )
            
            # Default for other SQLAgentErrors
            return f"{user_msg_prefix} {specific_detail} {default_suggestion}"
        
        # Generic fallback for unexpected non-SQLAgent errors
        return (
            f"An unexpected technical issue has occurred. We apologize for the inconvenience. "
            f"Please try again. If the problem persists, please contact support and describe the action you were performing."
        )

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None, user_message_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Handles an error by logging it, generating messages, and updating the changelog.

        Args:
            error (Exception): The error/exception object.
            context (Optional[Dict[str, Any]]): Additional context about the error (e.g., module, function, inputs).
            user_message_override (Optional[str]): A specific user-friendly message to use instead of auto-generated.

        Returns:
            Dict[str, Any]: A dictionary containing error_id, user_message, and technical_message.
        """
        error_id = self._generate_error_id()
        timestamp = datetime.utcnow().isoformat()
        
        error_type = error.__class__.__name__
        error_message = str(error)
        full_traceback = traceback.format_exc()

        # Determine error code for logging and reporting
        if isinstance(error, SQLAgentError):
            error_code_to_log = error.error_code
        else:
            error_code_to_log = "GEN_001" # Generic error code for non-SQLAgentErrors

        # Analyze context using ErrorContextAnalyzer
        context_report = self.context_analyzer.analyze_context(error, additional_context=context)

        # Log the error details, including context report
        log_message = f"Error Handled [ID: {error_id}] - Code: {error_code_to_log}, Type: {error_type}, Message: {error_message}\n"
        log_message += f"Analyzed Context Report: {context_report}\n"

        # Get suggestions from SolutionSuggestionEngine
        suggestions = self.suggestion_engine.get_suggestions(context_report)
        log_message += f"Suggested Solutions: {suggestions}\nTraceback:\n{full_traceback}"
        self.app_logger.error(log_message)

        user_message_base = user_message_override if user_message_override else self._get_user_friendly_message(error)

        # Append suggestions to the user message
        user_message_with_suggestions = f"{user_message_base}\n\nTroubleshooting Suggestions:"
        if suggestions:
            for sug in suggestions:
                user_message_with_suggestions += f"\n- {sug}"
        else:
            user_message_with_suggestions += "\n- No specific suggestions available at this time."

        technical_message = f"Error ID: {error_id}, Code: {error_code_to_log}, Type: {error_type}, Timestamp: {timestamp}. Details: {error_message}. See logs for full traceback."

        # Update changelog
        self.changelog_engine.update_changelog(
            action_summary=f"Error handled: {error_type}",
            action_type="Error Handling",
            previous_state="Operational",
            current_state=f"Error occurred (ID: {error_id})",
            changes_made=[
                f"Error ID: {error_id}",
                f"Error Code: {error_code_to_log}",
                f"Error Type: {error_type}",
                f"Error Message: {error_message}",
                f"Context: {context or 'N/A'}"
            ],
            files_affected=[{"file_path": self.app_logger.handlers[0].baseFilename if self.app_logger.handlers else 'application.log', "change_type": "APPENDED", "impact_level": "HIGH"}],
            technical_decisions=["Centralized error captured and logged. User message generated."]
        )

        return {
            'error_id': error_id,
            'user_message': user_message,
            'technical_message': technical_message,
            'timestamp': timestamp
        }

# Example Usage (Illustrative - typically ErrorHandler would be part of a larger app context)
if __name__ == "__main__":
    # Setup dummy components for demo
    class DummyChangelogEngine:
        def update_changelog(self, **kwargs):
            # Simulate changelog behavior for both ErrorHandler and ErrorContextAnalyzer
            if 'ErrorContextAnalyzer' in str(kwargs.get('action_summary')) or 'Error context analyzed' in str(kwargs.get('action_summary')):
                print(f"CHANGELOG_UPDATE (from ErrorContextAnalyzer via ErrorHandler demo): {kwargs.get('action_summary')}")
            elif 'SolutionSuggestionEngine' in str(kwargs.get('action_summary')) or 'Suggestions provided' in str(kwargs.get('action_summary')):
                print(f"CHANGELOG_UPDATE (from SolutionSuggestionEngine via ErrorHandler demo): {kwargs.get('action_summary')}")
            else:
                print(f"CHANGELOG_UPDATE (from ErrorHandler demo): {kwargs.get('action_summary')}")

    class DummyErrorContextAnalyzer:
        def __init__(self, changelog_engine):
            self.changelog_engine = changelog_engine
            print("DummyErrorContextAnalyzer initialized for demo.")

        def analyze_context(self, error: Exception, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            print(f"DUMMY_CONTEXT_ANALYSIS: Analyzing {error.__class__.__name__} with additional context: {additional_context is not None}")
            # Simulate a basic report structure
            return {
                'error_details': {'error_type': error.__class__.__name__, 'error_message': str(error), 'error_code': getattr(error, 'error_code', 'N/A')},
                'call_stack_summary': [{'file': 'dummy_file.py', 'line': 10, 'function': 'dummy_function', 'code_context': 'x = 1/0'}],
                'additional_context': additional_context or {}
            }

    class DummySolutionSuggestionEngine:
        def __init__(self, changelog_engine):
            self.changelog_engine = changelog_engine
            print("DummySolutionSuggestionEngine initialized for demo.")
        
        def get_suggestions(self, error_context_report: Dict[str, Any]) -> List[str]:
            error_type = error_context_report.get('error_details', {}).get('error_type', 'Unknown')
            print(f"DUMMY_SUGGESTION_ENGINE: Generating suggestions for {error_type}")
            return [
                f"Dummy suggestion 1 for {error_type}",
                f"Dummy suggestion 2 for {error_type}"
            ]

    demo_logger = logging.getLogger('DemoAppLogger')
    demo_logger.setLevel(logging.DEBUG)
    # Ensure logs/ directory exists or change log path
    try:
        handler = logging.FileHandler('logs/demo_app_errors.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        demo_logger.addHandler(handler)
    except FileNotFoundError:
        print("Error: 'logs' directory not found. Cannot create 'logs/demo_app_errors.log'. Skipping file logging for demo.")
        # Add a StreamHandler for console output if file logging fails
        stream_handler = logging.StreamHandler()
        demo_logger.addHandler(stream_handler)


    changelog_engine_instance = DummyChangelogEngine()
    # For the demo, we can pass the dummy context analyzer to the error handler
    # In a real app, ErrorHandler would likely create its own instances if not provided.
    dummy_context_analyzer_instance = DummyErrorContextAnalyzer(changelog_engine_instance)
    dummy_suggestion_engine_instance = DummySolutionSuggestionEngine(changelog_engine_instance)
    error_handler_instance = ErrorHandler(
        changelog_engine_instance, 
        app_logger=demo_logger,
        context_analyzer=dummy_context_analyzer_instance,
        suggestion_engine=dummy_suggestion_engine_instance # Pass the dummy suggestion engine
    )

    print("--- Demonstrating Error Handling ---")

    # Example 1: Handling a custom SQLAgentError
    try:
        raise SQLParsingError("Invalid SELECT statement.", error_code="SQL-001")
    except Exception as e:
        print(f"\nCaught exception: {type(e).__name__} - {e}")
        error_info = error_handler_instance.handle_error(e, context={'module': 'query_parser', 'input_sql': 'SELEC * FRO Users'})
        print(f"User Message: {error_info['user_message']}")
        print(f"Technical Message: {error_info['technical_message']}")

    # Example 2: Handling a standard Python error
    try:
        result = 10 / 0
    except Exception as e:
        print(f"\nCaught exception: {type(e).__name__} - {e}")
        error_info = error_handler_instance.handle_error(e, context={'module': 'calculator', 'operation': 'divide'})
        print(f"User Message: {error_info['user_message']}")
        print(f"Technical Message: {error_info['technical_message']}")

    # Example 3: ConfigurationError with user message override
    try:
        raise ConfigurationError("Database connection string missing.")
    except Exception as e:
        print(f"\nCaught exception: {type(e).__name__} - {e}")
        error_info = error_handler_instance.handle_error(
            e, 
            context={'module': 'app_startup', 'config_file': 'settings.ini'},
            user_message_override="Critical setup error: The application cannot start. Please contact admin."
        )
        print(f"User Message: {error_info['user_message']}")
        print(f"Technical Message: {error_info['technical_message']}")

    # Final message for the ErrorHandler module itself
    error_handler_instance.changelog_engine.update_changelog(
        action_summary="ErrorHandler module demonstrated",
        action_type="Component Initialization", # Re-using for demo completion
        previous_state="ErrorHandler initialized",
        current_state="ErrorHandler demonstration completed",
        changes_made=["Showcased handling of custom and standard exceptions, logging, and message generation."],
        files_affected=[{"file_path": "scripts/core/error_handler.py", "change_type": "EXECUTED_EXAMPLE", "impact_level": "LOW"}],
        technical_decisions=["Provided a robust structure for centralized error management."]
    )
    print("\n--- Error Handling Demonstration Complete ---")

