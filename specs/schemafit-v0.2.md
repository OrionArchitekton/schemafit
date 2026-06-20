# schemafit v0.2 MAP — 2026-06-20 (SCOPE → CARVE → MAP → GATE)

Status: STEP 1 of 2 MAP. Stop at gate. This run is **READ-ONLY** except this MAP file (the sole intended mutation). STEP 2 (`~/.orion/goal-prompts/schemafit-v02-implement-20260620.md`) fires only after Dan approves this MAP.
Verification window: 2026-06-20 ~19:42Z–20:10Z UTC (live re-ground of `~/src/schemafit` + adversarially-verified landscape re-scan). The MAP path did **not** pre-exist (no-prior-v0.2-artifact attested below); this run created it.

**Recommendation (one line):** Approve the **TIGHT** v0.2 cut for `schemafit` — ship a **SARIF output reporter** (`--format sarif`, CI/code-scanning native, no dep) + **two new static provider rule packs (Mistral, Cohere)**, doubling the provider matrix 3→5. This deepens the static, local-first, declarative-rule-pack multi-provider linter wedge — which the landscape re-scan confirms is **still open** — while staying network-free, core dep-free, and hermetically one-run-provable. Defer `--live-verify` (the central-fork AMBITIOUS arm), rule-pack drift detection, Bedrock/Vertex packs, and Pydantic source-model to v0.3. Keep the LOCKED-OUT set (hosted SaaS service, browser UI/dashboard, runtime validation proxy/gateway) untouched.

---

## OPERATOR GATE DECISION (2026-06-20) — **AMBITIOUS** (AUTHORITATIVE; supersedes the TIGHT recommendation)

Dan chose the **AMBITIOUS** central-fork arm at the gate. This section is the authority for STEP-2 and **overrides** the §Central-Fork-Resolution TIGHT recommendation. Approved v0.2 IN cut:

- **IN 1 (spine): `--live-verify`** — an OPT-IN, env-key-gated, mock/fixture-proven, **never-default-CI** mode that calls each provider (via a mockable client) to CONFIRM acceptance, turning "the docs forbid this" into "the provider actually rejected/accepted it."
- **IN 2 (static companion): SARIF output reporter** (`--format sarif`) — exactly as specified in §v0.2 IN-Set Design → "IN 1 (spine): SARIF output reporter".
- **DEFER to v0.3 (moved from the TIGHT IN):** Mistral/Cohere packs (C2), rule-pack drift (C3), Bedrock/Vertex (C6), Pydantic (C5), JS-port/Zod (C7/C8). The packs move IN→DEFER under this cut to keep the run convergent — live-verify is the real work.
- **Publish posture:** HANDOFF (Dan pushes the irreversible `v0.2.0` tag). **LOCKED-OUT** untouched.
- **Operator-acknowledged risk (from W1 + §Central-Fork-Resolution):** AMBITIOUS steps toward the occupied runtime lane (keeps-static 2/5) and its mock/key/CI-gating plumbing is the harder STEP-2; accepted.

### `--live-verify` IN-design (the AMBITIOUS spine)
- **CLI surface:** add `--live-verify` to `p_lint` (mirror the `--strict` opt-in at `cli.py:166`); OFF by default, never implied. Branch in `cmd_lint` (`cli.py:52-78`).
- **Module:** new `schemafit/live.py` with a provider-client abstraction whose **default is a MOCK/recorded client (no network)** — used by tests + the docker proof; a real client is used ONLY when `--live-verify` is passed AND an env key is present. `model.py:25-34` `Finding` gains `confirmed_by_provider: bool | None`.
- **Dep posture:** core `dependencies=[]` stays. Real provider calls use stdlib HTTP or a provider SDK under `[project.optional-dependencies]` (`live`); the core + default path make **NO** network call.
- **Safety (admissibility):** opt-in flag (never default), env-key gate (no key in CI/transcript), mock/recorded response for the test + docker proof, **fail-closed on a provider rejection**, non-determinism handled.
- **Test plan:** (a) `--live-verify` w/ the MOCK client confirms a known-good schema (`confirmed_by_provider=True`) and **FAILS-CLOSED** on a mock provider-rejection; (b) WITHOUT `--live-verify` the static path + exit codes are unchanged; (c) NO real key read in CI; (d) the two existing CI exit-code contracts still hold; (e) SARIF tests per IN 1.
- **Docker proof (mock, no network/key/port):** `docker run --rm -i schemafit:v02 lint - --provider openai --live-verify < fixtures/portable-good.json` (MOCK client) → output shows `confirmed_by_provider`; a mock-rejection fixture → fail-closed exit 1. Plus the SARIF proof from IN 1.
- **Version/docs:** bump `0.1.0→0.2.0`; README `--live-verify` section (opt-in, env key, mock default) + SARIF; CHANGELOG `0.2.0`.

IN_DESIGN_ROW: item=live-verify | cli=lint --live-verify (opt-in like --strict, cli.py:166) | module=schemafit/live.py(mock-default client)+model.py confirmed_by_provider | dep_posture=core-none;real-calls=optional-extra[live] | tests=mock-confirms-good+fail-closed-on-mock-rejection+no-flag-unchanged+no-key-in-CI | docker_proof=lint --live-verify with MOCK client shows confirmed_by_provider + mock-rejection fail-closed; no network/key | version_docs=0.2.0 README-live-verify+sarif CHANGELOG

**STEP-2 builds: IN 1 (`--live-verify`, mock-default) + IN 2 (SARIF reporter). Defers the packs. The §STEP-2 Prep Appendix fire line's "TIGHT" precondition is superseded by this AMBITIOUS cut — branch slug `codex/v0.2-live-verify-sarif-20260620`.**

---

## Severity findings

## Severity findings

- **BLOCKING:** none. No live state contradicts any settled/locked value. The v0.2 worktree/branch/tag are expected-absent (research-before-build), not a contradiction.
- **WARNING (W1):** Landscape verdict is **WEDGE-OPEN at *medium* confidence**, not high. Absence on PyPI/GitHub cannot be proven exhaustively, and LiteLLM already holds the per-provider constraint *knowledge* in its model-params map — so the moat is **packaging (offline rule-pack + CI/pre-commit/SARIF UX), not novel knowledge**. A single-provider OpenAI sanitizer extending to multi-provider + static CLI is the most likely fast-follow. This argues *for* shipping the convergent static cut now, not for over-investing in a wide v0.2.
- **WARNING (W2):** New provider packs (Mistral, Cohere) MUST have every rule grounded in a **primary provider source** at build time. Any constraint that cannot be primary-sourced is `confidence:none` → **dropped, never invented** (no-invented-demand). A pack rule that needs a `kind` the linter doesn't dispatch requires an `apply_rule` clause **and** a `repair` strategy + tests (see Extension-Point Map).
- **INFO:** Two **recon-shape corrections** confirmed against live code (do not block; STEP-2 must honor them): (1) repair dispatches on `Finding.auto_repair`, **not** on rule `kind`; (2) the rule JSON shape carries a `context` field (for `forbidden_keyword_in_context`), which recon's 8-field list omitted. Details in the Settled-Decision/EVIDENCE notes.
- **INFO:** `confidence:none` audit — none used as load-bearing evidence in this MAP. Every IN/DEFER candidate is backed by the published roadmap (`README.md:123-126`), a real in-code attachment point, or a cited live source. The drift/live-verify *external need* leans on cited provider-divergence evidence, flagged where confidence is medium.

---

## Extension-Point Map

Fresh local state (turn-1 baseline, re-verified this run): `~/src/schemafit` is on `main` at `7fcefd47e5c70517fcd5fccb0dc7d5844140da7e`; local `HEAD` == `origin/main` (fetched, parity); public repo `OrionArchitekton/schemafit` (PUBLIC, MIT); only tag is `v0.1.0`; `pyproject.toml` version `0.1.0`; core `dependencies = []`; **0 open issues / 0 open PRs**; no v0.2 worktree/branch/MAP. Linter dispatches exactly **5 rule kinds**; repair dispatches **4 strategies** off `auto_repair`.

| v0.2 candidate | real code attachment point | file:line evidence | v0.2 attachment plan |
|---|---|---|---|
| **SARIF output reporter** (IN) | Reporters live in `report.py` (`format_human`, `format_json`, `format_json_multi`); `cli.py` selects via `--format` choices `("human","json")` and branches in `cmd_lint`. `Finding` fields are the SARIF result source. | `report.py:14,42,46`; `cli.py:165` (`--format` choices) + `cli.py:72-77` (branch); `model.py:25-34` (`Finding`) | IN. Add `format_sarif(results)` + `format_sarif_multi(all_results)` to `report.py` (reuse `_results_payload`/`Finding.to_dict`). Add `"sarif"` to `cli.py:165` choices + a `cmd_lint` branch (`cli.py:72-77`) calling `format_sarif_multi`. Map `rule_id→ruleId`, `severity→level`, `reason→message.text`, `doc_url→helpUri`, `json_pointer→logicalLocation`, `provider→properties`. No dep (hand-emit JSON). |
| **Mistral + Cohere rule packs** (IN) | Packs load lazily+cached from `rules/<provider>.json` via `load_rule_pack`; `PROVIDERS` tuple is the single registry consumed by `cli.py` (`_parse_providers`, `cmd_providers`) and `__init__.py`. | `linter.py:11` (`PROVIDERS`), `linter.py:16-23` (`load_rule_pack`), `linter.py:114` (`pack.get("rules", [])`); `cli.py:42-49,113-116` | IN. Add `"mistral","cohere"` to `PROVIDERS` (`linter.py:11`) + drop `rules/mistral.json`, `rules/cohere.json` beside `openai.json`. Each rule uses the existing JSON shape `{id,kind,keyword[,value][,context],severity,auto_repair,reason,doc_url}`. **Zero engine code** if rules reuse existing kinds; a new `kind` needs an `apply_rule` clause (`linter.py:65-104`) + a `repair` strategy (`repair.py:37-61`) + tests. Every rule primary-sourced (W2). |
| **rule JSON shape / 5 kinds** (reference) | `apply_rule` recognizes exactly: `forbidden_keyword`, `forbidden_keyword_in_context` (uses `context`), `object_requires` (uses `value`), `object_all_properties_required`, `forbidden_additional_properties_schema`; any other raises `ValueError`. | `linter.py:65-104` (kinds), `linter.py:103-104` (guard); `repair.py:37` dispatches on `auto_repair` → `strip`/`set_false`/`fill_required`/`manual` (`repair.py:38-61`) | Reference for IN-pack authoring. Recon CORRECTION: repair keys off `auto_repair`, not `kind`; the shape includes `context` (e.g. `openai.json:37`). |
| **automatic rule-pack drift detection** (DEFER-v0.3) | Packs + their per-rule `doc_url` primary-source links are the only source-of-truth anchors; no drift hook exists. | `linter.py:16-23` (load), `linter.py:11` (registry); `openai.json:13`, `anthropic.json:5` (`doc_url`) | DEFER-v0.3. Natural home: new `drift.py` + a new `cli` subcommand (`cli.py:175-179`). **Requires network at check time** (fetch `doc_url` + diff) → breaks static/network-free convergence; abstention handling makes hermetic one-run proof hard. Pairs naturally with `--live-verify` and a broader pack surface in v0.3. |
| **`--live-verify` opt-in live mode** (DEFER-v0.3 / central-fork AMBITIOUS) | A new `--live-verify` flag mirrors the existing `--strict` opt-in pattern; `Finding`/severity would carry a confirmed-by-provider result. | `cli.py:162-167` (`p_lint`, after `--strict` at `:166`), `cli.py:52-78` (`cmd_lint`); `model.py:25-34` (add `confirmed_by_provider`); `linter.py:124-125` (`has_errors`), `report.py:11` (`_status`) | DEFER-v0.3. Central-fork AMBITIOUS arm. Crosses static→live (keys/network/cost/non-determinism). If ever IN: opt-in, env-key-gated, mock/fixture-proven, never default-CI. See Central-Fork Resolution. |
| **Pydantic source-model auto-fix** (DEFER-v0.3) | Schema ingestion is `_load_schema` (JSON file/stdin → dict); engine is JSON-Schema-native. | `cli.py:35-39` (`_load_schema`), `cli.py:59,86` (feeds `lint_multi`/`repair`); `walk.py:48`, `linter.py:109` | DEFER-v0.3. Attach a model-input mode at the loader (`Model.model_json_schema()` → dict) + a CLI arg. Adds `pydantic` **optional-extra**. Sizeable standalone increment — would crowd v0.2 convergence. |
| Bedrock + Vertex packs (DEFER-v0.3) | Same pack mechanism as Mistral/Cohere. | `linter.py:11`, `rules/` | DEFER-v0.3. **Platform multiplexers** — their "schema constraints" are the underlying model's (Claude-on-Bedrock = Anthropic; Gemini-on-Vertex = Gemini). A clean declarative pack risks conflating/duplicating model rules (invented-demand risk). Model after dedicated-provider pattern + drift land in v0.3. |
| npm/`ajv` JS-port, Zod source-model (DEFER-BIG) | N/A (second ecosystem) | `README.md:124,126` | DEFER-BIG. A whole JS/TS second-ecosystem port; legitimate future direction, far too large for a convergent Python v0.2. Not locked-out. |
| Rebuild v0.1 surface (DROP) | `lint`/`repair`/`providers`/`demo` + the 3 packs already shipped. | `cli.py:162,169,175,178`; `CHANGELOG.md:9-18` | DROP. Do not rebuild; only extend. Anti-regression: all v0.1 tests + the two CI contracts stay green. |

---

## Landscape Re-Scan

Four orthogonal angles, each scanned then **adversarially verified** (try-to-refute, abstention-safe). All four held at **WEDGE-OPEN, medium confidence, refuted=false**. The wedge = *a STATIC, local-first, pip-installable, declarative-rule-pack CLI/CI linter checking JSON-Schema structured-output schemas against MULTIPLE LLM providers' documented constraints, no network at lint time*.

### Angle 1 — multi-provider structured-output CI linter → WEDGE-OPEN (medium)
The 2026 structured-output landscape is uniformly **runtime/generation-time**, not static lint-time:
- **LiteLLM** (`supports_response_schema()`, `get_supported_openai_params()`, `drop_params=True`) encodes per-provider schema-constraint knowledge — *the hardest part to assemble* — but operates inside the **request path** (transform-and-send; raises against a LIVE response). PARTIAL overlap, runtime. https://docs.litellm.ai/docs/completion/drop_params · https://github.com/BerriAI/litellm/issues/6136
- **Instructor / Pydantic-AI / Outlines / Guardrails AI / Prompture** — runtime validation/retry/constrained-decoding over Pydantic/Zod; no static schema-vs-provider lint. https://python.useinstructor.com/
- **GitHub repo search** for the exact wedge returned **zero third-party repos** (the only hit was the project itself, `OrionArchitekton/_schemafit`).
Verify: *"Could not refute… none is a static, no-network, provider-constraint rule-pack CLI/CI linter."* Honest caveat: knowledge already exists inside LiteLLM → defensibility is packaging, not novelty (W1).

### Angle 2 — SARIF-emitting schema/provider validator → WEDGE-OPEN (medium)
- **sourcemeta/jsonschema** (leading JSON-Schema CLI: validate/fmt/lint/bundle, pre-commit/CI) — verified to output **only `--json`/pretty, NO SARIF**, anti-patterns are generic JSON-Schema hygiene with **zero LLM-provider awareness**. https://github.com/sourcemeta/jsonschema/blob/main/docs/lint.markdown
- **claudelint** emits **SARIF v2.1.0** for GitHub code-scanning — but for *Claude Code config* (CLAUDE.md/skills/hooks), not JSON-Schema. Proves the form factor ships. https://claudelint.com/integrations/sarif
- **QWED Protocol Verification** (`pip install qwed`, SARIF→Security tab) — surfaced by the adversarial pass; a **runtime output-instance** AISecOps firewall, **not** a static schema-definition linter; no OpenAI-strict/Gemini-keyword awareness. https://github.com/QWED-AI/qwed-verification
- **check-jsonschema** — static/local/CI/pip CLI + pre-commit, but provider-agnostic (validates data vs schema, not schema vs provider rules). https://github.com/python-jsonschema/check-jsonschema
Verify: *"five independent angles corroborate… no pip-packaged dedicated static multi-provider structured-output schema linter… wedge remains genuinely open."* claudelint + QWED prove SARIF-static-lint ships in the LLM ecosystem but neither aims at multi-provider schema-definition constraints — **strengthens** the SARIF IN.

### Angle 3 — rule-pack drift detector → WEDGE-OPEN (medium)
- **AI Dev Hub Structured Output Validator** — hosted web/REST, validates output *instances* vs draft-07 with OpenAI/Anthropic/MCP presets; **no drift detection, not pip/CLI/CI**. https://aidevhub.io/structured-output-validator/
- Existing tooling clusters into runtime transformers/sanitizers (OpenAI SDK `to_strict_json_schema`, `schemic`, Instructor/LangChain/LiteLLM) and runtime output-instance validators — none is a static declarative-rule-pack linter, **none alerts on drift in documented constraints**.
- Corroborating substrate: providers have **genuinely divergent, version-shifting documented constraints** (Claude strict rejects `min/max`, string-length, recursive, external `$ref`; OpenAI bans `anyOf`, requires `additionalProperties:false`+all-required; Gemini = OpenAPI subset; schemafit's own CHANGELOG records Gemini `anyOf` Jan 2026 / `additionalProperties` Nov 2025). Exactly what a drift detector would watch.
Verify: *"verified-open rather than unverified-abstain… searches genuinely inconclusive for a closing tool."* This validates drift as a real v0.3 candidate (network cost defers it from v0.2).

### Angle 4 — direct schemafit competitor since 2026-06-20 → WEDGE-OPEN (medium)
6 refutation searches (CI linter+SARIF+multi-provider; pip lint CLI; Action/pre-commit; "schema compatibility checker"; OpenAI strict static analysis; declarative rule-pack). Every candidate fell into (1) runtime multi-provider libs/gateways, (2) generic JSON-Schema linters with no provider awareness, or (3) single-provider runtime mutators. *"Could not find any tool occupying the wedge."*

**LANDSCAPE_VERDICT: WEDGE-OPEN | confidence=medium | refuted=false (4/4 angles) | moat=packaging-not-knowledge | nearest_runtime=LiteLLM | nearest_static=sourcemeta/jsonschema(no-provider,no-SARIF) | sarif_precedent=claudelint,QWED(different-subject)**

---

## Candidate Scoreboard

Scores 1–5: **wedge-fit / need-cited / one-run-buildable / keeps-static-local-first**. Verdicts: IN-v0.2 / DEFER-v0.3 / DROP.

| id | candidate | scores (wf/nc/orb/ksl) | need evidence | verdict |
|---|---|---:|---|---|
| C1 | SARIF output reporter | 5/5/5/5 | roadmap `README.md:125`; attach `report.py:42-48`,`cli.py:165`; no JSON-Schema/LLM validator emits SARIF (Angle 2 verified); claudelint/QWED prove form factor | **IN-v0.2** |
| C2 | Mistral + Cohere rule packs | 5/4/4/5 | roadmap `README.md:124`; attach `linter.py:11`+`rules/`; LiteLLM proves per-provider constraint value (Angle 1); divergent documented constraints (Angle 3) | **IN-v0.2** |
| C3 | rule-pack drift detection | 4/4/3/3 | roadmap `README.md:125`; `CHANGELOG.md:29-32` Gemini drift; no detector exists (Angle 3) — but needs network + abstention handling | DEFER-v0.3 |
| C4 | `--live-verify` (central-fork AMBITIOUS) | 3/4/3/2 | roadmap `README.md:123` (first listed); attach `cli.py:162-167`,`model.py:25-34` — but crosses static→live (keys/network) | DEFER-v0.3 |
| C5 | Pydantic source-model auto-fix | 4/4/3/4 | roadmap `README.md:126`; attach `cli.py:35-39` — sizeable; adds `pydantic` optional-extra | DEFER-v0.3 |
| C6 | Bedrock + Vertex packs | 4/3/2/5 | roadmap `README.md:124` — but platform multiplexers; constraints are underlying-model's (invented-demand risk) | DEFER-v0.3 |
| C7 | npm/ajv JS-port | 3/3/1/4 | roadmap `README.md:124` — whole second ecosystem; too big for Python v0.2 | DEFER-v0.3 (BIG) |
| C8 | Zod source-model | 3/2/1/4 | roadmap `README.md:126` — JS ecosystem (pairs with JS port) | DEFER-v0.3 (BIG) |
| C9 | rebuild v0.1 surface | 1/1/5/5 | already shipped `CHANGELOG.md:9-18` | DROP |

SCOREBOARD_ROW: id=C1 | candidate=sarif-output-reporter | wedge_fit=5 | need_cited=5 | one_run_buildable=5 | keeps_static_local_first=5 | need_evidence=roadmap:README.md:125;attach:report.py:42-48,cli.py:165;cited:Angle2-WEDGE-OPEN-no-sarif-llm-validator,claudelint-sarif-2.1.0 | verdict=IN-v0.2 | confidence=verified
SCOREBOARD_ROW: id=C2 | candidate=mistral-cohere-rule-packs | wedge_fit=5 | need_cited=4 | one_run_buildable=4 | keeps_static_local_first=5 | need_evidence=roadmap:README.md:124;attach:linter.py:11,rules/;cited:Angle1-LiteLLM-per-provider-constraints-runtime-only,Angle3-divergent-documented-constraints | verdict=IN-v0.2 | confidence=verified
SCOREBOARD_ROW: id=C3 | candidate=rule-pack-drift-detection | wedge_fit=4 | need_cited=4 | one_run_buildable=3 | keeps_static_local_first=3 | need_evidence=roadmap:README.md:125;in-code:CHANGELOG.md:29-32-gemini-drift;cited:Angle3-no-detector-exists;blocker=needs-network+abstention | verdict=DEFER-v0.3 | confidence=verified
SCOREBOARD_ROW: id=C4 | candidate=live-verify | wedge_fit=3 | need_cited=4 | one_run_buildable=3 | keeps_static_local_first=2 | need_evidence=roadmap:README.md:123;attach:cli.py:162-167,model.py:25-34;blocker=crosses-static-to-live-keys-network | verdict=DEFER-v0.3 | confidence=verified
SCOREBOARD_ROW: id=C5 | candidate=pydantic-source-model | wedge_fit=4 | need_cited=4 | one_run_buildable=3 | keeps_static_local_first=4 | need_evidence=roadmap:README.md:126;attach:cli.py:35-39;cost=pydantic-optional-extra+sizeable | verdict=DEFER-v0.3 | confidence=verified
SCOREBOARD_ROW: id=C6 | candidate=bedrock-vertex-packs | wedge_fit=4 | need_cited=3 | one_run_buildable=2 | keeps_static_local_first=5 | need_evidence=roadmap:README.md:124;risk=platform-multiplexer-constraints-are-underlying-model-invented-demand | verdict=DEFER-v0.3 | confidence=verified
SCOREBOARD_ROW: id=C7 | candidate=npm-ajv-js-port | wedge_fit=3 | need_cited=3 | one_run_buildable=1 | keeps_static_local_first=4 | need_evidence=roadmap:README.md:124;blocker=whole-second-ecosystem | verdict=DEFER-v0.3-BIG | confidence=verified
SCOREBOARD_ROW: id=C8 | candidate=zod-source-model | wedge_fit=3 | need_cited=2 | one_run_buildable=1 | keeps_static_local_first=4 | need_evidence=roadmap:README.md:126;blocker=js-ecosystem-pairs-with-js-port | verdict=DEFER-v0.3-BIG | confidence=verified
SCOREBOARD_ROW: id=C9 | candidate=rebuild-v0.1-surface | wedge_fit=1 | need_cited=1 | one_run_buildable=5 | keeps_static_local_first=5 | need_evidence=already-shipped:CHANGELOG.md:9-18 | verdict=DROP | confidence=verified

---

## Central-Fork Resolution

**Recommendation: TIGHT (static-only deepening).** Ship C1 (SARIF) + C2 (Mistral/Cohere packs); **defer `--live-verify` to v0.3**.

Rationale:
1. **Convergence/provability.** TIGHT is **network-free**, so the entire v0.2 — including the `docker run` proof — is **hermetic and one-run-provable**. AMBITIOUS `--live-verify` requires a mock/fixture provider harness, opt-in/key-gating plumbing, and a fail-closed provider-rejection test — real work that risks non-convergence in one autonomous STEP-2 run.
2. **Wedge-fit / identity.** The landscape re-scan shows the **runtime lane is already occupied** (LiteLLM, Instructor, Mastra). `--live-verify` steps *toward* that contested territory and *away from* the static local-first identity (keeps-static score 2/5). The **static multi-provider + SARIF lane is exactly what is open** — TIGHT plants the flag there (wedge-fit 5/5).
3. **Sequencing.** `--live-verify` pairs naturally with **drift detection** (both network-touching, both confirm against the live provider) — they belong together in a v0.3 "live" increment, after the static surface is broad. Shipping live-verify alone in v0.2 splits that theme.
4. **Risk posture.** W1 (thin, packaging-based moat) argues for shipping the convergent static cut *now* and iterating, not for a wide/ambitious v0.2.

**Alternative kept for the gate (AMBITIOUS):** ship `--live-verify` as an OPT-IN, env-key-gated, mock/fixture-proven, never-default-CI mode that calls each provider (mockable client) to confirm acceptance — paired with a smaller static item (e.g. SARIF only, deferring the new packs). Turns "the docs forbid this" into "the provider actually rejected/accepted it." Admissible only with: opt-in flag (never implied), env-key gate, no real key in CI/transcript, recorded/mock response for the docker+test proof, fail-closed on provider rejection, core `dependencies=[]` preserved (stdlib HTTP or a provider SDK as optional-extra).

CENTRAL_FORK_RESOLUTION: recommendation=TIGHT-static-only | in=sarif-reporter+mistral-cohere-packs | alternative=AMBITIOUS-live-verify-opt-in-mock-proven | rationale=network-free-hermetic-one-run-proof+static-wedge-is-the-open-lane+live-verify-pairs-with-drift-in-v0.3 | locked_out_untouched=true | core_dependencies=keep-[]

---

## v0.2 IN-Set Design

Shared constraints (both items): core `pyproject.toml` `dependencies = []` stays true; **no new dep** is expected (SARIF hand-emitted; packs are declarative JSON); if an implementation unexpectedly needs one it goes under `[project.optional-dependencies]` only and is justified in the PR. All v0.1 commands (`lint`/`repair`/`providers`/`demo`), the 3 existing packs, `walk` traversal, the v0.1 hardening fixes, and the **two CI exit-code contracts** stay green. The `docker run` proof must exercise a NEW v0.2 capability (not the v0.1 demo).

### IN 1 (spine): SARIF output reporter

Purpose: emit SARIF 2.1.0 so `schemafit lint` results drop straight into **GitHub code-scanning / the Security tab** — the CI-native surface no LLM-provider schema linter currently fills.

Design:
- **CLI surface:** add `"sarif"` to `p_lint --format` choices (`cli.py:165` → `choices=("human","json","sarif")`); branch in `cmd_lint` (`cli.py:72-77`) to print `report.format_sarif_multi(all_results)` when `args.format=="sarif"`. Exit-code unchanged (still 1 on errors; SARIF is emitted to stdout regardless, so code-scanning gets the artifact even on a failing gate). `repair` keeps no `--format` (`cli.py:169-173`).
- **Module:** `schemafit/report.py` — add `format_sarif(results)` + `format_sarif_multi(all_results)` reusing `_results_payload`/`Finding.to_dict`.
- **SARIF mapping (2.1.0):** top-level `{"$schema": "...sarif-2.1.0...", "version":"2.1.0", "runs":[{...}]}`; `tool.driver.name="schemafit"`, `.version=__version__`, `.rules[]` = de-duped fired rule_ids with `helpUri=doc_url`; each finding → `results[]` with `ruleId=rule_id`, `level` ∈ {`error`,`warning`} (map `severity`), `message.text=reason`, `locations[].logicalLocations[].fullyQualifiedName=json_pointer`, `properties={provider, kind, keyword}`; the linted file path → `physicalLocation.artifactLocation.uri`.
- **Dep posture:** core-none (stdlib `json`).
- **Test plan:** `tests/test_report_sarif.py` (+ a `test_cli.py` format case): (a) output parses as JSON and has `version=="2.1.0"` + `$schema` + `runs[0].tool.driver.name=="schemafit"`; (b) a known-bad schema yields ≥1 `result` with `level=="error"`, correct `ruleId`, and `helpUri`; (c) **NEW FAILURE MODE** — a clean schema yields a *valid* SARIF doc with `results: []` (must not crash, must not omit the `run`); (d) `--format sarif` still returns exit 1 on errors / 0 on clean (exit-code contract preserved); (e) `level` correctly downgrades a Gemini warning to `"warning"`.
- **`docker run` smoke-proof (fixture-based, no network/port):** `docker run --rm -i schemafit:v02 lint - --provider anthropic --format sarif < fixtures/anthropic-bad.json` → stdout is SARIF JSON. **Proof lines to grep:** `"version": "2.1.0"`, `"driver"` with `"name": "schemafit"`, and a `"ruleId"` matching an anthropic rule (e.g. `anthropic-*`).
- **Version/docs delta:** bump `0.1.0→0.2.0`; README: add `--format sarif` to usage + a "GitHub code-scanning" subsection; CHANGELOG `0.2.0` Added: "SARIF 2.1.0 output (`--format sarif`) for GitHub code-scanning."

IN_DESIGN_ROW: item=sarif-output-reporter | cli=lint --format sarif (add to choices cli.py:165 + branch cli.py:72-77) | module=schemafit/report.py:format_sarif+format_sarif_multi | dep_posture=core-none | tests=tests/test_report_sarif.py valid-2.1.0+bad-schema-error-result+clean-empty-results-NEWFAILMODE+exit-code-preserved+warning-level | docker_proof=docker run -i schemafit:v02 lint - --provider anthropic --format sarif < fixtures/anthropic-bad.json prints version 2.1.0 + driver schemafit + a ruleId | version_docs=0.2.0 README-code-scanning CHANGELOG

### IN 2 (spine): Mistral + Cohere rule packs

Purpose: extend the static provider matrix 3→5 — the core multi-provider differentiator nobody packages statically — with two **dedicated** (non-multiplexer) providers whose structured-output constraints are documented and primary-sourceable.

Design:
- **CLI surface:** none new — `providers` (`cli.py:113-116`) auto-lists from `PROVIDERS`; `lint`/`repair` accept the new names via `_parse_providers` (`cli.py:42-49`).
- **Module / data:** add `"mistral","cohere"` to `PROVIDERS` (`linter.py:11`); add `schemafit/rules/mistral.json`, `schemafit/rules/cohere.json` (root `{provider, doc, rules:[...]}`). Add to `pyproject.toml` package-data (already globs `rules/*.json` at `pyproject.toml:40` — no change needed). Each rule uses the existing shape + an existing `kind` where possible; if a provider's documented constraint needs a new `kind`, add the `apply_rule` clause (`linter.py:65-104`) **and** wire its `auto_repair` to an existing strategy or add a `repair.py` branch (`repair.py:37-61`) — with a test for each.
- **Rule grounding (W2 — STEP-2 obligation):** every rule's `doc_url` MUST be a primary provider source; any constraint that cannot be primary-sourced is **dropped, not invented** (`confidence:none` flagged in the PR). Severity follows the v0.1 convention: hard provider-400 constraints = `error`; version/portability cautions = `warning` (gate with `--strict`).
- **Dep posture:** core-none (declarative JSON).
- **Test plan:** extend `tests/test_lint.py`: each new pack **catches** a schema violating its documented constraint (reproduce the real 400) and **passes** `portable-good.json`; `tests/test_cli.py` — `providers` lists all 5. **NEW FAILURE MODE** — a new fixture (e.g. `fixtures/mistral-bad.json`) FAILS under `--provider mistral` (exit 1) while `portable-good.json` PASSES under all 5. If a new `kind`/`auto_repair` is added, a `test_repair.py` case proves the repair path.
- **`docker run` smoke-proof (fixture-based, no network/port):** `docker run --rm schemafit:v02 providers` lists `mistral`+`cohere`; `docker run --rm -i schemafit:v02 lint - --provider mistral < fixtures/mistral-bad.json` exits 1 with a `mistral-*` finding. **Proof lines:** `providers` output includes `mistral` and `cohere`; a `[mistral] FAIL` line (or SARIF `ruleId` `mistral-*`) on the bad fixture.
- **CI contract delta:** extend the second (PASS) contract to `--provider openai,anthropic,gemini,mistral,cohere` (proves new packs don't false-positive on clean schemas); keep the first (anthropic-bad FAIL) contract. (ci.yml is in-repo; editing it is in-scope for STEP-2.)
- **Version/docs delta:** bump `0.1.0→0.2.0`; README provider list 3→5; CHANGELOG `0.2.0` Added: "Mistral and Cohere provider rule packs (provider matrix 3→5), each rule primary-sourced."

IN_DESIGN_ROW: item=mistral-cohere-rule-packs | cli=none-new(providers auto-lists PROVIDERS) | module=linter.py:11 PROVIDERS+=mistral,cohere; rules/mistral.json+rules/cohere.json | dep_posture=core-none | tests=tests/test_lint.py new-pack-catches-bad+passes-portable-good; test_cli.py providers-lists-5; NEWFAILMODE fixtures/mistral-bad.json FAILs+portable-good PASSes-all-5 | docker_proof=docker run schemafit:v02 providers lists mistral+cohere; lint - --provider mistral < fixtures/mistral-bad.json exits 1 with mistral-* | version_docs=0.2.0 README-providers-3to5 CHANGELOG; ci.yml PASS-contract extended to 5 providers

---

## DEFER-to-v0.3 and LOCKED-OUT

### DEFER-to-v0.3 (the explicit residue — seeds the next harness fire)

| item | reason |
|---|---|
| `--live-verify` (AMBITIOUS) | Central-fork alternative. Crosses static→live (keys/network/cost/non-determinism). Pair with drift in a v0.3 "live confirmation" increment; needs opt-in+key-gate+mock-proof+never-default-CI. |
| rule-pack drift detection | Needs network at check time + abstention handling → not hermetically one-run-provable in v0.3-style scope; pairs with `--live-verify`. Strong roadmap+CHANGELOG evidence. |
| Bedrock + Vertex packs | Platform multiplexers; constraints are the underlying model's — model after the dedicated-provider pattern + drift, to avoid conflated/invented rules. |
| Pydantic source-model auto-fix | Sizeable; adds `pydantic` optional-extra; clean standalone increment that would crowd v0.2 convergence. |
| npm/ajv JS-port, Zod source-model (BIG) | Whole second (JS/TS) ecosystem; far beyond a convergent Python v0.2. Not locked-out. |

DEFER_ROW: item=live-verify | verdict=DEFER-v0.3 | reason=central-fork-AMBITIOUS-network+keys-pairs-with-drift
DEFER_ROW: item=rule-pack-drift-detection | verdict=DEFER-v0.3 | reason=needs-network+abstention-not-hermetic-one-run
DEFER_ROW: item=bedrock-vertex-packs | verdict=DEFER-v0.3 | reason=platform-multiplexer-constraints-are-underlying-model
DEFER_ROW: item=pydantic-source-model | verdict=DEFER-v0.3 | reason=sizeable+pydantic-extra-would-crowd-convergence
DEFER_ROW: item=npm-ajv-js-port-and-zod | verdict=DEFER-v0.3-BIG | reason=whole-second-js-ecosystem

### LOCKED-OUT (asserted-excluded — NOT re-gated, NOT proposed)

| locked-out item | one-line reason |
|---|---|
| hosted SaaS linter service | Breaks the static, local-first, CLI/CI identity; introduces a hosted runtime. |
| browser UI / dashboard | Frontend/admin surface; drifts from CLI/CI-proof local-first identity. |
| runtime validation proxy/gateway | That is LiteLLM/Mastra's lane (runtime request-path); breaks static-by-default identity. |

LOCKED_OUT_ROW: item=hosted-saas-linter-service | status=asserted-excluded | reason=hosted-runtime-breaks-static-local-first
LOCKED_OUT_ROW: item=browser-ui-dashboard | status=asserted-excluded | reason=frontend-surface-not-cli-ci-proof
LOCKED_OUT_ROW: item=runtime-validation-proxy-gateway | status=asserted-excluded | reason=runtime-request-path-litellm-mastra-lane

---

## Settled-Decision EVIDENCE Table (SD1–SD5)

Confirm-against-live = silent evidence (NOT a Dan-facing re-decision). An expected-absent probe (v0.2 worktree) is `unverifiable-pending`, not a contradiction.

| SD | locked value | fresh confirmation probe | status |
|---|---|---|---|
| SD1 | Extend existing repo `~/src/schemafit` from a worktree off `origin/main` (branch `codex/v0.2-<slug>-20260620`); bump 0.1.0→0.2.0. NOT a new repo. | `HEAD`==`origin/main`==`7fcefd4` (fetched, parity); only tag `v0.1.0`; only branch `main`; `git worktree list` shows just the canonical; `pyproject.toml:7` version `0.1.0`. v0.2 worktree/branch/MAP absent. | confirmed-against-live; worktree=unverifiable-pending (expected-absent) |
| SD2 | Static local-first: core `dependencies=[]`; no hosted service; static-by-default; new deps optional-extras only. | `pyproject.toml:23` `dependencies = []`; only extra `[dev]` (`:29-30`); `Dockerfile:12-13` CLI entrypoint, no `EXPOSE`/port; `CHANGELOG.md:37-38` "Zero runtime dependencies (stdlib-only lint path)". | confirmed-against-live |
| SD3 | v0.2 DEEPENS the static wedge; LOCKED-OUT = hosted SaaS / browser UI / runtime proxy-gateway; DEFER = npm/ajv, `--live-verify`, Zod. | `README.md:123-126` roadmap matches; this MAP asserts the LOCKED-OUT exclusions and selects only static IN items. | confirmed-against-live |
| SD4 | Fuller-but-convergent v0.2: buildable+provable (tests + docker run + CI contracts) in ONE STEP-2 run; explicit DEFER list above the line. | IN set = 2 bounded items, both network-free with CLI/module/tests/docker-proof; DEFER-v0.3 + LOCKED-OUT explicit. | confirmed-against-live (scope ceiling — design-level) |
| SD5 | Publish posture decided at gate; default HANDOFF (tag→PyPI IRREVERSIBLE); identity `Dan Mercede <dan@danmercede.com>`. | `release.yml:3-25` `push: tags [v*]` → PyPI Trusted Publishing (`environment: pypi`, `id-token: write`, no stored token) + GHCR; `pyproject.toml:12` authors = `Dan Mercede <dan@danmercede.com>`; global git email is OAC (leak risk → local override required). | confirmed-against-live |

SETTLED_DECISION_ROW: SD1 | status=confirmed-against-live;worktree=unverifiable-pending-expected-absent | probe=HEAD==origin/main==7fcefd4;only-tag-v0.1.0;only-branch-main;pyproject-0.1.0;no-v0.2-worktree
SETTLED_DECISION_ROW: SD2 | status=confirmed-against-live | probe=pyproject:23-dependencies-empty;only-[dev]-extra;Dockerfile-cli-no-port;CHANGELOG-zero-runtime-deps
SETTLED_DECISION_ROW: SD3 | status=confirmed-against-live | probe=README:123-126-roadmap;MAP-asserts-locked-out;IN-items-static-only
SETTLED_DECISION_ROW: SD4 | status=confirmed-against-live | probe=2-bounded-network-free-IN-items-with-tests+docker-proof;explicit-defer+locked-out
SETTLED_DECISION_ROW: SD5 | status=confirmed-against-live | probe=release.yml-tags-v*-pypi-trusted-publishing+ghcr;pyproject-authors-dan@danmercede.com;global-email-OAC-leak

---

## Publish-Posture Recommendation (SD5)

**Recommended posture: HANDOFF** (mirror the v0.1 release).

- Worktree: `~/.worktrees/schemafit-v02`. Branch: `codex/v0.2-sarif-providers-20260620`. PR target: `OrionArchitekton/schemafit` `main`.
- Identity: `Dan Mercede <dan@danmercede.com>`, set **locally in the worktree before the first commit** (global = OAC email, would leak); **no Claude co-author trailer**.
- Version: bump `0.1.0→0.2.0`.
- **Release act (IRREVERSIBLE):** after Dan reviews CI-green + the built artifact, pushing tag **`v0.2.0`** triggers `release.yml` → **PyPI Trusted Publishing** (auto-publish, *no re-upload possible*) + GHCR image. The tag **is** the publish act; there is no separate publish dry-run.
- **Fail-closed (absolute):** never tag until CI is green on `main` AND the docker-run proof passed. If `v0.2.0` already exists on PyPI/as a tag → **HALT** (do not overwrite a published version). Never force-push.
- **Open fork:** who pushes the tag — **Dan** (default), or the STEP-2 run **only if Dan explicitly approves autonomous tag** at this gate.

---

## Read-Before-Approving Synthesis

**The arc.** schemafit v0.1.0 shipped a static, stdlib-only, declarative-rule-pack CLI that lints JSON-Schema structured-output schemas against OpenAI/Anthropic/Gemini documented constraints, with `repair`, JSON/human reporters, a Docker image, a GitHub Action, and a tag→PyPI release. v0.2 deepens that exact wedge. The landscape re-scan (4 angles, adversarially verified, all WEDGE-OPEN) confirms the lane is open: the runtime lane is taken (LiteLLM/Instructor/Mastra), generic static linters carry no provider awareness (sourcemeta/check-jsonschema), and SARIF-in-CI ships for *other* subjects (claudelint/QWED) — nobody emits SARIF for multi-provider structured-output schema constraints.

**The central-fork close call.** TIGHT vs AMBITIOUS is genuinely close on *value* — `--live-verify`'s ground-truth confirmation is compelling. It loses on *fit and convergence*: it steps toward the occupied runtime lane (keeps-static 2/5), and its mock/key/CI-gating plumbing risks a non-convergent STEP-2 run. TIGHT keeps the whole increment hermetic and lands the static+SARIF flag first; live-verify + drift form a coherent v0.3 "live confirmation" pair. Recommend TIGHT; AMBITIOUS preserved as the gate alternative.

**Candidate drops + why.** Bedrock/Vertex deferred (platform multiplexers → invented-rule risk). Drift deferred (network + abstention → not hermetic). Pydantic deferred (sizeable + adds an extra). JS-port/Zod deferred-BIG (second ecosystem). v0.1 rebuild dropped. The honest risk (W1): the moat is packaging, not knowledge — which is *why* shipping the convergent static cut now and iterating beats a wide v0.2.

---

## STEP-2 Prep Appendix

Consistency check: the staged STEP-2 implement prompt (`~/.orion/goal-prompts/schemafit-v02-implement-20260620.md`) is **generic across cut-lines** (it explicitly handles SARIF / new provider packs / drift / `--live-verify`) and is **consistent with this TIGHT recommendation** — no refinement required beyond filling the `<slug>` = `sarif-providers`. Its SPINE-FIRST rule, dep-free/identity/CI/docker contracts, and fail-closed release posture all match this MAP.

**Worktree (off origin/main, local identity before first commit):**
```bash
git -C ~/src/schemafit fetch origin main --tags
git worktree add ~/.worktrees/schemafit-v02 -b codex/v0.2-sarif-providers-20260620 origin/main
cd ~/.worktrees/schemafit-v02
git config user.name "Dan Mercede"
git config user.email "dan@danmercede.com"
```

**Modules/CLI/packs to add/update:**
- `schemafit/report.py`: add `format_sarif` + `format_sarif_multi`.
- `schemafit/cli.py`: add `"sarif"` to `--format` choices (`:165`) + a `cmd_lint` branch (`:72-77`).
- `schemafit/linter.py`: `PROVIDERS += ("mistral","cohere")` (`:11`). Add an `apply_rule` clause + `repair` strategy + test **only if** a new pack needs a new `kind`.
- `schemafit/rules/mistral.json`, `schemafit/rules/cohere.json` (primary-sourced rules; drop un-sourceable constraints).
- `tests/test_report_sarif.py` (new), additions to `tests/test_lint.py` + `tests/test_cli.py` (+ `test_repair.py` if a new strategy).
- `fixtures/mistral-bad.json` (or per-provider bad fixture); ensure `fixtures/portable-good.json` stays clean across all 5.
- `pyproject.toml` version `0.1.0→0.2.0` (package-data already globs `rules/*.json`); `README.md` (SARIF + providers 3→5); `CHANGELOG.md` `0.2.0`.
- `.github/workflows/ci.yml`: extend the PASS contract to 5 providers (keep the FAIL contract).

**Test commands (match schemafit CI exactly — `ruff check`, NOT `ruff format --check`):**
```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
ruff check .
pytest -q
schemafit demo
# the two fixture exit-code contracts:
schemafit lint fixtures/anthropic-bad.json --provider anthropic ; test $? -ne 0   # MUST be non-zero
schemafit lint fixtures/portable-good.json --provider openai,anthropic,gemini,mistral,cohere  # MUST exit 0
```

**Docker proof (fixture-based, no network, no public port):**
```bash
docker build -t schemafit:v02 .
docker run --rm -i schemafit:v02 lint - --provider anthropic --format sarif < fixtures/anthropic-bad.json   # expect SARIF
docker run --rm    schemafit:v02 providers                                                                   # expect 5 incl mistral,cohere
docker run --rm -i schemafit:v02 lint - --provider mistral < fixtures/mistral-bad.json ; echo "exit=$?"      # expect exit 1 + mistral-* finding
```
Expected proof lines: `"version": "2.1.0"` + `"name": "schemafit"` + an anthropic `"ruleId"` (SARIF); `mistral` and `cohere` in `providers`; a `mistral-*` finding + `exit=1` on the bad fixture.

**Local-first + version proof:**
```bash
pip install .            # no extras, clean env — succeeds
schemafit --help ; schemafit demo   # run with NO external service / NO network
grep '^version' pyproject.toml       # 0.2.0
grep -n 'dependencies = \[\]' pyproject.toml   # core dep-free intact
```

**Release procedure (HANDOFF default; tag = IRREVERSIBLE PyPI publish):**
```bash
# after PR merged + CI green on main + docker proof passed:
git -C ~/src/schemafit fetch origin main --tags
git -C ~/src/schemafit checkout main && git -C ~/src/schemafit pull --ff-only origin main
git -C ~/src/schemafit tag -a v0.2.0 -m "schemafit v0.2.0"
git -C ~/src/schemafit push origin v0.2.0    # <-- release.yml auto-publishes to PyPI (Trusted Publishing) + GHCR. IRREVERSIBLE.
gh release create v0.2.0 --repo OrionArchitekton/schemafit --title "schemafit v0.2.0" \
  --notes "v0.2.0: SARIF 2.1.0 output for GitHub code-scanning; Mistral + Cohere provider rule packs (matrix 3→5). Core dep-free."
# rollback: revert the PR; PyPI version cannot be re-uploaded (yank, not delete).
```

**Exact STEP-2 fire line (fire only after Dan approves this MAP):**
```text
/goal ultracode -- Execute the GOAL BRIEF at ~/.orion/goal-prompts/schemafit-v02-implement-20260620.md end to end; load + VERIFY the recon seed ~/.orion/goal-prompts/schemafit-v02-20260620.recon.json AND the Dan-APPROVED MAP ~/.orion/schemafit-v02-MAP-20260620.md FIRST. This MUTATES a worktree off the EXISTING repo ~/src/schemafit (NOT a new repo, NOT the canonical checkout) and may RELEASE v0.2.0 per the GATE-APPROVED posture; release is FAIL-CLOSED on the test+docker proofs and the v0.2.0 tag→PyPI publish is IRREVERSIBLE. PRECONDITION: the MAP names the v0.2 IN cut-line = TIGHT (SARIF reporter + Mistral/Cohere packs), central fork resolved (live-verify DEFER-v0.3), the DEFER-to-v0.3 list, the LOCKED-OUT set, dep posture (core dependencies=[]), the test+docker proof plan, and HANDOFF publish posture; if missing/unresolved -> FINAL STATUS: INCOMPLETE — precondition unmet. Build ONLY the approved IN set (SARIF + Mistral/Cohere); defer everything else; never touch the LOCKED-OUT set. Condition met when ONE final turn shows ALL with FRESH same-turn tool results: (1) ls/grep of the approved MAP proving the TIGHT cut + HANDOFF posture, then git -C ~/.worktrees/schemafit-v02 rev-parse --abbrev-ref HEAD proving a codex/v0.2-* branch off origin/main + log --oneline + diff --stat origin/main; (2) git log -1 --format='%an <%ae>' = Dan Mercede <dan@danmercede.com>, NO Claude trailer; (3) FRESH full test run: ruff check + pytest -q + schemafit demo all exit 0 with summary, proving the NEW SARIF reporter + each new pack (with its new failure mode: a bad fixture FAILS, portable-good PASSES across all 5 providers) AND the full v0.1 surface still green; the two CI exit-code contracts hold; (4) FRESH docker build success + docker run demonstrating BOTH new capabilities (SARIF 2.1.0 emitted for a known-bad schema; providers lists mistral+cohere; a mistral-* finding on a bad fixture) — fixture-based, no network/public port; (5) FRESH local-first proof: pip install . (no extras) + schemafit --help/demo with NO service/network; pyproject core dependencies=[] (any new dep ONLY under optional-extras), version 0.2.0; CHANGELOG/README diff; (6) RELEASE per HANDOFF: PR to OrionArchitekton/schemafit open (URL), gitleaks clean, the post-merge git tag v0.2.0 && git push origin v0.2.0 release command printed + dry-verified, NOTHING tagged (unless Dan approved autonomous tag at the gate -> then gh release view v0.2.0 + tag landed + HEAD==origin/main fetched); each commit HEAD advanced, NO force-push; (7) SELF-AUDIT TABLE each DELIVER -> criterion -> evidence -> MET/UNMET-with-blocker, + ATTESTATION: only the TIGHT IN set built (DEFER+LOCKED-OUT untouched), work confined to the worktree (git -C ~/src/schemafit status --porcelain unchanged vs turn-1 baseline), core dep-free, no secret VALUE, no force-push, no premature tag. SPINE-FIRST: both SARIF and the packs are the spine and MUST be real+proven; no hollow stub. State how to use --format sarif + how to release (tag→PyPI) + rollback (revert PR / yank PyPI). ALT terminal: FINAL STATUS: INCOMPLETE with a date -u >= a later bound, listing every unmet item with quoted tool-result evidence of an external blocker after >=2 remediation attempts (release blocker: never a destructive retry); must not claim completion.
```

---

## GATE

**SETTLED-DECISIONS ASSERT (banner — not re-decided here):** SD1 existing-repo worktree off origin/main → 0.2.0 · SD2 static local-first, core `dependencies=[]` · SD3 deepen the static wedge, **LOCKED-OUT = hosted SaaS service / browser UI-dashboard / runtime validation proxy-gateway (asserted-excluded)** · SD4 fuller-but-convergent v0.2 · SD5 publish posture decided here. No locked value is being re-opened.

**Genuinely open forks for Dan (only these):**
1. **Approve the recommended TIGHT cut** — IN = SARIF output reporter + Mistral/Cohere rule packs (provider matrix 3→5), `--live-verify` deferred to v0.3.
2. **OR redirect to the central-fork AMBITIOUS alternative** — ship `--live-verify` (opt-in, env-key-gated, mock/fixture-proven, never-default-CI) paired with a smaller static item (e.g. SARIF only), deferring the new packs.
3. **Confirm publish posture** — HANDOFF (default; Dan pushes the irreversible `v0.2.0` tag after reviewing CI + artifact), OR explicitly authorize the STEP-2 run to push the tag autonomously after all proofs pass.

Awaiting explicit **"go"**. This step does not chain into building.

---

## Self-Audit Table

SELF_AUDIT_COUNTS: scoreboard_rows=9 | in_design_rows=2 | settled_decision_rows=5 | defer_rows=5 | locked_out_rows=3 | deliver_rows=11

| deliver item | criterion | evidence pointer | status |
|---|---|---|---|
| Extension-Point Map | candidates → real file:line attachment points | `## Extension-Point Map` | MET |
| Landscape re-scan | each angle ≥1 live cited source, abstention-safe, verdict | `## Landscape Re-Scan` + `LANDSCAPE_VERDICT` | MET |
| Candidate scoreboard | every candidate: 4 scores + need-evidence + verdict, greppable | `SCOREBOARD_ROW` C1–C9 | MET |
| Central-fork resolution | TIGHT vs AMBITIOUS, recommendation+rationale, alternative kept | `## Central-Fork Resolution` + `CENTRAL_FORK_RESOLUTION` | MET |
| v0.2 IN-set design | each IN: CLI, module, dep posture, tests(+new failure mode), docker proof, version/docs | `IN_DESIGN_ROW` ×2 + IN sections | MET |
| DEFER-to-v0.3 + LOCKED-OUT | explicit residue + asserted exclusions, greppable | `DEFER_ROW` ×5, `LOCKED_OUT_ROW` ×3 | MET |
| Settled-decision EVIDENCE | SD1–SD5 confirmed-against-live (or unverifiable-pending) | `SETTLED_DECISION_ROW` SD1–SD5 | MET |
| Publish-posture recommendation | HANDOFF default + worktree/branch/PR + IRREVERSIBLE tag→PyPI | `## Publish-Posture Recommendation` | MET |
| Read-before-approving synthesis | arc + central-fork close call + drops | `## Read-Before-Approving Synthesis` | MET |
| STEP-2 prep appendix | worktree cmd, modules, test cmds, docker proof + expected lines, release, fire line | `## STEP-2 Prep Appendix` | MET |
| GATE section | only open forks + settled-decisions assert banner (incl LOCKED-OUT) | `## GATE` | MET |

## Rails Attestation

This Step-1 run posture (final fresh proof printed in the closing turn):
- Intended file mutation: **this MAP only** (`~/.orion/schemafit-v02-MAP-20260620.md`).
- Worktree/branch/tag creation: **none**. Repo edits: **none**. Builds/tests/docker: **not run**.
- Web access: search/open **GET-only**; no forms/stars/comments/writes.
- Secrets: **no secret values** surfaced (provider doc URLs are public; no keys).
- Concurrent other-session `~/.orion/` artifacts (e.g. `schemafit-arc-state.json`) and hook-owned state (`*.nudged`, `handoffs/state/**`) are **not** this run's mutations.
- Canonical baseline: `git -C ~/src/schemafit status --porcelain` empty at turn-1 (`7fcefd4`); closing turn must show it unchanged.
