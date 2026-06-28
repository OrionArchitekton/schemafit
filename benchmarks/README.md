# schemafit real-world benchmark

**Question:** if you take JSON Schemas that developers *actually* feed to LLMs as
tool definitions / structured outputs, how many would a major provider reject?

**Answer (2026-06-28, schemafit v0.5.0):** across **50 real, public schemas**,
**44 (88%) would be rejected by at least one provider's structured-output
constraints**, and only **3 passed all five**. Full breakdown: [RESULTS.md](RESULTS.md).

## The corpus

50 schemas, each provenance-linked to a raw source URL in
[sources.tsv](sources.tsv):

- **15** from OpenAI & Anthropic cookbooks / SDK examples (`oa_*`).
- **17** from popular agent frameworks — instructor, langchain, pydantic-ai,
  crewai, guidance, llama-index, lm-format-enforcer (`fw_*`). Some are committed
  JSON; some are `model_json_schema()` of an official example Pydantic model
  (the source URL points at the model definition).
- **18** tool `inputSchema`s from official Model Context Protocol servers (`mcp_*`).

The schema files themselves are **not vendored** here — they belong to their
upstream projects. `sources.tsv` lists every one so you can audit or re-fetch.

## Reproduce

```bash
pip install schemafit
# point it at any directory of *.json schema files (yours, or re-fetched from sources.tsv)
python benchmarks/run.py path/to/schemas/
```

Each schema is linted with one command — static, offline, no provider calls:

```bash
schemafit lint <schema.json> --provider openai,anthropic,gemini,mistral,cohere --format json
```

## Honesty notes

- **OpenAI is the firm case.** Strict Structured Outputs *require*
  `additionalProperties: false` and every property in `required`; the schemas
  that pass OpenAI genuinely carry both (verified). That's the rock-solid 88%.
- **Mistral's number uses schemafit's more conservative rule** — its finding text
  notes the constraint is example-derived (Mistral's docs *show* but don't
  prose-mandate `additionalProperties:false`). Read Mistral as "likely-reject."
- **Gemini hits are warnings** (`$ref` recursion, `anyOf`), not hard errors.
- Every rule is grounded in a cited provider doc/issue (each finding carries a
  `doc_url`). The corpus is provider-mixed by design, so 88% is a floor, not a
  cherry-pick.
