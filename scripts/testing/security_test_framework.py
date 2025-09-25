"""
Security Test Framework for SQL Agent

This module provides a framework for security testing of the SQL Agent,
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
from testing.test_framework import SQLAgentTestCase
from typing import Dict, List, Any, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/security_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecurityVulnerability:
    """Class representing a security vulnerability"""
    def __init__(self, 
                 name: str, 
                 description: str, 
                 severity: str, 
                 test_payload: str,
                 mitigation: str):
        """
        Initialize a security vulnerability
        
        Args:
            name: Name of the vulnerability
            description: Description of the vulnerability
            severity: Severity level (HIGH, MEDIUM, LOW)
            test_payload: Test payload to detect the vulnerability
            mitigation: Recommended mitigation strategy
        """
        self.name = name
        self.description = description
        self.severity = severity
        self.test_payload = test_payload
        self.mitigation = mitigation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "test_payload": self.test_payload,
            "mitigation": self.mitigation
        }


class SecurityTestResult:
    """Class representing a security test result"""
    def __init__(self, 
                 vulnerability: SecurityVulnerability,
                 is_vulnerable: bool,
                 details: str = "",
                 evidence: Any = None):
        """
        Initialize a security test result
        
        Args:
            vulnerability: The vulnerability being tested
            is_vulnerable: Whether the system is vulnerable
            details: Details about the test result
            evidence: Evidence of the vulnerability
        """
        self.vulnerability = vulnerability
        self.is_vulnerable = is_vulnerable
        self.details = details
        self.evidence = evidence
        self.timestamp = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "vulnerability": self.vulnerability.to_dict(),
            "is_vulnerable": self.is_vulnerable,
            "details": self.details,
            "evidence": str(self.evidence) if self.evidence else None,
            "timestamp": self.timestamp
        }


class SecurityTestCase(SQLAgentTestCase):
    """Base class for security test cases"""
    def setUp(self):
        """Set up security test with changelog update"""
        super().setUp()
        
        # Create test output directory
        self.output_dir = Path("test_output/security")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Setting up security test environment",
            changes=["Initializing security test case"],
            files=[("CREATE", str(self.output_dir), "Security test output directory")]
        )
    
    def test_for_vulnerability(self, 
                              vulnerability: SecurityVulnerability,
                              test_function: Callable,
                              *args, **kwargs) -> SecurityTestResult:
        """
        Test for a specific vulnerability
        
        Args:
            vulnerability: The vulnerability to test for
            test_function: Function to execute for testing
            *args, **kwargs: Arguments to pass to the test function
            
        Returns:
            SecurityTestResult object with the test results
        """
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary=f"Testing for {vulnerability.name}",
            changes=[f"Executing security test for {vulnerability.name} vulnerability"],
            files=[("READ", "scripts/testing/security_test_framework.py", "Security test execution")]
        )
        
        logger.info(f"Testing for vulnerability: {vulnerability.name}")
        
        try:
            # Execute the test function with the vulnerability payload
            is_vulnerable, details, evidence = test_function(
                vulnerability.test_payload, *args, **kwargs
            )
            
            # Create test result
            result = SecurityTestResult(
                vulnerability=vulnerability,
                is_vulnerable=is_vulnerable,
                details=details,
                evidence=evidence
            )
            
            # Log the result
            if is_vulnerable:
                logger.warning(f"VULNERABILITY DETECTED: {vulnerability.name}")
                logger.warning(f"Details: {details}")
                logger.warning(f"Mitigation: {vulnerability.mitigation}")
            else:
                logger.info(f"No vulnerability detected: {vulnerability.name}")
            
            # Post-Response: System validation
            self.changelog_engine.quick_update(
                action_summary=f"Completed test for {vulnerability.name}",
                changes=[
                    f"{'VULNERABILITY DETECTED' if is_vulnerable else 'No vulnerability detected'}: {vulnerability.name}",
                    f"Severity: {vulnerability.severity}"
                ],
                files=[("READ", "scripts/testing/security_test_framework.py", "Security test execution")]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing for vulnerability {vulnerability.name}: {str(e)}")
            
            # Error Handling: Recovery protocol activation
            self.changelog_engine.quick_update(
                action_summary=f"Error in security test for {vulnerability.name}",
                changes=[f"Exception occurred: {str(e)}"],
                files=[("READ", "scripts/testing/security_test_framework.py", "Security test error")]
            )
            
            # Return a result indicating an error
            return SecurityTestResult(
                vulnerability=vulnerability,
                is_vulnerable=True,  # Assume vulnerable if test fails
                details=f"Error during testing: {str(e)}"
            )
    
    def tearDown(self):
        """Clean up security test with changelog update"""
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Cleaning up security test environment",
            changes=["Completed security test case"],
            files=[("READ", "scripts/testing/security_test_framework.py", "Security test cleanup")]
        )
        
        super().tearDown()


class SQLInjectionTestCase(SecurityTestCase):
    """Test case for SQL injection vulnerabilities"""
    def test_sql_injection_in_query_engine(self):
        """Test for SQL injection vulnerabilities in the query engine"""
        # Import the query engine
        from query.query_engine import QueryEngine
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing SQL injection in query engine",
            changes=["Executing SQL injection tests against query engine"],
            files=[
                ("READ", "scripts/testing/security_test_framework.py", "Security test execution"),
                ("READ", "query/query_engine.py", "Target component for testing")
            ]
        )
        
        # Create query engine
        query_engine = QueryEngine()
        
        # Define SQL injection vulnerabilities to test
        vulnerabilities = [
            SecurityVulnerability(
                name="Basic SQL Injection",
                description="Testing for basic SQL injection vulnerabilities",
                severity="HIGH",
                test_payload="SELECT * FROM users WHERE id = 1 OR 1=1",
                mitigation="Use parameterized queries or prepared statements"
            ),
            SecurityVulnerability(
                name="Union-Based SQL Injection",
                description="Testing for union-based SQL injection vulnerabilities",
                severity="HIGH",
                test_payload="SELECT * FROM users UNION SELECT username, password FROM admin",
                mitigation="Validate and sanitize all user inputs, use parameterized queries"
            ),
            SecurityVulnerability(
                name="Error-Based SQL Injection",
                description="Testing for error-based SQL injection vulnerabilities",
                severity="MEDIUM",
                test_payload="SELECT * FROM users WHERE id = 1 AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(VERSION(), FLOOR(RAND(0)*2)) AS x FROM information_schema.tables GROUP BY x) y)",
                mitigation="Implement proper error handling and avoid exposing database errors"
            ),
            SecurityVulnerability(
                name="Blind SQL Injection",
                description="Testing for blind SQL injection vulnerabilities",
                severity="HIGH",
                test_payload="SELECT * FROM users WHERE id = 1 AND (SELECT 1 FROM users WHERE username = 'admin' AND LENGTH(password) > 5)",
                mitigation="Use parameterized queries and implement input validation"
            )
        ]
        
        # Test each vulnerability
        results = []
        for vulnerability in vulnerabilities:
            # Define test function for query engine
            def test_query_engine(payload):
                try:
                    # Attempt to validate the payload as a query
                    validation_result = query_engine.validate_query(payload)
                    
                    # If validation passes for a malicious query, it might be vulnerable
                    is_vulnerable = validation_result
                    details = "Query engine accepted a potentially malicious query"
                    evidence = {"validation_result": validation_result, "query": payload}
                    
                    return is_vulnerable, details, evidence
                except Exception as e:
                    # If validation raises an exception, it might be properly rejecting the payload
                    is_vulnerable = False
                    details = f"Query engine rejected the malicious query: {str(e)}"
                    evidence = {"error": str(e), "query": payload}
                    
                    return is_vulnerable, details, evidence
            
            # Test the vulnerability
            result = self.test_for_vulnerability(vulnerability, test_query_engine)
            results.append(result)
        
        # Save results to file
        results_file = self.output_dir / "sql_injection_results.json"
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed SQL injection tests",
            changes=[
                f"Executed {len(results)} SQL injection tests",
                f"Vulnerabilities detected: {sum(1 for r in results if r.is_vulnerable)}"
            ],
            files=[
                ("READ", "scripts/testing/security_test_framework.py", "Security test execution"),
                ("CREATE", str(results_file), "Security test results")
            ]
        )


class InputValidationTestCase(SecurityTestCase):
    """Test case for input validation vulnerabilities"""
    def test_input_validation_in_response_processor(self):
        """Test for input validation vulnerabilities in the response processor"""
        # Import the response processor
        from processing.response_processor import ResponseProcessor
        
        # Pre-Response: Changelog update execution
        self.changelog_engine.quick_update(
            action_summary="Testing input validation in response processor",
            changes=["Executing input validation tests against response processor"],
            files=[
                ("READ", "scripts/testing/security_test_framework.py", "Security test execution"),
                ("READ", "processing/response_processor.py", "Target component for testing")
            ]
        )
        
        # Create response processor
        response_processor = ResponseProcessor()
        
        # Define input validation vulnerabilities to test
        vulnerabilities = [
            SecurityVulnerability(
                name="Path Traversal",
                description="Testing for path traversal vulnerabilities",
                severity="HIGH",
                test_payload="../../etc/passwd",
                mitigation="Validate file paths and use path sanitization"
            ),
            SecurityVulnerability(
                name="Command Injection",
                description="Testing for command injection vulnerabilities",
                severity="HIGH",
                test_payload="filename; rm -rf /",
                mitigation="Avoid using user input in system commands, use allowlists"
            ),
            SecurityVulnerability(
                name="XSS in Output",
                description="Testing for cross-site scripting in output",
                severity="MEDIUM",
                test_payload="<script>alert('XSS')</script>",
                mitigation="Sanitize output data, especially in HTML contexts"
            ),
            SecurityVulnerability(
                name="Large Input DoS",
                description="Testing for denial of service via large inputs",
                severity="MEDIUM",
                test_payload="A" * 1000000,  # 1 million characters
                mitigation="Implement input size limits and timeouts"
            )
        ]
        
        # Test each vulnerability
        results = []
        for vulnerability in vulnerabilities:
            # Define test function for response processor
            def test_response_processor(payload):
                try:
                    # For path traversal and command injection
                    if "Path Traversal" in vulnerability.name or "Command Injection" in vulnerability.name:
                        # Try to save results with a malicious filename
                        import pandas as pd
                        df = pd.DataFrame({"test": [1, 2, 3]})
                        
                        try:
                            # This should fail or sanitize the path
                            response_processor.save_results(df, filename=payload, format_type="csv")
                            is_vulnerable = True
                            details = "Response processor accepted a potentially malicious filename"
                            evidence = {"filename": payload}
                        except Exception as e:
                            is_vulnerable = False
                            details = f"Response processor rejected the malicious filename: {str(e)}"
                            evidence = {"error": str(e), "filename": payload}
                    
                    # For XSS
                    elif "XSS" in vulnerability.name:
                        # Try to format results with malicious data
                        import pandas as pd
                        df = pd.DataFrame({"test": [payload]})
                        
                        # This should sanitize the output
                        output = response_processor.format_results(df, format_type="html")
                        is_vulnerable = payload in output and "<script>" in output
                        details = "Response processor did not sanitize HTML output" if is_vulnerable else "Response processor properly sanitized HTML output"
                        evidence = {"output": output[:100] + "..." if len(output) > 100 else output}
                    
                    # For DoS
                    elif "DoS" in vulnerability.name:
                        # Try to process a very large input
                        import pandas as pd
                        import time
                        
                        # Create a large DataFrame
                        df = pd.DataFrame({"test": [payload]})
                        
                        # Measure processing time
                        start_time = time.time()
                        response_processor.format_results(df, format_type="json")
                        processing_time = time.time() - start_time
                        
                        # If processing takes too long, it might be vulnerable to DoS
                        is_vulnerable = processing_time > 5  # 5 seconds threshold
                        details = f"Response processor took {processing_time:.2f} seconds to process large input"
                        evidence = {"processing_time": processing_time, "input_size": len(payload)}
                    
                    else:
                        is_vulnerable = False
                        details = "No specific test for this vulnerability type"
                        evidence = None
                    
                    return is_vulnerable, details, evidence
                
                except Exception as e:
                    # If an unexpected exception occurs, log it
                    is_vulnerable = True
                    details = f"Unexpected error during testing: {str(e)}"
                    evidence = {"error": str(e), "payload": payload[:100] + "..." if len(payload) > 100 else payload}
                    
                    return is_vulnerable, details, evidence
            
            # Test the vulnerability
            result = self.test_for_vulnerability(vulnerability, test_response_processor)
            results.append(result)
        
        # Save results to file
        results_file = self.output_dir / "input_validation_results.json"
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Post-Response: System validation
        self.changelog_engine.quick_update(
            action_summary="Completed input validation tests",
            changes=[
                f"Executed {len(results)} input validation tests",
                f"Vulnerabilities detected: {sum(1 for r in results if r.is_vulnerable)}"
            ],
            files=[
                ("READ", "scripts/testing/security_test_framework.py", "Security test execution"),
                ("CREATE", str(results_file), "Security test results")
            ]
        )


def run_security_tests():
    """Run all security tests"""
    # Create changelog engine
    changelog_engine = ChangelogEngine()
    
    # Pre-Response: Changelog update execution
    changelog_engine.quick_update(
        action_summary="Running security tests",
        changes=["Executing security test suite"],
        files=[("READ", "scripts/testing/security_test_framework.py", "Security test execution")]
    )
    
    # Import unittest
    import unittest
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(SQLInjectionTestCase))
    suite.addTest(unittest.makeSuite(InputValidationTestCase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)
    
    # Process results
    test_results = {
        "total_tests": results.testsRun,
        "passed_tests": results.testsRun - len(results.failures) - len(results.errors),
        "failed_tests": len(results.failures) + len(results.errors),
        "failures": [str(failure) for failure in results.failures],
        "errors": [str(error) for error in results.errors]
    }
    
    # Calculate pass rate
    test_results["pass_rate"] = round((test_results["passed_tests"] / test_results["total_tests"]) * 100, 2) if test_results["total_tests"] > 0 else 0
    
    # Save results to file
    output_dir = Path("test_output/security")
    output_dir.mkdir(exist_ok=True, parents=True)
    results_file = output_dir / "security_test_results.json"
    
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2)
    
    # Post-Response: System validation
    changelog_engine.quick_update(
        action_summary="Completed security tests",
        changes=[
            f"Executed {test_results['total_tests']} security tests",
            f"Pass rate: {test_results['pass_rate']}%",
            f"Vulnerabilities detected: {test_results['failed_tests']}"
        ],
        files=[
            ("READ", "scripts/testing/security_test_framework.py", "Security test execution"),
            ("CREATE", str(results_file), "Security test results")
        ]
    )
    
    return test_results


if __name__ == "__main__":
    run_security_tests()
