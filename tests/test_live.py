"""--live-verify: mock-default client, fail-closed, key-gated real selection."""

from __future__ import annotations

import io
import json
import os
import sys

import pytest

from schemafit import live
from schemafit.cli import main
from schemafit.live import (
    LiveResult,
    MockProviderClient,
    RealHTTPClient,
    get_client,
    interpret_response,
    verify_providers,
)

_KEYS = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY")

_GOOD = {
    "type": "object",
    "additionalProperties": False,
    "properties": {"n": {"type": "string"}},
    "required": ["n"],
}
_BAD = {"type": "object", "properties": {"n": {"type": "string", "minLength": 1}}}


@pytest.fixture(autouse=True)
def _no_provider_keys(monkeypatch):
    """Default every test to a key-free environment (CI/hermetic posture)."""
    for k in _KEYS:
        monkeypatch.delenv(k, raising=False)


def _write(tmp_path, obj):
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return str(p)


# --- pure verdict-interpretation logic (covers the real client's decision) ----

def test_interpret_response_maps_status_to_tristate():
    assert interpret_response(200) is True
    assert interpret_response(201) is True
    assert interpret_response(400, "invalid schema") is False
    # auth / quota / server / transport -> abstain, never a false "rejected"
    assert interpret_response(401) is None
    assert interpret_response(403) is None
    assert interpret_response(429) is None
    assert interpret_response(500) is None


# --- mock client: deterministic, faithful to the static rule pack -------------

def test_mock_client_accepts_clean_rejects_bad():
    mc = MockProviderClient()
    assert mc.verify(_GOOD, "anthropic").accepted is True
    assert mc.verify(_BAD, "anthropic").accepted is False


def test_get_client_is_mock_without_key_real_with_key(monkeypatch):
    assert isinstance(get_client("openai"), MockProviderClient)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-used")
    client = get_client("openai")
    assert isinstance(client, RealHTTPClient)
    # allow_real=False must force the mock even when a key is present
    assert isinstance(get_client("openai", allow_real=False), MockProviderClient)


def test_verify_providers_returns_per_provider_mock_verdicts():
    out = verify_providers(_BAD, ["openai", "anthropic", "gemini"], allow_real=False)
    assert out["anthropic"].accepted is False  # minLength -> rejected
    assert out["anthropic"].client == "mock"
    assert out["gemini"].accepted is True  # gemini treats these as warnings -> accepted


def test_live_verify_makes_no_network_call_on_mock_path(monkeypatch, tmp_path, capsys):
    def _boom(*a, **k):  # any network call is a bug on the default path
        raise AssertionError("network call attempted on the mock path")

    monkeypatch.setattr(live.urllib.request, "urlopen", _boom)
    rc = main(["lint", _write(tmp_path, _GOOD), "--provider", "openai", "--live-verify"])
    assert rc == 0
    assert "confirmed_by_provider=True" in capsys.readouterr().out


# --- CLI integration: confirm-good, fail-closed-bad ---------------------------

def test_cli_live_verify_confirms_good_schema(tmp_path, capsys):
    rc = main(["lint", _write(tmp_path, _GOOD), "--provider", "openai", "--live-verify"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "LIVE-VERIFY confirmed_by_provider=True" in out
    assert "client=mock" in out


def test_cli_live_verify_fails_closed_on_mock_rejection(tmp_path, capsys):
    rc = main(["lint", _write(tmp_path, _BAD), "--provider", "anthropic", "--live-verify"])
    out = capsys.readouterr().out
    assert rc == 1  # fail-closed
    assert "confirmed_by_provider=False" in out


def test_cli_live_verify_fail_closed_even_when_static_passes(monkeypatch, tmp_path, capsys):
    # A schema that statically PASSES but the (injected) provider rejects must
    # still fail closed — the core value-add of a real live call.
    def _reject(schema, providers, **kwargs):
        return {
            p: LiveResult(p, accepted=False, client="openai", detail="injected") for p in providers
        }

    monkeypatch.setattr("schemafit.cli.verify_providers", _reject)
    rc = main(["lint", _write(tmp_path, _GOOD), "--provider", "openai", "--live-verify"])
    assert rc == 1
    assert "confirmed_by_provider=False" in capsys.readouterr().out


def test_cli_live_verify_abstain_does_not_fail(monkeypatch, tmp_path, capsys):
    # Abstain (None) is not a refutation: a clean schema with an abstaining live
    # call must still pass (no false CI failure).
    def _abstain(schema, providers, **kwargs):
        return {
            p: LiveResult(p, accepted=None, client="openai", detail="rate-limited")
            for p in providers
        }

    monkeypatch.setattr("schemafit.cli.verify_providers", _abstain)
    rc = main(["lint", _write(tmp_path, _GOOD), "--provider", "openai", "--live-verify"])
    assert rc == 0
    assert "confirmed_by_provider=None" in capsys.readouterr().out


def test_live_verify_annotates_findings_in_json(tmp_path, capsys):
    args = ["lint", _write(tmp_path, _BAD), "--provider", "anthropic", "--live-verify"]
    rc = main([*args, "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 1
    payload = json.loads(out)
    entry = next(iter(payload.values()))["anthropic"]
    assert entry["confirmed_by_provider"] is False
    assert all(f["confirmed_by_provider"] is False for f in entry["findings"])


def test_live_only_rejection_surfaces_in_json(monkeypatch, tmp_path, capsys):
    # A static-pass schema that the (injected) provider rejects must materialize a
    # first-class finding in JSON output — not just exit 1 with a PASS payload.
    def _reject(schema, providers, **kwargs):
        return {
            p: LiveResult(p, accepted=False, client="openai", detail="injected reject")
            for p in providers
        }

    monkeypatch.setattr("schemafit.cli.verify_providers", _reject)
    args = ["lint", _write(tmp_path, _GOOD), "--provider", "openai", "--live-verify"]
    rc = main([*args, "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 1
    payload = json.loads(out)
    entry = next(iter(payload.values()))["openai"]
    assert entry["status"] == "FAIL"
    rule_ids = {f["rule_id"] for f in entry["findings"]}
    # v0.5: static-pass + live-reject is now surfaced as *-drift (rule-pack drift)
    assert "openai-drift" in rule_ids


def test_live_only_rejection_surfaces_in_sarif(monkeypatch, tmp_path, capsys):
    # The same static-pass / live-reject case must emit a non-empty SARIF run, or
    # GitHub code-scanning sees an empty results array and clears stale alerts.
    def _reject(schema, providers, **kwargs):
        return {
            p: LiveResult(p, accepted=False, client="openai", detail="injected reject")
            for p in providers
        }

    monkeypatch.setattr("schemafit.cli.verify_providers", _reject)
    rc = main(
        [
            "lint",
            _write(tmp_path, _GOOD),
            "--provider",
            "openai",
            "--live-verify",
            "--format",
            "sarif",
        ]
    )
    out = capsys.readouterr().out
    assert rc == 1
    doc = json.loads(out)
    results = doc["runs"][0]["results"]
    assert results, "SARIF must not be empty when a live rejection fails CI"
    # v0.5: static-pass + live-reject surfaces as drift ruleId
    assert any(r["ruleId"] == "openai-drift" for r in results)


def test_live_abstain_does_not_synthesize_finding(monkeypatch, tmp_path, capsys):
    # Abstain (None) is not a rejection: no synthetic finding, clean pass.
    def _abstain(schema, providers, **kwargs):
        return {
            p: LiveResult(p, accepted=None, client="openai", detail="rate-limited")
            for p in providers
        }

    monkeypatch.setattr("schemafit.cli.verify_providers", _abstain)
    args = ["lint", _write(tmp_path, _GOOD), "--provider", "openai", "--live-verify"]
    rc = main([*args, "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    entry = next(iter(payload.values()))["openai"]
    assert entry["status"] == "PASS"
    assert not any(f["rule_id"] == "openai-live-rejection" for f in entry["findings"])


def test_no_live_verify_leaves_static_path_unchanged(tmp_path, capsys):
    # Without the flag: no LIVE-VERIFY output, unchanged exit codes.
    rc = main(["lint", _write(tmp_path, _BAD), "--provider", "anthropic"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "LIVE-VERIFY" not in out
    assert "confirmed_by_provider" not in out


# --- v0.5 drift detection (rule-pack drift via live on mock) -----------------

def test_cli_drift_mock_bad_produces_drift_finding_and_nonzero_exit(tmp_path, capsys):
    """Drift case: static-clean schema (for cohere) but mock live reveals violation.
    (via live_modeled_rejects for anchored pattern in fixture).
    Expect rule_id containing 'drift', FAIL, exit 1.
    """
    # use the committed drift fixture (relative path works from repo root under pytest)
    rc = main(["lint", "fixtures/drift-mock-bad.json", "--provider", "cohere", "--live-verify"])
    out = capsys.readouterr().out
    assert rc == 1, f"expected nonzero for drift case, got {rc}; out={out[:300]}"
    # must surface a drift finding (ruleId with 'drift')
    assert "drift" in out.lower() or "cohere-drift" in out
    assert "FAIL" in out
    # ensure live verify line appears
    assert "LIVE-VERIFY" in out or "confirmed_by_provider" in out


# --- regression: --live-verify is opt-in; never auto-enabled by the runtime env -

def test_docker_stdin_without_flag_stays_static(monkeypatch, capsys):
    """`--live-verify` is opt-in by contract. A Dockerized bare `lint -` (no flag)
    must keep the static default: no implicit /.dockerenv probe may turn live
    verification on and change exit-code/output semantics for stdin consumers.
    The schema is static-clean for cohere but carries a real anchor, so if live were
    wrongly auto-enabled it would synthesize a cohere-drift finding and exit 1.
    """
    drift_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"id": {"type": "string", "pattern": "^[a-z]+$"}},
        "required": ["id"],
    }
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(drift_schema)))
    # Simulate running inside a container: /.dockerenv "exists".
    real_exists = os.path.exists
    monkeypatch.setattr(
        os.path, "exists", lambda p: True if p == "/.dockerenv" else real_exists(p)
    )
    rc = main(["lint", "-", "--provider", "cohere"])
    out = capsys.readouterr().out
    assert rc == 0, f"static-clean schema must pass without --live-verify; got {rc}: {out[:200]}"
    assert "LIVE-VERIFY" not in out
    assert "drift" not in out.lower()
    assert "confirmed_by_provider" not in out


# --- regression: modeled cohere caveat targets true anchors, not literal ^/$ -----

@pytest.mark.parametrize("pat", [r"\^literal", r"\$literal", "[$]", "[^abc]", r"price\$[0-9]+"])
def test_live_modeled_rejects_ignores_escaped_and_classed_caret_dollar(pat):
    """Escaped (`\\^`, `\\$`) or character-class (`[$]`, `[^a]`) carets/dollars are
    regex literals, not start/end anchors. The modeled cohere caveat must not
    false-reject a static-clean schema that merely contains them."""
    schema = {"type": "object", "properties": {"x": {"type": "string", "pattern": pat}}}
    assert live.live_modeled_rejects(schema, "cohere") is False, f"{pat!r} wrongly rejected"


@pytest.mark.parametrize("pat", ["^x", "x$", "^[a-z]+$", "(?=foo)", "(?!bar)"])
def test_live_modeled_rejects_still_catches_true_anchors(pat):
    """True anchors/lookarounds remain the modeled cohere caveat -> rejected."""
    schema = {"type": "object", "properties": {"x": {"type": "string", "pattern": pat}}}
    assert live.live_modeled_rejects(schema, "cohere") is True, f"{pat!r} should be rejected"
