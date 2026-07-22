# 🚀 Agentic Rollout Plan (v1)

**Status:** APPROVED.
**Source:** synthesized from a 9-expert planning panel (skills, MCP, CLI, subagents, harness, A2A, RAG, API, frameworks), each grounded against the real repos. **Date:** 2026-07-17.

**Progress (2026-07-22):** OS Phase 0 (the observable context-plane walking skeleton) is complete and validated: the four context verbs, the scheduler, the observability trace, `examples/log_look.py`, and passing unit tests are on disk, producing `examples/logs/trace.jsonl` end to end. The `ws` workflow shipped the task-approval and task-launch protocols and retired `orchestrator.py`, which closes the harness bug flagged below (completion on exit-code-0, hardcoded `repo_dir`) and most of Phase 3. Estate Phase 0 (the two agentic standards) is now unblocked and resuming.

---

## 🔍 What the Panel Found (Corrections to the Briefing)

The experts verified against source and surfaced assets the briefing missed. These change the baseline:

- **lodestar already has a project MCP** (`lodestar/src/lodestar/mcp_server.py`: `retrieve_knowledge`, `get_career_advice`) plus a live Cloudflare Worker API. Project-MCP count is 1, not 0.
- **sanyer-website already has 16 subagents** (a "domain council": brand-steward, copywriter, ux-architect, seo-specialist, etc.), all tightly tool-scoped. The best real instance of the subagent standard in the estate.
- **~18 to 23 subagents exist total**, with a logged audit debt (predate the sizing + tool-scoping rules; never audited).
- **The harness already runs** (`inter-agency/tools/orchestrator.py`: subprocess-per-task = fresh context per iteration, HITL start gate). But it has a real bug: it marks a task `completed` on **subprocess exit code 0 alone** (no verification), and hardcodes `repo_dir = ev-pulse-nc` regardless of `--workspace`. No process timeout.
- **The infra MCP/RAG servers are demo-mode** (`run_sql_server.py` on sample data, `retrieval_server.py` ingested only against its own docs). They *work* but prove nothing on real content.
- **adagio's Ollama endpoint has no app auth** (Tailscale-only), and `agent.py` uses `api_key="ollama"` (a placeholder). Flagged as the estate's top security gap. The adagio URL is DRY-broken (hardcoded in two repos).
- **Distribution is already answered:** `standards/claude-tooling/skills-and-agents.md` §5 prescribes symlink-now, plugin-later. Not a new decision.

## 📍 Confirmed: The Placement Model

All nine experts confirmed it: **orchestrator sources, projects own, inter-agency runs, infra powers.** No changes.

## 🗝️ Key Decisions the Panel Made (Deferrals Worth Noting)

- **DEFER the orchestrator/`ws` inventory MCP.** `ws status --json` already gives structured state to every Bash-capable actor; an MCP peer would be schema cost for zero new capability. Build only if a non-Bash actor (agy, codex) genuinely needs it. *(This overrules the briefing's suggestion.)*
- **DEFER formal A2A** (Agent Cards over JSON-RPC/HTTP/SSE) to `agentic-lab` backlog, gated on a real external/vendor agent to interoperate with. The cheap on-path step (an actor-card sidecar) is in Phase 4.
- **DEFER plugin distribution.** Symlink now; graduate to a plugin only at the rule of three (3+ shared skills) or a second machine.
- **Frameworks: only `agentic-lab` (LangGraph).** Everything else stays framework-light; do not port the working blackboard to CrewAI/AutoGen.

---

## 📋 The Phased Plan

Each phase: **Goal · Tasks · Depends on · Done-criterion.** Owners map to the inter-agency execution team.

### Phase 0: Foundation & Reconciliation (Cheap, Gates the Rest)

- **Goal:** correct the ground truth and write the two standards that discipline every later build decision.
- **Tasks:**
  - Reconcile the asset inventory (add the lodestar MCP + sanyer's 16 subagents; settle the "~23 subagents" count).
  - Write `standards/agentic/cli-vs-mcp.md` (CLI for what the model knows cold; MCP only at a real gap or governance need) with a pointer table of existing CLI assets.
  - Write `standards/agentic/api-constants.md` (auth minimum, rate-limit/budget-cap modeled on lodestar's Worker, stdio-vs-HTTP transport rule, docs bar).
  - Record the **adagio auth decision** (accept-and-document Tailscale-only, or add a credential) and single-source the adagio base URL into a standard.
- **Depends on:** nothing.
- **Done:** the two standards exist and the next MCP/API proposal cites them; the adagio decision is written down; the inventory is corrected.
- **Owner:** claude (authoring) + wolfie (review/adagio decision).

### Phase 1: Skills First (Pilot) + Subagent Audit

- **Goal:** prove the skills pattern end-to-end on the lowest-risk, highest-repetition surface, and close the subagent debt.
- **Tasks:**
  - Author `life-admin/.claude/skills/budget-close/SKILL.md` (wraps `analyze_budget.py` + `ACCOUNTING-CONVENTION.md`), project-scoped, no distribution (privacy-first). Then `loan-payoff`.
  - Run both through `skill-creator`'s on/off baseline eval.
  - Audit the ~18 existing subagents against `skills-and-agents.md` §4 (tool-scope + sizing); record pass/fail; close or re-scope the logged debt.
- **Depends on:** nothing (skills are standalone).
- **Done:** "close out July's budget" auto-triggers the skill and reproduces the hand-run `close-summary.md` in fewer turns, no steps skipped; every subagent has a recorded verdict.
- **Owner:** claude (skills + audit) + wolfie (privacy sign-off on any credential-ops skill).

### Phase 2: Prove MCP/RAG on Real Data + the Standards Index

- **Goal:** move the infra servers from demo to real, and stand up the "query our own knowledge" tool.
- **Tasks:**
  - Point `run_sql_server.py` at a real practice/engagement dataset (`DUCKDB_PATH`); point `retrieval_server.py` at a real corpus.
  - Build the **orchestrator-standards + agentic-research RAG index** (`standards.db`) via the *existing* `retrieval_server.py` (one server, many indexes via `RAG_DB_PATH`); register it; document a manual re-ingest trigger.
- **Depends on:** adagio reachable (Phase 0 auth decision); Phase 0 cli-vs-mcp standard (so no redundant servers get built).
- **Done:** `list_schema` returns real tables; `search_docs` answers 4/5 real past-confusion questions with the right source file; no life-admin/credential-ops/email-ops data indexed.
- **Owner:** claude/codex (ai-ops) + hope/adagio (backend).

### Phase 3: Harness: Fix the Finish-Gate, Then Formalize

- **Goal:** close the real bug before documenting the pattern.
- **Tasks:**
  - `orchestrator.py`: require a verification line in the handoff "Checkpoints" before `complete_task` (else re-surface for human finish-approval); parameterize `repo_dir` per workspace via `config.json`; add a subprocess wall-clock timeout; **deny-list** life-admin/credential-ops/email-ops from auto-execution.
  - Then write `standards/agentic/agent-harness.md` documenting the gap-closed contract (fresh context per iteration, start gate, **finish gate**, requirements-doc convention). Document cowork as a second instance of the same schema.
- **Depends on:** should precede Phase 4 (A2A cards operate inside the loop; fix the finish-gate first).
- **Done:** a task whose dispatched agent omits the verification line is refused completion and re-surfaced; a proper one completes; the standard documents the true behavior.
- **Owner:** claude (code) + wolfie (HITL).

### Phase 4: A2A: Machine-Readable Actor Cards (On-Path, Cheap)

- **Goal:** take the one real step toward A2A without building a protocol.
- **Tasks:** generate an actor-card sidecar (role/inputs/outputs) *from and validated against* `collaboration-matrix.md` (extend the `VALID_ACTORS` single-source pattern); expose it via `mcp_server.py` resources.
- **Depends on:** Phase 3 (harness contract); Phase 0 api-constants (if any HTTP is ever added later).
- **Done:** editing the matrix without updating the sidecar fails validation non-zero; the coordination MCP returns capability fields per actor.
- **Owner:** agy (architecture) + claude.

### Phase 5: Frameworks: The One Real Build

- **Goal:** the single legitimate framework build; keep it scoped.
- **Tasks:** finish `agentic-lab` Phase 1 (`prompt_chain.py`, currently `NotImplementedError`), then a **2-node LangGraph graph (researcher → writer) with checkpointing** as the first increment; add the reviewer loop as a second increment.
- **Depends on:** agentic-lab Phase 1 (already PIPELINE Active Focus #4).
- **Done:** a runnable checkpointed `StateGraph` produces one reviewed artifact; logged in `agentic-lab/docs/LEARNING-LOG.md`.
- **Owner:** claude (build).

---

## 🔀 Cross-Cutting (Applies to Every Phase)

- **Capture → distill → graduate:** each proven pattern graduates into `standards/agentic/` (rule of three); the study/build source of truth stays `agentic-lab`.
- **Privacy deny-lists:** life-admin, credential-ops, email-ops are never auto-executed by the harness, never indexed into a shared RAG, never scoped to a broad-access subagent. Hard checks in code, not just docs.
- **Advisor / opusplan for execution:** when a phase runs on faster executors (Sonnet subagents, inter-agency actors), wrap the high-judgment forks (architecture validation, "is this the right tool") with the advisor; Opus (this session) reviews the merged output.
- **Commits human-run**, `[TAG][TYPE]`, no AI attribution.
- **Right-tool discipline everywhere:** default CLI; MCP only at a gap; RAG only where grep fails; framework only where a shape demands it.

## ➕ Addendum v1.1: Three Cross-Cutting Disciplines

Added 2026-07-17 from the `a2a/` research (A2A protocol, multi-agent systems, and the IBM+Anthropic secure-agents guide). These sharpen the plan's weakest axis: not "can agents act" but "do they act *correctly, safely, and verifiably*."

### A. Framework & Structure Selection (Pick by Shape, Not Popularity)

Selection is two nested questions, not one:

1. **Single vs multi-agent.** Multi wins for complex, multi-domain, scale-across-changing-environments work (it outperforms single: more action plans, more reflection and synthesis). Single wins for bounded work. The tax of multi is real: shared-LLM pitfalls, coordination complexity (agents overriding each other), amplified unpredictability. "Too many cooks."
2. **If multi, which structure:** decentralized network (peers, equal authority) vs hierarchical/supervisor (manager, supervisors, workers) vs dynamic (authority shifts by expertise/situation). Only after structure do you pick a framework (the five shapes).

Your estate maps cleanly: inter-agency = **hierarchical role-based** (wolfie/orchestrator supervises; claude/codex/etc. are workers), hand-built and correct; agentic-lab = production orchestration (LangGraph); everything else single-agent / CLI / framework-light.

**Deliverable:** `standards/agentic/framework-selection.md` (single-vs-multi test + structure rubric + the five-shapes table + the estate mapping). Slots into **Phase 0** as a gating standard; governs **Phase 5**.

### B. Harness Enforcement (Make the Boundary Real; Do Not Trust Behavior)

The harness must **deterministically enforce** controls, not rely on the agent behaving. The panel already found the gap (a task auto-completes on exit-code-0). The IBM+Anthropic secure-agents guide names the full control set to enforce:

- **Least privilege + sandboxing:** each agent gets only the tools/paths it needs, in a sandbox; the privacy deny-list (life-admin, credential-ops, email-ops) is a hard sandbox boundary in code.
- **Non-human identity:** each agent has a unique credential; no shared creds. Two current failures: `api_key="ollama"` (placeholder) and the self-asserted actor-string in `mcp_server.py` (unverified).
- **Just-in-time / time-based access + RBAC:** the lock lease is a start; extend to scoped, expiring permissions per role.
- **Observable traces + audit:** every decision/action logged and traceable to *which* agent.
- **HITL oversight:** the `pending_approval` gate; keep it, add the finish-side gate.
- **AI firewall / proxy** for input and MCP calls: prompt-injection detection + data-loss prevention on data flowing out.

**Expands Phase 3:** the harness work grows from "fix the finish-gate" to "fix the finish-gate + stand up the enforcement layer" (identity, scoped permissions, audit log, sandbox boundary). Ground it in the actual IBM+Anthropic guide.

### C. Communication Verification: How Do We Know They Deliver the Right Stuff?

The answer is a paradigm shift the secure-agents guide names outright: **evaluation-first** (measure outcomes against the stated goal, not implementation). Concretely, a four-layer verification stack for every agent-to-agent handoff:

1. **Contract (up front):** every task carries explicit **acceptance criteria** (what "done right" means). This is the A2A model: the client sets the goal, the remote returns **artifacts** (tangible outputs: a doc, structured data), and can "request more information" mid-task. Plus the harness requirements-doc.
2. **Gate (at finish):** the harness refuses completion without **structured proof** (test run, output check against criteria), not exit-code-0. The panel's Phase-3 fix, promoted to a first-class rule.
3. **Judge (independent):** the artifact is checked against the criteria by something *other* than its author: LLM-as-judge (agentic-lab Phase 4 evals) or the **Advisor tool** (Opus reviewing a faster executor's output). This is exactly where the advisor earns its keep in execution.
4. **Trace + audit:** observable traces of the reasoning + an audit record (which agent produced what, checked how). The governance layer; what lets you trust the system over time.

Your file-based handoffs already have a rough version (What Has Been Done / Next Actions / Checkpoints); the verification stack makes "Checkpoints" carry real proof.

**Cross-cutting, touches Phase 3/4:** verification is a discipline every phase inherits, not one phase. Capture it as `standards/agentic/verification.md` (or fold into `agent-harness.md`): acceptance-criteria contract, finish gate, independent judge, audit trace.

---

## ➕ Addendum v1.2: The agent-os Pivot and the Context Plane

Added 2026-07-18. Working Phase 0 bullet 1 (reconcile the inventory) surfaced that the highest-leverage asset is not a doc to catalog but a system to build: an **agent operating system** (`agent-os`, its own repo). The initiative's center of gravity is now that build; the estate-wide Phase 0 above is **paused, contingent on the OS** (writing the asset map and the CLI/MCP/API standards before the OS exists means writing them twice, since the OS reorganizes what the assets are and how they are categorized). Research and plan now live in `agent-os/docs/`; live coordination stays in `inter-agency/context-engineering/`.

### The Foundation: The Context Plane

The OS is built kernel-first, one service at a time (walking skeleton). Its **foundation is the context plane**: the layer that constructs every model call, sitting under the six kernel services and above the raw model.

```
agents / teams    actors that run
kernel services   scheduler, memory, tools, identity, observability, guardrails
CONTEXT PLANE     context-assembly (mechanism) + prompt library/standard (resource)
model             the raw LLM
```

Two categories, one role:

- **Context engineering is a kernel subsystem** (a mechanism the OS runs): the
  context-assembly service, real code in `src/agent_os/`.
- **Prompt engineering is a discipline plus a managed resource:** the craft of the
  instruction slot and the prompt library it draws from, held to a prompt-craft
  standard. This half is not new work: it already exists as a mature body of standards
  in orchestrator (detailed below), consumed by reference.
- **Neither is an actor.** Agents run on the plane; they are not peers of it. Together
  the two form the plane, the OS foundation. ADR
  `0006-context-plane-as-kernel-foundation` records this and resolves the earlier open
  question: context-assembly is a distinct subsystem, not folded into memory and not a
  seventh peer service.

**Prompt engineering is the base of context engineering, not a peer of it.** The instruction slot is the small static core, roughly 20 percent, that the plane wraps in dynamically assembled content, roughly 80 percent: memory, task state, retrieval, and tool interfaces populated at runtime. Put plainly: better prompts give better questions; the plane gives better systems. Prompt-craft is the foundation the plane is built on, which is why the two standards were always going to converge.

### What the Plane Is Made Of (From the Context-Engineering Research)

- **The frame** is the plane's output schema, assembled per call from four services:
  instructions and output-format (guardrails), user input (scheduler), retrieved facts
  plus short-term and long-term memory (memory), tools and their schemas (tool manager,
  fed by the asset-map registry). To these, promote one ingredient the original
  7-piece stack understates to **first-class status: task state, owned by the
  scheduler.** It is the multi-step progress that keeps an agent from losing context
  mid-task (did the flight book, what is the arrival time), it is distinct from memory,
  and it is your `state.json` blackboard pattern in frame form. So the frame is the
  seven pieces plus a first-class, scheduler-owned state slot.
- **The four operations are the plane's API:** write, select (hybrid keyword plus
  semantic, backed by adagio `nomic-embed` plus a keyword index), and compress (the
  memory service surface); isolate (tool sandbox plus scheduler subagent dispatch,
  which is why the teams layer is a context-safety mechanism, not just an org chart).
- **The four failure modes are the plane's fault taxonomy:** poisoning (provenance
  tracking, evict on trace), distraction (automatic compaction plus a fresh-plan
  checkpoint), confusion (relevance filter on select), clash (contradiction detection
  plus a precedence policy). Instrumented by observability and guardrails.

### The Prompt-Engineering Half Already Exists (orchestrator)

The plane's instruction-slot discipline is not new work; it is a mature body of standards in orchestrator, distilled from Anthropic's prompt-engineering guide and tuned for Opus 4.8. The OS consumes these by reference (orchestrator owns them, the OS cites them, nothing is copied):

- **The rules:** `standards/ai-codegen/prompt-authoring.md`, an 18-rule authoring
  standard where each rule carries its *why* (specific output and constraints, positive
  framing, role, few-shot examples, XML structure, an explicit EVALUATION / self-check
  step, right-sized autonomy, Goldilocks system-prompt sizing, long-context handling
  with data-at-top and query-at-end and quote-grounding).
- **The library (a formality ladder):** `prompts/templates/` holds AIM (quick
  single-shot: Actor / Input / Mission), BRIDGE (full rigor: background, scoped inputs,
  guardrails, evaluation), and MAP (Memory / Assets / Actions / Prompt). MAP already
  structures the *context* you feed, so it is the bridge between the two halves of the
  plane.
- **The quality gates:** `prompts/meta/` holds the matched set that runs over a draft:
  verify-checklist (is it true), humanization-checklist (does it sound human),
  OCEAN-framework (is it good). These map to the OS guardrails plus the AgentOps
  evaluation layer.
- **The registry:** `tools/prompt_router` reads YAML frontmatter (id, purpose,
  task_type, triggers) as a keyword-selectable registry, and the user-level
  `prompt-authoring` skill surfaces the library on demand. This is the precursor to the
  OS selecting a prompt for the instruction slot.

Two things this settles. First, the prompt and context standards are **already connected**: `prompt-authoring.md` rule 16 cross-references `standards/agentic/context-and-chaining.md` §3 (the failure-mode taxonomy), and MAP plus rule 14 (long-context) already reach into context engineering. The plane operationalizes an already-linked pair; it does not invent the union. Second, the **co-evolution loop** is concrete: the built plane graduates refinements back into `prompt-authoring.md` and `context-and-chaining.md`, both written for the manual / artifact world and now getting OS-aware extensions.

### OS Phase 0: Stand Up the Observable Context Plane

The OS's own Phase 0 is the walking skeleton: **an observable context-assembly service** that builds the 7-piece frame, applies prompt-craft to the instruction slot, and emits a trace of what it assembled. This fuses the two foundations (context plus prompt) with the AgentOps ordering (observability first): the trace of the frame is exactly how the four failure modes get caught. The five remaining kernel services are later increments that plug into the plane.

- **Done-criterion:** a LogLook-analog agent (a fleet-log or mailbox-ops triage agent
  on real data) runs end to end on the plane, exercising all seven frame pieces and all
  four verbs, with a readable trace. First `examples/` app.
- **Standards co-evolution loop:** the built plane graduates refinements back into
  `orchestrator/standards/agentic/context-and-chaining.md` and a new prompt standard
  (both were written for the manual world and get OS-aware extensions when the paused
  estate Phase 0 resumes).

---

## 🧭 Open Decisions for wolfie (Before or During Execution)

1. **adagio auth:** accept-and-document Tailscale-only, or add a real credential? (Phase 0.)
2. **Pilot confirmation:** life-admin `budget-close` as the first skill? (Phase 1.)
3. **Execution team:** run each phase via my subagents, or route to the real inter-agency actors (agy/codex/...) via the blackboard? (The plan assumes the latter for the dogfood; confirm.)
4. **Sequencing appetite:** run phases strictly in order (0→5), or parallelize the independent ones (Phase 1 skills + Phase 5 agentic-lab have no cross-dependency)?
5. **Secure-agents guide:** should I pull the actual IBM + Anthropic "architecting secure enterprise AI agents with MCP" guide to ground the Phase-3 enforcement layer and the verification standard in the primary source?
6. **New standards:** framework-selection and verification as standalone `standards/agentic/` docs, or folded into fewer docs (e.g. verification into `agent-harness.md`)?

---

## ➕ Addendum v1.3: Architecture Alignment & Next Moves

Added 2026-07-18. Following a deep architecture review, the open questions from the cowork handoff and the open decisions have been resolved and aligned with the architectural specifications in `docs/architecture/`.

### A. Recommended Decisions for wolfie

1. **adagio auth:** Accept Tailscale-only for local coordinate transport, but require token-based auth for the VM database write tools. Set a unique API key for each agent in their local environment config (rather than the global placeholder `"ollama"`) to satisfy the secure-agents guide's **non-human identity** principle.
2. **Pilot confirmation:** Confirm `life-admin` monthly `budget-close` and `loan-payoff` as the first skills. Set `disable-model-invocation: true` on both skills in frontmatter to guarantee they are only triggered manually by the user, ensuring financial operations are never run autonomously.
3. **Execution team:** Route the execution of rollout tasks to the actual inter-agency actors (agy, cowork, codex) via the blackboard state.json protocol to dogfood the coordination fabric.
4. **Sequencing appetite:** Run Phase 1 (skills) and Phase 5 (agentic-lab LangGraph) in parallel to maximize development velocity, as they have zero cross-dependencies. Gate the core OS kernel development on Phase 0 and Phase 2 (RAG/adagio setup).
5. **Secure-agents guide:** The core principles (least privilege, sandboxing, non-human identity, audit trails, and input/output proxy gateways) have been harvested from the IBM+Anthropic guide and integrated directly into the `agent-os` architecture specs.
6. **New standards:** Fold the framework-selection rubric and A2A verification rules into a single consolidated `standards/agentic/architecture-principles.md` inside `orchestrator` to keep standards documentation DRY and dense.

### B. OS Phase 0 Implementation Plan (Walking Skeleton)

The initial implementation will stand up the Context-Assembly service as the minimal observable core.

1. **Directory Stubbing:**
   - `src/agent_os/kernel/context.py`: Contains `ContextAssemblyService` exposing `write`, `select`, `compress`, and `isolate`.
   - `src/agent_os/kernel/scheduler.py`: Contains a lightweight blackboard state reader.
   - `src/agent_os/observability/trace.py`: Contains JSONL trace logger.
2. **Done-Criterion Validator (examples/log_look.py):**
   - Create a diagnostic triage agent (`examples/log_look.py`) that reads system/fleet log entries.
   - It invokes `ContextAssemblyService` to construct its frame (instructions, log data as user input, active blackboard step state, and tool schemas).
   - Runs the agent query (streamed) and writes a complete trace file showing frame construction, inputs, outputs, and provenance.
