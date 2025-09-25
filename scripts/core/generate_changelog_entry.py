#!/usr/bin/env python3
"""
Changelog Entry Generator
Interactive tool to generate properly formatted changelog entries
that comply with the validation requirements.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import argparse
import re

# Add parent directory to path to import scripts.core.changelog_engine as changelog_engine
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector

class ChangelogEntryGenerator:
    """Interactive tool to generate changelog entries"""
    
    def __init__(self, changelog_path: str):
        """Initialize with path to changelog file"""
        self.changelog_path = Path(changelog_path)
        self.changelog_engine = ChangelogEngine()
        
    def get_next_answer_number(self):
        """Determine the next sequential answer number"""
        if not self.changelog_path.exists():
            return 1
            
        content = self.changelog_path.read_text()
        answer_ids = [int(m) for m in re.findall(r'### Answer #(\d+)', content)]
        
        if not answer_ids:
            return 1
        
        return max(answer_ids) + 1
        
    def prompt_for_input(self):
        """Prompt user for changelog entry details"""
        print("\n=== Changelog Entry Generator ===\n")
        
        # Basic entry information
        answer_number = self.get_next_answer_number()
        print(f"Generating entry for Answer #{answer_number:03d}")
        
        action_summary = input("Action Summary: ")
        action_type = input("Action Type [Architecture/Implementation/Modification/Documentation]: ")
        previous_state = input("Previous State: ")
        current_state = input("Current State: ")
        
        # Changes made
        changes_made = []
        print("\nChanges Made (enter empty line to finish):")
        while True:
            change = input("- ")
            if not change:
                break
            changes_made.append(change)
            
        # Files affected
        files_affected = []
        print("\nFiles Affected (enter empty line to finish):")
        print("Format: status:path:impact:category[:dependencies]")
        print("Example: NEW:scripts/core/my_script.py:MEDIUM:Feature Implementation:changelog_engine.py")
        while True:
            file_input = input("> ")
            if not file_input:
                break
                
            try:
                parts = file_input.split(":")
                if len(parts) >= 4:
                    status = parts[0]
                    path = parts[1]
                    impact = parts[2]
                    category = parts[3]
                    deps = parts[4].split(",") if len(parts) > 4 else []
                    
                    files_affected.append(ChangeVector(
                        file_path=path,
                        change_type=status,
                        impact_level=impact,
                        change_category=category,
                        dependencies=deps
                    ))
            except Exception as e:
                print(f"Error parsing file input: {e}")
                
        # Technical decisions
        technical_decisions = []
        print("\nTechnical Decisions (enter empty line to finish):")
        while True:
            decision = input("- ")
            if not decision:
                break
            technical_decisions.append(decision)
            
        # Next actions
        next_actions = []
        print("\nNext Actions Required (enter empty line to finish):")
        while True:
            action = input("- ")
            if not action:
                break
            next_actions.append(action)
            
        return {
            "answer_number": answer_number,
            "action_summary": action_summary,
            "action_type": action_type,
            "previous_state": previous_state,
            "current_state": current_state,
            "changes_made": changes_made,
            "files_affected": files_affected,
            "technical_decisions": technical_decisions,
            "next_actions": next_actions
        }
        
    def generate_entry(self):
        """Generate a changelog entry based on user input"""
        entry_data = self.prompt_for_input()
        
        # Override the answer counter to ensure sequential numbering
        self.changelog_engine.answer_counter = entry_data["answer_number"]
        
        # Generate the entry
        entry = self.changelog_engine.generate_answer_entry(
            action_summary=entry_data["action_summary"],
            action_type=entry_data["action_type"],
            previous_state=entry_data["previous_state"],
            current_state=entry_data["current_state"],
            changes_made=entry_data["changes_made"],
            files_affected=entry_data["files_affected"],
            technical_decisions=entry_data["technical_decisions"],
            next_actions=entry_data["next_actions"]
        )
        
        # Preview the entry
        print("\n=== Generated Entry ===\n")
        print(entry)
        
        # Confirm and add to changelog
        confirm = input("\nAdd this entry to the changelog? (y/n): ")
        if confirm.lower() == 'y':
            self._add_to_changelog(entry)
            print("Entry added to changelog.")
        else:
            print("Entry not added.")
            
    def _add_to_changelog(self, entry: str):
        """Add the entry to the changelog file"""
        if not self.changelog_path.exists():
            # Create new changelog file
            content = "# CHANGELOG.md\n\n## Session: " + datetime.now().strftime("%Y-%m-%d") + "\n\n" + entry
            self.changelog_path.write_text(content)
        else:
            # Add to existing changelog
            content = self.changelog_path.read_text()
            
            # Find the position after the most recent entry
            session_match = re.search(r'## Session:', content)
            if session_match:
                # Insert after the session header and any existing entries
                content_parts = content.split("---\n\n", 1)
                if len(content_parts) > 1:
                    # Insert after the first entry
                    new_content = content_parts[0] + "---\n\n" + entry + content_parts[1]
                else:
                    # Insert after the session header
                    new_content = content_parts[0] + entry
                    
                self.changelog_path.write_text(new_content)
            else:
                # No session header found, append to the end
                new_content = content + "\n\n## Session: " + datetime.now().strftime("%Y-%m-%d") + "\n\n" + entry
                self.changelog_path.write_text(new_content)
                
def main():
    parser = argparse.ArgumentParser(description='Generate a changelog entry')
    parser.add_argument('--changelog', default='Changelog.md', help='Path to changelog file')
    args = parser.parse_args()
    
    generator = ChangelogEntryGenerator(args.changelog)
    generator.generate_entry()
    
if __name__ == "__main__":
    main()
