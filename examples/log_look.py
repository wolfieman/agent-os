"""LogLook walking-skeleton validator: an end-to-end Context Plane triage loop.

This is the Phase 0 diagnostic-triage script (task ce-093). It drives the three
built kernel/observability surfaces through one complete log-triage cycle so we
can prove the walking skeleton runs end-to-end:

    Scheduler.get_task_state  -> read the active task off a mock blackboard
    ContextAssemblyService    -> write log lines, then select / isolate /
                                 compress them (the Phase 0 mock verbs)
    ObservabilityService      -> log the assembled trace and record metrics

The "model call" is simulated: no LLM is invoked. A deterministic summary is
synthesized from the triaged alerts so the loop is reproducible and offline.
The run writes its recorded traces to `examples/logs/trace.jsonl` and exits 0.

Copyright © 2026 Wolfgang Sanyer
Licensed under the Polyform Noncommercial License 1.0.0 (see LICENSE).
"""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from agent_os.kernel.context import ContextAssemblyService
from agent_os.kernel.scheduler import Scheduler
from agent_os.observability.trace import ObservabilityService

_TASK_ID = "ce-002"
_OUTPUT_DIR = Path(__file__).resolve().parent / "logs"
_TARGET_TOKENS = 24

# A mock system log with a mix of severities; the ERROR/CRITICAL lines are the
# ones triage must surface.
_SAMPLE_LOG = [
    "INFO  boot sequence complete",
    "INFO  scheduler claimed task ce-002",
    "WARNING disk usage at 82% on /var/log",
    "ERROR failed to reach node-3 after 3 retries",
    "WARNING handoff latency 4200ms exceeds 3000ms budget",
    "CRITICAL replication halted: quorum lost",
    "INFO  retry scheduled in 30s",
]


def _mock_blackboard(state_dir: Path) -> str:
    """Write a mock `state.json` holding the active task and return its path."""
    board = {
        "workspace": "context-engineering",
        "tasks": [
            {
                "id": _TASK_ID,
                "description": "Log Triage Analysis",
                "status": "in_progress",
                "assigned_to": "loglook",
            }
        ],
    }
    path = state_dir / "state.json"
    path.write_text(json.dumps(board), encoding="utf-8")
    return str(path)


def _simulate_model_response(task: dict, alerts: list[str]) -> str:
    """Synthesize a deterministic triage summary (stands in for an LLM call)."""
    errors = sum(1 for line in alerts if "ERROR" in line)
    criticals = sum(1 for line in alerts if "CRITICAL" in line)
    return (
        f"Triage summary for {task['id']} ({task['description']}): "
        f"{len(alerts)} alert line(s) — {errors} ERROR, {criticals} CRITICAL. "
        "Recommend investigating node-3 reachability and the replication halt."
    )


def run() -> Path:
    """Run the full triage loop and return the path of the written trace file."""
    started = time.perf_counter()

    context = ContextAssemblyService()
    observability = ObservabilityService()

    # 1. Read the active task off a mock blackboard via the Scheduler.
    with tempfile.TemporaryDirectory() as state_dir:
        scheduler = Scheduler(_mock_blackboard(Path(state_dir)))
        task = scheduler.get_task_state(_TASK_ID)
    if task is None:
        raise RuntimeError(f"mock blackboard is missing task {_TASK_ID}")

    # 2. Frame assembly: write each log line as its own frame entry so `select`
    #    can return individual lines and `compress` has line granularity.
    for line in _SAMPLE_LOG:
        context.write(_TASK_ID, line)

    # 3. Context verbs: select the alert lines, record the sandbox boundary,
    #    then move the alerts into their own frame and compress to budget.
    alerts: list[str] = []
    for keyword in ("ERROR", "CRITICAL"):
        for line in context.select(_TASK_ID, keyword, limit=None):
            if line not in alerts:
                alerts.append(line)

    isolated = context.isolate(_TASK_ID, [str(_OUTPUT_DIR), "/var/log"])

    alert_frame = f"{_TASK_ID}:alerts"
    for line in alerts:
        context.write(alert_frame, line)
    compressed = context.compress(alert_frame, target_tokens=_TARGET_TOKENS)

    # 4. Simulate the model call over the assembled frame.
    prompt = (
        f"Task {task['id']}: {task['description']}\n"
        f"Triage the following alert lines:\n{compressed}"
    )
    response = _simulate_model_response(task, alerts)

    elapsed_ms = (time.perf_counter() - started) * 1000

    # 5. Observability: record the assembled trace and the run metrics.
    observability.log_trace(
        {
            "task_id": task["id"],
            "agent": "loglook",
            "prompt": prompt,
            "response": response,
            "alert_count": len(alerts),
            "sandbox_recorded": isolated,
        }
    )
    observability.record_metric(
        "prompt_tokens", float(len(prompt.split())), {"task_id": task["id"]}
    )
    observability.record_metric(
        "alert_lines", float(len(alerts)), {"task_id": task["id"]}
    )
    observability.record_metric(
        "trace_duration_ms", elapsed_ms, {"task_id": task["id"]}
    )

    # 6. Persist the recorded traces (the service is in-memory; the script owns
    #    durability). One JSON object per line.
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    trace_path = _OUTPUT_DIR / "trace.jsonl"
    with trace_path.open("w", encoding="utf-8") as handle:
        for trace in observability.get_traces():
            handle.write(json.dumps(trace) + "\n")

    return trace_path


def main() -> None:
    trace_path = run()
    print(f"LogLook triage complete. Trace written to {trace_path}")


if __name__ == "__main__":
    main()
