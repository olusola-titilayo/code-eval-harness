"""Command line entry point.

    python -m code_eval_harness PROBLEM.json SAMPLE.py [SAMPLE.py ...]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .metrics import summarize
from .runner import run_candidate


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="code_eval_harness", description=__doc__.splitlines()[0])
    parser.add_argument("problem", type=Path, help="JSON file with entry_point and cases")
    parser.add_argument("samples", type=Path, nargs="+", help="candidate solution files")
    parser.add_argument("--timeout", type=float, default=2.0, help="seconds per test case")
    parser.add_argument("--verbose", "-v", action="store_true", help="print every failing case")
    args = parser.parse_args(argv)

    problem = json.loads(args.problem.read_text())
    results = []
    for path in args.samples:
        run = run_candidate(path.read_text(), problem["entry_point"], problem["cases"], args.timeout)
        results.append(run)
        mark = "PASS" if run.passed else "FAIL"
        print(f"{mark}  {path.name}  ({run.pass_rate:.0%} of cases)")
        if args.verbose:
            for case in run.cases:
                if case.status != "passed":
                    detail = case.error or (f"got {case.actual!r}" if case.status == "failed" else "")
                    print(f"      {case.status:<8} args={case.args!r} expected={case.expected!r} {detail}")
    print(json.dumps(summarize(results), indent=2))
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
