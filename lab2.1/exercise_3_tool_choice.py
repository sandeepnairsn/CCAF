"""
Exercise 3: Selection Control with tool_choice (S3)
-----------------------------------------------------
Every incoming support ticket must first be classified into exactly one
routing category, deterministically. This script runs four sample tickets
under three tool_choice settings -- auto, any, and FORCED -- to show that
only the forced mode reliably guarantees a clean classify_ticket call.

Run:
    python exercise_3_tool_choice.py
"""

import os
import sys
from anthropic import Anthropic

MODEL = "claude-haiku-4-5-20251001"

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
CLASSIFY_TOOL = {
    "name": "classify_ticket",
    "description": "Classify a support ticket into exactly one routing category.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["order_issue", "product_question", "return_request", "other"],
            },
            "reason": {"type": "string"},
        },
        "required": ["category", "reason"],
    },
}

DRAFT_REPLY_TOOL = {
    "name": "draft_customer_reply",
    "description": "Draft a plain-text reply to send to the customer.",
    "input_schema": {
        "type": "object",
        "properties": {
            "reply": {"type": "string", "description": "The drafted reply text."},
        },
        "required": ["reply"],
    },
}

TOOLS = [CLASSIFY_TOOL, DRAFT_REPLY_TOOL]


# ---------------------------------------------------------------------------
# tool_choice modes -- the three values we fill in
# ---------------------------------------------------------------------------
modes = {
    "auto": {"type": "auto"},
    "any": {"type": "any"},
    "FORCED": {"type": "tool", "name": "classify_ticket"},
}


# ---------------------------------------------------------------------------
# Sample tickets
# ---------------------------------------------------------------------------
TICKETS = [
    "My order NP-104822 was supposed to arrive three days ago and it's still not here.",
    "Does the 65L backpack come in a women's fit?",
    "I'd like to return the sleeping bag I bought, it's too small for me.",
    "Hey, just wanted to say your customer service team was awesome yesterday!",
]


def run_ticket(tool_choice, ticket_text):
    """Sends one ticket under the given tool_choice and reports what happened."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        tools=TOOLS,
        tool_choice=tool_choice,
        messages=[{"role": "user", "content": ticket_text}],
    )

    tool_use = next((b for b in response.content if b.type == "tool_use"), None)
    text = "".join(b.text for b in response.content if b.type == "text")

    if tool_use is None:
        return f"NO TOOL CALL (plain text): {text!r}"
    if tool_use.name == "classify_ticket":
        return f"classify_ticket -> category={tool_use.input.get('category')!r}"
    return f"WRONG TOOL: {tool_use.name} called instead of classify_ticket"


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: set ANTHROPIC_API_KEY in your environment first.", file=sys.stderr)
        sys.exit(1)

    for mode_name, tool_choice in modes.items():
        print(f"\n=== tool_choice = {mode_name} ({tool_choice}) ===")
        classified = 0
        for i, ticket in enumerate(TICKETS, start=1):
            outcome = run_ticket(tool_choice, ticket)
            if outcome.startswith("classify_ticket"):
                classified += 1
            print(f"Ticket {i}: {ticket}")
            print(f"  -> {outcome}")
        print(f"--- {mode_name}: {classified}/{len(TICKETS)} tickets classified ---")


if __name__ == "__main__":
    main()
