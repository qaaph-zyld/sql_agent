#!/usr/bin/env python3
"""
Workspace Reorganization - Implement workspace structure improvements
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

def main():
    print("Starting workspace reorganization...")
    
    # Define base directory
    base_dir = Path(".")
    
    # Create directories if they don't exist
    directories = [
        "docs",
        "logs",
        "config",
        "scripts/core",
        "scripts/reports",
        "scripts/data_quality",
        "scripts/utilities"
    ]
    
    for directory in directories:
        dir_path = base_dir / directory
        if not dir_path.exists():
            print(f"Creating directory: {directory}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # Move documentation files to docs directory
    doc_files = [
        "DATA_QUALITY_README.md",
        "POWER_BI_INTEGRATION.md",
        "integrated-persona.md",
        "project_development_prompt.md",
        "prompt.md",
        "sql-agent-implementation.md",
        "sql-agent-initial-prompt.md",
        "sql-agent-roadmap.md",
        "workspace_structure_complete.md",
        "workspace_structure_analysis.md"
    ]
    
    for doc_file in doc_files:
        src = base_dir / doc_file
        dst = base_dir / "docs" / doc_file
        if src.exists() and not dst.exists():
            print(f"Moving {doc_file} to docs directory")
            shutil.copy2(src, dst)
    
    # Move log files to logs directory
    log_files = [
        "custom_query_analysis.log",
        "dashboard_generator.log",
        "data_lineage.log",
        "data_quality.log",
        "pdf_extraction.log",
        "query_interface.log"
    ]
    
    for log_file in log_files:
        src = base_dir / log_file
        dst = base_dir / "logs" / log_file
        if src.exists() and not dst.exists():
            print(f"Moving {log_file} to logs directory")
            shutil.copy2(src, dst)
    
    # Move configuration files to config directory
    config_files = [
        "config.ini"
    ]
    
    for config_file in config_files:
        src = base_dir / config_file
        dst = base_dir / "config" / config_file
        if src.exists() and not dst.exists():
            print(f"Moving {config_file} to config directory")
            shutil.copy2(src, dst)
    
    # Move core scripts to scripts/core directory
    core_scripts = [
        "changelog_engine.py",
        "validation_suite.py",
        "run_validation.py"
    ]
    
    for script in core_scripts:
        src = base_dir / script
        dst = base_dir / "scripts" / "core" / script
        if src.exists() and not dst.exists():
            print(f"Moving {script} to scripts/core directory")
            shutil.copy2(src, dst)
    
    # Move data quality scripts to scripts/data_quality directory
    data_quality_scripts = [
        "data_quality_core.py",
        "data_quality_manager.py"
    ]
    
    for script in data_quality_scripts:
        src = base_dir / script
        dst = base_dir / "scripts" / "data_quality" / script
        if src.exists() and not dst.exists():
            print(f"Moving {script} to scripts/data_quality directory")
            shutil.copy2(src, dst)
    
    # Move report scripts to scripts/reports directory
    report_scripts = [
        "Inventory_daily_report.py",
        "generate_interactive_dashboard.py"
    ]
    
    for script in report_scripts:
        src = base_dir / script
        dst = base_dir / "scripts" / "reports" / script
        if src.exists() and not dst.exists():
            print(f"Moving {script} to scripts/reports directory")
            shutil.copy2(src, dst)
    
    # Move utility scripts to scripts/utilities directory
    utility_scripts = [
        "query_parameter_interface.py",
        "custom_query_analyzer.py",
        "data_lineage_mapper.py",
        "relationship_mapper.py",
        "enhanced_db_mapper.py",
        "extract_field_info.py",
        "pdf_field_extractor.py"
    ]
    
    for script in utility_scripts:
        src = base_dir / script
        dst = base_dir / "scripts" / "utilities" / script
        if src.exists() and not dst.exists():
            print(f"Moving {script} to scripts/utilities directory")
            shutil.copy2(src, dst)
    
    # Create .gitignore file if it doesn't exist
    gitignore_content = """# Logs
logs/
*.log

# Python cache
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
env/
ENV/

# Generated files
reports/*/
*.xlsx
*.png
*.json

# Configuration
.env
"""
    
    gitignore_path = base_dir / ".gitignore"
    if not gitignore_path.exists():
        print("Creating .gitignore file")
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)
    
    # Create __init__.py files in each directory to make them proper Python packages
    for directory in directories:
        if directory.startswith("scripts"):
            init_file = base_dir / directory / "__init__.py"
            if not init_file.exists():
                print(f"Creating __init__.py in {directory}")
                init_file.touch()
    
    # Update changelog
    update_changelog()
    
    print("\nWorkspace reorganization completed successfully!")
    print("Note: Original files were not deleted, only copied to new locations.")
    print("After verifying the new structure works correctly, you may want to remove the original files.")

def update_changelog():
    """Update changelog with workspace reorganization details"""
    engine = ChangelogEngine("Changelog.md")
    
    # Create files affected list
    files_affected = [
        ChangeVector(
            file_path="docs/",
            change_type=ChangeType.FEATURE,
            operation="NEW",
            impact_level="MEDIUM",
            dependencies=[]
        ),
        ChangeVector(
            file_path="logs/",
            change_type=ChangeType.FEATURE,
            operation="NEW",
            impact_level="MEDIUM",
            dependencies=[]
        ),
        ChangeVector(
            file_path="config/",
            change_type=ChangeType.FEATURE,
            operation="NEW",
            impact_level="MEDIUM",
            dependencies=[]
        ),
        ChangeVector(
            file_path="scripts/",
            change_type=ChangeType.FEATURE,
            operation="NEW",
            impact_level="HIGH",
            dependencies=[]
        ),
        ChangeVector(
            file_path=".gitignore",
            change_type=ChangeType.CONFIG,
            operation="MODIFIED",
            impact_level="LOW",
            dependencies=[]
        ),
        ChangeVector(
            file_path="workspace_reorganization.py",
            change_type=ChangeType.FEATURE,
            operation="NEW",
            impact_level="MEDIUM",
            dependencies=["changelog_engine.py"]
        ),
        ChangeVector(
            file_path="Changelog.md",
            change_type=ChangeType.DOCS,
            operation="MODIFIED",
            impact_level="MEDIUM",
            dependencies=["changelog_engine.py"]
        )
    ]
    
    # Create record
    record = AnswerRecord(
        answer_id=engine.answer_counter,
        timestamp=datetime.now().isoformat(),
        action_type="Workspace Restructuring",
        previous_state="Flat workspace structure with mixed file organization",
        current_state="Hierarchical workspace structure with logical file organization",
        changes_made=[
            "Created directory structure as recommended in workspace_structure_analysis.md",
            "Organized documentation files into docs/ directory",
            "Moved log files to logs/ directory",
            "Relocated configuration files to config/ directory",
            "Categorized Python scripts into functional subdirectories",
            "Created proper Python package structure with __init__.py files",
            "Updated .gitignore to exclude logs and cache files"
        ],
        files_affected=files_affected,
        technical_decisions=[
            "Implemented hierarchical directory structure for improved maintainability",
            "Separated concerns by functionality (core, reports, data quality, utilities)",
            "Preserved original files during transition to ensure system stability",
            "Created proper Python package structure for better imports and modularity"
        ],
        next_actions=[
            "Verify all scripts work correctly with new file paths",
            "Update import statements in Python files to reflect new structure",
            "Remove original files after successful verification",
            "Document new structure in README.md"
        ]
    )
    
    # Update changelog
    engine.update_changelog(record)

if __name__ == "__main__":
    main()
