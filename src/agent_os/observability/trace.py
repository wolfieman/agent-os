"""Observability service: the OS's "security camera" for agent execution.

The Observability Service records structured traces of every assembled Frame
and model response, tracks AgentOps performance metrics, and exposes both for
later diagnostic triage (the LogLook agent). This module implements that
surface as `ObservabilityService` and its three core verbs from the kernel
service spec (`docs/architecture/kernel/services.md`): `log_trace`,
`record_metric`, and `get_traces`.

Phase 0 scope (task ce-021): all three verbs are functional. Recording and
querying traces needs no infrastructure that does not exist yet — an in-memory
store is the smallest thing that makes the service genuinely stateful and
testable, mirroring `ContextAssemblyService.write` (task ce-008). Durable
storage (append-only `traces.jsonl`, a metrics database) is deferred; the
in-memory store is a faithful stand-in for that seam, not a stub.

Every trace and metric is stamped with a local-offset ISO 8601 timestamp
(never raw UTC `Z`), per the Timezone Offset Standard in
`docs/architecture/inter-agency-patterns.md`.

Copyright © 2026 Wolfgang Sanyer
Licensed under the Polyform Noncommercial License 1.0.0 (see LICENSE).
"""

from __future__ import annotations

import copy
from datetime import datetime


def _local_timestamp() -> str:
    """Return the current time as a local-offset ISO 8601 string.

    Uses the system's local timezone offset (e.g. `-04:00`) rather than raw
    UTC `Z`, so traces recorded across a timezone shift still order and
    correlate correctly (Timezone Offset Standard, inter-agency-patterns.md).
    """
    return datetime.now().astimezone().isoformat()


class ObservabilityService:
    """Records execution traces and metrics and answers queries over them.

    Traces and metrics are held in insertion order so `get_traces` can return
    them chronologically. The richer durable trace store described in
    `docs/architecture/kernel/services.md` (append-only log, cost accounting,
    handoff-latency rollups) is deferred; an in-memory list is the smallest
    store that supports honest recording and retrieval today.
    """

    def __init__(self) -> None:
        self._traces: list[dict] = []
        self._metrics: list[dict] = []

    def log_trace(self, trace: dict) -> bool:
        """Record a structured trace of an assembled Frame and model response.

        The caller's `trace` dict is stored as-is under a `payload` key so the
        recorded envelope (with its `recorded_at` timestamp) never mutates the
        caller's object. A local-offset timestamp is added if the caller did
        not supply one.

        Args:
            trace: The structured trace to record (e.g. frame contents, model
                response, tool calls, timings). Must be a non-empty mapping.

        Returns:
            True if the trace was recorded, False if `trace` was empty or not
            a mapping (an empty trace is a caller error, not a reason to grow
            the store).
        """
        if not isinstance(trace, dict) or not trace:
            return False

        self._traces.append(
            {
                "recorded_at": _local_timestamp(),
                "payload": copy.deepcopy(trace),
            }
        )
        return True

    def record_metric(
        self, metric_name: str, value: float, metadata: dict | None = None
    ) -> bool:
        """Record a named AgentOps performance metric.

        Args:
            metric_name: Identifier of the metric (e.g. `trace_duration_ms`,
                `handoff_latency_ms`, `cost_usd`). Must be non-empty.
            value: The numeric measurement.
            metadata: Optional dimensions for the measurement (e.g. agent id,
                tool name, task id).

        Returns:
            True if the metric was recorded, False if `metric_name` was empty.
        """
        if not metric_name:
            return False

        self._metrics.append(
            {
                "recorded_at": _local_timestamp(),
                "name": metric_name,
                "value": value,
                "metadata": dict(metadata) if metadata else {},
            }
        )
        return True

    def get_traces(self, filters: dict | None = None) -> list[dict]:
        """Return recorded traces in chronological order, optionally filtered.

        A trace matches when, for every key in `filters`, that key is present
        in the trace's `payload` and holds an equal value. An empty or absent
        `filters` returns every trace. Copies are returned so callers cannot
        mutate the internal store.

        Args:
            filters: Optional exact-match constraints applied to each trace's
                payload. All constraints must match (logical AND).

        Returns:
            The matching traces, each a fresh copy, oldest first.
        """
        if not filters:
            return [copy.deepcopy(trace) for trace in self._traces]

        matches = []
        for trace in self._traces:
            payload = trace["payload"]
            if all(payload.get(key) == want for key, want in filters.items()):
                matches.append(copy.deepcopy(trace))
        return matches
