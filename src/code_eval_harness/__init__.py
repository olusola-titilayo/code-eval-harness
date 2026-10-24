"""Run candidate solutions against test cases in isolated subprocesses and score them."""

from .runner import CaseResult, RunResult, run_candidate
from .metrics import pass_at_k, summarize

__all__ = ["CaseResult", "RunResult", "run_candidate", "pass_at_k", "summarize"]
__version__ = "0.1.0"
