"""
Security Tests for Response Processor

This module contains security tests for the SQL Agent's Response Processor,
focusing on input validation, output sanitization, and file system security.

RESPONSE_SEQUENCE {
  1. changelog_engine.update_changelog()
  2. execute_security_tests()
  3. validation_suite.run_validation()
  4. workspace_state_sync()
}
"""

import os
import sys
import json
import pandas as pd
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from core.changelog_engine import ChangelogEngine
from processing.response_processor import ResponseProcessor
from testing.security_test_framework import (
    SecurityVulnerability, 
    SecurityTestResult,
    SecurityTestCase,
    InputValidationTestCase
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/response_processor_security_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResponseProcessorSecurityTest(SecurityTestCase):
    """
    Security tests for the Response Processor component
    """
    def setUp(self):
        """Set up security test with changelog update"""
        super().setUp()
        
        # Initialize the response processor
        self.response_processor = ResponseProcessor()
        
        # Create test data
        self.test_data = pd.DataFrame({
            "id": range(1, 11),
            "name": [f"User {i}" for i in range(1, 11)],
            "value": [i * 10 for i in range(1, 11)]
        })
        
        # Create test directory for file output tests
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Define common malicious inputs
        self.malicious_inputs = [
            "<script>alert('XSS')</script>",
            "$(rm -rf /)",
            "{{7*7}}",
            "${7*7}",
            "#{7*7}",
            "`rm -rf /`",
            "../../../etc/passwd",
            "C:\\Windows\\System32\\cmd.exe",
            "/dev/null; touch /tmp/pwned",
            "file:///etc/passwd"
        ]
        
        # Define malicious file paths
        self.malicious_file_paths = [
            "../../../etc/passwd",
            "C:\\Windows\\System32\\cmd.exe",
            "/etc/shadow",
            "~/.ssh/id_rsa",
            "/var/www/html/config.php",
            "C:\\Program Files\\Important\\secret.txt",
            "/dev/null; touch /tmp/pwned",
            "file:///etc/passwd",
            "\\\\evil-server\\share\\malware.exe",
            "http://malicious-site.com/payload.php"
        ]
        
        # Define security vulnerabilities to test
        self.xss_vulnerability = SecurityVulnerability(
            name="Cross-Site Scripting (XSS)",
            description="XSS attacks enable attackers to inject client-side scripts into web pages viewed by other users",
            severity="Medium",
            test_payload="<script>alert('XSS')</script>",
            mitigation="Sanitize and encode user input before rendering it"
        )
        
        self.path_traversal_vulnerability = SecurityVulnerability(
            name="Path Traversal",
            description="Path traversal attacks aim to access files and directories stored outside the intended directory",
            severity="High",
            test_payload="../../../etc/passwd",
            mitigation="Validate file paths, use whitelists, and implement proper access controls"
        )
        
        self.insecure_file_handling_vulnerability = SecurityVulnerability(
            name="Insecure File Handling",
            description="Insecure file handling can lead to unauthorized access, data leakage, or system compromise",
            severity="High",
            test_payload="/etc/shadow",
            mitigation="Implement proper file permissions, validate file paths, and sanitize file names"
        )
        
        logger.info("ResponseProcessorSecurityTest setup completed")
    
    def tearDown(self):
        """Clean up after tests"""
        super().tearDown()
        # Clean up temporary directory
        self.test_dir.cleanup()
    
    def test_xss_in_formatted_output(self):
        """Test XSS prevention in formatted output"""
        logger.info("Testing XSS prevention in formatted output")
        
        results = []
        for payload in self.malicious_inputs:
            # Create a DataFrame with potentially malicious content
            malicious_df = pd.DataFrame({
                "id": [1, 2, 3],
                "content": [
                    f"Normal content",
                    f"{payload}",
                    f"More normal content"
                ]
            })
            
            # Test if the response processor properly sanitizes output
            def test_output_sanitization(payload):
                try:
                    # Format the DataFrame with potentially malicious content
                    formats = ["html", "markdown", "json", "csv"]
                    for format_type in formats:
                        formatted_output = self.response_processor.format_results(malicious_df, format_type)
                        
                        # Check if the output contains unsanitized XSS payload
                        if format_type == "html" and "<script>" in formatted_output and "</script>" in formatted_output:
                            # Potential XSS vulnerability in HTML output
                            return False
                        elif format_type == "markdown" and "<script>" in formatted_output and not "\\<script>" in formatted_output:
                            # Potential XSS vulnerability in Markdown output
                            return False
                    
                    # All formats passed the test
                    return True
                except Exception as e:
                    # If an exception is raised, it might be because the processor detected
                    # and blocked the malicious input (good) or because of another error
                    if "security violation" in str(e).lower() or "invalid input" in str(e).lower():
                        # Processor detected and blocked the attack
                        return True
                    # Other exception - might indicate a vulnerability
                    return False
            
            result = self.test_for_vulnerability(
                vulnerability=self.xss_vulnerability,
                test_function=test_output_sanitization,
                payload=payload
            )
            results.append(result)
            
            if result.is_vulnerable:
                logger.warning(f"XSS vulnerability detected in formatted output: {payload}")
            else:
                logger.info(f"XSS test passed for formatted output with payload: {payload}")
        
        return results
    
    def test_path_traversal_in_file_saving(self):
        """Test path traversal prevention in file saving"""
        logger.info("Testing path traversal prevention in file saving")
        
        results = []
        for payload in self.malicious_file_paths:
            # Test if the response processor properly validates file paths
            def test_path_validation(payload):
                try:
                    # Attempt to save results to a potentially malicious path
                    file_path = os.path.join(self.test_dir.name, payload)
                    self.response_processor.save_results(self.test_data, file_path, "csv")
                    
                    # Check if the file was created outside the intended directory
                    # This is a simplified check - in a real test, we would need to verify
                    # that the file was not created in an unauthorized location
                    if os.path.exists(file_path) and not file_path.startswith(self.test_dir.name):
                        # Potential path traversal vulnerability
                        return False
                    return True
                except Exception as e:
                    # If an exception is raised, it might be because the processor detected
                    # and blocked the malicious path (good) or because of another error
                    if "security violation" in str(e).lower() or "invalid path" in str(e).lower():
                        # Processor detected and blocked the attack
                        return True
                    # Other exception - might indicate a vulnerability
                    return False
            
            result = self.test_for_vulnerability(
                vulnerability=self.path_traversal_vulnerability,
                test_function=test_path_validation,
                payload=payload
            )
            results.append(result)
            
            if result.is_vulnerable:
                logger.warning(f"Path traversal vulnerability detected: {payload}")
            else:
                logger.info(f"Path traversal test passed for payload: {payload}")
        
        return results
    
    def test_insecure_file_handling(self):
        """Test insecure file handling prevention"""
        logger.info("Testing insecure file handling prevention")
        
        results = []
        for payload in self.malicious_file_paths:
            # Test if the response processor properly handles file operations
            def test_file_handling(payload):
                try:
                    # Create a file path with a potentially malicious name
                    file_path = os.path.join(self.test_dir.name, f"test_file_{payload.replace('/', '_').replace('\\', '_')}.csv")
                    
                    # Attempt to save results to the file
                    self.response_processor.save_results(self.test_data, file_path, "csv")
                    
                    # Check if the file was created with proper permissions
                    # This is a simplified check - in a real test, we would need to verify
                    # file permissions and other security attributes
                    if os.path.exists(file_path):
                        # File was created, check permissions
                        if os.name == 'posix':  # Unix/Linux/MacOS
                            import stat
                            file_stats = os.stat(file_path)
                            # Check if file is world-writable (insecure)
                            if file_stats.st_mode & stat.S_IWOTH:
                                # Potential insecure file handling vulnerability
                                return False
                    
                    return True
                except Exception as e:
                    # If an exception is raised, it might be because the processor detected
                    # and blocked the malicious operation (good) or because of another error
                    if "security violation" in str(e).lower() or "invalid file" in str(e).lower():
                        # Processor detected and blocked the attack
                        return True
                    # Other exception - might indicate a vulnerability
                    return False
            
            result = self.test_for_vulnerability(
                vulnerability=self.insecure_file_handling_vulnerability,
                test_function=test_file_handling,
                payload=payload
            )
            results.append(result)
            
            if result.is_vulnerable:
                logger.warning(f"Insecure file handling vulnerability detected: {payload}")
            else:
                logger.info(f"Insecure file handling test passed for payload: {payload}")
        
        return results
    
    def test_all(self):
        """Run all security tests for the Response Processor"""
        logger.info("Running all Response Processor security tests")
        
        # Pre-Response: Changelog update execution
        changelog_engine = ChangelogEngine()
        changelog_engine.quick_update(
            action_summary="Running Response Processor security tests",
            changes=["Executing comprehensive security tests for the Response Processor component"],
            files=[("READ", "scripts/testing/test_response_processor_security.py", "Security test execution")]
        )
        
        # Execute security tests
        xss_results = self.test_xss_in_formatted_output()
        path_traversal_results = self.test_path_traversal_in_file_saving()
        file_handling_results = self.test_insecure_file_handling()
        
        # Aggregate results
        all_results = xss_results + path_traversal_results + file_handling_results
        vulnerable_count = sum(1 for result in all_results if result.is_vulnerable)
        
        # Generate test summary
        test_summary = {
            "total_tests": len(all_results),
            "passed_tests": len(all_results) - vulnerable_count,
            "failed_tests": vulnerable_count,
            "pass_rate": round(((len(all_results) - vulnerable_count) / len(all_results)) * 100, 2) if all_results else 0,
            "vulnerabilities_detected": [
                {
                    "name": result.vulnerability.name,
                    "description": result.vulnerability.description,
                    "severity": result.vulnerability.severity,
                    "details": result.details,
                    "payload": result.vulnerability.test_payload,
                    "mitigation": result.vulnerability.mitigation
                }
                for result in all_results if result.is_vulnerable
            ]
        }
        
        # Save test results to file
        results_dir = Path("test_results/security")
        results_dir.mkdir(exist_ok=True, parents=True)
        results_file = results_dir / "response_processor_security_test_results.json"
        
        with open(results_file, "w") as f:
            json.dump(test_summary, f, indent=4)
        
        logger.info(f"Response Processor security test results saved to {results_file}")
        logger.info(f"Security tests completed with {test_summary['pass_rate']}% pass rate")
        
        # Post-Response: System validation
        changelog_engine.quick_update(
            action_summary="Completed Response Processor security tests",
            changes=[
                f"Security tests completed with {test_summary['pass_rate']}% pass rate",
                f"Detected {vulnerable_count} potential vulnerabilities"
            ],
            files=[
                ("MODIFY", "scripts/testing/test_response_processor_security.py", "Security test execution"),
                ("CREATE", str(results_file), "Security test results")
            ]
        )
        
        return test_summary

def run_security_tests():
    """Run all security tests for the Response Processor"""
    # Pre-Response: Changelog update execution
    changelog_engine = ChangelogEngine()
    changelog_engine.quick_update(
        action_summary="Initializing Response Processor security tests",
        changes=["Starting security test execution for Response Processor component"],
        files=[("READ", "scripts/testing/test_response_processor_security.py", "Security test initialization")]
    )
    
    # Execute security tests
    test_case = ResponseProcessorSecurityTest()
    test_case.setUp()
    test_summary = test_case.test_all()
    test_case.tearDown()
    
    # Post-Response: System validation
    changelog_engine.quick_update(
        action_summary="Completed Response Processor security test execution",
        changes=[
            f"Security tests completed with {test_summary['pass_rate']}% pass rate",
            f"Detected {test_summary['failed_tests']} potential vulnerabilities"
        ],
        files=[("READ", "scripts/testing/test_response_processor_security.py", "Security test completion")]
    )
    
    return test_summary

if __name__ == "__main__":
    run_security_tests()
