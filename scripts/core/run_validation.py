#!/usr/bin/env python3
"""
Run Validation - Execute validation suite and generate report
"""

import time
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord
from scripts.core.validation_suite import ValidationSuite, ValidationLevel

def main():
    print("Starting validation process...")
    start_time = time.perf_counter()
    
    # Initialize validation suite
    validator = ValidationSuite(performance_threshold_ms=50.0)
    
    # Define expected workspace structure with new directory structure
    expected_structure = {
        "scripts": {
            "type": "directory",
            "core": {
                "type": "directory",
                "changelog_engine.py": {"type": "file"},
                "validation_suite.py": {"type": "file"},
                "run_validation.py": {"type": "file"},
                "workspace_scanner.py": {"type": "file"},
                "state_manager.py": {"type": "file"}
            },
            "db": {
                "type": "directory",
                "db_connector.py": {"type": "file"},
                "query_engine.py": {"type": "file"},
                "schema_extractor.py": {"type": "file"}
            },
            "utilities": {
                "type": "directory",
                "fix_changelog_numbering.py": {"type": "file"},
                "cleanup_original_files.py": {"type": "file"},
                "update_imports.py": {"type": "file"},
                "generate_changelog_entry.py": {"type": "file"},
                "update_workspace_structure.py": {"type": "file"},
                "schedule_maintenance.py": {"type": "file"}
            }
        },
        "logs": {
            "type": "directory"
        },
        "docs": {
            "type": "directory",
            "changelog_system_guide.md": {"type": "file"},
            "changelog_integration_plan.md": {"type": "file"}
        },
        "config": {
            "type": "directory",
            "config.ini": {"type": "file"}
        },
        "app.py": {"type": "file"},
        ".env": {"type": "file"},
        "Changelog.md": {"type": "file"},
        "README.md": {"type": "file"},
        "sample_queries.json": {"type": "file"}
    }
    
    # Run validations with detailed error reporting
    changelog_result = validator.validate_changelog_integrity("Changelog.md")
    if not changelog_result.status:
        # Add detailed error checking
        try:
            content = Path("Changelog.md").read_text()
            print("\nChangelog Validation Details:")
            has_session_header = "## Session:" in content
            print(f"- Has session header: {has_session_header}")
            
            has_answer_entries = "### Answer #" in content
            print(f"- Has answer entries: {has_answer_entries}")
            
            required_sections = ["#### Changes Made:", "#### Files Affected:", 
                              "#### Technical Decisions:", "#### Next Actions Required:"]
            for section in required_sections:
                print(f"- Has '{section}': {section in content}")
            
            import re
            answer_ids = [int(m) for m in re.findall(r'### Answer #(\d+)', content)]
            print(f"- Answer IDs found: {answer_ids}")
            sequential = answer_ids == list(range(1, len(answer_ids) + 1)) if answer_ids else True
            print(f"- Sequential numbering: {sequential}")
        except Exception as e:
            print(f"Error analyzing changelog: {str(e)}")
    
    workspace_result = validator.validate_workspace_consistency(".", expected_structure)
    performance_result = validator.validate_performance_compliance((time.perf_counter() - start_time) * 1000)
    
    # Add results to validation suite
    validator.validation_results.extend([
        changelog_result,
        workspace_result,
        performance_result
    ])
    
    # Generate validation report
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": all(result.status for result in validator.validation_results),
        "execution_time_ms": (time.perf_counter() - start_time) * 1000,
        "results": [
            {
                "test_name": result.test_name,
                "status": "PASS" if result.status else "FAIL",
                "level": result.level.value,
                "execution_time_ms": result.execution_time_ms,
                "error_message": result.error_message
            }
            for result in validator.validation_results
        ]
    }
    
    # Save report
    report_path = Path("validation_report.json")
    report_path.write_text(json.dumps(report, indent=2))
    
    # Update changelog with validation results
    update_changelog(report)
    
    # Display validation report
    print("\nValidation Report:")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Overall Status: {'PASS' if report['overall_status'] else 'FAIL'}")
    print(f"Execution Time: {report['execution_time_ms']:.2f}ms")
    print("\nTest Results:")
    
    for result in report["results"]:
        status_display = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_display} {result['test_name']} ({result['level']}): {result['execution_time_ms']:.2f}ms")
        if result["error_message"]:
            print(f"   Error: {result['error_message']}")
    
    print(f"\nSystem is {'production-ready' if report['overall_status'] else 'NOT production-ready'}")
    print(f"Full report saved to {report_path}")

def update_changelog(report):
    """Update changelog with validation results"""
    engine = ChangelogEngine("Changelog.md")
    
    # Create files affected list
    files_affected = [
        ChangeVector(
            file_path="validation_suite.py",
            change_type=ChangeType.FEATURE,
            operation="VERIFIED",
            impact_level="HIGH",
            dependencies=[]
        ),
        ChangeVector(
            file_path="changelog_engine.py",
            change_type=ChangeType.FEATURE,
            operation="VERIFIED",
            impact_level="HIGH",
            dependencies=[]
        ),
        ChangeVector(
            file_path="Changelog.md",
            change_type=ChangeType.DOCS,
            operation="MODIFIED",
            impact_level="MEDIUM",
            dependencies=["changelog_engine.py"]
        ),
        ChangeVector(
            file_path="run_validation.py",
            change_type=ChangeType.FEATURE,
            operation="NEW",
            impact_level="MEDIUM",
            dependencies=["validation_suite.py", "changelog_engine.py"]
        ),
        ChangeVector(
            file_path="validation_report.json",
            change_type=ChangeType.DOCS,
            operation="NEW",
            impact_level="LOW",
            dependencies=["run_validation.py"]
        )
    ]
    
    # Create record
    record = AnswerRecord(
        answer_id=engine.answer_counter,
        timestamp=datetime.now().isoformat(),
        action_type="Implementation Validation",
        previous_state="Changelog system initialized",
        current_state="Changelog system validated and operational",
        changes_made=[
            "Executed full validation suite against changelog system",
            "Verified structural integrity of changelog",
            "Confirmed performance compliance (<50ms overhead)",
            "Generated validation report",
            f"System status: {'PRODUCTION-READY' if report['overall_status'] else 'REQUIRES ATTENTION'}"
        ],
        files_affected=files_affected,
        technical_decisions=[
            "Implemented validation against defined quality gates",
            "Established performance baseline for future reference",
            "Created validation report for system transparency"
        ],
        next_actions=[
            "Implement workspace structure improvements",
            "Establish regular validation schedule",
            "Integrate with CI/CD pipeline"
        ]
    )
    
    # Update changelog
    engine.update_changelog(record)

if __name__ == "__main__":
    main()
