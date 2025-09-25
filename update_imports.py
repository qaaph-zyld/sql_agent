#!/usr/bin/env python3
"""
SQL Agent Import Path Updater

This script scans Python files in the reorganized project structure
and updates import statements to match the new module organization.
"""

import os
import re
import sys
from pathlib import Path
import datetime

# Define import path mappings (old -> new)
IMPORT_MAPPINGS = {
    # Core functionality
    r'from\s+scripts\.db\.([\w\.]+)\s+import': r'from sql_agent.core.\1 import',
    r'import\s+scripts\.db\.([\w\.]+)': r'import sql_agent.core.\1',
    
    # Utilities
    r'from\s+scripts\.utilities\.([\w\.]+)\s+import': r'from sql_agent.utils.\1 import',
    r'import\s+scripts\.utilities\.([\w\.]+)': r'import sql_agent.utils.\1',
    
    # Analysis
    r'from\s+analysis\.rct_wo_analysis\.([\w\.]+)\s+import': r'from sql_agent.analysis.rct_wo.\1 import',
    r'import\s+analysis\.rct_wo_analysis\.([\w\.]+)': r'import sql_agent.analysis.rct_wo.\1',
    
    # Config
    r'from\s+config\.([\w\.]+)\s+import': r'from sql_agent.config.\1 import',
    r'import\s+config\.([\w\.]+)': r'import sql_agent.config.\1',
    
    # General scripts imports
    r'from\s+scripts\.([\w\.]+)\s+import': r'from sql_agent.\1 import',
    r'import\s+scripts\.([\w\.]+)': r'import sql_agent.\1',
}

def update_imports(file_path):
    """Update import statements in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Apply each import mapping pattern
    for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
        new_content, count = re.subn(old_pattern, new_pattern, content)
        if count > 0:
            content = new_content
            changes_made += count
    
    # Only write the file if changes were made
    if changes_made > 0:
        # Create a backup of the original file
        backup_path = f"{file_path}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Updated {changes_made} import statements in {file_path}")
        print(f"Backup saved to {backup_path}")
        return changes_made
    
    return 0

def scan_directory(directory):
    """Scan a directory for Python files and update imports."""
    total_changes = 0
    total_files = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                changes = update_imports(file_path)
                if changes > 0:
                    total_files += 1
                total_changes += changes
    
    return total_changes, total_files

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python update_imports.py <directory>")
        print("Example: python update_imports.py src")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Scanning {directory} for Python files...")
    total_changes, total_files = scan_directory(directory)
    
    print(f"\nSummary:")
    print(f"- Scanned directory: {directory}")
    print(f"- Updated files: {total_files}")
    print(f"- Total import statements changed: {total_changes}")

if __name__ == "__main__":
    main()
