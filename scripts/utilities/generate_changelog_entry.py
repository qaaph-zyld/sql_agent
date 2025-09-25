#!/usr/bin/env python3
"""
Generate Changelog Entry - Interactive tool for creating properly formatted changelog entries
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from enum import Enum
import argparse

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.core.changelog_engine import ChangelogEngine, ChangeVector, ChangeType, AnswerRecord

class InteractiveChangelogGenerator:
    def __init__(self):
        self.engine = ChangelogEngine()
        self.action_summary = ""
        self.action_type = ""
        self.previous_state = ""
        self.current_state = ""
        self.changes_made = []
        self.files_affected = []
        self.technical_decisions = []
        self.next_actions = []
    
    def prompt(self, message, default=None):
        """Prompt user for input with optional default value"""
        if default:
            user_input = input(f"{message} [{default}]: ")
            return user_input if user_input else default
        else:
            return input(f"{message}: ")
    
    def prompt_list(self, message, stop_word="done"):
        """Prompt for a list of items until user enters stop word"""
        print(f"{message} (enter '{stop_word}' when finished):")
        items = []
        while True:
            item = input("> ")
            if item.lower() == stop_word.lower():
                break
            items.append(item)
        return items
    
    def prompt_file_change(self):
        """Prompt for file change details"""
        file_path = self.prompt("File path")
        if not file_path:
            return None
        
        print("Change type options:")
        for ct in ChangeType:
            print(f"  {ct.name}: {ct.value}")
        
        change_type_str = self.prompt("Change type", "FEATURE")
        try:
            change_type = ChangeType[change_type_str.upper()]
        except KeyError:
            print(f"Invalid change type. Using FEATURE as default.")
            change_type = ChangeType.FEATURE
        
        operation = self.prompt("Operation (NEW, MODIFIED, REMOVED)", "MODIFIED")
        impact_level = self.prompt("Impact level (LOW, MEDIUM, HIGH)", "LOW")
        dependencies = self.prompt_list("Dependencies", "none")
        if len(dependencies) == 0 or (len(dependencies) == 1 and dependencies[0].lower() == "none"):
            dependencies = []
        
        return ChangeVector(
            file_path=file_path,
            change_type=change_type,
            operation=operation,
            impact_level=impact_level,
            dependencies=dependencies
        )
    
    def collect_information(self):
        """Collect all required information for changelog entry"""
        print("\n=== Changelog Entry Generator ===\n")
        
        self.action_summary = self.prompt("Action summary")
        self.action_type = self.prompt("Action type (Architecture, Implementation, Modification, Documentation)", "Implementation")
        self.previous_state = self.prompt("Previous state", "System ready for modification")
        self.current_state = self.prompt("Current state", f"System updated with {self.action_summary}")
        
        self.changes_made = self.prompt_list("Changes made")
        
        print("\nFiles affected (enter file details, 'done' when finished):")
        while True:
            file_change = self.prompt_file_change()
            if not file_change:
                break
            self.files_affected.append(file_change)
            print("File added. Add another? (Enter to continue, 'done' to finish)")
            if input() == "done":
                break
        
        self.technical_decisions = self.prompt_list("Technical decisions")
        self.next_actions = self.prompt_list("Next actions required")
    
    def generate_entry(self):
        """Generate and return changelog entry"""
        if not self.action_summary:
            self.collect_information()
        
        record = AnswerRecord(
            answer_id=self.engine.answer_counter,
            timestamp=datetime.now().isoformat(),
            action_type=self.action_type,
            previous_state=self.previous_state,
            current_state=self.current_state,
            changes_made=self.changes_made,
            files_affected=self.files_affected,
            technical_decisions=self.technical_decisions,
            next_actions=self.next_actions
        )
        
        return self.engine.generate_answer_entry(
            self.action_summary,
            record.action_type,
            record.previous_state,
            record.current_state,
            record.changes_made,
            record.files_affected,
            record.technical_decisions,
            record.next_actions
        )
    
    def update_changelog(self):
        """Update changelog with new entry"""
        if not self.action_summary:
            self.collect_information()
        
        record = AnswerRecord(
            answer_id=self.engine.answer_counter,
            timestamp=datetime.now().isoformat(),
            action_type=self.action_type,
            previous_state=self.previous_state,
            current_state=self.current_state,
            changes_made=self.changes_made,
            files_affected=self.files_affected,
            technical_decisions=self.technical_decisions,
            next_actions=self.next_actions
        )
        
        self.engine.update_changelog(record)
        print(f"\nChangelog updated successfully. New answer ID: #{self.engine.answer_counter-1:03d}")

def main():
    parser = argparse.ArgumentParser(description="Generate a changelog entry")
    parser.add_argument("--preview", action="store_true", help="Preview entry without updating changelog")
    parser.add_argument("--from-json", type=str, help="Load entry data from JSON file")
    args = parser.parse_args()
    
    generator = InteractiveChangelogGenerator()
    
    if args.from_json:
        try:
            with open(args.from_json, 'r') as f:
                data = json.load(f)
                
            generator.action_summary = data.get("action_summary", "")
            generator.action_type = data.get("action_type", "Implementation")
            generator.previous_state = data.get("previous_state", "")
            generator.current_state = data.get("current_state", "")
            generator.changes_made = data.get("changes_made", [])
            generator.technical_decisions = data.get("technical_decisions", [])
            generator.next_actions = data.get("next_actions", [])
            
            # Process files affected
            files = data.get("files_affected", [])
            for file_data in files:
                try:
                    change_type = ChangeType[file_data.get("change_type", "FEATURE").upper()]
                except KeyError:
                    change_type = ChangeType.FEATURE
                
                generator.files_affected.append(ChangeVector(
                    file_path=file_data.get("file_path", ""),
                    change_type=change_type,
                    operation=file_data.get("operation", "MODIFIED"),
                    impact_level=file_data.get("impact_level", "LOW"),
                    dependencies=file_data.get("dependencies", [])
                ))
            
            print(f"Loaded entry data from {args.from_json}")
        except Exception as e:
            print(f"Error loading JSON file: {str(e)}")
            return
    else:
        generator.collect_information()
    
    if args.preview:
        entry = generator.generate_entry()
        print("\n=== Generated Entry ===\n")
        print(entry)
    else:
        generator.update_changelog()

if __name__ == "__main__":
    main()
