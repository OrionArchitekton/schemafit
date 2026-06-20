"""Best-effort, conservative auto-repair toward a provider-valid schema.

Repair is deliberately limited to transforms that are *safe* or whose lossiness
is reported. It never silently changes meaning without flagging it. Transforms
it cannot perform safely are returned as ``manual_required`` rather than guessed.
"""

from __future__ import annotations

import copy
from typing import Any

from .linter import lint
from .walk import resolve_pointer


def repair(schema: object, provider: str) -> tuple[Any, dict]:
    """Return ``(fixed_schema, report)``.

    report = {auto_fixed: [...], lossy: [...], manual_required: [...]}
    Each entry is a short ``"<rule_id> @ <pointer>"`` string.
    """
    fixed = copy.deepcopy(schema)
    report: dict[str, list[str]] = {"auto_fixed": [], "lossy": [], "manual_required": []}

    # Re-lint the working copy; apply fixes by each rule's declared strategy.
    for finding in lint(fixed, provider):
        if finding.severity != "error":
            continue  # warnings don't fail CI; leave them for the author
        node = resolve_pointer(fixed, finding.node_pointer)
        if not isinstance(node, dict):
            # The node was removed/overwritten by an earlier fix in this pass —
            # already handled; do not emit a dangling tag.
            continue
        tag = f"{finding.rule_id} @ {finding.json_pointer}"

        strategy = finding.auto_repair
        if strategy == "strip":
            # Dropping a validation constraint is provider-valid but lossy.
            if finding.keyword in node:
                del node[finding.keyword]
                report["auto_fixed"].append(tag)
                report["lossy"].append(tag)
        elif strategy == "set_false":
            # Overwriting a subschema (open-map) with False discards a constraint.
            if isinstance(node.get(finding.keyword), dict):
                report["lossy"].append(tag)
            node[finding.keyword] = False
            report["auto_fixed"].append(tag)
        elif strategy == "fill_required":
            props = node.get("properties")
            if isinstance(props, dict):
                node["required"] = sorted(set(node.get("required", []) or []) | set(props))
                report["auto_fixed"].append(tag)
                report["lossy"].append(tag)  # optional fields made required
            else:
                report["manual_required"].append(tag)
        else:
            # "manual": structural rewrites (anyOf/oneOf removal, dict->object)
            # are unsafe to guess — surface for a human.
            report["manual_required"].append(tag)

    return fixed, report
