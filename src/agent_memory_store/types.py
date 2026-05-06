"""Type definitions for Agent Memory Store."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4


@dataclass
class Memory:
    """A single memory entry."""

    id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    space_id: Optional[str] = None  # For shared spaces
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if this memory has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def matches_query(self, query: str) -> bool:
        """Simple substring match for search."""
        query_lower = query.lower()
        if query_lower in self.content.lower():
            return True
        # Also search in metadata values
        for value in self.metadata.values():
            if isinstance(value, str) and query_lower in value.lower():
                return True
        return False


@dataclass
class MemorySearchResult:
    """Result of a memory search."""

    memory: Memory
    score: float = 1.0  # Simple implementation: all matches have score 1.0
