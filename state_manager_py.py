#!/usr/bin/env python3
"""
State Management Engine
High-performance change detection with multi-tier caching
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, asdict
from scripts.core.workspace_scanner import WorkspaceScanner, WorkspaceState

@dataclass
class CacheMetrics:
    hit_count: int = 0
    miss_count: int = 0
    cache_size: int = 0
    last_update: float = 0

@dataclass
class ChangeEvent:
    timestamp: str
    change_type: str
    file_path: str
    details: Dict
    impact_level: str

class StateManager:
    def __init__(self, cache_dir: str = ".workspace_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.scanner = WorkspaceScanner()
        self.current_state: Optional[WorkspaceState] = None
        self.previous_state: Optional[WorkspaceState] = None
        self.metrics = CacheMetrics()
        
        # Performance configuration
        self.max_cache_size = 100 * 1024 * 1024  # 100MB
        self.cache_ttl = 3600  # 1 hour
        self.compression_enabled = True
        
    def _get_cache_path(self, cache_type: str) -> Path:
        """Generate cache file path"""
        return self.cache_dir / f"{cache_type}_state.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is within TTL"""
        if not cache_path.exists():
            return False
        
        cache_age = time.time() - cache_path.stat().st_mtime
        return cache_age < self.cache_ttl
    
    def save_state_cache(self, state: WorkspaceState, cache_type: str = "current"):
        """Save workspace state to cache"""
        cache_path = self._get_cache_path(cache_type)
        
        state_dict = {
            "timestamp": state.timestamp,
            "root_path": state.root_path,
            "files": {k: asdict(v) for k, v in state.files.items()},
            "directories": sorted(state.directories),
            "total_files": state.total_files,
            "total_size": state.total_size,
            "state_hash": state.state_hash
        }
        
        with open(cache_path, 'w') as f:
            json.dump(state_dict, f, separators=(',', ':') if self.compression_enabled else None)
        
        self.metrics.cache_size = cache_path.stat().st_size
        self.metrics.last_update = time.time()
    
    def load_state_cache(self, cache_type: str = "current") -> Optional[WorkspaceState]:
        """Load workspace state from cache"""
        cache_path = self._get_cache_path(cache_type)
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                
                from scripts.core.workspace_scanner import FileState
                files = {k: FileState(**v) for k, v in data["files"].items()}
                
                self.metrics.hit_count += 1
                return WorkspaceState(
                    timestamp=data["timestamp"],
                    root_path=data["root_path"],
                    files=files,
                    directories=set(data["directories"]),
                    total_files=data["total_files"],
                    total_size=data["total_size"],
                    state_hash=data["state_hash"]
                )
            except (json.JSONDecodeError, KeyError):
                self.metrics.miss_count += 1
                return None
        
        self.metrics.miss_count += 1
        return None
    
    def get_current_state(self, force_refresh: bool = False) -> WorkspaceState:
        """Get current workspace state with caching"""
        if not force_refresh and self.current_state:
            cached_state = self.load_state_cache("current")
            if cached_state and cached_state.state_hash == self.current_state.state_hash:
                return cached_state
        
        # Generate fresh state
        self.previous_state = self.current_state
        self.current_state = self.scanner.scan_workspace()
        
        # Cache new state
        self.save_state_cache(self.current_state, "current")
        if self.previous_state:
            self.save_state_cache(self.previous_state, "previous")
        
        return self.current_state
    
    def detect_changes(self) -> List[ChangeEvent]:
        """Detect changes between states"""
        current = self.get_current_state()
        
        if not self.previous_state:
            return []
        
        changes = self.scanner.compare_states(self.previous_state, current)
        events = []
        
        # Process added files
        for file_path in changes["added"]:
            file_info = current.files[file_path]
            events.append(ChangeEvent(
                timestamp=current.timestamp,
                change_type="ADDED",
                file_path=file_path,
                details={
                    "size": file_info.size,
                    "type": file_info.type,
                    "hash": file_info.hash
                },
                impact_level=self._assess_impact(file_path, "ADDED")
            ))
        
        # Process removed files
        for file_path in changes["removed"]:
            file_info = self.previous_state.files[file_path]
            events.append(ChangeEvent(
                timestamp=current.timestamp,
                change_type="REMOVED",
                file_path=file_path,
                details={
                    "size": file_info.size,
                    "type": file_info.type
                },
                impact_level=self._assess_impact(file_path, "REMOVED")
            ))
        
        # Process modified files
        for mod_info in changes["modified"]:
            events.append(ChangeEvent(
                timestamp=current.timestamp,
                change_type="MODIFIED",
                file_path=mod_info["path"],
                details={
                    "size_change": mod_info["size_change"],
                    "modified_time": mod_info["modified_time"]
                },
                impact_level=self._assess_impact(mod_info["path"], "MODIFIED")
            ))
        
        return events
    
    def _assess_impact(self, file_path: str, change_type: str) -> str:
        """Assess change impact level"""
        file_path_lower = file_path.lower()
        
        # Critical system files
        if any(pattern in file_path_lower for pattern in [
            'changelog.md', 'requirements.txt', 'config.ini', 
            'main.py', 'app.py', '__init__.py'
        ]):
            return "HIGH"
        
        # Configuration and documentation
        if any(pattern in file_path_lower for pattern in [
            '.md', '.json', '.yaml', '.yml', '.ini', '.cfg'
        ]):
            return "MEDIUM"
        
        # Source code
        if any(pattern in file_path_lower for pattern in [
            '.py', '.js', '.sql', '.html', '.css'
        ]):
            return "MEDIUM"
        
        # Logs and temporary files
        if any(pattern in file_path_lower for pattern in [
            '.log', '.tmp', '.cache', 'temp'
        ]):
            return "LOW"
        
        return "MEDIUM"
    
    def generate_change_summary(self, events: List[ChangeEvent]) -> Dict:
        """Generate structured change summary"""
        summary = {
            "total_changes": len(events),
            "by_type": {"ADDED": 0, "MODIFIED": 0, "REMOVED": 0},
            "by_impact": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "affected_types": set(),
            "critical_changes": []
        }
        
        for event in events:
            summary["by_type"][event.change_type] += 1
            summary["by_impact"][event.impact_level] += 1
            
            # Extract file type
            file_type = event.details.get("type", "unknown")
            summary["affected_types"].add(file_type)
            
            # Track critical changes
            if event.impact_level == "HIGH":
                summary["critical_changes"].append({
                    "file": event.file_path,
                    "type": event.change_type,
                    "details": event.details
                })
        
        summary["affected_types"] = list(summary["affected_types"])
        return summary
    
    def cleanup_cache(self):
        """Clean up expired cache files"""
        for cache_file in self.cache_dir.glob("*_state.json"):
            if not self._is_cache_valid(cache_file):
                cache_file.unlink()
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        hit_rate = 0
        if self.metrics.hit_count + self.metrics.miss_count > 0:
            hit_rate = self.metrics.hit_count / (self.metrics.hit_count + self.metrics.miss_count)
        
        return {
            "cache_hit_rate": f"{hit_rate:.2%}",
            "cache_size_mb": f"{self.metrics.cache_size / (1024*1024):.2f}",
            "last_update": self.metrics.last_update,
            "total_requests": self.metrics.hit_count + self.metrics.miss_count
        }

if __name__ == "__main__":
    manager = StateManager()
    current_state = manager.get_current_state()
    changes = manager.detect_changes()
    summary = manager.generate_change_summary(changes)
    metrics = manager.get_metrics()
    
    print(f"State: {current_state.total_files} files, {summary['total_changes']} changes")
    print(f"Metrics: {metrics['cache_hit_rate']} hit rate, {metrics['cache_size_mb']}MB cache")