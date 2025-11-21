"""
Blackboard Pattern Implementation

A shared workspace where multiple agents can asynchronously read and write data.
This is a framework-agnostic implementation that can be used with both ADK and CrewAI.

Reference: Pattern #8 - Blackboard Pattern
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import json
import threading


@dataclass
class BlackboardEntry:
    """A single entry in the blackboard."""

    key: str
    value: Any
    author: str
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "metadata": self.metadata,
        }


class BlackboardMonitor:
    """Monitors changes to the blackboard."""

    def __init__(self):
        self.changes: List[Dict[str, Any]] = []

    def record_change(self, action: str, entry: BlackboardEntry):
        """Record a change to the blackboard."""
        self.changes.append({
            "action": action,
            "key": entry.key,
            "author": entry.author,
            "timestamp": entry.timestamp.isoformat(),
            "version": entry.version,
        })

    def get_history(self, key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get change history, optionally filtered by key."""
        if key:
            return [c for c in self.changes if c["key"] == key]
        return self.changes


class Blackboard:
    """
    Shared workspace for multi-agent collaboration.

    Agents can asynchronously write contributions and read others' work.
    Thread-safe for concurrent access.

    Example:
        >>> blackboard = Blackboard(name="ProductDesign")
        >>> blackboard.write("design_specs", {...}, author="DesignAgent")
        >>> specs = blackboard.read("design_specs")
        >>> all_data = blackboard.read_all()
    """

    def __init__(self, name: str = "SharedWorkspace"):
        self.name = name
        self._data: Dict[str, BlackboardEntry] = {}
        self._lock = threading.RLock()
        self.monitor = BlackboardMonitor()

    def write(
        self,
        key: str,
        value: Any,
        author: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BlackboardEntry:
        """
        Write or update an entry on the blackboard.

        Args:
            key: Unique identifier for the entry
            value: Data to store (any JSON-serializable type)
            author: Name of the agent writing the data
            metadata: Optional metadata about the entry

        Returns:
            The created/updated BlackboardEntry
        """
        with self._lock:
            version = 1
            if key in self._data:
                version = self._data[key].version + 1

            entry = BlackboardEntry(
                key=key,
                value=value,
                author=author,
                metadata=metadata or {},
                version=version
            )

            self._data[key] = entry
            self.monitor.record_change("write", entry)

            return entry

    def read(self, key: str) -> Optional[Any]:
        """
        Read a value from the blackboard.

        Args:
            key: Key to read

        Returns:
            The value if it exists, None otherwise
        """
        with self._lock:
            entry = self._data.get(key)
            return entry.value if entry else None

    def read_entry(self, key: str) -> Optional[BlackboardEntry]:
        """
        Read the full entry (with metadata) from the blackboard.

        Args:
            key: Key to read

        Returns:
            The BlackboardEntry if it exists, None otherwise
        """
        with self._lock:
            return self._data.get(key)

    def read_all(self) -> Dict[str, Any]:
        """
        Read all values from the blackboard.

        Returns:
            Dictionary of all key-value pairs
        """
        with self._lock:
            return {key: entry.value for key, entry in self._data.items()}

    def read_all_entries(self) -> Dict[str, BlackboardEntry]:
        """
        Read all entries (with metadata) from the blackboard.

        Returns:
            Dictionary of all entries
        """
        with self._lock:
            return self._data.copy()

    def exists(self, key: str) -> bool:
        """Check if a key exists on the blackboard."""
        with self._lock:
            return key in self._data

    def delete(self, key: str, author: str) -> bool:
        """
        Delete an entry from the blackboard.

        Args:
            key: Key to delete
            author: Name of the agent deleting the entry

        Returns:
            True if deleted, False if key didn't exist
        """
        with self._lock:
            if key in self._data:
                entry = self._data[key]
                entry.author = author  # Track who deleted it
                self.monitor.record_change("delete", entry)
                del self._data[key]
                return True
            return False

    def clear(self):
        """Clear all entries from the blackboard."""
        with self._lock:
            self._data.clear()
            self.monitor.changes.clear()

    def get_contributors(self) -> List[str]:
        """Get list of all agents who have written to the blackboard."""
        with self._lock:
            return list(set(entry.author for entry in self._data.values()))

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the blackboard state."""
        with self._lock:
            return {
                "name": self.name,
                "total_entries": len(self._data),
                "contributors": self.get_contributors(),
                "keys": list(self._data.keys()),
                "total_changes": len(self.monitor.changes),
            }

    def to_json(self) -> str:
        """Serialize blackboard to JSON."""
        with self._lock:
            data = {
                "name": self.name,
                "entries": {
                    key: entry.to_dict()
                    for key, entry in self._data.items()
                },
            }
            return json.dumps(data, indent=2)

    def __repr__(self) -> str:
        return f"Blackboard(name='{self.name}', entries={len(self._data)})"
