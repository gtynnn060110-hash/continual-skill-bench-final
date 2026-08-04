"""Independent trial test for task 75 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task075_output_exists():
    assert_clawbench_submission(75)
