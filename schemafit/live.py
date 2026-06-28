"""Optional ``--live-verify`` mode: confirm a schema against a live provider.

The default client is a **MOCK** that needs no network and no API key: it
replays the static rule pack, so a schema with error-severity findings is
"rejected" and a clean schema is "accepted". This makes ``--live-verify``
deterministic and provable offline (the test suite + the Docker proof) while
exercising exactly the code path a real provider call would.

A real provider client is used ONLY when ``--live-verify`` is passed AND that
provider's API key is present in the environment. Real calls use the standard
library (``urllib``) so the core package stays dependency-free; the ``[live]``
optional-extra is reserved for provider SDKs. The real path is opt-in, never
runs in default CI (no key is present there), and no key value is ever surfaced.

Tri-state verdict (``LiveResult.accepted`` / ``Finding.confirmed_by_provider``):

* ``True``  — the provider accepted the schema (confirmed compatible).
* ``False`` — the provider rejected the schema (fail-closed: ``lint`` exits 1).
* ``None``  — abstain: unverifiable (no key, rate-limited, network error).
  Abstain is NOT a rejection (abstention != refutation) and never fails CI.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from .linter import PROVIDERS, has_errors, lint

# Env var holding each provider's API key. Only PRESENCE (never the value)
# selects the real client; the value is used solely to authenticate the request.
PROVIDER_KEY_ENV: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


@dataclass(frozen=True)
class LiveResult:
    """The outcome of a live acceptance check for one (schema, provider)."""

    provider: str
    accepted: bool | None  # True=accepted, False=rejected, None=abstain
    client: str  # "mock" | "openai" | "anthropic" | "gemini"
    detail: str = ""

    @property
    def verdict(self) -> str:
        return {True: "accepted", False: "rejected", None: "abstain"}[self.accepted]


class ProviderClient:
    """A provider acceptance check. Implementations must make NO network call
    until ``verify`` is invoked, so importing this module is side-effect free."""

    name = "base"

    def verify(self, schema: object, provider: str) -> LiveResult:  # pragma: no cover
        raise NotImplementedError


class MockProviderClient(ProviderClient):
    """Deterministic, network-free stand-in.

    Models provider acceptance with the static rule pack: a schema with any
    error-severity finding is rejected, otherwise accepted. Used by the tests
    and the Docker proof so ``--live-verify`` is provable with no key/network.

    Additionally models the deferred cohere caveat for regex anchors inside
    pattern (pure function, no env/filename hacks).
    """

    name = "mock"

    def verify(self, schema: object, provider: str) -> LiveResult:
        rejected = has_errors(lint(schema, provider)) or live_modeled_rejects(schema, provider)
        return LiveResult(
            provider=provider,
            accepted=not rejected,
            client="mock",
            detail="modeled from the static rule pack (no network, no key)",
        )


def resolve_drift_doc_url(pack: dict) -> str:
    """Pure: return the first rule's doc_url (never the pack-level 'doc' text)."""
    for r in pack.get("rules", []):
        if r.get("doc_url"):
            return r["doc_url"]
    return ""


def _regex_has_anchor(pat: str) -> bool:
    """True if ``pat`` uses a start/end anchor (``^``/``$``) or a lookaround
    (``(?=``/``(?!``/``(?<=``/``(?<!``) as a *regex token*.

    Escaped literals (``\\^``, ``\\$``) and characters inside a class (``[$]``,
    ``[^a]``) are ordinary literals, not anchors, and must not match — scanning the
    raw string for any ``^``/``$`` byte (the prior behaviour) false-rejected them.
    """
    i, n, in_class = 0, len(pat), False
    while i < n:
        c = pat[i]
        if c == "\\":  # escaped: the next char is a literal, skip both
            i += 2
            continue
        if in_class:
            if c == "]":
                in_class = False
            i += 1
            continue
        if c == "[":
            in_class = True
            i += 1
            continue
        if c in "^$":  # unescaped and outside a class -> a true anchor
            return True
        if pat.startswith(("(?=", "(?!", "(?<=", "(?<!"), i):  # lookaround
            return True
        i += 1
    return False


def live_modeled_rejects(schema: object, provider: str) -> bool:
    """Pure: for cohere, reject schemas with regex anchors (^ $ (?= (?! ) inside any 'pattern'.
    This models the deferred caveat in the cohere pack doc (not yet enforced by static rules).
    """
    if provider != "cohere":
        return False
    if not isinstance(schema, dict):
        return False

    def _has_anchor(node: object) -> bool:
        if isinstance(node, dict):
            pat = node.get("pattern")
            if isinstance(pat, str):
                if _regex_has_anchor(pat):
                    return True
            for v in node.values():
                if _has_anchor(v):
                    return True
        elif isinstance(node, list):
            for item in node:
                if _has_anchor(item):
                    return True
        return False

    return _has_anchor(schema)


def interpret_response(status: int, body: str = "") -> bool | None:
    """Map a provider HTTP status to a tri-state acceptance verdict.

    Pure and unit-tested, so the real client's *decision logic* is covered even
    though the network round-trip cannot run without a key.

    * ``2xx``                      -> accepted (True)
    * ``400`` (schema/invalid req) -> rejected (False)
    * ``401``/``403``/``429``/``5xx``/other -> abstain (None): NOT a refutation
    """
    if 200 <= status < 300:
        return True
    if status == 400:
        # A 400 on a structured-output request is the provider rejecting the
        # schema itself. Auth/quota failures are 401/403/429, not 400 — those
        # abstain rather than masquerade as a schema rejection.
        return False
    return None


def _build_request(provider: str, schema: object) -> tuple[str, dict, dict]:
    """Build the (endpoint, json-payload, headers) for a real probe request.

    A minimal structured-output request that carries ``schema`` on the surface
    the provider validates. Best-effort and provider-version-sensitive; only
    reached on the opt-in, key-gated real path (never in default CI).
    """
    env_var = PROVIDER_KEY_ENV.get(provider)
    if not env_var:  # defensive: PROVIDERS gained an entry without a real client
        raise ValueError(f"no real live-verify client for provider {provider!r}")
    key = os.environ[env_var]
    if provider == "openai":
        endpoint = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": os.environ.get("SCHEMAFIT_OPENAI_MODEL", "gpt-4o-mini"),
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "schemafit live-verify probe"}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "schemafit_probe", "strict": True, "schema": schema},
            },
        }
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    elif provider == "anthropic":
        endpoint = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": os.environ.get("SCHEMAFIT_ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "schemafit live-verify probe"}],
            "tools": [{"name": "schemafit_probe", "input_schema": schema}],
        }
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
    elif provider == "gemini":
        model = os.environ.get("SCHEMAFIT_GEMINI_MODEL", "gemini-2.5-flash")
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": "schemafit live-verify probe"}]}],
            "generationConfig": {"responseMimeType": "application/json", "responseSchema": schema},
        }
        headers = {"Content-Type": "application/json", "x-goog-api-key": key}
    else:  # defensive: PROVIDERS gained an entry without a real client
        raise ValueError(f"no real live-verify client for provider {provider!r}")
    return endpoint, payload, headers


class RealHTTPClient(ProviderClient):
    """Env-key-gated real client using stdlib ``urllib`` (no third-party dep).

    Sends a minimal structured-output request carrying the schema and maps the
    HTTP status via :func:`interpret_response`. Opt-in only; never invoked in
    default CI. Transport errors abstain (``None``) so a flaky network never
    masquerades as a provider rejection.
    """

    def __init__(self, provider: str, *, timeout: float = 15.0) -> None:
        self.name = provider
        self._provider = provider
        self._timeout = timeout

    def _request(self, schema: object) -> tuple[int, str]:  # pragma: no cover - network
        endpoint, payload, headers = _build_request(self._provider, schema)
        data = json.dumps(payload).encode("utf-8")
        # endpoint is one of a fixed https allowlist built in _build_request.
        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")  # noqa: S310
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:  # noqa: S310
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", "replace")

    def verify(self, schema: object, provider: str) -> LiveResult:  # pragma: no cover - network
        try:
            status, body = self._request(schema)
        except Exception as exc:
            # Any transport-layer failure abstains rather than crashing the CLI.
            # http.client.HTTPException subclasses (IncompleteRead, BadStatusLine)
            # do NOT inherit from OSError, so a narrow except would let them crash
            # instead of safely abstaining. Abstain (None) != refutation.
            detail = f"abstain: transport error ({type(exc).__name__})"
            return LiveResult(provider, None, provider, detail)

        detail = f"HTTP {status}"
        if status == 400 and body:
            # Surface the provider's own error message for debugging instead of a
            # bare "HTTP 400". Best-effort; a parse failure falls back to a snippet.
            try:
                data = json.loads(body)
                err = data.get("error") if isinstance(data, dict) else None
                if isinstance(err, dict) and isinstance(err.get("message"), str):
                    detail = f"HTTP 400: {err['message']}"
                elif isinstance(err, str):
                    detail = f"HTTP 400: {err}"
                elif isinstance(data, dict) and isinstance(data.get("message"), str):
                    detail = f"HTTP 400: {data['message']}"
                else:
                    detail = f"HTTP 400: {body[:200]}"
            except (ValueError, AttributeError):
                detail = f"HTTP 400: {body[:200]}"

        return LiveResult(provider, interpret_response(status, body), provider, detail)


def get_client(provider: str, *, allow_real: bool = True) -> ProviderClient:
    """Return the real client when the provider key is in the environment (and
    real calls are allowed), else the deterministic mock.

    Selection reads only key PRESENCE, never the value. ``allow_real=False``
    forces the mock — used by tests and any hermetic context.
    """
    if allow_real and os.environ.get(PROVIDER_KEY_ENV.get(provider, "")):
        return RealHTTPClient(provider)
    return MockProviderClient()


def verify_providers(
    schema: object, providers: list[str], *, allow_real: bool = True
) -> dict[str, LiveResult]:
    """Run a live acceptance check for each provider; return per-provider results."""
    out: dict[str, LiveResult] = {}
    for provider in providers:
        if provider not in PROVIDERS:
            raise ValueError(f"unknown provider: {provider!r}")
        out[provider] = get_client(provider, allow_real=allow_real).verify(schema, provider)
    return out
