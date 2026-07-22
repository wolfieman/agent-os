"""Context-Assembly service: the Context Plane's frame store and core verbs.

The Context Plane assembles the Frame (the payload sent to the LLM) from
contributions supplied by the kernel services. This module exposes that
assembly surface as `ContextAssemblyService` and its four core verbs:
`write`, `select`, `compress`, and `isolate`.

Phase 0 scope: `write` is functional (task ce-008) so the service is genuinely
stateful and testable. `select`, `compress`, and `isolate` are **deterministic
Phase 0 mocks** (task ce-093): each returns a real, honest result computed by
lightweight fallback logic so the walking-skeleton validator (`examples/
log_look.py`) can run the full log-triage loop end-to-end without a
`NotImplementedError`. Every mock self-labels as a mock in its docstring — its
result stands in for the eventual backend (hybrid search, a summarization
model, and the tool sandbox respectively), it is not that backend.

`isolate` is the one verb whose result is a security claim, so its mock never
overstates it: `True` means "the whitelist was accepted and recorded as the
declared sandbox boundary", explicitly **not** "isolation is enforced". A jail
that actually confines execution awaits the real tool sandbox.

Copyright © 2026 Wolfgang Sanyer
Licensed under the Polyform Noncommercial License 1.0.0 (see LICENSE).
"""

from __future__ import annotations


class ContextAssemblyService:
    """Owns the active context frames and exposes the four core verbs.

    A frame is keyed by `context_id` and holds the ordered content written to
    it. The richer slotted Frame described in `docs/architecture/overview.md`
    (instructions, task_state, memory tiers, provenance) is deferred until the
    kernel services that populate those slots exist; a flat ordered list is the
    smallest store that supports `write` honestly today.
    """

    def __init__(self) -> None:
        self._frames: dict[str, list[str]] = {}
        # Declared sandbox boundaries recorded by `isolate`, keyed by
        # context_id. Phase 0 records the whitelist so the mock is genuinely
        # stateful; it does not yet enforce it (see the module docstring).
        self._sandboxes: dict[str, list[str]] = {}

    def write(
        self, context_id: str, content: str, provenance: dict | None = None
    ) -> bool:
        """Append content to the active frame, creating it if absent.

        Args:
            context_id: Identifier of the frame to write into
            content: The content to append
            provenance: Optional metadata tracking the source and lineage
                of the content (e.g., tool name, step ID, author)

        Returns:
            True if the content was stored, False if `content` was empty
            (an empty write is a caller error, not a reason to grow the frame)
        """
        if not content:
            return False

        # In Phase 0, we store a flat list of strings. Provenance tracking is
        # stubbed and will be fully integrated when the memory managers are added.
        self._frames.setdefault(context_id, []).append(content)
        return True

    def select(
        self,
        context_id: str,
        query: str,
        filters: dict | None = None,
        limit: int = 5,
    ) -> list:
        """Filter or search the frame for slices relevant to `query`.

        Args:
            context_id: Identifier of the frame to search
            query: The search expression
            filters: Optional metadata filters to constrain search scope
            limit: Maximum number of context slices to return

        Returns:
            The matching frame entries, oldest first, capped at `limit`.

        Phase 0 mock: a case-insensitive substring match over the frame's
        stored entries stands in for the hybrid vector + keyword search backed
        by the Memory Manager. `filters` is accepted for API stability but not
        yet applied. An empty `query` matches every entry; an unknown
        `context_id` yields an empty list (an empty frame, not an error).
        """
        entries = self._frames.get(context_id, [])
        if query:
            needle = query.lower()
            matches = [entry for entry in entries if needle in entry.lower()]
        else:
            matches = list(entries)
        if limit is not None and limit >= 0:
            matches = matches[:limit]
        return matches

    def compress(
        self,
        context_id: str,
        strategy: str = "summary",
        target_tokens: int | None = None,
    ) -> str:
        """Reduce the frame to fit the token budget.

        Args:
            context_id: Identifier of the frame to compress
            strategy: The compression strategy to apply
            target_tokens: Optional token limit to target

        Returns:
            The compressed frame content as a single newline-joined string.

        Phase 0 mock: line-based truncation stands in for the summarization
        model. Frame entries are kept in order while their running token
        estimate (whitespace-delimited words) stays within `target_tokens`;
        once the budget would be exceeded the remainder is dropped and a
        `"\\n[Mock Compression: Truncated to fit target_tokens]"` marker is
        appended so a caller can never mistake a truncated frame for a whole
        one. A `None` budget returns the full frame unchanged; `strategy` is
        accepted for API stability but line truncation is the only Phase 0
        strategy.
        """
        entries = self._frames.get(context_id, [])
        if target_tokens is None:
            return "\n".join(entries)

        kept: list[str] = []
        used = 0
        truncated = False
        for entry in entries:
            entry_tokens = len(entry.split())
            if used + entry_tokens > target_tokens:
                truncated = True
                break
            kept.append(entry)
            used += entry_tokens

        result = "\n".join(kept)
        if truncated:
            marker = "[Mock Compression: Truncated to fit target_tokens]"
            result = f"{result}\n{marker}" if result else marker
        return result

    def isolate(self, context_id: str, path_whitelist: list[str]) -> bool:
        """Record `path_whitelist` as the frame's declared sandbox boundary.

        Args:
            context_id: Identifier of the frame to constrain
            path_whitelist: Paths the sandbox may access

        Returns:
            True if the whitelist was accepted and recorded as the declared
            sandbox boundary; False if it was empty or malformed (a
            non-list, or containing a non-string / empty path), because there
            is then no boundary to record and so no success to report.

        Phase 0 mock: this verb's result is a security claim, so the mock is
        careful never to overstate it. `True` means only that a well-formed
        whitelist was accepted and stored as the *declared* boundary — it does
        **not** mean execution is confined to those paths. A jail that actually
        enforces the boundary awaits the real tool sandbox.
        """
        if not isinstance(path_whitelist, list) or not path_whitelist:
            return False
        if not all(isinstance(path, str) and path for path in path_whitelist):
            return False
        self._sandboxes[context_id] = list(path_whitelist)
        return True
