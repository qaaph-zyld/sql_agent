#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Index Suggestion Generator Module

This module provides functionality to generate database index suggestions based on
column usage patterns and estimated impact.
"""

import logging
from typing import Dict, List, Any, Optional

# Attempt to import dependent analyzers/estimators
# These imports assume the other modules exist and are in the expected locations.
# For initial development, these might be mocked or their interfaces simplified.
try:
    from scripts.analysis.column_usage_analyzer import ColumnUsageAnalyzer # Placeholder
    from scripts.analysis.index_impact_estimator import IndexImpactEstimator
except ImportError as e:
    logging.warning(f"Could not import all dependencies for IndexSuggestionGenerator: {e}. Functionality may be limited.")
    # Define placeholder classes if imports fail, to allow type hinting and basic structure
    class ColumnUsageAnalyzer:
        def get_column_usage_stats(self) -> Dict[str, List[Dict[str, Any]]]: return {}
    class IndexImpactEstimator:
        def estimate_impact(self, table_name: str, columns: List[str], query_patterns: Optional[List[Dict[str, Any]]] = None) -> tuple[float, str, Dict[str, List[str]]]: return 0.0, "", {}

    # Set them to None as well if you want to check for their presence explicitly later
    # ColumnUsageAnalyzer = None 
    # IndexImpactEstimator = None 

# Configure logging
logger = logging.getLogger(__name__)

class IndexSuggestionGenerator:
    """
    Generates potential database index suggestions.
    """

    def __init__(
        self,
        column_analyzer: Optional[ColumnUsageAnalyzer],
        impact_estimator: Optional[IndexImpactEstimator],
        schema_info: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes the IndexSuggestionGenerator.

        Args:
            column_analyzer: An instance of ColumnUsageAnalyzer providing column usage data.
            impact_estimator: An instance of IndexImpactEstimator for assessing potential indexes.
            schema_info: An optional dictionary containing schema information.
        """
        self.column_analyzer = column_analyzer
        self.impact_estimator = impact_estimator
        self.schema_info = schema_info if schema_info else {}
        if not self.column_analyzer:
            logger.warning("ColumnUsageAnalyzer not provided or failed to import. Suggestion quality will be limited.")
        if not self.impact_estimator:
            logger.warning("IndexImpactEstimator not provided or failed to import. Cannot estimate impact.")
        logger.info("IndexSuggestionGenerator initialized.")

    def generate_suggestions(
        self,
        min_impact_score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Generates index suggestions based on column usage and estimated impact.

        Args:
            min_impact_score_threshold (float): Minimum estimated impact score for an index to be suggested.

        Returns:
            List[Dict[str, Any]]: A list of suggested indexes, each with DDL and impact assessment.
                                  Example: [
                                      {
                                          "table_name": "Users", 
                                          "index_columns": ["email"], 
                                          "ddl": "CREATE INDEX idx_users_email ON Users (email);", 
                                          "estimated_impact_score": 1.2, 
                                          "assessment": "Moderate positive impact",
                                          "details": {...}
                                      }
                                  ]
        """
        if not self.impact_estimator:
            logger.error("IndexImpactEstimator is not available. Cannot estimate impact for suggestions.")
            return []
        
        if not self.column_analyzer:
            logger.error("ColumnUsageAnalyzer is not available. Cannot get column usage data to generate suggestions.")
            return []
        
        column_usage_data = self.column_analyzer.get_column_usage_stats()
        if not column_usage_data:
             logger.warning("No column usage data obtained from ColumnUsageAnalyzer. Cannot generate suggestions.")
             return []

        suggestions = []

        for table_name, usages in column_usage_data.items():
            candidate_single_columns = set()
            candidate_composite_columns = []

            for usage_details in usages: # Renamed 'usage' to 'usage_details' for clarity
                index_columns: Optional[List[str]] = None
                usage_type = usage_details.get("usage_type", "UNKNOWN_USAGE")
                frequency = usage_details.get("frequency", 0)

                # Arbitrary frequency threshold - consider making this configurable
                if frequency <= 5:
                    # logger.debug(f"Skipping usage for table {table_name} due to low frequency: {usage_details}")
                    continue

                # Check for composite index candidate first
                if "columns" in usage_details and isinstance(usage_details["columns"], list) and usage_details["columns"]:
                    # Ensure all elements in 'columns' are strings
                    if all(isinstance(col, str) for col in usage_details["columns"]):
                        index_columns = usage_details["columns"]
                    else:
                        logger.warning(f"Skipping composite usage for table {table_name} due to non-string elements in 'columns': {usage_details}")
                        continue
                # Check for single column index candidate
                elif "column" in usage_details and isinstance(usage_details["column"], str):
                    index_columns = [usage_details["column"]]
                else:
                    logger.warning(f"Skipping usage for table {table_name} due to missing or invalid 'column' or 'columns' key: {usage_details}")
                    continue
                
                if not index_columns: # Should not happen if logic above is correct, but as a safeguard
                    logger.warning(f"Skipping usage for table {table_name} as no valid index columns were derived: {usage_details}")
                    continue

                # Mock query patterns for impact estimation - this would ideally come from column_usage_data details
                # For now, it's a generic pattern. Future: make this more specific based on usage_type.
                mock_query_patterns = [{
                    "type": "SELECT", 
                    "table": table_name, 
                    "clause": "WHERE", # Assuming most indexes are for WHERE, JOIN, ORDER BY, GROUP BY which relate to filtering/sorting
                    "columns": index_columns
                }]
                
                score, assessment, impact_details = self.impact_estimator.estimate_impact(
                    table_name, index_columns, query_patterns=mock_query_patterns
                )

                # The 'assessment' from impact_estimator is a string like "High positive impact"
                # The 'impact_details' contains 'positive_factors' and 'negative_factors'
                positive_factors = impact_details.get("positive_factors", [])
                # negative_factors = impact_details.get("negative_factors", []) # Not currently used in reasoning string

                if score >= min_impact_score_threshold:
                    index_name_suffix = '_'.join(index_columns).lower() # ensure lowercase for consistency
                    columns_ddl_part = ', '.join(index_columns)
                    
                    reasoning_parts = [f"Potential positive impact based on heuristic score ({score:.2f})."]
                    reasoning_parts.append(f"Usage Type: {usage_type} (Frequency: {frequency}).")
                    if positive_factors:
                        reasoning_parts.append(f"Positive Factors: {', '.join(positive_factors)}.")
                    # if negative_factors:
                    #     reasoning_parts.append(f"Negative Factors: {', '.join(negative_factors)}.")

                    suggestions.append({
                        "table_name": table_name,
                        "index_columns": index_columns,
                        "index_type": "COMPOSITE" if len(index_columns) > 1 else "SINGLE_COLUMN",
                        "reasoning": ' '.join(reasoning_parts),
                        "assessment": assessment, 
                        "estimated_impact_score": score,
                        "ddl_statement": f"CREATE INDEX idx_{table_name.lower()}_{index_name_suffix} ON {table_name} ({columns_ddl_part});",
                        "metrics": {
                            "frequency": frequency,
                            "selectivity": usage_details.get("selectivity"),
                            "distinct_values": usage_details.get("distinct_values")
                        },
                        "raw_usage_details": usage_details 
                    })

        logger.info(f"Generated {len(suggestions)} index suggestions.")
        return suggestions

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Mock schema_info and instantiate analyzers for testing
    mock_schema_info = {
        "tables": {
            "Users": {"row_count": 100000, "columns": ["id", "email", "status", "registration_date"]},
            "Orders": {"row_count": 2000000, "columns": ["id", "customer_id", "order_date", "total_amount", "product_id"]},
            "Products": {"row_count": 50000, "columns": ["id", "name", "category_id"]}
        }
    }

    # Ensure ColumnUsageAnalyzer and IndexImpactEstimator are available (imported or placeholders)
    if ColumnUsageAnalyzer and IndexImpactEstimator:
        # Instantiate the (placeholder) ColumnUsageAnalyzer
        col_analyzer = ColumnUsageAnalyzer(schema_info=mock_schema_info)
        
        # Instantiate the IndexImpactEstimator
        estimator = IndexImpactEstimator(schema_info=mock_schema_info)
        
        # Instantiate the IndexSuggestionGenerator with the analyzer and estimator
        generator = IndexSuggestionGenerator(
            column_analyzer=col_analyzer, 
            impact_estimator=estimator, 
            schema_info=mock_schema_info
        )

        print("\n--- Generating Index Suggestions (using ColumnUsageAnalyzer) ---")
        # Now, generate_suggestions does not take mock_usage directly
        suggestions = generator.generate_suggestions(min_impact_score_threshold=0.3)
        
        if suggestions:
            for i, sug in enumerate(suggestions):
                print(f"\nSuggestion #{i+1}:")
                print(f"  Table: {sug['table_name']}")
                print(f"  Columns: {sug['index_columns']}")
                print(f"  DDL: {sug['ddl_statement']}")
                print(f"  Score: {sug['estimated_impact_score']:.2f}")
                print(f"  Assessment: {sug['reasoning']}")
                print(f"  Assessment: {sug['assessment']}")
                # print(f"  Details: {sug['details']}") # Can be verbose
        else:
            print("No index suggestions generated with the current criteria.")
    else:
        print("ColumnUsageAnalyzer or IndexImpactEstimator not available, cannot run IndexSuggestionGenerator example.")
