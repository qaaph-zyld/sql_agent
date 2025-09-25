#!/usr/bin/env python3
"""
Automated Workspace State Scanner
Real-time filesystem analysis with performance optimization
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class FileState:
    path: str
    size: int
    modified: float
    hash: str
    type: str

@dataclass
class WorkspaceState:
    timestamp: str
    root_path: str
    files: Dict[str, FileState]
    directories: Set[str]
    total_files: int
    total_size: int
    state_hash: str

class WorkspaceScanner:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.ignore_patterns = {
            "__pycache__", ".git", ".venv", "venv", "node_modules",
            ".pytest_cache", ".mypy_cache", "*.pyc", "*.pyo"
        }
        
    def should_ignore(self, path: Path) -> bool:
        """Determine if path should be ignored"""
        for pattern in self.ignore_patterns:
            if pattern.startswith("*."):
                if path.suffix == pattern[1:]:
                    return True
            elif pattern in path.parts:
                return True
        return False
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Generate SHA-256 hash for file content"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()[:16]  # Truncate for performance
        except (OSError, IOError):
            return "error"
    
    def get_file_type(self, path: Path) -> str:
        """Classify file type"""
        suffix = path.suffix.lower()
        type_map = {
            '.py': 'python', '.js': 'javascript', '.html': 'html',
            '.css': 'css', '.md': 'markdown', '.json': 'json',
            '.sql': 'sql', '.txt': 'text', '.log': 'log',
            '.ini': 'config', '.yaml': 'config', '.yml': 'config'
        }
        return type_map.get(suffix, 'other')
    
    def scan_workspace(self) -> WorkspaceState:
        """Generate complete workspace state"""
        files = {}
        directories = set()
        total_size = 0
        
        for root, dirs, filenames in os.walk(self.root_path):
            root_path = Path(root)
            
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not self.should_ignore(root_path / d)]
            
            # Add directory to set
            rel_dir = root_path.relative_to(self.root_path)
            if str(rel_dir) != ".":
                directories.add(str(rel_dir))
            
            # Process files
            for filename in filenames:
                file_path = root_path / filename
                
                if self.should_ignore(file_path):
                    continue
                
                try:
                    stat = file_path.stat()
                    rel_path = str(file_path.relative_to(self.root_path))
                    
                    file_state = FileState(
                        path=rel_path,
                        size=stat.st_size,
                        modified=stat.st_mtime,
                        hash=self.calculate_file_hash(file_path),
                        type=self.get_file_type(file_path)
                    )
                    
                    files[rel_path] = file_state
                    total_size += stat.st_size
                    
                except (OSError, IOError):
                    continue
        
        # Generate state hash
        state_content = json.dumps({
            "files": {k: asdict(v) for k, v in files.items()},
            "directories": sorted(directories)
        }, sort_keys=True)
        state_hash = hashlib.sha256(state_content.encode()).hexdigest()[:16]
        
        return WorkspaceState(
            timestamp=datetime.now().isoformat(),
            root_path=str(self.root_path),
            files=files,
            directories=directories,
            total_files=len(files),
            total_size=total_size,
            state_hash=state_hash
        )
    
    def compare_states(self, old_state: WorkspaceState, new_state: WorkspaceState) -> Dict:
        """Generate diff between workspace states"""
        changes = {
            "added": [],
            "modified": [],
            "removed": [],
            "moved": []
        }
        
        old_files = set(old_state.files.keys())
        new_files = set(new_state.files.keys())
        
        # Added files
        changes["added"] = list(new_files - old_files)
        
        # Removed files
        changes["removed"] = list(old_files - new_files)
        
        # Modified files
        for file_path in old_files & new_files:
            old_file = old_state.files[file_path]
            new_file = new_state.files[file_path]
            
            if old_file.hash != new_file.hash:
                changes["modified"].append({
                    "path": file_path,
                    "size_change": new_file.size - old_file.size,
                    "modified_time": new_file.modified
                })
        
        return changes
    
    def save_state(self, state: WorkspaceState, output_path: str = "workspace_state.json"):
        """Save workspace state to file"""
        state_dict = {
            "timestamp": state.timestamp,
            "root_path": state.root_path,
            "files": {k: asdict(v) for k, v in state.files.items()},
            "directories": sorted(state.directories),
            "total_files": state.total_files,
            "total_size": state.total_size,
            "state_hash": state.state_hash
        }
        
        with open(output_path, 'w') as f:
            json.dump(state_dict, f, indent=2)
    
    def load_state(self, input_path: str = "workspace_state.json") -> WorkspaceState:
        """Load workspace state from file"""
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            files = {k: FileState(**v) for k, v in data["files"].items()}
            
            return WorkspaceState(
                timestamp=data["timestamp"],
                root_path=data["root_path"],
                files=files,
                directories=set(data["directories"]),
                total_files=data["total_files"],
                total_size=data["total_size"],
                state_hash=data["state_hash"]
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

if __name__ == "__main__":
    scanner = WorkspaceScanner()
    current_state = scanner.scan_workspace()
    scanner.save_state(current_state)
    print(f"Workspace scanned: {current_state.total_files} files, {current_state.total_size:,} bytes")