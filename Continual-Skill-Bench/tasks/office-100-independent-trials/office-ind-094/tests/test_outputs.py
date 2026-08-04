"""Independent trial test for task 94 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task094_output_exists():
    assert_clawbench_submission(94)
