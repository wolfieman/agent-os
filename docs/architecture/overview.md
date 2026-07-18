# 🏛️ Agent OS: Architecture Overview

This document provides a high-level overview of the `agent-os` architecture. It explains how the system is structured to provide safety, scheduling, observability, memory, and sandboxing to autonomous agents.

---

## 🧱 1. System Layers

Agent OS is designed as a three-tier system:

```
+------------------------------------------------------------+
|                         AGENTS                             |
| (Autonomous actors, domain specialists, and agent teams)   |
+------------------------------------------------------------+
|                         KERNEL                             |
| (Six services: Scheduler, Memory, Tools, Identity,         |
|  Observability, Guardrails, unified by the Context Plane)   |
+------------------------------------------------------------+
|                     INFRASTRUCTURE                         |
| (LLM Models, Vector Databases, Sandboxes, API Credentials) |
+------------------------------------------------------------+
```

1. **Agents / Teams (Policy):** Define *who* is acting and *what* they are doing. This includes specialized subagents and multi-agent coordination topologies (e.g., researcher-writer loops).
2. **Kernel (Mechanism):** Provides the operating environment. It does not decide the agent's goal; it manages its resources, schedules its execution, isolates its tools, and monitors its choices.
3. **Infrastructure (Resources):** The physical or virtual resources being managed (Ollama, Cloudflare Vectorize, local filesystems, SaaS APIs).

---

## 🧩 2. The Context Plane: Core OS Foundation

The foundation of the kernel is the **Context Plane** (formalized in [ADR 0006](file:///home/wolfie/projects/agent-os/docs/decisions/0006-context-plane-as-kernel-foundation.md)). The Context Plane is responsible for assembling the **Frame** (the payload sent to the LLM) from contributions provided by the kernel services.

### The Frame Structure

The Frame is a structured JSON payload constructed dynamically per LLM call:

```json
{
  "instructions": "Role persona, formatting constraints, safety policies",
  "user_input": "The active prompt or task query",
  "task_state": {
    "task_id": "ce-002",
    "status": "in_progress",
    "step_index": 3,
    "plan": ["Step 1", "Step 2", "Step 3"]
  },
  "short_term_memory": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "long_term_memory": [
    {"chunk_id": "r-102", "content": "RAG snippet...", "provenance": "standards.db"}
  ],
  "tool_definitions": [
    {"name": "search_docs", "description": "...", "parameters": "..."}
  ],
  "provenance": {
    "instructions": {"source": "prompt_router", "hash": "sha256..."},
    "long_term_memory": {"source_files": ["standards/ai-codegen/prompt-authoring.md"]}
  }
}
```

---

## ❓ 3. Resolving the Open Questions

### Q1: The Context-Assembly Service Design
The Context-Assembly service exposes four core verbs as its API:
- `write(key, data, provenance)`: Appends data to memory tiers or task state.
- `select(query, filters, limit)`: Hybrid search (vector + keyword) to fetch relevant context slices while filtering out noise.
- `compress(strategy, target_tokens)`: Performs pruning or LLM-based summarization to prevent *distraction*.
- `isolate(boundary)`: Sandbox definition for executing code or spawning subagents.

*Provenance & Observability:* Injected data carries metadata indicating its source, author, and timestamp. If a validation check fails (e.g. poisoning or injection), the context plane can evict the tainted source. Every assembled Frame is logged to a structured JSONL trace file, which serves as the observability substrate.

### Q2: The Kernel Interface Layer ("Syscall" Boundary)
Kernel services do not directly query the LLM. Instead, they register as `FrameProviders`. The context assembler invokes `provide_context(request)` on each service, aggregating their contributions into the final Frame.

### Q3: Scheduler & Task State
Task state is a first-class citizen in the Frame. Rather than storing state solely in the agent's short-term context (which is easily summarized away or lost), the scheduler maintains the task's progress on an external blackboard (`state.json`). This structured state is explicitly injected as a dedicated XML/JSON slot in the Frame, keeping the agent grounded.

### Q4: The Isolate Primitive & OS/Teams Seam
- **Isolate:** Combines a tool sandbox (limiting path access and blocking network calls) and a subprocess subagent dispatcher.
- **OS/Teams Seam:** The OS kernel manages the execution environment, scheduling, and resource leases. The Teams layer defines coordinating graphs (LangGraph) and assigns tasks to agents based on their **Actor Cards** (published capability resumes).

### Q5: Framework Selection
Following [ADR 0007](file:///home/wolfie/projects/agent-os/docs/decisions/0007-framework-light-kernel-design.md), the core kernel is kept **framework-light** (written in vanilla Python) to maximize performance and auditability. LangGraph is used exclusively in the application layer (`agent-teams`) for structuring multi-agent graph pipelines.

### Q6: v0 Walking Skeleton Scope
- Stand up `src/agent_os/kernel/context.py` exposing the `ContextAssemblyService`.
- Implement a basic blackboard scheduler reading task state from a local file.
- Implement trace-logging that emits JSONL outputs for every frame assembled.
- Validate by running the **LogLook-analog** triage agent (`examples/log_look.py`), which uses the context plane to read, process, and summarize real log files.
