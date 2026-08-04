"""Independent trial test for task 96 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task096_output_exists():
    assert_clawbench_submission(96)
