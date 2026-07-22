# ⚙️ Agent OS Kernel Services: Specifications

This document outlines the detailed specifications, boundaries, and interfaces for the six core kernel services of Agent OS.

---

## 🗓️ 1. Scheduler Service

The Scheduler is responsible for managing task lifecycles, assigning tasks to agents, and ensuring execution order.

- **Responsibilities:**
  - Maintain the active blackboard state (`state.json`).
  - Enforce Human-in-the-Loop (HITL) gates on tasks marked `pending_approval`.
  - Dispatch agent processes in isolated sandbox environments.
  - Coordinate workspace lock leases.
- **Syscall / API Interface:**
  - `get_task_state(task_id: str) -> TaskState`
  - `claim_task(task_id: str, actor_id: str) -> bool`
  - `complete_task(task_id: str, actor_id: str) -> bool`
  - `fail_task(task_id: str, actor_id: str, error: str) -> bool`

---

## 🧠 2. Memory Manager Service

The Memory Manager gives agents short-term and long-term context retention.

- **Responsibilities:**
  - Manage short-term sliding conversational history (truncating/summarizing older turns when token bounds are approached).
  - Retrieve relevant facts/rules from long-term memory databases using vector similarity search (via adagio `nomic-embed` and local SQLite indices).
  - Maintain episodic memory of past attempts (successes and failures) to prevent repetitive errors.
- **Syscall / API Interface:**
  - `get_chat_history(session_id: str) -> list[Message]`
  - `retrieve_context(query: str, filters: dict, limit: int) -> list[MemoryChunk]`
  - `write_memory(session_id: str, content: str, type: str) -> bool`
- **Relationship to the context-plane verbs:** the plane's `select` verb (`src/agent_os/kernel/context.py`) is the frame-assembly entry point and calls `retrieve_context` here to pull long-term slices. `select` reads the active frame, `retrieve_context` reads the memory store: two layers of one read path, not duplicates.

---

## 🧰 3. Tool Manager Service

The Tool Manager acts as a dynamic toolbox for the agent, exposing schemas and executing commands.

- **Responsibilities:**
  - Maintain the registry of available tools (CLI scripts, MCP servers, and system actions).
  - Expose JSON schemas of tools to the Context Plane.
  - Support **Tool Search** (progressive disclosure) so the agent only loads schemas relevant to the current task context, keeping the frame lean.
  - Coordinate stdio and HTTP/WebSocket MCP server connections.
- **Syscall / API Interface:**
  - `get_tool_schemas(context_tags: list[str]) -> list[dict]`
  - `execute_tool(tool_name: str, arguments: dict, sandbox_id: str) -> ToolResult`

---

## 🪪 4. Identity Manager Service

The Identity Manager establishes trust, authentication, and actor credentials.

- **Responsibilities:**
  - Manage unique non-human identities for agents (each agent has its own identifier and scoped credentials).
  - Issue short-lived, expiring access tokens for tools and workspace paths.
  - Verify that the calling agent is authorized to run a requested tool or access a specific path (RBAC/Risk-Based Access Control).
- **Syscall / API Interface:**
  - `get_actor_identity(actor_id: str) -> Identity`
  - `verify_access(actor_id: str, resource: str, action: str) -> bool`
  - `issue_token(actor_id: str, scope: str, duration: int) -> Token`

---

## 📹 5. Observability Service

Observability is the "security camera" of the OS, recording execution metrics and decision paths.

- **Responsibilities:**
  - Log complete structured traces of every assembled Frame and model response.
  - Track AgentOps performance metrics: end-to-end trace duration, agent-to-agent handoff latency, tool execution latency, and cost per request.
  - Support the LogLook diagnostic agent, enabling autonomous triage of fleet failures.
- **Syscall / API Interface:**
  - `log_trace(trace: dict) -> bool`
  - `record_metric(metric_name: str, value: float, metadata: dict) -> bool`
  - `get_traces(filters: dict) -> list[dict]`

---

## 🛡️ 6. Guardrails Service

Guardrails act as the safety net, analyzing inputs and validating outputs.

- **Responsibilities:**
  - **Input Guardrails:** Inspect incoming prompts for prompt injections or malicious override attempts.
  - **Output Guardrails (AI Firewall):** Inspect model outputs before executing actions or returning results to verify structured formatting (e.g. valid JSON) and prevent Data Loss Prevention (DLP) violations.
  - **Verification Enforcement:** Enforce the "finish gate" rule, rejecting task completion if the output lacks verified proof (e.g. output format check, test check).
- **Syscall / API Interface:**
  - `validate_input(prompt: str) -> bool`
  - `validate_output(output: str, schema: dict) -> OutputValidationResult`
