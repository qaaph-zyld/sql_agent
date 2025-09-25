#!/usr/bin/env python
"""
SQL Agent Post-Deployment Monitoring Setup

This script sets up monitoring for the SQL Agent after deployment.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'post_deploy_monitor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('post_deploy_monitor')

class PostDeployMonitor:
    """Sets up post-deployment monitoring for the SQL Agent."""
    
    def __init__(self, config_path):
        """Initialize with configuration path."""
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Load the configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    def setup_log_monitoring(self):
        """Set up log monitoring and alerting."""
        logger.info("Setting up log monitoring...")
        
        try:
            # Create log monitoring configuration
            log_config = {
                'log_directory': self.config.get('logging', {}).get('log_directory', 'logs'),
                'alert_on_error': True,
                'alert_on_warning': True,
                'check_interval_seconds': 60,
                'alert_recipients': self.config.get('monitoring', {}).get('alert_recipients', [])
            }
            
            # Write log monitoring configuration
            os.makedirs('config/monitoring', exist_ok=True)
            with open('config/monitoring/log_monitor.json', 'w') as f:
                json.dump(log_config, f, indent=2)
            
            logger.info("Log monitoring configuration created")
            return True
        except Exception as e:
            logger.error(f"Failed to set up log monitoring: {e}")
            return False
    
    def setup_performance_monitoring(self):
        """Set up performance monitoring."""
        logger.info("Setting up performance monitoring...")
        
        try:
            # Create performance monitoring configuration
            perf_config = {
                'metrics': [
                    {
                        'name': 'query_execution_time',
                        'threshold': 1000,
                        'alert_threshold': 5000
                    },
                    {
                        'name': 'database_connections',
                        'threshold': 50,
                        'alert_threshold': 80
                    },
                    {
                        'name': 'memory_usage',
                        'threshold': 512,
                        'alert_threshold': 1024
                    }
                ],
                'collection_interval_seconds': 60,
                'retention_days': 30
            }
            
            # Write performance monitoring configuration
            with open('config/monitoring/performance_monitor.json', 'w') as f:
                json.dump(perf_config, f, indent=2)
            
            logger.info("Performance monitoring configuration created")
            return True
        except Exception as e:
            logger.error(f"Failed to set up performance monitoring: {e}")
            return False
    
    def setup_health_checks(self):
        """Set up health checks."""
        logger.info("Setting up health checks...")
        
        try:
            # Create health check configuration
            health_config = {
                'checks': [
                    {
                        'name': 'database_connection',
                        'interval_seconds': 60
                    },
                    {
                        'name': 'api_status',
                        'interval_seconds': 30
                    },
                    {
                        'name': 'disk_space',
                        'interval_seconds': 300
                    }
                ],
                'alert_on_failure': True
            }
            
            # Write health check configuration
            with open('config/monitoring/health_checks.json', 'w') as f:
                json.dump(health_config, f, indent=2)
            
            logger.info("Health check configuration created")
            return True
        except Exception as e:
            logger.error(f"Failed to set up health checks: {e}")
            return False
    
    def run(self):
        """Run all monitoring setup tasks."""
        logger.info("Starting post-deployment monitoring setup...")
        
        success = True
        success &= self.setup_log_monitoring()
        success &= self.setup_performance_monitoring()
        success &= self.setup_health_checks()
        
        if success:
            logger.info("Post-deployment monitoring setup completed successfully")
            return True
        else:
            logger.error("Post-deployment monitoring setup completed with errors")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Set up post-deployment monitoring')
    parser.add_argument('--config', required=True, help='Path to configuration file')
    args = parser.parse_args()
    
    monitor = PostDeployMonitor(args.config)
    success = monitor.run()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
