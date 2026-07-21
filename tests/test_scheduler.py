"""Tests for the Scheduler blackboard reader (task ce-021).

Copyright © 2026 Wolfgang Sanyer
Licensed under the Polyform Noncommercial License 1.0.0 (see LICENSE).
"""

from __future__ import annotations

import json

import pytest

from agent_os.kernel.scheduler import Scheduler

_BOARD = {
    "workspace": "context-engineering",
    "tasks": [
        {"id": "ce-020", "status": "completed", "assigned_to": "codex"},
        {"id": "ce-021", "status": "in_progress", "assigned_to": "claude"},
    ],
}


def _write_board(tmp_path, board) -> str:
    path = tmp_path / "state.json"
    path.write_text(json.dumps(board), encoding="utf-8")
    return str(path)


def test_get_task_state_returns_matching_record(tmp_path) -> None:
    scheduler = Scheduler(_write_board(tmp_path, _BOARD))

    task = scheduler.get_task_state("ce-021")
    assert task is not None
    assert task["status"] == "in_progress"
    assert task["assigned_to"] == "claude"


def test_get_task_state_returns_none_for_unknown_task(tmp_path) -> None:
    scheduler = Scheduler(_write_board(tmp_path, _BOARD))

    assert scheduler.get_task_state("ce-999") is None


def test_get_task_state_returns_copy(tmp_path) -> None:
    scheduler = Scheduler(_write_board(tmp_path, _BOARD))

    task = scheduler.get_task_state("ce-021")
    task["status"] = "tampered"

    assert scheduler.get_task_state("ce-021")["status"] == "in_progress"


def test_get_task_state_reads_current_on_disk_state(tmp_path) -> None:
    path = _write_board(tmp_path, _BOARD)
    scheduler = Scheduler(path)

    # A write after construction is observed on the next read.
    updated = json.loads(json.dumps(_BOARD))
    updated["tasks"][1]["status"] = "completed"
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(updated, handle)

    assert scheduler.get_task_state("ce-021")["status"] == "completed"


def test_get_task_state_handles_missing_tasks_key(tmp_path) -> None:
    scheduler = Scheduler(_write_board(tmp_path, {"workspace": "x"}))

    assert scheduler.get_task_state("ce-021") is None


@pytest.mark.parametrize(
    ("verb", "args"),
    [
        ("claim_task", ("ce-021", "claude")),
        ("complete_task", ("ce-021", "claude")),
        ("fail_task", ("ce-021", "claude", "boom")),
    ],
)
def test_mutating_verbs_raise_until_lock_manager_exists(
    tmp_path, verb, args
) -> None:
    scheduler = Scheduler(_write_board(tmp_path, _BOARD))

    with pytest.raises(NotImplementedError, match="lock manager"):
        getattr(scheduler, verb)(*args)
