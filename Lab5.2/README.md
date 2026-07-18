# Lab 5.2 - Resilient Systems: Error Propagation & Large Codebase Exploration

CCA-F | Module 5 | Sections S3-S4

Build three resilience techniques into one healthcare-claims pipeline
(intake -> validation -> adjudication) so a long batch fails loudly, writes
everything to disk as it goes, and survives a crash without redoing finished
work. One `main.py` coordinator drives all three demos; each demo has one TODO.

## Setup

```bash
# 1. Python 3.10+ environment and dependencies
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                     # anthropic + python-dotenv

# 2. API key (loaded via python-dotenv)
cp .env.example .env            # then paste your key into .env

# 3. After completing the TODOs, run the pipeline
python main.py                  # run again to see crash-recovery skipping
```

## The three TODOs (one focal area per demo)

| Demo | Section | File | Your TODO |
|------|---------|------|-----------|
| 1 - Error Propagation | S3 | `agents.py` | Implement the three subagents (`run_intake`, `run_validation`, `run_adjudication`) - each returns a `StageResult` and never raises. The envelope is provided. |
| 2 - Scratchpad | S4 | `scratchpad.py` | Implement `log`, `mark_done`, `mark_failed`, `_flush` - every mutation flushes to disk. `__init__`/`status` provided. |
| 3 - Crash recovery | S4 | `main.py` | Complete `process_claim` (walk stages, log, mark terminal) and the skip rule (skip claims already `done`/`failed`). |

`sample_claims.py` (three mock claims + policy set) is provided as data.

## Notes

- **This lab makes real API calls** (the intake subagent). There is no offline
  mode. On the fresh starter, `python main.py` stops at the first unimplemented
  TODO with a clear message; the three demos are interleaved into one
  coordinator loop, so complete all three, then run.
- Scripts read the model from `MODEL_NAME` (default `claude-sonnet-4-5`) and the
  key from `ANTHROPIC_API_KEY`, both via `python-dotenv`.
- State lives in `scratchpad.json`. To reset, delete it by hand - the lab never
  deletes it from code (that's your manual reset switch).
- The mock claims are synthetic (no PHI).
