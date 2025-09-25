#!/usr/bin/env python3
"""
SQL Agent Migration Finalization Script

This script performs the following tasks:
1. Verifies that all necessary files have been migrated
2. Updates import statements in Python files
3. Creates any missing __init__.py files
4. Generates a migration report
"""

import os
import re
import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("migration_finalization.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Regular expressions for finding imports
IMPORT_PATTERN = re.compile(r'^\s*import\s+([\w\.]+)', re.MULTILINE)
FROM_IMPORT_PATTERN = re.compile(r'^\s*from\s+([\w\.]+)\s+import', re.MULTILINE)

# Old import patterns that should be updated
IMPORT_MAPPINGS = {
    r'scripts\.db': 'sql_agent.core',
    r'analysis\.rct_wo_analysis': 'sql_agent.analysis.rct_wo',
    r'config\.': 'sql_agent.config.',
    r'utils\.': 'sql_agent.utils.'
}

def find_files(directory: str, extensions: List[str] = None) -> List[str]:
    """Find all files with the given extensions in the directory and its subdirectories."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if extensions is None or any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the given directory and its subdirectories."""
    return find_files(directory, ['.py'])

def extract_imports(file_path: str) -> Tuple[List[str], List[str]]:
    """Extract all import statements from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all import statements
        direct_imports = IMPORT_PATTERN.findall(content)
        from_imports = FROM_IMPORT_PATTERN.findall(content)
        
        return direct_imports, from_imports
    except Exception as e:
        logger.error(f"Error extracting imports from {file_path}: {e}")
        return [], []

def check_imports(imports: List[str], import_mappings: Dict[str, str]) -> Dict[str, str]:
    """Check if any imports match the old patterns and return mappings for those that do."""
    problematic_imports = {}
    for imp in imports:
        for pattern, replacement in import_mappings.items():
            if re.search(pattern, imp):
                new_import = re.sub(pattern, replacement, imp)
                problematic_imports[imp] = new_import
                break
    return problematic_imports

def update_file_imports(file_path: str, import_mappings: Dict[str, str]) -> Tuple[int, List[str]]:
    """Update import statements in a file based on the provided mappings."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create backup
        backup_path = f"{file_path}.bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Track changes
        changes_made = 0
        changes_list = []
        
        # Update imports
        for pattern, replacement in import_mappings.items():
            # Update "import x.y.z" statements
            import_regex = re.compile(r'^\s*import\s+(.*' + pattern + r'.*?)($|\s+as\s+|\s*#)', re.MULTILINE)
            for match in import_regex.finditer(content):
                old_import = match.group(1)
                new_import = re.sub(pattern, replacement, old_import)
                if old_import != new_import:
                    old_statement = f"import {old_import}"
                    new_statement = f"import {new_import}"
                    content = content.replace(old_statement, new_statement)
                    changes_made += 1
                    changes_list.append(f"{old_statement} → {new_statement}")
            
            # Update "from x.y.z import" statements
            from_regex = re.compile(r'^\s*from\s+(.*' + pattern + r'.*?)\s+import', re.MULTILINE)
            for match in from_regex.finditer(content):
                old_import = match.group(1)
                new_import = re.sub(pattern, replacement, old_import)
                if old_import != new_import:
                    # Need to find the full statement to replace it
                    line_regex = re.compile(r'^\s*from\s+' + re.escape(old_import) + r'\s+import.*$', re.MULTILINE)
                    for line_match in line_regex.finditer(content):
                        old_line = line_match.group(0)
                        new_line = old_line.replace(old_import, new_import)
                        content = content.replace(old_line, new_line)
                        changes_made += 1
                        changes_list.append(f"{old_line.strip()} → {new_line.strip()}")
        
        # Write updated content if changes were made
        if changes_made > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            # Remove backup if no changes were made
            os.remove(backup_path)
        
        return changes_made, changes_list
    except Exception as e:
        logger.error(f"Error updating imports in {file_path}: {e}")
        return 0, []

def create_init_files(directory: str) -> int:
    """Create __init__.py files in all Python package directories."""
    count = 0
    for root, dirs, files in os.walk(directory):
        # Check if this directory contains Python files
        has_py_files = any(f.endswith('.py') for f in files)
        has_init = '__init__.py' in files
        
        if has_py_files and not has_init:
            init_path = os.path.join(root, '__init__.py')
            with open(init_path, 'w', encoding='utf-8') as f:
                package_name = os.path.basename(root)
                f.write(f'"""\n{package_name} package.\n"""\n')
            logger.info(f"Created {init_path}")
            count += 1
    
    return count

def verify_directory_structure(base_dir: str) -> Dict[str, bool]:
    """Verify that all required directories exist."""
    required_dirs = [
        'src/sql_agent',
        'src/sql_agent/core',
        'src/sql_agent/cli',
        'src/sql_agent/analysis',
        'src/sql_agent/analysis/rct_wo',
        'src/sql_agent/utils',
        'src/sql_agent/config',
        'tests',
        'configs',
        'docs',
        'scripts',
        'data',
        'data/Database_tables',
        'examples',
        'logs'
    ]
    
    results = {}
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        exists = os.path.isdir(full_path)
        results[dir_path] = exists
        if not exists:
            logger.warning(f"Required directory not found: {dir_path}")
            os.makedirs(full_path, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    return results

def verify_config_files(base_dir: str) -> Dict[str, bool]:
    """Verify that all required configuration files exist."""
    required_files = [
        'configs/database.json',
        'configs/logging.json',
        'configs/app_config.json',
        'setup.py',
        'README.md',
        'CHANGELOG.md'
    ]
    
    results = {}
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        exists = os.path.isfile(full_path)
        results[file_path] = exists
        if not exists:
            logger.warning(f"Required file not found: {file_path}")
    
    return results

def generate_report(
    base_dir: str,
    dir_results: Dict[str, bool],
    file_results: Dict[str, bool],
    import_stats: Dict[str, int],
    init_files_created: int
) -> str:
    """Generate a migration report."""
    report_path = os.path.join(base_dir, 'migration_report.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# SQL Agent Migration Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Directory Structure\n\n")
        f.write("| Directory | Status |\n")
        f.write("|-----------|--------|\n")
        for dir_path, exists in dir_results.items():
            status = "✅ Exists" if exists else "❌ Missing (Created)"
            f.write(f"| {dir_path} | {status} |\n")
        
        f.write("\n## Configuration Files\n\n")
        f.write("| File | Status |\n")
        f.write("|------|--------|\n")
        for file_path, exists in file_results.items():
            status = "✅ Exists" if exists else "❌ Missing"
            f.write(f"| {file_path} | {status} |\n")
        
        f.write("\n## Import Updates\n\n")
        f.write(f"- Total Python files processed: {import_stats.get('total_files', 0)}\n")
        f.write(f"- Files with updated imports: {import_stats.get('files_updated', 0)}\n")
        f.write(f"- Total import statements updated: {import_stats.get('total_updates', 0)}\n")
        
        f.write("\n## Package Structure\n\n")
        f.write(f"- `__init__.py` files created: {init_files_created}\n")
        
        f.write("\n## Next Steps\n\n")
        f.write("1. Test the reorganized project structure\n")
        f.write("2. Update any remaining references to old file paths\n")
        f.write("3. Clean up backup files after confirming everything works\n")
    
    logger.info(f"Generated migration report: {report_path}")
    return report_path

def main():
    """Main function."""
    # Define the base directory
    base_dir = os.getcwd()
    logger.info(f"Starting migration finalization in {base_dir}")
    
    # Verify directory structure
    logger.info("Verifying directory structure...")
    dir_results = verify_directory_structure(base_dir)
    
    # Verify configuration files
    logger.info("Verifying configuration files...")
    file_results = verify_config_files(base_dir)
    
    # Create __init__.py files
    logger.info("Creating __init__.py files...")
    init_files_created = create_init_files(os.path.join(base_dir, 'src'))
    
    # Find all Python files
    src_dir = os.path.join(base_dir, 'src')
    python_files = find_python_files(src_dir)
    logger.info(f"Found {len(python_files)} Python files to process")
    
    # Update import statements
    import_stats = {
        'total_files': len(python_files),
        'files_updated': 0,
        'total_updates': 0
    }
    
    for file_path in python_files:
        direct_imports, from_imports = extract_imports(file_path)
        all_imports = direct_imports + from_imports
        
        # Check for problematic imports
        import_mappings = {}
        for pattern, replacement in IMPORT_MAPPINGS.items():
            for imp in all_imports:
                if re.search(pattern, imp):
                    import_mappings[pattern] = replacement
        
        # Update imports if needed
        if import_mappings:
            changes, change_list = update_file_imports(file_path, import_mappings)
            if changes > 0:
                import_stats['files_updated'] += 1
                import_stats['total_updates'] += changes
                rel_path = os.path.relpath(file_path, base_dir)
                logger.info(f"Updated {changes} imports in {rel_path}")
                for change in change_list:
                    logger.info(f"  {change}")
    
    # Generate report
    report_path = generate_report(
        base_dir,
        dir_results,
        file_results,
        import_stats,
        init_files_created
    )
    
    logger.info("Migration finalization complete!")
    logger.info(f"See {report_path} for details")

if __name__ == "__main__":
    main()
