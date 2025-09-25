#!/usr/bin/env python3
"""
Fix Changelog Numbering
Ensures sequential numbering of answer entries in the changelog file
"""

import re
import sys
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("changelog_fixer")

def fix_changelog_numbering(changelog_path: str) -> bool:
    """Fix the sequential numbering of answer entries in the changelog file"""
    try:
        # Read the changelog file
        with open(changelog_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        logger.info(f"Read {len(lines)} lines from {changelog_path}")
        
        # Find all answer entry lines
        answer_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith('### Answer #'):
                answer_lines.append((i, line.strip()))
                logger.debug(f"Found answer line at {i}: {line.strip()}")
        
        if not answer_lines:
            logger.error("No answer entries found in the changelog")
            return False
        
        logger.info(f"Found {len(answer_lines)} answer entries")
        
        # Extract current answer IDs
        current_ids = []
        for i, line in answer_lines:
            # Extract the ID number from the line
            match = re.search(r'### Answer #(\d+)', line)
            if match:
                current_ids.append(int(match.group(1)))
                logger.debug(f"Extracted ID {match.group(1)} from line: {line}")
            else:
                logger.warning(f"Could not extract ID from line: {line}")
        
        logger.info(f"Current answer IDs: {sorted(current_ids)}")
        
        # Sort answer lines by position in file (reverse order)
        answer_lines.sort(key=lambda x: x[0], reverse=True)
        
        # Assign new sequential IDs starting from 1
        total_entries = len(answer_lines)
        logger.info(f"Total entries: {total_entries}")
        
        # Create a mapping of original positions to new IDs
        # We want Answer #001 to be at the bottom of the file
        position_to_id = {}
        for i, (line_num, _) in enumerate(answer_lines):
            position_to_id[line_num] = total_entries - i
            logger.debug(f"Mapping line {line_num} to ID {total_entries - i}")
        
        # Update the lines with new IDs
        for line_num, line in answer_lines:
            new_id = position_to_id[line_num]
            old_id = "unknown"
            match = re.search(r'### Answer #(\d+)', line)
            if match:
                old_id = match.group(1)
                
            # Format the ID with leading zeros if needed
            if any(len(str(id)) >= 3 for id in current_ids):
                new_id_str = f"{new_id:03d}"
            else:
                new_id_str = str(new_id)
            
            logger.info(f"Changing ID from {old_id} to {new_id_str} at line {line_num}")
            
            # Replace the old ID with the new ID
            new_line = re.sub(r'### Answer #\d+', f'### Answer #{new_id_str}', line)
            # Remove any extra text after the ID
            new_line = re.sub(r'(### Answer #\d+).*', r'\1', new_line)
            
            lines[line_num] = new_line + '\n'
        
        # Write the updated changelog
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        logger.info(f"Fixed changelog numbering. New IDs: {sorted(position_to_id.values())}")
        return True
        
    except Exception as e:
        logger.error(f"Error fixing changelog numbering: {e}")
        return False

def main():
    """Main entry point"""
    workspace_root = Path(__file__).parent.parent.parent
    changelog_path = workspace_root / "Changelog.md"
    
    if not changelog_path.exists():
        logger.error(f"Changelog file not found at {changelog_path}")
        sys.exit(1)
        
    logger.info(f"Fixing changelog numbering in {changelog_path}")
    success = fix_changelog_numbering(str(changelog_path))
    
    if success:
        logger.info("Changelog numbering fixed successfully")
    else:
        logger.error("Failed to fix changelog numbering")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
