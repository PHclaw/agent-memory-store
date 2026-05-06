# Agent Memory Store

A lightweight, isolated memory store for multi-agent systems. Each agent gets its own memory namespace with support for:

- **Isolation**: Agent memories are completely isolated by default
- **Shared Memory**: Optional shared memory spaces for inter-agent communication
- **Session Tracking**: Track memories by conversation/session
- **TTL Support**: Automatic expiration of old memories
- **Multiple Backends**: In-memory (default), SQLite, JSON file

## Installation

```bash
pip install agent-memory-store
```

## Quick Start

```python
from agent_memory_store import AgentMemoryStore

# Create a memory store
store = AgentMemoryStore()

# Create agent-specific memory
agent_memory = store.get_agent_memory("agent-001")

# Add memory
agent_memory.add(
    "User prefers dark mode",
    metadata={"category": "preference", "confidence": 0.9}
)

# Search memories
results = agent_memory.search("dark mode")
print(results)
# [Memory(content="User prefers dark mode", metadata={...}, ...)]

# Get all memories for an agent
all_memories = agent_memory.get_all()
```

## Multi-Agent Isolation

```python
store = AgentMemoryStore()

# Each agent has isolated memory
agent1 = store.get_agent_memory("agent-001")
agent2 = store.get_agent_memory("agent-002")

agent1.add("This is agent 1's memory")
agent2.add("This is agent 2's memory")

# Agent 1 cannot see Agent 2's memories
assert len(agent1.search("agent 2")) == 0
assert len(agent2.search("agent 1")) == 0
```

## Shared Memory Spaces

```python
store = AgentMemoryStore()

# Create a shared space
shared = store.get_shared_memory("project-alpha")

# Agents can read/write to shared space
agent1 = store.get_agent_memory("agent-001", shared_spaces=["project-alpha"])
agent2 = store.get_agent_memory("agent-002", shared_spaces=["project-alpha"])

# Add to shared space
shared.add("Project deadline: 2024-12-31")

# Both agents can see shared memories
assert len(agent1.search("deadline")) == 1
assert len(agent2.search("deadline")) == 1
```

## Session Tracking

```python
store = AgentMemoryStore()
agent = store.get_agent_memory("agent-001")

# Add memories with session tracking
with agent.session("conv-123") as session:
    session.add("User asked about pricing")
    session.add("Provided pricing info")

# Query by session
session_memories = agent.get_by_session("conv-123")
```

## Backends

### In-Memory (Default)

```python
store = AgentMemoryStore(backend="memory")
```

### SQLite

```python
store = AgentMemoryStore(backend="sqlite", path="./memories.db")
```

### JSON File

```python
store = AgentMemoryStore(backend="json", path="./memories.json")
```

## API Reference

### AgentMemoryStore

- `get_agent_memory(agent_id, shared_spaces=None)` - Get isolated memory for an agent
- `get_shared_memory(space_id)` - Get a shared memory space
- `list_agents()` - List all agents with memories
- `list_shared_spaces()` - List all shared spaces
- `clear_all()` - Clear all memories

### AgentMemory

- `add(content, metadata=None, ttl=None)` - Add a memory
- `search(query, limit=10)` - Search memories by content
- `get_all()` - Get all memories
- `get_by_session(session_id)` - Get memories by session
- `delete(memory_id)` - Delete a memory
- `clear()` - Clear all memories for this agent

## License

MIT
