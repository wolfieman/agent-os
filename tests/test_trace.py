"""Tests for the Observability Service (task ce-021).

Copyright © 2026 Wolfgang Sanyer
Licensed under the Polyform Noncommercial License 1.0.0 (see LICENSE).
"""

from __future__ import annotations

import re

from agent_os.observability.trace import ObservabilityService

# ISO 8601 with a required numeric timezone offset (never bare UTC `Z`).
_OFFSET_TS = re.compile(r"T.*[+-]\d{2}:\d{2}$")


def test_log_trace_records_and_stamps_local_offset() -> None:
    service = ObservabilityService()

    assert service.log_trace({"agent": "claude", "step": "assemble"}) is True

    traces = service.get_traces()
    assert len(traces) == 1
    assert traces[0]["payload"] == {"agent": "claude", "step": "assemble"}
    assert _OFFSET_TS.search(traces[0]["recorded_at"])


def test_log_trace_rejects_empty_or_non_mapping() -> None:
    service = ObservabilityService()

    assert service.log_trace({}) is False
    assert service.log_trace("not a dict") is False  # type: ignore[arg-type]
    assert service.get_traces() == []


def test_log_trace_copies_payload_so_caller_mutation_does_not_leak() -> None:
    service = ObservabilityService()
    payload = {"agent": "claude"}

    service.log_trace(payload)
    payload["agent"] = "mutated"

    assert service.get_traces()[0]["payload"]["agent"] == "claude"


def test_get_traces_returns_copies() -> None:
    service = ObservabilityService()
    service.log_trace({"agent": "claude"})

    fetched = service.get_traces()
    fetched[0]["payload"]["agent"] = "tampered"

    assert service.get_traces()[0]["payload"]["agent"] == "claude"


def test_get_traces_filters_by_payload_keys() -> None:
    service = ObservabilityService()
    service.log_trace({"agent": "claude", "task": "ce-021"})
    service.log_trace({"agent": "codex", "task": "ce-021"})
    service.log_trace({"agent": "claude", "task": "ce-008"})

    claude_traces = service.get_traces({"agent": "claude"})
    assert len(claude_traces) == 2
    assert all(t["payload"]["agent"] == "claude" for t in claude_traces)

    both = service.get_traces({"agent": "claude", "task": "ce-021"})
    assert len(both) == 1


def test_get_traces_returns_chronological_order() -> None:
    service = ObservabilityService()
    for i in range(3):
        service.log_trace({"seq": i})

    assert [t["payload"]["seq"] for t in service.get_traces()] == [0, 1, 2]


def test_record_metric_stores_name_value_and_metadata() -> None:
    service = ObservabilityService()

    assert (
        service.record_metric("trace_duration_ms", 1234.5, {"agent": "claude"})
        is True
    )

    # Metrics are recorded independently of traces.
    assert service.get_traces() == []


def test_record_metric_rejects_empty_name() -> None:
    service = ObservabilityService()

    assert service.record_metric("", 1.0) is False


def test_record_metric_metadata_defaults_to_empty() -> None:
    service = ObservabilityService()

    assert service.record_metric("cost_usd", 0.01) is True
