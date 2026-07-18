"""Persistent case facts that survive every turn of a long session."""


class CaseFacts:
    """A tiny key-value store of facts that must survive every turn."""

    def __init__(self):
        self._facts: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        """Pin a fact. Overwrites any earlier value for the same key."""
        self._facts[key] = value

    def get(self, key: str) -> str | None:
        """Read a pinned fact back (handy when experimenting in the REPL)."""
        return self._facts.get(key)

    def as_system_block(self) -> str:
        """
        Render the facts as a chunk of text appended to the system prompt
        every turn. Keep it short - every token here is paid for on every
        API call.
        """
        if not self._facts: 
            return "" 
        lines = ["[CASE FACTS - these are confirmed and must be preserved]"] 
        for k, v in self._facts.items(): 
            lines.append(f"- {k}: {v}") 
        return "\n".join(lines)
        # =================================================================
        # TODO (Demo 1 - Preservation): render the pinned facts.
        #
        #   1. If there are no facts (self._facts is empty), return "" so the
        #      system prompt stays small until you have something to pin.
        #   2. Otherwise build a short, labelled block, e.g.:
        #
        #         [CASE FACTS - these are confirmed and must be preserved]
        #         - customer_id: C-1001
        #         - tier: Gold
        #
        #      Start with the "[CASE FACTS ...]" header line, then one
        #      "- key: value" line per pinned fact, and join them with "\n".
        #
        # This block is what gets appended to the system prompt on EVERY
        # messages.create() call, so the model never loses these values.
        # =================================================================
        #raise NotImplementedError("Implement as_system_block() - see the TODO above.")
