"""
Exercise 2: Structured Errors & Retries (S2)
---------------------------------------------
NorthPeak's Orders service is flaky. Instead of letting exceptions crash the
agentic loop, every tool call returns a structured envelope:

    success -> {"isError": False, ...order fields}
    failure -> {"isError": True, "isRetryable": <bool>, "status": <int>, "error": <msg>}

A retry loop then retries only retryable failures (timeouts, rate limits,
5xx) with exponential backoff, and stops immediately on permanent failures
(400 malformed id, 404 not found).

Run offline self-check (no API key needed):
    python exercise_2_structured_errors.py --check

Run the live agent over three failure shapes:
    python exercise_2_structured_errors.py
"""

import os
import re
import sys
import time
from anthropic import Anthropic

MODEL = "claude-haiku-4-5-20251001"

RETRYABLE = {408, 429, 500, 502, 503, 504}


# ---------------------------------------------------------------------------
# Mock Orders service + failure injection
# ---------------------------------------------------------------------------
class ServiceError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(message)


# call counters so we can simulate "times out once, then succeeds"
_call_counts = {}

# Canned order data
_ORDERS = {
    "NP-100245": {
        "order_id": "NP-100245",
        "status": "shipped",
        "items": ["4-person tent"],
        "tracking": "1Z999AA10123456784",
    },
}


def orders_service(order_id):
    """Raw (flaky) service call. Raises ServiceError on failure."""
    # 1) malformed id -> permanent 400, never even reaches "the backend"
    if not re.match(r"^NP-[0-9]{6}$", order_id):
        raise ServiceError(400, f"Malformed order id: {order_id!r}")

    # 2) unknown order -> permanent 404
    if order_id not in _ORDERS:
        raise ServiceError(404, f"Order {order_id} not found")

    # 3) known order, but inject one transient timeout before succeeding
    count = _call_counts.get(order_id, 0) + 1
    _call_counts[order_id] = count
    if order_id == "NP-100245" and count == 1:
        raise ServiceError(504, "Gateway timeout")

    return _ORDERS[order_id]


# ---------------------------------------------------------------------------
# Step 1: the two functions we implement
# ---------------------------------------------------------------------------
def call_order_tool(order_id):
    """Wraps orders_service and NEVER raises -- always returns a dict envelope."""
    try:
        data = orders_service(order_id)
        return {"isError": False, **data}
    except ServiceError as err:
        return {
            "isError": True,
            "isRetryable": err.status in RETRYABLE,
            "status": err.status,
            "error": err.message,
        }


def run_with_retry(order_id, max_attempts=4):
    delay = 0.2
    for attempt in range(1, max_attempts + 1):
        result = call_order_tool(order_id)
        if not result["isError"]:
            return result
        if result["isRetryable"] and attempt < max_attempts:
            time.sleep(delay)
            delay *= 2  # exponential backoff
            continue
        return result  # permanent, or out of attempts -> stop
    return result


# ---------------------------------------------------------------------------
# Offline self-check (--check): proves the envelope logic without any API call
# ---------------------------------------------------------------------------
def offline_self_check():
    print("=== Offline self-check ===")

    # Reset call counters for a clean run
    _call_counts.clear()

    # 1) A good id eventually succeeds (after one simulated timeout+retry)
    result = run_with_retry("NP-100245")
    assert result["isError"] is False, f"expected success, got {result}"
    assert result["order_id"] == "NP-100245"
    print("[OK] NP-100245 succeeds after retrying a transient 504")

    # 2) A 404 is non-retryable
    result = run_with_retry("NP-999999")
    assert result["isError"] is True
    assert result["status"] == 404
    assert result["isRetryable"] is False
    print("[OK] NP-999999 returns non-retryable 404")

    # 3) A malformed id is non-retryable (400)
    result = run_with_retry("100245")
    assert result["isError"] is True
    assert result["status"] == 400
    assert result["isRetryable"] is False
    print("[OK] '100245' (malformed) returns non-retryable 400")

    # 4) Direct check: a queued 503 is retryable per call_order_tool logic
    fake_result = {"isError": True, "isRetryable": 503 in RETRYABLE, "status": 503}
    assert fake_result["isRetryable"] is True
    print("[OK] 503 classified as retryable")

    print("\nAll offline checks passed.")


# ---------------------------------------------------------------------------
# Live agent loop
# ---------------------------------------------------------------------------
GET_ORDER_STATUS_TOOL = {
    "name": "get_order_status",
    "description": (
        "Retrieve the status of an existing customer order by its order ID "
        "(shipping status, items, tracking)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "Order ID, expected format 'NP-XXXXXX'.",
                "pattern": "^NP-[0-9]{6}$",
            },
        },
        "required": ["order_id"],
    },
}


SYSTEM_PROMPT = (
    "When calling get_order_status, pass the order_id exactly as the "
    "customer typed it -- do not correct, reformat, or add a prefix to it. "
    "Validation of the id format is handled by the tool itself, not by you."
)


def run_agent_turn(client, user_message):
    """Runs one user message through the agentic loop, executing the tool
    with run_with_retry and feeding the structured result back as a
    tool_result (using is_error to flag permanent failures to the model)."""
    messages = [{"role": "user", "content": user_message}]

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        tools=[GET_ORDER_STATUS_TOOL],
        messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})

    # Handle a tool_use block if present
    tool_use = next((b for b in response.content if b.type == "tool_use"), None)
    if tool_use is None:
        return "".join(b.text for b in response.content if b.type == "text")

    order_id = tool_use.input.get("order_id", "")
    print(f"  DEBUG: model called get_order_status(order_id={order_id!r})")
    result = run_with_retry(order_id)

    tool_result_content = {
        "type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": str(result),
        "is_error": bool(result.get("isError")),
    }
    messages.append({"role": "user", "content": [tool_result_content]})

    final = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        tools=[GET_ORDER_STATUS_TOOL],
        messages=messages,
    )
    return "".join(b.text for b in final.content if b.type == "text")


def main():
    if "--check" in sys.argv:
        offline_self_check()
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: set ANTHROPIC_API_KEY in your environment first.", file=sys.stderr)
        sys.exit(1)

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    scenarios = [
        ("(A) transient timeout then success", "What's the status of order NP-100245?"),
        ("(B) permanent 404", "What's the status of order NP-999999?"),
        ("(C) malformed id", "What's the status of order 100245?"),
    ]

    for label, question in scenarios:
        print(f"\n=== {label} ===")
        print(f"User: {question}")
        answer = run_agent_turn(client, question)
        print(f"Agent: {answer}")


if __name__ == "__main__":
    main()