#!/usr/bin/env python3
"""
Enhanced SQL Agent with Vanna.AI Integration
Converts natural language queries to SQL using RAG-based approach
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Vanna.AI imports
try:
    from vanna.ollama import Ollama
    from vanna.chromadb import ChromaDB_VectorStore
    from vanna.base import VannaBase
except ImportError:
    print("Vanna.AI not installed. Please run: pip install vanna")
    sys.exit(1)

# Database and utility imports
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sql_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sql_agent")

class VannaSQL(ChromaDB_VectorStore, Ollama):
    """Custom Vanna class combining ChromaDB vector store with Ollama LLM"""
    
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

class EnhancedSQLAgent:
    """Enhanced SQL Agent with AI-powered natural language to SQL conversion"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Enhanced SQL Agent"""
        self.logger = logging.getLogger("sql_agent")
        self.logger.info("Initializing Enhanced SQL Agent with Vanna.AI")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize database connection
        self.engine = self._create_database_engine()
        
        # Initialize Vanna.AI
        self.vanna = self._initialize_vanna()
        
        # Training status
        self.is_trained = False
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment variables"""
        load_dotenv()
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "database": {
                "server": os.getenv("DB_SERVER", "a265m001"),
                "database": os.getenv("DB_NAME", "QADEE2798"),
                "username": os.getenv("DB_USERNAME", "PowerBI"),
                "password": os.getenv("DB_PASSWORD", "P0werB1"),
                "driver": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
            },
            "vanna": {
                "model": os.getenv("OLLAMA_MODEL", "llama3"),
                "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.1")),
                "chroma_path": os.getenv("CHROMA_PATH", "./chroma_db")
            }
        }
    
    def _create_database_engine(self) -> sa.Engine:
        """Create SQLAlchemy database engine"""
        db_config = self.config["database"]
        
        connection_string = (
            f"mssql+pyodbc://{db_config['username']}:{db_config['password']}"
            f"@{db_config['server']}/{db_config['database']}"
            f"?driver={db_config['driver'].replace(' ', '+')}"
        )
        
        try:
            engine = create_engine(connection_string, echo=False)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.logger.info("Database connection established successfully")
            return engine
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _initialize_vanna(self) -> VannaSQL:
        """Initialize Vanna.AI with Ollama and ChromaDB"""
        vanna_config = self.config["vanna"]
        
        try:
            vanna = VannaSQL(config={
                'model': vanna_config['model'],
                'temperature': vanna_config['temperature'],
                'path': vanna_config['chroma_path']
            })
            
            # Connect to database
            vanna.connect_to_mssql(
                odbc_conn_str=self._get_odbc_connection_string()
            )
            
            self.logger.info("Vanna.AI initialized successfully")
            return vanna
        except Exception as e:
            self.logger.error(f"Failed to initialize Vanna.AI: {e}")
            raise
    
    def _get_odbc_connection_string(self) -> str:
        """Get ODBC connection string for Vanna"""
        db_config = self.config["database"]
        return (
            f"DRIVER={{{db_config['driver']}}};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']}"
        )
    
    def extract_database_schema(self) -> Dict[str, Any]:
        """Extract database schema information"""
        self.logger.info("Extracting database schema...")
        
        schema_info = {
            "tables": {},
            "relationships": []
        }
        
        try:
            with self.engine.connect() as conn:
                # Get table information
                tables_query = """
                SELECT 
                    TABLE_NAME,
                    TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
                """
                
                tables_result = conn.execute(text(tables_query))
                
                for table_row in tables_result:
                    table_name = table_row[0]
                    
                    # Get column information for each table
                    columns_query = """
                    SELECT 
                        COLUMN_NAME,
                        DATA_TYPE,
                        IS_NULLABLE,
                        COLUMN_DEFAULT,
                        CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = :table_name
                    ORDER BY ORDINAL_POSITION
                    """
                    
                    columns_result = conn.execute(text(columns_query), {"table_name": table_name})
                    
                    columns = []
                    for col_row in columns_result:
                        columns.append({
                            "name": col_row[0],
                            "type": col_row[1],
                            "nullable": col_row[2] == "YES",
                            "default": col_row[3],
                            "max_length": col_row[4]
                        })
                    
                    schema_info["tables"][table_name] = {
                        "columns": columns,
                        "type": "BASE TABLE"
                    }
                
                # Get foreign key relationships
                fk_query = """
                SELECT 
                    fk.name AS FK_NAME,
                    tp.name AS PARENT_TABLE,
                    cp.name AS PARENT_COLUMN,
                    tr.name AS REFERENCED_TABLE,
                    cr.name AS REFERENCED_COLUMN
                FROM sys.foreign_keys fk
                INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
                INNER JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
                INNER JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
                INNER JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
                INNER JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
                """
                
                fk_result = conn.execute(text(fk_query))
                
                for fk_row in fk_result:
                    schema_info["relationships"].append({
                        "fk_name": fk_row[0],
                        "parent_table": fk_row[1],
                        "parent_column": fk_row[2],
                        "referenced_table": fk_row[3],
                        "referenced_column": fk_row[4]
                    })
                
                self.logger.info(f"Extracted schema for {len(schema_info['tables'])} tables")
                return schema_info
                
        except Exception as e:
            self.logger.error(f"Error extracting database schema: {e}")
            raise
    
    def generate_ddl_from_schema(self, schema_info: Dict[str, Any]) -> List[str]:
        """Generate DDL statements from schema information"""
        ddl_statements = []
        
        for table_name, table_info in schema_info["tables"].items():
            columns_ddl = []
            
            for column in table_info["columns"]:
                col_def = f"[{column['name']}] {column['type']}"
                
                if column['max_length']:
                    col_def += f"({column['max_length']})"
                
                if not column['nullable']:
                    col_def += " NOT NULL"
                
                if column['default']:
                    col_def += f" DEFAULT {column['default']}"
                
                columns_ddl.append(col_def)
            
            ddl = f"CREATE TABLE [{table_name}] (\n    " + ",\n    ".join(columns_ddl) + "\n)"
            ddl_statements.append(ddl)
        
        return ddl_statements
    
    def train_vanna(self, training_data_path: Optional[str] = None):
        """Train Vanna.AI with database schema and examples"""
        self.logger.info("Training Vanna.AI with database knowledge...")
        
        try:
            # Extract and train with database schema
            schema_info = self.extract_database_schema()
            ddl_statements = self.generate_ddl_from_schema(schema_info)
            
            # Train with DDL statements
            for ddl in ddl_statements:
                self.vanna.train(ddl=ddl)
                self.logger.debug(f"Trained with DDL: {ddl[:100]}...")
            
            # Train with example queries if available
            if training_data_path and Path(training_data_path).exists():
                self._train_with_examples(training_data_path)
            else:
                # Use built-in example queries
                self._train_with_builtin_examples()
            
            # Train with business documentation
            self._train_with_business_context()
            
            self.is_trained = True
            self.logger.info("Vanna.AI training completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error training Vanna.AI: {e}")
            raise
    
    def _train_with_examples(self, examples_path: str):
        """Train with example queries from file"""
        try:
            with open(examples_path, 'r') as f:
                examples = json.load(f)
            
            for example in examples:
                if 'sql' in example:
                    self.vanna.train(sql=example['sql'])
                if 'question' in example and 'sql' in example:
                    self.vanna.train(question=example['question'], sql=example['sql'])
                    
        except Exception as e:
            self.logger.error(f"Error training with examples: {e}")
    
    def _train_with_builtin_examples(self):
        """Train with built-in example queries for QADEE2798 database"""
        examples = [
            "SELECT TOP 10 * FROM so_mstr ORDER BY so_nbr DESC",
            "SELECT COUNT(*) FROM pt_mstr WHERE pt_status = 'Active'",
            "SELECT so_cust, COUNT(*) as order_count FROM so_mstr GROUP BY so_cust ORDER BY order_count DESC",
            "SELECT p.pt_part, p.pt_desc, SUM(t.tr_qty_loc) as total_qty FROM pt_mstr p LEFT JOIN tr_hist t ON p.pt_part = t.tr_part GROUP BY p.pt_part, p.pt_desc",
            "SELECT a.ad_name, COUNT(s.so_nbr) as sales_orders FROM ad_mstr a LEFT JOIN so_mstr s ON a.ad_addr = s.so_cust GROUP BY a.ad_name"
        ]
        
        for sql in examples:
            self.vanna.train(sql=sql)
    
    def _train_with_business_context(self):
        """Train with business context and documentation"""
        business_docs = [
            "The QADEE2798 database contains manufacturing and sales data including sales orders (so_mstr), parts master (pt_mstr), transaction history (tr_hist), and address master (ad_mstr).",
            "Sales orders are stored in so_mstr table with so_nbr as primary key and so_cust linking to customer addresses in ad_mstr.",
            "Parts information is in pt_mstr with pt_part as the part number and pt_desc as description.",
            "Transaction history in tr_hist tracks inventory movements with tr_part linking to pt_mstr.",
            "Address master ad_mstr contains customer and vendor information with ad_addr as primary key."
        ]
        
        for doc in business_docs:
            self.vanna.train(documentation=doc)
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Process a natural language question and return SQL + results"""
        if not self.is_trained:
            self.logger.warning("Vanna.AI not trained yet. Training now...")
            self.train_vanna()
        
        try:
            self.logger.info(f"Processing question: {question}")
            
            # Generate SQL using Vanna
            sql = self.vanna.generate_sql(question)
            
            if not sql:
                return {
                    "question": question,
                    "sql": None,
                    "results": None,
                    "error": "Could not generate SQL for this question"
                }
            
            # Execute the SQL
            try:
                df = self.vanna.run_sql(sql)
                
                return {
                    "question": question,
                    "sql": sql,
                    "results": df,
                    "error": None,
                    "row_count": len(df) if df is not None else 0
                }
                
            except Exception as e:
                return {
                    "question": question,
                    "sql": sql,
                    "results": None,
                    "error": f"SQL execution error: {str(e)}"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing question: {e}")
            return {
                "question": question,
                "sql": None,
                "results": None,
                "error": f"Processing error: {str(e)}"
            }
    
    def get_training_data(self) -> List[Dict[str, Any]]:
        """Get current training data from Vanna"""
        try:
            return self.vanna.get_training_data()
        except Exception as e:
            self.logger.error(f"Error getting training data: {e}")
            return []
    
    def save_training_data(self, filepath: str):
        """Save current training data to file"""
        try:
            training_data = self.get_training_data()
            with open(filepath, 'w') as f:
                json.dump(training_data, f, indent=2, default=str)
            self.logger.info(f"Training data saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving training data: {e}")

def main():
    """Main function for testing the SQL Agent"""
    agent = EnhancedSQLAgent()
    
    # Train the agent
    print("Training the SQL Agent...")
    agent.train_vanna()
    
    # Interactive mode
    print("\nSQL Agent ready! Ask questions about your database (type 'quit' to exit):")
    
    while True:
        question = input("\nQuestion: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            continue
        
        result = agent.ask_question(question)
        
        print(f"\nSQL Generated: {result['sql']}")
        
        if result['error']:
            print(f"Error: {result['error']}")
        else:
            print(f"Results ({result['row_count']} rows):")
            if result['results'] is not None and not result['results'].empty:
                print(result['results'].head(10).to_string())
            else:
                print("No results returned")

if __name__ == "__main__":
    main()
