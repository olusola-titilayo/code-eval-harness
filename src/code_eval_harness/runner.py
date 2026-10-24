"""Execute a candidate solution against test cases, one subprocess per case.

Each case runs in a fresh interpreter with a wall-clock timeout, so an infinite
loop, a crash or a ``sys.exit`` in one case cannot affect the others.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any, List, Sequence

# The driver is run as a separate script so the candidate never shares a
# process with the harness. It prints exactly one JSON line on stdout.
_DRIVER = r'''
import json, sys, traceback, io, contextlib
payload = json.loads(sys.stdin.read())
ns = {}
out = io.StringIO()
try:
    with contextlib.redirect_stdout(out):
        exec(compile(payload["source"], "<candidate>", "exec"), ns)
        fn = ns.get(payload["entry_point"])
        if not callable(fn):
            raise NameError("entry point %r not defined" % payload["entry_point"])
        result = fn(*payload["args"])
    print(json.dumps({"ok": True, "result": result}))
except BaseException as exc:  # report everything, including SystemExit
    print(json.dumps({"ok": False, "error": type(exc).__name__ + ": " + str(exc)}))
'''


@dataclass
class CaseResult:
    args: List[Any]
    expected: Any
    status: str  # "passed" | "failed" | "error" | "timeout"
    actual: Any = None
    error: str = ""
    seconds: float = 0.0


@dataclass
class RunResult:
    cases: List[CaseResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return bool(self.cases) and all(c.status == "passed" for c in self.cases)

    @property
    def pass_rate(self) -> float:
        if not self.cases:
            return 0.0
        return sum(c.status == "passed" for c in self.cases) / len(self.cases)


def _normalise(value: Any) -> Any:
    """Round-trip through JSON so tuples/lists compare the way they serialise."""
    return json.loads(json.dumps(value))


def run_candidate(
    source: str,
    entry_point: str,
    cases: Sequence[dict],
    timeout: float = 2.0,
) -> RunResult:
    """Run ``entry_point`` from ``source`` against each ``{"args": [...], "expected": ...}`` case."""
    with tempfile.TemporaryDirectory() as tmp:
        driver = os.path.join(tmp, "driver.py")
        with open(driver, "w") as fh:
            fh.write(_DRIVER)

        result = RunResult()
        for case in cases:
            args, expected = list(case["args"]), case["expected"]
            payload = json.dumps({"source": source, "entry_point": entry_point, "args": args})
            start = time.perf_counter()
            try:
                proc = subprocess.run(
                    [sys.executable, "-I", driver],
                    input=payload,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tmp,
                )
            except subprocess.TimeoutExpired:
                result.cases.append(CaseResult(args, expected, "timeout", seconds=timeout))
                continue
            elapsed = time.perf_counter() - start

            lines = proc.stdout.strip().splitlines()
            try:
                report = json.loads(lines[-1])
            except (IndexError, json.JSONDecodeError):
                err = proc.stderr.strip().splitlines()[-1:] or ["no output from driver"]
                result.cases.append(CaseResult(args, expected, "error", error=err[0], seconds=elapsed))
                continue

            if not report["ok"]:
                result.cases.append(CaseResult(args, expected, "error", error=report["error"], seconds=elapsed))
            elif _normalise(report["result"]) == _normalise(expected):
                result.cases.append(CaseResult(args, expected, "passed", report["result"], seconds=elapsed))
            else:
                result.cases.append(CaseResult(args, expected, "failed", report["result"], seconds=elapsed))
        return result
