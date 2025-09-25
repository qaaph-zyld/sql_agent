#!/usr/bin/env python3
"""
Import Statement Updater
Updates import statements in Python files to reflect the new directory structure.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# Add parent directory to path to import scripts.core.changelog_engine as changelog_engine
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent.parent / "logs" / "import_updater.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("import_updater")

class ImportUpdater:
    """Updates import statements in Python files"""
    
    def __init__(self, workspace_root: str):
        """Initialize with workspace root path"""
        self.workspace_root = Path(workspace_root).resolve()
        self.changelog_engine = ChangelogEngine()
        self.module_mapping = self._create_module_mapping()
        self.files_updated = []
        
    def _create_module_mapping(self) -> Dict[str, str]:
        """Create mapping of old module names to new module names"""
        # Map of old module/file names to new module paths
        mapping = {
            # Core modules
            "changelog_engine": "scripts.core.changelog_engine",
            "validation_suite": "scripts.core.validation_suite",
            "run_validation": "scripts.core.run_validation",
            "workspace_scanner": "scripts.core.workspace_scanner",
            "state_manager": "scripts.core.state_manager",
            
            # Data quality modules
            "data_quality_core": "scripts.data_quality.data_quality_core",
            "data_quality_manager": "scripts.data_quality.data_quality_manager",
            
            # Report modules
            "Inventory_daily_report": "scripts.reports.Inventory_daily_report",
            "generate_interactive_dashboard": "scripts.reports.generate_interactive_dashboard",
            
            # Utility modules
            "custom_query_analyzer": "scripts.utilities.custom_query_analyzer",
            "data_lineage_mapper": "scripts.utilities.data_lineage_mapper",
            "enhanced_db_mapper": "scripts.utilities.enhanced_db_mapper",
            "extract_field_info": "scripts.utilities.extract_field_info",
            "pdf_field_extractor": "scripts.utilities.pdf_field_extractor",
            "query_parameter_interface": "scripts.utilities.query_parameter_interface",
            "relationship_mapper": "scripts.utilities.relationship_mapper"
        }
        return mapping
        
    def update_imports(self, dry_run: bool = False) -> List[Tuple[str, int]]:
        """Update import statements in all Python files"""
        python_files = list(self.workspace_root.glob("**/*.py"))
        
        for file_path in python_files:
            # Skip files in __pycache__ directories
            if "__pycache__" in str(file_path):
                continue
                
            # Read file content
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue
                
            # Track if this file was modified
            original_content = content
            
            # Update import statements
            for old_module, new_module in self.module_mapping.items():
                # Update "import module" statements
                pattern = rf"import\s+{old_module}(?!\w)"
                replacement = f"import {new_module} as {old_module}"
                content = re.sub(pattern, replacement, content)
                
                # Update "from module import ..." statements
                pattern = rf"from\s+{old_module}(?!\w)"
                replacement = f"from {new_module}"
                content = re.sub(pattern, replacement, content)
                
                # Update "import module as alias" statements
                pattern = rf"import\s+{old_module}(?!\w)\s+as\s+(\w+)"
                replacement = f"import {new_module} as \\1"
                content = re.sub(pattern, replacement, content)
                
            # Check if content was modified
            if content != original_content:
                if dry_run:
                    logger.info(f"Would update imports in {file_path.relative_to(self.workspace_root)}")
                else:
                    try:
                        with open(file_path, 'w') as f:
                            f.write(content)
                        logger.info(f"Updated imports in {file_path.relative_to(self.workspace_root)}")
                        self.files_updated.append((str(file_path.relative_to(self.workspace_root)), 1))
                    except Exception as e:
                        logger.error(f"Error writing file {file_path}: {e}")
                        
        return self.files_updated
        
    def update_changelog(self):
        """Update the changelog with import statement updates"""
        if not self.files_updated:
            logger.info("No files were updated, skipping changelog update")
            return
            
        # Create change vectors for affected files
        files_affected = []
        for file_path, count in self.files_updated:
            files_affected.append(
                ChangeVector(
                    file_path=file_path,
                    change_type="MODIFIED",
                    impact_level="MEDIUM",
                    change_category="Code Refactoring",
                    dependencies=[]
                )
            )
            
        # Generate changelog entry
        self.changelog_engine.update_changelog(
            action_summary="Import Statement Updates",
            action_type="Code Refactoring",
            previous_state="Import statements using old file paths",
            current_state="Import statements using new module structure",
            changes_made=[
                f"Updated import statements in {len(self.files_updated)} files",
                "Converted direct imports to module-based imports",
                "Preserved module aliases for backward compatibility"
            ],
            files_affected=files_affected,
            technical_decisions=[
                "Used regex pattern matching for precise import statement updates",
                "Maintained backward compatibility with module aliases",
                "Applied consistent import style across all files"
            ],
            next_actions=[
                "Test all modules to ensure correct functionality",
                "Remove original files after successful verification",
                "Update documentation with new import patterns"
            ]
        )
        
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update import statements in Python files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    parser.add_argument('--skip-changelog', action='store_true', help='Skip updating the changelog')
    args = parser.parse_args()
    
    workspace_root = Path(__file__).parent.parent.parent
    updater = ImportUpdater(workspace_root)
    
    files_updated = updater.update_imports(args.dry_run)
    
    if files_updated and not args.dry_run and not args.skip_changelog:
        updater.update_changelog()
        
    logger.info(f"Updated imports in {len(files_updated)} files")
    
if __name__ == "__main__":
    main()
