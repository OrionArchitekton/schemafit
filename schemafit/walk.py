"""Deterministic JSON-Schema traversal with JSON-Pointer tracking.

Yields every *object-form* subschema node, with a precise JSON Pointer and an
*edge context* (how this node relates to its parent, e.g. it is an array's
``items`` schema). The context describes only the immediate parent edge and is
intentionally NOT inherited, so a rule like "oneOf is forbidden inside array
items" matches the items schema itself and not arbitrarily deep descendants.

Boolean subschemas (the JSON-Schema ``true``/``false`` forms) are not yielded:
they carry no keywords for the rule engine to inspect. Provider rules that care
about the open-map form check the parent node's keyword value directly.
"""

from __future__ import annotations

from collections.abc import Iterator

# subschema maps: {name -> schema}
_CHILD_MAP_KEYS = ("properties", "patternProperties", "$defs", "definitions", "dependentSchemas")
# single subschema values
_CHILD_SCHEMA_KEYS = (
    "items",
    "additionalItems",
    "additionalProperties",
    "unevaluatedItems",
    "unevaluatedProperties",
    "contains",
    "contentSchema",
    "propertyNames",
    "not",
    "if",
    "then",
    "else",
)
# lists of subschemas
_CHILD_LIST_KEYS = ("allOf", "anyOf", "oneOf", "prefixItems")


def _escape(token: str) -> str:
    """Escape a JSON Pointer reference token (RFC 6901)."""
    return token.replace("~", "~0").replace("/", "~1")


def _unescape(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def walk(
    schema: object,
    pointer: str = "#",
    context: frozenset[str] = frozenset(),
) -> Iterator[tuple[str, dict, frozenset[str]]]:
    """Yield ``(json_pointer, node, edge_context)`` for every subschema dict."""
    if not isinstance(schema, dict):
        return
    yield pointer, schema, context

    for key in _CHILD_MAP_KEYS:
        sub = schema.get(key)
        if isinstance(sub, dict):
            child_ctx = frozenset({"property"}) if key == "properties" else frozenset()
            for name, child in sub.items():
                yield from walk(child, f"{pointer}/{key}/{_escape(str(name))}", child_ctx)

    for key in _CHILD_SCHEMA_KEYS:
        sub = schema.get(key)
        if isinstance(sub, dict):
            if key in ("items", "additionalItems", "unevaluatedItems"):
                child_ctx = frozenset({"array_items"})
            elif key in ("additionalProperties", "unevaluatedProperties"):
                child_ctx = frozenset({"additional_properties"})
            else:
                child_ctx = frozenset()
            yield from walk(sub, f"{pointer}/{key}", child_ctx)
        elif key == "items" and isinstance(sub, list):
            # tuple validation: items as an array of schemas
            for i, child in enumerate(sub):
                yield from walk(child, f"{pointer}/items/{i}", frozenset({"array_items"}))

    for key in _CHILD_LIST_KEYS:
        sub = schema.get(key)
        if isinstance(sub, list):
            for i, child in enumerate(sub):
                child_ctx = (
                    frozenset({"array_items"})
                    if key == "prefixItems"
                    else frozenset({f"{key}_member"})
                )
                yield from walk(child, f"{pointer}/{key}/{i}", child_ctx)

    # draft-07 "dependencies": map of name -> (schema | list[str]). Only dict
    # values are subschemas; array values are property-name lists, so skip them.
    deps = schema.get("dependencies")
    if isinstance(deps, dict):
        for name, child in deps.items():
            if isinstance(child, dict):
                yield from walk(child, f"{pointer}/dependencies/{_escape(str(name))}", frozenset())


def resolve_pointer(root: object, pointer: str) -> object | None:
    """Resolve a JSON Pointer (``#`` / ``#/a/b/0``) to its node, or None."""
    if pointer in ("#", ""):
        return root
    if not pointer.startswith("#/"):
        return None
    node: object = root
    for raw in pointer[2:].split("/"):
        token = _unescape(raw)
        if isinstance(node, list):
            try:
                node = node[int(token)]
            except (ValueError, IndexError):
                return None
        elif isinstance(node, dict):
            if token not in node:
                return None
            node = node[token]
        else:
            return None
    return node
