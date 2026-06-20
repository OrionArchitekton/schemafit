"""Human, JSON, and SARIF reporters for lint results."""

from __future__ import annotations

import json

from . import __version__
from .model import Finding

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_VERSION = "2.1.0"
_INFO_URI = "https://github.com/OrionArchitekton/schemafit"


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


def _results_payload(
    results: dict[str, list[Finding]], live: dict[str, bool | None] | None = None
) -> dict:
    payload = {}
    for provider, findings in results.items():
        entry: dict = {
            "status": _status(findings),
            "findings": [f.to_dict() for f in findings],
        }
        if live is not None and provider in live:
            entry["confirmed_by_provider"] = live[provider]
        payload[provider] = entry
    return payload


def format_json(results: dict[str, list[Finding]]) -> str:
    return json.dumps(_results_payload(results), indent=2, sort_keys=True)


def format_json_multi(
    all_results: dict[str, dict[str, list[Finding]]],
    live: dict[str, dict[str, bool | None]] | None = None,
) -> str:
    payload = {
        path: _results_payload(results, (live or {}).get(path))
        for path, results in all_results.items()
    }
    return json.dumps(payload, indent=2, sort_keys=True)


# --- SARIF 2.1.0 (GitHub code-scanning native) ------------------------------


def _sarif_level(severity: str) -> str:
    """Map a finding severity to a SARIF result level."""
    return {"error": "error", "warning": "warning"}.get(severity, "note")


def _sarif_run(items: list[tuple[str, Finding]]) -> dict:
    """Build one SARIF run from ``(artifact_uri, finding)`` pairs."""
    rule_index: dict[str, int] = {}
    rules: list[dict] = []
    sarif_results: list[dict] = []

    for uri, f in items:
        if f.rule_id not in rule_index:
            rule_index[f.rule_id] = len(rules)
            rule_obj: dict = {
                "id": f.rule_id,
                "properties": {"provider": f.provider, "kind": f.kind},
            }
            if f.reason:
                rule_obj["shortDescription"] = {"text": f.reason}
            if f.doc_url:
                rule_obj["helpUri"] = f.doc_url
            rules.append(rule_obj)

        props: dict = {"provider": f.provider, "kind": f.kind, "keyword": f.keyword}
        if f.confirmed_by_provider is not None:
            props["confirmed_by_provider"] = f.confirmed_by_provider
        sarif_results.append(
            {
                "ruleId": f.rule_id,
                "ruleIndex": rule_index[f.rule_id],
                "level": _sarif_level(f.severity),
                "message": {"text": f.reason},
                "locations": [
                    {
                        "physicalLocation": {"artifactLocation": {"uri": uri}},
                        "logicalLocations": [{"fullyQualifiedName": f.json_pointer}],
                    }
                ],
                "properties": props,
            }
        )

    return {
        "tool": {
            "driver": {
                "name": "schemafit",
                "version": __version__,
                "informationUri": _INFO_URI,
                "rules": rules,
            }
        },
        "results": sarif_results,
    }


def _sarif_doc(items: list[tuple[str, Finding]]) -> dict:
    return {"$schema": SARIF_SCHEMA, "version": SARIF_VERSION, "runs": [_sarif_run(items)]}


def format_sarif(results: dict[str, list[Finding]], uri: str = "schema.json") -> str:
    """SARIF for a single schema's per-provider findings."""
    items = [(uri, f) for findings in results.values() for f in findings]
    return json.dumps(_sarif_doc(items), indent=2, sort_keys=True)


def format_sarif_multi(all_results: dict[str, dict[str, list[Finding]]]) -> str:
    """SARIF across multiple schema files (one run, file path per result)."""
    items: list[tuple[str, Finding]] = []
    for path, results in all_results.items():
        uri = "stdin" if path == "-" else path
        for findings in results.values():
            items.extend((uri, f) for f in findings)
    return json.dumps(_sarif_doc(items), indent=2, sort_keys=True)
