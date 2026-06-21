# schemafit v0.3 MAP — 2026-06-21 (SCOPE → CARVE → MAP → GATE)

Status: STEP 1 of 2 MAP. **READ-ONLY** except this MAP file (the sole intended mutation of this run). STEP 2 (`~/.orion/goal-prompts/schemafit-v03-implement-20260621.md`) fires only after Dan approves this MAP.
Verification window: 2026-06-21 ~14:53Z–15:06Z UTC (live re-ground of `~/src/schemafit` **at the `v0.2.0` tag** via `git show v0.2.0:…` + a bounded, adversarially-verified landscape re-scan over the live web, GET-only). The MAP path did **not** pre-exist (no-prior-v0.3-artifact attested below); this run created it.
Recon seed verified (not trusted blindly): `~/.orion/goal-prompts/schemafit-v03-20260621.recon.json`. Corrections X1–X5 confirmed/adjusted (see Settled-Decision EVIDENCE + Severity findings).

**Recommendation (one line):** Approve the **TIGHT static-breadth** v0.3 cut — ship **two new static provider rule packs (Cohere + Mistral)**, taking the provider matrix **3→5**, where **Cohere is the rich, fully-primary-sourced SPINE** (a hard-error unsupported-keyword pack reusing the existing `forbidden_keyword` engine) and **Mistral is a thin, honestly-sized companion** (2 rules reusing OpenAI's exact kinds, example-derived). Both are network-free and hermetically one-run-provable. **Defer the AMBITIOUS arm (automatic rule-pack DRIFT detection on the shipped `--live-verify` foundation) to v0.4**, kept as the gate alternative. Keep core `dependencies=[]`; the LOCKED-OUT set (hosted SaaS service / browser UI-dashboard / runtime validation proxy-gateway) untouched.

**Material correction this run contributes (beyond the recon):** the recon's "packs = DATA-ONLY (no engine code)" is **partly wrong**. Adding a provider is a **minimal engine touch**, not zero-engine: `PROVIDERS` is hardcoded at `linter.py:11`, and **two tests lock the 3-provider matrix** (`tests/test_lint.py:152-154` `test_unknown_provider_raises()` asserts `lint({}, "mistral")` raises; `tests/test_cli.py:91-95` `test_providers_matrix_is_exactly_three()` asserts the output is exactly `["openai","anthropic","gemini"]`, commented "Locks the cut against scope creep"). Both **break the moment a provider is added** and MUST be updated. "Zero engine code" is true only of `apply_rule`/`repair.py` when rules reuse the 5 existing kinds + 4 existing strategies. (See WARNING W3.)

---

## No-prior-v0.3-artifact attestation (false-completion guard)

Fresh probes this run (2026-06-21 ~14:53Z): `git branch -a | grep -i v0.3` → **NONE**; `git tag` → exactly `v0.1.0`, `v0.2.0` (no `v0.3*`); `ls ~/.orion/maps/schemafit-v03-MAP-20260621.md` → **ABSENT** before this run created it; `gh pr list --state all` → only **#1, #2 (both MERGED)**; `gh issue list --state open` → **empty (0 issues)**. schemafit v0.1.0 **and** v0.2.0 are already shipped/on PyPI — that is **not** this run's completion. This run produces only the NEW dated MAP.

---

## Severity findings

- **BLOCKING:** none. No live state affirmatively contradicts any settled/locked value. The v0.3 worktree/branch/tag are **expected-absent** (research-before-build), not a contradiction.
- **WARNING (W1) — wedge OPEN but moat is packaging, not knowledge.** The static, multi-provider, no-network lint-time lane is **OPEN** (5/5 landscape angles hold), but the *knowledge* of per-provider constraints already lives inside runtime tools (LiteLLM `drop_params`, Instructor, Outlines, Guardrails, BAML) — so schemafit's moat is **packaging** (offline rule-pack + Python/PyPI + SARIF + `--live-verify` + the 5-provider matrix), not novel knowledge. This argues *for* shipping the convergent static-breadth cut now and iterating, not for over-investing.
- **WARNING (W2) — every new pack rule PRIMARY-sourced or DROPPED.** Confirmed against primary docs: **Cohere is RICH** (`docs.cohere.com/docs/structured-outputs` enumerates an explicit "Unsupported schema features" table → ~10 hard-error keyword rules + 2 structural rules, all primary-sourceable). **Mistral is THIN** (`docs.mistral.ai` / `platform-docs-public.pages.dev` custom-structured-output) — only `additionalProperties:false` + all-properties-`required` are schema-node-lintable, and those are **documented BY EXAMPLE only** (the official curl sample), not asserted as a prose MUST; `strict:true` and the `codestral-mamba` exclusion are **API/model-level, not schema-node-level** → they become README notes, **not lint rules**. Mistral has **NO documented per-keyword unsupported list** → any keyword-blocklist Mistral rule would be **invented → DROPPED**. Do not pre-promise Mistral parity. (Confidence: Cohere HIGH; Mistral MEDIUM — canonical `docs.mistral.ai` renders client-side and would not load; content came from Mistral's own `platform-docs-public.pages.dev` deployment. STEP-2 must re-verify against the canonical render before locking the Mistral pack.)
- **WARNING (W3) — packs are a MINIMAL ENGINE TOUCH, not DATA-ONLY.** See the one-line correction above. `PROVIDERS` tuple (`linter.py:11`) + the two matrix-locking tests + the `--provider` help strings (`cli.py:218,235`) + the CI PASS contract MUST change. "Zero engine code" applies only to `apply_rule`/`repair.py` when rules reuse existing kinds/strategies (true for all 10 Cohere forbidden-keyword rules + both Mistral rules). The 2 Cohere **structural** rules (top-level-must-be-object; every object ≥1 `required`) are **NOT** expressible with the 5 existing kinds → each needs a new `apply_rule` clause → they are **DEFER-v0.4 (stretch)**, not in the convergent spine.
- **WARNING (W4) — drift competitor-absence is ABSTAIN-UNVERIFIED, not confirmed-empty.** The bounded search found no dedicated static Mistral/Cohere pack linter and no documentation-constraint drift detector since 2026-06-20, but GitHub/PyPI/npm were web-searched, **not** queried exhaustively (a package published in the last 24–48h could be below index visibility). State "none found," never "proven empty."
- **INFO (I1) — competitor `Ayubjon/tool-schema-lint` is REAL but near-dead and unpublished.** Created `2026-06-10T18:19:15Z`, last push `2026-06-11` (~1 day of activity, stale since), JavaScript/Node 18+, **2 stars / 0 forks / 0 issues**, **function-calling/tool schemas only** (not structured-output), 3 providers (OpenAI/Anthropic/Gemini). `registry.npmjs.org/tool-schema-lint` → **HTTP 404 (NOT published)** — its README `npm install`/`npx` instructions are unbacked. It overlaps only the *non-differentiating* shared core (static lint + zero-dep/offline + CI exit codes). No SARIF / drift / Pydantic / live-verify / Mistral / Cohere.
- **INFO (I2) — git-identity discrepancy.** The v0.2.0 tagged commit was actually authored `Dan Mercede <dan.mercede@gmail.com>`, **not** `dan@danmercede.com` (which is what `pyproject.toml` `authors` and the v0.2 MAP/recon assert). Global git email is the OAC address (`Dan.mercede@orionapexcapital.com`). SD5 keeps the **declared project identity `Dan Mercede <dan@danmercede.com>`** (pyproject = source of truth); STEP-2 must set it LOCALLY in the worktree and NOT blindly mirror v0.2.0's actual gmail commit. Surfaced for Dan's awareness, not a re-gate.
- **INFO (I3) — `confidence:none` audit.** No `confidence:none` evidence is load-bearing in this MAP. Every IN/DEFER candidate is backed by the published roadmap (`README.md` "Deferred (v0.3+)"), a real in-code attachment point (file:line at the v0.2.0 tag), or a cited live primary source. Mistral's thinness is the only MEDIUM-confidence input and is flagged (W2).

---

## Extension-Point Map

Fresh state (turn-1 baseline, this run): canonical `~/src/schemafit` local `main` = `7fcefd47…` (**STALE v0.1** working tree — no `live.py`, no SARIF, version 0.1.0); `origin/main` = `c45d840…` (**v0.2.0** merged); shape below read from **`git show v0.2.0:…`**, never the working tree (correction X2). `git status --porcelain` = empty. Public `OrionArchitekton/schemafit` (MIT); tags `v0.1.0`,`v0.2.0`; **0 open issues / PRs #1,#2 MERGED**; no v0.3 worktree/branch/MAP. Linter dispatches exactly **5 rule kinds**; repair dispatches **4 strategies** off `auto_repair`; `PROVIDERS` is **3** (`openai`,`anthropic`,`gemini`).

| v0.3 candidate | real code attachment point (v0.2.0 tag) | file:line evidence | v0.3 attachment plan |
|---|---|---|---|
| **Cohere rule pack** (IN, SPINE) | Packs load lazily+cached from `schemafit/rules/<p>.json` via `load_rule_pack`; `PROVIDERS` is the single registry consumed by `cli._parse_providers`, `cmd_providers`, `verify_providers`. The unsupported-keyword rules reuse the existing `forbidden_keyword` kind. | `linter.py:11` (`PROVIDERS`), `:16-23` (`load_rule_pack`, raises `ValueError` if provider∉`PROVIDERS`), `:65-70` (`forbidden_keyword`), `:109-118` (`lint`); `repair.py:38` (`strip`) | IN. Add `"cohere"` to `PROVIDERS` (`linter.py:11`); add `schemafit/rules/cohere.json` (root `{provider,doc,rules:[…]}`). ~10 hard-error `forbidden_keyword` rules: `allOf`,`oneOf`,`not`,`minimum`,`maximum`,`minItems`,`maxItems`,`minLength`,`maxLength`,`uniqueItems` (each `severity:error`, `auto_repair:strip` for the validation keywords / `manual` for composition). **Zero `apply_rule`/`repair.py` change** (reuses existing kind+strategy). Every rule `doc_url=https://docs.cohere.com/docs/structured-outputs` (W2). |
| **Mistral rule pack** (IN, thin) | Same pack mechanism; the two Mistral schema-node constraints reuse OpenAI's exact kinds. | `linter.py:11`, `:78-86` (`object_requires`), `:88-96` (`object_all_properties_required`); `repair.py:44` (`set_false`), `:50` (`fill_required`); `rules/openai.json` (kind exemplars) | IN (thin). Add `"mistral"` to `PROVIDERS`; add `schemafit/rules/mistral.json` with **2 rules**: `additionalProperties:false` required (`kind:object_requires`,`value:false`,`auto_repair:set_false`) + all-properties-required (`kind:object_all_properties_required`,`auto_repair:fill_required`) — mirrors `openai.json`. Example-derived (W2 caveat). `strict:true` + `codestral-mamba` exclusion = **README notes, not rules**. **Zero `apply_rule`/`repair.py` change.** |
| **provider registry / matrix-lock tests** (IN, engine touch) | `PROVIDERS` tuple + the two tests that lock it to 3 + `--provider` help strings + the CI PASS contract. | `linter.py:11`; `tests/test_lint.py:152-154` (`test_unknown_provider_raises` uses `"mistral"`); `tests/test_cli.py:91-95` (`test_providers_matrix_is_exactly_three`); `cli.py:218,235` (help text); `.github/workflows/ci.yml` PASS step | IN (the minimal engine touch — W3). `PROVIDERS += ("mistral","cohere")`; change `test_unknown_provider_raises` to a still-unknown provider (e.g. `"bedrock"`); update/retitle `test_providers_matrix_is_exactly_three` to the 5-provider list; update the two `--provider` help strings; extend the CI PASS contract to `openai,anthropic,gemini,mistral,cohere`. |
| **Cohere structural rules (2 new kinds)** (DEFER-v0.4 / stretch) | `apply_rule` recognizes exactly 5 kinds (else `ValueError`); no "root type" / "min-one-required" kind exists. | `linter.py:44-104` (`apply_rule`, guard `:104`); `walk.py` (root node at pointer `#`) | DEFER-v0.4 (stretch). "Top-level type must be object" + "every object ≥1 `required` field" need 2 new `apply_rule` clauses (before `:104`) + tests. Real Cohere constraints, primary-sourced — but they break the data-only spine → first v0.4 add-back. |
| **automatic rule-pack DRIFT detection** (DEFER-v0.4 / central-fork AMBITIOUS) | Reuse the shipped `--live-verify` foundation; per-rule `doc_url` on every rule is the drift source-of-truth anchor; fold drift verdicts into `Finding`s through the SAME SARIF/report path (the `live-rejection` synthetic Finding is the pattern). | `live.py:56-63` (`ProviderClient`), `:66-83` (`MockProviderClient`), `:42-53` (`LiveResult` tri-state), `:86-103` (`interpret_response`), `:214-223` (`get_client`), `:157-180` (`RealHTTPClient._request` urllib); new subparser `cli.py` after `:244`; synthetic Finding `cli.py:86-102`; SARIF reuse `report.py:71-164`; `doc_url` `openai.json:13,21,30,40` etc. | DEFER-v0.4 (central-fork alternative). Feasible (mock-default, env/flag-gated real fetch, abstention-safe) — but network-at-check-time, harder convergence; pairs with the now-broader pack surface. New `drift.py` + `drift` subcommand; **no parallel reporter**. |
| **Pydantic source-model auto-fix** (DEFER-v0.4) | Schema ingestion is `_load_schema` (JSON file/stdin→dict); engine is JSON-Schema-native. | `cli.py:39-43` (`_load_schema`), feeds `lint_multi`/`repair`; `pyproject.toml:34` (`live=[]` extra slot) | DEFER-v0.4. Attach a model-input mode at the loader (`Model.model_json_schema()`→dict) + a CLI arg; adds a `pydantic` **optional-extra**. Sizeable standalone increment — crowds v0.3 convergence. |
| **Bedrock + Vertex packs** (DEFER-BIG-v0.4) | Same pack mechanism as Cohere/Mistral. | `linter.py:11`, `schemafit/rules/` | DEFER-BIG. **Platform multiplexers** — their "schema constraints" are the underlying model's (Claude-on-Bedrock = Anthropic; Gemini-on-Vertex = Gemini) → conflated/invented-rule risk. Model after the dedicated-provider pattern. |
| **npm/`ajv` JS-port, Zod source-model** (DEFER-BIG-v0.4) | N/A (second ecosystem). | `README.md` "Deferred (v0.3+)" | DEFER-BIG. Whole JS/TS second ecosystem. The npm slot is *still unclaimed* (the JS competitor is unpublished — I1), but far too large for a convergent Python v0.3. Not locked-out. |
| **Rebuild v0.1/v0.2 surface** (DROP) | `lint`/`repair`/`providers`/`demo` + 3 packs + SARIF + `--live-verify` already shipped. | `cli.py:217,234,240,243`; `CHANGELOG.md` `[0.1.0]`,`[0.2.0]` | DROP. Do not rebuild; only extend. Anti-regression: all v0.1+v0.2 tests + the two CI contracts stay green. |

---

## Landscape Re-Scan (bounded; abstention-safe; adversarially verified)

The wedge = *a STATIC, local-first, pip-installable, declarative-rule-pack CLI/CI linter checking JSON-Schema structured-output / tool schemas against MULTIPLE LLM providers' documented constraints, with no network at lint time.* Five angles, each scanned then adversarially refutation-tested. **Verdict: WEDGE STILL OPEN (high confidence on the broad lane; ABSTAIN-UNVERIFIED on the dedicated-pack/drift sub-wedge).**

### Angle 1 — named static competitor `Ayubjon/tool-schema-lint` → OPEN (high)
REAL but tiny/narrow/unpublished (I1). `api.github.com/repos/Ayubjon/tool-schema-lint`: created `2026-06-10`, JS/Node 18+, 2★/0 forks, function-calling/tool schemas only, 3 providers. `registry.npmjs.org/tool-schema-lint` → **HTTP 404** (verified ×2 + npm search). **schemafit differentiators:** 5-provider matrix (adds Cohere+Mistral) · Python/PyPI+stdlib (vs unpublished Node) · SARIF 2.1.0 · `--live-verify` · drift (roadmap) · Pydantic (roadmap) · **both** structured-output AND function-calling schemas. Shared/non-differentiating: static lint + zero-dep/offline + CI exit codes.

### Angle 2 — Cohere structured-output constraints (primary-sourceable for the pack) → RICH (high)
`docs.cohere.com/docs/structured-outputs` enumerates an explicit **"Unsupported schema features"** table → hard-error keyword rules: `allOf`,`oneOf`,`not`,`minimum`,`maximum`,`minItems`,`maxItems`,`minLength`,`maxLength`,`uniqueItems`; plus 2 structural rules (top-level type must be `object`; every object ≥1 `required`). Supported (do NOT flag): `anyOf`,`$ref`,`$defs`,`enum`,`const`,`pattern`. Caveats (drop/defer): regex anchors within `pattern` unsupported (needs value-inspection → defer); `format` restricted to `date-time`/`uuid`/`date`/`time` (needs value-inspection → defer); `additionalProperties` supported-but-non-enforcing (a caution, lean drop). Strong, fully primary-sourced pack.

### Angle 3 — Mistral structured-output constraints → THIN (medium)
`docs.mistral.ai` / `platform-docs-public.pages.dev` custom-structured-output. Schema-node-lintable + primary-sourceable: `additionalProperties:false`, all-properties-`required` (both **example-derived**, not prose-MUST). API/model-level (README notes, NOT rules): `response_format:{type:json_schema}`+`strict:true`; `codestral-mamba` exclusion. **No documented per-keyword unsupported list** → no keyword-blocklist rule (would be invented → DROPPED). Canonical `docs.mistral.ai` renders client-side and would not load → MEDIUM confidence; re-verify in STEP-2 (W2).

### Angle 4 — dedicated Mistral/Cohere static pack + documentation-drift detector → ABSTAIN-UNVERIFIED (medium)
None found (the expected, abstention-safe result — W4). Adjacent-but-distinct: generic JSON-Schema linters (vacuum, Spectral, `sourcemeta/jsonschema`, `check-jsonschema`, schemalint) — no provider-specific rule pack; spec-diff drift (oasdiff, Bump.sh) and live-response drift (Treblle, API Detective, Tusk) — diff spec files / live traffic, **not** provider-docs-as-source constraint drift; MCP schema monitors (Bellwether, DriftCop); runtime validators (excluded). No tool consumes provider docs as a drift source.

### Angle 5 — runtime lane occupancy (distinct from static) → OPEN (high)
All six runtime tools confirmed in the runtime lane, none a static pre-ship CLI linter: **Instructor** (request-time Pydantic validation), **Outlines** & **llguidance** (decode-time logit/grammar constraint), **LiteLLM `drop_params`** (call-time param mutation — explicitly NOT a static lint), **Guardrails AI** (runtime I/O guards), **BAML** (compile-time codegen but runtime Schema-Aligned Parsing). Cross-provider divergence is caught reactively at runtime (e.g. `additionalProperties:false` valid on OpenAI → 400 on xAI/Grok), which is exactly the gap a static pre-ship linter fills.

**LANDSCAPE_VERDICT: WEDGE-OPEN | broad-lane-confidence=high | dedicated-pack+drift-subwedge=ABSTAIN-UNVERIFIED | refuted=false (5/5 angles) | moat=packaging-not-knowledge | named_competitor=Ayubjon/tool-schema-lint(JS,3-provider,function-only,npm-404-unpublished,2-stars,stale) | cohere=RICH-primary-sourced | mistral=THIN-example-derived | nearest_runtime=LiteLLM | nearest_static=sourcemeta/jsonschema(no-provider,no-SARIF)**

---

## Candidate Scoreboard

Scores 1–5: **wedge-fit / need-cited / one-run-buildable / keeps-static-local-first**. Verdicts: IN-v0.3 / DEFER-v0.4 / DROP.

| id | candidate | scores (wf/nc/orb/ksl) | need evidence | verdict |
|---|---|---:|---|---|
| C1 | Cohere rule pack (data-only forbidden-keyword) | 5/5/5/5 | roadmap `README.md` "Deferred(v0.3+)"; attach `linter.py:11,:65-70`,`repair.py:38`; **primary-sourced** `docs.cohere.com/docs/structured-outputs` (Angle 2 RICH); deepens vs 3-provider competitor (Angle 1) | **IN-v0.3** |
| C2 | Mistral rule pack (thin, data-only) | 4/3/5/5 | roadmap; attach `linter.py:11,:78-96`,`repair.py:44,:50`; primary-sourced-by-example only (Angle 3 THIN, W2) — 2 rules; names Mistral in the matrix | **IN-v0.3** |
| C3 | provider registry + matrix-lock test touch | 5/5/5/5 | in-code: `linter.py:11`,`test_lint.py:152-154`,`test_cli.py:91-95`,`cli.py:218,235` (W3) — prerequisite for C1/C2 | **IN-v0.3** |
| C4 | Cohere structural rules (2 new kinds) | 4/4/4/5 | primary-sourced (Angle 2: top-level-object + ≥1-required); but needs 2 new `apply_rule` kinds → breaks data-only spine (W3) | DEFER-v0.4 (stretch) |
| C5 | rule-pack DRIFT detection (AMBITIOUS) | 4/4/3/3 | roadmap; README says drift "pairs with `--live-verify`"; feasible on `live.py` (verify-2 SURVIVES) — network-at-check, abstention complexity, harder convergence | DEFER-v0.4 (central-fork alt) |
| C6 | Pydantic source-model auto-fix | 4/3/3/4 | roadmap; attach `cli.py:39-43`; sizeable; adds `pydantic` optional-extra | DEFER-v0.4 |
| C7 | Bedrock + Vertex packs | 3/2/2/5 | roadmap — platform multiplexers; constraints are underlying-model's (invented-demand risk) | DEFER-BIG-v0.4 |
| C8 | npm/ajv JS-port | 3/3/1/4 | roadmap — whole second ecosystem; npm slot unclaimed (competitor 404) but too big for Python v0.3 | DEFER-BIG-v0.4 |
| C9 | Zod source-model | 3/2/1/4 | roadmap — JS ecosystem (pairs with the JS port) | DEFER-BIG-v0.4 |
| C10 | rebuild v0.1/v0.2 surface | 1/1/5/5 | already shipped `CHANGELOG.md` `[0.1.0]`,`[0.2.0]` | DROP |

SCOREBOARD_ROW: id=C1 | candidate=cohere-rule-pack | wedge_fit=5 | need_cited=5 | one_run_buildable=5 | keeps_static_local_first=5 | need_evidence=roadmap:README-deferred-v0.3;attach:linter.py:11+:65-70,repair.py:38;primary:docs.cohere.com/docs/structured-outputs-Angle2-RICH | verdict=IN-v0.3 | confidence=high
SCOREBOARD_ROW: id=C2 | candidate=mistral-rule-pack-thin | wedge_fit=4 | need_cited=3 | one_run_buildable=5 | keeps_static_local_first=5 | need_evidence=roadmap;attach:linter.py:11+:78-96,repair.py:44+:50;primary-by-example-only:Angle3-THIN-W2;2-rules-only | verdict=IN-v0.3 | confidence=medium
SCOREBOARD_ROW: id=C3 | candidate=provider-registry+matrix-lock-test-touch | wedge_fit=5 | need_cited=5 | one_run_buildable=5 | keeps_static_local_first=5 | need_evidence=in-code:linter.py:11,test_lint.py:152-154,test_cli.py:91-95,cli.py:218+235-W3-prerequisite | verdict=IN-v0.3 | confidence=high
SCOREBOARD_ROW: id=C4 | candidate=cohere-structural-rules-2-new-kinds | wedge_fit=4 | need_cited=4 | one_run_buildable=4 | keeps_static_local_first=5 | need_evidence=primary:Angle2-top-level-object+min-one-required;blocker=needs-2-new-apply_rule-kinds-breaks-data-only-spine-W3 | verdict=DEFER-v0.4 | confidence=high
SCOREBOARD_ROW: id=C5 | candidate=rule-pack-drift-detection | wedge_fit=4 | need_cited=4 | one_run_buildable=3 | keeps_static_local_first=3 | need_evidence=roadmap:README-drift-pairs-with-live-verify;feasible-on-live.py-verify2-SURVIVES;blocker=network-at-check+abstention+harder-convergence | verdict=DEFER-v0.4 | confidence=high
SCOREBOARD_ROW: id=C6 | candidate=pydantic-source-model | wedge_fit=4 | need_cited=3 | one_run_buildable=3 | keeps_static_local_first=4 | need_evidence=roadmap;attach:cli.py:39-43;cost=pydantic-optional-extra+sizeable | verdict=DEFER-v0.4 | confidence=high
SCOREBOARD_ROW: id=C7 | candidate=bedrock-vertex-packs | wedge_fit=3 | need_cited=2 | one_run_buildable=2 | keeps_static_local_first=5 | need_evidence=roadmap;risk=platform-multiplexer-constraints-are-underlying-model-invented-demand | verdict=DEFER-BIG-v0.4 | confidence=high
SCOREBOARD_ROW: id=C8 | candidate=npm-ajv-js-port | wedge_fit=3 | need_cited=3 | one_run_buildable=1 | keeps_static_local_first=4 | need_evidence=roadmap;npm-slot-unclaimed-competitor-404;blocker=whole-second-ecosystem | verdict=DEFER-BIG-v0.4 | confidence=high
SCOREBOARD_ROW: id=C9 | candidate=zod-source-model | wedge_fit=3 | need_cited=2 | one_run_buildable=1 | keeps_static_local_first=4 | need_evidence=roadmap;blocker=js-ecosystem-pairs-with-js-port | verdict=DEFER-BIG-v0.4 | confidence=high
SCOREBOARD_ROW: id=C10 | candidate=rebuild-v0.1-v0.2-surface | wedge_fit=1 | need_cited=1 | one_run_buildable=5 | keeps_static_local_first=5 | need_evidence=already-shipped:CHANGELOG-0.1.0+0.2.0 | verdict=DROP | confidence=high

---

## Central-Fork Resolution

**Recommendation: TIGHT — static-breadth (Cohere + Mistral packs, matrix 3→5).** Ship C1 (Cohere, the rich primary-sourced SPINE) + C2 (Mistral, thin companion) + C3 (the minimal engine touch). **Defer C5 (AMBITIOUS drift detection) to v0.4**, kept as the gate alternative.

Rationale:
1. **Convergence / spend-kill robustness (decisive).** TIGHT is **network-free**, so the whole increment — including the `docker run` proof — is **hermetic and one-run-provable**. SPINE-FIRST: the **Cohere pack is the spine** (rich, fully primary-sourced, pure data after the engine touch); Mistral is cheap periphery that degrades to a self-audit note if the run is spend-killed (the v0.2 run *was* spend-killed mid-flight). AMBITIOUS drift adds a mock/fixture harness, env/flag-gating, abstention-safe diffing, and a new subcommand — real work that risks non-convergence in one autonomous STEP-2 run.
2. **Need-evidence asymmetry.** Cohere is **RICH and primary-sourced** (Angle 2); the AMBITIOUS arm would partly lean on a broad Mistral pack that is **THIN** (Angle 3) — broad Mistral keyword rules would be **invented → dropped** under W2. The static-breadth value is *available now*; the drift value is *novel but contingent*.
3. **Differentiation.** Adding Cohere+Mistral takes the matrix to 5 — a lane the 3-provider, function-only, unpublished JS competitor (I1) cannot match — and is exactly the OPEN static-multi-provider lane (Angles 1, 5).
4. **Sequencing.** `--live-verify` already shipped (v0.2); drift "pairs with `--live-verify`" (README) and now also wants a **broader pack surface** of `doc_url`s to watch. Shipping the broader packs in v0.3, then drift in v0.4, is the natural order (mirrors the v0.2 MAP's "live + drift belong together" logic, advanced one step).

**Alternative kept for the gate (AMBITIOUS):** build automatic rule-pack DRIFT detection on the shipped `live.py` foundation — a new `drift` subcommand that fetches each rule's `doc_url` and diffs documented constraints. Admissible ONLY as: **mock/fixture-default** (hermetic test + docker proof — no real network in CI), real `doc_url` fetch **env/flag-gated**, **abstention-safe** (a rate-limited/abstaining fetch = `UNVERIFIED`, never "no drift"), reusing `live.py` `ProviderClient`/`MockProviderClient`/tri-state/`urllib`, and folding drift verdicts into `Finding`s through the **same** SARIF/report path (no parallel reporter). Higher novelty/moat, harder convergence. If chosen, pair it with the thin Mistral pack only (drop Cohere's rich pack from the cut to stay convergent).

CENTRAL_FORK_RESOLUTION: recommendation=TIGHT-static-breadth | in=cohere-pack(SPINE)+mistral-pack-thin+provider-engine-touch | alternative=AMBITIOUS-drift-detection-mock-default-on-live.py | rationale=network-free-hermetic-one-run-proof+spend-kill-SPINE-FIRST+cohere-RICH-vs-mistral-THIN-need-asymmetry+deepens-vs-3-provider-competitor+drift-pairs-with-broader-pack-surface-in-v0.4 | locked_out_untouched=true | core_dependencies=keep-[]

---

## v0.3 IN-Set Design

Shared constraints: core `pyproject.toml` `dependencies = []` stays true; **no new dep** (packs are declarative JSON; `rules/*.json` is already package-data-globbed at `pyproject.toml`). All v0.1+v0.2 commands (`lint`/`repair`/`providers`/`demo`), the 3 existing packs, the SARIF reporter, `--live-verify` (mock-default/tri-state/fail-closed), `walk` traversal, and the v0.1 hardening fixes stay green. The `docker run` proof exercises a NEW v0.3 capability (a new pack catching a violating schema + `providers` listing 5).

### IN 1 (SPINE): Cohere rule pack

- **CLI surface:** none new — `providers` (`cli.py:168-172`) auto-lists from `PROVIDERS`; `lint`/`repair` accept `cohere` via `_parse_providers` (`cli.py:46-54`).
- **Module / data:** add `"cohere"` to `PROVIDERS` (`linter.py:11`); add `schemafit/rules/cohere.json` (root `{provider,doc,rules:[…]}`). ~10 rules, all `kind:forbidden_keyword`, `severity:error`: `allOf`/`oneOf`/`not` (`auto_repair:manual` — composition rewrites are unsafe to guess), `minimum`/`maximum`/`minItems`/`maxItems`/`minLength`/`maxLength`/`uniqueItems` (`auto_repair:strip`). **Zero `apply_rule`/`repair.py` change** — all reuse the existing `forbidden_keyword` kind + `strip`/`manual` strategies.
- **W2 grounding:** every rule `doc_url = https://docs.cohere.com/docs/structured-outputs` (primary). Supported keywords (`anyOf`,`$ref`,`$defs`,`enum`,`const`,`pattern`) are **NOT** flagged. Deferred-as-unsourceable-cleanly: regex-anchor-in-`pattern` and `format`-value restrictions (need value-inspection → a new kind → C4/v0.4).
- **Dep posture:** core-none (declarative JSON).
- **Test plan:** extend `tests/test_lint.py` — Cohere **catches** a schema using a forbidden keyword (e.g. `{"type":"object","properties":{"x":{"type":"array","minItems":1}},"required":["x"]}` → `cohere-no-minItems` error) and **passes** `fixtures/portable-good.json`. **NEW FAILURE MODE:** add `fixtures/cohere-bad.json` that FAILS under `--provider cohere` (exit 1) while `portable-good.json` PASSES under all 5.
- **`docker run` smoke-proof (fixture-based, no network/port):** `docker run --rm -i schemafit:v03 lint - --provider cohere < fixtures/cohere-bad.json` → exit 1 with a `cohere-*` finding (e.g. `cohere-no-minItems`); `docker run --rm schemafit:v03 lint - --provider cohere --format sarif < fixtures/cohere-bad.json` → SARIF `ruleId` `cohere-*`. Proof lines: `[cohere] FAIL`, a `cohere-*` rule id, `exit=1`.
- **Version/docs delta:** README provider table 3→5 (Cohere row, primary-sourced); CHANGELOG `0.3.0` Added: "Cohere provider rule pack (hard-error unsupported-keyword constraints, primary-sourced)."

IN_DESIGN_ROW: item=cohere-rule-pack | cli=none-new(providers auto-lists PROVIDERS) | module=linter.py:11 PROVIDERS+=cohere; rules/cohere.json (~10 forbidden_keyword rules error severity, reuse strip/manual) | dep_posture=core-none | tests=test_lint.py cohere-catches-forbidden-kw+passes-portable-good; NEWFAILMODE fixtures/cohere-bad.json FAILs+portable-good PASSes-all-5 | docker_proof=lint - --provider cohere < fixtures/cohere-bad.json exits 1 with cohere-* finding; --format sarif shows cohere-* ruleId; no network/port | version_docs=0.3.0 README-providers-3to5-cohere-row CHANGELOG; every rule doc_url=docs.cohere.com/docs/structured-outputs(W2)

### IN 2: Mistral rule pack (thin, honestly sized)

- **CLI surface:** none new (as IN 1).
- **Module / data:** add `"mistral"` to `PROVIDERS` (`linter.py:11`); add `schemafit/rules/mistral.json` with **exactly 2 rules** (mirror `openai.json`): `additionalProperties:false` required (`kind:object_requires`,`keyword:additionalProperties`,`value:false`,`severity:error`,`auto_repair:set_false`); all-properties-required (`kind:object_all_properties_required`,`severity:error`,`auto_repair:fill_required`). **Zero `apply_rule`/`repair.py` change.**
- **W2 grounding (honest):** both rules `doc_url = https://docs.mistral.ai/capabilities/structured-output/custom_structured_output/`, labeled **example-derived** in `reason` (the official sample sets them; docs do not state them as a prose MUST). `strict:true` + `codestral-mamba` exclusion = **README notes only**, NOT rules (API/model-level). **No keyword-blocklist rule** (Mistral docs enumerate none → would be invented). STEP-2 re-verifies against the canonical `docs.mistral.ai` render before locking (W2; canonical rendered client-side at scan time).
- **Dep posture:** core-none.
- **Test plan:** extend `tests/test_lint.py` — Mistral **catches** an object missing `additionalProperties:false` / with an optional property, and **passes** `portable-good.json`. **NEW FAILURE MODE:** `fixtures/mistral-bad.json` FAILS under `--provider mistral`; `portable-good.json` PASSES under all 5.
- **`docker run` smoke-proof:** `docker run --rm schemafit:v03 providers` lists 5 incl. `mistral`+`cohere`; `docker run --rm -i schemafit:v03 lint - --provider mistral < fixtures/mistral-bad.json` → exit 1 with a `mistral-*` finding.
- **Version/docs delta:** README provider table +Mistral row (note: thin/strict-semantics, example-derived; `strict:true`+codestral-mamba as prose notes); CHANGELOG `0.3.0` Added: "Mistral provider rule pack (strict structured-output semantics: additionalProperties:false + all-required; example-derived)."

IN_DESIGN_ROW: item=mistral-rule-pack-thin | cli=none-new | module=linter.py:11 PROVIDERS+=mistral; rules/mistral.json (2 rules: object_requires/set_false + object_all_properties_required/fill_required, mirror openai) | dep_posture=core-none | tests=test_lint.py mistral-catches-missing-addlprops+optional-prop+passes-portable-good; NEWFAILMODE fixtures/mistral-bad.json FAILs+portable-good PASSes-all-5 | docker_proof=providers lists 5 incl mistral+cohere; lint - --provider mistral < fixtures/mistral-bad.json exits 1 with mistral-* | version_docs=0.3.0 README-+mistral-row(thin,example-derived,strict+codestral-mamba=notes) CHANGELOG; doc_url=docs.mistral.ai/capabilities/structured-output/custom_structured_output(W2-reverify-canonical)

### IN 3: provider registry + matrix-lock test touch (the minimal engine touch — W3)

- **Module:** `PROVIDERS += ("mistral","cohere")` (`linter.py:11`).
- **Tests that MUST change (else CI fails):** `tests/test_lint.py:152-154` `test_unknown_provider_raises()` — swap `"mistral"` for a still-unknown provider (e.g. `"bedrock"`); `tests/test_cli.py:91-95` `test_providers_matrix_is_exactly_three()` — update the asserted list to the 5 providers and retitle (`…_is_exactly_five`).
- **Help strings:** update the two `--provider` help texts (`cli.py:218` lint, `cli.py:235` repair) from `openai,anthropic,gemini` to include `mistral,cohere` (cosmetic but should match reality).
- **CI contract:** extend the PASS step in `.github/workflows/ci.yml` to `--provider openai,anthropic,gemini,mistral,cohere` (proves the new packs don't false-positive on `portable-good.json`); keep the FAIL step (anthropic-bad) unchanged.
- **Dep posture:** core-none.

IN_DESIGN_ROW: item=provider-registry+matrix-lock-test-touch | cli=update --provider help strings cli.py:218+235 | module=linter.py:11 PROVIDERS+=mistral,cohere | dep_posture=core-none | tests=FIX test_lint.py:152-154 unknown-provider->bedrock; UPDATE/RETITLE test_cli.py:91-95 matrix-is-exactly-five | docker_proof=providers lists exactly 5 | version_docs=ci.yml PASS-contract extended to 5 providers (FAIL contract anthropic-bad unchanged)

---

## DEFER-to-v0.4 and LOCKED-OUT

### DEFER-to-v0.4 (the explicit residue — seeds the next harness fire)

| item | reason |
|---|---|
| Cohere structural rules (top-level-object; every object ≥1 required) | Need 2 new `apply_rule` kinds → break the data-only spine; primary-sourced (first v0.4 add-back). |
| rule-pack DRIFT detection (AMBITIOUS arm) | Network-at-check-time + abstention complexity → harder convergence; pairs with `--live-verify` + the now-broader pack surface. Build mock-default on `live.py`. |
| Pydantic source-model auto-fix | Sizeable; adds a `pydantic` optional-extra; would crowd v0.3 convergence. |
| Bedrock + Vertex packs (BIG) | Platform multiplexers — constraints are the underlying model's; model after the dedicated-provider pattern to avoid invented rules. |
| npm/ajv JS-port, Zod source-model (BIG) | Whole JS/TS second ecosystem; npm slot unclaimed (competitor 404) but far beyond a convergent Python v0.3. Not locked-out. |

DEFER_ROW: item=cohere-structural-rules-new-kinds | verdict=DEFER-v0.4 | reason=needs-2-new-apply_rule-kinds-breaks-data-only-spine
DEFER_ROW: item=rule-pack-drift-detection | verdict=DEFER-v0.4 | reason=central-fork-AMBITIOUS-network-at-check+abstention-pairs-with-broader-pack-surface
DEFER_ROW: item=pydantic-source-model | verdict=DEFER-v0.4 | reason=sizeable+pydantic-extra-would-crowd-convergence
DEFER_ROW: item=bedrock-vertex-packs | verdict=DEFER-BIG-v0.4 | reason=platform-multiplexer-constraints-are-underlying-model
DEFER_ROW: item=npm-ajv-js-port-and-zod | verdict=DEFER-BIG-v0.4 | reason=whole-second-js-ecosystem-npm-slot-unclaimed-but-too-big

### LOCKED-OUT (asserted-excluded — NOT re-gated, NOT proposed)

| locked-out item | one-line reason |
|---|---|
| hosted SaaS linter service | Hosted runtime breaks the static, local-first, CLI/CI identity. |
| browser UI / dashboard | Frontend/admin surface; drifts from the CLI/CI-proof local-first identity. |
| runtime validation proxy/gateway | The LiteLLM/Guardrails runtime request-path lane; breaks static-by-default identity. |

LOCKED_OUT_ROW: item=hosted-saas-linter-service | status=asserted-excluded | reason=hosted-runtime-breaks-static-local-first
LOCKED_OUT_ROW: item=browser-ui-dashboard | status=asserted-excluded | reason=frontend-surface-not-cli-ci-proof
LOCKED_OUT_ROW: item=runtime-validation-proxy-gateway | status=asserted-excluded | reason=runtime-request-path-litellm-guardrails-lane

---

## Settled-Decision EVIDENCE Table (SD1–SD5)

Confirm-against-live = silent evidence (NOT a Dan-facing re-decision). An expected-absent probe (the v0.3 worktree) is `unverifiable-pending`, not a contradiction.

| SD | locked value | fresh confirmation probe | status |
|---|---|---|---|
| SD1 | Extend existing repo `~/src/schemafit` from a worktree off **freshly-fetched origin/main** (v0.2.0 base `c45d840`; branch `codex/v0.3-<slug>-20260621`); bump 0.2.0→0.3.0. NOT a new repo, NOT the stale local checkout. | `origin/main`=`c45d840` (v0.2.0); local `main`=`7fcefd4` (STALE v0.1, working-tree pyproject 0.1.0); `git show v0.2.0:pyproject.toml` version `0.2.0`; tags `v0.1.0`,`v0.2.0`; no `v0.3*` branch/tag; no v0.3 worktree/MAP. | confirmed-against-live; worktree=unverifiable-pending (expected-absent) |
| SD2 | Static local-first: core `dependencies=[]`; no hosted service; static-by-default; new deps optional-extras only (packs add none). | `git show v0.2.0:pyproject.toml` `dependencies = []`; extras `[dev]` + `live=[]` (empty); `Dockerfile` CLI `ENTRYPOINT`, no `EXPOSE`; CHANGELOG `[0.2.0]` "Core package stays zero-dependency"; `rules/*.json` already package-data-globbed. | confirmed-against-live |
| SD3 | v0.3 DEEPENS the static wedge; LOCKED-OUT = hosted SaaS / browser UI / runtime proxy-gateway; DEFER-BIG = Bedrock/Vertex, npm/ajv JS-port, Zod. | `git show v0.2.0:README.md` "Deferred (v0.3+)" roadmap matches (Mistral/Cohere/Bedrock/Vertex packs, drift, Pydantic, npm/ajv+Zod); this MAP asserts the LOCKED-OUT exclusions and selects only static-breadth IN items. | confirmed-against-live |
| SD4 | Fuller-but-convergent v0.3: buildable+provable (tests + docker run + CI contracts) in ONE STEP-2 run, spend-kill-robust (SPINE-FIRST); explicit DEFER list above the line. | IN = 2 network-free data packs + a minimal engine touch, all with CLI/module/tests/docker-proof; Cohere=spine, Mistral=cheap periphery; explicit DEFER-v0.4 + LOCKED-OUT. | confirmed-against-live (scope ceiling — design-level) |
| SD5 | Publish posture decided at gate; default HANDOFF (tag→PyPI IRREVERSIBLE); identity `Dan Mercede <dan@danmercede.com>`; tag string full `v0.3.0`. | `git show v0.2.0:.github/workflows/release.yml` `on.push.tags:[v*]` → PyPI Trusted Publishing (`environment: pypi`, `id-token: write`, no stored token) + GHCR; tags show `v0.2.0` present (released, arc-state `v0.2.0 released`); `pyproject.toml` authors `Dan Mercede <dan@danmercede.com>`; global git email = OAC `Dan.mercede@orionapexcapital.com` (leak risk → LOCAL override required); **INFO I2: v0.2.0 commit actually authored `dan.mercede@gmail.com`** — set declared `dan@danmercede.com` in STEP-2. | confirmed-against-live (identity discrepancy flagged I2) |

SETTLED_DECISION_ROW: SD1 | status=confirmed-against-live;worktree=unverifiable-pending-expected-absent | probe=origin/main=c45d840-v0.2.0;local-main=7fcefd4-stale-v0.1;git-show-v0.2.0-pyproject-0.2.0;tags-v0.1.0+v0.2.0-no-v0.3;no-v0.3-worktree/MAP
SETTLED_DECISION_ROW: SD2 | status=confirmed-against-live | probe=git-show-v0.2.0-pyproject-dependencies-empty;[dev]+live=[]-extras;Dockerfile-cli-no-EXPOSE;CHANGELOG-zero-dependency;rules-globbed
SETTLED_DECISION_ROW: SD3 | status=confirmed-against-live | probe=git-show-v0.2.0-README-deferred-v0.3-roadmap-matches;MAP-asserts-locked-out;IN-static-breadth-only
SETTLED_DECISION_ROW: SD4 | status=confirmed-against-live | probe=2-network-free-data-packs+minimal-engine-touch-with-tests+docker-proof;cohere-spine-mistral-periphery;explicit-defer-v0.4+locked-out
SETTLED_DECISION_ROW: SD5 | status=confirmed-against-live;identity-discrepancy-flagged-I2 | probe=git-show-v0.2.0-release.yml-tags-v*-pypi-trusted-publishing+ghcr;v0.2.0-tag-present-released;pyproject-authors-dan@danmercede.com;global-OAC-leak;v0.2.0-commit-actually-gmail-I2

---

## Publish-Posture Recommendation (SD5)

**Recommended posture: HANDOFF** (mirror the v0.1/v0.2 release).

- Worktree: `~/.worktrees/schemafit-v03`. Branch: `codex/v0.3-mistral-cohere-packs-20260621`. PR target: `OrionArchitekton/schemafit` `main`.
- Identity: `Dan Mercede <dan@danmercede.com>` (the **declared** project identity — pyproject `authors`), set **locally in the worktree before the first commit** (global = OAC email, would leak; v0.2.0's actual gmail commit is the INFO-I2 discrepancy — use the declared address); **no Claude co-author trailer**.
- Version: bump `0.2.0→0.3.0`.
- **Release act (IRREVERSIBLE):** after Dan reviews CI-green + the built artifact, pushing tag **`v0.3.0`** triggers `release.yml` → **PyPI Trusted Publishing** (auto-publish, no re-upload possible) + GHCR image. The tag **is** the publish act. Tag string is the full `v0.3.0` (the v0.2 run had a `v0.2`→`v0.2.0` tag bug — name it correctly).
- **Fail-closed (absolute):** never tag until CI is green on `main` AND the docker-run proof passed. If `v0.3.0` already exists on PyPI/as a tag → **HALT**. Never force-push.
- **Open fork:** who pushes the tag — **Dan** (default), or the STEP-2 run **only if Dan explicitly approves autonomous tag** at this gate.

---

## Read-Before-Approving Synthesis

**The arc.** v0.1.0 shipped the static, stdlib-only, declarative-rule-pack CLI (lint/repair/providers/demo, 3 packs, human/JSON reporters, Docker, Action, tag→PyPI). v0.2.0 shipped the **AMBITIOUS** central-fork arm (corrected from the stale v0.2 appendix per X1): the **SARIF 2.1.0 reporter + opt-in `--live-verify`** (mock-default, tri-state, fail-closed) — and **deferred the Mistral/Cohere packs to v0.3**. v0.3 now deepens the static breadth those packs represent.

**The central-fork close call.** TIGHT (static-breadth packs) vs AMBITIOUS (live-depth drift) is genuinely close on *value* — drift is the more novel, higher-moat feature. It loses on *convergence and need-evidence*: drift is network-at-check-time (harder one-run proof) and the broad pack it would lean on is THIN for Mistral, whereas Cohere's static pack is **rich and primary-sourced today**. SPINE-FIRST + spend-kill robustness (the v0.2 run was spend-killed) decide it: ship the hermetic Cohere spine now, keep drift as the coherent v0.4 increment (it pairs with the now-broader pack surface). Recommend TIGHT; AMBITIOUS preserved as the gate alternative.

**Candidate drops + why.** Cohere structural rules deferred (need 2 new kinds → break the data-only spine; first v0.4 add-back). Drift deferred (network + abstention → not hermetic in this scope). Pydantic deferred (sizeable + adds an extra). Bedrock/Vertex deferred-BIG (platform multiplexers → invented-rule risk). npm/ajv+Zod deferred-BIG (second ecosystem; npm slot unclaimed but too big). v0.1/v0.2 rebuild dropped. The honest risk (W1): the moat is packaging, not knowledge — which is *why* shipping the convergent static-breadth cut now and iterating beats over-investing. The honest sizing (W2/W3): Mistral is thin and example-derived; packs are a minimal engine touch, not zero-engine.

---

## STEP-2 Prep Appendix

Consistency check: the staged STEP-2 implement prompt (`~/.orion/goal-prompts/schemafit-v03-implement-20260621.md`) is **generic across cut-lines** (it explicitly handles both packs and drift), already carries the correct **worktree-off-freshly-fetched-origin-main** lines (its §SETTLED-DECISIONS 1 + gotcha "worktree-off-origin-main") and the **full `v0.3.0` tag** discipline (its GOAL line: "Tag string is the full `v0.3.0` (not `v0.3`)"), and uses a `<slug>` placeholder resolved from this MAP. **No edit to the implement prompt is required** (this run's single write is the MAP). Set **`<slug>` = `mistral-cohere-packs`** ⇒ branch `codex/v0.3-mistral-cohere-packs-20260621`.

**Worktree (off freshly-fetched origin/main, local identity before first commit):**
```bash
git -C ~/src/schemafit fetch origin main --tags
git worktree add ~/.worktrees/schemafit-v03 -b codex/v0.3-mistral-cohere-packs-20260621 origin/main
cd ~/.worktrees/schemafit-v03
git config user.name "Dan Mercede"
git config user.email "dan@danmercede.com"
# VERIFY the worktree carries v0.2.0 (NOT stale v0.1) before building:
test -f schemafit/live.py && grep -q sarif schemafit/report.py && grep -q '^version = "0.2.0"' pyproject.toml && echo "OK: carries v0.2.0"
```

**Modules/data/tests to add/update:**
- `schemafit/linter.py`: `PROVIDERS += ("mistral","cohere")` (`:11`). **No `apply_rule` change** (rules reuse existing kinds).
- `schemafit/rules/cohere.json`: ~10 `forbidden_keyword` error rules (`allOf`/`oneOf`/`not` → `manual`; `minimum`/`maximum`/`minItems`/`maxItems`/`minLength`/`maxLength`/`uniqueItems` → `strip`); every `doc_url=https://docs.cohere.com/docs/structured-outputs`.
- `schemafit/rules/mistral.json`: 2 rules (`object_requires` additionalProperties:false/`set_false` + `object_all_properties_required`/`fill_required`); `doc_url=https://docs.mistral.ai/capabilities/structured-output/custom_structured_output/`; **re-verify against the canonical render** (W2); `strict:true`+`codestral-mamba` = README notes only.
- `tests/test_lint.py`: new Cohere + Mistral catch/pass cases; **FIX `test_unknown_provider_raises` (`:152-154`)** to use `"bedrock"`.
- `tests/test_cli.py`: **UPDATE/RETITLE `test_providers_matrix_is_exactly_three` (`:91-95`)** to the 5-provider list.
- `fixtures/cohere-bad.json`, `fixtures/mistral-bad.json`; ensure `fixtures/portable-good.json` stays clean across all 5.
- `schemafit/cli.py`: update the two `--provider` help strings (`:218`,`:235`).
- `pyproject.toml` version `0.2.0→0.3.0` (package-data already globs `rules/*.json`); `README.md` provider table 3→5; `CHANGELOG.md` `[0.3.0]`.
- `.github/workflows/ci.yml`: extend the PASS contract to 5 providers (keep the FAIL contract).

**Test commands (match schemafit CI exactly — `ruff check`, NOT `ruff format --check`):**
```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
ruff check .
pytest -q
schemafit demo
# the two fixture exit-code contracts:
schemafit lint fixtures/anthropic-bad.json --provider anthropic ; test $? -ne 0     # MUST be non-zero
schemafit lint fixtures/portable-good.json --provider openai,anthropic,gemini,mistral,cohere  # MUST exit 0
```

**Docker proof (fixture-based, no network, no public port):**
```bash
docker build -t schemafit:v03 .
docker run --rm    schemafit:v03 providers                                                              # expect 5 incl mistral,cohere
docker run --rm -i schemafit:v03 lint - --provider cohere  < fixtures/cohere-bad.json  ; echo "exit=$?" # expect exit 1 + cohere-* finding
docker run --rm -i schemafit:v03 lint - --provider mistral < fixtures/mistral-bad.json ; echo "exit=$?" # expect exit 1 + mistral-* finding
docker run --rm -i schemafit:v03 lint - --provider cohere --format sarif < fixtures/cohere-bad.json     # expect SARIF ruleId cohere-*
```
Expected proof lines: `providers` lists `mistral` and `cohere`; `[cohere] FAIL` + a `cohere-*` rule id + `exit=1`; `[mistral] FAIL` + a `mistral-*` rule id + `exit=1`; SARIF `"ruleId": "cohere-…"` + `"version": "2.1.0"` + `"name": "schemafit"`.

**Local-first + version proof:**
```bash
pip install .                          # no extras, clean env — succeeds
schemafit --help ; schemafit demo      # run with NO external service / NO network
grep '^version' pyproject.toml         # 0.3.0
grep -n 'dependencies = \[\]' pyproject.toml   # core dep-free intact
```

**Release procedure (HANDOFF default; tag = IRREVERSIBLE PyPI publish):**
```bash
# after PR merged + CI green on main + docker proof passed:
git -C ~/src/schemafit fetch origin main --tags
git -C ~/src/schemafit checkout main && git -C ~/src/schemafit pull --ff-only origin main
git -C ~/src/schemafit tag -a v0.3.0 -m "schemafit v0.3.0"
git -C ~/src/schemafit push origin v0.3.0    # <-- release.yml auto-publishes to PyPI (Trusted Publishing) + GHCR. IRREVERSIBLE.
gh release create v0.3.0 --repo OrionArchitekton/schemafit --title "schemafit v0.3.0" \
  --notes "v0.3.0: Cohere + Mistral provider rule packs (matrix 3→5). Core dep-free."
# rollback: revert the PR; a PyPI version cannot be re-uploaded (yank, not delete).
```

**Exact STEP-2 fire line (fire only after Dan approves THIS MAP):**
```text
/goal ultracode -- Execute the GOAL BRIEF at ~/.orion/goal-prompts/schemafit-v03-implement-20260621.md end to end; load + VERIFY the recon seed ~/.orion/goal-prompts/schemafit-v03-20260621.recon.json AND the Dan-APPROVED MAP ~/.orion/maps/schemafit-v03-MAP-20260621.md FIRST. This MUTATES a worktree off the EXISTING repo ~/src/schemafit (worktree off FRESHLY-FETCHED origin/main, v0.2.0 base; branch codex/v0.3-mistral-cohere-packs-20260621; NOT a new repo, NOT the stale local checkout) and may RELEASE v0.3.0 per the GATE-APPROVED posture; release is FAIL-CLOSED on the test+docker proofs and the v0.3.0 tag→PyPI publish is IRREVERSIBLE (v0.2.0 already on PyPI). PRECONDITION: the MAP names the v0.3 IN cut-line = TIGHT (Cohere rich pack SPINE + Mistral thin pack + the minimal provider-registry engine touch), central fork resolved (drift detection DEFER-v0.4), the DEFER-to-v0.4 list, the LOCKED-OUT set, dep posture (core dependencies=[]), the test+docker proof plan, and HANDOFF publish posture; if missing/unresolved -> FINAL STATUS: INCOMPLETE — precondition unmet. Build ONLY the approved IN set (Cohere + Mistral packs + the registry/test/CI touch); the packs are DATA + a minimal engine touch (PROVIDERS tuple + FIX test_unknown_provider_raises + UPDATE test_providers_matrix + help strings) — NO apply_rule/repair engine logic (rules reuse the 5 kinds + 4 strategies); every Cohere rule primary-sourced to docs.cohere.com/docs/structured-outputs; Mistral is 2 example-derived rules only (re-verify canonical docs.mistral.ai; strict+codestral-mamba are README notes, NOT rules; no invented keyword-blocklist); defer drift/Cohere-structural-new-kinds/Pydantic/Bedrock-Vertex/JS-port; never touch the LOCKED-OUT set. SPINE-FIRST: the Cohere pack is the spine (must be real+proven); Mistral degrades to a self-audit note under a spend-kill, never a hollow stub. Condition met when ONE final turn shows ALL with FRESH same-turn tool results: (1) ls/grep of the approved MAP proving the TIGHT cut + HANDOFF posture, then git -C ~/.worktrees/schemafit-v03 rev-parse --abbrev-ref HEAD proving codex/v0.3-mistral-cohere-packs-* off origin/main + log --oneline + diff --stat origin/main; (2) git log -1 --format='%an <%ae>' = Dan Mercede <dan@danmercede.com>, NO Claude trailer; (3) FRESH full test run: ruff check + pytest -q + schemafit demo all exit 0 with summary, proving each new pack (NEW failure mode: cohere-bad.json + mistral-bad.json FAIL, portable-good PASSES across all 5) AND the full v0.1+v0.2 surface (SARIF, --live-verify) still green; the two CI exit-code contracts hold (PASS extended to 5 providers); (4) FRESH docker build success + docker run demonstrating the NEW capability (providers lists 5 incl mistral+cohere; a cohere-* and a mistral-* finding on the bad fixtures; SARIF cohere-* ruleId) — fixture-based, no network/public port; (5) FRESH local-first proof: pip install . (no extras) + schemafit --help/demo with NO service/network; pyproject core dependencies=[] (any new dep ONLY under optional-extras), version 0.3.0; CHANGELOG/README diff; (6) RELEASE per HANDOFF: PR to OrionArchitekton/schemafit open (URL), gitleaks/secret-scan clean, the post-merge git tag v0.3.0 && git push origin v0.3.0 release command printed + dry-verified, NOTHING tagged (unless Dan approved autonomous tag at the gate -> then gh release view v0.3.0 + tag landed + HEAD==origin/main fetched); each commit HEAD advanced, NO force-push; (7) SELF-AUDIT TABLE each DELIVER -> criterion -> evidence -> MET/UNMET-with-blocker, + ATTESTATION: only the TIGHT IN set built (DEFER+LOCKED-OUT untouched), worktree off FRESH origin/main carrying v0.2.0 (not stale local), work confined to the worktree (git -C ~/src/schemafit status --porcelain unchanged vs turn-1 baseline), core dep-free, no secret VALUE, no force-push, no premature tag. ALT terminal: FINAL STATUS: INCOMPLETE with a date -u >= a later bound, listing every unmet item with quoted tool-result evidence of an external blocker after >=2 remediation attempts (release blocker: never a destructive retry); must not claim completion.
```

---

## GATE

**SETTLED-DECISIONS ASSERT (banner — not re-decided here):** SD1 existing-repo worktree off freshly-fetched origin/main → 0.3.0 · SD2 static local-first, core `dependencies=[]` · SD3 deepen the static wedge, **LOCKED-OUT = hosted SaaS service / browser UI-dashboard / runtime validation proxy-gateway (asserted-excluded)** · SD4 fuller-but-convergent SPINE-FIRST v0.3 · SD5 publish posture decided here (default HANDOFF; tag→PyPI IRREVERSIBLE; identity `Dan Mercede <dan@danmercede.com>`). DEFER-BIG (not locked-out): Bedrock/Vertex, npm/ajv JS-port, Zod. **No locked value is being re-opened.**

**Genuinely open forks for Dan (only these):**
1. **Approve the recommended TIGHT cut** — IN = Cohere rich pack (SPINE) + Mistral thin pack + the minimal provider-registry engine touch (matrix 3→5); drift detection deferred to v0.4.
2. **OR redirect to the central-fork AMBITIOUS alternative** — build automatic rule-pack DRIFT detection on the shipped `live.py` foundation (mock-default, env/flag-gated real fetch, abstention-safe, SARIF/Finding reuse), paired with the thin Mistral pack only (dropping Cohere's rich pack to stay convergent).
3. **Confirm publish posture** — HANDOFF (default; Dan pushes the irreversible `v0.3.0` tag after reviewing CI + artifact), OR explicitly authorize the STEP-2 run to push the tag autonomously after all proofs pass.

Awaiting explicit **"go"**. This step does not chain into building.

---

## Self-Audit Table

SELF_AUDIT_COUNTS: scoreboard_rows=10 | in_design_rows=3 | settled_decision_rows=5 | defer_rows=5 | locked_out_rows=3 | deliver_rows=12

| deliver item | criterion | evidence pointer | status |
|---|---|---|---|
| Extension-Point Map | candidates → real file:line attachment points (v0.2.0 tree) | `## Extension-Point Map` | MET |
| Landscape re-scan | each angle ≥1 live cited source, abstention-safe; NAME tool-schema-lint + differentiators; verdict | `## Landscape Re-Scan` + `LANDSCAPE_VERDICT` | MET |
| Candidate scoreboard | every candidate: 4 scores + need-evidence + verdict, greppable | `SCOREBOARD_ROW` C1–C10 | MET |
| Central-fork resolution | TIGHT vs AMBITIOUS, recommendation+rationale, alternative kept | `## Central-Fork Resolution` + `CENTRAL_FORK_RESOLUTION` | MET |
| v0.3 IN-set design | each IN: CLI, module, dep posture, tests(+new failure mode), docker proof, version/docs | `IN_DESIGN_ROW` ×3 + IN sections | MET |
| DEFER-to-v0.4 + LOCKED-OUT | explicit residue + asserted exclusions, greppable | `DEFER_ROW` ×5, `LOCKED_OUT_ROW` ×3 | MET |
| Settled-decision EVIDENCE | SD1–SD5 confirmed-against-live (or unverifiable-pending) | `SETTLED_DECISION_ROW` SD1–SD5 | MET |
| Publish-posture recommendation | HANDOFF default + worktree/branch/PR + IRREVERSIBLE tag→PyPI | `## Publish-Posture Recommendation` | MET |
| Read-before-approving synthesis | arc (v0.2 shipped AMBITIOUS) + central-fork close call + drops | `## Read-Before-Approving Synthesis` | MET |
| STEP-2 prep appendix | worktree cmd (slug set), modules, test cmds, docker proof + expected lines, release, fire line | `## STEP-2 Prep Appendix` | MET |
| GATE section | only open forks + settled-decisions assert banner (incl LOCKED-OUT) | `## GATE` | MET |
| No-prior-v0.3-artifact attestation | no v0.3 branch/tag/MAP; tags only v0.1.0,v0.2.0; 0 issues; PRs merged | `## No-prior-v0.3-artifact attestation` | MET |

## Rails Attestation

This Step-1 run posture (fresh proof printed in the closing turn):
- Intended file mutation: **this MAP only** (`~/.orion/maps/schemafit-v03-MAP-20260621.md`). The staged STEP-2 prompt was **not edited** (slug recorded here instead).
- Worktree/branch/tag creation: **none**. Repo edits: **none**. Builds/tests/docker: **not run**.
- Web access: search/open **GET-only**; no forms/stars/comments/logins.
- Secrets: **no secret values** surfaced (provider doc URLs are public; no keys).
- Read repo SHAPE via `git show v0.2.0:…`, never the stale working tree (X2).
- Concurrent other-session `~/.orion/` artifacts (e.g. `schemafit-arc-state.json`) and hook-owned state (`*.nudged`, `handoffs/state/**`) are **not** this run's mutations.
- Canonical baseline: `git -C ~/src/schemafit status --porcelain` empty at turn-1 (`7fcefd4`); closing turn must show it unchanged.
