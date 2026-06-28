"""SARIF 2.1.0 reporter contract (GitHub code-scanning native)."""

from __future__ import annotations

import json
import pathlib
import tomllib

from schemafit import __version__
from schemafit.cli import main
from schemafit.linter import lint_multi
from schemafit.report import format_sarif, format_sarif_multi


def test_runtime_version_matches_pyproject():
    # The CLI `--version` and SARIF `tool.driver.version` both import
    # `schemafit.__version__`; a release must not identify itself with a stale
    # version number that drifts from the packaged metadata.
    pyproject = pathlib.Path(__file__).resolve().parent.parent / "pyproject.toml"
    meta = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert __version__ == meta["project"]["version"]


def test_sarif_is_valid_2_1_0_document():
    results = lint_multi(
        {"type": "object", "properties": {"n": {"type": "string", "minLength": 1}}}, ["anthropic"]
    )
    doc = json.loads(format_sarif(results, uri="order.json"))
    assert doc["version"] == "2.1.0"
    assert "$schema" in doc and "sarif" in doc["$schema"]
    driver = doc["runs"][0]["tool"]["driver"]
    assert driver["name"] == "schemafit"
    assert driver["version"] == __version__


def test_sarif_bad_schema_has_error_result_with_ruleid_and_helpuri():
    results = lint_multi(
        {"type": "object", "properties": {"n": {"type": "string", "minLength": 1}}}, ["anthropic"]
    )
    run = json.loads(format_sarif(results, uri="order.json"))["runs"][0]
    assert run["results"], "expected at least one SARIF result"
    r0 = next(r for r in run["results"] if r["ruleId"] == "anthropic-no-minLength")
    assert r0["level"] == "error"
    assert r0["message"]["text"]
    rule = run["tool"]["driver"]["rules"][r0["ruleIndex"]]
    assert rule["id"] == "anthropic-no-minLength"
    assert rule["helpUri"].startswith("http")
    loc = r0["locations"][0]
    assert loc["logicalLocations"][0]["fullyQualifiedName"].startswith("#/")
    assert loc["physicalLocation"]["artifactLocation"]["uri"] == "order.json"


def test_sarif_clean_schema_is_valid_with_empty_results():
    # NEW FAILURE MODE: a clean schema must still emit a *valid* SARIF doc with
    # an empty results array and a present run/driver — never crash, never omit
    # the run (a code-scanning upload of an empty-but-valid run clears old alerts).
    clean = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"n": {"type": "string"}},
        "required": ["n"],
    }
    doc = json.loads(format_sarif_multi({"clean.json": lint_multi(clean, ["openai", "anthropic"])}))
    assert doc["version"] == "2.1.0"
    run = doc["runs"][0]
    assert run["results"] == []
    assert run["tool"]["driver"]["name"] == "schemafit"


def test_sarif_warning_level_for_gemini_portability_warning():
    # Gemini anyOf is a version-sensitive *warning* -> SARIF level "warning".
    results = lint_multi(
        {"type": "object", "properties": {"s": {"anyOf": [{"type": "string"}, {"type": "null"}]}}},
        ["gemini"],
    )
    run = json.loads(format_sarif(results))["runs"][0]
    assert run["results"], "expected a gemini warning result"
    assert {r["level"] for r in run["results"]} == {"warning"}


def test_sarif_stdin_path_renders_as_stdin_uri(tmp_path, capsys):
    schema = {"type": "object", "properties": {"n": {"type": "string", "minLength": 1}}}
    # exercise format_sarif_multi's "-" -> "stdin" mapping via the CLI stdin path
    import io
    import sys

    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps(schema))
    try:
        rc = main(["lint", "-", "--provider", "anthropic", "--format", "sarif"])
    finally:
        sys.stdin = old_stdin
    out = capsys.readouterr().out
    assert rc == 1
    doc = json.loads(out)
    uris = {
        loc["physicalLocation"]["artifactLocation"]["uri"]
        for r in doc["runs"][0]["results"]
        for loc in r["locations"]
    }
    assert uris == {"stdin"}


def test_sarif_uri_normalizes_separators_and_encodes_unsafe_chars():
    # Backslashes become forward slashes (path separators kept literal); spaces,
    # '#', '?', '%' and other URI-unsafe chars are percent-encoded so the
    # artifactLocation.uri is a valid RFC 3986 reference for SARIF consumers.
    results = lint_multi(
        {"type": "object", "properties": {"n": {"type": "string", "minLength": 1}}}, ["anthropic"]
    )
    run = json.loads(format_sarif(results, uri=r"sub dir\a#b.json"))["runs"][0]
    uris = {
        loc["physicalLocation"]["artifactLocation"]["uri"]
        for r in run["results"]
        for loc in r["locations"]
    }
    assert uris == {"sub%20dir/a%23b.json"}


def test_cli_format_sarif_preserves_exit_codes(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"type": "object", "properties": {"n": {"minLength": 1}}}))
    rc = main(["lint", str(bad), "--provider", "anthropic", "--format", "sarif"])
    out = capsys.readouterr().out
    assert rc == 1  # exit-code contract preserved under SARIF
    assert json.loads(out)["version"] == "2.1.0"

    good = tmp_path / "good.json"
    good.write_text(
        json.dumps(
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {"n": {"type": "string"}},
                "required": ["n"],
            }
        )
    )
    rc2 = main(["lint", str(good), "--provider", "openai,anthropic,gemini", "--format", "sarif"])
    out2 = capsys.readouterr().out
    assert rc2 == 0
    assert json.loads(out2)["runs"][0]["results"] == []
