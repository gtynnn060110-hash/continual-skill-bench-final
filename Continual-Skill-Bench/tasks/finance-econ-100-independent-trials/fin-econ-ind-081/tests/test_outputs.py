"""Independent trial test for task 81 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task081_output_exists():
    assert_clawbench_submission(81)
