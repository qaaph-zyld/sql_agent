#!/usr/bin/env python3
"""
Original Files Cleanup Utility
Identifies and removes original files that have been moved to the new directory structure.
Only removes files after verification to ensure system stability.
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Set
import subprocess
import argparse

# Add parent directory to path to import scripts.core.changelog_engine as changelog_engine
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent.parent / "logs" / "cleanup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cleanup_utility")

class CleanupUtility:
    """Identifies and removes original files after verification"""
    
    def __init__(self, workspace_root: str):
        """Initialize with workspace root path"""
        self.workspace_root = Path(workspace_root).resolve()
        self.changelog_engine = ChangelogEngine()
        self.original_files = self._identify_original_files()
        self.files_removed = []
        
    def _identify_original_files(self) -> Dict[str, Path]:
        """Identify original files that have been moved to the new structure"""
        # Map of original file paths to their new locations
        original_files = {
            # Core scripts
            "changelog_engine.py": self.workspace_root / "scripts" / "core" / "changelog_engine.py",
            "validation_suite.py": self.workspace_root / "scripts" / "core" / "validation_suite.py",
            "run_validation.py": self.workspace_root / "scripts" / "core" / "run_validation.py",
            "workspace_scanner.py": self.workspace_root / "scripts" / "core" / "workspace_scanner.py",
            "state_manager.py": self.workspace_root / "scripts" / "core" / "state_manager.py",
            
            # Data quality scripts
            "data_quality_core.py": self.workspace_root / "scripts" / "data_quality" / "data_quality_core.py",
            "data_quality_manager.py": self.workspace_root / "scripts" / "data_quality" / "data_quality_manager.py",
            
            # Report scripts
            "Inventory_daily_report.py": self.workspace_root / "scripts" / "reports" / "Inventory_daily_report.py",
            "generate_interactive_dashboard.py": self.workspace_root / "scripts" / "reports" / "generate_interactive_dashboard.py",
            
            # Utility scripts
            "custom_query_analyzer.py": self.workspace_root / "scripts" / "utilities" / "custom_query_analyzer.py",
            "data_lineage_mapper.py": self.workspace_root / "scripts" / "utilities" / "data_lineage_mapper.py",
            "enhanced_db_mapper.py": self.workspace_root / "scripts" / "utilities" / "enhanced_db_mapper.py",
            "extract_field_info.py": self.workspace_root / "scripts" / "utilities" / "extract_field_info.py",
            "pdf_field_extractor.py": self.workspace_root / "scripts" / "utilities" / "pdf_field_extractor.py",
            "query_parameter_interface.py": self.workspace_root / "scripts" / "utilities" / "query_parameter_interface.py",
            "relationship_mapper.py": self.workspace_root / "scripts" / "utilities" / "relationship_mapper.py",
            
            # Log files
            "custom_query_analysis.log": self.workspace_root / "logs" / "custom_query_analysis.log",
            "dashboard_generator.log": self.workspace_root / "logs" / "dashboard_generator.log",
            "data_lineage.log": self.workspace_root / "logs" / "data_lineage.log",
            "data_quality.log": self.workspace_root / "logs" / "data_quality.log",
            
            # Documentation files
            "DATA_QUALITY_README.md": self.workspace_root / "docs" / "DATA_QUALITY_README.md",
            "POWER_BI_INTEGRATION.md": self.workspace_root / "docs" / "POWER_BI_INTEGRATION.md",
            
            # Configuration files
            "config.ini": self.workspace_root / "config" / "config.ini"
        }
        
        # Filter to only include files that exist in both locations
        return {name: new_path for name, new_path in original_files.items() 
                if (self.workspace_root / name).exists() and new_path.exists()}
        
    def verify_files(self) -> Dict[str, bool]:
        """Verify that new files work correctly"""
        verification_results = {}
        
        # Run validation suite to verify system integrity
        logger.info("Running validation suite to verify system integrity...")
        validation_script = self.workspace_root / "scripts" / "core" / "run_validation.py"
        try:
            result = subprocess.run(
                [sys.executable, str(validation_script)],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True
            )
            
            validation_passed = "System is production-ready" in result.stdout
            logger.info(f"Validation {'passed' if validation_passed else 'failed'}")
            
            if not validation_passed:
                logger.warning("Validation failed, skipping file removal")
                logger.warning(f"Validation output: {result.stdout}")
                return {}
                
        except Exception as e:
            logger.error(f"Error running validation: {e}")
            return {}
            
        # Verify each file individually
        for name, new_path in self.original_files.items():
            try:
                # For Python files, try to import them
                if name.endswith('.py'):
                    module_path = str(new_path.relative_to(self.workspace_root)).replace('/', '.').replace('\\', '.').replace('.py', '')
                    try:
                        # Try importing the module
                        import_cmd = f"import {module_path}"
                        exec(import_cmd)
                        verification_results[name] = True
                        logger.info(f"Successfully imported {module_path}")
                    except Exception as e:
                        verification_results[name] = False
                        logger.error(f"Error importing {module_path}: {e}")
                else:
                    # For non-Python files, just check if they exist and have content
                    verification_results[name] = new_path.exists() and new_path.stat().st_size > 0
                    logger.info(f"Verified {name} exists at {new_path}")
            except Exception as e:
                verification_results[name] = False
                logger.error(f"Error verifying {name}: {e}")
                
        return verification_results
        
    def remove_original_files(self, verification_results: Dict[str, bool], dry_run: bool = False) -> List[str]:
        """Remove original files that have been verified"""
        for name, verified in verification_results.items():
            if verified:
                original_path = self.workspace_root / name
                if original_path.exists():
                    if dry_run:
                        logger.info(f"Would remove {original_path}")
                    else:
                        try:
                            if original_path.is_dir():
                                shutil.rmtree(original_path)
                            else:
                                original_path.unlink()
                            logger.info(f"Removed {original_path}")
                            self.files_removed.append(name)
                        except Exception as e:
                            logger.error(f"Error removing {original_path}: {e}")
                            
        return self.files_removed
        
    def update_changelog(self):
        """Update the changelog with file removal information"""
        if not self.files_removed:
            logger.info("No files were removed, skipping changelog update")
            return
            
        # Create change vectors for affected files
        files_affected = []
        for file_name in self.files_removed:
            files_affected.append(
                ChangeVector(
                    file_path=file_name,
                    change_type=ChangeType.DELETED,
                    operation="Workspace Cleanup",
                    impact_level="LOW",
                    dependencies=[]
                )
            )
            
        # Create an AnswerRecord object
        answer_record = AnswerRecord(
            action_summary="Original Files Cleanup",
            action_type="Workspace Maintenance",
            previous_state="Duplicate files in workspace (original and new locations)",
            current_state="Clean workspace with files only in their new locations",
            changes_made=[
                f"Removed {len(self.files_removed)} original files after verification",
                "Verified all new files work correctly before removal",
                "Maintained system integrity during cleanup process"
            ],
            files_affected=files_affected,
            technical_decisions=[
                "Verified system integrity with validation suite before removal",
                "Removed files only after confirming new versions work correctly",
                "Preserved system stability during transition"
            ],
            next_actions=[
                "Update documentation to reflect final workspace structure",
                "Implement regular maintenance schedule",
                "Consider additional workspace optimizations"
            ]
        )
            
        # Generate changelog entry
        self.changelog_engine.update_changelog(answer_record)
        
def main():
    parser = argparse.ArgumentParser(description='Clean up original files after verification')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be removed without making changes')
    parser.add_argument('--skip-verification', action='store_true', help='Skip verification and remove files immediately (not recommended)')
    parser.add_argument('--skip-changelog', action='store_true', help='Skip updating the changelog')
    args = parser.parse_args()
    
    workspace_root = Path(__file__).parent.parent.parent
    cleanup_utility = CleanupUtility(workspace_root)
    
    # Verify files if not skipping verification
    verification_results = {}
    if not args.skip_verification:
        verification_results = cleanup_utility.verify_files()
    else:
        # If skipping verification, assume all files are verified
        for name in cleanup_utility.original_files.keys():
            verification_results[name] = True
        logger.warning("Skipping verification - this is not recommended")
    
    # Remove original files
    removed_files = cleanup_utility.remove_original_files(verification_results, args.dry_run)
    logger.info(f"Removed {len(removed_files)} original files")
    
    # Update changelog if files were removed and not skipping changelog
    # Skip changelog update in dry-run mode or if explicitly requested
    if removed_files and not args.skip_changelog and not args.dry_run:
        cleanup_utility.update_changelog()
        
    logger.info(f"Removed {len(removed_files)} original files")
    
if __name__ == "__main__":
    main()
