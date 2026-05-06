# Agent Memory Store

> Give your AI agents long-term memory that actually works.

Built this because I was tired of agents forgetting everything between conversations. No magic, no vector embeddings — just a simple key-value store with proper isolation between agents.

## Why

When you run multiple AI agents, they inevitably step on each other's toes. Agent A reads Agent B's memories, shared context gets mixed up, and suddenly your customer support bot is talking about internal devops stuff.

This library solves that by giving each agent its own private memory space, with optional shared areas for when you actually want agents to communicate.

## Install

```bash
pip install agent-memory-store
```

Requires Python 3.9+.

## Quick Example

```python
from agent_memory_store import AgentMemoryStore

store = AgentMemoryStore()

# Agent gets its own isolated memory
memory = store.get_agent_memory("support-bot")

# Remember things
memory.add("Customer asked about enterprise pricing")
memory.add("FAQ: cancellation takes 24h to process")

# Search works
results = memory.search("pricing")
```

That's it. No setup, no configuration, no external services.

## Multi-Agent Setup

```python
store = AgentMemoryStore()

# Each agent has completely separate memory
agent1 = store.get_agent_memory("sales-bot")
agent2 = store.get_agent_memory("support-bot")

agent1.add("Q3 sales target: $500k")
agent2.add("Refund policy updated")

# Agents can't see each other's memories
agent1.search("refund")  # empty
agent2.search("sales")   # empty
```

## Shared Memory (When Needed)

```python
store = AgentMemoryStore()

# Create a shared space both agents can access
shared = store.get_shared_memory("product-knowledge")

# Give both agents access
sales = store.get_agent_memory("sales-bot", shared_spaces=["product-knowledge"])
support = store.get_agent_memory("support-bot", shared_spaces=["product-knowledge"])

# Add to shared space
shared.add("Product launch: May 15th")

# Both agents see it
sales.search("launch")   # finds it
support.search("launch") # finds it
```

## Session Tracking

Useful when you want to group memories by conversation:

```python
memory = store.get_agent_memory("support-bot")

with memory.session("conv-12345") as s:
    s.add("Customer: I can't login")
    s.add("Solution: Reset password sent")

# Later: get all memories from this conversation
memory.get_by_session("conv-12345")
```

## Auto-Expiring Memories

```python
from datetime import timedelta

memory = store.get_agent_memory("temp-agent")

# This memory expires in 1 hour
memory.add(
    "Temporary context for current task",
    ttl=timedelta(hours=1)
)
```

## What This Is Not

- Not a vector database. No embeddings, no semantic search.
- Not for storing huge amounts of data. It's an in-memory store with optional SQLite/JSON persistence.
- Not magic. It's a dictionary with extra features.

## What This Is

- Fast. Just Python dicts under the hood.
- Simple. 5 minute learning curve.
- Isolated. Agents can't accidentally read each other's memories.
- No dependencies beyond Python standard library.

## API

### AgentMemoryStore

```python
store = AgentMemoryStore()

# Get an agent's memory
memory = store.get_agent_memory(agent_id, shared_spaces=["space1", "space2"])

# Create shared space
shared = store.get_shared_memory(space_id)

# List stuff
store.list_agents()        # -> ["sales-bot", "support-bot"]
store.list_shared_spaces() # -> ["product-knowledge"]
```

### AgentMemory

```python
memory.add(content, metadata=None, ttl=None, session_id=None)
memory.search(query, limit=10)
memory.get_all()
memory.get_by_session(session_id)
memory.delete(memory_id)
memory.clear()
```

### SharedMemory

```python
shared.add(content, metadata=None, ttl=None)
shared.search(query, limit=10)
shared.get_all()
shared.clear()
```

## License

MIT — do whatever you want with it.
