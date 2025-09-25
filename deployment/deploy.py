#!/usr/bin/env python
"""
SQL Agent Deployment Script

This script automates the deployment of the SQL Agent to a production environment.
It handles configuration validation, environment setup, and deployment tasks.
"""

import os
import sys
import json
import shutil
import logging
import argparse
import datetime
import subprocess
from pathlib import Path

# Add parent directory to path to allow imports from the main project
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'deployment.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('deployment')

class DeploymentManager:
    """Manages the deployment process for the SQL Agent."""
    
    def __init__(self, config_path, env_vars_path=None):
        """
        Initialize the deployment manager.
        
        Args:
            config_path (str): Path to the production configuration file
            env_vars_path (str, optional): Path to environment variables file
        """
        self.config_path = config_path
        self.env_vars_path = env_vars_path
        self.config = None
        self.env_vars = {}
        
        # Load configuration
        self._load_config()
        
        # Load environment variables if provided
        if env_vars_path:
            self._load_env_vars()
    
    def _load_config(self):
        """Load the production configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    def _load_env_vars(self):
        """Load environment variables from file."""
        try:
            with open(self.env_vars_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        self.env_vars[key.strip()] = value.strip()
            logger.info(f"Loaded environment variables from {self.env_vars_path}")
        except Exception as e:
            logger.error(f"Failed to load environment variables: {e}")
            sys.exit(1)
    
    def _substitute_env_vars(self):
        """Substitute environment variables in the configuration."""
        config_str = json.dumps(self.config)
        
        # Replace environment variables in the configuration
        for key, value in self.env_vars.items():
            placeholder = f"${{{key}}}"
            config_str = config_str.replace(placeholder, value)
        
        # Replace release date if not already set
        if '"${RELEASE_DATE}"' in config_str:
            release_date = datetime.datetime.now().strftime("%Y-%m-%d")
            config_str = config_str.replace('"${RELEASE_DATE}"', f'"{release_date}"')
        
        # Parse the modified configuration
        self.config = json.loads(config_str)
        logger.info("Substituted environment variables in configuration")
    
    def validate_config(self):
        """Validate the production configuration."""
        logger.info("Validating configuration...")
        
        # Check required configuration sections
        required_sections = ['database', 'logging', 'security', 'monitoring', 'deployment']
        missing_sections = [section for section in required_sections if section not in self.config]
        
        if missing_sections:
            logger.error(f"Missing required configuration sections: {', '.join(missing_sections)}")
            return False
        
        # Check database configuration
        db_config = self.config.get('database', {})
        required_db_fields = ['db_host', 'db_name', 'db_user', 'db_password']
        missing_db_fields = [field for field in required_db_fields if field not in db_config]
        
        if missing_db_fields:
            logger.error(f"Missing required database configuration fields: {', '.join(missing_db_fields)}")
            return False
        
        # Check for placeholder values that weren't substituted
        config_str = json.dumps(self.config)
        if '${' in config_str and '}' in config_str:
            logger.error("Configuration contains unsubstituted environment variables")
            return False
        
        logger.info("Configuration validation successful")
        return True
    
    def setup_environment(self):
        """Set up the production environment."""
        logger.info("Setting up production environment...")
        
        # Create necessary directories
        log_dir = self.config.get('logging', {}).get('log_directory', 'logs/production')
        os.makedirs(log_dir, exist_ok=True)
        logger.info(f"Created log directory: {log_dir}")
        
        # Check Python dependencies
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                          check=True, capture_output=True)
            logger.info("Installed Python dependencies")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e.stderr.decode()}")
            return False
        
        return True
    
    def backup_current_state(self):
        """Backup the current state before deployment."""
        logger.info("Backing up current state...")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup configuration
        shutil.copy2('config/config.ini', f"{backup_dir}/config.ini")
        
        # Backup database (if applicable)
        # This would be implemented based on the specific database system
        
        logger.info(f"Backup created in {backup_dir}")
        return backup_dir
    
    def deploy(self):
        """Execute the deployment process."""
        logger.info("Starting deployment process...")
        
        # Substitute environment variables in the configuration
        if self.env_vars:
            self._substitute_env_vars()
        
        # Validate the configuration
        if not self.validate_config():
            logger.error("Configuration validation failed. Deployment aborted.")
            return False
        
        # Backup current state
        backup_dir = self.backup_current_state()
        
        # Set up the environment
        if not self.setup_environment():
            logger.error("Environment setup failed. Deployment aborted.")
            return False
        
        # Update the main configuration file with production settings
        try:
            # Create a production-specific config.ini
            with open('config/config.ini.production', 'w') as f:
                f.write("[DATABASE]\n")
                f.write(f"db_host = {self.config['database']['db_host']}\n")
                f.write(f"db_name = {self.config['database']['db_name']}\n")
                f.write(f"db_user = {self.config['database']['db_user']}\n")
                f.write(f"db_password = {self.config['database']['db_password']}\n")
                
                # Add additional sections as needed
                f.write("\n[LOGGING]\n")
                f.write(f"level = {self.config['logging']['level']}\n")
                f.write(f"file_rotation = {self.config['logging']['file_rotation']}\n")
                f.write(f"retention_days = {self.config['logging']['retention_days']}\n")
                
                f.write("\n[SECURITY]\n")
                f.write(f"use_ssl = {str(self.config['security']['use_ssl']).lower()}\n")
                f.write(f"require_authentication = {str(self.config['security']['require_authentication']).lower()}\n")
                
            logger.info("Created production configuration file")
        except Exception as e:
            logger.error(f"Failed to create production configuration: {e}")
            return False
        
        # Run database migrations (if applicable)
        # This would be implemented based on the specific database system
        
        # Update version information
        version_info = {
            "version": self.config['deployment']['version'],
            "environment": self.config['deployment']['environment'],
            "release_date": self.config['deployment']['release_date'],
            "deployed_by": os.environ.get('USERNAME', 'unknown')
        }
        
        with open('version.json', 'w') as f:
            json.dump(version_info, f, indent=2)
        
        logger.info("Deployment completed successfully")
        logger.info(f"SQL Agent version {version_info['version']} deployed to {version_info['environment']}")
        logger.info(f"Backup available at {backup_dir}")
        
        return True

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SQL Agent Deployment Tool')
    parser.add_argument('--config', default='config/production_config.json',
                        help='Path to production configuration file')
    parser.add_argument('--env', default='.env',
                        help='Path to environment variables file')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    # Create deployment manager
    manager = DeploymentManager(args.config, args.env)
    
    # Execute deployment
    success = manager.deploy()
    
    sys.exit(0 if success else 1)
