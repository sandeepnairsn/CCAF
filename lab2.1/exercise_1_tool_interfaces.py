"""
Exercise 1: Tool Interfaces (S1)
--------------------------------
Proves that tool-selection reliability is an interface problem, not a
model-size problem, by running the SAME model over a WEAK and a STRONG
toolset and measuring routing accuracy on six support questions.

Run:
    python exercise_1_tool_interfaces.py
"""

import os
import sys
from anthropic import Anthropic

MODEL = "claude-haiku-4-5-20251001"

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


# ---------------------------------------------------------------------------
# WEAK TOOLSET
# Vague names, overlapping descriptions, loose "q" parameter.
# ---------------------------------------------------------------------------
WEAK_TOOLS = [
    {
        "name": "search",
        "description": "Search for stuff in the system.",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {"type": "string"},
            },
            "required": ["q"],
        },
    },
    {
        "name": "lookup",
        "description": "Look something up.",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {"type": "string"},
            },
            "required": ["q"],
        },
    },
]


# ---------------------------------------------------------------------------
# STRONG TOOLSET
# Object + action names, explicit "when NOT to use" contrast, typed params.
# ---------------------------------------------------------------------------
STRONG_TOOLS = [
    {
        "name": "search_products",
        "description": (
            "Search the NorthPeak product CATALOG for items we sell (tents, "
            "sleeping bags, stoves, boots, etc.) by free-text query. Use this for "
            "availability, price, or whether a product exists. Do NOT use this to "
            "check something a customer already bought — for an existing purchase "
            "use get_order_status instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Free-text product query, e.g. '4 person tent'.",
                },
                "max_results": {"type": "integer", "minimum": 1, "maximum": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_order_status",
        "description": (
            "Retrieve the status of an EXISTING customer order by its order ID "
            "(shipping status, items, tracking). Use this whenever the customer "
            "gives an order number or references a purchase. Do NOT use this to "
            "browse the catalog — for products use search_products instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order ID in the format 'NP-XXXXXX'.",
                    "pattern": "^NP-[0-9]{6}$",
                },
            },
            "required": ["order_id"],
        },
    },
]


# ---------------------------------------------------------------------------
# TEST CASES
# Each maps a realistic support question to the tool that SHOULD be picked
# under a well-designed (strong) toolset.
# ---------------------------------------------------------------------------
TEST_CASES = [
    {
        "question": "Do you have any 4-person tents in stock?",
        "expected_strong": "search_products",
    },
    {
        "question": "Can you tell me the shipping status for order NP-104822?",
        "expected_strong": "get_order_status",
    },
    {
        "question": "What's the price of your 30-degree sleeping bag?",
        "expected_strong": "search_products",
    },
    {
        "question": "My order NP-559013 hasn't arrived yet, what's going on?",
        "expected_strong": "get_order_status",
    },
    {
        "question": "Do you sell waterproof hiking boots in size 10?",
        "expected_strong": "search_products",
    },
    {
        "question": "I need tracking info for NP-778341.",
        "expected_strong": "get_order_status",
    },
]

# For the weak toolset there's no principled way to know which of the two
# near-identical tools is "correct" from the interface alone -- that's the
# whole point of the exercise. We still score against the same expected
# tool concept (catalog lookup -> "search", order lookup -> "lookup") so we
# can print a comparable OK/MISS count, but expect this to be unreliable.
EXPECTED_WEAK_MAP = {
    "search_products": "search",
    "get_order_status": "lookup",
}


def run_case(tools, question):
    """Force a tool call (tool_choice=any) and return the tool name picked."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        tools=tools,
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": question}],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.name
    return None  # shouldn't happen with tool_choice=any


def score_toolset(name, tools, expected_key_fn):
    print(f"\n=== {name} toolset ===")
    correct = 0
    for i, case in enumerate(TEST_CASES, start=1):
        question = case["question"]
        expected = expected_key_fn(case)
        picked = run_case(tools, question)
        ok = picked == expected
        correct += int(ok)
        status = "OK  " if ok else "MISS"
        print(f"[{status}] Q{i}: {question}")
        print(f"        expected={expected!r} picked={picked!r}")
    print(f"--- {name} total: {correct}/{len(TEST_CASES)} ---")
    return correct


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: set ANTHROPIC_API_KEY in your environment first.", file=sys.stderr)
        sys.exit(1)

    weak_score = score_toolset(
        "WEAK",
        WEAK_TOOLS,
        expected_key_fn=lambda case: EXPECTED_WEAK_MAP[case["expected_strong"]],
    )
    strong_score = score_toolset(
        "STRONG",
        STRONG_TOOLS,
        expected_key_fn=lambda case: case["expected_strong"],
    )

    print("\n=== Summary ===")
    print(f"Weak toolset:   {weak_score}/{len(TEST_CASES)}")
    print(f"Strong toolset: {strong_score}/{len(TEST_CASES)}")


if __name__ == "__main__":
    main()
