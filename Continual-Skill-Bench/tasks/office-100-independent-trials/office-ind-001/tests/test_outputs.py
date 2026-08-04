"""Independent trial test for task 1 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task001_output_exists():
    assert_clawbench_submission(1)
