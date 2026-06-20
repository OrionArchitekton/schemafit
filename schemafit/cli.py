"""schemafit command-line interface.

Commands:
  lint <schema.json> --provider openai[,anthropic,gemini]   # exit 1 on violations
  repair <schema.json> --provider <p> [--out fixed.json]
  providers
  demo                                                       # hermetic proof
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, report
from .linter import PROVIDERS, has_errors, lint, lint_multi
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
        return json.load(sys.stdin)
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
        all_results[path] = results
        if args.strict:
            failed = any(findings for findings in results.values())
        else:
            failed = any(has_errors(findings) for findings in results.values())
        overall_fail = overall_fail or failed
        if args.format != "json":
            if len(args.schemas) > 1:
                print(f"== {path} ==")
            print(report.format_human(results))
    if args.format == "json":
        print(report.format_json_multi(all_results))
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
    p_lint.add_argument("--provider", required=True, help="comma list: openai,anthropic,gemini")
    p_lint.add_argument("--format", choices=("human", "json"), default="human")
    p_lint.add_argument("--strict", action="store_true", help="also fail (exit 1) on warnings")
    p_lint.set_defaults(func=cmd_lint)

    p_rep = sub.add_parser("repair", help="emit a best-effort provider-valid variant")
    p_rep.add_argument("schema", help="path to a JSON schema file, or '-' for stdin")
    p_rep.add_argument("--provider", required=True, help="one of: openai|anthropic|gemini")
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
