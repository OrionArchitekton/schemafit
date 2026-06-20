# Contributing to schemafit

Thanks for your interest! schemafit aims to be a small, dependency-free, and
well-grounded tool.

## Ground rules

- **Every rule must cite a real source.** A new provider constraint needs a
  `doc_url` pointing at a provider issue, doc, or reproducible 400. No
  speculative rules.
- **Keep the core dependency-free.** The lint path is stdlib-only by design.
- **Rule packs are data.** Add or change constraints in
  `schemafit/rules/<provider>.json`, not in code, wherever possible.

## Dev setup

```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
ruff check .
pytest -q
schemafit demo
```

## Adding a provider rule

1. Add a rule object to `schemafit/rules/<provider>.json` with a stable `id`,
   a `kind` the engine supports, a `reason`, a `severity`, and a `doc_url`.
2. Add a test in `tests/test_lint.py` that reproduces the real failure the rule
   guards against (assert it fires on a bad schema and not on a good one).
3. Run `ruff check . && pytest -q`.

## Adding a new rule *kind*

Implement it in `schemafit/linter.py::apply_rule` and, if auto-fixable, in
`schemafit/repair.py`. Unsafe transforms must be reported as `manual_required`,
never guessed.

## Pull requests

Keep PRs focused. Include tests. CI (ruff + pytest + `schemafit demo`) must be
green.
