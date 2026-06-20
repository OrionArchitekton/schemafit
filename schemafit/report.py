"""Human and JSON reporters for lint results."""

from __future__ import annotations

import json

from .model import Finding


def _status(findings: list[Finding]) -> str:
    return "FAIL" if any(f.severity == "error" for f in findings) else "PASS"


def format_human(results: dict[str, list[Finding]]) -> str:
    lines: list[str] = []
    for provider, findings in results.items():
        errs = [f for f in findings if f.severity == "error"]
        warns = [f for f in findings if f.severity != "error"]
        lines.append(
            f"[{provider}] {_status(findings)} — {len(errs)} error(s), {len(warns)} warning(s)"
        )
        for f in findings:
            lines.append(f"  {f.severity.upper():<7} {f.json_pointer}  ({f.rule_id})")
            lines.append(f"          {f.reason}")
            if f.doc_url:
                lines.append(f"          ref: {f.doc_url}")
    if not lines:
        lines.append("(no providers selected)")
    return "\n".join(lines)


def _results_payload(results: dict[str, list[Finding]]) -> dict:
    return {
        provider: {
            "status": _status(findings),
            "findings": [f.to_dict() for f in findings],
        }
        for provider, findings in results.items()
    }


def format_json(results: dict[str, list[Finding]]) -> str:
    return json.dumps(_results_payload(results), indent=2, sort_keys=True)


def format_json_multi(all_results: dict[str, dict[str, list[Finding]]]) -> str:
    payload = {path: _results_payload(results) for path, results in all_results.items()}
    return json.dumps(payload, indent=2, sort_keys=True)
