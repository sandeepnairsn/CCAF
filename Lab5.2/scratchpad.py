"""
scratchpad.py - Disk-backed scratchpad for the claims pipeline.

WHY THIS EXISTS
---------------
Long-running multi-agent pipelines need to survive crashes. If the
adjudication subagent dies on claim #47 of 100, you don't want to
re-process 1..46 on restart.

The scratchpad does two jobs:
  1. It records EVERY finding (intake output, validation result, etc.)
     so a human can audit what happened.
  2. It marks each claim as `done`, `failed` or `in_progress`, so
     restarts can skip already-processed work.

Everything is persisted to a single JSON file. No DB needed for the lab.

YOUR TASK (Demo 2 - Context Management / scratchpad, S4): implement the four
mutating methods (log, mark_done, mark_failed, _flush). __init__ and status()
are provided. The contract that makes crash recovery work is: EVERY mutation
calls _flush() so the file on disk is always up to date.
"""

import json
from pathlib import Path


class Scratchpad:
    """A tiny JSON-on-disk store keyed by claim_id."""

    def __init__(self, path: str = "scratchpad.json"):
        self.path = Path(path)
        self._data: dict = {}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text())
            except json.JSONDecodeError:
                # Corrupted file - start fresh but don't delete it.
                # In real systems you would alert here.
                self._data = {}

    def status(self, claim_id: str) -> str:
        """Return 'new', 'in_progress', 'done', or 'failed'."""
        entry = self._data.get(claim_id)
        if not entry:
            return "new"
        return entry.get("status", "new")

    def log(self, claim_id: str, stage: str, payload) -> None:
        """Record what happened in a given stage for a given claim."""
        entry = self._data.setdefault(claim_id, {"status": "in_progress", "findings": []}) 
        entry["findings"].append({"stage": stage, "payload": payload}) 
        self._flush() 
    def _flush(self) -> None: 
        self.path.write_text(json.dumps(self._data, indent=2))
        # =================================================================
        # TODO (Demo 2): append a {stage, payload} record to this claim's
        # findings list, then flush.
        #   entry = self._data.setdefault(
        #       claim_id, {"status": "in_progress", "findings": []})
        #   entry["findings"].append({"stage": stage, "payload": payload})
        #   self._flush()
        # =================================================================
        #raise NotImplementedError("Implement log() - see the TODO above.")

    def mark_done(self, claim_id: str) -> None:
        self._data[claim_id]["status"] = "done" 
        self._flush()
        # =================================================================
        # TODO (Demo 2): set this claim's status to "done", then flush.
        #   self._data[claim_id]["status"] = "done"
        #   self._flush()
        # =================================================================
        #raise NotImplementedError("Implement mark_done() - see the TODO above.")

    def mark_failed(self, claim_id: str, reason: str) -> None:
        entry = self._data.setdefault(claim_id, {"findings": []}) 
        entry["status"] = "failed" 
        entry["failure_reason"] = reason 
        self._flush()
        # =================================================================
        # TODO (Demo 2): set status to "failed", record failure_reason, flush.
        #   entry = self._data.setdefault(claim_id, {"findings": []})
        #   entry["status"] = "failed"
        #   entry["failure_reason"] = reason
        #   self._flush()
        # =================================================================
        #raise NotImplementedError("Implement mark_failed() - see the TODO above.")

    def _flush(self) -> None:
        """Write to disk after every mutation. Cheap for small batches."""
        # =================================================================
        # TODO (Demo 2): persist the whole store to self.path as pretty JSON.
        #   self.path.write_text(json.dumps(self._data, indent=2))
        # This is the write-immediately contract that makes crash recovery work.
        # =================================================================
        raise NotImplementedError("Implement _flush() - see the TODO above.")
