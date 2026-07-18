# Agent OS Architecture

This document synthesizes the architectural design of `agent-os` (the Operating System for AI Agents), resolving the core questions left by `cowork` in the handoff document [to_agy.md](file:///home/wolfie/projects/inter-agency/context-engineering/processing/handoffs/to_agy.md).

> [!NOTE]
> We have successfully drafted the architectural specs and decision records in the `agent-os` repository. You can access the following files directly:
> - **Architecture Overview:** [overview.md](file:///home/wolfie/projects/agent-os/docs/architecture/overview.md)
> - **Vertical Layering:** [layering.md](file:///home/wolfie/projects/agent-os/docs/architecture/layering.md)
> - **OS / Teams Seam:** [agent-teams.md](file:///home/wolfie/projects/agent-os/docs/architecture/agent-teams.md)
> - **Inter-Agency Pattern Harvesting:** [inter-agency-patterns.md](file:///home/wolfie/projects/agent-os/docs/architecture/inter-agency-patterns.md)
> - **Kernel Services Specifications:** [services.md](file:///home/wolfie/projects/agent-os/docs/architecture/kernel/services.md)
> - **ADR 0006 (Context Plane):** [0006-context-plane-as-kernel-foundation.md](file:///home/wolfie/projects/agent-os/docs/decisions/0006-context-plane-as-kernel-foundation.md)
> - **ADR 0007 (Framework Selection):** [0007-framework-light-kernel-design.md](file:///home/wolfie/projects/agent-os/docs/decisions/0007-framework-light-kernel-design.md)

---

## 1. System Architecture & The Context Plane

The foundation of the kernel is the **Context Plane**. In an agentic operating system, context is the primary scarce resource (subject to token bounds, attention decay, and latency). The Context Plane handles the raw formatting and assembly of the model payload (the **Frame**).

### Vertical Stack Flow

```mermaid
graph TD
    subgraph Sibling Repo (Policy)
        Teams["Agents & Teams (e.g., LangGraph Graphs, Roles)"]
    end
    subgraph Agent OS Kernel (Mechanism)
        Services["Kernel Services (Scheduler, Memory, Tools, Identity, Obs, Guardrails)"]
        Plane["Context Plane (Context-Assembly Service, Prompt Standards)"]
    end
    subgraph Infrastructure
        Model["Raw Language Model (Ollama local, adagio, Cloud APIs)"]
    end

    Teams -- Syscalls --> Services
    Services -- Contributions --> Plane
    Plane -- Assembled Frame --> Model
    Model -- Response/Trace --> Plane
```

---

## 2. Resolving the Handoff's Open Questions

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

---

## 3. Recommended Decisions for Wolfie

We have updated the rollout plan with **Addendum v1.3** to lock in the following architectural recommendations:

| Decision Axis | Recommendation | Rationale |
|---|---|---|
| **adagio Auth** | Tailscale-only for transport; static keys for DB writes. | Fits the secure-agents guide's **non-human identity** principle; avoids placeholder keys like `"ollama"`. |
| **Pilot Skill** | Monthly `budget-close` and `loan-payoff`. | High value, but must be configured with `disable-model-invocation: true` to prevent autonomous execution of financial actions. |
| **Execution Team** | Dogfood via inter-agency actors (agy, cowork). | Proves and exercises the file-based blackboard protocol on real coordination work. |
| **Sequencing** | Run Phase 1 (skills) and Phase 5 (LangGraph) in parallel. | Both have zero cross-dependencies; speeds up overall estate rollout. |
| **Secure-Agents** | Harvest principles directly. | Least privilege, sandboxing, input/output firewalls, and audit trails are implemented directly as OS kernel mechanisms. |
| **New Standards** | Fold into a single `architecture-principles.md` standard. | Minimizes document bloat while keeping guidelines DRY and centralized. |

---

## 4. Immediate Next Steps

To begin execution of **Phase 0 (OS Skeleton)**:
1. **Approve this Architecture and Rollout Plan:** Review [agentic-rollout-plan.md](file:///home/wolfie/projects/agent-os/docs/planning/agentic-rollout-plan.md).
2. **Execute the OS Phase 0 Code Stubbing:** Code the `ContextAssemblyService` in `src/agent_os/kernel/context.py` and the observability trace logger in `src/agent_os/observability/trace.py`.
3. **Build the LogLook-analog:** Write the `examples/log_look.py` triage agent to run against real system logs and confirm frame assembly and trace output.
