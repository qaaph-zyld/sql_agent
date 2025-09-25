#!/usr/bin/env python3
"""
Schema Extractor - Database schema documentation tools
"""

import os
from pathlib import Path
import json
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord
from scripts.db.db_connector import DatabaseConnector

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent.parent / "logs" / "schema_extractor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("schema_extractor")

class SchemaExtractor:
    """Database schema extraction and documentation tools"""
    
    def __init__(self):
        """Initialize schema extractor"""
        self.db_connector = DatabaseConnector()
        self.changelog_engine = ChangelogEngine()
        
    def extract_full_schema(self) -> Dict[str, Any]:
        """
        Extract complete database schema
        
        Returns:
            Dictionary containing complete database schema
        """
        try:
            # Get all table names
            tables = self.db_connector.get_table_names()
            
            # Build schema dictionary
            schema = {
                "database": os.getenv("DB_NAME", "unknown"),
                "tables": {},
                "relationships": self._extract_relationships(),
                "extracted_at": self._get_current_timestamp()
            }
            
            # Extract schema for each table
            for table_name in tables:
                schema["tables"][table_name] = {
                    "columns": self.db_connector.get_table_schema(table_name),
                    "indexes": self._extract_table_indexes(table_name),
                    "row_count": self._get_table_row_count(table_name)
                }
                
            logger.info(f"Extracted complete schema for {len(tables)} tables")
            
            # Update changelog
            self._update_changelog(tables)
            
            return schema
        except Exception as e:
            logger.error(f"Error extracting full schema: {e}")
            raise
            
    def _extract_table_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Extract indexes for a specific table"""
        try:
            query = """
            SELECT 
                i.name AS index_name,
                i.type_desc AS index_type,
                STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS column_names,
                i.is_unique,
                i.is_primary_key
            FROM 
                sys.indexes i
            INNER JOIN 
                sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            INNER JOIN 
                sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
            INNER JOIN 
                sys.tables t ON i.object_id = t.object_id
            WHERE 
                t.name = :table_name
            GROUP BY
                i.name, i.type_desc, i.is_unique, i.is_primary_key
            """
            
            results = self.db_connector.execute_query(query, {"table_name": table_name})
            logger.info(f"Extracted {len(results)} indexes for table {table_name}")
            return results
        except Exception as e:
            logger.error(f"Error extracting indexes for table {table_name}: {e}")
            return []
            
    def _extract_relationships(self) -> List[Dict[str, Any]]:
        """Extract foreign key relationships between tables"""
        try:
            query = """
            SELECT 
                fk.name AS constraint_name,
                pt.name AS parent_table,
                pc.name AS parent_column,
                rt.name AS referenced_table,
                rc.name AS referenced_column
            FROM 
                sys.foreign_keys fk
            INNER JOIN 
                sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            INNER JOIN 
                sys.tables pt ON fkc.parent_object_id = pt.object_id
            INNER JOIN 
                sys.columns pc ON fkc.parent_object_id = pc.object_id AND fkc.parent_column_id = pc.column_id
            INNER JOIN 
                sys.tables rt ON fkc.referenced_object_id = rt.object_id
            INNER JOIN 
                sys.columns rc ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id
            """
            
            results = self.db_connector.execute_query(query)
            logger.info(f"Extracted {len(results)} table relationships")
            return results
        except Exception as e:
            logger.error(f"Error extracting relationships: {e}")
            return []
            
    def _get_table_row_count(self, table_name: str) -> int:
        """Get approximate row count for a table"""
        try:
            query = f"SELECT COUNT(*) AS row_count FROM {table_name}"
            results = self.db_connector.execute_query(query)
            return results[0]["row_count"] if results else 0
        except Exception as e:
            logger.error(f"Error getting row count for table {table_name}: {e}")
            return 0
            
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def save_schema_to_file(self, schema: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Save schema to JSON file
        
        Args:
            schema: Schema dictionary to save
            output_path: Optional output file path
            
        Returns:
            Path to saved schema file
        """
        if output_path is None:
            # Default path in docs directory
            output_path = Path(__file__).parent.parent.parent / "docs" / "database_schema.json"
        else:
            output_path = Path(output_path)
            
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save schema to file
        with open(output_path, "w") as f:
            json.dump(schema, f, indent=2)
            
        logger.info(f"Saved schema to {output_path}")
        return str(output_path)
        
    def generate_schema_documentation(self, schema: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Generate human-readable schema documentation in Markdown format
        
        Args:
            schema: Schema dictionary
            output_path: Optional output file path
            
        Returns:
            Path to saved documentation file
        """
        if output_path is None:
            # Default path in docs directory
            output_path = Path(__file__).parent.parent.parent / "docs" / "database_schema.md"
        else:
            output_path = Path(output_path)
            
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate documentation
        with open(output_path, "w") as f:
            f.write(f"# Database Schema Documentation\n\n")
            f.write(f"Database: {schema['database']}\n\n")
            f.write(f"Generated: {schema['extracted_at']}\n\n")
            
            f.write("## Tables\n\n")
            for table_name, table_info in schema["tables"].items():
                f.write(f"### {table_name}\n\n")
                f.write(f"Row count: {table_info['row_count']}\n\n")
                
                f.write("#### Columns\n\n")
                f.write("| Column Name | Data Type | Length | Nullable | Default |\n")
                f.write("|------------|-----------|--------|----------|--------|\n")
                
                for column in table_info["columns"]:
                    length = column.get("CHARACTER_MAXIMUM_LENGTH", "")
                    if length == -1:
                        length = "MAX"
                    elif length is None:
                        length = ""
                        
                    f.write(f"| {column['COLUMN_NAME']} | {column['DATA_TYPE']} | {length} | {column['IS_NULLABLE']} | {column.get('COLUMN_DEFAULT', '')} |\n")
                
                f.write("\n#### Indexes\n\n")
                f.write("| Index Name | Type | Columns | Unique | Primary Key |\n")
                f.write("|------------|------|---------|--------|------------|\n")
                
                for index in table_info["indexes"]:
                    f.write(f"| {index['index_name']} | {index['index_type']} | {index['column_names']} | {index['is_unique']} | {index['is_primary_key']} |\n")
                
                f.write("\n")
                
            f.write("## Relationships\n\n")
            f.write("| Constraint Name | Parent Table | Parent Column | Referenced Table | Referenced Column |\n")
            f.write("|-----------------|-------------|---------------|-----------------|------------------|\n")
            
            for rel in schema["relationships"]:
                f.write(f"| {rel['constraint_name']} | {rel['parent_table']} | {rel['parent_column']} | {rel['referenced_table']} | {rel['referenced_column']} |\n")
                
        logger.info(f"Generated schema documentation at {output_path}")
        return str(output_path)
        
    def _update_changelog(self, tables: List[str]) -> None:
        """Update changelog with schema extraction details"""
        files_affected = [
            ChangeVector(
                file_path="scripts/db/schema_extractor.py",
                change_type=ChangeType.READ,
                operation="Schema Extraction",
                impact_level="LOW",
                dependencies=["scripts/db/db_connector.py"]
            ),
            ChangeVector(
                file_path="docs/database_schema.json",
                change_type=ChangeType.CREATED,
                operation="Schema Documentation",
                impact_level="MEDIUM",
                dependencies=[]
            ),
            ChangeVector(
                file_path="docs/database_schema.md",
                change_type=ChangeType.CREATED,
                operation="Schema Documentation",
                impact_level="MEDIUM",
                dependencies=[]
            )
        ]
        
        answer_record = AnswerRecord(
            action_summary="Database Schema Extraction and Documentation",
            action_type="Schema Analysis",
            previous_state="Undocumented database schema",
            current_state="Fully documented database schema",
            changes_made=[
                f"Extracted schema for {len(tables)} tables",
                "Generated JSON schema representation",
                "Created human-readable Markdown documentation"
            ],
            files_affected=files_affected,
            technical_decisions=[
                "Used SQL Server system tables for metadata extraction",
                "Generated both machine-readable (JSON) and human-readable (Markdown) documentation",
                "Included table relationships and indexes in documentation"
            ],
            next_actions=[
                "Review schema documentation for completeness",
                "Identify potential optimization opportunities",
                "Use schema information to improve query generation"
            ]
        )
        
        self.changelog_engine.update_changelog(answer_record)
        logger.info("Changelog updated with schema extraction details")

if __name__ == "__main__":
    # Simple test of the schema extractor
    try:
        extractor = SchemaExtractor()
        schema = extractor.extract_full_schema()
        json_path = extractor.save_schema_to_file(schema)
        md_path = extractor.generate_schema_documentation(schema)
        print(f"Schema extracted and saved to {json_path}")
        print(f"Documentation generated at {md_path}")
    except Exception as e:
        print(f"Error testing schema extractor: {e}")
