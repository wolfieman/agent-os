# ADR 0006: Context Plane as Kernel Foundation

- **Status:** Proposed
- **Date:** 2026-07-18
- **Authors:** agy (architecture)
- **Decides:** Positioning the Context Plane as the central foundation layer of the agent-os kernel, sitting under the six services and above the raw model.

---

## Context

In traditional operating systems, the virtual memory manager, scheduler, and filesystem are kernel services that manage hardware resources. For an AI agent operating system, the primary scarce resource is the **LLM context window** (limited by token budget, attention decay/rot, and latency ceilings).

Initially, there was a question of whether context engineering should be treated as a seventh peer service alongside the core six (scheduler, memory, tools, identity, observability, guardrails). 

However, context is not just another resource to manage—it is the *medium* through which the agent perceives its environment and makes decisions. Prompt engineering (the static instruction slot) and context engineering (dynamic aggregation of memory, state, and tools) form a single unified plane.

## Decision

We will design the `agent-os` kernel with the **Context Plane as the foundation layer**.

```
+--------------------------------------------------------+
|                    Agents / Teams                      |
| (Actors that execute tasks; defined as policy layers)  |
+--------------------------------------------------------+
|                    Kernel Services                     |
|  (Scheduler, Memory, Tools, Identity, Obs, Guardrails)  |
+---------+----------------------------------------------+
          |  Feeds frame contributions
          v
+--------------------------------------------------------+
|                     CONTEXT PLANE                      |
|  - Context-Assembly Service (mechanism, code in src/)  |
|  - Prompt Library & Standards (resource, orchestrator) |
+---------+----------------------------------------------+
          |  Assembles structured Frame
          v
+--------------------------------------------------------+
|                      Raw LLM Model                     |
+--------------------------------------------------------+
```

1. **Context-Assembly Service:** A core kernel mechanism written in `src/agent_os/kernel/context.py` that exposes the `write`, `select`, `compress`, and `isolate` APIs.
2. **Dynamic Assembly:** The context plane constructs a structured **Frame** for every model call. It queries each kernel service for its "contribution" (e.g., tools from Tool Manager, facts from Memory, task state from Scheduler) and merges them.
3. **Prompt-Craft Integration:** The instruction slot of the Frame is managed by the orchestrator prompt standards (`prompt-authoring.md`, AIM/BRIDGE/MAP templates). The OS consumes these standards by reference.

## Consequences

- **Separation of Concerns:** Kernel services do not make raw LLM calls. They contribute metadata, schemas, and records to the context plane, which handles assembly.
- **Observability Hook:** By routing all context assembly through a single service, we gain a unified trace point. The trace of the assembled Frame is the primary substrate for observability and debugging (AgentOps Layer 1).
- **Security Checkpoint:** Input and output guardrails can be deterministically applied right at the context assembly boundaries, acting as an AI Firewall/Proxy.
- **DRY Compliance:** Existing prompt-engineering templates and rules in `orchestrator` are reused by reference, avoiding duplication.
