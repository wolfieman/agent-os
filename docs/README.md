# 🗺️ agent-os docs: The Initiative Map

This is the "you are here" for the agent-os initiative: what it is, where each piece lives, and the current status.

## 🎯 What This Is

Building an operating system for AI agents (a kernel: scheduler, memory, tools, identity, observability, guardrails), with a teams layer as a future sibling repo. It grew out of the context-engineering research effort.

## 📍 Where Things Live

- **Research** (`research/`): `context-engineering-report.md` is the synthesis; `sources/` holds the source transcripts it distills.
- **Architecture** (`architecture/`): the OS design. `agent-os-architecture.md` (the master), `overview.md`, `layering.md`, `agent-teams.md`, `inter-agency-patterns.md`, and the per-service specs in `kernel/services.md`.
- **Decisions** (`decisions/`): architecture decision records. `0006-context-plane-as-kernel-foundation.md` and `0007-framework-light-kernel-design.md`.
- **Planning** (`planning/`): `agentic-rollout-plan.md` is the initiative plan; `rollout-planning-briefing.md` is the panel input that fed it.

## 🚦 Status

- **OS Phase 0, the observable context-plane walking skeleton, is complete and validated.** The four context verbs (`src/agent_os/kernel/context.py`), the scheduler, the observability trace, `examples/log_look.py`, and the unit tests are on disk, and a full run produces `examples/logs/trace.jsonl` end to end.
- **Estate-rollout Phase 0** (the two agentic standards, `cli-vs-mcp.md` and `api-constants.md`) is unblocked and resuming; it was paused contingent on the OS, which now exists.
- Live coordination for this initiative runs in `inter-agency/context-engineering/` (its symlinks point back into this repo).
- **Next:** either resume estate Phase 0 (draft the two standards, plus the adagio auth decision and the asset-map reconciliation) or continue the OS kernel (graduate the mock verbs to real `select` / `compress` / `isolate`, then the remaining five services). The track order is wolfie's call.
