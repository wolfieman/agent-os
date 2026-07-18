# 🧠 Context Engineering, Skills, and MCP

**A synthesis of the agentic-research reading set. Living document; more research to be appended.**

- **Started:** 2026-07-17
- **Phase:** the *context engineering* stage of the agentic-AI research (skills, MCP, and the framing terms), following the *prompt engineering* stage already absorbed into the orchestrator standards.
- **Source docs (this folder):** `five-terms-you-need-to-know-about-agentic-ai.pdf`, `context-engineering-guide.pdf`, `agent-skills-overview.pdf`, `mcp-server-overview.pdf`, `mcp-servers-vs-skills.pdf`.

---

## 🦴 1. The Spine: The Five Terms

The IBM doc is the cleanest frame. A modern agent has five building blocks, in three groups:

- **Inside the agent (shape behavior):**
  - `AGENTS.md` (our `CLAUDE.md`): project instructions read on entry, nestable, closest-to-working-dir wins.
  - **Agent Skills:** a folder plus `SKILL.md` teaching *one kind of task*, loaded only when relevant.
- **Reaching outward:**
  - **MCP** (Model Context Protocol): agent to tools and data.
  - **A2A** (Agent-to-Agent): agent to agent, via a published "Agent Card."
- **Scaling:**
  - **Subagents:** child agents in *fresh* context windows for work too big or embarrassingly parallel.

| Term | What it is | Already in my world |
|---|---|---|
| `CLAUDE.md` | Per-project agent instructions | `.claude/CLAUDE.md` across every repo |
| Agent Skills | Task-specific know-how, loaded on demand | Large existing skills library |
| MCP | Standard access to external tools/data | Connectors (Gmail, Calendar, Drive), mcp-registry |
| A2A | Agent-to-agent coordination via Agent Cards | inter-agency blackboard (hand-rolled A2A: collaboration-matrix + handoffs) |
| Subagents | Child agents, separate context windows | The Task/Agent tool |

Takeaway: I already run all five, mostly by hand. This research is about formalizing patterns already in use, not learning foreign territory.

## ☂️ 2. Context Engineering Is the Umbrella

Prompt engineering did not die; it grew into context engineering: designing the *entire* context window, not just the prompt (system prompt, instructions, user input, structured I/O, tools, RAG and memory, state and history). The Five Terms plus Skills plus MCP are all *instruments* of context engineering.

The unifying idea across every doc: **the context window is a scarce budget, and the whole game is getting the *right* context in and keeping the wrong context out.** That is precisely why progressive disclosure (skills) and tool search (MCP) exist.

Candid note: `context-engineering-guide.pdf` is broad and textbook-style, a decent checklist but thin on depth. The real substance is in the Skills and MCP docs.

## 🎓 3. Skills (The Deep One)

A Skill is a directory with `SKILL.md` (YAML frontmatter plus a markdown body) and optional scripts and resources. The core mechanic is **progressive disclosure, in three levels:**

1. **Metadata** (name and description): always loaded, roughly 100 tokens per skill. This is why many skills can be installed cheaply; the description is the trigger.
2. **Instructions** (the `SKILL.md` body): loaded only when triggered, under about 5k tokens.
3. **Resources and scripts:** zero tokens until accessed. Critically, a script's source never enters context; only its output does.

Levers worth knowing (Claude Code):

- Frontmatter: `description` / `when_to_use` (triggering), `disable-model-invocation` (manual-only, for side-effecting workflows like `/deploy`), `user-invocable`, `allowed-tools` / `disallowed-tools`, `paths` (glob-scoped auto-activation), `model` / `effort` overrides.
- **`context: fork` plus `agent:`** runs a skill *inside a subagent* with an isolated context.
- **Dynamic context injection:** `` !`cmd` `` runs a shell command *before* the skill loads and substitutes its output (for example, inject the live `git diff` into a commit-summary skill). This is the `get-current-date.sh` pattern, formalized.
- Precedence: Enterprise > Personal (`~/.claude/skills`) > Project (`.claude/skills`); plugin skills are namespaced.
- **Evals matter** (triggering is not the same as quality): the `skill-creator` plugin does baseline on-vs-off comparison, description tuning, and A/B between versions.
- Keep `SKILL.md` under about 500 lines; push detail into referenced files. A skill folder plus `plugin.json` becomes a full plugin (skills, agents, hooks, MCP, styles).

For me: this is the authoritative reference for what I already do a lot, and my prompt-authoring standards map straight onto skill descriptions and bodies. Two likely-underused power features: `context: fork` and dynamic injection.

## 🔌 4. MCP (The Access Layer)

MCP is an open standard connecting the agent to tools and data (Anthropic-born, now under the Linux Foundation). A server wraps an API in a standard interface; the agent speaks MCP and the server handles the POST/GET plus authentication.

- **Transports:** HTTP (remote, OAuth-capable, recommended), stdio (local process, filesystem and system access), WebSocket (push), SSE (deprecated).
- **Scopes:** local / project (`.mcp.json`, shareable, trust-gated) / user. Precedence: local > project > user > plugin > claude.ai connector.
- **Auth:** OAuth 2.0, static headers, or `headersHelper` for custom schemes (SSO, Kerberos, short-lived tokens).
- **Tool search (default on):** defers tool schemas until needed, so adding many servers costs little context; the server's `instructions` field (about 2 KB) becomes the discovery hook.
- **Channels:** servers can *push* events into a session (CI, alerts, chat), the reactive arm.
- claude.ai connectors flow into Claude Code; Gmail, Calendar, and M365 must be connected via claude.ai Settings then Connectors (redirect-URI constraint), which is my current setup.
- Claude Code can itself *be* an MCP server (`claude mcp serve`).

For me: I already *consume* MCP. The new lever is *building* one (the `mcp-server-dev` plugin scaffolds stdio or HTTP), for example an orchestrator/`ws` MCP so any agent queries the repo inventory or blackboard through a standard tool instead of raw file reads.

## ⚖️ 5. Skills vs MCP (The Crux)

The single cleanest line, straight from the "MCP vs Skills" doc:

> **MCP gives the agent access to *things*. Skills teach the agent *how* to do things.**

MCP retrieves the customer record from the CRM; a Skill says how the team wants it analyzed, formatted, validated, and presented. It is not either/or; it is **MCP plus Skills**: MCP supplies live data and actions, Skills supply the repeatable procedure and domain knowledge for using them correctly. A skill can even list an MCP tool in `allowed-tools`, so the skill *orchestrates* the MCP calls.

Rule of thumb: reach for a **skill** when you keep re-pasting the same *instructions or procedure*; reach for **MCP** when you keep pasting *data* from another system.

## 🧭 6. Where This Points (The Next Step)

"Continuing with context engineering" concretely means: the `CLAUDE.md` files plus skills plus connectors already *are* a context-engineering system. The moves are:

1. Formalize more repeated procedures into skills, with real descriptions and evals.
2. Exploit `context: fork` and dynamic injection.
3. Author an MCP server for my own infra so orchestrator and inter-agency become first-class *tools*, not just files.
4. Graduate the blackboard toward real A2A / Agent-Card semantics.

## 🔎 7. On penny and notebook

The five local docs were self-sufficient for absorption; penny (Perplexity) and notebook (NotebookLM) were not needed. Where they would earn their keep later: penny for *current* external state (newest Agentic AI Foundation standards, competing skill/MCP registries); notebook to fuse this plus the standards into a durable, queryable long-form corpus.

---

---

## 🔁 Round 2: The Harness Layer, CLI-vs-MCP, Frameworks, and the Core Repos

**Added 2026-07-17.** Source: six IBM Technology / Caleb-Writes-Code videos in `context-engineering/` (a2a-vs-mcp, agent-harness, agentic-ai-frameworks, cli-vs-mcp, mcp-vs-rag, what-is-an-api).

### 8. The Full Stack: Prompt < Context < Harness

The most important addition. Three nested engineering layers, each wrapping the last:

1. **Prompt engineering** (innermost): the persona and task. Still used, but now a small component (it "reminds the agent who it is").
2. **Context engineering**: managing the *window* (tool calling, MCP, RAG) to load the right context and drop the wrong. This is where the base research sat.
3. **Harness engineering** (outermost, coined early 2026): the *environment* that runs the agent in a **loop**, each iteration getting a **fresh, clean context** under strict start/finish rules. It does not replace the inner two; it leverages them.

Why it emerged: long tasks plus context summarization means the agent shrinks its own context and then "assumes the task is done," leaving work half-finished. The fix is not a bigger window; it is a loop: write a requirements doc (often JSON), then loop one task at a time, test and document each, fresh context per iteration, until done. (Reference architectures: "Ralph," Anthropic's harness demo, and now most coding agents build the harness layer in.)

### 9. Three Clean Decision Axes

**Access to *data*: RAG vs MCP.** RAG = *know more* (retrieve static/unstructured knowledge into context, ground answers, cite sources; steps: ask, retrieve, return, augment, generate). MCP = *do more* (connect to systems to act; steps: discover, understand, plan, execute, integrate). They combine (MCP can call RAG as a tool). Rule: retrieve knowledge with RAG, take actions with MCP.

**Access to *tools*: CLI vs MCP.** CLI = the agent runs terminal commands it already knows cold from training (`ls`, `grep`, `git`, `curl`): compact, composes with pipes, zero schema cost. MCP = structured tools with JSON schemas loaded up front (GitHub's MCP server ships 80 tools, roughly 55k tokens, even to use one). CLI wins when commands map to the job (file ops, git, text, scripts). MCP wins when there is a *gap* between the raw tool and what you need (rendering a JavaScript page, server-managed auth, org governance: per-user access, no shared creds, audit trails). Use both; the agent picks. Signal you picked wrong: it reverse-engineers a framework just to read a webpage.

**Communication: A2A vs MCP.** MCP = agent-to-tools/data (host + server + primitives: tools, resources, prompts; stdio local or HTTP remote; JSON-RPC). A2A = agent-to-agent (open, cross-vendor; each agent publishes an **Agent Card**, a capability "resume"; discover dynamically, delegate; HTTP + JSON-RPC 2.0; server-sent-event streaming for long jobs; modality-agnostic). They complement: A2A between agents, MCP between an agent and its tools.

**APIs underneath.** Every one of these sits on APIs: the standardized contract letting software talk. For AI, an API is both a "straw" (feed private data in) and a hand (act). Types: web/HTTP (open, partner, internal, composite), plus database and OS APIs; protocols REST, GraphQL, gRPC, SOAP, WebSocket. Constants: auth, encryption, rate limiting.

### 10. Frameworks: Pick by System Shape, Not Popularity

| System shape | When | Framework fit |
|---|---|---|
| Linear workflow | predictable, sequential, reliable | LangChain, LlamaIndex (data-heavy) |
| Autonomous multi-agent | open-ended goal, agents figure it out | AutoGen, CrewAI, BabyAGI |
| Role-based multi-agent | multiple agents, each a defined role | CrewAI, AutoGen + structure |
| Production orchestration | real-world, deep API/DB/workflow integration | LangGraph, Agent Framework |
| Rapid prototyping | validate an idea fast, drag-and-drop | LangFlow, Flowise |

### 11. Applied to the Three Core Repos

**Headline: inter-agency is already a hand-built version of most of this.** The other two are earlier on the curve.

- **inter-agency (already A2A + harness + context-chaining, by hand).**
  - Actor registry (wolfie, agy, claude, codex, cowork, ...) with roles = an A2A actor set; `cowork` is literally labelled "hybrid agent harness."
  - Blackboard (`state.json`) + handoff files (`to_[actor].md`: What Has Been Done / Next Actions / Checkpoints) + file-lock leases = file-based A2A coordination (the handoffs are hand-rolled Agent Cards + task messages).
  - `pending_approval` gate + watcher daemon = the harness loop's human-in-the-loop control.
  - The four-verb checklist (Write, Select, Compress, Isolate) in `context-and-chaining.md` = context engineering, already standardized.
  - `tools/` already holds a "local MCP server"; `adagio` runs `nomic-embed` for RAG vector DBs.
  - **Upgrade path:** formalize the file-handoffs toward real A2A semantics (Agent Cards, JSON-RPC, SSE streaming) and name the blackboard loop explicitly as the *harness* (requirements doc, one task per iteration, fresh context, test+document each). This is where the research pays off most.

- **infrastructure-consulting (context-eng + some MCP; skills-shaped).**
  - Runs on `.claude/CLAUDE.md` plus a large body of runbooks and procedures. `lab/ai-ops` already carries MCP servers (DuckDB, sqlite-vec) and a Pydantic-AI agent; the fleet is CLI-first (`ws`, shell wrappers).
  - **Move:** the many repeated procedures (lab runbooks, practice workflows, the standards themselves) are textbook **skills** (SKILL.md + optional scripts, on demand). CLI-vs-MCP validates staying CLI-first for git/file/shell; reserve MCP for gap cases (a repo-inventory / blackboard MCP so agents query structured state instead of reading files).

- **life-admin (CLI/Python only; keep it lean).**
  - Pure personal-ops: budget = CSV + Python (`analyze_budget.py`, `loan_payoff.py`), privacy-first (data gitignored, sanitization bar). No agents/skills/MCP, and the research says that is *correct* for a predictable, CLI-shaped domain.
  - **Move (light touch):** two candidate **skills** wrapping the existing scripts (a monthly budget-close skill; a loan-payoff skill), invoked on demand, so the recurring procedure is one command instead of re-explained monthly. MCP is justified here *only* if sensitive-data access ever needs governance (per-source access, audit); otherwise the CLI/Python path is the right, cheap answer. Multi-agent frameworks would be over-engineering.

### Cross-Repo Rule of Thumb

**Prompt** = who the agent is (CLAUDE.md persona), **context** = what it sees (four-verb chaining), **harness** = the loop that runs it (inter-agency's blackboard). Add **skills** where a procedure repeats, **CLI** where the model already knows the tool, **MCP** where there is a real gap or a governance need, **RAG** where it must *know* more, **A2A** where agents talk to agents. inter-agency is the mature node; infra is a skills-formalization opportunity; life-admin should stay deliberately lean.

---

## 📎 Appendix: Research Log

- **2026-07-17:** initial synthesis from the five base docs (sections 1 to 7).
- **2026-07-17:** round 2, six augmenting docs plus application to infra / life-admin / inter-agency (sections 8 to 11).
- _(next research appends here)_
