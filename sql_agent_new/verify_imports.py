#!/usr/bin/env python3
"""
Import Verification Script

This script scans all Python files in the project and verifies that import statements
are using the new package structure. It reports any imports that may need to be updated.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Regular expressions for finding imports
IMPORT_PATTERN = re.compile(r'^\s*import\s+([\w\.]+)', re.MULTILINE)
FROM_IMPORT_PATTERN = re.compile(r'^\s*from\s+([\w\.]+)\s+import', re.MULTILINE)

# Old import patterns that should be updated
OLD_IMPORT_PATTERNS = [
    r'scripts\.db',
    r'analysis\.rct_wo_analysis',
    r'config\.',
    r'utils\.'
]

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the given directory and its subdirectories."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def extract_imports(file_path: str) -> Tuple[List[str], List[str]]:
    """Extract all import statements from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all import statements
    direct_imports = IMPORT_PATTERN.findall(content)
    from_imports = FROM_IMPORT_PATTERN.findall(content)
    
    return direct_imports, from_imports

def check_imports(imports: List[str], old_patterns: List[str]) -> List[str]:
    """Check if any imports match the old patterns."""
    problematic_imports = []
    for imp in imports:
        for pattern in old_patterns:
            if re.search(pattern, imp):
                problematic_imports.append(imp)
                break
    return problematic_imports

def suggest_new_import(old_import: str) -> str:
    """Suggest a new import path based on the old import."""
    if 'scripts.db' in old_import:
        return old_import.replace('scripts.db', 'sql_agent.core')
    elif 'analysis.rct_wo_analysis' in old_import:
        return old_import.replace('analysis.rct_wo_analysis', 'sql_agent.analysis.rct_wo')
    elif 'config.' in old_import:
        return old_import.replace('config.', 'sql_agent.config.')
    elif 'utils.' in old_import:
        return old_import.replace('utils.', 'sql_agent.utils.')
    return old_import

def main():
    """Main function."""
    # Define the source directory
    src_dir = os.path.join(os.getcwd(), 'src')
    if not os.path.exists(src_dir):
        print(f"Error: Source directory '{src_dir}' not found.")
        sys.exit(1)
    
    # Find all Python files
    python_files = find_python_files(src_dir)
    print(f"Found {len(python_files)} Python files to check.")
    
    # Check each file for imports
    files_with_issues = 0
    total_issues = 0
    
    for file_path in python_files:
        direct_imports, from_imports = extract_imports(file_path)
        all_imports = direct_imports + from_imports
        
        problematic_imports = check_imports(all_imports, OLD_IMPORT_PATTERNS)
        
        if problematic_imports:
            files_with_issues += 1
            total_issues += len(problematic_imports)
            
            rel_path = os.path.relpath(file_path, os.getcwd())
            print(f"\nFile: {rel_path}")
            print("  Problematic imports:")
            
            for imp in problematic_imports:
                suggestion = suggest_new_import(imp)
                print(f"    - {imp} → {suggestion}")
    
    # Print summary
    print("\nSummary:")
    print(f"  Total Python files checked: {len(python_files)}")
    print(f"  Files with import issues: {files_with_issues}")
    print(f"  Total import issues found: {total_issues}")
    
    if total_issues > 0:
        print("\nRecommendation:")
        print("  Run the update_imports.py script to automatically fix these issues:")
        print("  python update_imports.py --directory src")
    else:
        print("\nAll imports appear to be using the correct package structure.")

if __name__ == "__main__":
    main()
