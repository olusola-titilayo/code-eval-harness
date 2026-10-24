# code-eval-harness

![CI](https://github.com/olusola-titilayo/code-eval-harness/actions/workflows/ci.yml/badge.svg)

A small, dependency-free harness for grading code solutions — the kind of loop used to evaluate
LLM-generated code. Each test case runs in a **fresh, isolated Python subprocess** with a wall-clock
timeout, and results are aggregated into the unbiased **pass@k** metric from
[Chen et al., 2021](https://arxiv.org/abs/2107.03374).

## Why

When you grade many candidate solutions you need to survive everything a candidate can do wrong:

| Candidate behaviour | What the harness records |
|---|---|
| Returns the wrong value | `failed`, with the actual value |
| Raises an exception / has a syntax error | `error`, with the exception type and message |
| Infinite loop | `timeout` — the other cases still run |
| Calls `sys.exit()` or prints noise | `error` / ignored — the harness keeps working |
| Returns a tuple where a list is expected | compared after JSON normalisation, so it passes |

## Quick start

```bash
pip install -e ".[dev]"
code-eval-harness examples/problems/two_sum.json examples/sample_*.py --timeout 1 -v
```

```
FAIL  sample_buggy.py  (40% of cases)
      failed   args=[[3, 2, 4], 6] expected=[1, 2] got [0, 0]
PASS  sample_correct.py  (100% of cases)
FAIL  sample_hangs.py  (0% of cases)
      timeout  args=[[2, 7, 11, 15], 9] expected=[0, 1]
{
  "samples": 3,
  "correct": 1,
  "pass@1": 0.3333,
  ...
}
```

## Problem format

```json
{
  "entry_point": "two_sum",
  "cases": [
    {"args": [[2, 7, 11, 15], 9], "expected": [0, 1]}
  ]
}
```

## Library use

```python
from code_eval_harness import run_candidate, pass_at_k

run = run_candidate(source_code, "two_sum", cases, timeout=2.0)
run.passed      # True only if every case passed
run.pass_rate   # fraction of cases passed

pass_at_k(n=20, c=3, k=5)   # probability at least one of 5 samples is correct
```

## Design notes

- **Isolation:** the candidate never shares a process with the harness. A tiny driver script runs
  under `python -I` (isolated mode: no user site-packages, no `PYTHONPATH`) in a temporary directory
  and reports back one JSON line.
- **pass@k:** computed as `1 - C(n-c, k) / C(n, k)`, which is unbiased, unlike the naive
  `1 - (1 - c/n)^k`.
- **Not a security sandbox.** Subprocess isolation stops crashes and hangs, not malicious code.
  For untrusted code, run the harness inside a container with no network.

## Tests

```bash
pytest -q   # 21 tests: runner edge cases, pass@k maths, CLI end-to-end
```
