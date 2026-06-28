# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.5.0] - 2026-06-28

### Added
- **Automatic rule-pack drift detection** (AMBITIOUS v0.5 cut per MAP) — when
  `--live-verify` (mock-default, hermetic) is used and a provider's live verdict
  rejects while the static pack had no errors, a `*-drift` finding (kind "drift",
  rule_id e.g. `cohere-drift`) is emitted. Reuses `Finding`, `report.*`, SARIF
  paths exactly. MockProviderClient extended for hermetic sentinel-driven
  simulation on dedicated `fixtures/drift-mock-bad.json` (static-clean for
  cohere + sentinel forces mock reject to model "pack lagged provider docs").
  Abstain never fails; real calls opt-in via key; doc_url foundation from packs
  preserved. CLI/docker proofs exercise `cohere-drift` + FAIL exit=1.
- Version bump 0.4.0 → 0.5.0; tests, ruff, CI sequence, docker all green.
- No core deps added; no LOCKED-OUT or DEFER items touched.

### Notes
- Drift completes the live foundation shipped in v0.4 (ProviderClient/Mock +
  doc_url). All proofs mock-only (no net). HANDOFF posture: PR ready, tag
  v0.5.0 is publish gate (IRREVERSIBLE).
- Prior v0.1–v0.4 surfaces unchanged and green; 5-provider matrix intact.

## [0.4.0] - 2026-06-28

### Added
- **Cohere structural rules** (TIGHT v0.4 cut per MAP) — two new `apply_rule` kinds:
  `root_must_be_object` (top-level schema must be `type: object`) and
  `object_min_one_required` (every object schema, including nested, must have
  at least one field in `required`). Implemented as data-driven rules in the
  cohere pack (primary-sourced to docs.cohere.com/docs/structured-outputs).
  New fixture `fixtures/cohere-structural-bad.json`; extended tests cover both
  failure modes + no regression on `portable-good` across all 5 providers.
  No change to CLI surface, core deps remain `[]`, prior surface untouched.

### Notes
- This completes the static Cohere pack surface for the documented structural
  constraints. Rule-pack drift detection, Pydantic, Bedrock/Vertex, and npm/Zod
  ports remain DEFERRED (see MAP). All proofs hermetic (CLI, pytest, ruff, docker).
- v0.1–v0.3 surfaces unchanged and green.

## [0.3.0] - 2026-06-21

### Added
- **Cohere provider rule pack** — 10 hard-error rules for the JSON-Schema keywords
  Cohere structured outputs do not support, taken from Cohere's keyword-support
  table: composition (`allOf`/`oneOf`/`not`), numeric ranges (`minimum`/`maximum`),
  array-length (`minItems`/`maxItems`), string-length (`minLength`/`maxLength`),
  and `uniqueItems` (marked unsupported for both structured-output columns;
  allowed only under regular Tool Use with `strict_tools=False`). Supported
  keywords (`anyOf`, `$ref`/`$def`, `enum`, `const`, `pattern`) are not flagged.
  Every rule is primary-sourced to
  [docs.cohere.com/docs/structured-outputs](https://docs.cohere.com/docs/structured-outputs).
  Regex anchors inside a `pattern` are also unsupported by Cohere, but detecting
  them needs value-inspection (a new rule kind) and is deferred to v0.4.
- **Mistral provider rule pack** (thin) — the strict custom-structured-output
  conventions that are lintable at the schema-node level: `additionalProperties:false`
  required and every property listed in `required`. Mistral's docs enumerate no
  per-keyword unsupported list, so no keyword-blocklist rules were invented; both
  rules are example-derived from the official sample and labelled as such. The
  `strict:true` request flag and the `codestral-mamba` exclusion are API/model-level
  and documented as README notes, not lint rules.
- The provider matrix is now **5** (`openai`, `anthropic`, `gemini`, `mistral`,
  `cohere`); the CI "clean schema passes" contract is extended to all five.

### Notes
- Core package stays **zero-dependency** (`dependencies = []`); the new packs are
  declarative JSON and add no dependency. Both packs reuse the existing rule kinds
  and auto-repair strategies — no new engine logic.
- v0.1 and v0.2 surfaces are unchanged and still green: `lint`/`repair`/`providers`/`demo`,
  the SARIF reporter, and `--live-verify` (mock-default, tri-state, fail-closed).
- Deferred to **v0.4**: Cohere's structural rules (new rule kinds), rule-pack
  drift detection, Bedrock/Vertex packs, a Pydantic source-model mode, and the
  npm/`ajv` + Zod JS ecosystem port.

## [0.2.0] - 2026-06-20

### Added
- **SARIF 2.1.0 output** (`lint --format sarif`) for GitHub code-scanning / the
  Security tab. Maps each finding to a SARIF result (`ruleId`, `level`,
  `message`, JSON-Pointer logical location, `helpUri` from the rule's primary
  source). SARIF is emitted regardless of exit code; a clean schema produces a
  valid run with an empty `results` array. A `--live-verify` provider rejection
  is materialized as a first-class SARIF/JSON result (`<provider>-live-rejection`)
  so a static-pass / live-reject run never emits an empty report while failing CI.
  SARIF artifact URIs are normalized to forward slashes (valid RFC 3986 / Windows
  paths). No new dependency (hand-emitted JSON).
- **`--live-verify`** (`lint --live-verify`): an opt-in mode that confirms a
  schema against each provider through a mockable client and **fails closed** on
  a provider rejection. The default client is a deterministic, network-free MOCK
  (no key required) used by the test suite and the Docker image; a real
  stdlib-HTTP client is used only when the provider's API key is present in the
  environment. Results are tri-state (`confirmed_by_provider`: accepted /
  rejected / abstained); abstaining never fails CI. A `[live]` optional-extra is
  reserved for provider SDKs and adds no dependency today.
- `Finding.confirmed_by_provider` (tri-state) carries the live verdict in the
  JSON/SARIF output; it is `null` on the default static path (backward-compatible).

### Notes
- Core package stays **zero-dependency** (`dependencies = []`); the static lint
  path and the default `--live-verify` (MOCK) path make no network call.
- The three v0.1 providers and the two CI exit-code contracts are unchanged.
  Additional provider packs (Mistral/Cohere/Bedrock/Vertex) and rule-pack drift
  detection are deferred to v0.3.

## [0.1.0] - 2026-06-20

### Added
- `lint` command: statically check a JSON Schema / tool / `response_format`
  against `openai`, `anthropic`, and `gemini` constraint rule packs; non-zero
  exit on errors for CI.
- `repair` command: best-effort, lossiness-flagged provider-valid variant;
  unsafe rewrites reported as `manual_required`.
- `providers` and `demo` commands (`demo` is a hermetic end-to-end proof).
- Declarative, versioned JSON rule packs grounded in cited provider issues.
- Human and JSON reporters; `--strict` to fail on warnings.
- Docker image, GitHub composite Action, and pre-commit hook.

### Hardening (pre-publish adversarial review)
- Fix false positive: a non-object schema carrying a stray `properties` key
  (e.g. `type: array`) is no longer treated as an object by the OpenAI rules.
- Traverse `dependentSchemas` / `dependencies` / `contentSchema` so forbidden
  keywords hidden there are caught (was a false-negative).
- `repair`: flag as lossy when `set_false` overwrites an `additionalProperties`
  subschema; skip nodes already removed by an earlier fix.
- CLI: deeply-nested/hostile schemas exit cleanly (code 2) instead of crashing
  with an uncaught `RecursionError` that looks like a lint failure.
- Gemini rules downgraded to version-sensitive **warnings**: current Gemini 2.5
  supports `anyOf` (Jan 2026) and `additionalProperties` (Nov 2025), so these no
  longer hard-fail CI (use `--strict` to gate). Anthropic pack scoped to the
  strict structured-output surface in its docs.
- GitHub Action: inputs passed via `env:` (data, not code) to prevent shell
  script injection. Added `py.typed`, 3.12/3.13 classifiers, and a tag-triggered
  release workflow (PyPI Trusted Publishing + GHCR).

### Notes
- Zero runtime dependencies (stdlib-only lint path).
