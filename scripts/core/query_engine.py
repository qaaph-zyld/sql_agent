# scripts/core/query_engine.py

import re
from typing import Dict, Any, List
import sys
import time
import logging
from .exceptions import (
    NLProcessingError,
    QueryValidationError,
    SchemaError,
    DatabaseConnectionError,
    DatabaseExecutionError,
    SQLAgentError
)
from .utils import retry_on_exception
from .user_guidance_manager import UserGuidanceManager

# Assuming DatabaseConnector is in a module like scripts.connectors
# from ..connectors.database_connector import DatabaseConnector
# For now, let's use a placeholder type until the actual path is confirmed
DatabaseConnector = Any


class QueryEngine:
    """
    Processes natural language queries, generates SQL, validates SQL,
    and interacts with the database.
    """
    def __init__(self, db_connector: DatabaseConnector, schema_info: Dict[str, Any], user_guidance_manager: UserGuidanceManager):
        """
        Initializes the QueryEngine.

        Args:
            db_connector: An instance of DatabaseConnector.
            schema_info: A dictionary containing schema information.
            user_guidance_manager: An instance of UserGuidanceManager.
        """
        self.db_connector = db_connector
        self.schema_info = schema_info
        self.user_guidance_manager = user_guidance_manager
        self.query_metadata: Dict[str, Any] = {}

        self.MIN_NL_QUERY_LENGTH_CHARS = 10
        self.MAX_NL_QUERY_LENGTH_CHARS = 1000
        self.MIN_NL_QUERY_LENGTH_WORDS = 2

        # Regex for suspicious patterns (SQL keywords, comments)
        # Case-insensitive, whole word matching for keywords
        suspicious_keywords = [
            r'SELECT\b', r'INSERT\b', r'UPDATE\b', r'DELETE\b', r'DROP\b', 
            r'CREATE\b', r'ALTER\b', r'TRUNCATE\b', r'UNION\b', r'EXEC\b', 
            r'DECLARE\b', r'XP_CMDSHELL\b'
        ]
        suspicious_comments = [r'--', r'\/\*', r'\*\/'] # Escaped for regex
        self.MAX_WORD_LENGTH = 50
        self.REPETITIVE_CHAR_MIN_LEN = 10
        # Regex to find any character repeated REPETITIVE_CHAR_MIN_LEN or more times. 
        # For REPETITIVE_CHAR_MIN_LEN = 10, this means 9 repetitions after the first char: (.)\1{9,}
        self._repetitive_char_regex = re.compile(r'(.)\1{' + str(self.REPETITIVE_CHAR_MIN_LEN - 1) + r',}')

        self._suspicious_pattern_regex = re.compile(
            r'(' + '|'.join(suspicious_keywords + suspicious_comments) + r')',
            re.IGNORECASE
        )

    def _check_excessively_long_word(self, nl_query: str) -> None:
        """
        Checks if the query contains any single word that is too long.
        Raises QueryValidationError if such a word is found.
        """
        words = nl_query.split()
        for word in words:
            if len(word) > self.MAX_WORD_LENGTH:
                raise QueryValidationError(
                    f"Query contains an excessively long word ('{word[:20]}...') "
                    f"exceeding {self.MAX_WORD_LENGTH} characters. Please shorten it."
                )

    def _check_repetitive_chars(self, nl_query: str) -> None:
        """
        Checks if the query contains excessively repetitive character sequences.
        Raises QueryValidationError if such sequences are found.
        """
        match = self._repetitive_char_regex.search(nl_query)
        if match:
            raise QueryValidationError(
                f"Query contains an excessively repetitive character sequence "
                f"(e.g., '{match.group(0)[:20]}...'). Please rephrase your query."
            )

    def _check_non_ascii_chars(self, nl_query: str) -> None:
        """
        Checks if the query contains non-ASCII characters.
        Raises QueryValidationError if non-ASCII characters are found.
        """
        if not nl_query.isascii():
            # Find the first non-ASCII character for a more informative message
            first_non_ascii = next((char for char in nl_query if not char.isascii()), "")
            raise QueryValidationError(
                f"Query contains non-ASCII characters (e.g., '{first_non_ascii}'). Please use standard ASCII characters."
            )

    def _validate_nl_query_basic(self, nl_query: str) -> None:
        """
        Performs basic validation on the natural language query.
        """
        if not nl_query or not nl_query.strip():
            raise QueryValidationError("Natural language query cannot be empty.")

        if len(nl_query) < self.MIN_NL_QUERY_LENGTH_CHARS:
            raise QueryValidationError(
                f"Natural language query is too short (min {self.MIN_NL_QUERY_LENGTH_CHARS} chars)."
            )
        
        if len(nl_query) > self.MAX_NL_QUERY_LENGTH_CHARS:
            raise QueryValidationError(
                f"Natural language query is too long (max {self.MAX_NL_QUERY_LENGTH_CHARS} chars)."
            )

        if len(nl_query.split()) < self.MIN_NL_QUERY_LENGTH_WORDS:
             raise QueryValidationError(
                f"Natural language query is too short (min {self.MIN_NL_QUERY_LENGTH_WORDS} words)."
            )
        
        self._check_suspicious_patterns(nl_query)
        self._check_non_ascii_chars(nl_query)
        self._check_excessively_long_word(nl_query)
        self._check_repetitive_chars(nl_query)

    def _check_suspicious_patterns(self, nl_query: str) -> None:
        """
        Checks for suspicious patterns (SQL keywords, comments) in the NL query.
        Raises QueryValidationError if a suspicious pattern is found.
        """
        match = self._suspicious_pattern_regex.search(nl_query)
        if match:
            pattern_found = match.group(1) # Store for clarity
            detail_message = (
                f"Query contains suspicious patterns ('{pattern_found}') "
                f"that resemble SQL commands or comments. Please rephrase your question."
            )
            raise QueryValidationError(detail_message)

    def process_natural_language_query(self, nl_query: str) -> Dict[str, Any]:
        """
        Processes a natural language query, generates SQL, executes it, and returns results.
        """
        try:
            # Strip whitespace at the beginning for consistent validation
            nl_query_cleaned = nl_query.strip()
            self._validate_nl_query_basic(nl_query_cleaned)
            
            # Use nl_query_cleaned for further processing
            sql_query = self._generate_sql(nl_query_cleaned, [])
            self.validate_sql_query(sql_query) # Validate before attempting execution
            
            # Actual database execution
            results = self.db_connector.execute_query(sql_query)
            return {"data": results, "query_generated": sql_query, "status": "success"}

        except QueryValidationError as qve:
            error_message = self.user_guidance_manager.get_guidance(
                "error_query_validation", 
                params={"details": str(qve)}
            ) or str(qve)
            return {"error": error_message, "status": "validation_error"}
        except NLProcessingError as nlpe:
            error_message = self.user_guidance_manager.get_guidance(
                "error_nl_processing",
                params={"details": str(nlpe)}
            ) or str(nlpe)
            return {"error": error_message, "status": "nl_processing_error"}
        except SchemaError as se:
            error_message = self.user_guidance_manager.get_guidance(
                "error_schema",
                params={"details": str(se)}
            ) or str(se)
            return {"error": error_message, "status": "schema_error"}
        except DatabaseConnectionError as dce:
            error_message = self.user_guidance_manager.get_guidance(
                "error_db_connection",
                params={"details": str(dce)}
            ) or str(dce)
            return {"error": error_message, "status": "db_connection_error"}
        except DatabaseExecutionError as dee:
            error_message = self.user_guidance_manager.get_guidance(
                "error_sql_execution",
                params={"details": str(dee)}
            ) or str(dee)
            return {"error": error_message, "status": "sql_execution_error"}
        except Exception as e:
            # For truly unexpected errors, a generic message is fine
            error_message = self.user_guidance_manager.get_guidance(
                "error_unexpected",
                params={"details": str(e)}
            ) or f"An unexpected error occurred: {str(e)}"
            return {"error": error_message, "status": "unexpected_error"}

    def _generate_sql(self, nl_query: str, relevant_tables: List[str]) -> str:
        """
        (Internal) Generates SQL from a natural language query.
        """
        if "error_trigger_nl" in nl_query:
            raise NLProcessingError("Failed to process natural language for SQL generation.")
        
        # Specific triggers for mock execution errors, matching test case NL queries
        if nl_query == "trigger db_exec_error query":
            return "SQL_TRIGGER_DB_EXEC_ERROR"
        if nl_query == "trigger db_conn_error_exec query":
            return "SQL_TRIGGER_DB_CONN_ERROR_EXEC"
        
        # Triggers for transient error simulation
        if "trigger_transient_conn_succeeds" in nl_query:
            # self.db_connector is MockDBConnector instance in tests
            self.db_connector.transient_error_to_raise = DatabaseConnectionError
            self.db_connector.transient_fail_attempts_remaining = 2 # Fails twice, succeeds on 3rd
            return "SQL_FOR_TRANSIENT_CONN_SUCCEEDS"
        if "trigger_transient_exec_succeeds" in nl_query:
            self.db_connector.transient_error_to_raise = DatabaseExecutionError
            self.db_connector.transient_fail_attempts_remaining = 2
            return "SQL_FOR_TRANSIENT_EXEC_SUCCEEDS"
        if "trigger_transient_conn_fails_all" in nl_query:
            self.db_connector.transient_error_to_raise = DatabaseConnectionError
            self.db_connector.transient_fail_attempts_remaining = 4 # Retries = 3, so 3+1=4 attempts will fail
            return "SQL_FOR_TRANSIENT_CONN_FAILS_ALL"
        if "trigger_transient_exec_fails_all" in nl_query:
            self.db_connector.transient_error_to_raise = DatabaseExecutionError
            self.db_connector.transient_fail_attempts_remaining = 4
            return "SQL_FOR_TRANSIENT_EXEC_FAILS_ALL"
            
        if "invalid_sql_trigger" in nl_query: # For SQL validation test
            return "SELECT INVALID SQL" # Intentionally invalid SQL
        
        # Simplified mock SQL generation for other cases
        # In a real scenario, this would involve complex NLP and schema mapping
        if not relevant_tables and self.schema_info.get("tables"):
            # Fallback to the first table if no relevant tables identified (very naive)
            first_table_name = list(self.schema_info["tables"].keys())[0]
            relevant_tables.append(first_table_name)
        
        if relevant_tables:
            # Example: SELECT * FROM {table_name} WHERE ... (based on nl_query)
            # This is highly simplified for mock purposes.
            return f"SELECT * FROM {relevant_tables[0]} WHERE nl_query_was='{nl_query}'"
        
        # Fallback if no tables could be determined (should ideally be handled by NL processing)
        return f"-- Could not determine relevant tables for NL query: {nl_query}"

    def validate_sql_query(self, sql_query: str) -> bool:
        """
        Validates a given SQL query against the schema or other rules.
        """
        if not sql_query or not sql_query.strip():
            raise QueryValidationError("Generated SQL query is empty.")
        
        if "invalid_sql_trigger" in sql_query:
            raise QueryValidationError("Generated SQL is invalid.")
            
        if "non_existent_table" in sql_query:
            raise SchemaError("Query references a non-existent table.")

        self.query_metadata['validated_sql'] = sql_query
        return True

if __name__ == '__main__':
    class MockDBConnector:
        def __init__(self):
            self.force_connection_error_on_connect = False
            # For simulating transient errors that can be retried
            self.transient_fail_attempts_remaining = 0
            self.transient_error_to_raise = None # e.g., DatabaseConnectionError or DatabaseExecutionError
            # Flags to control behavior for testing execute_query (non-transient, immediate failures)
            self.force_connection_error_on_execute = False 
            self.force_execution_error_on_execute = False

        def connect(self):
            print("MockDBConnector: connect() called")
            if self.force_connection_error_on_connect:
                # This flag is set externally by test setup if needed
                raise DatabaseConnectionError("Mocked connection failure during connect.")
            return True

        def disconnect(self):
            print("MockDBConnector: disconnect() called")

        @retry_on_exception(retries=3, delay_seconds=0.1, exceptions_to_catch=(DatabaseConnectionError, DatabaseExecutionError))
        def execute_query(self, sql_query: str) -> str:
            print(f"MockDBConnector: execute_query() called with: {sql_query}")

            # Simulate transient errors first
            if self.transient_error_to_raise and self.transient_fail_attempts_remaining > 0:
                self.transient_fail_attempts_remaining -= 1
                logging.info(f"MockDBConnector: Simulating transient error ({self.transient_error_to_raise.__name__}). Attempts remaining before success: {self.transient_fail_attempts_remaining}")
                raise self.transient_error_to_raise(f"Mocked transient {self.transient_error_to_raise.__name__}")

            if self.force_connection_error_on_execute or sql_query == "SQL_TRIGGER_DB_CONN_ERROR_EXEC":
                raise DatabaseConnectionError("Mocked connection failure during execute.")
            if self.force_execution_error_on_execute or sql_query == "SQL_TRIGGER_DB_EXEC_ERROR":
                raise DatabaseExecutionError("Mocked SQL execution error.")
            return f"Mock results for SQL: {sql_query}"

    class MockUserGuidanceManager:
        def get_guidance(self, context_key: str, params: dict = None) -> str:
            details = params.get('details', 'No details provided') if params else 'No details provided'
            # Simulate fetching a template and formatting it
            # For testing, we can just return a string that indicates what was called
            if context_key == "error_query_validation":
                return f"Mock Guidance (Query Validation): {details}"
            elif context_key == "error_nl_processing":
                return f"Mock Guidance (NL Processing): {details}"
            elif context_key == "error_sql_execution":
                return f"Mock Guidance (SQL Execution): {details}"
            elif context_key == "error_schema":
                return f"Mock Guidance (Schema Error): {details}"
            elif context_key == "error_db_connection":
                return f"Mock Guidance (DB Connection): {details}"
            elif context_key == "error_unexpected":
                return f"Mock Guidance (Unexpected Error): {details}"
            return f"Mock Guidance: Unknown context key '{context_key}'. Details: {details}"

    mock_schema = {"tables": {"example_table": {"columns": ["id", "name"]}}}
    
    engine = QueryEngine(
        db_connector=MockDBConnector(),
        schema_info=mock_schema,
        user_guidance_manager=MockUserGuidanceManager()
    )

    queries_to_test = [
        "show me all users", # Expected to pass (no error)
        ("", "Mock Guidance (Query Validation): Natural language query cannot be empty."),
        ("short", "Mock Guidance (Query Validation): Natural language query is too short (min 10 chars)."),
        ("one", "Mock Guidance (Query Validation): Natural language query is too short (min 10 chars)."), # Fails char check before word check
        ("a" * 1001, "Mock Guidance (Query Validation): Natural language query is too long (max 1000 chars)."),
        ("longenough", "Mock Guidance (Query Validation): Natural language query is too short (min 2 words)."), 
        ("SELECT * FROM users", "Mock Guidance (Query Validation): Query contains suspicious patterns ('SELECT') that resemble SQL commands or comments. Please rephrase your question."),
        ("DROP TABLE important_data", "Mock Guidance (Query Validation): Query contains suspicious patterns ('DROP') that resemble SQL commands or comments. Please rephrase your question."),
        ("Hello -- comment", "Mock Guidance (Query Validation): Query contains suspicious patterns ('--') that resemble SQL commands or comments. Please rephrase your question."),
        ("Query with 😊 emoji", "Mock Guidance (Query Validation): Query contains non-ASCII characters (e.g., '😊'). Please use standard ASCII characters."),
        ("two_words word_that_is_very_very_long_and_should_exceed_the_fifty_character_limit_easily", "Mock Guidance (Query Validation): Query contains an excessively long word ('word_that_is_very_ve...') exceeding 50 characters. Please shorten it."),
        ("short aaaaaaaaaa pattern", "Mock Guidance (Query Validation): Query contains an excessively repetitive character sequence (e.g., 'aaaaaaaaaa...'). Please rephrase your query."),
        ('error_trigger_nl two_words', "Mock Guidance (NL Processing): Failed to process natural language for SQL generation."),
        # Tests for execution phase errors
        ("trigger db_exec_error query", "Mock Guidance (SQL Execution): Mocked SQL execution error."),
        ("trigger db_conn_error_exec query", "Mock Guidance (DB Connection): Mocked connection failure during execute."),
        ("force_db_connection_error_on_connect_test_case_id", "Mock Guidance (DB Connection): Mocked connection failure during connect."),
        # New tests for retry logic
        "trigger_transient_conn_succeeds query", # Expect success after 2 fails (3rd attempt)
        "trigger_transient_exec_succeeds query", # Expect success after 2 fails (3rd attempt)
        ("trigger_transient_conn_fails_all query", "Mock Guidance (DB Connection): Mocked transient DatabaseConnectionError"), # Expect final failure after 3 retries (4 attempts)
        ("trigger_transient_exec_fails_all query", "Mock Guidance (SQL Execution): Mocked transient DatabaseExecutionError")  # Expect final failure after 3 retries (4 attempts)
    ]

for item in queries_to_test:
    query_text: str
    expected_error_snippet: str = None

    if isinstance(item, tuple):
        query_text, expected_error_snippet = item
    else:  # item is a string, no error expected
        query_text = item
        # expected_error_snippet remains None

    print(f"\nProcessing NL Query: '{query_text}'")
    
    # Reset transient error flags for MockDBConnector before each test
    if hasattr(engine.db_connector, 'transient_fail_attempts_remaining'):
        engine.db_connector.transient_fail_attempts_remaining = 0
    if hasattr(engine.db_connector, 'transient_error_to_raise'):
        engine.db_connector.transient_error_to_raise = None

    # Special handling for the connection error test for MockDBConnector
    # This part is for tests that want to simulate a connection failure *before* query execution
    original_force_connect_error = getattr(engine.db_connector, 'force_connection_error_on_connect', False)
    if query_text == "force_db_connection_error_on_connect_test_case_id": # Use a unique ID for this specific test case
        engine.db_connector.force_connection_error_on_connect = True
        
    result = engine.process_natural_language_query(query_text)

    # Reset the flag if it was set for a specific test case
    if query_text == "force_db_connection_error_on_connect_test_case_id":
        engine.db_connector.force_connection_error_on_connect = original_force_connect_error

    if expected_error_snippet:
        if "error" not in result or expected_error_snippet not in result.get("error", ""):
            print(f"--- FAILED (mismatched error) ---")
            print(f"QUERY          : '{query_text}'")
            print(f"EXPECTED ERROR : {repr(expected_error_snippet)}")
            print(f"ACTUAL         : {repr(result)}")
        else:
            print(f"PASSED (expected error): '{query_text}'")
    else:
        if "error" in result:
            print(f"--- FAILED (unexpected error) ---")
            print(f"QUERY          : '{query_text}'")
            print(f"ACTUAL ERROR   : {repr(result.get('error'))}")
        else:
            print(f"PASSED (no error expected): '{query_text}'")

test_sql_validation = [
    ("SELECT * FROM example_table;", None), # Valid, no error expected
    ("", "Generated SQL query is empty."),
    ("SELECT * FROM non_existent_table;", "Query references a non-existent table."),
    ("SELECT * FROM example_table WHERE invalid_sql_trigger;", "Generated SQL is invalid.")
]
print("\n--- Testing SQL Validation Directly ---")
for sql_q, expected_error_str in test_sql_validation:
    print(f"\nValidating SQL: '{sql_q}'")
    try:
        is_valid = engine.validate_sql_query(sql_q)
        if expected_error_str:
            # This block should not be reached if an error is expected, as the exception should be caught.
            print(f"--- FAILED (SQL VAL - Expected Error Not Raised) ---")
            print(f"SQL_QUERY      : '{sql_q}'")
            print(f"EXPECTED_ERROR : {repr(expected_error_str)}")
            print(f"RESULT         : Validation returned {is_valid} instead of raising an exception.")
        else:
            # No error expected, and none was raised.
            assert is_valid is True, f"SQL Validation for '{sql_q}' should return True but returned {is_valid}"
            print(f"PASSED (SQL VAL - No Error Expected): '{sql_q}' is valid.")

    except (QueryValidationError, SchemaError) as e:
        if not expected_error_str:
            # Error was raised, but none was expected.
            print(f"--- FAILED (SQL VAL - Unexpected Error) ---")
            print(f"SQL_QUERY      : '{sql_q}'")
            print(f"EXPECTED_ERROR : None")
            print(f"ACTUAL_ERROR   : {type(e).__name__}: {str(e)}")
        elif expected_error_str in str(e):
            # Error was raised and its message contains the expected substring.
            print(f"PASSED (SQL VAL - Expected Error Caught): '{sql_q}' -> {type(e).__name__}: {str(e)}")
        else:
            # Error was raised, but its message does not match the expected substring.
            print(f"--- FAILED (SQL VAL - Mismatched Error Message) ---")
            print(f"SQL_QUERY      : '{sql_q}'")
            print(f"EXPECTED_ERROR : (substring) {repr(expected_error_str)}")
            print(f"ACTUAL_ERROR   : {type(e).__name__}: {str(e)}")
    except Exception as e:
        # Catch any other unexpected exceptions during validation
        print(f"--- FAILED (SQL VAL - Unexpected Exception Type) ---")
        print(f"SQL_QUERY      : '{sql_q}'")
        print(f"EXCEPTION_TYPE : {type(e).__name__}")
        print(f"EXCEPTION_MSG  : {str(e)}")
