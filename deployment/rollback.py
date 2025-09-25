#!/usr/bin/env python
"""
SQL Agent Rollback Script

This script provides rollback functionality for the SQL Agent deployment.
It restores the system to a previous state in case of deployment failures.
"""

import os
import sys
import json
import shutil
import logging
import argparse
from pathlib import Path

# Add parent directory to path to allow imports from the main project
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'rollback.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('rollback')

class RollbackManager:
    """Manages the rollback process for the SQL Agent."""
    
    def __init__(self, backup_dir):
        """
        Initialize the rollback manager.
        
        Args:
            backup_dir (str): Path to the backup directory
        """
        self.backup_dir = backup_dir
        
        # Validate backup directory
        if not os.path.isdir(backup_dir):
            logger.error(f"Backup directory does not exist: {backup_dir}")
            sys.exit(1)
    
    def validate_backup(self):
        """Validate the backup directory contents."""
        logger.info("Validating backup...")
        
        # Check for required backup files
        required_files = ['config.ini']
        missing_files = [file for file in required_files if not os.path.exists(os.path.join(self.backup_dir, file))]
        
        if missing_files:
            logger.error(f"Missing required backup files: {', '.join(missing_files)}")
            return False
        
        logger.info("Backup validation successful")
        return True
    
    def restore_configuration(self):
        """Restore configuration files from backup."""
        logger.info("Restoring configuration files...")
        
        try:
            # Restore config.ini
            shutil.copy2(os.path.join(self.backup_dir, 'config.ini'), 'config/config.ini')
            logger.info("Restored config.ini")
            
            # Remove production config if it exists
            if os.path.exists('config/config.ini.production'):
                os.remove('config/config.ini.production')
                logger.info("Removed production configuration")
            
            return True
        except Exception as e:
            logger.error(f"Failed to restore configuration: {e}")
            return False
    
    def restore_database(self):
        """Restore database from backup (if applicable)."""
        logger.info("Checking for database backup...")
        
        # This would be implemented based on the specific database system
        # For now, we'll just log a message
        logger.info("Database restoration would be performed here if implemented")
        return True
    
    def rollback(self):
        """Execute the rollback process."""
        logger.info("Starting rollback process...")
        
        # Validate the backup
        if not self.validate_backup():
            logger.error("Backup validation failed. Rollback aborted.")
            return False
        
        # Restore configuration
        if not self.restore_configuration():
            logger.error("Configuration restoration failed.")
            return False
        
        # Restore database (if applicable)
        if not self.restore_database():
            logger.error("Database restoration failed.")
            return False
        
        # Remove version.json if it exists
        if os.path.exists('version.json'):
            try:
                os.remove('version.json')
                logger.info("Removed version.json")
            except Exception as e:
                logger.warning(f"Failed to remove version.json: {e}")
        
        logger.info("Rollback completed successfully")
        return True

def list_backups():
    """List available backup directories."""
    backup_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith('backup_')]
    
    if not backup_dirs:
        print("No backup directories found.")
        return
    
    print("Available backup directories:")
    for i, backup_dir in enumerate(sorted(backup_dirs, reverse=True)):
        print(f"{i+1}. {backup_dir}")
    
    return backup_dirs

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SQL Agent Rollback Tool')
    parser.add_argument('--backup', help='Path to backup directory')
    parser.add_argument('--list', action='store_true', help='List available backup directories')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    # List available backups if requested
    if args.list:
        backup_dirs = list_backups()
        sys.exit(0)
    
    # Get backup directory
    backup_dir = args.backup
    if not backup_dir:
        backup_dirs = list_backups()
        if not backup_dirs:
            sys.exit(1)
        
        try:
            choice = int(input("Enter the number of the backup to restore: "))
            if 1 <= choice <= len(backup_dirs):
                backup_dir = backup_dirs[choice-1]
            else:
                print("Invalid choice.")
                sys.exit(1)
        except ValueError:
            print("Invalid input.")
            sys.exit(1)
    
    # Create rollback manager
    manager = RollbackManager(backup_dir)
    
    # Execute rollback
    success = manager.rollback()
    
    sys.exit(0 if success else 1)
