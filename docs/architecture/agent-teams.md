# 🔗 OS / Teams Seam: Sibling Architecture

This document describes the design boundary between `agent-os` (the kernel repository) and `agent-teams` (the future sibling repository that defines multi-agent policies).

---

## ⚖️ 1. Mechanism vs. Policy

The boundary between the kernel and the teams layer follows the classic software engineering principle: **separate mechanism from policy**.

| Layer | Responsibility | Suited Framework |
|---|---|---|
| **OS Kernel** (`agent-os`) | **Mechanism:** Sandboxing, lock leases, memory storage/retrieval, task state blackboard storage, raw context assembly, identity validation, trace logging. | Framework-Light (Vanilla Python) |
| **Teams Layer** (`agent-teams`) | **Policy:** Multi-agent collaboration graphs, role definitions (e.g., researcher, writer, editor), review loops, task delegation, human-in-the-loop workflows. | LangGraph / CrewAI |

---

## 🔌 2. The Seam: Actor Cards & Blackboard Tasks

The interaction between the kernel and the teams layer occurs through two primary structures:

### A. Actor Cards
An **Actor Card** is a machine-readable capability manifest published by an agent or team role. It is exposed to the kernel's Tool/Identity manager.

```json
{
  "actor_id": "clinical_doc_agent",
  "role": "Clinical Documentation Specialist",
  "capabilities": ["retrieve_ehr_records", "summarize_lab_results"],
  "model_preferences": {
    "default": "claude-3-5-sonnet",
    "cheap": "qwen3:4b-instruct"
  },
  "required_tools": ["search_docs", "ehr_read_api"],
  "allowed_paths": ["/home/wolfie/projects/inter-agency/shared-context/symlinks/"]
}
```

The teams layer queries these cards to discover which agents have the capability to handle a specific subtask, enabling dynamic task routing.

### B. Blackboard Task Delegation
When a multi-agent team decides to delegate work:
1. The coordination agent (e.g., the supervisor) writes a new task definition to the blackboard (`state.json`), setting the status to `backlog` and assigning it to a specific `actor_id` (based on its Actor Card capabilities).
2. The OS scheduler picks up the task, updates its status to `pending_approval` (if HITL is required) or claims it immediately.
3. The OS initializes a sandbox boundary for the target actor using the `isolate()` primitive, fetches its required tools, assembles the Context Frame, and launches the actor subprocess.

---

## 📡 3. Communication Patterns

Multi-agent coordination in `agent-teams` is implemented using state graphs (LangGraph). The graph nodes execute within sandbox boundaries managed by the kernel:

```
[Agent Teams Graph (LangGraph)]
         |
         | Spawns Node (Researcher)
         v
  [Kernel Sandbox (Isolate)]  <--- Limits path access, binds RAG/MCP tools
         |
         | Node Completes
         v
  [Reviewer Loop Node]        <--- Verifies output against criteria
         |
         | Spawns Node (Writer)
         v
  [Kernel Sandbox (Isolate)]
```

This structure ensures that even complex multi-agent graphs with autonomous routing behave safely, as the kernel strictly enforces the principle of least privilege at the sandbox boundaries of each individual node.

---

## 🎭 4. Actor Roles & Specializations

```
                    +---------------------------------------+
                    |             agy (Director)            |
                    |   - System architecture review        |
                    |   - Strategic oversight & ADRs        |
                    +---------------------------------------+
                                        |
                +-----------------------+-----------------------+
                |                                               |
                v                                               v
    +-----------------------+                       +-----------------------+
    |  cowork (Coordinator) |                       |  claude (Implementer) |
    |  - Planning & RAG     |                       |  - Stdio code edits   |
    |  - Standards/Docs     |                       |  - Test execution     |
    +-----------------------+                       +-----------------------+
                |                                               |
                +-----------------------+-----------------------+
                                        |
                                        v
                            +-----------------------+
                            |    codex (Auditor)    |
                            +-----------------------+
```

### A. Claude Code CLI (`claude`): The Implementer

`claude` (running Claude Code CLI) is highly optimized for direct, local code operations, fast editing loops, and running terminal tests.

* **Assign to:** Phases 0, 1, 2, and 5 (Writing the Code)
  * Creating the `ContextAssemblyService` (`src/agent_os/kernel/context.py`).
  * Creating the trace logging infrastructure (`src/agent_os/observability/trace.py`).
  * Writing the `examples/log_look.py` triage agent.
* **How to engage:** Create execution tasks (e.g., `os-001: Build Context Assembly Service`) on the blackboard `state.json` and assign them to `claude`. The harness orchestrator will launch the CLI to code, run tests, and generate the required artifacts.

### B. Claude Cowork (`cowork`): The Coordination & Standards Lead

`cowork` excels at high-level planning, synthesis, panel operations, and prose-standards drafting.

* **Assign to:** Phase 0 & 3 (Planning, Refinement, & Governance)
  * Maintaining the `agent-os` rollout plan and checking off completed milestones.
  * Fusing the framework-selection and A2A verification rules into the centralized `standards/agentic/architecture-principles.md` within `orchestrator`.
  * Coordinating multi-repo updates when the paused estate-wide context rollout resumes.
* **How to engage:** Assign planning, standardisation, and document-drafting tasks on the blackboard to `cowork`.

### C. Codex (`codex`): The Auditor & Safety Officer

`codex` (optimized for codebase checks and security) excels at finding edge-case logic flaws, validating safety structures, and auditing design compliance.

* **Assign to:** Phases 3 & 4 (Auditing & Quality Gates)
  * **ADR Compliance:** Verifying that the code written by `claude` complies strictly with `0006-context-plane-as-kernel-foundation.md` (Context Plane as foundation) and `0007-framework-light-kernel-design.md` (framework-light).
  * **Sandbox Audit:** Auditing the `isolate()` primitive's sandbox boundaries (verifying that file paths are properly validated and network calls are restricted).
  * **Privacy/DLP Audit:** Scanning the generated traces to ensure no sensitive files or credentials (e.g., `life-admin` details) leak into the logs.
* **How to engage:** Create audit tasks (e.g., `os-audit-01: Verify sandbox limits and path-traversal prevention`) and assign them to `codex` on the blackboard once `claude` completes an implementation.

### D. Agy (`agy`): The Architect & Director (Our Role)

We act as the central authority on system constraints, framework decisions, and ADR validation.

* **Responsibilities:**
  * Reviewing handoffs from `cowork` and `claude`.
  * Inspecting audit verdicts submitted by `codex` and resolving logic clashes.
  * Resolving high-judgment forks (e.g., when the implementation strategy must deviate from the plan due to local inference constraints).

