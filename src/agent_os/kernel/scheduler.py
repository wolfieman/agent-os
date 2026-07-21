"""Scheduler service: the kernel's owner of the task blackboard.

The Scheduler manages task lifecycles — reading the active blackboard state,
assigning tasks to agents, and enforcing execution order and Human-in-the-Loop
gates. This module implements that surface as `Scheduler` and the four core
verbs from the kernel service spec (`docs/architecture/kernel/services.md`):
`get_task_state`, `claim_task`, `complete_task`, and `fail_task`.

Phase 0 scope (task ce-021): `get_task_state` is functional — reading the
blackboard is a pure read of `state.json` and needs no infrastructure that does
not exist yet, so the service is genuinely useful and testable (mirroring
`ContextAssemblyService.write`, task ce-008). The three mutating verbs are
stubs that raise `NotImplementedError`, because every one of them must acquire
a workspace lock lease before it may write the blackboard, and the Concurrency
Lock Manager they depend on (inter-agency-patterns.md §3) does not exist yet. A
naive read-modify-write would look safe while silently losing writes under
concurrency; raising is the honest behaviour until leases exist.

The blackboard schema is the inter-agency `state.json`: a top-level object with
a `tasks` list, each task a mapping with at least `id`, `status`, and
`assigned_to`.

Copyright © 2026 Wolfgang Sanyer
Licensed under the Polyform Noncommercial License 1.0.0 (see LICENSE).
"""

from __future__ import annotations

import json
from pathlib import Path


class Scheduler:
    """Reads the task blackboard and owns the task lifecycle verbs.

    The blackboard lives at `blackboard_path` (an inter-agency-style
    `state.json`). The reader loads it on demand so a caller always observes
    the current on-disk state rather than a snapshot cached at construction.
    """

    def __init__(self, blackboard_path: str | Path) -> None:
        self._blackboard_path = Path(blackboard_path)

    def _load_tasks(self) -> list[dict]:
        """Return the blackboard's task list, or an empty list if absent.

        A missing `tasks` key yields an empty list (an empty board, not an
        error). A malformed or unreadable file is a genuine fault and is
        allowed to raise.
        """
        with self._blackboard_path.open(encoding="utf-8") as handle:
            board = json.load(handle)
        tasks = board.get("tasks", [])
        return tasks if isinstance(tasks, list) else []

    def get_task_state(self, task_id: str) -> dict | None:
        """Return the blackboard record for `task_id`, or None if not present.

        Args:
            task_id: Identifier of the task to look up (e.g. `ce-021`).

        Returns:
            A fresh copy of the task's blackboard record, or None if no task
            with that id exists. A copy is returned so callers cannot mutate
            the on-disk state through the returned dict.
        """
        for task in self._load_tasks():
            if task.get("id") == task_id:
                return dict(task)
        return None

    def claim_task(self, task_id: str, actor_id: str) -> bool:
        """Assign `task_id` to `actor_id` and mark it in progress.

        Args:
            task_id: Identifier of the task to claim.
            actor_id: Identifier of the agent claiming the task.

        Returns:
            True once the claim is durably recorded.

        Raises:
            NotImplementedError: Always; claiming mutates the blackboard and so
                must hold a workspace lock lease, which awaits the Concurrency
                Lock Manager.
        """
        raise NotImplementedError("claim_task awaits the concurrency lock manager")

    def complete_task(self, task_id: str, actor_id: str) -> bool:
        """Mark `task_id` completed on behalf of `actor_id`.

        Args:
            task_id: Identifier of the task to complete.
            actor_id: Identifier of the agent completing the task.

        Returns:
            True once completion is durably recorded.

        Raises:
            NotImplementedError: Always; completion mutates the blackboard and
                releases the task's lock lease, which awaits the Concurrency
                Lock Manager.
        """
        raise NotImplementedError(
            "complete_task awaits the concurrency lock manager"
        )

    def fail_task(self, task_id: str, actor_id: str, error: str) -> bool:
        """Mark `task_id` failed on behalf of `actor_id`.

        Args:
            task_id: Identifier of the task to fail.
            actor_id: Identifier of the agent reporting the failure.
            error: Human-readable description of the terminal failure.

        Returns:
            True once the failure is durably recorded.

        Raises:
            NotImplementedError: Always; recording a failure mutates the
                blackboard and releases the task's lock lease, which awaits the
                Concurrency Lock Manager.
        """
        raise NotImplementedError("fail_task awaits the concurrency lock manager")
