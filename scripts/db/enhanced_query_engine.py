#!/usr/bin/env python3
"""
Enhanced Query Engine with Schema Knowledge Integration

This module extends the base query engine with schema knowledge
to improve query generation, validation, and optimization.
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.db.query_engine import QueryEngine
from scripts.analysis.schema_analyzer import SchemaAnalyzer
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord
from scripts.core.user_guidance_manager import UserGuidanceManager

# Configure logging
import logging
logger = logging.getLogger(__name__)

class EnhancedQueryEngine(QueryEngine):
    """
    Enhanced query engine that leverages schema knowledge for improved
    query generation, validation, and optimization.
    """
    
    def __init__(self, database_dir: Optional[str] = None, user_guidance_manager: Optional[UserGuidanceManager] = None):
        """
        Initialize enhanced query engine
        
        Args:
            database_dir: Path to directory containing database schema files
        """
        # Initialize base query engine, passing the UGM instance
        super().__init__(user_guidance_manager=user_guidance_manager)
        self.ugm = user_guidance_manager # Also store it locally if EnhancedQueryEngine needs direct access
        
        # Initialize changelog engine
        self.changelog_engine = ChangelogEngine()
        
        # Set database directory
        if database_dir:
            self.database_dir = Path(database_dir)
        else:
            # Default to QADEE2798 database
            self.database_dir = Path(__file__).parent.parent.parent / "Database_tables" / "QADEE2798"
            
        # Load schema information
        self.schema_info = self._load_schema_info()
        
        # Initialize query templates
        self.query_templates = self._initialize_query_templates()
        
        logger.info(f"Enhanced query engine initialized with schema from {self.database_dir}")
        
    def _initialize_query_templates(self) -> Dict[str, str]:
        """
        Initialize query templates based on schema information
        
        Returns:
            Dictionary of query templates
        """
        templates = {}
        
        if not self.schema_info or "tables" not in self.schema_info:
            logger.warning("No schema information available for templates")
            return templates
            
        # Generate basic templates for each table
        tables = self.schema_info.get("tables", {})
        for table_name, table_info in tables.items():
            # SELECT all template
            templates[f"select_all_{table_name}"] = f"SELECT * FROM {table_name}"
            
            # COUNT template
            templates[f"count_{table_name}"] = f"SELECT COUNT(*) AS count FROM {table_name}"
            
            # If columns are available, create more specific templates
            columns = table_info.get("columns", [])
            if columns:
                # Assume first column might be primary key
                pk_column = columns[0].get("name")
                templates[f"get_{table_name}_by_id"] = f"SELECT * FROM {table_name} WHERE {pk_column} = ?"
                
        # Generate join templates from relationships
        relationships = self.schema_info.get("relationships", [])
        for rel in relationships:
            if "source_table" in rel and "target_table" in rel:
                source = rel["source_table"]
                target = rel["target_table"]
                source_col = rel.get("source_column", "id")
                target_col = rel.get("target_column", f"{source}_id")
                
                templates[f"join_{source}_{target}"] = (
                    f"SELECT * FROM {source} s " 
                    f"JOIN {target} t ON s.{source_col} = t.{target_col}"
                )
                
        # Add templates from common query patterns
        query_patterns = self.schema_info.get("query_patterns", {})
        
        # Common joins
        for i, join in enumerate(query_patterns.get("common_joins", [])):
            table = join.get("table")
            if table:
                templates[f"pattern_join_{i}"] = f"JOIN {table}"
                
        # Common filters
        for i, filter_pattern in enumerate(query_patterns.get("common_filters", [])):
            if filter_pattern:
                templates[f"pattern_filter_{i}"] = f"WHERE {filter_pattern}"
                
        # Common aggregations
        for i, agg in enumerate(query_patterns.get("common_aggregations", [])):
            agg_type = agg.get("type")
            column = agg.get("column")
            if agg_type and column:
                templates[f"pattern_agg_{i}"] = f"SELECT {agg_type}({column}) AS result"
                
        logger.info(f"Initialized {len(templates)} query templates")
        return templates
        
    def _load_schema_info(self) -> Dict[str, Any]:
        """
        Load schema information using schema analyzer
        
        Returns:
            Dictionary containing schema information
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            "Loading schema information for enhanced query engine",
            ["Initializing schema analyzer", "Loading table structures", "Loading relationships"],
            []
        )
        
        # Check if schema analysis results exist
        schema_file = Path(__file__).parent.parent.parent / "schema_analysis_results.json"
        if schema_file.exists():
            try:
                with open(schema_file, "r", encoding="utf-8") as f:
                    schema_info = json.load(f)
                logger.info(f"Loaded schema information from {schema_file}")
                return schema_info
            except Exception as e:
                logger.error(f"Error loading schema information: {e}")
                
        # If schema file doesn't exist or couldn't be loaded, run schema analyzer
        logger.info("Running schema analyzer to generate schema information")
        analyzer = SchemaAnalyzer(str(self.database_dir))
        schema_info = analyzer.analyze_schema()
        
        return schema_info
    
    def generate_sql(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Generate SQL from natural language query with schema knowledge
        
        Args:
            query: Natural language query
            
        Returns:
            Tuple of (SQL query, metadata)
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            "Generating enhanced SQL query",
            ["Analyzing natural language query", "Matching query to schema", "Applying query templates"],
            []
        )
        
        start_time = time.time()
        
        # Try to match query to a template
        template_name, template_sql = self._match_query_to_template(query)
        
        if template_sql:
            # Template matched, use it
            logger.info(f"Using template {template_name} for query")
            sql = template_sql
            metadata = {
                "generation": {
                    "method": "template",
                    "template": template_name,
                    "time_ms": (time.time() - start_time) * 1000
                }
            }
        else:
            # No template match, use base query engine
            logger.info("No template match, using base query generation")
            sql, base_metadata = super().generate_sql(query)
            
            # Enhance the query with schema knowledge
            sql = self._enhance_query_with_schema(sql, query)
            
            metadata = base_metadata
            metadata["generation"]["enhanced"] = True
            metadata["generation"]["time_ms"] = (time.time() - start_time) * 1000
        
        return sql, metadata
        
    def _match_query_to_template(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Match natural language query to a template
        
        Args:
            query: Natural language query
            
        Returns:
            Tuple of (template_name, template_sql) if matched, (None, None) otherwise
        """
        query_lower = query.lower()
        
        # Extract potential table names from query
        tables = self.schema_info.get("tables", {})
        mentioned_tables = []
        
        for table_name in tables.keys():
            if table_name.lower() in query_lower:
                mentioned_tables.append(table_name)
                
        if not mentioned_tables:
            logger.info("No tables mentioned in query")
            return None, None
            
        # Check for count queries
        if re.search(r"count|how many", query_lower):
            for table in mentioned_tables:
                template_name = f"count_{table}"
                if template_name in self.query_templates:
                    return template_name, self.query_templates[template_name]
                    
        # Check for "get all" queries
        if re.search(r"all|list|show", query_lower):
            for table in mentioned_tables:
                template_name = f"select_all_{table}"
                if template_name in self.query_templates:
                    return template_name, self.query_templates[template_name]
                    
        # Check for "get by id" queries
        if re.search(r"by id|where.*id|find.*id", query_lower):
            for table in mentioned_tables:
                template_name = f"get_{table}_by_id"
                if template_name in self.query_templates:
                    return template_name, self.query_templates[template_name]
                    
        # Check for join queries
        if re.search(r"join|combine|related|between", query_lower) and len(mentioned_tables) >= 2:
            # Check all pairs of mentioned tables
            for i, table1 in enumerate(mentioned_tables):
                for table2 in mentioned_tables[i+1:]:
                    template_name = f"join_{table1}_{table2}"
                    if template_name in self.query_templates:
                        return template_name, self.query_templates[template_name]
                        
                    # Check reverse direction
                    template_name = f"join_{table2}_{table1}"
                    if template_name in self.query_templates:
                        return template_name, self.query_templates[template_name]
                        
        # No match found
        return None, None
        
    def _enhance_query_with_schema(self, sql: str, query: str) -> str:
        """
        Enhance SQL query with schema knowledge
        
        Args:
            sql: Original SQL query
            query: Natural language query
            
        Returns:
            Enhanced SQL query
        """
        # Add query as a comment
        sql = f"/* {query} */\n{sql}"
        
        # Add table aliases for better readability
        sql = self._add_table_aliases(sql)
        
        # Add column comments if possible
        sql = self._add_column_comments(sql)
        
        return sql
        
    def _add_table_aliases(self, sql: str) -> str:
        """
        Add table aliases to SQL query for better readability
        
        Args:
            sql: Original SQL query
            
        Returns:
            SQL query with table aliases
        """
        # Extract table names from FROM and JOIN clauses
        from_pattern = re.compile(r"FROM\s+(\w+)(?:\s+AS\s+(\w+))?", re.IGNORECASE)
        join_pattern = re.compile(r"JOIN\s+(\w+)(?:\s+AS\s+(\w+))?", re.IGNORECASE)
        
        # Find all table references without aliases
        from_matches = from_pattern.findall(sql)
        join_matches = join_pattern.findall(sql)
        
        # Add aliases where missing
        for table, alias in from_matches:
            if not alias:
                # Use first letter of table as alias
                new_alias = table[0].lower()
                sql = re.sub(
                    rf"FROM\s+{table}(?!\s+AS)",
                    f"FROM {table} AS {new_alias}",
                    sql,
                    flags=re.IGNORECASE
                )
                
        for table, alias in join_matches:
            if not alias:
                # Use first letter of table as alias
                new_alias = table[0].lower()
                sql = re.sub(
                    rf"JOIN\s+{table}(?!\s+AS)",
                    f"JOIN {table} AS {new_alias}",
                    sql,
                    flags=re.IGNORECASE
                )
                
        return sql
        
    def _add_column_comments(self, sql: str) -> str:
        """
        Add column comments to SQL query
        
        Args:
            sql: Original SQL query
            
        Returns:
            SQL query with column comments
        """
        # Only add comments if we have schema information
        if not self.schema_info or "tables" not in self.schema_info:
            return sql
            
        # Extract column references from query
        column_pattern = re.compile(r"(\w+)\.(\w+)", re.IGNORECASE)
        column_refs = column_pattern.findall(sql)
        
        # Add comments for each column
        comments = []
        for alias, column in column_refs:
            # Find the actual table for this alias
            table_match = re.search(rf"FROM\s+(\w+)\s+(?:AS\s+)?{alias}|JOIN\s+(\w+)\s+(?:AS\s+)?{alias}", sql, re.IGNORECASE)
            if table_match:
                table = table_match.group(1) or table_match.group(2)
                if table in self.schema_info["tables"]:
                    # Find column description
                    for col in self.schema_info["tables"][table].get("columns", []):
                        if col["name"] == column:
                            description = col.get("description", "")
                            if description:
                                comments.append(f"/* {alias}.{column}: {description} */")
                                
        # Add comments at the top of the query
        if comments:
            sql = "\n".join(comments) + "\n" + sql
            
        return sql
        
    def validate_query(self, sql: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate SQL query with schema knowledge
        
        Args:
            sql: SQL query to validate
            
        Returns:
            Tuple of (is_valid, validation_metadata)
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            "Validating SQL query with schema knowledge",
            ["Checking syntax", "Validating table and column names", "Checking for dangerous operations"],
            []
        )
        
        start_time = time.time()
        
        # First use base validation
        is_valid, base_metadata = super().validate_query(sql)
        
        # Additional validation with schema knowledge
        if is_valid and self.schema_info and "tables" in self.schema_info:
            # Extract table names from query
            table_pattern = re.compile(r"FROM\s+(\w+)|JOIN\s+(\w+)", re.IGNORECASE)
            table_matches = table_pattern.findall(sql)
            query_tables = [t[0] or t[1] for t in table_matches if t[0] or t[1]]
            
            # Check if tables exist in schema
            schema_tables = self.schema_info["tables"].keys()
            for table in query_tables:
                if table not in schema_tables:
                    is_valid = False
                    base_metadata["message"] = f"Table '{table}' not found in schema"
                    break
                    
            # If tables are valid, check columns
            if is_valid:
                # Extract column references
                column_pattern = re.compile(r"(\w+)\.(\w+)", re.IGNORECASE)
                column_refs = column_pattern.findall(sql)
                
                for alias, column in column_refs:
                    if column == "*":
                        continue  # Skip wildcard columns
                        
                    # Find the actual table for this alias
                    table_match = re.search(rf"FROM\s+(\w+)\s+(?:AS\s+)?{alias}|JOIN\s+(\w+)\s+(?:AS\s+)?{alias}", sql, re.IGNORECASE)
                    if table_match:
                        table = table_match.group(1) or table_match.group(2)
                        if table in schema_tables:
                            # Check if column exists in table
                            table_columns = [col["name"] for col in self.schema_info["tables"][table].get("columns", [])]
                            if column not in table_columns:
                                is_valid = False
                                base_metadata["message"] = f"Column '{column}' not found in table '{table}'"
                                break
        
        # Add schema validation info to metadata
        base_metadata["schema_validated"] = True
        base_metadata["time_ms"] = (time.time() - start_time) * 1000
        
        return is_valid, base_metadata
        
    def _optimize_query(self, sql: str) -> Tuple[str, Dict[str, Any]]:
        """
        Optimize SQL query with schema knowledge
        
        Args:
            sql: SQL query to optimize
            
        Returns:
            Tuple of (optimized_sql, optimization_metadata)
        """
        start_time = time.time()
        optimized = False
        optimizations = []
        
        # Apply schema-based optimizations
        if self.schema_info:
            # Add index hints if available
            sql, index_hints = self._add_index_hints(sql)
            if index_hints:
                optimized = True
                optimizations.append("Added index hints")
                
            # Add query hints from performance recommendations
            sql, query_hints = self._add_query_hints(sql)
            if query_hints:
                optimized = True
                optimizations.append("Added query hints")
                
        # Return optimization metadata
        optimization_metadata = {
            "optimized": optimized,
            "optimizations": optimizations,
            "time_ms": (time.time() - start_time) * 1000
        }
        
        return sql, optimization_metadata
        
    def _add_index_hints(self, sql: str) -> Tuple[str, List[str]]:
        """
        Add index hints to SQL query based on schema knowledge
        
        Args:
            sql: SQL query to optimize
            
        Returns:
            Tuple of (optimized_sql, index_hints)
        """
        hints = []
        
        # Check if we have performance recommendations
        if not self.schema_info or "performance_recommendations" not in self.schema_info:
            return sql, hints
            
        # Extract table names from query
        table_pattern = re.compile(r"FROM\s+(\w+)|JOIN\s+(\w+)", re.IGNORECASE)
        table_matches = table_pattern.findall(sql)
        query_tables = [t[0] or t[1] for t in table_matches if t[0] or t[1]]
        
        # Get index recommendations for tables in query
        for recommendation in self.schema_info["performance_recommendations"].get("index_recommendations", []):
            table = recommendation.get("table")
            index = recommendation.get("index")
            
            if table in query_tables and index:
                # Add index hint to query
                if "WHERE" in sql:
                    # Add index hint before WHERE clause
                    sql = sql.replace("WHERE", f"USE INDEX ({index}) WHERE")
                    hints.append(f"USE INDEX ({index}) for table {table}")
                else:
                    # Add index hint at the end of the FROM clause
                    sql = re.sub(
                        rf"FROM\s+{table}(?:\s+AS\s+\w+)?",
                        f"FROM {table} USE INDEX ({index})",
                        sql,
                        flags=re.IGNORECASE
                    )
                    hints.append(f"USE INDEX ({index}) for table {table}")
                
        return sql, hints
        
    def _add_query_hints(self, sql: str) -> Tuple[str, List[str]]:
        """
        Add query hints to SQL query based on performance recommendations
        
        Args:
            sql: SQL query to optimize
            
        Returns:
            Tuple of (optimized_sql, query_hints)
        """
        hints = []
        
        # Check if we have performance recommendations
        if not self.schema_info or "performance_recommendations" not in self.schema_info:
            return sql, hints
            
        # Get query optimization hints
        for hint in self.schema_info["performance_recommendations"].get("query_hints", []):
            hint_type = hint.get("type")
            hint_value = hint.get("value")
            
            if hint_type and hint_value:
                # Add hint to query
                if hint_type == "STRAIGHT_JOIN":
                    # Replace SELECT with SELECT STRAIGHT_JOIN
                    if sql.upper().startswith("SELECT"):
                        sql = "SELECT STRAIGHT_JOIN" + sql[6:]
                        hints.append("Added STRAIGHT_JOIN hint")
                elif hint_type == "SQL_BUFFER_RESULT":
                    # Replace SELECT with SELECT SQL_BUFFER_RESULT
                    if sql.upper().startswith("SELECT"):
                        sql = "SELECT SQL_BUFFER_RESULT" + sql[6:]
                        hints.append("Added SQL_BUFFER_RESULT hint")
                elif hint_type == "SQL_CALC_FOUND_ROWS":
                    # Replace SELECT with SELECT SQL_CALC_FOUND_ROWS
                    if sql.upper().startswith("SELECT"):
                        sql = "SELECT SQL_CALC_FOUND_ROWS" + sql[6:]
                        hints.append("Added SQL_CALC_FOUND_ROWS hint")
                
        return sql, hints
        
    def execute_query(self, sql: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Execute SQL query with schema-aware validation and optimization
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Tuple of (results, metadata)
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            "Executing SQL query with schema knowledge",
            ["Validating query against schema", "Optimizing query", "Executing query"],
            []
        )
        
        start_time = time.time()
        
        # Validate query
        is_valid, validation_metadata = self.validate_query(sql)
        
        if not is_valid:
            original_validation_message = validation_metadata['message']
            logger.error(f"Query validation failed: {original_validation_message}")
            
            final_message = original_validation_message
            if self.ugm:
                # Determine context key based on validation message content
                context_key = "error_validation_generic" # Default validation error key
                guidance_params = {"validation_error": original_validation_message, "sql_query": sql}
                
                if "Table '" in original_validation_message and "' not found" in original_validation_message:
                    context_key = "error_validation_table_not_found"
                    # Attempt to extract table name for more specific guidance
                    try:
                        table_name = original_validation_message.split("Table '")[1].split("' not found")[0]
                        guidance_params["table_name"] = table_name
                    except IndexError:
                        pass # Stick to generic if parsing fails
                elif "Column '" in original_validation_message and "' not found" in original_validation_message:
                    context_key = "error_validation_column_not_found"
                    try:
                        column_name = original_validation_message.split("Column '")[1].split("' not found")[0]
                        table_name = original_validation_message.split("in table '")[1].split("'")[0] if "in table '" in original_validation_message else "unknown"
                        guidance_params["column_name"] = column_name
                        guidance_params["table_name"] = table_name
                    except IndexError:
                        pass # Stick to generic if parsing fails

                guidance = self.ugm.get_guidance(context_key, params=guidance_params)
                if guidance:
                    final_message = f"{original_validation_message}\n\n💡 **Guidance:** {guidance}"
                else:
                    logger.info(f"No specific guidance found for key '{context_key}' during validation error.")

            return [], {
                "validation": validation_metadata,
                "status": "ERROR",
                "message": final_message, # Use potentially augmented message
                "total_time_ms": (time.time() - start_time) * 1000
            }
            
        # Optimize query
        optimized_sql, optimization_metadata = self._optimize_query(sql)
        
        # Execute query using base engine
        results, execution_metadata = super().execute_query(optimized_sql)
        
        # Combine metadata
        metadata = {
            "validation": validation_metadata,
            "optimization": optimization_metadata,
            "execution": execution_metadata,
            "total_time_ms": (time.time() - start_time) * 1000
        }
        
        # Post-Response: System validation
        self._update_changelog(sql, optimized_sql, results, metadata)
        
        return results, metadata
        
    def process_query(self, query: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Process natural language query end-to-end
        
        Args:
            query: Natural language query
            
        Returns:
            Tuple of (results, metadata)
        """
        # Generate SQL
        sql, generation_metadata = self.generate_sql(query)
        
        # Execute query
        results, execution_metadata = self.execute_query(sql)
        
        # Combine metadata
        metadata = {
            "query": query,
            "sql": sql,
            "generation": generation_metadata,
            "execution": execution_metadata,
            "total_time_ms": generation_metadata.get("generation", {}).get("time_ms", 0) + 
                             execution_metadata.get("total_time_ms", 0)
        }
        
        return results, metadata
        
    def _update_changelog(self, original_sql: str, optimized_sql: str, results: List[Dict[str, Any]], metadata: Dict[str, Any]) -> None:
        """
        Update changelog with query execution details
        
        Args:
            original_sql: Original SQL query
            optimized_sql: Optimized SQL query
            results: Query results
            metadata: Query metadata
        """
        # Prepare changelog entry
        action_summary = "Executed schema-aware SQL query"
        
        # Prepare changes made
        changes_made = [
            f"Generated SQL query from natural language",
            f"Validated query against schema"
        ]
        
        if original_sql != optimized_sql:
            changes_made.append("Optimized query with schema knowledge")
            
        changes_made.append(f"Executed query returning {len(results)} results")
        
        # Prepare files affected
        files_affected = [
            {
                "file_path": str(self.database_dir / "database_summary.md"),
                "change_type": ChangeType.READ,
                "operation": "Read schema information",
                "impact_level": "LOW"
            }
        ]
        
        # Prepare technical decisions
        technical_decisions = [
            "Used schema knowledge to validate query",
            f"Query generation method: {metadata.get('generation', {}).get('method', 'unknown')}"
        ]
        
        if metadata.get("optimization", {}).get("optimized", False):
            technical_decisions.append("Applied schema-based query optimizations")
            
        # Prepare next actions
        next_actions = [
            "Refine query templates based on usage patterns",
            "Enhance optimization strategies",
            "Update schema information as database evolves"
        ]
        
        # Create answer record
        answer_record = AnswerRecord(
            action_summary=action_summary,
            previous_state="Query not executed",
            current_state=f"Query executed with {len(results)} results",
            changes_made=changes_made,
            files_affected=[ChangeVector(**file) for file in files_affected],
            technical_decisions=technical_decisions,
            next_actions_required=next_actions,
            execution_time_ms=metadata.get("total_time_ms", 0)
        )
        
        # Update changelog
        self.changelog_engine.update_changelog(answer_record)
        
        logger.info("Updated changelog with query execution details")
