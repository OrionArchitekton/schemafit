#!/usr/bin/env python3
"""Reproduce the schemafit real-world benchmark.

Runs `schemafit lint` over a directory of JSON Schema files against all five
providers and prints the aggregate (rejection rate, per-provider, top violations).

Usage:
    pip install schemafit
    python benchmarks/run.py path/to/schemas/   # a dir of *.json schema files

The 50 schemas behind benchmarks/RESULTS.md are NOT vendored (they belong to
their upstream projects); every source is listed with a raw URL in
benchmarks/sources.tsv so you can audit or re-fetch them. Point this script at
your OWN tool/output schemas to see what your providers would reject.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import subprocess
import sys

PROVIDERS = ["openai", "anthropic", "gemini", "mistral", "cohere"]


def lint(path: str) -> dict | None:
    p = subprocess.run(
        ["schemafit", "lint", path, "--provider", ",".join(PROVIDERS), "--format", "json"],
        capture_output=True, text=True,
    )
    try:
        return next(iter(json.loads(p.stdout).values()))
    except Exception:
        return None


def main(schema_dir: str) -> int:
    files = sorted(glob.glob(os.path.join(schema_dir, "*.json")))
    if not files:
        print(f"no *.json schemas found in {schema_dir!r}", file=sys.stderr)
        return 2
    err_kw = collections.Counter()
    prov_err = collections.Counter()
    fail_any = clean_all = 0
    for fn in files:
        r = lint(fn)
        if r is None:
            continue
        any_err = any_warn = False
        for prov in PROVIDERS:
            fs = r.get(prov, {}).get("findings", [])
            errs = [f for f in fs if f.get("severity") == "error"]
            if errs:
                prov_err[prov] += 1
                any_err = True
                for f in errs:
                    err_kw[f.get("keyword")] += 1
            if any(f.get("severity") == "warning" for f in fs):
                any_warn = True
        fail_any += any_err
        clean_all += (not any_err and not any_warn)
    n = len(files)
    print(f"schemas: {n}")
    print(f"would error on >=1 provider: {fail_any} ({100*fail_any//n}%)")
    print(f"perfectly clean on all five: {clean_all} ({100*clean_all//n}%)")
    print("per-provider errors:", dict(prov_err))
    print("top error keywords:", err_kw.most_common(8))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "schemas"))
