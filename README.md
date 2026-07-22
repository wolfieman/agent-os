# 🤖 agent-os

An operating system for AI agents. A small kernel that gives autonomous agents what a real OS gives applications: scheduling, memory, sandboxed tools, identity, observability, and guardrails. The goal is agents that run as infrastructure you can trust, not as unsupervised one-off scripts.

## 🧱 The Three Layers

- **Agents** (top): the workers that do tasks.
- **Kernel** (middle): the six services this repo builds. Scheduler, memory manager,
  tool manager, identity manager, observability, guardrails.
- **Infrastructure** (bottom): the models, stores, and tools the kernel manages.

Teams of agents (roles, feedback loops) are *policy* built on top of the kernel. They live in a separate sibling repo, `agent-teams`, documented here under `docs/architecture/agent-teams.md` until it is stood up.

## 🚦 Status

OS Phase 0 is complete: the observable context-plane walking skeleton (the four context verbs, the scheduler, the observability trace, and the `examples/log_look.py` validator) is built and tested. The remaining kernel services come next, incrementally. Start at `docs/README.md` for the map, and `docs/planning/agentic-rollout-plan.md` for the plan.

## 🗂️ Layout

- `docs/research/`: the research this is grounded in (a synthesis plus source transcripts).
- `docs/architecture/`: the OS design (overview, layering, per-service specs).
- `docs/decisions/`: architecture decision records.
- `docs/planning/`: the initiative plan and its briefing.
- `src/agent_os/`: the kernel (Python).
- `tests/`, `evals/`, `examples/`: verification and the teams-seam stub.

## 📜 License

Polyform Noncommercial 1.0.0. See `LICENSE`.
