"""Independent trial test for task 95 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task095_output_exists():
    assert_clawbench_submission(95)
