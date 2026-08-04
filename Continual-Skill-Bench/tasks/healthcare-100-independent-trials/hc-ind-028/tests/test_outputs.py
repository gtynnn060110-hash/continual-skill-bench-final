"""Independent trial test for task 28 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task028_output_exists():
    assert_clawbench_submission(28)
