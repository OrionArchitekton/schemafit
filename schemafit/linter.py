"""The lint engine: apply a provider's declarative rule pack to a schema."""

from __future__ import annotations

import json
from importlib.resources import files

from .model import Finding
from .walk import walk

PROVIDERS: tuple[str, ...] = ("openai", "anthropic", "gemini", "mistral", "cohere")

_RULE_CACHE: dict[str, dict] = {}


def load_rule_pack(provider: str) -> dict:
    """Load a provider's JSON rule pack from packaged data (cached)."""
    if provider not in PROVIDERS:
        raise ValueError(f"unknown provider: {provider!r} (choose from {', '.join(PROVIDERS)})")
    if provider not in _RULE_CACHE:
        text = files("schemafit").joinpath("rules", f"{provider}.json").read_text(encoding="utf-8")
        _RULE_CACHE[provider] = json.loads(text)
    return _RULE_CACHE[provider]


def _is_object_schema(node: dict) -> bool:
    t = node.get("type")
    if t == "object":
        return True
    if isinstance(t, list) and "object" in t:
        return True
    # Untyped schema: a 'properties' key implies an object. But if an explicit
    # non-object type is declared, a stray 'properties' key does NOT make it one
    # (e.g. {"type": "array", "properties": {...}} is an array, not an object).
    if t is None:
        return "properties" in node
    return False


def _join(pointer: str, token: str) -> str:
    return f"{pointer}/{token}"


def apply_rule(
    rule: dict, provider: str, nodes: list[tuple[str, dict, frozenset[str]]]
) -> list[Finding]:
    """Apply one rule across every walked node, returning findings."""
    kind = rule["kind"]
    out: list[Finding] = []

    def mk(node_ptr: str, json_ptr: str, keyword: str) -> Finding:
        return Finding(
            provider=provider,
            rule_id=rule["id"],
            kind=kind,
            node_pointer=node_ptr,
            json_pointer=json_ptr,
            keyword=keyword,
            reason=rule.get("reason", ""),
            severity=rule.get("severity", "error"),
            doc_url=rule.get("doc_url", ""),
            auto_repair=rule.get("auto_repair", "manual"),
        )

    if kind == "forbidden_keyword":
        kw = rule["keyword"]
        for ptr, node, _ctx in nodes:
            if kw in node:
                out.append(mk(ptr, _join(ptr, kw), kw))

    elif kind == "forbidden_keyword_in_context":
        kw = rule["keyword"]
        need = rule["context"]
        for ptr, node, ctx in nodes:
            if need in ctx and kw in node:
                out.append(mk(ptr, _join(ptr, kw), kw))

    elif kind == "object_requires":
        kw = rule["keyword"]
        val = rule["value"]
        for ptr, node, _ctx in nodes:
            if _is_object_schema(node) and node.get(kw) != val:
                # If the keyword is absent, point at the offending object node
                # (a "<ptr>/<kw>" pointer would not resolve in the source).
                json_ptr = _join(ptr, kw) if kw in node else ptr
                out.append(mk(ptr, json_ptr, kw))

    elif kind == "object_all_properties_required":
        for ptr, node, _ctx in nodes:
            props = node.get("properties")
            if _is_object_schema(node) and isinstance(props, dict):
                required = set(node.get("required", []) or [])
                for name in props:
                    if name not in required:
                        # Point at the property that should be required (resolves).
                        out.append(mk(ptr, _join(_join(ptr, "properties"), name), name))

    elif kind == "forbidden_additional_properties_schema":
        for ptr, node, _ctx in nodes:
            if isinstance(node.get("additionalProperties"), dict):
                out.append(mk(ptr, _join(ptr, "additionalProperties"), "additionalProperties"))

    elif kind == "root_must_be_object":
        for ptr, node, _ctx in nodes:
            if ptr == "#" and not _is_object_schema(node):
                out.append(mk(ptr, ptr, "type"))

    elif kind == "object_min_one_required":
        for ptr, node, _ctx in nodes:
            if _is_object_schema(node):
                req = node.get("required")
                if not isinstance(req, list) or len(req) == 0:
                    json_ptr = _join(ptr, "required") if "required" in node else ptr
                    out.append(mk(ptr, json_ptr, "required"))

    else:  # defensive: unknown rule kind in a pack
        raise ValueError(f"unknown rule kind: {kind!r} (rule {rule.get('id')!r})")

    return out


def lint(schema: object, provider: str) -> list[Finding]:
    """Lint ``schema`` against one provider; return sorted findings."""
    pack = load_rule_pack(provider)
    nodes = list(walk(schema))
    findings: list[Finding] = []
    for rule in pack.get("rules", []):
        findings.extend(apply_rule(rule, provider, nodes))
    findings.sort(key=lambda f: (f.json_pointer, f.rule_id, f.keyword))
    return findings


def lint_multi(schema: object, providers: list[str]) -> dict[str, list[Finding]]:
    return {p: lint(schema, p) for p in providers}


def has_errors(findings: list[Finding]) -> bool:
    return any(f.severity == "error" for f in findings)
