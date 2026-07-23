# 📌 Open Items

Running list of what is blocked on wolfie and forward interests not yet started for `agent-os`. Per-repo tracker (house pattern: `orchestrator/standards/docs-prose/README.md` section 5); cross-cutting items live in `../infrastructure-consulting/OPEN-ITEMS.md`.

**Last updated:** 2026-07-22

---

## 🙋 Blocked on Me

Waiting on wolfie's input or call.

_Nothing currently blocked._

---

## 🎯 Forward Interests

Captured but not started, grouped by area.

### 🔐 Security & Credentials

| Item | Why on the radar | Next step |
|---|---|---|
| 1. **Per-agent adagio API auth (reserve)** | The Ollama API rides shared tailnet-device identity: no per-agent credential and no per-call audit at the API layer. Accepted as-is under the ratified Tailscale-only posture (the tailnet is the boundary). Only a trigger changes that: adagio serves something sensitive, the tailnet grows past a single operator, or per-agent audit is wanted. | **Deferred, trigger-gated.** If a trigger fires, augment via Tailscale ACLs/tags (light, identity-aware, no token) or an Ollama auth-proxy checking a vault-backed token modeled on `lab-unlock` (heavy). The heavy path is gated on the KeePassXC vault rollout (tracked in `../infrastructure-consulting/OPEN-ITEMS.md`). |

---

## 🧾 Conventions for This File

- A row moves out when work starts: promoted to a task or its own doc, not left here as "done".
- Keep this file short. If it grows unwieldy, items are accumulating rather than resolving.
