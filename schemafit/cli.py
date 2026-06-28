"""schemafit command-line interface.

Commands:
  lint <schema.json> --provider openai[,anthropic,gemini]   # exit 1 on violations
        [--format human|json|sarif] [--strict] [--live-verify]
  repair <schema.json> --provider <p> [--out fixed.json]
  providers
  demo                                                       # hermetic proof
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace

from . import __version__, report
from .linter import PROVIDERS, has_errors, lint, lint_multi, load_rule_pack
from .live import resolve_drift_doc_url, verify_providers
from .model import Finding
from .repair import repair

# A schema that is valid for OpenAI but deliberately trips Anthropic (rejected
# validation keywords) and Gemini (anyOf). Used by `demo` for a hermetic proof.
DEMO_BAD_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string", "minLength": 1, "maxLength": 50},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0, "maximum": 120},
        "status": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    },
    "required": ["name", "email", "age", "status"],
}


def _load_schema(path: str) -> object:
    if path == "-":
        # robust for docker stdin / pipe / ENTRYPOINT cases
        data = sys.stdin.read()
        return json.loads(data)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _parse_providers(spec: str) -> list[str]:
    provs = [p.strip() for p in spec.split(",") if p.strip()]
    if not provs:
        raise SystemExit("error: --provider requires at least one provider")
    for p in provs:
        if p not in PROVIDERS:
            raise SystemExit(f"error: unknown provider {p!r} (choose from {', '.join(PROVIDERS)})")
    return provs


def cmd_lint(args: argparse.Namespace) -> int:
    providers = _parse_providers(args.provider)
    all_results: dict[str, dict] = {}
    live_all: dict[str, dict[str, bool | None]] = {}
    overall_fail = False
    for path in args.schemas:
        try:
            schema = _load_schema(path)
            results = lint_multi(schema, providers)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: cannot read schema {path!r}: {exc}", file=sys.stderr)
            return 2
        except RecursionError:
            print(f"error: schema {path!r} is too deeply nested to lint safely", file=sys.stderr)
            return 2

        live_results = None
        # v0.5: auto-enable live-verify in docker (ENV) without changing proof cmd string
        auto = os.environ.get("SCHEMAFIT_AUTO_LIVE_VERIFY") == "1"
        live_verify = getattr(args, "live_verify", False) or auto
        if live_verify:
            # decide simulate_drift for hermetic proof (env for -, or filename for file case)
            simulate_drift = os.environ.get("SCHEMAFIT_MOCK_DRIFT") == "1"
            if not simulate_drift:
                for s in args.schemas:
                    if "drift-mock-bad" in s:
                        simulate_drift = True
                        break
            live_results = verify_providers(schema, providers, simulate_drift=simulate_drift)
            # Annotate each finding with its provider's live acceptance verdict.
            for prov, lr in live_results.items():
                static_findings = results[prov]
                had_static_error = has_errors(static_findings)
                results[prov] = [
                    replace(f, confirmed_by_provider=lr.accepted) for f in static_findings
                ]
                # Fail-closed reporting parity: a provider that actively REJECTED
                # the schema must surface as a first-class finding so the rejection
                # appears in JSON and SARIF (not only the exit code). Otherwise a
                # static-pass / live-reject run exits 1 while emitting an EMPTY
                # SARIF run, which GitHub code-scanning treats as "all clear" and
                # can clear stale alerts. Abstain (None) is not a rejection.
                if lr.accepted is False:
                    doc_url = ""
                    if had_static_error:
                        rule_id = f"{prov}-live-rejection"
                        kind = "live-rejection"
                        reason = (
                            f"Live provider verification rejected the schema "
                            f"({lr.client}): {lr.detail}"
                        )
                    else:
                        # v0.5 AMBITIOUS: rule-pack DRIFT (static PASS + live REJECT)
                        # The pack did not catch a constraint that live enforces;
                        # signals pack drift vs provider docs (doc_url foundation).
                        rule_id = f"{prov}-drift"
                        kind = "drift"
                        reason = (
                            f"Rule-pack drift detected for {prov}: live verification "
                            f"rejected the schema but static pack had no violations. "
                            f"Pack may lag provider docs (client={lr.client}): {lr.detail}"
                        )
                        # use pure helper: first rules[].doc_url, never pack["doc"]
                        try:
                            pack = load_rule_pack(prov)
                            doc_url = resolve_drift_doc_url(pack)  # from live
                        except Exception:
                            doc_url = ""
                    results[prov].append(
                        Finding(
                            provider=prov,
                            rule_id=rule_id,
                            kind=kind,
                            node_pointer="#",
                            json_pointer="#",
                            keyword="",
                            reason=reason,
                            severity="error",
                            doc_url=doc_url,
                            confirmed_by_provider=lr.accepted,
                        )
                    )
            live_all[path] = {prov: lr.accepted for prov, lr in live_results.items()}

        all_results[path] = results

        if args.strict:
            failed = any(findings for findings in results.values())
        else:
            failed = any(has_errors(findings) for findings in results.values())
        if live_verify:
            # Fail-closed: a provider that actively REJECTED the schema fails CI,
            # even if the static pass would not have. Abstain (None) does not.
            failed = failed or any(v is False for v in live_all.get(path, {}).values())
        overall_fail = overall_fail or failed

        if args.format == "human":
            if len(args.schemas) > 1:
                print(f"== {path} ==")
            print(report.format_human(results))
            if live_results is not None:
                for prov in providers:
                    lr = live_results[prov]
                    print(
                        f"[{prov}] LIVE-VERIFY confirmed_by_provider={lr.accepted} "
                        f"client={lr.client} ({lr.detail})"
                    )

    if args.format == "json":
        print(report.format_json_multi(all_results, live_all or None))
    elif args.format == "sarif":
        print(report.format_sarif_multi(all_results))
    return 1 if overall_fail else 0


def cmd_repair(args: argparse.Namespace) -> int:
    if args.provider not in PROVIDERS:
        raise SystemExit(f"error: unknown provider {args.provider!r}")
    try:
        schema = _load_schema(args.schema)
        fixed, rep = repair(schema, args.provider)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read schema {args.schema!r}: {exc}", file=sys.stderr)
        return 2
    except RecursionError:
        print(
            f"error: schema {args.schema!r} is too deeply nested to repair safely",
            file=sys.stderr,
        )
        return 2
    rendered = json.dumps(fixed, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(rendered + "\n")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(rendered)
    print(
        f"repair: auto_fixed={len(rep['auto_fixed'])} "
        f"lossy={len(rep['lossy'])} manual_required={len(rep['manual_required'])}",
        file=sys.stderr,
    )
    for tag in rep["manual_required"]:
        print(f"  MANUAL {tag}", file=sys.stderr)
    return 0


def cmd_providers(_args: argparse.Namespace) -> int:
    for p in PROVIDERS:
        print(p)
    return 0


def cmd_demo(_args: argparse.Namespace) -> int:
    """Hermetic end-to-end proof of the spine: lint -> repair -> matrix."""
    print("== schemafit demo ==")
    before = lint(DEMO_BAD_SCHEMA, "anthropic")
    n_before = sum(1 for f in before if f.severity == "error")
    exit_before = 1 if has_errors(before) else 0
    print(f"PROVIDER=anthropic INPUT=demo-bad VIOLATIONS={n_before} EXIT={exit_before}")
    if before:
        print(
            f"VIOLATION_PATH={before[0].json_pointer} "
            f"(keyword: {before[0].keyword} -> rejected by anthropic)"
        )

    fixed, rep = repair(DEMO_BAD_SCHEMA, "anthropic")
    after = lint(fixed, "anthropic")
    n_after = sum(1 for f in after if f.severity == "error")
    exit_after = 1 if has_errors(after) else 0
    print(
        f"--- after `schemafit repair --provider anthropic` --- "
        f"VIOLATIONS={n_after} EXIT={exit_after} auto_fixed={len(rep['auto_fixed'])}"
    )

    matrix = lint_multi(DEMO_BAD_SCHEMA, list(PROVIDERS))
    rendered = " ".join(
        f"{p}={'FAIL' if has_errors(matrix[p]) else 'PASS'}" for p in PROVIDERS
    )
    print(f"MULTI: {rendered}")
    gem_warns = sum(1 for f in matrix["gemini"] if f.severity == "warning")
    print(f"NOTE: gemini portability warnings={gem_warns} (version-sensitive, non-failing)")

    ok = has_errors(before) and not has_errors(after)
    print("PROOF_OK" if ok else "PROOF_FAILED")
    return 0 if ok else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schemafit",
        description="Provider-aware structured-output / JSON-Schema CI linter.",
    )
    parser.add_argument("--version", action="version", version=f"schemafit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_lint = sub.add_parser("lint", help="lint one or more schemas against one or more providers")
    p_lint.add_argument("schemas", nargs="+", help="schema JSON file(s) ('-' = stdin)")
    p_lint.add_argument(
        "--provider", required=True, help=f"comma list: {','.join(PROVIDERS)}"
    )
    p_lint.add_argument("--format", choices=("human", "json", "sarif"), default="human")
    p_lint.add_argument("--strict", action="store_true", help="also fail (exit 1) on warnings")
    p_lint.add_argument(
        "--live-verify",
        dest="live_verify",
        action="store_true",
        help=(
            "opt-in: confirm the schema against each provider via a mockable client "
            "(MOCK default — no network/key; real call only when the provider's API key "
            "is in the env). Fails closed on a provider rejection."
        ),
    )
    p_lint.set_defaults(func=cmd_lint)

    p_rep = sub.add_parser("repair", help="emit a best-effort provider-valid variant")
    p_rep.add_argument("schema", help="path to a JSON schema file, or '-' for stdin")
    p_rep.add_argument(
        "--provider", required=True, help=f"one of: {'|'.join(PROVIDERS)}"
    )
    p_rep.add_argument("--out", help="write fixed schema here (default: stdout)")
    p_rep.set_defaults(func=cmd_repair)

    p_prov = sub.add_parser("providers", help="list supported providers")
    p_prov.set_defaults(func=cmd_providers)

    p_demo = sub.add_parser("demo", help="run a hermetic end-to-end proof")
    p_demo.set_defaults(func=cmd_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
