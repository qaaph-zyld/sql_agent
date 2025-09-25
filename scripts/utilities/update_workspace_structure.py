#!/usr/bin/env python3
"""
Update Workspace Structure - Utility to keep workspace structure documentation current
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

class WorkspaceStructureUpdater:
    def __init__(self, root_path, output_file="workspace_structure_complete.md"):
        self.root_path = Path(root_path)
        self.output_file = Path(output_file) if not output_file.startswith("/") else Path(output_file)
        if not self.output_file.is_absolute():
            self.output_file = self.root_path / self.output_file
        self.ignore_dirs = [".git", "__pycache__", "venv", "env", ".vscode", ".idea", "node_modules"]
        self.ignore_files = [".gitignore", ".env", "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.exe"]
        self.file_count = 0
        self.dir_count = 0
    
    def _should_ignore(self, path):
        """Check if path should be ignored"""
        name = path.name
        
        # Check directory ignores
        if path.is_dir():
            return name in self.ignore_dirs
        
        # Check file ignores
        for pattern in self.ignore_files:
            if pattern.startswith("*"):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern == name:
                return True
        
        return False
    
    def _scan_directory(self, directory, level=0):
        """Recursively scan directory and return markdown structure"""
        if self._should_ignore(directory):
            return ""
        
        path = directory.relative_to(self.root_path) if directory != self.root_path else Path(".")
        
        # For root directory, add header
        if level == 0:
            result = f"# Project Structure: {self.root_path.name}\n\n"
            result += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
            result += "```\n"
        else:
            result = ""
            self.dir_count += 1
        
        # Add directory name with indentation
        indent = "  " * level
        result += f"{indent}[DIR] {path.name}/\n"
        
        # Get all items in directory
        items = list(directory.iterdir())
        
        # Sort items: directories first, then files
        dirs = sorted([item for item in items if item.is_dir()], key=lambda x: x.name.lower())
        files = sorted([item for item in items if item.is_file()], key=lambda x: x.name.lower())
        
        # Process directories
        for dir_item in dirs:
            if not self._should_ignore(dir_item):
                result += self._scan_directory(dir_item, level + 1)
        
        # Process files
        for file_item in files:
            if not self._should_ignore(file_item):
                self.file_count += 1
                file_path = file_item.relative_to(self.root_path)
                file_indent = "  " * (level + 1)
                result += f"{file_indent}[FILE] {file_item.name}\n"
        
        # Close code block for root level
        if level == 0:
            result += "```\n\n"
            result += f"*Total: {self.dir_count} directories, {self.file_count} files*\n\n"
            
            # Add section for key components
            result += "## Key Components\n\n"
            result += "### Core Components\n\n"
            result += "- `scripts/core/changelog_engine.py` - Automated changelog generation and management\n"
            result += "- `scripts/core/validation_suite.py` - System integrity verification and validation\n"
            result += "- `scripts/core/run_validation.py` - Validation execution and reporting\n\n"
            
            result += "### Database Components\n\n"
            result += "- `scripts/db/db_connector.py` - Database connection and query execution\n"
            result += "- `scripts/db/query_engine.py` - Natural language to SQL conversion\n"
            result += "- `scripts/db/schema_extractor.py` - Database schema extraction and documentation\n\n"
            
            result += "### Utilities\n\n"
            result += "- `scripts/utilities/generate_changelog_entry.py` - Interactive changelog entry creation\n"
            result += "- `scripts/utilities/update_workspace_structure.py` - This utility\n"
            result += "- `scripts/utilities/schedule_maintenance.py` - Automated maintenance scheduling\n"
            result += "- `scripts/utilities/update_imports.py` - Import statement updater\n"
            result += "- `scripts/utilities/cleanup_original_files.py` - Safe removal of original files\n\n"
            
            result += "### Application\n\n"
            result += "- `app.py` - Main application entry point\n"
            result += "- `.env` - Environment configuration\n"
            result += "- `sample_queries.json` - Example natural language queries\n\n"
            
            result += "### Documentation\n\n"
            result += "- `docs/changelog_integration_plan.md` - Changelog integration details\n"
            result += "- `docs/changelog_system_guide.md` - Guide for using the changelog system\n"
            result += "- `README.md` - Project overview and setup instructions\n"
        
        return result
    
    def update_structure_doc(self):
        """Generate and save workspace structure documentation"""
        content = self._scan_directory(self.root_path)
        self.output_file.write_text(content)
        return content
    
    def update_changelog(self):
        """Update changelog with workspace structure update"""
        engine = ChangelogEngine()
        
        files_affected = [
            ChangeVector(
                file_path=str(self.output_file.relative_to(self.root_path)),
                change_type=ChangeType.DOCS,
                operation="MODIFIED",
                impact_level="LOW",
                dependencies=[]
            )
        ]
        
        record = AnswerRecord(
            answer_id=engine.answer_counter,
            timestamp=datetime.now().isoformat(),
            action_type="Documentation",
            previous_state="Workspace structure documentation outdated",
            current_state="Workspace structure documentation updated",
            changes_made=[
                f"Updated workspace structure documentation with {self.dir_count} directories and {self.file_count} files",
                "Added key components section with descriptions",
                "Generated complete directory tree"
            ],
            files_affected=files_affected,
            technical_decisions=[
                "Automated documentation generation to ensure accuracy",
                "Excluded non-essential directories and files"
            ],
            next_actions=[
                "Review updated documentation for accuracy",
                "Schedule regular updates to maintain documentation currency"
            ]
        )
        
        engine.update_changelog(record)

def main():
    parser = argparse.ArgumentParser(description="Update workspace structure documentation")
    parser.add_argument("--root", type=str, default=".", help="Root directory to scan")
    parser.add_argument("--output", type=str, default="workspace_structure_complete.md", help="Output file path")
    parser.add_argument("--no-changelog", action="store_true", help="Skip changelog update")
    args = parser.parse_args()
    
    updater = WorkspaceStructureUpdater(args.root, args.output)
    content = updater.update_structure_doc()
    
    print(f"Workspace structure documentation updated: {updater.output_file}")
    print(f"Found {updater.dir_count} directories and {updater.file_count} files")
    
    if not args.no_changelog:
        updater.update_changelog()
        print("Changelog updated with workspace structure changes")

if __name__ == "__main__":
    main()
