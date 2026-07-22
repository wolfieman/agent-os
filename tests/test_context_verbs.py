"""Tests for the Context Plane Phase 0 mock verbs (task ce-093).

Covers the deterministic fallback logic of `select`, `compress`, and
`isolate` — the mocks that let `examples/log_look.py` run the log-triage loop
end-to-end before the real search / summarization / sandbox backends exist.

Copyright © 2026 Wolfgang Sanyer
Licensed under the Polyform Noncommercial License 1.0.0 (see LICENSE).
"""

from __future__ import annotations

from agent_os.kernel.context import ContextAssemblyService

_LOG = [
    "INFO  boot sequence complete",
    "WARNING disk usage at 82%",
    "ERROR failed to reach node-3",
    "CRITICAL replication halted",
    "INFO  retry scheduled",
]


def _frame_with_log() -> tuple[ContextAssemblyService, str]:
    service = ContextAssemblyService()
    context_id = "ce-002"
    for line in _LOG:
        service.write(context_id, line)
    return service, context_id


# --- select ---------------------------------------------------------------


def test_select_substring_match_is_case_insensitive() -> None:
    service, context_id = _frame_with_log()

    matches = service.select(context_id, "error")

    assert matches == ["ERROR failed to reach node-3"]


def test_select_preserves_insertion_order() -> None:
    service, context_id = _frame_with_log()

    matches = service.select(context_id, "INFO")

    assert matches == ["INFO  boot sequence complete", "INFO  retry scheduled"]


def test_select_honors_limit() -> None:
    service, context_id = _frame_with_log()

    assert service.select(context_id, "INFO", limit=1) == [
        "INFO  boot sequence complete"
    ]


def test_select_empty_query_returns_all_entries() -> None:
    service, context_id = _frame_with_log()

    assert service.select(context_id, "", limit=None) == _LOG


def test_select_unknown_context_returns_empty() -> None:
    service = ContextAssemblyService()

    assert service.select("nope", "ERROR") == []


# --- compress -------------------------------------------------------------


def test_compress_without_budget_returns_full_frame() -> None:
    service, context_id = _frame_with_log()

    assert service.compress(context_id) == "\n".join(_LOG)


def test_compress_truncates_and_marks_when_over_budget() -> None:
    service, context_id = _frame_with_log()

    # Lines 0 and 1 are 4 and 5 words; a 9-token budget fits exactly those
    # two (4 + 5 = 9) and truncates the rest.
    result = service.compress(context_id, target_tokens=9)

    lines = result.splitlines()
    assert lines[:2] == _LOG[:2]
    assert lines[-1] == "[Mock Compression: Truncated to fit target_tokens]"


def test_compress_generous_budget_keeps_everything_unmarked() -> None:
    service, context_id = _frame_with_log()

    result = service.compress(context_id, target_tokens=1000)

    assert result == "\n".join(_LOG)
    assert "Mock Compression" not in result


# --- isolate --------------------------------------------------------------


def test_isolate_records_wellformed_whitelist() -> None:
    service, context_id = _frame_with_log()

    assert service.isolate(context_id, ["/var/log", "/tmp"]) is True


def test_isolate_rejects_empty_whitelist() -> None:
    service, context_id = _frame_with_log()

    # An empty whitelist records no boundary, so there is no success to report.
    assert service.isolate(context_id, []) is False


def test_isolate_rejects_malformed_whitelist() -> None:
    service, context_id = _frame_with_log()

    assert service.isolate(context_id, ["/var/log", ""]) is False
    assert service.isolate(context_id, "not-a-list") is False  # type: ignore[arg-type]
