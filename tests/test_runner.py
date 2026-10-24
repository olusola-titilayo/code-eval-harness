from code_eval_harness import run_candidate

CASES = [{"args": [2, 3], "expected": 5}, {"args": [-1, 1], "expected": 0}]


def test_correct_solution_passes_all_cases():
    run = run_candidate("def add(a, b):\n    return a + b\n", "add", CASES)
    assert run.passed
    assert [c.status for c in run.cases] == ["passed", "passed"]


def test_wrong_answer_is_failed_not_error():
    run = run_candidate("def add(a, b):\n    return a - b\n", "add", CASES)
    assert not run.passed
    assert run.cases[0].status == "failed" and run.cases[0].actual == -1


def test_exception_is_reported_with_type():
    run = run_candidate("def add(a, b):\n    raise ValueError('boom')\n", "add", CASES)
    assert run.cases[0].status == "error"
    assert run.cases[0].error.startswith("ValueError: boom")


def test_missing_entry_point():
    run = run_candidate("def plus(a, b):\n    return a + b\n", "add", CASES[:1])
    assert run.cases[0].status == "error" and "NameError" in run.cases[0].error


def test_infinite_loop_times_out_without_blocking_other_cases():
    src = "def add(a, b):\n    while a < 0:\n        pass\n    return a + b\n"
    run = run_candidate(src, "add", [{"args": [-1, 1], "expected": 0}, {"args": [2, 3], "expected": 5}], timeout=0.5)
    assert [c.status for c in run.cases] == ["timeout", "passed"]


def test_sys_exit_and_prints_do_not_break_the_harness():
    src = "import sys\ndef add(a, b):\n    print('noise')\n    if a == 2:\n        sys.exit(3)\n    return a + b\n"
    run = run_candidate(src, "add", CASES)
    assert [c.status for c in run.cases] == ["error", "passed"]
    assert "SystemExit" in run.cases[0].error


def test_tuple_result_matches_list_expectation():
    run = run_candidate("def pair(x):\n    return (x, x)\n", "pair", [{"args": [1], "expected": [1, 1]}])
    assert run.passed


def test_syntax_error_in_candidate():
    run = run_candidate("def add(a, b) return a + b\n", "add", CASES[:1])
    assert run.cases[0].status == "error" and "SyntaxError" in run.cases[0].error


def test_empty_case_list_is_not_a_pass():
    assert not run_candidate("def add(a, b):\n    return a + b\n", "add", []).passed
