"""Memory interfaces for agents and shared spaces."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

from .types import Memory, MemorySearchResult


class AgentMemory:
    """Isolated memory for a single agent."""

    def __init__(
        self,
        agent_id: str,
        store: Any,  # AgentMemoryStore (avoid circular import)
        shared_spaces: Optional[list[str]] = None,
    ) -> None:
        self.agent_id = agent_id
        self._store = store
        self._shared_spaces = shared_spaces or []
        self._current_session: Optional[str] = None

    def add(
        self,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
        ttl: Optional[timedelta] = None,
        session_id: Optional[str] = None,
    ) -> Memory:
        """Add a new memory."""
        expires_at = None
        if ttl is not None:
            expires_at = datetime.utcnow() + ttl

        memory = Memory(
            content=content,
            agent_id=self.agent_id,
            session_id=session_id or self._current_session,
            metadata=metadata or {},
            expires_at=expires_at,
        )
        self._store._add_memory(memory)
        return memory

    def search(self, query: str, limit: int = 10) -> list[MemorySearchResult]:
        """Search memories by content."""
        results = []

        # Search agent's own memories
        for memory in self._store._get_agent_memories(self.agent_id):
            if memory.is_expired():
                continue
            if memory.matches_query(query):
                results.append(MemorySearchResult(memory=memory))

        # Search shared spaces
        for space_id in self._shared_spaces:
            for memory in self._store._get_shared_memories(space_id):
                if memory.is_expired():
                    continue
                if memory.matches_query(query):
                    results.append(MemorySearchResult(memory=memory))

        return results[:limit]

    def get_all(self) -> list[Memory]:
        """Get all memories for this agent."""
        memories = list(self._store._get_agent_memories(self.agent_id))
        # Include shared spaces
        for space_id in self._shared_spaces:
            memories.extend(self._store._get_shared_memories(space_id))
        return [m for m in memories if not m.is_expired()]

    def get_by_session(self, session_id: str) -> list[Memory]:
        """Get memories by session."""
        memories = self._store._get_agent_memories(self.agent_id)
        return [
            m
            for m in memories
            if m.session_id == session_id and not m.is_expired()
        ]

    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        return self._store._delete_memory(memory_id, self.agent_id)

    def clear(self) -> None:
        """Clear all memories for this agent."""
        self._store._clear_agent_memories(self.agent_id)

    def session(self, session_id: str) -> SessionContext:
        """Create a session context manager."""
        return SessionContext(self, session_id)


class SessionContext:
    """Context manager for session-scoped memory operations."""

    def __init__(self, agent_memory: AgentMemory, session_id: str) -> None:
        self._agent_memory = agent_memory
        self._session_id = session_id

    def __enter__(self) -> SessionContext:
        self._agent_memory._current_session = self._session_id
        return self

    def __exit__(self, *args: Any) -> None:
        self._agent_memory._current_session = None

    def add(
        self,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
        ttl: Optional[timedelta] = None,
    ) -> Memory:
        """Add a memory within this session."""
        return self._agent_memory.add(
            content, metadata=metadata, ttl=ttl, session_id=self._session_id
        )


class SharedMemory:
    """Shared memory space for inter-agent communication."""

    def __init__(self, space_id: str, store: Any) -> None:
        self.space_id = space_id
        self._store = store

    def add(
        self,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
        ttl: Optional[timedelta] = None,
    ) -> Memory:
        """Add a memory to the shared space."""
        expires_at = None
        if ttl is not None:
            expires_at = datetime.utcnow() + ttl

        memory = Memory(
            content=content,
            space_id=self.space_id,
            metadata=metadata or {},
            expires_at=expires_at,
        )
        self._store._add_memory(memory)
        return memory

    def search(self, query: str, limit: int = 10) -> list[MemorySearchResult]:
        """Search memories in this shared space."""
        results = []
        for memory in self._store._get_shared_memories(self.space_id):
            if memory.is_expired():
                continue
            if memory.matches_query(query):
                results.append(MemorySearchResult(memory=memory))
        return results[:limit]

    def get_all(self) -> list[Memory]:
        """Get all memories in this shared space."""
        memories = self._store._get_shared_memories(self.space_id)
        return [m for m in memories if not m.is_expired()]

    def clear(self) -> None:
        """Clear all memories in this shared space."""
        self._store._clear_shared_memories(self.space_id)
