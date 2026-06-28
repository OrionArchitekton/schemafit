"""Lint rules reproduce the cited, real-world provider 400s."""

from __future__ import annotations

import pytest

from schemafit import has_errors, lint, lint_multi
from schemafit.linter import PROVIDERS


def _ids(findings):
    return {f.rule_id for f in findings}


# --- Anthropic: rejected validation keywords (vercel/ai#13355) -----------------

def test_anthropic_rejects_validation_keywords():
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string", "minLength": 1, "maxLength": 50, "pattern": "^x"},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0, "maximum": 120},
        },
        "required": ["name", "email", "age"],
    }
    findings = lint(schema, "anthropic")
    assert has_errors(findings)
    got = _ids(findings)
    for rid in (
        "anthropic-no-minLength",
        "anthropic-no-maxLength",
        "anthropic-no-pattern",
        "anthropic-no-format",
        "anthropic-no-minimum",
        "anthropic-no-maximum",
    ):
        assert rid in got, f"expected {rid} to fire"


def test_anthropic_pointer_is_precise():
    schema = {"type": "object", "properties": {"name": {"type": "string", "minLength": 1}}}
    findings = [f for f in lint(schema, "anthropic") if f.rule_id == "anthropic-no-minLength"]
    assert len(findings) == 1
    assert findings[0].json_pointer == "#/properties/name/minLength"


# --- OpenAI: strict structured-output constraints ------------------------------

def test_openai_requires_additional_properties_false():
    # claude-task-master#1522: additionalProperties is required to be false
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]}
    findings = lint(schema, "openai")
    assert "openai-additional-properties-false" in _ids(findings)
    assert has_errors(findings)


def test_openai_forbids_default():
    # openai-agents-python#474: default is not permitted within a property definition
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"a": {"type": "string", "default": "x"}},
        "required": ["a"],
    }
    assert "openai-no-default" in _ids(lint(schema, "openai"))


def test_openai_forbids_oneof_in_array_items_only():
    # openai-agents-python#474: oneOf not permitted within array items
    bad = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "xs": {"type": "array", "items": {"oneOf": [{"type": "string"}, {"type": "integer"}]}}
        },
        "required": ["xs"],
    }
    assert "openai-no-oneof-in-array-items" in _ids(lint(bad, "openai"))

    # oneOf NOT inside array items must not trip this rule
    ok_ctx = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"choice": {"oneOf": [{"type": "string"}, {"type": "integer"}]}},
        "required": ["choice"],
    }
    assert "openai-no-oneof-in-array-items" not in _ids(lint(ok_ctx, "openai"))


def test_openai_all_properties_required():
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
        "required": ["a"],
    }
    findings = [f for f in lint(schema, "openai") if f.rule_id == "openai-all-properties-required"]
    assert len(findings) == 1
    assert findings[0].keyword == "b"  # the missing one


# --- Gemini: unsupported constructs (python-genai#460) -------------------------

def test_gemini_anyof_is_version_sensitive_warning():
    # Current Gemini 2.5 (Jan 2026) supports anyOf, so it must NOT hard-fail CI;
    # it is a portability warning for older models/SDKs.
    schema = {
        "type": "object",
        "properties": {"status": {"anyOf": [{"type": "string"}, {"type": "null"}]}},
    }
    findings = lint(schema, "gemini")
    anyof = [f for f in findings if f.rule_id == "gemini-anyof-version-sensitive"]
    assert len(anyof) == 1
    assert anyof[0].severity == "warning"
    assert not has_errors(findings)


def test_gemini_open_dict_is_warning():
    schema = {"type": "object", "additionalProperties": {"type": "string"}}
    findings = lint(schema, "gemini")
    od = [f for f in findings if f.rule_id == "gemini-open-dict-version-sensitive"]
    assert len(od) == 1
    assert od[0].severity == "warning"
    assert not has_errors(findings)


def test_gemini_ref_is_warning_not_error():
    schema = {"type": "object", "properties": {"self": {"$ref": "#"}}}
    findings = [f for f in lint(schema, "gemini") if f.rule_id == "gemini-ref-recursion-risk"]
    assert len(findings) == 1
    assert findings[0].severity == "warning"
    # a warning alone does not fail CI
    assert not has_errors(findings)


# --- Clean schemas pass --------------------------------------------------------

def test_clean_schema_passes_all_providers():
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    }
    results = lint_multi(schema, list(PROVIDERS))
    for provider, findings in results.items():
        assert not has_errors(findings), f"{provider} unexpectedly failed: {findings}"


def test_unknown_provider_raises():
    # 'mistral'/'cohere' became valid in v0.3 — use a still-unknown provider.
    with pytest.raises(ValueError):
        lint({}, "bedrock")


def test_divergence_is_provider_specific():
    # One schema, different verdicts per provider — the whole point of the tool.
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "status": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        },
        "required": ["name", "status"],
    }
    results = lint_multi(schema, list(PROVIDERS))
    assert not has_errors(results["openai"])   # additionalProps+required ok; anyOf allowed
    assert has_errors(results["anthropic"])    # minLength rejected (hard 400 -> error)
    assert not has_errors(results["gemini"])   # anyOf is version-sensitive -> warning, not error
    assert any(f.rule_id == "gemini-anyof-version-sensitive" for f in results["gemini"])


def test_array_with_properties_not_treated_as_object():
    # Regression: a non-object schema carrying a stray 'properties' key must not
    # trigger OpenAI object rules (would be a false positive + bad repair).
    schema = {"type": "array", "items": {"type": "string"}, "properties": {"x": {"type": "string"}}}
    ids = _ids(lint(schema, "openai"))
    assert "openai-additional-properties-false" not in ids
    assert "openai-all-properties-required" not in ids


def test_forbidden_keyword_found_in_dependent_schemas():
    # Regression: forbidden keywords hidden in dependentSchemas must be caught
    # (false-negative = CI green then runtime 400).
    schema = {
        "type": "object",
        "dependentSchemas": {"a": {"properties": {"b": {"type": "string", "minLength": 3}}}},
    }
    assert "anthropic-no-minLength" in _ids(lint(schema, "anthropic"))


# --- v0.4 structural rules (Cohere TIGHT) exercised directly on dicts ----------

def test_root_must_be_object_cohere():
    # Root not object -> cohere-root-must-be-object
    bad = {"type": "array", "items": {"type": "string"}}
    got = _ids(lint(bad, "cohere"))
    assert "cohere-root-must-be-object" in got
    assert has_errors(lint(bad, "cohere"))

    # Implicit root object (only `properties`, no explicit `type: object`) is
    # rejected by Cohere at runtime, so it must also be flagged.
    implicit = {"properties": {"id": {"type": "string"}}, "required": ["id"]}
    assert "cohere-root-must-be-object" in _ids(lint(implicit, "cohere"))
    assert has_errors(lint(implicit, "cohere"))

    # Union/nullable root type (`["object", "null"]`) is not a literal
    # `type: object` and is likewise rejected.
    union = {"type": ["object", "null"], "properties": {"id": {"type": "string"}}}
    assert "cohere-root-must-be-object" in _ids(lint(union, "cohere"))
    assert has_errors(lint(union, "cohere"))


def test_object_min_one_required_cohere():
    # Object (root or nested) with properties but empty/missing required -> fires
    bad_root = {"type": "object", "properties": {"a": {"type": "string"}}}
    bad_nested = {
        "type": "object",
        "properties": {"top": {"type": "object", "properties": {"x": {"type": "string"}}}},
        "required": ["top"],
    }
    assert "cohere-object-min-required" in _ids(lint(bad_root, "cohere"))
    assert "cohere-object-min-required" in _ids(lint(bad_nested, "cohere"))


def test_structural_good_cohere_passes():
    good = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"id": {"type": "string"}},
        "required": ["id"],
    }
    assert not has_errors(lint(good, "cohere"))
