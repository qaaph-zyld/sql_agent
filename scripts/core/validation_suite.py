#!/usr/bin/env python3
"""
Validation Suite - System integrity verification and quality assurance
Performance monitoring and consistency validation framework
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ValidationLevel(Enum):
    CRITICAL = "Critical System Integrity"
    HIGH = "High Impact Validation"
    MEDIUM = "Standard Verification"
    LOW = "Optional Consistency Check"

@dataclass
class ValidationResult:
    test_name: str
    status: bool
    level: ValidationLevel
    execution_time_ms: float
    error_message: Optional[str] = None
    performance_data: Optional[Dict[str, Any]] = None

@dataclass
class SystemMetrics:
    memory_usage_mb: float
    response_overhead_ms: float
    cache_hit_ratio: float
    storage_efficiency: float
    change_detection_accuracy: float

class ValidationSuite:
    def __init__(self, performance_threshold_ms: float = 50.0):
        self.performance_threshold = performance_threshold_ms
        self.validation_results: List[ValidationResult] = []
        self.system_metrics = SystemMetrics(0, 0, 0, 0, 0)
        
    def validate_changelog_integrity(self, changelog_path: str) -> ValidationResult:
        """Validate changelog structural integrity and consistency"""
        start_time = time.perf_counter()
        
        try:
            changelog = Path(changelog_path)
            if not changelog.exists():
                return ValidationResult(
                    "changelog_integrity",
                    False,
                    ValidationLevel.CRITICAL,
                    (time.perf_counter() - start_time) * 1000,
                    "Changelog file not found"
                )
            
            content = changelog.read_text()
            
            # Validate structure
            has_session_header = "## Session:" in content
            has_answer_entries = "### Answer #" in content
            has_required_sections = all(section in content for section in [
                "#### Changes Made:",
                "#### Files Affected:",
                "#### Technical Decisions:",
                "#### Next Actions Required:"
            ])
            
            # Validate answer numbering sequence
            import re
            answer_ids = [int(m) for m in re.findall(r'### Answer #(\d+)', content)]
            sequential = answer_ids == list(range(1, len(answer_ids) + 1)) if answer_ids else True
            
            success = has_session_header and has_answer_entries and has_required_sections and sequential
            error_msg = None if success else "Changelog structure validation failed"
            
            return ValidationResult(
                "changelog_integrity",
                success,
                ValidationLevel.CRITICAL,
                (time.perf_counter() - start_time) * 1000,
                error_msg
            )
            
        except Exception as e:
            return ValidationResult(
                "changelog_integrity",
                False,
                ValidationLevel.CRITICAL,
                (time.perf_counter() - start_time) * 1000,
                f"Changelog validation error: {str(e)}"
            )
    
    def validate_workspace_consistency(self, workspace_path: str, expected_structure: Dict) -> ValidationResult:
        """Validate workspace structure against expected configuration"""
        start_time = time.perf_counter()
        
        try:
            workspace = Path(workspace_path)
            if not workspace.exists():
                return ValidationResult(
                    "workspace_consistency",
                    False,
                    ValidationLevel.HIGH,
                    (time.perf_counter() - start_time) * 1000,
                    "Workspace directory not found"
                )
            
            # Recursive structure validation
            def validate_structure(current_path: Path, expected: Dict) -> Tuple[bool, List[str]]:
                errors = []
                
                for item_name, item_config in expected.items():
                    item_path = current_path / item_name
                    
                    if isinstance(item_config, dict):
                        if "type" in item_config:
                            if item_config["type"] == "file" and not item_path.is_file():
                                errors.append(f"Missing file: {item_path}")
                            elif item_config["type"] == "directory" and not item_path.is_dir():
                                errors.append(f"Missing directory: {item_path}")
                        else:
                            # Nested directory structure
                            if item_path.is_dir():
                                nested_valid, nested_errors = validate_structure(item_path, item_config)
                                errors.extend(nested_errors)
                            else:
                                errors.append(f"Missing directory: {item_path}")
                
                return len(errors) == 0, errors
            
            is_valid, error_list = validate_structure(workspace, expected_structure)
            
            return ValidationResult(
                "workspace_consistency",
                is_valid,
                ValidationLevel.HIGH,
                (time.perf_counter() - start_time) * 1000,
                "; ".join(error_list) if error_list else None
            )
            
        except Exception as e:
            return ValidationResult(
                "workspace_consistency",
                False,
                ValidationLevel.HIGH,
                (time.perf_counter() - start_time) * 1000,
                f"Workspace validation error: {str(e)}"
            )
    
    def validate_performance_compliance(self, execution_time_ms: float) -> ValidationResult:
        """Validate system performance against defined thresholds"""
        start_time = time.perf_counter()
        
        compliant = execution_time_ms <= self.performance_threshold
        
        performance_data = {
            "execution_time_ms": execution_time_ms,
            "threshold_ms": self.performance_threshold,
            "compliance_ratio": min(execution_time_ms / self.performance_threshold, 2.0)
        }
        
        return ValidationResult(
            "performance_compliance",
            compliant,
            ValidationLevel.MEDIUM,
            (time.perf_counter() - start_time) * 1000,
            f"Performance threshold exceeded: {execution_time_ms}ms > {self.performance_threshold}ms" if not compliant else None,
            performance_data
        )
    
    def validate_change_chain_continuity(self, changelog_path: str) -> ValidationResult:
        """Validate answer chain continuity and state transitions"""
        start_time = time.perf_counter()
        
        try:
            changelog = Path(changelog_path)
            if not changelog.exists():
                return ValidationResult(
                    "change_chain_continuity",
                    False,
                    ValidationLevel.HIGH,
                    (time.perf_counter() - start_time) * 1000,
                    "Changelog not found for chain validation"
                )
            
            content = changelog.read_text()
            
            # Extract answer entries
            import re
            answer_pattern = r'### Answer #(\d+) - (.+?)\n.*?(?=### Answer #|\Z)'
            answers = re.findall(answer_pattern, content, re.DOTALL)
            
            # Validate sequential numbering
            answer_ids = [int(match[0]) for match in answers]
            sequential = answer_ids == list(range(1, len(answer_ids) + 1))
            
            # Validate state transition consistency
            state_transitions = []
            for match in answers:
                answer_content = match[1]
                current_state_match = re.search(r'\*\*Current State:\*\* (.+)', answer_content)
                if current_state_match:
                    state_transitions.append(current_state_match.group(1))
            
            # Check for state evolution (not all identical)
            state_evolution = len(set(state_transitions)) > 1 if state_transitions else False
            
            success = sequential and state_evolution
            error_msg = None
            if not sequential:
                error_msg = "Answer sequence not sequential"
            elif not state_evolution:
                error_msg = "No state evolution detected"
            
            return ValidationResult(
                "change_chain_continuity",
                success,
                ValidationLevel.HIGH,
                (time.perf_counter() - start_time) * 1000,
                error_msg
            )
            
        except Exception as e:
            return ValidationResult(
                "change_chain_continuity",
                False,
                ValidationLevel.HIGH,
                (time.perf_counter() - start_time) * 1000,
                f"Chain continuity validation error: {str(e)}"
            )
    
    def run_comprehensive_validation(self, 
                                   changelog_path: str,
                                   workspace_path: str,
                                   expected_structure: Dict,
                                   execution_time_ms: float) -> Dict[str, ValidationResult]:
        """Execute complete validation suite"""
        
        validations = {
            "changelog_integrity": self.validate_changelog_integrity(changelog_path),
            "workspace_consistency": self.validate_workspace_consistency(workspace_path, expected_structure),
            "performance_compliance": self.validate_performance_compliance(execution_time_ms),
            "change_chain_continuity": self.validate_change_chain_continuity(changelog_path)
        }
        
        self.validation_results = list(validations.values())
        return validations
    
    def generate_validation_report(self, validations: Dict[str, ValidationResult]) -> str:
        """Generate comprehensive validation report"""
        
        critical_failures = [v for v in validations.values() if not v.status and v.level == ValidationLevel.CRITICAL]
        high_failures = [v for v in validations.values() if not v.status and v.level == ValidationLevel.HIGH]
        
        report = f"""# VALIDATION REPORT
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Tests: {len(validations)}
- Passed: {sum(1 for v in validations.values() if v.status)}
- Failed: {sum(1 for v in validations.values() if not v.status)}
- Critical Failures: {len(critical_failures)}
- High Priority Failures: {len(high_failures)}

## Test Results
"""
        
        for test_name, result in validations.items():
            status_icon = "âœ…" if result.status else "âŒ"
            report += f"""
### {test_name.upper()}
{status_icon} **Status:** {'PASS' if result.status else 'FAIL'}
- **Level:** {result.level.value}
- **Execution Time:** {result.execution_time_ms:.2f}ms
"""
            if result.error_message:
                report += f"- **Error:** {result.error_message}\n"
            
            if result.performance_data:
                report += f"- **Performance Data:** {json.dumps(result.performance_data, indent=2)}\n"
        
        if critical_failures or high_failures:
            report += "\n## IMMEDIATE ACTION REQUIRED\n"
            for failure in critical_failures + high_failures:
                report += f"- **{failure.test_name}**: {failure.error_message}\n"
        
        return report
    
    def update_system_metrics(self, 
                            memory_mb: float,
                            response_ms: float,
                            cache_ratio: float,
                            storage_eff: float,
                            accuracy: float) -> None:
        """Update system performance metrics"""
        self.system_metrics = SystemMetrics(
            memory_usage_mb=memory_mb,
            response_overhead_ms=response_ms,
            cache_hit_ratio=cache_ratio,
            storage_efficiency=storage_eff,
            change_detection_accuracy=accuracy
        )

# Usage Example
if __name__ == "__main__":
    validator = ValidationSuite(performance_threshold_ms=50.0)
    
    # Example workspace structure
    expected_structure = {
        "Changelog.md": {"type": "file"},
        "changelog_engine.py": {"type": "file"},
        "validation_suite.py": {"type": "file"},
        "windsurf_rule.md": {"type": "file"}
    }
    
    # Run validation suite
    results = validator.run_comprehensive_validation(
        changelog_path="Changelog.md",
        workspace_path=".",
        expected_structure=expected_structure,
        execution_time_ms=45.0
    )
    
    # Generate report
    report = validator.generate_validation_report(results)
    print(report)
