# AGENTS.md - schemafit

## Repo Role

`schemafit` is a provider-aware structured-output and JSON Schema CI linter for
LLM integrations. It statically checks schemas and tool definitions against
provider-specific constraint rule packs before they fail at runtime.

## Boundaries

- Owns the Python package, CLI, provider rule packs, fixtures, benchmarks,
  tests, GitHub Action metadata, and repo docs.
- Does not own provider APIs, live API keys, production prompts, or downstream
  app schemas beyond lint input fixtures.
- Preserve offline/static linting as the default. Live-provider behavior must
  stay explicit and isolated.

## Authority Order

1. `/home/orion/src/orion-estate/platform/orion-estate-audit/AGENTS.md`
2. `README.md`
3. `specs/`, fixtures, provider rule packs, and tests
4. `pyproject.toml`, `action.yml`, and CLI source

## Validation

```bash
python -m pytest
ruff check .
```

For docs-only changes, run `git diff --check` at minimum.
