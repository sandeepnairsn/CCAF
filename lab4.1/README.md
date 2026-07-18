# Lab 4.1 - Precision Prompting: Explicit Criteria & Few-Shot Consistency

CCA-F | Module 4 | Sections S1-S2

Make a Trust & Safety triage classifier (REMOVE / REVIEW / ALLOW) precise using
prompting alone - no fine-tuning, no extra tooling. Three self-contained scripts,
each fills in one TODO and prints a before/after comparison.

## Setup

```bash
# 1. Create a Python 3.9+ environment and install the SDK
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                     # anthropic>=0.40.0

# 2. Add your API key
cp .env.example .env            # then paste your key into .env
export $(grep -v '^#' .env | xargs)

# 3. Confirm the first exercise runs
python exercise_1_explicit_criteria.py
```

## Exercises

| File | Section | Your TODO |
|------|---------|-----------|
| `exercise_1_explicit_criteria.py` | S1 | Fill in `EXPLICIT_PROMPT` with testable criteria; cut wrongful "remove" calls. |
| `exercise_2_few_shot.py` | S2 | Fill in `FEW_SHOT_EXAMPLES` (3 labeled examples) to lock the `ACTION | rationale` format. |
| `exercise_3_generalization.py` | S2 | Fill in the `PRINCIPLES` block so unseen, context-heavy cases route correctly. |

For each: open the file, complete the single TODO block, then run it and read the
before/after output. Everything else (test reports, scoring, parsing) is done for you.

## Notes

- Scripts read the model from `ANTHROPIC_MODEL` (default `claude-sonnet-4-6`) and
  the key from `ANTHROPIC_API_KEY`. Each run makes a handful of small API calls.
- Treat the moderation examples as professional triage - the reports are short,
  paraphrased descriptions.
- Keep outputs tight (one word, or `ACTION | rationale`) so scoring stays clean.
