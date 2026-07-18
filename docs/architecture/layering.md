# 🏗️ Agent OS Layering

This document outlines the vertical layering of Agent OS, mapping the data flow from the raw language models at the bottom to the active agent coordinators at the top.

---

## 📚 The Stack

```
+-----------------------------------------------------------+
|                      AGENTS / TEAMS                       |
|   (Policy: Role taxomony, LangGraph workflows, HITL)     |
+-----------------------------------------------------------+
                             | Syscalls / APIs
                             v
+-----------------------------------------------------------+
|                      KERNEL SERVICES                      |
| (Mechanisms: Scheduler, Memory, Tools, Identity, Obs)     |
+-----------------------------------------------------------+
                             | Feeds context contributions
                             v
+-----------------------------------------------------------+
|                       CONTEXT PLANE                       |
|   (Context-Assembly Service, Prompt Standards, Tracing)   |
+-----------------------------------------------------------+
                             | Formats Frame
                             v
+-----------------------------------------------------------+
|                        RAW MODELS                         |
|   (Ollama local models, adagio embeddings, cloud APIs)    |
+-----------------------------------------------------------+
```

---

## 🧊 1. Raw Models Layer (Bottom)

The foundation of the entire system is the raw language model (LLM). This layer is responsible for the raw text generation, function parsing, and embedding calculations.

- **Local Inference:** Optimized CPU/iGPU execution via Ollama (VM `adagio` running `qwen3:4b-instruct` or workstation `hope` running `qwen-ov`).
- **Embeddings:** Fast local vector calculations (using `nomic-embed-text` on `adagio`).
- **Cloud Models:** Larger hosted models (e.g., Claude 3.5 Sonnet, Claude 3 Opus) accessed via API when high-reasoning effort is required.

---

## 🧩 2. Context Plane Layer

The Context Plane is the interface directly wrapping the raw models. It handles the scarce token budget of the model's context window.

- **Context-Assembly Service:** Dynamically constructs the input payload (the **Frame**).
- **Prompt Library:** Manages reusable templates (AIM, BRIDGE, MAP) and applies prompt-authoring checklists to the instruction slot.
- **Observability Hook:** Emits structural JSONL traces of every assembled Frame before execution.
- **APIs Exposed:** `write()`, `select()`, `compress()`, `isolate()`.

---

## ⚙️ 3. Kernel Services Layer

The Kernel Services are modular subsystems that coordinate resources and safety. They communicate with the Context Plane using the **Syscall interface**.

- **Scheduler:** Manages task assignment, blackboard state updates, and locks.
- **Memory Manager:** Handles short-term conversation sliding-windows and retrieves long-term semantic knowledge via RAG.
- **Tool Manager:** Maintains the registry of available tools, manages their schemas, and loads them dynamically.
- **Identity Manager:** Provides unique non-human credentials and verifies agent scopes.
- **Guardrails:** Evaluates inputs for prompt injection and validates output formats (DLP, JSON structure validation).
- **Observability Service:** Records metrics (latency, cost, token efficiency) and parses trace files.

---

## 🤖 4. Agents / Teams Layer (Top)

The uppermost layer represents the application space. It defines the specific goals, agent roles, and collaboration logic.

- **Single Agents:** Bounded CLI tools running targeted scripts.
- **Agent Teams:** Orchestrated multi-agent topologies (e.g., supervisor managers, reviewer loops, state graphs).
- **HITL Integration:** Human-in-the-loop approval gates for high-stakes or destructive operations.
