# CCA-F Module 2, Lab 2.1 — Designing Reliable Tools: Interfaces, Errors & Selection Control

This lab works through three self-contained exercises on making tool use reliable in agentic systems: tool **interface design**, **structured error handling with retries**, and **selection control via `tool_choice`**.

All exercises target `claude-haiku-4-5-20251001` via the Anthropic Messages API.

## Setup

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
```

---

## File Inventory

| File | Exercise | Purpose |
|---|---|---|
| `exercise_1_tool_interfaces.py` | Ex 1 | Weak vs. strong toolset + scoring harness over six support questions. |
| `exercise_2_structured_errors.py` | Ex 2 | `isError` / `isRetryable` envelope, retry-with-backoff loop, agentic loop over a flaky Orders service. `--check` runs offline. |
| `exercise_3_tool_choice.py` | Ex 3 | `classify_ticket` + `draft_customer_reply` run under `auto` / `any` / `FORCED` `tool_choice`. |
| `solutions/` | all | Finished reference versions of all three exercise files. |

---

## Exercise 1: Tool Interfaces (S1)

**Question:** Is tool-selection reliability a model-size problem, or an interface problem?

Runs the same model over a `WEAK_TOOLS` set (vague names like `search`/`lookup`, overlapping descriptions, a loose `q` parameter) and a `STRONG_TOOLS` set (`search_products` / `get_order_status`, each with an explicit "do NOT use this for X, use the other tool instead" contrast, and a regex-typed `order_id`). Six support questions are routed against both sets using `tool_choice={"type": "any"}`, forcing a tool call so the harness measures *which* tool gets picked, not *whether* one does.

**Run:**
```bash
python exercise_1_tool_interfaces.py
```

**Result observed:** the strong toolset routed noticeably more reliably than the weak one on the same six questions with the same model — confirming that selection reliability comes from the interface (names, descriptions, schemas), not model capability.

---

## Exercise 2: Structured Errors & Retries (S2)

**Question:** How should a tool behave when the backend it wraps is flaky?

`call_order_tool` never raises — it always returns a structured envelope (`{"isError": False, ...}` on success, `{"isError": True, "isRetryable": bool, "status": int, "error": str}` on failure). `run_with_retry` retries only when `isRetryable` is `True`, using exponential backoff (0.2s → 0.4s → 0.8s) capped at 4 attempts.

**Offline self-check (no API key required):**
```bash
python exercise_2_structured_errors.py --check
```
Confirms: a good id succeeds (after one simulated transient 504), a 404 is non-retryable, a malformed id is a non-retryable 400, and a 503 is classified as retryable.

**Live run (three failure shapes):**
```bash
python exercise_2_structured_errors.py
```
- **(A)** `NP-100245` times out once (504) → loop retries → succeeds on attempt 2, agent answers normally.
- **(B)** `NP-999999` → 404, no retry, agent reports the order wasn't found.
- **(C)** `100245` (malformed) → 400, no retry, agent asks for a correctly formatted id.

**Note on (C):** getting a clean 400 here depends on the model passing the id through to the tool *exactly* as the customer typed it, rather than "helpfully" normalizing it (e.g. `100245` → `NP-100245`) before calling the tool. This version adds a system prompt instructing the model not to reformat the id, plus a debug print showing exactly what value was sent to `get_order_status`, and a `pattern` constraint on the schema for extra rigor at the interface level. Model behavior on this kind of edge case isn't 100% guaranteed deterministic even with these mitigations — check the debug line if scenario (C) doesn't produce a 400 on a given run.

---

## Exercise 3: Selection Control with `tool_choice` (S3)

**Question:** How do you guarantee a deterministic tool call for a routing/triage step?

Four sample tickets are run under three `tool_choice` settings against a two-tool set (`classify_ticket`, `draft_customer_reply`):

| Mode | Constraint |
|---|---|
| `auto` | May answer in plain text, pick any tool, or pick none. |
| `any` | Must call *some* tool — but may pick the wrong one. |
| `FORCED` (`{"type": "tool", "name": "classify_ticket"}`) | Must call exactly `classify_ticket`. |

**Run:**
```bash
python exercise_3_tool_choice.py
```

**Results observed:**
- `auto`: inconsistent — at least one ticket (typically the compliment, "your team was awesome!") produced no tool call at all, since there's nothing to classify.
- `any`: a tool was always called, but not always the right one — e.g. a direct product question ("Does the backpack come in a women's fit?") got routed to `draft_customer_reply` instead of `classify_ticket`, since the model reasoned the helpful action was to answer rather than triage. Total: 2/4 classified correctly on this run.
- `FORCED`: 4/4 — every ticket returned a clean `classify_ticket` call with a category, regardless of ambiguity.

**Takeaway:** only `FORCED` is reliable enough for a routing pipeline to depend on. `any`'s wrong-tool failures are worse than `auto`'s no-tool failures for a triage step, because a pipeline expecting a `category` field would either crash or silently mis-route the ticket rather than failing loudly.

---

## Reflection Questions

The reflection questions at the end of each exercise (in the lab handout) are intentionally left for independent write-up rather than answered here — they're where the graded learning is meant to land.
