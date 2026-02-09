#!/usr/bin/env python3
"""
Training Data Extractor for SQL Agent
Extracts training data from the existing QADEE2798 database documentation
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingDataExtractor:
    """Extracts training data from QADEE2798 database documentation"""
    
    def __init__(self, repo_path: str = "./existing_repo"):
        self.repo_path = Path(repo_path)
        self.db_docs_path = self.repo_path / "Database_tables" / "QADEE2798"
        
    def extract_all_training_data(self) -> Dict[str, Any]:
        """Extract all available training data"""
        training_data = {
            "ddl_statements": [],
            "example_queries": [],
            "business_documentation": [],
            "column_definitions": {},
            "table_relationships": []
        }
        
        # Extract from various documentation files
        training_data["business_documentation"].extend(self._extract_business_context())
        training_data["example_queries"].extend(self._extract_example_queries())
        training_data["column_definitions"].update(self._extract_column_definitions())
        training_data["table_relationships"].extend(self._extract_table_relationships())
        
        return training_data
    
    def _extract_business_context(self) -> List[str]:
        """Extract business context from documentation files"""
        business_docs = []
        
        # From database summary
        summary_file = self.db_docs_path / "database_summary.md"
        if summary_file.exists():
            content = summary_file.read_text(encoding='utf-8')
            
            # Extract table descriptions
            table_descriptions = self._extract_table_descriptions(content)
            business_docs.extend(table_descriptions)
            
            # Extract common query patterns
            patterns = self._extract_query_patterns(content)
            business_docs.extend(patterns)
        
        # From data lineage
        lineage_file = self.db_docs_path / "data_lineage.md"
        if lineage_file.exists():
            content = lineage_file.read_text(encoding='utf-8')
            lineage_docs = self._extract_lineage_info(content)
            business_docs.extend(lineage_docs)
        
        return business_docs
    
    def _extract_table_descriptions(self, content: str) -> List[str]:
        """Extract table descriptions from database summary"""
        descriptions = []
        
        # Look for table listings with descriptions
        table_pattern = r'`(\w+)`[:\-\s]*([^`\n]+)'
        matches = re.findall(table_pattern, content)
        
        for table_name, description in matches:
            if len(description.strip()) > 10:  # Filter out very short descriptions
                descriptions.append(f"Table {table_name}: {description.strip()}")
        
        return descriptions
    
    def _extract_query_patterns(self, content: str) -> List[str]:
        """Extract common query patterns"""
        patterns = []
        
        # Look for query pattern sections
        pattern_section = re.search(r'Common Query Patterns.*?(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if pattern_section:
            pattern_text = pattern_section.group(0)
            
            # Extract individual patterns
            pattern_items = re.findall(r'[-*]\s*([^-*\n]+)', pattern_text)
            for pattern in pattern_items:
                if len(pattern.strip()) > 10:
                    patterns.append(f"Common query pattern: {pattern.strip()}")
        
        return patterns
    
    def _extract_lineage_info(self, content: str) -> List[str]:
        """Extract data lineage information"""
        lineage_docs = []
        
        # Extract data flow descriptions
        flow_pattern = r'(\w+)\s*->\s*(\w+)[:\s]*([^->\n]+)'
        matches = re.findall(flow_pattern, content)
        
        for source, target, description in matches:
            lineage_docs.append(f"Data flows from {source} to {target}: {description.strip()}")
        
        return lineage_docs
    
    def _extract_example_queries(self) -> List[Dict[str, str]]:
        """Extract example SQL queries"""
        examples = []
        
        # From query_examples.md
        examples_file = self.db_docs_path / "query_examples.md"
        if examples_file.exists():
            content = examples_file.read_text(encoding='utf-8')
            examples.extend(self._parse_sql_examples(content))
        
        # From custom_queries.md
        custom_file = self.db_docs_path / "custom_queries.md"
        if custom_file.exists():
            content = custom_file.read_text(encoding='utf-8')
            examples.extend(self._parse_custom_queries(content))
        
        return examples
    
    def _parse_sql_examples(self, content: str) -> List[Dict[str, str]]:
        """Parse SQL examples from markdown content"""
        examples = []
        
        # Look for SQL code blocks
        sql_blocks = re.findall(r'```sql\n(.*?)\n```', content, re.DOTALL)
        
        for sql in sql_blocks:
            sql = sql.strip()
            if sql and len(sql) > 20:  # Filter out very short queries
                examples.append({
                    "sql": sql,
                    "description": "Example query from documentation"
                })
        
        return examples
    
    def _parse_custom_queries(self, content: str) -> List[Dict[str, str]]:
        """Parse custom queries from documentation"""
        examples = []
        
        # Look for query names and descriptions
        query_pattern = r'###?\s*([^#\n]+)\n(.*?)(?=###?|\Z)'
        matches = re.findall(query_pattern, content, re.DOTALL)
        
        for query_name, description in matches:
            # Look for SQL in the description
            sql_match = re.search(r'```sql\n(.*?)\n```', description, re.DOTALL)
            if sql_match:
                sql = sql_match.group(1).strip()
                examples.append({
                    "sql": sql,
                    "description": f"{query_name.strip()}: {description[:200]}..."
                })
        
        return examples
    
    def _extract_column_definitions(self) -> Dict[str, Any]:
        """Extract column definitions and business rules"""
        definitions = {}
        
        # From Column_prompts.md
        prompts_file = self.db_docs_path / "Column_prompts.md"
        if prompts_file.exists():
            content = prompts_file.read_text(encoding='utf-8')
            definitions.update(self._parse_column_prompts(content))
        
        # From data_dictionary.md
        dict_file = self.db_docs_path / "data_dictionary.md"
        if dict_file.exists():
            content = dict_file.read_text(encoding='utf-8')
            definitions.update(self._parse_data_dictionary(content))
        
        return definitions
    
    def _parse_column_prompts(self, content: str) -> Dict[str, str]:
        """Parse column calculation rules from Column_prompts.md"""
        definitions = {}
        
        # Look for column definitions with rules
        column_pattern = r'\[([^\]]+)\][:\s]*([^[\n]+)'
        matches = re.findall(column_pattern, content)
        
        for column_name, rule in matches:
            if len(rule.strip()) > 10:
                definitions[column_name] = rule.strip()
        
        return definitions
    
    def _parse_data_dictionary(self, content: str) -> Dict[str, str]:
        """Parse data dictionary for column descriptions"""
        definitions = {}
        
        # Look for table sections and column information
        table_sections = re.split(r'##\s+Table:', content)
        
        for section in table_sections[1:]:  # Skip first empty section
            lines = section.split('\n')
            table_name = lines[0].strip() if lines else ""
            
            # Look for column information in tables
            for line in lines:
                if '|' in line and not line.startswith('|---'):
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        col_name = parts[1]
                        if col_name and col_name != 'Field Name':
                            definitions[f"{table_name}.{col_name}"] = f"Column in {table_name}"
        
        return definitions
    
    def _extract_table_relationships(self) -> List[Dict[str, str]]:
        """Extract table relationships"""
        relationships = []
        
        lineage_file = self.db_docs_path / "data_lineage.md"
        if lineage_file.exists():
            content = lineage_file.read_text(encoding='utf-8')
            
            # Look for relationship patterns
            rel_pattern = r'(\w+)\s*(?:->|→)\s*(\w+)'
            matches = re.findall(rel_pattern, content)
            
            for source, target in matches:
                relationships.append({
                    "source_table": source,
                    "target_table": target,
                    "relationship_type": "data_flow"
                })
        
        return relationships
    
    def save_training_data(self, output_file: str = "training_data.json"):
        """Extract and save all training data to JSON file"""
        logger.info("Extracting training data from QADEE2798 documentation...")
        
        training_data = self.extract_all_training_data()
        
        # Add metadata
        training_data["metadata"] = {
            "source": "QADEE2798 database documentation",
            "extracted_at": "2024-01-01",  # You can make this dynamic
            "tables_count": len(set(rel["source_table"] for rel in training_data["table_relationships"])),
            "examples_count": len(training_data["example_queries"]),
            "business_docs_count": len(training_data["business_documentation"])
        }
        
        # Save to file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Training data saved to {output_path}")
        logger.info(f"Extracted: {len(training_data['example_queries'])} SQL examples, "
                   f"{len(training_data['business_documentation'])} business docs, "
                   f"{len(training_data['column_definitions'])} column definitions")
        
        return training_data

def main():
    """Main function to extract training data"""
    extractor = TrainingDataExtractor()
    training_data = extractor.save_training_data()
    
    print("Training data extraction completed!")
    print(f"SQL Examples: {len(training_data['example_queries'])}")
    print(f"Business Documentation: {len(training_data['business_documentation'])}")
    print(f"Column Definitions: {len(training_data['column_definitions'])}")
    print(f"Table Relationships: {len(training_data['table_relationships'])}")

if __name__ == "__main__":
    main()
