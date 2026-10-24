# Show HN draft: schemafit

Status: DRAFT for Dan to edit and post. Planned for Wed Oct 28, 2026.
Not posted anywhere.

## Title (chosen; 76 chars, HN limit is 80)

Show HN: Schemafit, a linter for JSON schemas that LLM providers will reject

Alternates (not used):

- Show HN: Schemafit, catch LLM schema 400s in CI before they hit production (74)
- Show HN: Lint your LLM tool schemas against OpenAI, Anthropic, Gemini rules (75)

URL: https://github.com/OrionArchitekton/schemafit

## First comment

I kept hitting the same bug: a JSON schema for structured output or a tool
definition works on one provider and returns a 400 on another. OpenAI strict
mode wants `additionalProperties: false` and every property in `required`.
Anthropic's structured-output path rejects `minimum`, `pattern`, `format`, and
other validation keywords. Cohere rejects `oneOf` and length limits. The error
usually tells you the request failed, not which keyword caused it.

schemafit is a small CLI that checks a schema against each provider's documented
rules before you ship it. It prints the JSON Pointer path, the keyword, and a
link to the doc or issue the rule came from, and exits 1 so CI fails. It is
offline, needs no API key, and has no runtime dependencies. It also does SARIF
output, a GitHub Action, a pre-commit hook, and a best-effort `repair` command.

Try it without installing anything (needs uv):

    echo '{"type":"object","additionalProperties":false,"properties":{"sku":{"type":"string","pattern":"^[A-Z]{3}-[0-9]{4}$"},"qty":{"type":"integer","minimum":1}},"required":["sku","qty"]}' | uvx schemafit lint - --provider openai,anthropic,gemini,mistral,cohere

That schema passes OpenAI, Gemini, and Mistral, and fails Anthropic and Cohere.

I ran it over 50 public schemas from cookbooks, agent frameworks, and MCP
servers. 44 would fail at least one provider, but most of that is OpenAI strict
mode: those 44 are exactly the schemas strict mode rejects, mostly for a missing
`additionalProperties: false`.
If you don't use strict mode, the numbers that matter are Anthropic (6 of 50)
and Cohere (13 of 50). The corpus and script are in `benchmarks/`.

Limits I know about: the rules are static, so they lag when a provider changes
its docs. Gemini's rules are warnings only, because its schema support changed
several times in the last year. The Mistral pack is thin because Mistral's docs
don't list unsupported keywords. There is an opt-in `--live-verify` mode that
sends a real probe when you have a key, and flags when a provider rejects
something the static rules passed.

I'd like to hear about provider rules I've missed or got wrong, especially for
Bedrock and Vertex, which aren't covered yet.

## Pre-post checklist

- [ ] v0.5.1 tagged and on PyPI, so the README demo output matches `uvx schemafit`
- [ ] Re-run the demo command above from a clean shell on post day
- [ ] Re-check the Anthropic and Gemini rules against current provider docs
- [ ] Be around for the first two hours to answer comments
