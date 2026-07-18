# Rollout Planning: Shared Briefing for the Expert Panel

**Purpose.** This is the shared context every expert on the planning panel reads before drafting their slice. The goal is a lean-but-thorough phased plan to roll out **skills, MCP, RAG, subagents, agent-harness, A2A, CLI, API, and framework** patterns across Wolfgang Sanyer's repo estate. Read the companion `context-engineering-report.md` (both rounds) for the concept synthesis; this doc is the ground truth on *what already exists* so the plan builds on reality, not assumptions.

**Prime directives (house rules the plan must honor):**

- **DRY / single-source:** cross-repo things live once in `orchestrator` and are distributed, never copied.
- **Federated model:** `orchestrator` = index + standards; each repo owns its granular leaf state.
- **Capture → distill → graduate (rule of three):** a cross-repo standard is *earned* after a pattern proves itself more than once (source of truth for agentic standards is `agentic-lab`).
- **Dogfooding model:** we adopt agentic AI on three axes: (A) standards add/retrofit/enforce, (B) build by implementing, (C) operate the patterns on real work, all feeding the consulting sell-side. Using this panel to plan the rollout *is* axis B/C.
- **Right-tool discipline:** do not over-tool. CLI where the model already knows the tool; MCP only at a real gap or governance need; RAG only where a corpus plus adagio exist.
- **Privacy:** `life-admin` and `credential-ops`/`email-ops` are sensitive; real data is gitignored; do not design anything that puts PII in git.
- **Commits are human-run**, `[TAG][TYPE]` convention, no AI attribution.

---

## 1. The whole repo estate

| Code | Repo | Domain |
|---|---|---|
| `ORCHSTR` | orchestrator | Cross-repo standards hub + tooling + index (the library) |
| `AGENCY` | inter-agency | Multi-agent coordination: blackboard, handoffs, harness (the runtime) |
| `INFRA` | infrastructure-consulting | Practice + `lab/` AI infra + career (the backend + domain hub) |
| `LIFE` | life-admin | Personal ops: finance, health, household (lean, CLI/Python, private) |
| `EVPULSE` | ev-pulse-nc | EV infrastructure analytics (research / portfolio anchor) |
| `VENDOR` | vendor-scope | Vendor readiness analytics (portfolio; PWC case study) |
| `LODESTAR` | lodestar | IgniteAI app (live; Cloudflare Worker + Vectorize) |
| `SANYER` | sanyer-website | Portfolio website |
| `MARIAN` | marian-study | Ministry: RCIA study PWA |
| `AGENTIC` | agentic-lab | Agentic-AI build lab (LangGraph, MCP, evals, deploy) |
| `ACCT610` | spring-26-acct610 | Last active MBA course |

The four **chore repos** (`ORCHSTR`, `AGENCY`, `INFRA`, `LIFE`) are infrastructure; the rest are **projects** that consume from the chore repos and are orchestrated by `AGENCY`.

---

## 2. The four chore repos in detail

### orchestrator (the library / source)

- **`standards/`** (the single source of cross-repo conventions), tiers include: `agentic/`, `ai-codegen/`, `git/` (now has §6 "track vs local-only"), `docs-prose/`, `hooks/`, `ci/`, `cd/`, `python/`, `shell/`, `web-ts/`, `sql-data/`, `testing/`, `universal/`, `patterns/`, `principles/`, `brand/`, `claude-tooling/`, plus top-level `PLAYBOOK.md`, `tool-selection.md`, `advisor-tool-protocol.md`, `sdlc-tooling-survey.md`, `public-exposure-checklist.md`, `open-decisions.md`, `facets.md`.
  - **`standards/agentic/`** already exists: `context-and-chaining.md` (the context-engineering four-verb checklist), `collaboration-matrix.md` (the agent role matrix), `inter-agency-protocol.md`, `dogfooding-model.md`. New agentic standards graduate here.
  - **`advisor-tool-protocol.md`** documents the Advisor tool (see §4).
- **`tools/`**: `ws/` (the multi-repo git + workspace CLI, the flagship), `prompt_router/` (prompt registry + humanize flagger), `external_analysis.py`, `standards_facets.py`, `fleet_hook_rollout.py`, `convert_office_to_md.py`, `get-current-date.sh`.
- **`.claude/skills/`**: `evpulse` (one project-context skill). **`.claude/agents/`**: `repo-auditor.md`. User-level: a `prompt-authoring` skill and a `syllabus-map-checker` agent.
- **`prompts/`**: `meta/`, `notebooklm/`, `playbooks/`, `runbooks/`, `templates/`, `workflows/`.

### inter-agency (the runtime)

- **Actors** (with roles): `wolfie`, `agy` (Gemini architecture), `claude` (Sonnet dev CLI), `codex` (ChatGPT audits), `cowork` (labelled "hybrid agent harness"), `chromie`, `chatty`, `claudia`, `penny` (Perplexity research), `notebook` (NotebookLM synthesis), plus daemons `adagio` and `hope`.
- **Blackboard pattern:** each workspace has `processing/state.json` (tasks, statuses backlog/pending_approval/in_progress/completed/failed), `handoffs/to_[actor].md` (schema: What Has Been Done / Next Actions / Checkpoints), `locks/state.lock` (lease), `shared-context/`, `logs/`.
- **`tools/`**: `mcp_server.py` (a local MCP server already exists), `orchestrator.py`, `agent_ws.py`, `lock_manager.py`, `watcher.py` (desktop-notify harness daemon), `vm_control.py`, `constants.py`, `config.json`.
- **Workspaces:** `finc-analysis`, `home-network`, `job-hunting`, `seinforms`, `standards-reorg`, `inbox`.
- **Node infra:** `hope` (workstation, local `qwen-ov` iGPU inference), `adagio` (Ollama VM: `nomic-embed-text` for vectors, `qwen3:4b`).
- Human-in-the-loop `pending_approval` gate before any agent claims a task.

### infrastructure-consulting (the AI backend + practice/lab hub)

- `.claude/CLAUDE.md` present.
- **`lab/`** modules: `ai-ops` (**`agent.py`** Pydantic-AI agent, **`retrieval_server.py`** = a RAG/retrieval MCP, **`run_sql_server.py`** = a DuckDB/SQL MCP, `bench.py`, `Modelfile`), `cloud-ops` (deployment topology, tracked), `credential-ops` (KeePassXC, **local-only/untracked**), `email-ops` (mailbox.org, **local-only/untracked**), `home-network` (fleet inventory + runbooks, tracked).
- **`practice/`**: brand, business-planning, client-development, code, data, engagements, market-research, portfolio, references, research, service-offerings. **`career/`** and the cross-repo `OPEN-ITEMS.md` tracker.
- Fleet is CLI-first (`ws`, shell wrappers, VM launchers).

### life-admin (lean personal ops)

- `.claude/CLAUDE.md` present. Domains: `finance/` (budget = CSV + Python: `analyze_budget.py`, `loan_payoff.py`, `categories.csv`, `ACCOUNTING-CONVENTION.md`, `SANITIZATION.md`; real data gitignored under `data/`), `health/` (records gitignored), `household/` (dmv/legal gitignored PII).
- No agents, skills, MCP, or RAG. Privacy-first; the working `.xlsx` is gitignored, PDF is the canonical tracked artifact.

---

## 3. Current agentic assets, mapped to the terms

| Term | What already exists | Where |
|---|---|---|
| CLAUDE.md (context/persona) | Present everywhere | every repo `.claude/CLAUDE.md` |
| Skills | `evpulse` (project), `prompt-authoring` (user-level); Anthropic doc skills available in cowork | orchestrator + user-level |
| MCP servers | `mcp_server.py`; `run_sql_server.py` (DuckDB), `retrieval_server.py` (RAG); SaaS connectors | inter-agency `tools/`; infra `lab/ai-ops`; claude.ai |
| RAG / vector | `nomic-embed-text` on adagio; `retrieval_server.py`; lodestar Vectorize; `shared-context/` | adagio, infra ai-ops, lodestar, inter-agency |
| Subagents | `repo-auditor`, `syllabus-map-checker`; the Task tool | orchestrator + user-level |
| A2A | Blackboard + `to_[actor].md` handoffs + actor cards (hand-rolled) | inter-agency |
| Agent harness | Blackboard loop + `watcher.py` + `cowork` (labelled harness) | inter-agency + cowork |
| CLI | `ws` (flagship), `get-current-date.sh`, `agent_ws.py`, fleet shell scripts | orchestrator + inter-agency + infra |
| API | Underpins connectors, MCP servers, A2A-over-HTTP | cross-cutting |
| Frameworks | LangGraph study/build; role-based multi-agent (the actor set) | agentic-lab + inter-agency |
| Advisor / model levers | `advisor-tool-protocol.md`; `opusplan`; `ai-codegen` model/effort tiers | orchestrator standards |
| Governance | capture→distill→graduate; `dogfooding-model.md`; `standards/agentic/` | orchestrator |

**Headline for the panel:** `inter-agency` is already a hand-built A2A + harness + context-chaining system, and `infra/lab/ai-ops` already runs MCP + a RAG server + a Pydantic-AI agent. The rollout is mostly *formalizing and distributing* patterns that already exist in one place, not inventing from scratch.

---

## 4. The Advisor tool and model levers (for execution planning)

- **Advisor tool:** pairs a faster **executor** model with a stronger **advisor** model (Opus) that gives strategic guidance mid-generation. Use for multi-turn planning, risk assessment, long-horizon loops, and when a wrong early decision cascades. Skip for single-turn lookups and routine ops.
- **opusplan** (Opus plans upfront, Sonnet executes) is the sibling lever: use when the hard part is upfront. **They are alternatives, not a stack.**
- Relevance to this rollout: the *planning* is already running on Opus (cowork), so the advisor lever adds little here; it earns its keep in **execution**, when work runs on faster executors (Sonnet subagents or inter-agency actors). The plan should mark where advisor/opusplan calls belong.

---

## 5. The placement model (proposed, section 12 of the report)

**orchestrator sources, projects own, inter-agency runs, infra powers.**

| Artifact | Where it lives |
|---|---|
| General skill | orchestrator → symlink `~/.claude/skills` or plugin |
| Domain skill | the owning repo's `.claude/skills/` |
| Infra/standards MCP | orchestrator (ws/inventory) |
| Coordination MCP | inter-agency `tools/` (blackboard) |
| Data/vector MCP + RAG backend | infra `lab/ai-ops` + adagio |
| Project API/DB MCP or corpus RAG | the project repo |
| SaaS connectors | user-scope via claude.ai |
| Harness / loop | inter-agency + cowork |
| Subagents | cross-repo → orchestrator; domain → the repo |

---

## 6. What each expert returns (bounded template)

For *your domain only*, in this exact structure so synthesis stays clean:

1. **Inventory:** what already exists across the repos (cite §2/§3) vs what is missing.
2. **Placement:** where each artifact in your domain should live (per §5), and why.
3. **Sequence + dependencies:** the order to build, what you are blocked by, what you block.
4. **Risks / anti-patterns:** what to avoid (over-tooling, DRY breaks, privacy, drift).
5. **First move:** the single highest-leverage first step, with a concrete eval / done-criterion.

Keep it tight. You are one voice; the architect merges the nine into one phased plan.
