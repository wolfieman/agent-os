# 🧩 ADR 0008: HOTL Oversight Model (Human-on-the-Loop, Risk-Tiered)

- **Status:** Proposed (cowork-drafted from the HOTL research confirmation, 2026-07-22; pending agy architectural ratification)
- **Date:** 2026-07-22
- **Authors:** cowork (research/synthesis)
- **Decides:** The human-oversight model for `agent-os`: autonomous by default, human *on* the loop (supervisory), escalating to a blocking gate only at defined risk tiers. Fixes the drift by which the OS docs inherited the ws/inter-agency harness's blanket HITL gate.

---

## 🧭 Context

The scarce resource an agent OS governs is not just the context window but *human attention*. An OS that puts a human in front of every action is not an autonomous agent OS; it is a slow harness. The research this repo is grounded in framed the OS accordingly, as a supervisor over autonomous agents, not an in-line approver of each step:

- `docs/research/sources/a2a/why-ai-agents-need-an-operating-system.md`: the OS exists to **supervise** autonomous agents and "keep things from going horribly wrong"; governance is the policy layer where "**some** actions require human approval," with the canonical risk-tiered example: an agent processes refunds under $50 automatically, and only over $50 does a human approve.
- `docs/research/sources/a2a/guide-to-architect-secure-ai-agents-best-practices-for-safety.md` (IBM + Anthropic): agents act "autonomously, without human intervention," and the human role is to "continuously observe the reasoning and govern for compliance" — **oversight** over autonomous operation, with least-privilege and sandboxing as the hard boundaries.
- `docs/research/context-engineering-report.md` already scoped the blocking gate to the harness, not the OS: "`pending_approval` gate + watcher daemon = **the harness loop's** human-in-the-loop control."

Despite that basis, the architecture docs adopted "HITL" for the OS layer, inherited wholesale from `inter-agency-patterns.md`, which promotes the inter-agency `pending_approval` blocking gate straight into the kernel. That flattened the intended risk-tiered oversight into a blanket gate. The label diverged from the design.

Two distinct models were being conflated:

- The **ws / inter-agency harness** is **HITL**. `pending_approval` and `ws sign-off` block *every* task. This is correct and intentional: it is wolfie's human-supervised dogfooding harness, and he wants to be in that loop.
- **agent-os** is **HOTL**. The OS runs agents autonomously and supervises them; a human is escalated to a blocking gate only at a risk threshold.

## ✅ Decision

1. **`agent-os` oversight is HOTL (human-on-the-loop).** Agents run autonomously by default. The OS supervises through Observability (traces of every decision) and Guardrails (input/output checks). The default path has no blocking human step.
2. **Escalation is risk-tiered.** A human is escalated to a *blocking* approval gate only when an action crosses a defined tier:
   - the privacy deny-list (`life-admin`, `credential-ops`, `email-ops`) — always;
   - destructive or irreversible operations;
   - spend or external-effect actions above a configured threshold (the ">$50" pattern).

   Everything below the tiers runs autonomously under observation, reviewable after the fact from the trace.
3. **This is distinct from, and does not inherit, the harness's HITL.** The ws/inter-agency `pending_approval` + sign-off gates remain HITL and unchanged; the OS does not adopt that blanket gate.
4. **Ownership within the kernel:** the **Guardrails/governance** service holds the risk-tier policy and decides when to escalate; the **Scheduler** surfaces the escalated gate; **Observability** records the autonomous decisions so oversight is real after the fact, not just at a gate.

## ⚖️ Consequences

- **Docs corrected:** OS-layer "HITL" references are reframed to HOTL / risk-tiered escalation (`services.md`, `layering.md`, `inter-agency-patterns.md`). References that genuinely describe the harness (`context-engineering-report.md`, the ws gate) stay HITL and are correct as-is.
- **The promoted gate is generalized:** in `inter-agency-patterns.md`, the kernel promotion of `pending_approval` changes from "a blanket HITL gate" to "a risk-tiered HOTL escalation," so the OS does not copy the harness's every-task blocking behavior.
- **Guardrails gains a risk-tier policy** as a first-class responsibility; the default is autonomous, gating is the exception.
- **Least-privilege and the privacy deny-list stay hard, code-level boundaries** (not merely policy), consistent with the secure-agents guide and the rollout plan's privacy deny-lists. HOTL loosens *routine* approval, never the hard safety boundaries.
- **Supersedes the ambient assumption** (from `inter-agency-patterns.md`) that the OS gate equals the harness gate. It does not.
