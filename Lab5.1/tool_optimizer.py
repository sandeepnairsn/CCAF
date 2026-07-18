"""Shrink bulky tool outputs to a per-tool whitelist before they hit the model."""

# Fields we actually care about for each tool. Anything not in this list
# is dropped before the result reaches the model. (Provided for you - adding a
# new tool is just one more line here, not a new code path.)
RELEVANT_FIELDS = {
    "lookup_orders":     ["order_id", "status", "placed_on", "total"],
    "get_order_details": ["order_id", "status", "placed_on", "total", "items"],
}


def optimize(tool_name: str, raw_result):
    """
    Trim a tool's raw output down to just the fields that matter.

    Returns the trimmed result in the same shape (list or dict) it came in.
    Unknown tools pass through untouched (consider logging a warning in
    production so unconfigured tools don't sneak past).
    """
    # =====================================================================
    # TODO (Demo 2 - Optimization): trim raw_result to the whitelisted fields.
    #
    #   1. keep = RELEVANT_FIELDS.get(tool_name)
    #   2. if keep is None: return raw_result   (no rule for this tool -
    #      pass through untouched; in production you'd log a warning here)
    #   3. if raw_result is a list (many rows): return a new list where each
    #      row is trimmed to only the keys in `keep` that the row actually has:
    #          [{k: row[k] for k in keep if k in row} for row in raw_result]
    #   4. if raw_result is a dict (one record): trim it the same way.
    #   5. otherwise (not a list or dict): return raw_result unchanged.
    #
    # Keep the SAME shape it came in (list stays a list, dict stays a dict).
    # =====================================================================
    raise NotImplementedError("Implement optimize() - see the TODO above.")
