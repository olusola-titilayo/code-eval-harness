from pathlib import Path

from code_eval_harness.cli import main

EX = Path(__file__).resolve().parent.parent / "examples"


def test_cli_reports_pass_and_fail(capsys):
    code = main([str(EX / "problems/two_sum.json"), str(EX / "sample_correct.py"),
                 str(EX / "sample_buggy.py"), "--timeout", "1", "-v"])
    out = capsys.readouterr().out
    assert code == 1
    assert "PASS  sample_correct.py" in out
    assert "FAIL  sample_buggy.py" in out
    assert '"pass@1": 0.5' in out
