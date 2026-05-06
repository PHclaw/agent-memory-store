"""Main Agent Memory Store implementation."""

from __future__ import annotations

from typing import Optional

from .memory import AgentMemory, SharedMemory
from .types import Memory


class AgentMemoryStore:
    """Lightweight isolated memory store for multi-agent systems."""

    def __init__(
        self,
        backend: str = "memory",
        path: Optional[str] = None,
    ) -> None:
        """Initialize the memory store.

        Args:
            backend: Storage backend - "memory" (default), "sqlite", or "json"
            path: Path for file-based backends (sqlite/json)
        """
        self.backend = backend
        self.path = path

        # In-memory storage
        self._memories: dict[str, Memory] = {}
        self._agent_index: dict[str, set[str]] = {}  # agent_id -> memory_ids
        self._space_index: dict[str, set[str]] = {}  # space_id -> memory_ids

        # For file-based backends, we'd initialize here
        if backend == "sqlite":
            self._init_sqlite()
        elif backend == "json":
            self._init_json()

    def _init_sqlite(self) -> None:
        """Initialize SQLite backend."""
        # Placeholder - would use sqlite3
        pass

    def _init_json(self) -> None:
        """Initialize JSON file backend."""
        # Placeholder - would use json
        pass

    def get_agent_memory(
        self,
        agent_id: str,
        shared_spaces: Optional[list[str]] = None,
    ) -> AgentMemory:
        """Get isolated memory for an agent.

        Args:
            agent_id: Unique identifier for the agent
            shared_spaces: Optional list of shared space IDs to include

        Returns:
            AgentMemory instance for this agent
        """
        return AgentMemory(agent_id, self, shared_spaces)

    def get_shared_memory(self, space_id: str) -> SharedMemory:
        """Get a shared memory space.

        Args:
            space_id: Unique identifier for the shared space

        Returns:
            SharedMemory instance
        """
        return SharedMemory(space_id, self)

    def list_agents(self) -> list[str]:
        """List all agents with memories."""
        return list(self._agent_index.keys())

    def list_shared_spaces(self) -> list[str]:
        """List all shared spaces."""
        return list(self._space_index.keys())

    def clear_all(self) -> None:
        """Clear all memories."""
        self._memories.clear()
        self._agent_index.clear()
        self._space_index.clear()

    # Internal methods used by AgentMemory and SharedMemory

    def _add_memory(self, memory: Memory) -> None:
        """Add a memory to the store."""
        self._memories[memory.id] = memory

        # Index by agent
        if memory.agent_id:
            if memory.agent_id not in self._agent_index:
                self._agent_index[memory.agent_id] = set()
            self._agent_index[memory.agent_id].add(memory.id)

        # Index by space
        if memory.space_id:
            if memory.space_id not in self._space_index:
                self._space_index[memory.space_id] = set()
            self._space_index[memory.space_id].add(memory.id)

    def _get_agent_memories(self, agent_id: str) -> list[Memory]:
        """Get all memories for an agent."""
        memory_ids = self._agent_index.get(agent_id, set())
        return [self._memories[mid] for mid in memory_ids if mid in self._memories]

    def _get_shared_memories(self, space_id: str) -> list[Memory]:
        """Get all memories in a shared space."""
        memory_ids = self._space_index.get(space_id, set())
        return [self._memories[mid] for mid in memory_ids if mid in self._memories]

    def _delete_memory(self, memory_id: str, agent_id: str) -> bool:
        """Delete a memory (only if owned by the agent)."""
        if memory_id not in self._memories:
            return False

        memory = self._memories[memory_id]
        if memory.agent_id != agent_id:
            return False  # Can't delete other agents' memories

        del self._memories[memory_id]
        self._agent_index.get(agent_id, set()).discard(memory_id)
        return True

    def _clear_agent_memories(self, agent_id: str) -> None:
        """Clear all memories for an agent."""
        memory_ids = self._agent_index.get(agent_id, set())
        for mid in memory_ids:
            if mid in self._memories:
                del self._memories[mid]
        if agent_id in self._agent_index:
            del self._agent_index[agent_id]

    def _clear_shared_memories(self, space_id: str) -> None:
        """Clear all memories in a shared space."""
        memory_ids = self._space_index.get(space_id, set())
        for mid in memory_ids:
            if mid in self._memories:
                del self._memories[mid]
        if space_id in self._space_index:
            del self._space_index[space_id]
