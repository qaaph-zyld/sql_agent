"""
Unit tests for the ChangelogEngine class.
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sql_agent.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

class TestChangelogEngine(unittest.TestCase):
    """Test cases for the ChangelogEngine class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_changelog_path = "test_changelog.md"
        self.changelog = ChangelogEngine(changelog_path=self.test_changelog_path)
        
        # Create a test changelog file
        with open(self.test_changelog_path, 'w', encoding='utf-8') as f:
            f.write("# Changelog\n\n")
    
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_changelog_path):
            os.remove(self.test_changelog_path)
    
    def test_initialization(self):
        """Test that the ChangelogEngine initializes correctly."""
        self.assertEqual(self.changelog.changelog_path, self.test_changelog_path)
        self.assertIsNotNone(self.changelog.session_id)
    
    def test_create_change_vector(self):
        """Test creating a change vector."""
        change = self.changelog._create_change_vector(
            change_type=ChangeType.FILE_MODIFIED,
            file_path="test_file.py",
            description="Test change"
        )
        
        self.assertEqual(change.type, ChangeType.FILE_MODIFIED)
        self.assertEqual(change.file_path, "test_file.py")
        self.assertEqual(change.description, "Test change")
    
    def test_add_answer_record(self):
        """Test adding an answer record to the changelog."""
        # Create a test answer record
        answer_record = AnswerRecord(
            answer_id="test-001",
            question="Test question",
            answer="Test answer",
            changes=[],
            technical_decisions=[],
            next_actions=[]
        )
        
        # Add the answer record
        self.changelog.add_answer_record(answer_record)
        
        # Verify the answer record was added
        self.assertEqual(len(self.changelog.answers), 1)
        self.assertEqual(self.changelog.answers[0].answer_id, "test-001")
    
    @patch('sql_agent.core.changelog_engine.datetime')
    def test_save_changelog(self, mock_datetime):
        """Test saving the changelog to a file."""
        # Mock the current datetime
        from datetime import datetime
        mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0, 0)
        
        # Create a test answer record
        answer_record = AnswerRecord(
            answer_id="test-001",
            question="Test question",
            answer="Test answer",
            changes=[],
            technical_decisions=[],
            next_actions=[]
        )
        
        # Add the answer record and save the changelog
        self.changelog.add_answer_record(answer_record)
        self.changelog.save_changelog()
        
        # Verify the changelog file was created and contains the expected content
        self.assertTrue(os.path.exists(self.test_changelog_path))
        
        with open(self.test_changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn("# Changelog", content)
        self.assertIn("## Answer #test-001", content)
        self.assertIn("### Question", content)
        self.assertIn("Test question", content)
        self.assertIn("### Answer", content)
        self.assertIn("Test answer", content)
        self.assertIn("### Changes", content)
        self.assertIn("### Technical Decisions", content)
        self.assertIn("### Next Actions", content)

if __name__ == "__main__":
    unittest.main()
