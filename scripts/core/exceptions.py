#!/usr/bin/env python3
"""
Custom exceptions for the SQL Agent application.
"""

class SQLAgentError(Exception):
    """Base class for exceptions in this module."""
    pass

class DatabaseConnectionError(SQLAgentError):
    """Raised when the database connection fails."""
    pass

class DatabaseExecutionError(SQLAgentError):
    """Raised for errors during database query execution."""
    pass

class SchemaError(SQLAgentError):
    """Raised for errors related to database schema (e.g., loading, not found)."""
    pass

class QueryValidationError(SQLAgentError):
    """Raised when a generated SQL query fails validation."""
    pass

class NLProcessingError(SQLAgentError):
    """Raised for errors during natural language processing or SQL generation."""
    pass

class ConfigurationError(SQLAgentError):
    """Raised for errors related to application configuration."""
    pass
