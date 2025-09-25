#!/usr/bin/env python3
"""
Schedule Maintenance - Automates regular system maintenance tasks
"""

import sys
import os
import time
import json
import logging
import argparse
import schedule
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/maintenance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("maintenance")

class MaintenanceScheduler:
    def __init__(self, root_path="."):
        self.root_path = Path(root_path).resolve()
        self.engine = ChangelogEngine()
        self.last_run = {}
        self.maintenance_config = {
            "daily": [
                {
                    "name": "Run validation suite",
                    "command": ["python", "scripts/core/run_validation.py"],
                    "update_changelog": True
                },
                {
                    "name": "Update workspace structure",
                    "command": ["python", "scripts/utilities/update_workspace_structure.py"],
                    "update_changelog": False  # Script updates changelog itself
                }
            ],
            "weekly": [
                {
                    "name": "Check for import issues",
                    "command": ["python", "scripts/utilities/update_imports.py", "--dry-run"],
                    "update_changelog": True
                }
            ],
            "monthly": [
                {
                    "name": "Full system verification",
                    "command": ["python", "scripts/core/run_validation.py", "--comprehensive"],
                    "update_changelog": True
                }
            ]
        }
        
        # Create logs directory if it doesn't exist
        logs_dir = self.root_path / "logs"
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True)
    
    def run_task(self, task):
        """Run a maintenance task and optionally update changelog"""
        logger.info(f"Running task: {task['name']}")
        
        start_time = time.time()
        
        try:
            # Change to root directory
            os.chdir(self.root_path)
            
            # Run command
            result = subprocess.run(
                task["command"],
                capture_output=True,
                text=True,
                check=False
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            # Log result
            if success:
                logger.info(f"Task '{task['name']}' completed successfully in {execution_time:.2f}s")
            else:
                logger.error(f"Task '{task['name']}' failed with exit code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
            
            # Update changelog if configured
            if task["update_changelog"] and success:
                self.update_changelog(task["name"], execution_time, result.stdout)
            
            # Update last run time
            self.last_run[task["name"]] = datetime.now()
            
            return success
            
        except Exception as e:
            logger.error(f"Error running task '{task['name']}': {str(e)}")
            return False
    
    def update_changelog(self, task_name, execution_time, output):
        """Update changelog with maintenance task results"""
        files_affected = []
        
        # Extract affected files from output if possible
        try:
            if "validation_report.json" in output:
                files_affected.append(
                    ChangeVector(
                        file_path="validation_report.json",
                        change_type=ChangeType.DOCS,
                        operation="MODIFIED",
                        impact_level="LOW",
                        dependencies=[]
                    )
                )
            
            if "workspace_structure_complete.md" in output:
                files_affected.append(
                    ChangeVector(
                        file_path="workspace_structure_complete.md",
                        change_type=ChangeType.DOCS,
                        operation="MODIFIED",
                        impact_level="LOW",
                        dependencies=[]
                    )
                )
        except:
            # If we can't parse output, just continue
            pass
        
        # Add changelog itself
        files_affected.append(
            ChangeVector(
                file_path="Changelog.md",
                change_type=ChangeType.DOCS,
                operation="MODIFIED",
                impact_level="LOW",
                dependencies=[]
            )
        )
        
        record = AnswerRecord(
            answer_id=self.engine.answer_counter,
            timestamp=datetime.now().isoformat(),
            action_type="Maintenance",
            previous_state="System due for scheduled maintenance",
            current_state="System maintenance completed",
            changes_made=[
                f"Executed scheduled maintenance task: {task_name}",
                f"Completed in {execution_time:.2f} seconds"
            ],
            files_affected=files_affected,
            technical_decisions=[
                "Automated maintenance execution to ensure system stability",
                "Generated validation report to verify system integrity"
            ],
            next_actions=[
                "Continue with regular maintenance schedule",
                "Review validation reports for any issues"
            ]
        )
        
        self.engine.update_changelog(record)
        logger.info("Changelog updated with maintenance results")
    
    def run_daily_tasks(self):
        """Run all daily maintenance tasks"""
        logger.info("Running daily maintenance tasks")
        for task in self.maintenance_config["daily"]:
            self.run_task(task)
    
    def run_weekly_tasks(self):
        """Run all weekly maintenance tasks"""
        logger.info("Running weekly maintenance tasks")
        for task in self.maintenance_config["weekly"]:
            self.run_task(task)
    
    def run_monthly_tasks(self):
        """Run all monthly maintenance tasks"""
        logger.info("Running monthly maintenance tasks")
        for task in self.maintenance_config["monthly"]:
            self.run_task(task)
    
    def schedule_tasks(self):
        """Schedule all maintenance tasks"""
        # Schedule daily tasks at 1:00 AM
        schedule.every().day.at("01:00").do(self.run_daily_tasks)
        
        # Schedule weekly tasks on Monday at 2:00 AM
        schedule.every().monday.at("02:00").do(self.run_weekly_tasks)
        
        # Schedule monthly tasks on the 1st of each month at 3:00 AM
        schedule.every().month.at("03:00").do(self.run_monthly_tasks)
        
        logger.info("Maintenance tasks scheduled")
        logger.info("Daily tasks will run at 01:00 AM")
        logger.info("Weekly tasks will run on Monday at 02:00 AM")
        logger.info("Monthly tasks will run on the 1st of each month at 03:00 AM")
    
    def run_now(self, frequency=None):
        """Run tasks for specified frequency immediately"""
        if frequency == "daily":
            self.run_daily_tasks()
        elif frequency == "weekly":
            self.run_weekly_tasks()
        elif frequency == "monthly":
            self.run_monthly_tasks()
        else:
            # Run all tasks
            self.run_daily_tasks()
            self.run_weekly_tasks()
            self.run_monthly_tasks()
    
    def start_daemon(self):
        """Start maintenance scheduler daemon"""
        self.schedule_tasks()
        
        logger.info("Maintenance scheduler daemon started")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    parser = argparse.ArgumentParser(description="Schedule and run system maintenance tasks")
    parser.add_argument("--root", type=str, default=".", help="Root directory path")
    parser.add_argument("--run-now", action="store_true", help="Run maintenance tasks immediately")
    parser.add_argument("--frequency", type=str, choices=["daily", "weekly", "monthly", "all"], 
                      default="all", help="Frequency of tasks to run now")
    parser.add_argument("--daemon", action="store_true", help="Start as daemon process")
    args = parser.parse_args()
    
    scheduler = MaintenanceScheduler(args.root)
    
    if args.run_now:
        scheduler.run_now(args.frequency if args.frequency != "all" else None)
    elif args.daemon:
        scheduler.start_daemon()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
