#!/usr/bin/env python3
"""Semantic regression tests for the seed-built Kix front end.

Accept cases must pass `--check` with exit code 0.  Reject cases must fail with
a non-zero exit code, a stable E6xxx diagnostic code (from the sibling `.code`
file), and a `file:line:column` location.  Diagnostics are matched structurally
rather than by free-form text.
"""

import argparse
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tests" / "kix" / "semantic"

LOCATION = re.compile(r"-->\s+\S+:\d+:\d+")


def run(compiler: Path, source: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(compiler), "--lang=kix", "--check", str(source)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def check_accept(compiler: Path) -> int:
    failures = 0
    for source in sorted((CASES / "accept").glob("*.kix")):
        result = run(compiler, source)
        if result.returncode != 0:
            failures += 1
            print(f"FAIL {source.name}: unexpected semantic failure")
            print(result.stderr or result.stdout)
        else:
            print(f"ok   accept/{source.name}")
    return failures


def check_reject(compiler: Path) -> int:
    failures = 0
    for source in sorted((CASES / "reject").glob("*.kix")):
        expected = source.with_suffix(".code").read_text().strip()
        result = run(compiler, source)
        diagnostic = result.stderr + result.stdout
        problems = []
        if result.returncode == 0:
            problems.append("expected a non-zero exit code")
        if expected not in diagnostic:
            problems.append(f"missing diagnostic code {expected}")
        if not LOCATION.search(diagnostic):
            problems.append("missing file:line:column location")
        if problems:
            failures += 1
            print(f"FAIL reject/{source.name}: {', '.join(problems)}")
            print(diagnostic)
        else:
            print(f"ok   reject/{source.name} ({expected})")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", type=Path, default=ROOT / "build" / "kixc-stage0")
    args = parser.parse_args()
    compiler = args.compiler.resolve()

    failures = check_accept(compiler) + check_reject(compiler)
    if failures:
        print(f"{failures} Kix semantic test(s) failed")
        return 1
    print("all Kix semantic tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
