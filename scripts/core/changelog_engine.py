#!/usr/bin/env python3
"""
Changelog Engine - Automated changelog generation and management
Core component of production changelog system architecture
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ChangeType(Enum):
    FEATURE = "Feature Implementation"
    REFACTOR = "Code/Structure Optimization"
    FIX = "Error Correction"
    DOCS = "Documentation Modification"
    CONFIG = "Configuration Adjustment"
    REMOVE = "Asset Elimination"

@dataclass
class ChangeVector:
    file_path: str
    change_type: ChangeType
    operation: str  # NEW, MODIFIED, REMOVED
    impact_level: str  # LOW, MEDIUM, HIGH
    dependencies: List[str]
    
@dataclass
class AnswerRecord:
    answer_id: int
    timestamp: str
    action_type: str
    previous_state: str
    current_state: str
    changes_made: List[str]
    files_affected: List[ChangeVector]
    technical_decisions: List[str]
    next_actions: List[str]

class ChangelogEngine:
    def __init__(self, changelog_path: str = "Changelog.md"):
        self.changelog_path = Path(changelog_path)
        self.session_date = datetime.now().strftime("%Y-%m-%d")
        self.answer_counter = self._get_last_answer_id() + 1
        
    def _get_last_answer_id(self) -> int:
        """Extract last answer ID from existing changelog"""
        if not self.changelog_path.exists():
            return 0
        
        content = self.changelog_path.read_text()
        import re
        matches = re.findall(r'### Answer #(\d+)', content)
        return max([int(m) for m in matches]) if matches else 0
    
    def generate_answer_entry(self, 
                            action_summary: str,
                            action_type: str,
                            previous_state: str,
                            current_state: str,
                            changes_made: List[str],
                            files_affected: List[ChangeVector],
                            technical_decisions: List[str],
                            next_actions: List[str]) -> str:
        """Generate formatted changelog entry"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        entry = f"""### Answer #{self.answer_counter:03d} - {action_summary}
**Timestamp:** {timestamp}
**Action Type:** {action_type}
**Previous State:** {previous_state}
**Current State:** {current_state}

#### Changes Made:
{chr(10).join(f'- {change}' for change in changes_made)}

#### Files Affected:
{self._format_files_affected(files_affected)}

#### Technical Decisions:
{chr(10).join(f'- {decision}' for decision in technical_decisions)}

#### Next Actions Required:
{chr(10).join(f'- {action}' for action in next_actions)}

---

"""
        return entry
    
    def _format_files_affected(self, files: List[ChangeVector]) -> str:
        """Format files affected section"""
        if not files:
            return "- No files modified"
        
        formatted = []
        for file_change in files:
            impact = f"[{file_change.impact_level}]" if file_change.impact_level != "LOW" else ""
            deps = f" (deps: {', '.join(file_change.dependencies)})" if file_change.dependencies else ""
            formatted.append(f"- **{file_change.operation}:** {file_change.file_path} - {file_change.change_type.value}{impact}{deps}")
        
        return chr(10).join(formatted)
    
    def update_changelog(self, answer_record: AnswerRecord) -> None:
        """Update changelog with new answer record"""
        entry = self.generate_answer_entry(
            f"Answer #{self.answer_counter:03d}",
            answer_record.action_type,
            answer_record.previous_state,
            answer_record.current_state,
            answer_record.changes_made,
            answer_record.files_affected,
            answer_record.technical_decisions,
            answer_record.next_actions
        )
        
        if self.changelog_path.exists():
            content = self.changelog_path.read_text()
            # Insert after session header
            session_marker = f"## Session: {self.session_date}"
            if session_marker in content:
                parts = content.split(session_marker)
                updated_content = f"{parts[0]}{session_marker}\n\n{entry}{parts[1] if len(parts) > 1 else ''}"
            else:
                updated_content = f"{content}\n\n{entry}"
        else:
            updated_content = self._create_initial_changelog(entry)
        
        self.changelog_path.write_text(updated_content)
        self.answer_counter += 1
    
    def _create_initial_changelog(self, first_entry: str) -> str:
        """Create initial changelog structure"""
        return f"""# CHANGELOG.md

## Session: {self.session_date}

{first_entry}

### Template for Future Entries:

### Answer #XXX - [Action Summary]
**Timestamp:** YYYY-MM-DD HH:MM
**Action Type:** [Architecture|Implementation|Modification|Documentation]
**Previous State:** [Brief state description]
**Current State:** [Brief state description]

#### Changes Made:
- [Specific change 1]
- [Specific change 2]

#### Files Affected:
- **NEW:** [filename] - [purpose]
- **MODIFIED:** [filename] - [changes made]
- **REMOVED:** [filename] - [reason]

#### Technical Decisions:
- [Decision rationale]

#### Next Actions Required:
- [Action item 1]
- [Action item 2]

---
"""

    def quick_update(self, 
                    action_summary: str,
                    changes: List[str],
                    files: List[Tuple[str, str, str]] = None) -> None:
        """Quick changelog update for simple operations"""
        files_affected = []
        if files:
            for operation, filepath, purpose in files:
                files_affected.append(ChangeVector(
                    file_path=filepath,
                    change_type=ChangeType.FEATURE,
                    operation=operation,
                    impact_level="LOW",
                    dependencies=[]
                ))
        
        record = AnswerRecord(
            answer_id=self.answer_counter,
            timestamp=datetime.now().isoformat(),
            action_type="Implementation",
            previous_state="System ready for modification",
            current_state=f"System updated with {action_summary}",
            changes_made=changes,
            files_affected=files_affected,
            technical_decisions=[f"Implemented {action_summary} for system enhancement"],
            next_actions=["Continue with development workflow"]
        )
        
        self.update_changelog(record)

# Usage Example
if __name__ == "__main__":
    engine = ChangelogEngine()
    
    # Quick update example
    engine.quick_update(
        "Core changelog engine implementation",
        [
            "Created automated changelog generation system",
            "Implemented change classification framework",
            "Established answer tracking protocol"
        ],
        [
            ("NEW", "changelog_engine.py", "Automated changelog management"),
            ("MODIFIED", "system_architecture.md", "Updated with changelog specifications")
        ]
    )