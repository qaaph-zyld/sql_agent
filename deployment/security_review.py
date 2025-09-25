#!/usr/bin/env python
"""
SQL Agent Security Review

This script performs a security review of the SQL Agent codebase and configuration
to identify potential security issues before deployment.
"""

import os
import sys
import re
import json
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
        logging.FileHandler(os.path.join('logs', 'security_review.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('security_review')

class SecurityReviewer:
    """Performs security reviews of the SQL Agent codebase and configuration."""
    
    def __init__(self, config_path, source_dirs=None):
        """
        Initialize the security reviewer.
        
        Args:
            config_path (str): Path to the configuration file
            source_dirs (list, optional): List of directories to scan
        """
        self.config_path = config_path
        self.config = None
        self.source_dirs = source_dirs or ['scripts', 'app.py']
        self.issues = []
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load the configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    def _add_issue(self, severity, category, description, file_path=None, line_number=None):
        """
        Add a security issue to the list.
        
        Args:
            severity (str): Issue severity (high, medium, low)
            category (str): Issue category
            description (str): Issue description
            file_path (str, optional): Path to the file with the issue
            line_number (int, optional): Line number in the file
        """
        issue = {
            'severity': severity,
            'category': category,
            'description': description
        }
        
        if file_path:
            issue['file_path'] = file_path
        
        if line_number is not None:
            issue['line_number'] = line_number
        
        self.issues.append(issue)
    
    def check_hardcoded_credentials(self):
        """Check for hardcoded credentials in the codebase."""
        logger.info("Checking for hardcoded credentials...")
        
        # Patterns to search for
        patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'passwd\s*=\s*[\'"][^\'"]+[\'"]',
            r'pwd\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
            r'apikey\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        
        # Files to exclude (e.g., test files, documentation)
        exclude_patterns = [
            r'test_',
            r'\.md$',
            r'\.txt$',
            r'\.json$',
            r'__pycache__',
            r'\.git'
        ]
        
        for source_dir in self.source_dirs:
            for root, dirs, files in os.walk(source_dir):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(re.search(pattern, d) for pattern in exclude_patterns)]
                
                for file in files:
                    # Skip excluded files
                    if any(re.search(pattern, file) for pattern in exclude_patterns):
                        continue
                    
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                            for i, line in enumerate(lines):
                                for pattern in patterns:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        # Check if this is in a comment
                                        if '#' in line and line.index('#') < line.find(re.search(pattern, line).group(0)):
                                            continue
                                        
                                        # Check if this is a variable name or placeholder
                                        if '${' in line and '}' in line:
                                            continue
                                        
                                        self._add_issue(
                                            'high',
                                            'hardcoded_credentials',
                                            f"Possible hardcoded credential found: {line.strip()}",
                                            file_path,
                                            i + 1
                                        )
                    except Exception as e:
                        logger.warning(f"Failed to read file {file_path}: {e}")
    
    def check_sql_injection(self):
        """Check for potential SQL injection vulnerabilities."""
        logger.info("Checking for SQL injection vulnerabilities...")
        
        # Patterns to search for
        patterns = [
            r'execute\s*\(\s*[\'"][^\'"]*(SELECT|INSERT|UPDATE|DELETE).*\%.*[\'"]',
            r'execute_query\s*\(\s*[\'"][^\'"]*(SELECT|INSERT|UPDATE|DELETE).*\%.*[\'"]',
            r'execute\s*\(\s*f[\'"].*\{.*\}.*[\'"]',
            r'execute_query\s*\(\s*f[\'"].*\{.*\}.*[\'"]',
            r'cursor\.execute\s*\(\s*[\'"][^\'"]*(SELECT|INSERT|UPDATE|DELETE).*\%.*[\'"]',
            r'cursor\.execute\s*\(\s*f[\'"].*\{.*\}.*[\'"]'
        ]
        
        for source_dir in self.source_dirs:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if not file.endswith('.py'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            for i, line in enumerate(lines):
                                for pattern in patterns:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        # Check if this is in a comment
                                        if '#' in line and line.index('#') < line.find(re.search(pattern, line).group(0)):
                                            continue
                                        
                                        self._add_issue(
                                            'high',
                                            'sql_injection',
                                            f"Potential SQL injection vulnerability: {line.strip()}",
                                            file_path,
                                            i + 1
                                        )
                    except Exception as e:
                        logger.warning(f"Failed to read file {file_path}: {e}")
    
    def check_insecure_configurations(self):
        """Check for insecure configurations."""
        logger.info("Checking for insecure configurations...")
        
        # Check SSL configuration
        if not self.config.get('security', {}).get('use_ssl', True):
            self._add_issue(
                'high',
                'insecure_configuration',
                "SSL is disabled in the configuration",
                self.config_path
            )
        
        # Check authentication configuration
        if not self.config.get('security', {}).get('require_authentication', True):
            self._add_issue(
                'high',
                'insecure_configuration',
                "Authentication is disabled in the configuration",
                self.config_path
            )
        
        # Check session timeout
        session_timeout = self.config.get('security', {}).get('session_timeout_minutes', 0)
        if session_timeout <= 0 or session_timeout > 60:
            self._add_issue(
                'medium',
                'insecure_configuration',
                f"Session timeout is set to {session_timeout} minutes, which is outside the recommended range (1-60 minutes)",
                self.config_path
            )
        
        # Check rate limiting
        rate_limiting = self.config.get('security', {}).get('rate_limiting', {})
        if not rate_limiting:
            self._add_issue(
                'medium',
                'insecure_configuration',
                "Rate limiting is not configured",
                self.config_path
            )
    
    def check_logging_configuration(self):
        """Check for insecure logging configurations."""
        logger.info("Checking logging configuration...")
        
        # Check if sensitive data masking is enabled
        if not self.config.get('logging', {}).get('sensitive_data_masking', False):
            self._add_issue(
                'medium',
                'insecure_logging',
                "Sensitive data masking is not enabled in the logging configuration",
                self.config_path
            )
        
        # Check log retention policy
        retention_days = self.config.get('logging', {}).get('retention_days', 0)
        if retention_days <= 0 or retention_days > 90:
            self._add_issue(
                'low',
                'insecure_logging',
                f"Log retention is set to {retention_days} days, which is outside the recommended range (1-90 days)",
                self.config_path
            )
    
    def run_review(self):
        """Run the security review."""
        logger.info("Starting security review...")
        
        # Run all checks
        self.check_hardcoded_credentials()
        self.check_sql_injection()
        self.check_insecure_configurations()
        self.check_logging_configuration()
        
        # Summarize issues
        high_issues = [issue for issue in self.issues if issue['severity'] == 'high']
        medium_issues = [issue for issue in self.issues if issue['severity'] == 'medium']
        low_issues = [issue for issue in self.issues if issue['severity'] == 'low']
        
        logger.info(f"Security review completed. Found {len(high_issues)} high, {len(medium_issues)} medium, and {len(low_issues)} low severity issues.")
        
        # Return issues
        return self.issues
    
    def generate_report(self, output_file):
        """
        Generate a security review report.
        
        Args:
            output_file (str): Path to the output file
        """
        logger.info(f"Generating security review report: {output_file}")
        
        # Create report
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'issues': self.issues,
            'summary': {
                'high': len([issue for issue in self.issues if issue['severity'] == 'high']),
                'medium': len([issue for issue in self.issues if issue['severity'] == 'medium']),
                'low': len([issue for issue in self.issues if issue['severity'] == 'low']),
                'total': len(self.issues)
            }
        }
        
        # Write report to file
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report written to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write report: {e}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SQL Agent Security Review Tool')
    parser.add_argument('--config', default='config/production_config.json',
                        help='Path to configuration file')
    parser.add_argument('--output', default='security_review_report.json',
                        help='Path to output report file')
    parser.add_argument('--source-dirs', nargs='+', default=['scripts', 'app.py'],
                        help='Directories to scan for security issues')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    # Create security reviewer
    reviewer = SecurityReviewer(args.config, args.source_dirs)
    
    # Run security review
    reviewer.run_review()
    
    # Generate report
    reviewer.generate_report(args.output)
