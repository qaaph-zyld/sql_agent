#!/usr/bin/env python3
"""
Schema Analyzer - Database schema analysis and documentation tool
"""

import os
import sys
import json
import csv
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent.parent / "logs" / "schema_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("schema_analyzer")

class SchemaAnalyzer:
    """Database schema analysis and documentation tool"""
    
    def __init__(self, database_dir: str):
        """
        Initialize schema analyzer
        
        Args:
            database_dir: Path to directory containing database schema files
        """
        self.database_dir = Path(database_dir)
        self.changelog_engine = ChangelogEngine()
        self.tables = {}
        self.relationships = []
        self.start_time = time.time()
        
    def analyze_schema(self) -> Dict[str, Any]:
        """
        Analyze database schema and return schema information
        
        Returns:
            Dictionary containing schema information
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            "Analyzing database schema",
            ["Scanning database directory", "Extracting table structures", "Identifying relationships"],
            []
        )
        
        logger.info(f"Analyzing schema in {self.database_dir}")
        
        # Extract tables and their structures
        tables = self._extract_tables()
        
        # Load database summary if available
        database_summary = self._load_database_summary()
        
        # Load relationships
        relationships = self._load_relationships()
        
        # Analyze query patterns
        query_patterns = self._analyze_query_patterns()
        
        # Load performance recommendations
        performance_recommendations = self._load_performance_recommendations()
        
        # Calculate execution time
        execution_time_ms = (time.time() - self.start_time) * 1000
        
        # Basic schema info
        schema_info = {
            "database_name": self.database_dir.name,
            "table_count": len(tables),
            "tables": tables,
            "relationships": relationships,
            "summary": database_summary,
            "query_patterns": query_patterns,
            "performance_recommendations": performance_recommendations,
            "execution_time_ms": execution_time_ms,
            "analyzed_at": self._get_current_timestamp()
        }
        
        logger.info(f"Found {len(tables)} tables in {self.database_dir.name}")
        
        # Post-Response: System validation
        self._update_changelog(schema_info)
        
        # Run validation
        try:
            from scripts.core.validation_suite import ValidationSuite
            validator = ValidationSuite()
            validation_results = validator.run_validation()
            logger.info(f"Validation results: {validation_results}")
        except Exception as e:
            logger.error(f"Error running validation: {e}")
        
        return schema_info
    
    def _extract_tables(self) -> Dict[str, Dict[str, Any]]:
        """Extract tables and their structures"""
        tables = {}
        
        # Find all table directories
        for item in self.database_dir.iterdir():
            if item.is_dir() and item.name.startswith("dbo."):
                table_name = item.name[4:]  # Remove "dbo." prefix
                logger.info(f"Found table: {table_name}")
                
                # Extract table structure
                table_info = self._extract_table_structure(item, table_name)
                if table_info:
                    tables[table_name] = table_info
                    
        return tables
        
    def _extract_table_structure(self, table_dir: Path, table_name: str) -> Dict[str, Any]:
        """Extract table structure from table directory"""
        table_info = {
            "name": table_name,
            "columns": [],
            "description": ""
        }
        
        # Look for field names file
        field_names_file = table_dir / f"{table_name}_field_names.md"
        if field_names_file.exists():
            try:
                with open(field_names_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Extract columns from markdown table
                columns = []
                in_table = False
                for line in content.split("\n"):
                    if line.startswith("|") and "---" in line:
                        in_table = True
                        continue
                        
                    if in_table and line.startswith("|"):
                        parts = [p.strip() for p in line.split("|")
                                if p.strip()]
                        if len(parts) >= 3:
                            column = {
                                "name": parts[0].strip(),
                                "type": parts[1].strip() if len(parts) > 1 else "",
                                "description": parts[2].strip() if len(parts) > 2 else ""
                            }
                            columns.append(column)
                            
                table_info["columns"] = columns
                
                # Extract description
                import re
                description_match = re.search(r"# (.+?)\n", content)
                if description_match:
                    table_info["description"] = description_match.group(1).strip()
                    
            except Exception as e:
                logger.error(f"Error extracting table structure for {table_name}: {e}")
                
        return table_info
    
    def _load_database_summary(self) -> Dict[str, Any]:
        """Load database summary from markdown file"""
        summary_path = self.database_dir / "database_summary.md"
        
        if not summary_path.exists():
            logger.warning(f"Database summary file not found: {summary_path}")
            return {}
            
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract sections
            sections = {}
            current_section = "overview"
            sections[current_section] = []
            
            for line in content.split("\n"):
                if line.startswith("## "):
                    current_section = line[3:].strip().lower().replace(" ", "_")
                    sections[current_section] = []
                else:
                    sections[current_section].append(line)
                    
            # Convert sections to text
            for section, lines in sections.items():
                sections[section] = "\n".join(lines).strip()
                
            return sections
        except Exception as e:
            logger.error(f"Error loading database summary: {e}")
            return {}
            
    def _load_relationships(self) -> List[Dict[str, Any]]:
        """Load relationships from inferred_relationships.csv"""
        relationships = []
        relationships_file = self.database_dir / "inferred_relationships.csv"
        
        if not relationships_file.exists():
            logger.warning(f"Relationships file not found: {relationships_file}")
            return []
            
        try:
            with open(relationships_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    relationships.append(dict(row))
                    
            return relationships
        except Exception as e:
            logger.error(f"Error loading relationships: {e}")
            return []
            
    def _analyze_query_patterns(self) -> Dict[str, Any]:
        """Analyze query patterns from custom_queries.md"""
        patterns = {
            "common_joins": [],
            "common_filters": [],
            "common_aggregations": []
        }
        
        queries_file = self.database_dir / "custom_queries.md"
        if not queries_file.exists():
            logger.warning(f"Custom queries file not found: {queries_file}")
            return patterns
            
        try:
            with open(queries_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract SQL queries
            sql_blocks = re.findall(r"```sql\n(.*?)\n```", content, re.DOTALL)
            
            # Analyze join patterns
            join_pattern = re.compile(r"JOIN\s+(\[?[\w\.\[\]]+\]?)\s+(?:AS\s+)?(\w+)?", re.IGNORECASE)
            for sql in sql_blocks:
                joins = join_pattern.findall(sql)
                for table, alias in joins:
                    if table not in [j["table"] for j in patterns["common_joins"]]:
                        patterns["common_joins"].append({
                            "table": table,
                            "alias": alias
                        })
                        
            # Analyze filter patterns
            where_pattern = re.compile(r"WHERE\s+(.*?)(?:GROUP BY|ORDER BY|HAVING|$)", re.IGNORECASE | re.DOTALL)
            for sql in sql_blocks:
                where_matches = where_pattern.findall(sql)
                for where_clause in where_matches:
                    conditions = where_clause.split("AND")
                    for condition in conditions:
                        condition = condition.strip()
                        if condition and condition not in patterns["common_filters"]:
                            patterns["common_filters"].append(condition)
                            
            # Analyze aggregation patterns
            agg_pattern = re.compile(r"(COUNT|SUM|AVG|MIN|MAX)\s*\(\s*([^)]+)\s*\)", re.IGNORECASE)
            for sql in sql_blocks:
                aggs = agg_pattern.findall(sql)
                for agg_type, column in aggs:
                    agg_info = {
                        "type": agg_type.upper(),
                        "column": column.strip()
                    }
                    if agg_info not in patterns["common_aggregations"]:
                        patterns["common_aggregations"].append(agg_info)
                        
            return patterns
        except Exception as e:
            logger.error(f"Error analyzing query patterns: {e}")
            return patterns
            
    def _load_performance_recommendations(self) -> List[str]:
        """Load performance recommendations from performance_recommendations.md"""
        recommendations = []
        recommendations_file = self.database_dir / "performance_recommendations.md"
        
        if not recommendations_file.exists():
            logger.warning(f"Performance recommendations file not found: {recommendations_file}")
            return []
            
        try:
            with open(recommendations_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract recommendations
            rec_pattern = re.compile(r"[*-]\s+(.*?)(?:\n|$)")
            recommendations = rec_pattern.findall(content)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error loading performance recommendations: {e}")
            return []
    
    def _update_changelog(self, schema_info: Dict[str, Any]) -> None:
        """Update changelog with schema analysis results"""
        # Prepare changelog entry
        action_summary = f"Database Schema Analysis for {schema_info['database_name']}"
        
        # Prepare changes made
        changes_made = [
            f"Analyzed {len(schema_info['tables'])} tables in {schema_info['database_name']}",
            f"Identified {len(schema_info['relationships'])} relationships between tables",
            f"Analyzed query patterns and identified {len(schema_info['query_patterns']['common_joins'])} common joins",
            f"Extracted {len(schema_info['performance_recommendations'])} performance recommendations"
        ]
        
        # Prepare files affected
        files_affected = [
            {
                "file_path": str(self.database_dir / "database_summary.md"),
                "change_type": ChangeType.READ,
                "operation": "Read database summary",
                "impact_level": "LOW"
            },
            {
                "file_path": str(self.database_dir / "inferred_relationships.csv"),
                "change_type": ChangeType.READ,
                "operation": "Read inferred relationships",
                "impact_level": "LOW"
            },
            {
                "file_path": str(self.database_dir / "custom_queries.md"),
                "change_type": ChangeType.READ,
                "operation": "Analyzed query patterns",
                "impact_level": "MEDIUM"
            },
            {
                "file_path": str(self.database_dir / "performance_recommendations.md"),
                "change_type": ChangeType.READ,
                "operation": "Extracted performance recommendations",
                "impact_level": "MEDIUM"
            }
        ]
        
        # Prepare technical decisions
        technical_decisions = [
            "Used regex pattern matching to extract table structures from markdown files",
            "Analyzed SQL queries to identify common join patterns and filter conditions",
            "Extracted performance recommendations from documentation",
            "Integrated with changelog system for automated documentation"
        ]
        
        # Prepare next actions
        next_actions = [
            "Generate comprehensive schema documentation",
            "Create query templates based on common patterns",
            "Implement performance optimizations based on recommendations",
            "Update query engine to leverage schema knowledge"
        ]
        
        # Create answer record
        answer_record = AnswerRecord(
            action_summary=action_summary,
            previous_state=f"Database schema not analyzed",
            current_state=f"Database schema analyzed with {len(schema_info['tables'])} tables and {len(schema_info['relationships'])} relationships",
            changes_made=changes_made,
            files_affected=[ChangeVector(**file) for file in files_affected],
            technical_decisions=technical_decisions,
            next_actions_required=next_actions,
            execution_time_ms=schema_info["execution_time_ms"]
        )
        
        # Update changelog
        self.changelog_engine.update_changelog(answer_record)
        
        logger.info(f"Updated changelog with schema analysis results")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()

if __name__ == "__main__":
    # Check if database directory is provided
    if len(sys.argv) < 2:
        print("Usage: python schema_analyzer.py <database_dir>")
        sys.exit(1)
        
    # Get database directory
    database_dir = sys.argv[1]
    
    # Create schema analyzer
    analyzer = SchemaAnalyzer(database_dir)
    
    # Analyze schema
    schema_info = analyzer.analyze_schema()
    
    # Print schema info
    print(json.dumps(schema_info, indent=2))
