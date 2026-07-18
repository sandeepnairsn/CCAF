# Lab 5.1 - Managing Context: Preservation, Optimization & Escalation

CCA-F | Module 5 | Sections S1-S2

Build three production context-management techniques into one e-commerce
support agent (Aarti Sharma, C-1001) so the same code works at turn 3 and turn
30. One `main.py` runs three labelled demos; each demo has exactly one TODO.

## Setup

```bash
# 1. Python 3.10+ environment and dependencies
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                     # anthropic + python-dotenv

# 2. API key (loaded via python-dotenv)
cp .env.example .env            # then paste your key into .env

# 3. After completing the three TODOs, run all three demos
python main.py
```

## The three TODOs (one per demo)

| Demo | Section | File | Your TODO |
|------|---------|------|-----------|
| 1 - Preservation | S1 | `case_facts.py` | Implement `as_system_block()` - render the pinned `[CASE FACTS]` block. |
| 2 - Optimization | S1 | `tool_optimizer.py` | Implement `optimize()` - trim tool output to the per-tool whitelist (`RELEVANT_FIELDS` is provided). |
| 3 - Escalation | S2 | `main.py` | Complete `SYSTEM_BASE` - the ASK-on-ambiguity rule (and the "[CASE FACTS] is authoritative" rule). |

Everything else is provided as working scaffolding: the chat loop and tool
dispatch (`main.py`), the mock data and lookups (`sample_data.py`), and the
`CaseFacts` store's `set`/`get` plus the `RELEVANT_FIELDS` whitelist.

## Notes

- **This lab makes real API calls** - there is no offline mode. On the fresh
  starter, `python main.py` stops at the first unfinished TODO with a clear
  message; complete all three and it runs Demo 1 -> 2 -> 3 in sequence.
- Scripts read the model from `MODEL_NAME` (default `claude-sonnet-4-6`) and the
  key from `ANTHROPIC_API_KEY`, both via `python-dotenv`.
- The mock data is one fictional customer with three orders - no real PII.
