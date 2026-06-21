"""v0.3 provider rule packs: Cohere (rich, primary-sourced) + Mistral (thin)."""

from __future__ import annotations

from pathlib import Path

from schemafit import has_errors, lint, lint_multi
from schemafit.cli import main
from schemafit.linter import PROVIDERS

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _ids(findings):
    return {f.rule_id for f in findings}


# --- Cohere: unsupported structured-output keywords (docs.cohere.com) ----------

def test_cohere_rejects_unsupported_keywords():
    # docs.cohere.com/docs/structured-outputs "Unsupported schema features":
    # Schema Composition (allOf/oneOf/not), Numeric Ranges (minimum/maximum),
    # Array Length Ranges (minItems/maxItems), String Length (minLength/maxLength).
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "a": {"allOf": [{"type": "integer"}]},
            "b": {"oneOf": [{"type": "string"}]},
            "c": {"not": {"type": "null"}},
            "n": {"type": "integer", "minimum": 0, "maximum": 9},
            "xs": {"type": "array", "minItems": 1, "maxItems": 3, "uniqueItems": True},
            "s": {"type": "string", "minLength": 1, "maxLength": 5},
        },
        "required": ["a", "b", "c", "n", "xs", "s"],
    }
    findings = lint(schema, "cohere")
    assert has_errors(findings)
    got = _ids(findings)
    for rid in (
        "cohere-no-allOf",
        "cohere-no-oneOf",
        "cohere-no-not",
        "cohere-no-minimum",
        "cohere-no-maximum",
        "cohere-no-minItems",
        "cohere-no-maxItems",
        "cohere-no-minLength",
        "cohere-no-maxLength",
        "cohere-no-uniqueItems",
    ):
        assert rid in got, f"expected {rid} to fire"


def test_cohere_does_not_flag_supported_keywords():
    # W2 false-positive guard: anyOf, $ref, enum, const, pattern are SUPPORTED by
    # Cohere structured outputs and must NOT be flagged. (pattern itself is
    # supported; only regex anchors inside it are not — that's a v0.4 deferral,
    # so a plain pattern without anchors must still pass.)
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "status": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            "self": {"$ref": "#"},
            "color": {"enum": ["r", "g", "b"]},
            "kind": {"const": "x"},
            "code": {"type": "string", "pattern": "[a-z]+"},
        },
        "required": ["status", "self", "color", "kind", "code"],
    }
    findings = lint(schema, "cohere")
    assert not has_errors(findings), f"cohere false-positive: {_ids(findings)}"


def test_cohere_pointer_is_precise():
    schema = {"type": "object", "properties": {"xs": {"type": "array", "minItems": 1}}}
    f = [x for x in lint(schema, "cohere") if x.rule_id == "cohere-no-minItems"]
    assert len(f) == 1
    assert f[0].json_pointer == "#/properties/xs/minItems"


# --- Mistral: thin, example-derived strict structured-output conventions -------

def test_mistral_requires_additional_properties_false():
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]}
    got = _ids(lint(schema, "mistral"))
    assert "mistral-additional-properties-false" in got


def test_mistral_requires_all_properties_required():
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
        "required": ["a"],
    }
    f = [x for x in lint(schema, "mistral") if x.rule_id == "mistral-all-properties-required"]
    assert len(f) == 1
    assert f[0].keyword == "b"  # the optional one


def test_mistral_has_no_keyword_blocklist():
    # Mistral docs enumerate no per-keyword unsupported list, so a schema that
    # only trips Cohere/Anthropic keyword rules (but is strict-shaped) must PASS
    # Mistral — proving we did NOT invent a keyword-blocklist pack.
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"s": {"type": "string", "minLength": 1, "pattern": "^x"}},
        "required": ["s"],
    }
    assert not has_errors(lint(schema, "mistral"))


# --- Cross-provider: the matrix is now 5; clean schema passes all -------------

def test_portable_good_fixture_passes_all_five_providers():
    import json

    schema = json.loads((FIXTURES / "portable-good.json").read_text())
    results = lint_multi(schema, list(PROVIDERS))
    assert set(PROVIDERS) == {"openai", "anthropic", "gemini", "mistral", "cohere"}
    for provider, findings in results.items():
        assert not has_errors(findings), f"{provider} unexpectedly failed portable-good: {findings}"


# --- New failure modes via the CLI (the two new fixtures) --------------------

def test_cohere_bad_fixture_fails_under_cohere(capsys):
    rc = main(["lint", str(FIXTURES / "cohere-bad.json"), "--provider", "cohere"])
    assert rc == 1
    assert "cohere" in capsys.readouterr().out.lower()


def test_mistral_bad_fixture_fails_under_mistral(capsys):
    rc = main(["lint", str(FIXTURES / "mistral-bad.json"), "--provider", "mistral"])
    assert rc == 1
    assert "mistral" in capsys.readouterr().out.lower()


def test_new_bad_fixtures_pass_unaffected_providers():
    # cohere-bad uses only composition/range keywords + strict shape -> Mistral
    # (no keyword blocklist) accepts it; mistral-bad is keyword-clean -> Cohere
    # accepts it. Confirms the packs are provider-specific, not blanket failures.
    import json

    cohere_bad = json.loads((FIXTURES / "cohere-bad.json").read_text())
    mistral_bad = json.loads((FIXTURES / "mistral-bad.json").read_text())
    assert not has_errors(lint(cohere_bad, "mistral"))
    assert not has_errors(lint(mistral_bad, "cohere"))
