import pytest

from code_eval_harness import pass_at_k, summarize
from code_eval_harness.runner import CaseResult, RunResult


@pytest.mark.parametrize(
    "n,c,k,expected",
    [(10, 0, 1, 0.0), (10, 10, 1, 1.0), (10, 5, 1, 0.5), (10, 1, 10, 1.0), (4, 2, 2, 1 - 1 / 6)],
)
def test_pass_at_k_known_values(n, c, k, expected):
    assert pass_at_k(n, c, k) == pytest.approx(expected)


def test_pass_at_k_is_monotonic_in_k():
    values = [pass_at_k(20, 3, k) for k in range(1, 21)]
    assert values == sorted(values)


@pytest.mark.parametrize("n,c,k", [(5, 6, 1), (5, -1, 1), (5, 2, 0), (5, 2, 6)])
def test_pass_at_k_rejects_bad_input(n, c, k):
    with pytest.raises(ValueError):
        pass_at_k(n, c, k)


def _run(*statuses):
    return RunResult([CaseResult([], None, s) for s in statuses])


def test_summarize_counts_samples_and_statuses():
    report = summarize([_run("passed", "passed"), _run("passed", "timeout"), _run("failed", "error")])
    assert report["samples"] == 3 and report["correct"] == 1
    assert report["pass@1"] == pytest.approx(1 / 3, abs=1e-4)
    assert report["cases_passed"] == 3 and report["cases_timeout"] == 1
    assert "pass@5" not in report
