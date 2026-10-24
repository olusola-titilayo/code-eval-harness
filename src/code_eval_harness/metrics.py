"""Scoring helpers."""

from __future__ import annotations

from math import comb
from typing import Dict, Iterable

from .runner import RunResult


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator (Chen et al., 2021).

    Given ``n`` samples of which ``c`` are correct, return the probability that
    at least one of ``k`` samples drawn without replacement is correct.
    """
    if not 0 <= c <= n:
        raise ValueError("need 0 <= c <= n")
    if not 1 <= k <= n:
        raise ValueError("need 1 <= k <= n")
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def summarize(results: Iterable[RunResult]) -> Dict[str, float]:
    """Aggregate several samples for one problem into a small report."""
    results = list(results)
    n = len(results)
    c = sum(r.passed for r in results)
    statuses: Dict[str, int] = {}
    for r in results:
        for case in r.cases:
            statuses[case.status] = statuses.get(case.status, 0) + 1
    report: Dict[str, float] = {"samples": n, "correct": c}
    for k in (1, 5, 10):
        if k <= n:
            report[f"pass@{k}"] = round(pass_at_k(n, c, k), 4)
    report.update({f"cases_{s}": v for s, v in sorted(statuses.items())})
    return report
