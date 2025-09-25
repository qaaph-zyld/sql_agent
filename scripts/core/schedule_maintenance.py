#!/usr/bin/env python3
"""
Maintenance Scheduler
Schedules and executes regular maintenance tasks:
- Validation suite execution
- Workspace structure documentation updates
- Changelog integrity checks
"""

import sys
import os
import time
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
from typing import Dict, List, Any

# Add parent directory to path to import scripts.core.changelog_engine as changelog_engine
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent.parent / "logs" / "maintenance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("maintenance_scheduler")

class MaintenanceScheduler:
    """Schedules and executes maintenance tasks"""
    
    def __init__(self, workspace_root: str, config_path: str = None):
        """Initialize with workspace root path and optional config path"""
        self.workspace_root = Path(workspace_root).resolve()
        self.config_path = Path(config_path) if config_path else self.workspace_root / "config" / "maintenance_config.json"
        self.changelog_engine = ChangelogEngine()
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                
        # Default configuration
        default_config = {
            "validation": {
                "schedule": "daily",  # daily, weekly, or manual
                "last_run": None,
                "next_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "workspace_structure": {
                "schedule": "weekly",
                "last_run": None,
                "next_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "changelog_check": {
                "schedule": "daily",
                "last_run": None,
                "next_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Save default config
        os.makedirs(self.config_path.parent, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        return default_config
        
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def _update_next_run(self, task: str):
        """Update the next run time for a task based on its schedule"""
        schedule = self.config[task]["schedule"]
        now = datetime.now()
        
        if schedule == "daily":
            next_run = now + timedelta(days=1)
        elif schedule == "weekly":
            next_run = now + timedelta(weeks=1)
        else:
            next_run = now  # Manual schedule defaults to now
            
        self.config[task]["last_run"] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.config[task]["next_run"] = next_run.strftime("%Y-%m-%d %H:%M:%S")
        
    def run_validation(self):
        """Run the validation suite"""
        logger.info("Running validation suite...")
        
        validation_script = self.workspace_root / "scripts" / "core" / "run_validation.py"
        try:
            result = subprocess.run(
                [sys.executable, str(validation_script)],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True
            )
            
            logger.info(f"Validation output:\n{result.stdout}")
            if result.returncode != 0:
                logger.error(f"Validation failed with return code {result.returncode}")
                logger.error(f"Error output:\n{result.stderr}")
                return False
                
            # Check if validation passed
            if "System is production-ready" in result.stdout:
                logger.info("Validation passed: System is production-ready")
                return True
            else:
                logger.warning("Validation failed: System is NOT production-ready")
                return False
                
        except Exception as e:
            logger.error(f"Error running validation: {e}")
            return False
            
    def update_workspace_structure(self):
        """Update the workspace structure documentation"""
        logger.info("Updating workspace structure documentation...")
        
        update_script = self.workspace_root / "scripts" / "core" / "update_workspace_structure.py"
        try:
            result = subprocess.run(
                [sys.executable, str(update_script)],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True
            )
            
            logger.info(f"Workspace structure update output:\n{result.stdout}")
            if result.returncode != 0:
                logger.error(f"Workspace structure update failed with return code {result.returncode}")
                logger.error(f"Error output:\n{result.stderr}")
                return False
                
            logger.info("Workspace structure documentation updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating workspace structure: {e}")
            return False
            
    def check_changelog_integrity(self):
        """Check the integrity of the changelog"""
        logger.info("Checking changelog integrity...")
        
        changelog_path = self.workspace_root / "Changelog.md"
        if not changelog_path.exists():
            logger.error("Changelog file not found")
            return False
            
        try:
            content = changelog_path.read_text()
            
            # Check for required sections
            has_session_header = "## Session:" in content
            has_answer_entries = "### Answer #" in content
            has_required_sections = all(section in content for section in [
                "#### Changes Made:",
                "#### Files Affected:",
                "#### Technical Decisions:",
                "#### Next Actions Required:"
            ])
            
            # Check answer numbering sequence
            import re
            answer_ids = [int(m) for m in re.findall(r'### Answer #(\d+)', content)]
            sequential = answer_ids == list(range(1, len(answer_ids) + 1)) if answer_ids else True
            
            integrity_ok = has_session_header and has_answer_entries and has_required_sections and sequential
            
            if integrity_ok:
                logger.info("Changelog integrity check passed")
            else:
                logger.warning("Changelog integrity check failed")
                if not has_session_header:
                    logger.warning("Missing session header")
                if not has_answer_entries:
                    logger.warning("Missing answer entries")
                if not has_required_sections:
                    logger.warning("Missing required sections")
                if not sequential:
                    logger.warning(f"Answer IDs not sequential: {answer_ids}")
                    
            return integrity_ok
            
        except Exception as e:
            logger.error(f"Error checking changelog integrity: {e}")
            return False
            
    def run_scheduled_tasks(self, force: bool = False):
        """Run tasks that are scheduled to run now or forced"""
        now = datetime.now()
        tasks_run = []
        
        # Check each task
        for task, config in self.config.items():
            next_run = datetime.strptime(config["next_run"], "%Y-%m-%d %H:%M:%S")
            
            if force or now >= next_run:
                logger.info(f"Running scheduled task: {task}")
                
                if task == "validation":
                    success = self.run_validation()
                elif task == "workspace_structure":
                    success = self.update_workspace_structure()
                elif task == "changelog_check":
                    success = self.check_changelog_integrity()
                else:
                    logger.warning(f"Unknown task: {task}")
                    continue
                    
                self._update_next_run(task)
                tasks_run.append({"task": task, "success": success})
                
        # Save updated config
        self._save_config()
        
        return tasks_run
        
    def update_changelog_with_maintenance(self, tasks_run: List[Dict[str, Any]]):
        """Update the changelog with maintenance results"""
        if not tasks_run:
            return
            
        # Create summary of tasks run
        changes_made = []
        for task in tasks_run:
            status = "successfully" if task["success"] else "with errors"
            changes_made.append(f"Ran {task['task']} {status}")
            
        # Create change vectors for affected files
        files_affected = []
        for task in tasks_run:
            if task["task"] == "validation":
                files_affected.append(
                    ChangeVector(
                        file_path="validation_report.json",
                        change_type=ChangeType.CONFIG,
                        operation="MODIFIED",
                        impact_level="LOW",
                        dependencies=["scripts/core/run_validation.py"]
                    )
                )
            elif task["task"] == "workspace_structure":
                files_affected.append(
                    ChangeVector(
                        file_path="workspace_structure_complete.md",
                        change_type=ChangeType.DOCS,
                        operation="MODIFIED",
                        impact_level="LOW",
                        dependencies=["scripts/core/update_workspace_structure.py"]
                    )
                )
                
        # Create an AnswerRecord object
        from datetime import datetime
        record = AnswerRecord(
            answer_id=self.changelog_engine.answer_counter,
            timestamp=datetime.now().isoformat(),
            action_type="System Maintenance",
            previous_state="Regular maintenance required",
            current_state="System maintenance completed",
            changes_made=changes_made,
            files_affected=files_affected,
            technical_decisions=[
                "Executed scheduled maintenance tasks",
                "Updated system documentation",
                "Verified system integrity"
            ],
            next_actions=[
                "Continue with development workflow",
                "Address any issues identified during maintenance",
                "Schedule next maintenance run"
            ]
        )
        
        # Update the changelog
        self.changelog_engine.update_changelog(record)
        
def main():
    parser = argparse.ArgumentParser(description='Schedule and run maintenance tasks')
    parser.add_argument('--force', action='store_true', help='Force all tasks to run regardless of schedule')
    parser.add_argument('--config', help='Path to configuration file')
    args = parser.parse_args()
    
    workspace_root = Path(__file__).parent.parent.parent
    scheduler = MaintenanceScheduler(workspace_root, args.config)
    
    tasks_run = scheduler.run_scheduled_tasks(args.force)
    
    if tasks_run:
        scheduler.update_changelog_with_maintenance(tasks_run)
        logger.info("Maintenance tasks completed and changelog updated")
    else:
        logger.info("No maintenance tasks were due to run")
    
if __name__ == "__main__":
    main()
