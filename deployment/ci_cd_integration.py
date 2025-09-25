#!/usr/bin/env python
"""
SQL Agent CI/CD Integration Script

This script facilitates integration with CI/CD pipelines for automated
testing, deployment, and validation of the SQL Agent.
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'ci_cd_integration.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ci_cd_integration')

class CICDIntegration:
    """Handles CI/CD pipeline integration for the SQL Agent."""
    
    def __init__(self, config_path):
        """Initialize with configuration path."""
        self.config_path = config_path
        self.config = self._load_config()
        self.report_data = {
            'tests': {
                'unit': {'passed': 0, 'failed': 0},
                'integration': {'passed': 0, 'failed': 0}
            },
            'security': {'passed': 0, 'failed': 0},
            'deployment': {'status': 'not_started'}
        }
    
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
    
    def _run_command(self, command, cwd=None):
        """Run a command and return its output."""
        logger.info(f"Running command: {' '.join(command)}")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd
            )
            
            stdout, stderr = process.communicate()
            return_code = process.returncode
            
            if return_code != 0:
                logger.error(f"Command failed with return code {return_code}")
                logger.error(f"stderr: {stderr}")
            else:
                logger.info(f"Command completed successfully")
            
            return return_code, stdout, stderr
        except Exception as e:
            logger.error(f"Failed to run command: {e}")
            return 1, '', str(e)
    
    def run_unit_tests(self):
        """Run unit tests."""
        logger.info("Running unit tests...")
        
        return_code, stdout, stderr = self._run_command(
            ['python', '-m', 'unittest', 'discover', 'tests/unit']
        )
        
        if return_code == 0:
            # Parse test results
            passed_count = stdout.count('ok')
            failed_count = stdout.count('FAIL')
            
            self.report_data['tests']['unit']['passed'] = passed_count
            self.report_data['tests']['unit']['failed'] = failed_count
            
            logger.info(f"Unit tests completed: {passed_count} passed, {failed_count} failed")
            return True
        else:
            logger.error("Unit tests failed")
            return False
    
    def run_integration_tests(self):
        """Run integration tests."""
        logger.info("Running integration tests...")
        
        return_code, stdout, stderr = self._run_command(
            ['python', '-m', 'unittest', 'discover', 'tests/integration']
        )
        
        if return_code == 0:
            # Parse test results
            passed_count = stdout.count('ok')
            failed_count = stdout.count('FAIL')
            
            self.report_data['tests']['integration']['passed'] = passed_count
            self.report_data['tests']['integration']['failed'] = failed_count
            
            logger.info(f"Integration tests completed: {passed_count} passed, {failed_count} failed")
            return True
        else:
            logger.error("Integration tests failed")
            return False
    
    def run_security_review(self):
        """Run security review."""
        logger.info("Running security review...")
        
        return_code, stdout, stderr = self._run_command(
            ['python', 'deployment/security_review.py', '--config', self.config_path, '--ci']
        )
        
        if return_code == 0:
            # Parse security results from stdout (assuming JSON output)
            try:
                security_results = json.loads(stdout)
                self.report_data['security']['passed'] = security_results.get('passed', 0)
                self.report_data['security']['failed'] = security_results.get('failed', 0)
            except json.JSONDecodeError:
                # Fallback if output is not JSON
                self.report_data['security']['passed'] = 1
                self.report_data['security']['failed'] = 0
            
            logger.info("Security review completed successfully")
            return True
        else:
            logger.error("Security review failed")
            self.report_data['security']['failed'] = 1
            return False
    
    def run_deployment(self, environment):
        """Run deployment to the specified environment."""
        logger.info(f"Running deployment to {environment}...")
        
        # Update deployment status
        self.report_data['deployment']['status'] = 'in_progress'
        self.report_data['deployment']['environment'] = environment
        
        return_code, stdout, stderr = self._run_command([
            'python', 'deployment/staged_deploy.py',
            '--config', self.config_path,
            '--environment', environment,
            '--ci'
        ])
        
        if return_code == 0:
            logger.info(f"Deployment to {environment} completed successfully")
            self.report_data['deployment']['status'] = 'success'
            return True
        else:
            logger.error(f"Deployment to {environment} failed")
            self.report_data['deployment']['status'] = 'failed'
            return False
    
    def generate_report(self, output_path):
        """Generate a CI/CD report."""
        logger.info(f"Generating CI/CD report to {output_path}...")
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.report_data, f, indent=2)
            
            logger.info("CI/CD report generated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to generate CI/CD report: {e}")
            return False
    
    def run_pipeline(self, environment=None, skip_tests=False, skip_security=False):
        """Run the CI/CD pipeline."""
        logger.info("Starting CI/CD pipeline...")
        
        success = True
        
        # Run tests if not skipped
        if not skip_tests:
            success &= self.run_unit_tests()
            success &= self.run_integration_tests()
        
        # Run security review if not skipped
        if not skip_security:
            success &= self.run_security_review()
        
        # Run deployment if environment is specified and previous steps succeeded
        if environment and success:
            success &= self.run_deployment(environment)
        
        # Generate report
        self.generate_report('ci_cd_report.json')
        
        if success:
            logger.info("CI/CD pipeline completed successfully")
            return True
        else:
            logger.error("CI/CD pipeline completed with errors")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='SQL Agent CI/CD Integration')
    parser.add_argument('--config', required=True, help='Path to configuration file')
    parser.add_argument('--environment', help='Environment to deploy to (dev, test, staging, production)')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    parser.add_argument('--skip-security', action='store_true', help='Skip security review')
    parser.add_argument('--report', default='ci_cd_report.json', help='Path to output report file')
    args = parser.parse_args()
    
    ci_cd = CICDIntegration(args.config)
    success = ci_cd.run_pipeline(
        environment=args.environment,
        skip_tests=args.skip_tests,
        skip_security=args.skip_security
    )
    
    # Generate report
    ci_cd.generate_report(args.report)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
