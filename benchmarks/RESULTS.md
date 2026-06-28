# schemafit proof run — what it actually catches on 50 real LLM schemas

*Run 2026-06-28 · schemafit v0.5.0 · 5 providers (OpenAI, Anthropic, Gemini, Mistral, Cohere)*

## TL;DR

- Took **50 real, public** LLM tool/structured-output JSON Schemas (not synthetic): 15 from OpenAI/Anthropic cookbooks & SDKs, 17 from agent frameworks (instructor, langchain, pydantic-ai, crewai, guidance, llama-index, lm-format-enforcer), 18 tool `inputSchema`s from official MCP servers. Every schema is provenance-linked to a raw source URL.
- **44/50 (88%) would be REJECTED by at least one major provider's structured-output constraints.**
- Only **3/50** were clean across all five. A schema that works on one provider usually does **not** work on the next — exactly the cross-provider 400 schemafit exists to catch in CI.
- The single biggest culprit: **`additionalProperties`** (134 flags) — the field almost nobody sets, which OpenAI strict Structured Outputs *requires* to be `false`.

## Rejections by provider

| Provider | Would reject (error) | Warn-only | Clean |
|---|---|---|---|
| openai | 44 (88%) | 0 | 6 |
| anthropic | 6 (12%) | 0 | 44 |
| gemini | 0 (0%) | 13 | 37 |
| mistral | 44 (88%) | 0 | 6 |
| cohere | 13 (26%) | 0 | 37 |


OpenAI is the firm, best-documented case: strict Structured Outputs **require** `additionalProperties:false` and **every** property listed in `required` on every object. The 6 schemas that pass OpenAI were verified to genuinely carry both. Mistral's numbers use schemafit's *more conservative* rule (its own finding text notes it is example-derived — Mistral's docs show `additionalProperties:false` but don't prose-mandate it), so treat Mistral as 'likely-reject' rather than 'documented-reject'. Gemini's hits are warnings ($ref recursion / anyOf), not hard errors.

## Portability — how many providers each schema breaks on

| Errors on… | # schemas | % |
|---|---|---|
| 0 provider(s) | 6 | 12% |
| 2 provider(s) | 30 | 60% |
| 3 provider(s) | 9 | 18% |
| 4 provider(s) | 5 | 10% |


## Most common violations (error severity)

| Keyword | Flags |
|---|---|
| additionalProperties | 134 |
| required | 12 |
| default | 11 |
| minLength | 6 |
| minimum | 6 |
| maximum | 4 |
| height | 4 |
| kind | 4 |



| Rule | Flags |
|---|---|
| openai-additional-properties-false | 67 |
| mistral-additional-properties-false | 67 |
| openai-all-properties-required | 38 |
| mistral-all-properties-required | 38 |
| cohere-object-min-required | 12 |
| openai-no-default | 11 |
| anthropic-no-minLength | 3 |
| anthropic-no-minimum | 3 |


## A few real examples

- `fw_instructor_validated_product.json` — errors on **openai** (additionalProperties), **anthropic** (exclusiveMinimum, maxLength, minLength, minimum), **mistral** (additionalProperties), **cohere** (maxLength, minLength, minimum)  
  ↳ source: https://raw.githubusercontent.com/567-labs/instructor/main/docs/concepts/validation.md
- `fw_instructor_validated_user.json` — errors on **openai** (additionalProperties), **anthropic** (maximum, minLength, minimum), **mistral** (additionalProperties), **cohere** (maximum, minLength, minimum)  
  ↳ source: https://raw.githubusercontent.com/567-labs/instructor/main/docs/concepts/validation.md
- `fw_langchain_pattern_anyof.json` — errors on **openai** (additionalProperties, endDate, kind, payload, startDate), **anthropic** (pattern), **mistral** (additionalProperties, endDate, kind, payload, startDate), **cohere** (required); warns on gemini  
  ↳ source: https://raw.githubusercontent.com/langchain-ai/langchain/master/libs/core/tests/unit_tests/utils/test_json_schema.py
- `fw_pydanticai_sql_result_union.json` — errors on **openai** (additionalProperties, default, explanation), **anthropic** (minLength), **mistral** (additionalProperties, explanation), **cohere** (minLength, type); warns on gemini  
  ↳ source: https://raw.githubusercontent.com/pydantic/pydantic-ai/main/examples/pydantic_ai_examples/sql_gen.py
- `oa_anth_save_note.json` — errors on **openai** (additionalProperties, default, is_public, priority), **anthropic** (format, maximum, minimum), **mistral** (additionalProperties, is_public, priority), **cohere** (maximum, minimum)  
  ↳ source: https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/tool_use/tool_use_with_pydantic.ipynb
- `fw_langchain_nested_refs.json` — errors on **openai** (additionalProperties, age, first_name, height, other), **mistral** (additionalProperties, age, first_name, height, other), **cohere** (required); warns on gemini  
  ↳ source: https://raw.githubusercontent.com/langchain-ai/langchain/master/libs/core/tests/unit_tests/utils/test_json_schema.py

## Method & honesty notes

- **Real, not synthetic.** Every schema was transcribed verbatim from a public source (raw URL recorded per schema in the manifests). 3 collectors gathered them; a sample was spot-checked back against live source.
- **One command per schema:** `schemafit lint <file> --provider openai,anthropic,gemini,mistral,cohere --format json`. Static, offline — no provider calls.
- **schemafit's rules are its encoding of each provider's documented constraint surface**, grounded in cited provider docs/issues (each finding carries a `doc_url`). Where a rule is a conservative reading (Mistral additionalProperties), the finding text says so — and this report flags it.
- **Corpus is provider-mixed by design** (cookbook examples skew toward already-strict OpenAI schemas; MCP/framework schemas skew permissive), which is why the headline number is a floor, not a cherry-pick.

*Reproduce: `pip install schemafit==0.5.0`, then run the command above over your own tool/output schemas.*
