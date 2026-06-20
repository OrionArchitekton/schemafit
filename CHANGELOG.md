# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
[Semantic Versioning](https://semver.org/).

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
