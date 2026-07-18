# Claude Code Instructions - agent-os

## What this repo is

An operating system for AI agents: the kernel that manages scheduling, memory,
sandboxed tools, identity, observability, and guardrails for autonomous agents. This
is the build home for the agent OS. Research and strategy context live in `docs/`.

The current coordination system (`inter-agency`) is the working reference. Its proven
patterns (lock leases, the actor registry, the handoff schema, the human-in-the-loop
gate) are harvested as OS requirements in
`docs/architecture/inter-agency-patterns.md`. This repo re-architects them cleanly; it
does not replace inter-agency until the kernel is proven.

## Standards (house, in the orchestrator repo, follow these)

- **Commit convention:** `../../orchestrator/standards/universal/commit-convention.md`.
  This repo's tag is **AGENTOS**: `[AGENTOS][TYPE] imperative subject`.
- **Python tooling:** `../../orchestrator/standards/python/tooling.md` (uv-only, ruff
  at line-length 88, pyright; every module docstring ends with the two-line Polyform banner).
- **Git / hooks:** `../../orchestrator/standards/git/README.md`.
- **Naming:** `../../orchestrator/standards/universal/naming-conventions.md`
  (domain-subject-grain, kebab-case directories, snake_case Python).
- **Licensing:** Polyform Noncommercial 1.0.0.

## Architecture

The design is the three-layer model (agents / kernel / infrastructure). The six kernel
services are specced in `docs/architecture/kernel/` and built one at a time as a
walking skeleton, observability first. The teams layer is policy on top of the kernel
and lives in the future sibling repo `agent-teams`, documented in
`docs/architecture/agent-teams.md`.

## Assets and commits

Repo agentic assets are listed in `.claude/assets.md`, created when the first asset
lands. Commits are human-run: agents stage work and hand off; wolfie runs `ws`.
