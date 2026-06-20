"""Traversal + pointer resolution invariants."""

from __future__ import annotations

from schemafit.walk import resolve_pointer, walk


def test_walk_yields_root_and_nested():
    schema = {"type": "object", "properties": {"a": {"type": "string"}}}
    pointers = {ptr for ptr, _node, _ctx in walk(schema)}
    assert "#" in pointers
    assert "#/properties/a" in pointers


def test_array_items_context_is_not_inherited():
    schema = {
        "type": "object",
        "properties": {
            "xs": {
                "type": "array",
                "items": {"type": "object", "properties": {"y": {"type": "string"}}},
            }
        },
    }
    ctx_by_ptr = {ptr: ctx for ptr, _node, ctx in walk(schema)}
    assert "array_items" in ctx_by_ptr["#/properties/xs/items"]
    # a grandchild of items must NOT carry array_items (context describes the parent edge only)
    assert "array_items" not in ctx_by_ptr["#/properties/xs/items/properties/y"]


def test_pointer_escaping_roundtrip():
    schema = {"properties": {"a/b": {"type": "string"}, "c~d": {"type": "string"}}}
    pointers = {ptr for ptr, _n, _c in walk(schema)}
    assert "#/properties/a~1b" in pointers
    assert "#/properties/c~0d" in pointers
    assert resolve_pointer(schema, "#/properties/a~1b") == {"type": "string"}


def test_resolve_pointer_root_and_missing():
    schema = {"type": "object", "properties": {"a": {"type": "string"}}}
    assert resolve_pointer(schema, "#") is schema
    assert resolve_pointer(schema, "#/properties/a") == {"type": "string"}
    assert resolve_pointer(schema, "#/properties/missing") is None


def test_walk_handles_combinators_and_defs():
    schema = {
        "$defs": {"Name": {"type": "string", "minLength": 1}},
        "anyOf": [{"type": "string"}, {"type": "integer"}],
    }
    pointers = {ptr for ptr, _n, _c in walk(schema)}
    assert "#/$defs/Name" in pointers
    assert "#/anyOf/0" in pointers
    assert "#/anyOf/1" in pointers
