# ADR 0007: Framework-Light Kernel Design

- **Status:** Proposed
- **Date:** 2026-07-18
- **Authors:** agy (architecture)
- **Decides:** Keeping the core `agent-os` kernel hand-built and lightweight (framework-light), while recommending frameworks (such as LangGraph) exclusively for the sibling policy layer (`agent-teams`).

---

## Context

When architecting AI agent systems, developers often reach for orchestration frameworks (e.g., LangChain, AutoGen, CrewAI, or LangGraph) to handle the entire lifecycle of the agent.

We must decide whether the core `agent-os` kernel services should be built on top of an existing framework, or whether they should be hand-built from basic primitives (standard Python library, basic tools/MCP bindings, and direct model client wrappers).

Addendum v1.1 of the rollout plan outlines a framework-selection rubric based on system shape:
- *Linear Workflows:* Predictable, sequential (LangChain, LlamaIndex).
- *Autonomous Agents:* Open-ended goals, multi-agent (AutoGen, CrewAI).
- *Role-Based Teams:* Clear boundaries, multi-agent (CrewAI, AutoGen).
- *Production Orchestration:* Deep API/DB/workflow integration, state graphs (LangGraph).
- *Rapid Prototyping:* Canvas drag-and-drop (LangFlow, Flowise).

## Decision

1. **Kernel is Framework-Light:** The core `agent-os` repository (`src/agent_os/`) will be hand-built. We will not use LangChain, LangGraph, CrewAI, or AutoGen in the kernel. Primitives like file locks, task blackboard state (`state.json`), process isolation, and the context-assembly frame builder will be implemented in vanilla Python.
2. **Teams Layer uses LangGraph:** The future sibling repository `agent-teams` (which represents the *policy* layer of agent interaction, role assignments, and review loops) is authorized to use LangGraph.
3. **Reasoning:**
   - **Kernel as Infrastructure:** A kernel must be highly performant, predictable, and carry minimal dependencies. Heavy frameworks introduce dependency bloat, restrict low-level control, and add black-box abstraction layers that make debugging and sandboxing more difficult.
   - **Mechanism vs. Policy:** In Unix philosophy, the kernel provides *mechanism* (locking, memory retrieval, sandboxing, trace emission) and applications provide *policy* (which agents talk to whom, in what order, using what evaluation graph). LangGraph is a policy framework; it belongs in the application space (`agent-teams`), not the kernel.

## Consequences

- **Minimal Dependencies:** The kernel's `pyproject.toml` will remain lean, relying primarily on standard libraries, low-level HTTP/JSON clients, and stdio/MCP wrappers (like `mcp` or `fastmcp`).
- **Ease of Auditing:** Hand-built security boundaries (process sandboxing, path validation) are easier to audit and guarantee than framework-abstracted executions.
- **Clear Developer Seam:** Developers writing multi-agent workflows will write LangGraph code in the `agent-teams` repo, which invokes the kernel's services via standard API calls or MCP tools.
