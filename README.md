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

## Supported providers (v0.1)

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

## Scope (v0.1) and roadmap

In scope now: the `lint` + `repair` core, three provider rule packs, JSON/human
reporters, Docker image, GitHub Action, pre-commit hook.

Deferred (v0.2+): a `--live-verify` mode that calls each provider to confirm,
an npm/`ajv` port for the JS/TS ecosystem, more providers (Mistral, Cohere,
Bedrock, Vertex), automatic rule-pack drift detection, SARIF output, and
source-model (Pydantic/Zod) auto-fix.

## License

MIT © 2026 Dan Mercede
