# 🗺️ agent-os docs: The Initiative Map

This is the "you are here" for the agent-os initiative: what it is, where each piece lives, and the current status.

## 🎯 What This Is

Building an operating system for AI agents (a kernel: scheduler, memory, tools, identity, observability, guardrails), with a teams layer as a future sibling repo. It grew out of the context-engineering research effort.

## 📍 Where Things Live

- **Research** (`research/`): `context-engineering-report.md` is the synthesis;
  `sources/` holds the source transcripts it distills.
- **Architecture** (`architecture/`): the OS design. `overview.md`, `layering.md`,
  `agent-teams.md`, `inter-agency-patterns.md`, and per-service specs in `kernel/`.
  (to be written)
- **Decisions** (`decisions/`): architecture decision records. (to be written)
- **Planning** (`planning/`): `agentic-rollout-plan.md` is the initiative plan;
  `rollout-planning-briefing.md` is the panel input that fed it.

## 🚦 Status

- Context-engineering rollout: **Phase 0 paused**, contingent on building this OS. The
  verified inventory and the two-tier asset-map design are recorded in the plan.
- Live coordination for this initiative runs in `inter-agency/context-engineering/`
  (its symlinks point back into this repo).
- Next: write the architecture and decision docs, then the v0 walking skeleton
  (observability first).
