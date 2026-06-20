"""Repair must turn a failing schema into a passing one (reproduce -> fix)."""

from __future__ import annotations

from schemafit import has_errors, lint, repair


def test_repair_strips_anthropic_keywords_then_passes():
    # CORE FAILURE-MODE TEST: assert it fails first, then passes after repair.
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string", "minLength": 1, "maxLength": 50},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0, "maximum": 120},
        },
        "required": ["name", "email", "age"],
    }
    assert has_errors(lint(schema, "anthropic"))  # fires pre-fix

    fixed, rep = repair(schema, "anthropic")
    assert not has_errors(lint(fixed, "anthropic"))  # clean post-fix
    assert rep["auto_fixed"], "expected auto-fixes recorded"
    assert rep["lossy"], "dropping validation constraints is lossy and must be flagged"
    # original is untouched (deepcopy)
    assert "minLength" in schema["properties"]["name"]
    assert "minLength" not in fixed["properties"]["name"]


def test_repair_injects_additional_properties_false():
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]}
    assert has_errors(lint(schema, "openai"))
    fixed, _rep = repair(schema, "openai")
    assert fixed["additionalProperties"] is False
    assert not has_errors(lint(fixed, "openai"))


def test_repair_fills_required():
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
        "required": ["a"],
    }
    fixed, rep = repair(schema, "openai")
    assert set(fixed["required"]) == {"a", "b"}
    assert rep["lossy"], "making optional fields required is lossy and must be flagged"
    assert not has_errors(lint(fixed, "openai"))


def test_repair_flags_unfixable_as_manual():
    # OpenAI oneOf-inside-array-items (an error-severity rule) cannot be safely
    # auto-rewritten -> it must be surfaced as manual_required, not silently fixed.
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"xs": {"type": "array", "items": {"oneOf": [{"type": "string"}]}}},
        "required": ["xs"],
    }
    _fixed, rep = repair(schema, "openai")
    assert rep["manual_required"], "oneOf-in-array-items must be surfaced as manual"
