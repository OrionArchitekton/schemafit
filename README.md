# schemafit

**Provider-aware structured-output / JSON-Schema CI linter.** Catch the schema
incompatibilities that make one provider `400` while another succeeds — *before*
they hit production, as a fast, offline CI check.

A JSON Schema / tool definition / `response_format` that works on OpenAI can
`400` on Anthropic or Gemini (and vice-versa): nested `oneOf`, a missing
`additionalProperties: false`, a `default` in a property, Anthropic-rejected
validation keywords (`minLength`, `format`, `pattern`, …), Gemini's lack of
`anyOf`/dict support. The API tells you it failed but not *which constraint*
violated it, so teams hand-port schemas and debug by trial-and-error at runtime.

`schemafit` encodes each provider's documented constraint surface as a
**versioned, declarative rule pack** and lints your schema statically — pointing
at the exact JSON-Pointer path, the keyword, and why — with a non-zero exit code
so CI fails the PR instead of prod.

> Every rule is grounded in a real, cited provider issue (see
> [`schemafit/rules/`](schemafit/rules/)). It is **not** a runtime client: it
> makes no model calls, needs no API key, and has **zero runtime dependencies**.

## Why this and not Instructor / BAML / LiteLLM / Vercel AI SDK?

Those are excellent **runtime** clients — they normalize, repair, or constrain a
schema *at call-time*. `schemafit` fills the gap they leave: a **static,
pre-ship CI lint** that fails the build before the schema ever reaches a
provider, over the raw schemas you already ship, with no DSL or codegen buy-in.

## Install

```bash
# From source (works today):
pip install "git+https://github.com/OrionArchitekton/schemafit"
# or build and run the container:
docker build -t schemafit . && docker run --rm schemafit demo
```

Once the first release is tagged (`v0.1.0`), `pip install schemafit` (PyPI) and
`docker run --rm ghcr.io/orionarchitekton/schemafit demo` (GHCR) become
available — both are published by the release workflow on a `v*` tag (PyPI via
Trusted Publishing; image to GHCR).

## Usage

```bash
# Lint one schema against several providers (exit 1 if any error):
schemafit lint my-schema.json --provider openai,anthropic,gemini

# Machine-readable output for CI annotations:
schemafit lint my-schema.json --provider anthropic --format json

# SARIF 2.1.0 for GitHub code-scanning / the Security tab:
schemafit lint my-schema.json --provider openai,anthropic --format sarif > schemafit.sarif

# Confirm against the live provider (opt-in; MOCK unless a key is in the env):
schemafit lint my-schema.json --provider openai --live-verify

# Also fail on warnings (e.g. Gemini $ref recursion risk):
schemafit lint my-schema.json --provider gemini --strict

# Emit a best-effort provider-valid variant (lossy transforms are flagged):
schemafit repair my-schema.json --provider anthropic --out fixed.json

# List supported providers / run a hermetic end-to-end proof:
schemafit providers
schemafit demo
```

Example:

```
$ schemafit lint order.json --provider anthropic
[anthropic] FAIL — 2 error(s), 0 warning(s)
  ERROR   #/properties/sku/pattern  (anthropic-no-pattern)
          Anthropic rejects the 'pattern' validation keyword (400 Bad Request).
          ref: https://github.com/vercel/ai/issues/13355
  ERROR   #/properties/qty/minimum  (anthropic-no-minimum)
          Anthropic rejects the 'minimum' validation keyword (400 Bad Request).
```

## Use in CI

GitHub Actions (this repo ships a composite action):

```yaml
- uses: OrionArchitekton/schemafit@v0.1.0
  with:
    schema: schemas/tool.json
    providers: openai,anthropic,gemini
```

Or directly / as a pre-commit hook (`.pre-commit-hooks.yaml` is included):

```yaml
- repo: https://github.com/OrionArchitekton/schemafit
  rev: v0.1.0
  hooks:
    - id: schemafit
      args: ["--provider", "openai,anthropic,gemini"]
      files: '^schemas/.*\.json$'   # scope to YOUR LLM schemas, not every .json
```

> Scope the hook with `files:` to the directory holding your LLM schemas — the
> default `types: [json]` would otherwise lint every JSON file in the repo
> (`package.json`, `tsconfig.json`, lockfiles), which are not LLM schemas.

## GitHub code-scanning (SARIF)

`--format sarif` emits [SARIF 2.1.0](https://sarifweb.azurewebsites.net/) so lint
findings show up as annotations in the **Security → Code scanning** tab, with the
exact JSON-Pointer path, the rule id, and the primary-source `helpUri`. SARIF is
written to stdout regardless of the exit code, so code-scanning still ingests the
artifact even when the gate fails (a clean schema produces a valid run with an
empty `results` array, which clears stale alerts):

```yaml
- run: schemafit lint schemas/*.json --provider openai,anthropic,gemini --format sarif > schemafit.sarif
  continue-on-error: true            # let code-scanning ingest the report
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: schemafit.sarif
```

## Live verification (`--live-verify`, opt-in)

`--live-verify` turns *"the docs forbid this"* into *"the provider actually
accepted/rejected it"* by sending a minimal structured-output probe to each
provider and **failing closed** on a rejection. It is **opt-in and key-gated**:

- **Default = MOCK** — with no provider key in the environment it uses a
  deterministic, network-free client modeled on the static rule pack, so CI and
  the Docker image run it with **no key and no network**.
- **Real call** — only when the provider's key (`OPENAI_API_KEY`,
  `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) is present in the environment. Real calls
  use the standard library (no new dependency); the `[live]` extra is reserved for
  optional provider SDKs.
- **Tri-state** — `confirmed_by_provider` is `true` (accepted), `false` (rejected
  → exit 1), or `null` (abstained: no key / rate-limited / network error).
  Abstaining is **not** a rejection and never fails CI.

> Never commit an API key. The real path reads keys only from the environment and
> never echoes their value. Leave `--live-verify` out of default CI.

## Supported providers (v0.2)

| Provider | Checks (grounded in) |
|---|---|
| `openai` | `additionalProperties:false` required; all properties required; no `default`; no `oneOf` in array items ([openai-agents-python#474](https://github.com/openai/openai-agents-python/issues/474), [claude-task-master#1522](https://github.com/eyaltoledano/claude-task-master/issues/1522)) |
| `anthropic` | 13 rejected validation keywords on the **strict structured-output surface**: `minLength`/`maxLength`/`pattern`/`format`/`minimum`/`maximum`/`exclusiveMinimum`/`exclusiveMaximum`/`minItems`/`maxItems`/`uniqueItems`/`minProperties`/`maxProperties` ([vercel/ai#13355](https://github.com/vercel/ai/issues/13355), [anthropic-sdk-python#1034](https://github.com/anthropics/anthropic-sdk-python/issues/1034)). General Messages-API tool `input_schema` is more permissive — run this pack against schemas you send on the structured-output path. |
| `gemini` | **Portability warnings** (version-sensitive, non-failing by default): `anyOf` (rejected by ≤2.0 / old SDKs, supported by 2.5), `oneOf`, open dict (`additionalProperties` schema), `$ref` recursion. Gemini's schema support changed fast (`anyOf` Jan 2026, `additionalProperties` Nov 2025), so these *warn* — use `--strict` to gate on them. ([python-genai#460](https://github.com/googleapis/python-genai/issues/460), [docs](https://ai.google.dev/gemini-api/docs/structured-output)) |

## Exit codes

| code | meaning |
|---|---|
| `0` | no errors (warnings allowed unless `--strict`) |
| `1` | at least one error (CI fail) |
| `2` | bad input (unreadable / invalid JSON) |

## Scope and roadmap

In scope now: the `lint` + `repair` core, three provider rule packs, human/JSON
**and SARIF 2.1.0** reporters, an opt-in **`--live-verify`** confirmation mode,
Docker image, GitHub Action, pre-commit hook.

Shipped in **v0.2**: SARIF output for GitHub code-scanning; the `--live-verify`
opt-in live-confirmation mode (MOCK by default, key-gated real calls, fail-closed).

Deferred (v0.3+): more provider rule packs (Mistral, Cohere, Bedrock, Vertex);
automatic rule-pack **drift detection** (pairs with `--live-verify` over the live
provider); a `pydantic` source-model auto-fix mode; and an npm/`ajv` port plus a
Zod source-model for the JS/TS ecosystem.

## License

MIT © 2026 Dan Mercede
