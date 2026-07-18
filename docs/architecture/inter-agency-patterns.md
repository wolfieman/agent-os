# Harvesting Inter-Agency Patterns for Agent OS

This document outlines how the successful, hand-rolled collaboration patterns from the `inter-agency` repository are harvested, standardized, and promoted to first-class features of the `agent-os` kernel.

---

## 1. Summary of Promoted Patterns

| Inter-Agency Pattern | Promoted Kernel Feature | Description |
|---|---|---|
| Blackboard (`state.json`) | **Scheduler Task Blackboard** | An OS-managed task blackboard system. It tracks task states, assigned actors, plans, and completion checkpoints. |
| File Locks (`state.lock`) | **Concurrency Lock Manager** | A standardized mechanism for acquiring, renewing, and releasing lock leases on workspace paths to prevent concurrent write collisions. |
| Handoffs (`to_<actor>.md`) | **Structured Handoff Messages** | The basis of the Agent-to-Agent (A2A) protocol. Promoted from plain markdown to structured JSON/XML payloads. |
| `pending_approval` HITL Gate | **Harness HITL Oversight Gate** | Standardized Human-in-the-Loop gates triggered by risk heuristics (e.g. actions on sensitive paths or values above threshold). |
| UTC/Local Timestamps | **Timezone Offset Standard** | Enforced ISO 8601 timestamps using local timezones with offsets (e.g., `-04:00` or `-05:00`), never raw UTC `Z`. |

---

## 2. Blackboard State Promotion

The inter-agency `state.json` tracks a list of tasks. In `agent-os`, the blackboard is promoted to a scheduler-owned subsystem. 

- **Blackboard Schema:** Standardized to include nested plan steps, checklist verification, and target artifact links.
- **Active Task Filtering:** The kernel automatically filters out completed tasks into historical logs (`completed.jsonl`) to prevent context window bloat during dynamic state assembly.
- **Injection:** Injected directly into the Frame as a `<task_state>` block, providing a memory anchor for the active agent.

---

## 3. Concurrency Lock Leases

Locking in `inter-agency` was accomplished using raw JSON file reads/writes in `lock_manager.py`. In `agent-os`, locking is promoted to a core kernel service:

- **Expiring Leases:** Every lock has an expiration timestamp (default 20 minutes). Stale locks are automatically cleared by the kernel.
- **Acquire/Release System Calls:** The context plane provides `workspace_lock_acquire` and `workspace_lock_release` APIs.
- **Automatic Releases:** On successful completion of a task, or upon a terminal execution failure, the kernel scheduler automatically releases the lock lease, preventing deadlocks.

---

## 4. Structured Handoffs (The A2A Seam)

Handoffs in `inter-agency` were written as markdown files (`to_claude.md`, `to_agy.md`). While human-readable, this format is difficult for agents to parse deterministically.

In `agent-os`, handoffs are promoted to a two-part format:
1. **The Artifact:** The actual deliverable written directly to the target project repository.
2. **The Handoff Schema (Metadata):** A structured JSON payload detailing:
   - `task_id`: The ID of the completed task.
   - `status`: `completed` or `failed`.
   - `artifacts`: List of file paths produced.
   - `next_actions`: Clear requirements for the downstream actor.
   - `verification_proof`: Verification command outputs (e.g., test pass count, lint check exit status).

---

## 5. Harness HITL Gate & Time Policy

- **The HITL safety net:** The `pending_approval` status halts execution. The user can review the proposed handoff and execution plan before the scheduler dispatches the agent process.
- **Timezone offsets:** Every timestamp written to logs, traces, lock files, and handoffs must include the local timezone offset to avoid coordination errors during timezone shifts.
