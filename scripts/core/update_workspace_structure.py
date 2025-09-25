#!/usr/bin/env python3
"""
Workspace Structure Update Tool
Automatically scans the workspace and updates the workspace_structure_complete.md file
with the current directory structure and file organization.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path to import scripts.core.changelog_engine as changelog_engine
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

class WorkspaceStructureUpdater:
    """Updates the workspace structure documentation file"""
    
    def __init__(self, workspace_root: str, output_file: str):
        """Initialize with workspace root path and output file path"""
        self.workspace_root = Path(workspace_root).resolve()
        self.output_file = Path(output_file).resolve()
        self.changelog_engine = ChangelogEngine()
        self.ignore_dirs = ['.git', '__pycache__', 'venv', '.pytest_cache']
        self.ignore_extensions = ['.pyc', '.pyo', '.pyd', '.git']
        
    def scan_workspace(self):
        """Scan the workspace and generate structure documentation"""
        start_time = time.perf_counter()
        
        content = [
            "# SQL_agent Workspace Structure",
            "",
            f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "## Root Directory"
        ]
        
        # Get all items in the root directory
        root_items = sorted(os.listdir(self.workspace_root))
        for item in root_items:
            item_path = self.workspace_root / item
            if self._should_ignore(item_path):
                continue
                
            if item_path.is_dir():
                content.append(f"- `{item}/` - Directory for {item}")
            else:
                description = self._get_file_description(item)
                content.append(f"- `{item}` - {description}")
        
        # Add sections for each major directory
        content.extend(self._process_directory("scripts", "Scripts Directory"))
        content.extend(self._process_directory("docs", "Documentation Directory"))
        content.extend(self._process_directory("config", "Configuration Directory"))
        content.extend(self._process_directory("logs", "Logs Directory"))
        
        # Write the content to the output file
        self.output_file.write_text("\n".join(content))
        
        execution_time = (time.perf_counter() - start_time) * 1000
        print(f"Workspace structure updated in {execution_time:.2f}ms")
        
        # Update changelog
        self._update_changelog(execution_time)
        
        return execution_time
        
    def _process_directory(self, dir_name: str, section_title: str):
        """Process a directory and return its structure as markdown lines"""
        dir_path = self.workspace_root / dir_name
        if not dir_path.exists():
            return []
            
        content = ["", f"## {section_title}"]
        
        # Get all items in the directory
        items = sorted(os.listdir(dir_path))
        for item in items:
            item_path = dir_path / item
            if self._should_ignore(item_path):
                continue
                
            if item_path.is_dir():
                content.append(f"- `{item}/` - Directory for {item}")
            else:
                description = self._get_file_description(item)
                content.append(f"- `{item}` - {description}")
                
        return content
        
    def _should_ignore(self, path: Path):
        """Check if a path should be ignored"""
        if path.is_dir() and path.name in self.ignore_dirs:
            return True
        if path.is_file() and path.suffix in self.ignore_extensions:
            return True
        return False
        
    def _get_file_description(self, filename: str):
        """Get a description for a file based on its name and extension"""
        name, ext = os.path.splitext(filename)
        
        if ext == '.py':
            return f"Script for {name.replace('_', ' ')}"
        elif ext == '.md':
            return f"Documentation for {name.replace('_', ' ')}"
        elif ext == '.json':
            return f"JSON file for {name.replace('_', ' ')}"
        elif ext == '.ini':
            return f"Configuration file for {name.replace('_', ' ')}"
        elif ext == '.log':
            return f"Log file for {name.replace('_', ' ')}"
        elif ext == '.sql':
            return f"SQL query for {name.replace('_', ' ')}"
        else:
            return f"File for {name.replace('_', ' ')}"
            
    def _update_changelog(self, execution_time_ms: float):
        """Update the changelog with the workspace structure update"""
        # Create change vectors for affected files
        files_affected = [
            ChangeVector(
                file_path=str(self.output_file.relative_to(self.workspace_root)),
                change_type=ChangeType.DOCS,
                operation="MODIFIED",
                impact_level="MEDIUM",
                dependencies=["scripts/core/update_workspace_structure.py"]
            )
        ]
        
        # Create an AnswerRecord object
        from datetime import datetime
        record = AnswerRecord(
            answer_id=self.changelog_engine.answer_counter,
            timestamp=datetime.now().isoformat(),
            action_type="Documentation Maintenance",
            previous_state="Outdated workspace structure documentation",
            current_state="Updated workspace structure documentation",
            changes_made=[
                "Updated workspace structure documentation with current directory layout",
                "Added descriptions for all files and directories",
                f"Execution completed in {execution_time_ms:.2f}ms"
            ],
            files_affected=files_affected,
            technical_decisions=[
                "Automated workspace structure documentation to ensure accuracy",
                "Implemented file type detection based on extensions",
                "Excluded irrelevant directories and files from documentation"
            ],
            next_actions=[
                "Schedule regular workspace structure updates",
                "Integrate with CI/CD pipeline",
                "Enhance file descriptions with more detailed information"
            ]
        )
        
        # Update the changelog
        self.changelog_engine.update_changelog(record)
        
if __name__ == "__main__":
    workspace_root = Path(__file__).parent.parent.parent
    output_file = workspace_root / "workspace_structure_complete.md"
    
    updater = WorkspaceStructureUpdater(workspace_root, output_file)
    updater.scan_workspace()
