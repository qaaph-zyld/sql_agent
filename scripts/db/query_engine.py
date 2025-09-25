#!/usr/bin/env python3
"""
Query Engine - Natural language to SQL processing
"""

import os
from pathlib import Path
import json
import re
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord
from scripts.db.db_connector import DatabaseConnector
from scripts.core.user_guidance_manager import UserGuidanceManager
from scripts.core import exceptions as core_exceptions

# Configure logging
import logging
import re
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent.parent / "logs" / "query_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("query_engine")

MAX_NL_QUERY_LENGTH = 1000  # Define a constant for max query length
SUSPICIOUS_PATTERNS_REGEX = re.compile(r"<script|\-\- |xp_|/\*|\*/|\b(ALTER|CREATE|DROP|TRUNCATE|INSERT|UPDATE|DELETE|GRANT|REVOKE)\b", re.IGNORECASE)

class QueryEngine:
    """Natural language to SQL query processing engine"""
    
    def __init__(self, user_guidance_manager: Optional[UserGuidanceManager] = None):
        """Initialize query engine"""
        self.db_connector = DatabaseConnector()
        self.changelog_engine = ChangelogEngine()
        self.ugm = user_guidance_manager
        self.schema_cache = {}
        self._load_schema_cache()
        
    def _load_schema_cache(self) -> None:
        """Load database schema into cache"""
        try:
            table_names = self.db_connector.get_table_names()
            for table in table_names:
                self.schema_cache[table] = self.db_connector.get_table_schema(table)
            logger.info(f"Loaded schema for {len(table_names)} tables into cache")
        except Exception as e:
            logger.error(f"Error loading schema cache: {e}")
            raise core_exceptions.SchemaError(f"Failed to load database schema: {e}")
            
    def process_natural_language_query(self, query: str) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Process natural language query and return SQL and results

        # Initialize metadata structure at the very beginning
        metadata = {
            "status": "",
            "message": "",
            "validation": {},
            "generation": {},
            "execution": {},
            "performance": {},
            "input_flags": [],
            "total_time_ms": 0
        }

        # Suspicious Pattern Check (run this early)
        if SUSPICIOUS_PATTERNS_REGEX.search(query):
            logger.warning(f"Potentially suspicious pattern detected in natural language query: {query[:100]}...")
            metadata["input_flags"].append("suspicious_pattern_detected")
        
        Args:
            query: Natural language query string
            
        Returns:
            Tuple containing (generated SQL query, query results, metadata)
            where metadata includes validation and performance information
        """
        # Input Validation (empty/whitespace)
        if not query or query.isspace():
            logger.warning("Received an empty or whitespace-only natural language query.")
            error_message = "Input query cannot be empty."
            if self.ugm:
                guidance = self.ugm.get_guidance("error_empty_query")
                if guidance:
                    error_message = f"{error_message}\n\n💡 **Guidance:** {guidance}"
            metadata["status"] = "ERROR"
            metadata["message"] = error_message
            metadata["validation"].update({"status": "FAILED", "message": error_message})
            return "", [], metadata

        if len(query) > MAX_NL_QUERY_LENGTH:
            logger.warning(f"Received an excessively long natural language query. Length: {len(query)}, Max: {MAX_NL_QUERY_LENGTH}")
            error_message = f"Input query is too long. Maximum length is {MAX_NL_QUERY_LENGTH} characters."
            if self.ugm:
                guidance = self.ugm.get_guidance("error_long_query", params={"max_length": MAX_NL_QUERY_LENGTH})
                if guidance:
                    error_message = f"{error_message}\n\n **Guidance:** {guidance}"
            metadata["status"] = "ERROR"
            metadata["message"] = error_message
            metadata["validation"].update({"status": "FAILED", "message": error_message})
            return "", [], metadata

        # Pre-Response: Changelog update execution (only if basic validations pass)
        self.changelog_engine.quick_update("Processing natural language query", [query], [])
        
        # Generate SQL from natural language
        start_time_generation = self._get_current_timestamp_ms()
        sql_query = "" # Initialize sql_query
        generation_time = 0
        try:
            sql_query = self._generate_sql(query)
            generation_time = self._get_current_timestamp_ms() - start_time_generation
            metadata["generation"].update({
                "status": "SUCCESS",
                "message": "SQL generated successfully.",
                "time_ms": generation_time,
                "original_query": sql_query # Store the generated SQL here
            })
        except core_exceptions.NLProcessingError as nle:
            generation_time = self._get_current_timestamp_ms() - start_time_generation
            logger.error(f"Natural language processing failed: {nle}. Query: {query}")
            self._update_changelog(
                query,
                "", # No SQL generated
                0,
                validation_status="SKIPPED",
                execution_status="SKIPPED",
                metadata={"nl_processing_error": str(nle)}
            )
            metadata["status"] = "ERROR"
            user_message = f"Could not process natural language query: {nle}" # Fallback message
            if self.ugm:
                guidance = self.ugm.get_guidance("error_nl_processing", params={"technical_error": str(nle)})
                if guidance:
                    user_message = guidance
            metadata["message"] = user_message
            metadata["generation"].update({
                "status": "FAILED",
                "message": str(nle),
                "time_ms": generation_time
            })
            metadata["validation"].update({"status": "SKIPPED", "message": "SQL generation failed."})
            metadata["execution"].update({"status": "SKIPPED", "message": "SQL generation failed."})
            metadata["total_time_ms"] = generation_time
            return "", [], metadata
        
        # Validate and optimize the SQL query
        start_time = self._get_current_timestamp_ms()
        final_query = sql_query # Default to original SQL query
        validation_time = 0
        try:
            optimized_query = self.validate_sql_query(sql_query)
            validation_time = self._get_current_timestamp_ms() - start_time
            final_query = optimized_query if optimized_query else sql_query # Use optimized if available
            metadata["validation"].update({
                "status": "SUCCESS",
                "message": "Query passed basic validation.", # Generic success message
                "time_ms": validation_time,
                "optimized": optimized_query is not None and optimized_query != sql_query
            })
        except core_exceptions.QueryValidationError as qve:
            validation_time = self._get_current_timestamp_ms() - start_time
            logger.warning(f"Query validation failed: {qve}")
            self._update_changelog(
                query,
                sql_query,
                0,
                validation_status="FAILED",
                validation_message=str(qve)
            )
            metadata["status"] = "ERROR"
            user_message = f"Query validation failed: {qve}" # Fallback message
            if self.ugm:
                guidance = self.ugm.get_guidance("error_query_validation", params={"technical_error": str(qve)})
                if guidance:
                    user_message = guidance
            metadata["message"] = user_message
            metadata["validation"].update({
                "status": "FAILED",
                "message": str(qve),
                "time_ms": validation_time
            })
            # metadata["generation"] is now updated within the try-except block for _generate_sql
            # or if NLProcessingError is caught.
            # metadata["generation"].update({
            #     "time_ms": generation_time,
            #     "original_query": sql_query
            # })
            metadata["execution"].update({
                "status": "SKIPPED",
                "time_ms": 0,
                "row_count": 0
            })
            metadata["total_time_ms"] = generation_time + validation_time
            return sql_query, [], metadata
        
        # Execute the validated and optimized query
        start_time = self._get_current_timestamp_ms()
        try:
            results = self.db_connector.execute_query(final_query)
            execution_status = "SUCCESS"
            execution_message = f"Query returned {len(results)} rows"
        except core_exceptions.DatabaseConnectionError as dce:
            logger.error(f"Database connection or query execution error: {dce}")
            results = []
            execution_status = "FAILED"
            original_error_message = str(dce)
            execution_message = original_error_message

            if self.ugm:
                guidance = self.ugm.get_guidance("error_db_connection", params={"error_message": original_error_message, "sql_query": final_query})
                if guidance:
                    execution_message = f"{original_error_message}\n\n **Guidance:** {guidance}"
        except Exception as e: # Catch other unexpected errors during execution
            logger.error(f"Query execution failed: {e}")
            results = []
            execution_status = "FAILED"
            original_error_message = str(e)
            execution_message = original_error_message # Default message

            if self.ugm:
                # Attempt to get more specific error type for context key if possible
                # For now, using a general key. Could be enhanced by parsing 'e'.
                context_key = "error_sql_execution"
                guidance_params = {"error_message": original_error_message, "sql_query": final_query}
                
                guidance = self.ugm.get_guidance(context_key, params=guidance_params)
                if guidance:
                    execution_message = f"{original_error_message}\n\n **Guidance:** {guidance}"
                else:
                    # Fallback if specific guidance key isn't found, try a very generic one or log it
                    logger.info(f"No specific guidance found for key '{context_key}' during SQL execution error.")
        execution_time = self._get_current_timestamp_ms() - start_time
        
        # Populate metadata for successful execution or execution attempt
        # metadata["validation"] is already updated in the try-except block for validate_sql_query
        # If execution is reached, validation was successful.
        metadata["generation"].update({
            "time_ms": generation_time,
            "original_query": sql_query
        })
        metadata["execution"].update({
            "status": execution_status,
            "time_ms": execution_time,
            "row_count": len(results),
            "message": execution_message
        })
        metadata["total_time_ms"] = generation_time + validation_time + execution_time

        if execution_status == "SUCCESS":
            metadata["status"] = "SUCCESS"
            metadata["message"] = "Query processed successfully."
        else:
            # If execution failed, status is already ERROR, message is from exception
            # Ensure the main status and message reflect the execution failure if not already set by a prior error
            if not metadata.get("status"):
                 metadata["status"] = "ERROR"
            if not metadata.get("message"):
                 metadata["message"] = execution_message
        
        # Post-Response: System validation
        self._update_changelog(
            query, 
            final_query, 
            len(results),
            validation_status="SUCCESS",
            validation_message=validation_message,
            execution_status=execution_status,
            execution_time_ms=execution_time,
            metadata=metadata
        )
        
        return final_query, results, metadata
        
    def _get_current_timestamp_ms(self) -> int:
        """Get current timestamp in milliseconds"""
        import time
        return int(time.time() * 1000)
        
    def _generate_sql(self, natural_language_query: str) -> str:
        """
        Generate SQL query from natural language
        
        Uses a more advanced pattern matching and context-aware approach
        to convert natural language to SQL queries.
        """
        query = natural_language_query.lower()
        logger.info(f"Processing natural language query: {query}")
        
        # Extract key components from the query
        intent = self._determine_query_intent(query)
        table_name = self._extract_table_name(query)
        columns = self._extract_columns(query, table_name)
        conditions = self._extract_conditions(query, table_name)
        order_by = self._extract_order_by(query, table_name)
        limit = self._extract_limit(query)
        group_by = self._extract_group_by(query, table_name)
        
        # Build SQL query based on intent and extracted components
        if not table_name and intent not in ["unknown_intent_no_table"]: # Allow certain intents to proceed without table for now
            raise core_exceptions.NLProcessingError(f"Could not identify a target table in the query: '{natural_language_query}'.")

        if intent == "count":
            if columns and columns != ["*"]:
                sql = f"SELECT COUNT({columns[0]}) as count FROM {table_name}"
            else:
                sql = f"SELECT COUNT(*) as count FROM {table_name}"
        elif intent == "average":
            column = columns[0] if columns and columns != ["*"] else self._get_numeric_column(table_name)
            if not column:
                raise core_exceptions.NLProcessingError(f"Could not identify a numeric column in table '{table_name}' for AVG operation.")
            sql = f"SELECT AVG({column}) as average FROM {table_name}"
        elif intent == "sum":
            column = columns[0] if columns and columns != ["*"] else self._get_numeric_column(table_name)
            if not column:
                raise core_exceptions.NLProcessingError(f"Could not identify a numeric column in table '{table_name}' for SUM operation.")
            sql = f"SELECT SUM({column}) as total FROM {table_name}"
        elif intent == "select":
            cols_str = ", ".join(columns) if columns else "*"
            sql = f"SELECT {cols_str} FROM {table_name}"
        elif intent == "group":
            agg_column = self._get_numeric_column(table_name)
            if not agg_column:
                raise core_exceptions.NLProcessingError(f"Could not identify a numeric column in table '{table_name}' for AVG aggregation in GROUP BY operation.")
            if not group_by:
                 raise core_exceptions.NLProcessingError(f"Could not identify a column to group by for table '{table_name}'.")
            sql = f"SELECT {group_by}, COUNT(*) as count, AVG({agg_column}) as average FROM {table_name} GROUP BY {group_by}"
        else: # Handles 'unknown_intent' or other fallbacks
            logger.warning(f"Could not determine specific intent for query: '{natural_language_query}'. Defaulting to SELECT *. Table identified: '{table_name}'")
            if not table_name:
                # This case should ideally be caught by the check at the beginning of the function.
                # However, if intent is 'unknown' and table_name is also None, it's a clear failure.
                raise core_exceptions.NLProcessingError(f"Could not understand the query or identify a target table: '{natural_language_query}'.")
            # Default to a simple select if table name is present
            sql = f"SELECT TOP 10 * FROM {table_name}"
            
        # Add WHERE clause if conditions exist
        if conditions:
            sql += f" WHERE {conditions}"
            
        # Add GROUP BY clause if needed and not already added
        if group_by and intent != "group":
            sql += f" GROUP BY {group_by}"
            
        # Add ORDER BY clause if specified
        if order_by:
            sql += f" ORDER BY {order_by}"
            
        # Add LIMIT/TOP clause if not already added and limit is specified
        if limit and "TOP" not in sql:
            # Replace SELECT with SELECT TOP for MS SQL Server
            sql = sql.replace("SELECT", f"SELECT TOP {limit}")
            
        logger.info(f"Generated SQL query: {sql}")
        return sql
        
    def _determine_query_intent(self, query: str) -> str:
        """Determine the primary intent of the query"""
        # Check for aggregation intents
        if re.search(r'\b(count|how many|total number)\b', query):
            return "count"
        elif re.search(r'\b(average|avg|mean)\b', query):
            return "average"
        elif re.search(r'\b(sum|total|add up)\b', query):
            return "sum"
        elif re.search(r'\b(group by|group|categorize|segment)\b', query):
            return "group"
        
        # Default intent is select
        return "select"
    
    def _get_numeric_column(self, table_name: str) -> str:
        """Get the first numeric column from a table for aggregation"""
        if table_name not in self.schema_cache:
            return "*"
            
        numeric_types = ["int", "float", "decimal", "numeric", "money", "smallint", "bigint"]
        
        for col in self.schema_cache[table_name]:
            if any(num_type in col["DATA_TYPE"].lower() for num_type in numeric_types):
                return col["COLUMN_NAME"]
                
        # If no numeric column found, return first column
        return self.schema_cache[table_name][0]["COLUMN_NAME"] if self.schema_cache[table_name] else "*"
        
    def _extract_columns(self, query: str, table_name: str) -> List[str]:
        """Extract column names from the query"""
        if table_name not in self.schema_cache:
            return ["*"]
            
        columns = []
        all_columns = [col["COLUMN_NAME"].lower() for col in self.schema_cache[table_name]]
        
        # Check for specific columns mentioned in query
        for col in all_columns:
            if col in query.lower():
                columns.append(col)
                
        # Look for "all columns" or similar phrases
        if re.search(r'\b(all|every|\*)\b', query):
            return ["*"]
            
        return columns if columns else ["*"]
        
    def _extract_conditions(self, query: str, table_name: str) -> str:
        """Extract WHERE conditions from the query"""
        if table_name not in self.schema_cache:
            return ""
            
        conditions = []
        
        # Look for comparison patterns
        # Format: <column> <operator> <value>
        operators = {
            "equal to": "=", 
            "equals": "=", 
            "is": "=",
            "greater than": ">", 
            "less than": "<",
            "at least": ">=", 
            "at most": "<=",
            "not equal": "!="
        }
        
        for col in self.schema_cache[table_name]:
            col_name = col["COLUMN_NAME"].lower()
            
            # Skip if column not mentioned
            if col_name not in query.lower():
                continue
                
            # Check for each operator
            for text_op, sql_op in operators.items():
                pattern = f"{col_name}\\s+{text_op}\\s+([\\w\\d]+)"
                match = re.search(pattern, query.lower())
                
                if match:
                    value = match.group(1)
                    # Add quotes if it's a string column
                    if col["DATA_TYPE"].lower() in ["varchar", "char", "text", "nvarchar"]:
                        conditions.append(f"{col_name} {sql_op} '{value}'")
                    else:
                        conditions.append(f"{col_name} {sql_op} {value}")
                        
        return " AND ".join(conditions)
        
    def _extract_order_by(self, query: str, table_name: str) -> str:
        """Extract ORDER BY clause from the query"""
        if table_name not in self.schema_cache:
            return ""
            
        # Look for ordering terms
        order_patterns = [
            (r'order by ([\w\s]+) ascending', "ASC"),
            (r'order by ([\w\s]+) descending', "DESC"),
            (r'sort by ([\w\s]+) ascending', "ASC"),
            (r'sort by ([\w\s]+) descending', "DESC"),
            (r'order by ([\w\s]+)', "ASC"),  # Default to ascending
            (r'sort by ([\w\s]+)', "ASC")     # Default to ascending
        ]
        
        for pattern, direction in order_patterns:
            match = re.search(pattern, query.lower())
            if match:
                col_name = match.group(1).strip()
                # Verify column exists
                for col in self.schema_cache[table_name]:
                    if col["COLUMN_NAME"].lower() == col_name:
                        return f"{col_name} {direction}"
                        
        return ""
        
    def _extract_limit(self, query: str) -> str:
        """Extract LIMIT/TOP value from the query"""
        # Look for limit patterns
        limit_patterns = [
            r'top (\d+)',
            r'limit (\d+)',
            r'first (\d+)',
            r'(\d+) results',
            r'(\d+) records',
            r'(\d+) rows'
        ]
        
        for pattern in limit_patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(1)
                
        return ""
        
    def _extract_group_by(self, query: str, table_name: str) -> str:
        """Extract GROUP BY column from the query"""
        if table_name not in self.schema_cache:
            return ""
            
        # Look for grouping terms
        group_patterns = [
            r'group by ([\w\s]+)',
            r'grouped by ([\w\s]+)',
            r'categorize by ([\w\s]+)',
            r'segment by ([\w\s]+)'
        ]
        
        for pattern in group_patterns:
            match = re.search(pattern, query.lower())
            if match:
                col_name = match.group(1).strip()
                # Verify column exists
                for col in self.schema_cache[table_name]:
                    if col["COLUMN_NAME"].lower() == col_name:
                        return col_name
                        
        return ""
    
    def _extract_table_name(self, query: str) -> str:
        """Extract table name from natural language query"""
        # Simple implementation - look for table names we know about
        for table in self.schema_cache.keys():
            if table.lower() in query.lower():
                return table
        
        # Default to first table if none found
        return list(self.schema_cache.keys())[0] if self.schema_cache else "unknown_table"
        
    def _extract_column_name(self, query: str, table_name: str) -> str:
        """Extract column name from natural language query"""
        if table_name not in self.schema_cache:
            return "*"
            
        columns = [col["COLUMN_NAME"] for col in self.schema_cache[table_name]]
        
        # Look for column names in the query
        for col in columns:
            if col.lower() in query.lower():
                return col
                
        # Default to first column if none found
        return columns[0] if columns else "*"
    
    def _update_changelog(self, natural_query: str, sql_query: str, result_count: int, 
                       validation_status: str = "SUCCESS", validation_message: str = "",
                       execution_status: str = "SUCCESS", execution_time_ms: int = 0,
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update changelog with query execution details"""
        files_affected = [
            ChangeVector(
                file_path="scripts/db/query_engine.py",
                change_type=ChangeType.READ,
                operation="Query Execution",
                impact_level="LOW",
                dependencies=["scripts/db/db_connector.py"]
            )
        ]
        
        # Build changes made list based on status
        changes_made = [f"Converted natural language to SQL: '{sql_query}'"]
        
        if validation_status == "SUCCESS":
            changes_made.append(f"Successfully validated SQL query: {validation_message}")
            if metadata and metadata.get("validation", {}).get("optimized", False):
                changes_made.append("Optimized query for better performance")
        else:
            changes_made.append(f"Query validation failed: {validation_message}")
            
        if execution_status == "SUCCESS":
            changes_made.append(f"Retrieved {result_count} results from database in {execution_time_ms}ms")
        elif execution_status == "FAILED":
            changes_made.append(f"Query execution failed: {validation_message}")
        else:  # SKIPPED
            changes_made.append("Query execution skipped due to validation failure")
        
        # Build technical decisions based on available data
        technical_decisions = [
            "Used advanced pattern matching for natural language processing",
            "Applied schema knowledge for column and table selection"
        ]
        
        if validation_status == "SUCCESS":
            technical_decisions.append("Validated query for safety and correctness")
            if metadata and metadata.get("validation", {}).get("optimized", False):
                technical_decisions.append("Applied query optimization techniques")
                
        if execution_status == "SUCCESS":
            technical_decisions.append("Executed read-only query with performance monitoring")
            
        # Build next actions based on results
        next_actions = []
        
        if validation_status != "SUCCESS":
            next_actions.append("Fix query validation issues")
        elif execution_status != "SUCCESS":
            next_actions.append("Investigate query execution failures")
        else:
            next_actions.append("Enhance natural language processing capabilities")
            next_actions.append("Improve query optimization techniques")
            
            if execution_time_ms > 1000:  # Slow query (>1 second)
                next_actions.append("Optimize slow query performance")
            
            if result_count > 1000:  # Large result set
                next_actions.append("Implement pagination for large result sets")
                
        # Create performance summary for current state
        performance_summary = "Performance metrics:\n"
        if metadata:
            performance_summary += f"- Generation time: {metadata.get('generation', {}).get('time_ms', 0)}ms\n"
            performance_summary += f"- Validation time: {metadata.get('validation', {}).get('time_ms', 0)}ms\n"
            performance_summary += f"- Execution time: {metadata.get('execution', {}).get('time_ms', 0)}ms\n"
            performance_summary += f"- Total processing time: {metadata.get('total_time_ms', 0)}ms\n"
        
        answer_record = AnswerRecord(
            action_summary=f"Executed Natural Language Query: '{natural_query}'",
            action_type="Query Execution",
            previous_state="Database in read state",
            current_state=f"Database in read state after query\n{performance_summary}",
            changes_made=changes_made,
            files_affected=files_affected,
            technical_decisions=technical_decisions,
            next_actions=next_actions
        )
        
        self.changelog_engine.update_changelog(answer_record)
        logger.info("Changelog updated with query execution details")
        
    def validate_sql_query(self, sql_query: str) -> str:
        """
        Validate the generated SQL query. Raises QueryValidationError on failure.
        Returns the optimized query string if validation passes.
        """
        if not sql_query.strip():
            raise core_exceptions.QueryValidationError("SQL query is empty.")

        query_upper = sql_query.strip().upper()
        if not (query_upper.startswith("SELECT") or query_upper.startswith("WITH")):
            raise core_exceptions.QueryValidationError("Query must be a SELECT statement or a CTE (WITH ... SELECT ...). Only data retrieval queries are allowed.")

        dangerous_patterns = [
            (r"\bDROP\b", "DROP operations are not allowed"),
            (r"\bDELETE\b", "DELETE operations are not allowed (use for specific record removal if ever enabled)"),
            (r"\bTRUNCATE\b", "TRUNCATE operations are not allowed"),
            (r"\bALTER\b", "ALTER operations are not allowed"),
            (r"\bCREATE\b", "CREATE operations are not allowed (except for temp tables if supported)"),
            (r"\bINSERT\b", "INSERT operations are not allowed"),
            (r"\bUPDATE\b", "UPDATE operations are not allowed"),
            (r"\bEXEC\b(?:UTE)?\b", "EXECUTE operations are not allowed"), # Catches EXEC and EXECUTE
            (r"\b(SP_|XP_)\w+\b", "Stored procedures are not allowed"), # Catches sp_ and xp_
            (r"--(?!(?:\s*(?:BEGIN|END)\s*(?:QUERY_OPTIMIZER_HINTS|QUERY_METADATA)|\s*\+|\s*ENABLE_PARALLEL_PLAN))", "SQL comments (--) are generally not allowed unless specific approved hints."),
            (r"/\*.*?\*/", "Block comments (/* ... */) are not allowed"),
            (r";(?!\s*(?:--\s*(?:BEGIN|END)\s*(?:QUERY_OPTIMIZER_HINTS|QUERY_METADATA)|\s*$))", "Multiple statements (;) are not allowed unless part of specific approved hints or end of query.")
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                logger.warning(f"SQL Validation failed due to dangerous pattern: {message}. Query: {sql_query[:200]}...")
                raise core_exceptions.QueryValidationError(message)

        if not self._check_basic_syntax(sql_query):
            # _check_basic_syntax logs its own warnings
            raise core_exceptions.QueryValidationError("SQL syntax appears to be invalid based on basic checks (e.g., unbalanced parentheses, missing SELECT/FROM).")

        tables = self._extract_tables_from_sql(sql_query)
        if not tables:
            # This might be acceptable for queries like 'SELECT 1+1', but for DB interaction, we expect tables.
            # Depending on strictness, this could be a warning or an error.
            # For now, let's assume a query interacting with DB should have tables.
            logger.warning(f"No valid table names found in query: {sql_query[:200]}...")
            # raise core_exceptions.QueryValidationError("No valid table names found in query. Queries are expected to interact with database tables.")
            # Relaxing this for now, as some valid SQL (e.g. SELECT GETDATE()) might not have tables.

        for table in tables: # This loop will be skipped if 'tables' is empty
            if table not in self.schema_cache:
                logger.warning(f"Validation failed: Table '{table}' does not exist. Query: {sql_query[:200]}...")
                raise core_exceptions.QueryValidationError(f"Table '{table}' does not exist in the database.")

        if self._needs_where_clause(sql_query, tables):
            logger.warning(f"Validation failed: Query may return too many rows. Query: {sql_query[:200]}...")
            raise core_exceptions.QueryValidationError("Query on potentially large table(s) is missing a WHERE clause or LIMIT/TOP specifier. This is to prevent excessive data retrieval.")

        optimized_query = self._optimize_query(sql_query)
        logger.info(f"Query passed validation. Original: '{sql_query[:100]}...', Optimized: '{optimized_query[:100]}...'")
        return optimized_query
    
    def _check_basic_syntax(self, sql_query: str) -> bool:
        """Check for basic SQL syntax validity"""
        # Check for balanced parentheses
        if sql_query.count('(') != sql_query.count(')'):
            logger.warning("Unbalanced parentheses in SQL query")
            return False
            
        # Check for basic SELECT structure
        if not re.search(r'\bSELECT\b.*\bFROM\b', sql_query, re.IGNORECASE | re.DOTALL):
            logger.warning("Query does not contain valid SELECT...FROM structure")
            return False
            
        return True
        
    def _extract_tables_from_sql(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query"""
        # Simple regex to extract table names from FROM and JOIN clauses
        from_pattern = r'\bFROM\s+([\w\[\]\._]+)'  # Matches: FROM table_name
        join_pattern = r'\bJOIN\s+([\w\[\]\._]+)'   # Matches: JOIN table_name
        
        tables = []
        
        # Extract FROM tables
        from_matches = re.findall(from_pattern, sql_query, re.IGNORECASE)
        if from_matches:
            tables.extend(from_matches)
            
        # Extract JOIN tables
        join_matches = re.findall(join_pattern, sql_query, re.IGNORECASE)
        if join_matches:
            tables.extend(join_matches)
            
        # Clean table names (remove brackets, schema prefixes, etc.)
        clean_tables = []
        for table in tables:
            # Remove brackets if present
            table = table.replace('[', '').replace(']', '')
            # Remove schema prefix if present
            if '.' in table:
                table = table.split('.')[-1]
            clean_tables.append(table)
            
        return clean_tables
        
    def _needs_where_clause(self, sql_query: str, tables: List[str]) -> bool:
        """Check if query needs a WHERE clause based on table sizes"""
        # If query already has a WHERE clause or LIMIT/TOP, it's fine
        if re.search(r'\bWHERE\b', sql_query, re.IGNORECASE) or \
           re.search(r'\bTOP\s+\d+', sql_query, re.IGNORECASE) or \
           re.search(r'\bLIMIT\s+\d+', sql_query, re.IGNORECASE):
            return False
            
        # Check if any table is large (more than 1000 rows)
        for table in tables:
            try:
                row_count = self._get_table_row_count(table)
                if row_count > 1000:
                    return True
            except Exception:
                # If we can't determine size, assume it's large
                return True
                
        return False
        
    def _optimize_query(self, sql_query: str) -> str:
        """Optimize SQL query for better performance"""
        optimized = sql_query
        
        # Add TOP clause if not present to limit results
        if not re.search(r'\bTOP\s+\d+', optimized, re.IGNORECASE) and \
           not re.search(r'\bLIMIT\s+\d+', optimized, re.IGNORECASE) and \
           not re.search(r'\bCOUNT\s*\(', optimized, re.IGNORECASE) and \
           not re.search(r'\bSUM\s*\(', optimized, re.IGNORECASE) and \
           not re.search(r'\bAVG\s*\(', optimized, re.IGNORECASE):
            # Add TOP 100 to SELECT statements without aggregates
            optimized = re.sub(r'\bSELECT\b', 'SELECT TOP 100', optimized, flags=re.IGNORECASE)
            
        # Replace SELECT * with specific columns when possible
        if re.search(r'\bSELECT\s+\*', optimized, re.IGNORECASE):
            tables = self._extract_tables_from_sql(optimized)
            if len(tables) == 1 and tables[0] in self.schema_cache:
                # Get top 5 important columns instead of all columns
                columns = self._get_important_columns(tables[0])
                if columns:
                    # Replace * with specific columns
                    optimized = re.sub(
                        r'\bSELECT\s+\*', 
                        f"SELECT {', '.join(columns)}", 
                        optimized, 
                        flags=re.IGNORECASE
                    )
        
        # Add query hints for large tables
        tables = self._extract_tables_from_sql(optimized)
        for table in tables:
            try:
                row_count = self._get_table_row_count(table)
                if row_count > 10000 and 'WITH (NOLOCK)' not in optimized:
                    # Add NOLOCK hint for read-only queries on large tables
                    optimized = optimized.replace(
                        f"FROM {table}", 
                        f"FROM {table} WITH (NOLOCK)"
                    )
            except Exception:
                pass
                
        return optimized
        
    def _get_important_columns(self, table_name: str, max_columns: int = 5) -> List[str]:
        """Get the most important columns from a table"""
        if table_name not in self.schema_cache:
            return []
            
        columns = []
        
        # Always include primary key columns
        primary_keys = self._get_primary_key_columns(table_name)
        columns.extend(primary_keys)
        
        # Add other important columns up to max_columns
        for col in self.schema_cache[table_name]:
            col_name = col["COLUMN_NAME"]
            # Skip columns already added
            if col_name in columns:
                continue
                
            # Prioritize columns with names like 'name', 'description', 'title', etc.
            important_patterns = ['name', 'description', 'title', 'code', 'id', 'key', 'date']
            if any(pattern in col_name.lower() for pattern in important_patterns):
                columns.append(col_name)
                
            # Stop if we have enough columns
            if len(columns) >= max_columns:
                break
                
        # If we still don't have enough columns, add more until we reach max_columns
        if len(columns) < max_columns:
            for col in self.schema_cache[table_name]:
                col_name = col["COLUMN_NAME"]
                if col_name not in columns:
                    columns.append(col_name)
                    if len(columns) >= max_columns:
                        break
                        
        return columns
        
    def _get_primary_key_columns(self, table_name: str) -> List[str]:
        """Get primary key columns for a table"""
        try:
            query = """
            SELECT 
                c.name AS column_name
            FROM 
                sys.indexes i
            INNER JOIN 
                sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            INNER JOIN 
                sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
            INNER JOIN 
                sys.tables t ON i.object_id = t.object_id
            WHERE 
                t.name = :table_name AND i.is_primary_key = 1
            """
            
            results = self.db_connector.execute_query(query, {"table_name": table_name})
            return [row["column_name"] for row in results]
        except Exception as e:
            logger.error(f"Error getting primary key columns: {e}")
            return []

if __name__ == "__main__":
    # Simple test of the query engine
    try:
        logger.info("Initializing QueryEngine for testing...")
        engine = QueryEngine() # Default instantiation for basic test
        logger.info("QueryEngine initialized successfully.")
        
        test_query = "Show me the count of records in Customers"
        sql, results = engine.process_natural_language_query(test_query)
        print(f"\nProcessed Query: {test_query}")
        print(f"Generated SQL: {sql}")
        print(f"Results: {results}")

    except core_exceptions.SchemaError as se:
        logger.error(f"Failed to initialize QueryEngine due to schema error: {se}")
        print(f"CRITICAL ERROR: Could not initialize QueryEngine. Schema loading failed: {se}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during testing: {e}", exc_info=True)
        print(f"An error occurred during testing: {e}")
