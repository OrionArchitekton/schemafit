"""CLI exit codes and output contracts (what CI depends on)."""

from __future__ import annotations

import json

from schemafit.cli import main


def _write(tmp_path, obj):
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return str(p)


def test_lint_exit_1_on_violation(tmp_path, capsys):
    path = _write(
        tmp_path, {"type": "object", "properties": {"n": {"type": "string", "minLength": 1}}}
    )
    rc = main(["lint", path, "--provider", "anthropic"])
    assert rc == 1
    assert "FAIL" in capsys.readouterr().out


def test_lint_exit_0_on_clean(tmp_path, capsys):
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"n": {"type": "string"}},
        "required": ["n"],
    }
    path = _write(tmp_path, schema)
    rc = main(["lint", path, "--provider", "openai,anthropic,gemini"])
    assert rc == 0
    assert "PASS" in capsys.readouterr().out


def test_lint_json_format_is_valid_json(tmp_path, capsys):
    path = _write(tmp_path, {"type": "object", "properties": {"n": {"minLength": 1}}})
    rc = main(["lint", path, "--provider", "anthropic", "--format", "json"])
    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload[path]["anthropic"]["status"] == "FAIL"
    assert payload[path]["anthropic"]["findings"]


def test_lint_multiple_files(tmp_path):
    good = _write(
        tmp_path,
        {
            "type": "object",
            "additionalProperties": False,
            "properties": {"n": {"type": "string"}},
            "required": ["n"],
        },
    )
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"type": "object", "properties": {"n": {"minLength": 1}}}))
    rc = main(["lint", good, str(bad), "--provider", "anthropic"])
    assert rc == 1  # one bad file fails the whole run


def test_strict_flag_fails_on_warning(tmp_path, capsys):
    # $ref is a Gemini warning; default lint passes, --strict fails.
    path = _write(tmp_path, {"type": "object", "properties": {"s": {"$ref": "#"}}})
    assert main(["lint", path, "--provider", "gemini"]) == 0
    capsys.readouterr()
    assert main(["lint", path, "--provider", "gemini", "--strict"]) == 1


def test_repair_command_writes_valid_output(tmp_path, capsys):
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"name": {"type": "string", "minLength": 1}},
        "required": ["name"],
    }
    path = _write(tmp_path, schema)
    out = tmp_path / "fixed.json"
    rc = main(["repair", path, "--provider", "anthropic", "--out", str(out)])
    assert rc == 0
    fixed = json.loads(out.read_text())
    assert "minLength" not in fixed["properties"]["name"]


def test_providers_command(capsys):
    assert main(["providers"]) == 0
    assert "anthropic" in capsys.readouterr().out


def test_demo_command_proof(capsys):
    rc = main(["demo"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "PROOF_OK" in out
    assert "MULTI:" in out


def test_deeply_nested_schema_exits_2_not_traceback(tmp_path):
    # A hostile/malformed deeply-nested schema must exit cleanly (2), never crash
    # with an uncaught RecursionError that masquerades as a lint failure (1).
    depth = 5000
    text = '{"not":' * depth + '{"type":"object"}' + "}" * depth
    path = tmp_path / "deep.json"
    path.write_text(text, encoding="utf-8")
    rc = main(["lint", str(path), "--provider", "anthropic"])
    assert rc == 2
