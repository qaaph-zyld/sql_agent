# SQL Agent Project Reorganization - Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the SQL Agent project reorganization according to the dev_framework structure and best practices. The reorganization transforms the current mixed structure into a standardized Python package structure with clear separation of concerns.

## Prerequisites

Before beginning the reorganization, ensure you have:

1. Committed all current changes to version control (if using Git)
2. Created a backup of your entire project
3. Administrator privileges on your system (for creating directories and files)
4. PowerShell and Python installed

## Implementation Steps

### Step 1: Review the Migration Plan

1. Open and review the `migration_plan.md` file to understand the overall reorganization strategy
2. Familiarize yourself with the new directory structure and file organization

### Step 2: Execute the Migration Script

The PowerShell migration script (`migrate_project.ps1`) will create the new directory structure and copy files to their new locations.

```powershell
# Open PowerShell as Administrator
# Navigate to your project directory
cd "c:\Users\ajelacn\OneDrive - Adient\Documents\Projects\SQL_scripts\SQL_agent"

# Run the migration script
.\migrate_project.ps1
```

This script will:
- Create the new directory structure
- Copy files to their new locations
- Create necessary package files (setup.py, requirements.txt)
- Update README.md and CHANGELOG.md
- Create backups of modified files

### Step 3: Update Import Statements

After the directory structure is reorganized, you need to update import statements in Python files to reflect the new module organization.

```powershell
# Run the import updater script
python update_imports.py src
```

This script will:
- Scan all Python files in the specified directory
- Update import statements based on predefined patterns
- Create backups of modified files
- Report the number of changes made

### Step 4: Test the Reorganized Project

After completing the reorganization, test that everything works correctly:

1. Create and activate a new virtual environment:
   ```powershell
   python -m venv venv_new
   .\venv_new\Scripts\Activate
   ```

2. Install the package in development mode:
   ```powershell
   pip install -e .
   ```

3. Verify that the package can be imported:
   ```python
   python -c "import sql_agent; print('Import successful!')"
   ```

4. Test key functionality:
   ```powershell
   # Run the RCT-WO analysis
   python -m sql_agent.analysis.rct_wo.analysis
   ```

### Step 5: Clean Up

After verifying that everything works correctly, you can clean up temporary files:

1. Remove backup files if no longer needed
2. Update any documentation or scripts that reference the old file structure
3. Commit the reorganized project to version control

## Troubleshooting

### Import Errors

If you encounter import errors after reorganization:

1. Check that the file exists in the expected location
2. Verify that `__init__.py` files are present in all package directories
3. Check for typos in import statements
4. Ensure the package is installed in development mode (`pip install -e .`)

### Missing Files

If files are missing after reorganization:

1. Check the migration log file (`migration_log_*.txt`) for any errors
2. Verify that the source files existed before migration
3. Check file permissions

### Package Installation Issues

If you have issues installing the package:

1. Verify that `setup.py` is correctly formatted
2. Check that all dependencies are available
3. Ensure you have the necessary permissions to install packages

## Rollback Plan

If you need to roll back the reorganization:

1. If using version control, revert to the previous commit
2. Otherwise, restore from your backup
3. Delete any new directories and files created during reorganization

## Next Steps

After successfully reorganizing the project:

1. Update any CI/CD pipelines to work with the new structure
2. Update documentation to reflect the new organization
3. Train team members on the new project structure
4. Consider implementing additional best practices from the dev_framework

## Conclusion

This reorganization aligns your SQL Agent project with industry standard Python project structures and best practices. The new structure provides better separation of concerns, improved maintainability, and a more developer-friendly codebase.

If you have any questions or encounter issues during the reorganization process, refer to the migration plan and log files for guidance.
