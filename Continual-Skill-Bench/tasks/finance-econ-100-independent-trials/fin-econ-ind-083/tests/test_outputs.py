"""Independent trial test for task 83 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task083_output_exists():
    assert_clawbench_submission(83)
