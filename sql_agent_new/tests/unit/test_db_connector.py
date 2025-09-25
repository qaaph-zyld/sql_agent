"""
Unit tests for the DatabaseConnector class.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sql_agent.core.db_connector import DatabaseConnector

class TestDatabaseConnector(unittest.TestCase):
    """Test cases for the DatabaseConnector class."""
    
    @patch('sql_agent.core.db_connector.create_engine')
    @patch('sql_agent.core.db_connector.load_dotenv')
    def setUp(self, mock_load_dotenv, mock_create_engine):
        """Set up test fixtures before each test method."""
        # Create a mock engine and connection
        self.mock_engine = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine
        
        # Create an instance of DatabaseConnector
        self.connector = DatabaseConnector()
    
    def test_initialization(self):
        """Test that the DatabaseConnector initializes correctly."""
        self.assertIsNotNone(self.connector)
        self.assertIsNotNone(self.connector.engine)
        self.assertIsNotNone(self.connector.config)
    
    @patch('sql_agent.core.db_connector.text')
    def test_execute_query(self, mock_text):
        """Test the execute_query method."""
        # Mock the result
        mock_result = MagicMock()
        mock_result.mappings.return_value = [{'id': 1, 'name': 'test'}]
        self.mock_connection.execute.return_value = mock_result
        
        # Execute a test query
        result = self.connector.execute_query("SELECT * FROM test_table")
        
        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['name'], 'test')
    
    def test_get_table_names(self):
        """Test the get_table_names method."""
        # Mock the inspector
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['table1', 'table2']
        with patch('sql_agent.core.db_connector.inspect', return_value=mock_inspector):
            tables = self.connector.get_table_names()
            self.assertEqual(tables, ['table1', 'table2'])
    
    def test_get_table_schema(self):
        """Test the get_table_schema method."""
        # Mock the inspector
        mock_inspector = MagicMock()
        mock_column = MagicMock()
        mock_column.name = 'test_column'
        mock_column.type = 'VARCHAR'
        mock_column.nullable = True
        mock_inspector.get_columns.return_value = [mock_column]
        
        with patch('sql_agent.core.db_connector.inspect', return_value=mock_inspector):
            schema = self.connector.get_table_schema('test_table')
            self.assertEqual(len(schema), 1)
            self.assertEqual(schema[0]['name'], 'test_column')
            self.assertEqual(schema[0]['type'], 'VARCHAR')

if __name__ == '__main__':
    unittest.main()
