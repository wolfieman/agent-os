"""Context-Assembly service: the Context Plane's frame store and core verbs.

The Context Plane assembles the Frame (the payload sent to the LLM) from
contributions supplied by the kernel services. This module exposes that
assembly surface as `ContextAssemblyService` and its four core verbs:
`write`, `select`, `compress`, and `isolate`.

Phase 0 scope (task ce-008): `write` is functional so the service is genuinely
stateful and testable; `select`, `compress`, and `isolate` are stubs that raise
`NotImplementedError` because each awaits infrastructure that does not exist
yet (hybrid search, a summarization model, and the tool sandbox respectively).
They raise rather than return empty results so a caller can never mistake an
unbuilt verb for a verb that found nothing.

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
            The matching context slices

        Raises:
            NotImplementedError: Always; awaits the hybrid vector + keyword
                search backed by the Memory Manager service
        """
        raise NotImplementedError("select awaits the hybrid search backend")

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
            The compressed frame content

        Raises:
            NotImplementedError: Always; awaits the summarization model and the
                token-accounting needed to target a budget
        """
        raise NotImplementedError("compress awaits the summarization backend")

    def isolate(self, context_id: str, path_whitelist: list[str]) -> bool:
        """Restrict the frame's execution sandbox to `path_whitelist`.

        Args:
            context_id: Identifier of the frame to constrain
            path_whitelist: Paths the sandbox may access

        Returns:
            True once the boundary is enforced

        Raises:
            NotImplementedError: Always; awaits the tool sandbox. This verb
                returns a security boundary, so it must never report success
                before one is actually enforced.
        """
        raise NotImplementedError("isolate awaits the tool sandbox")
