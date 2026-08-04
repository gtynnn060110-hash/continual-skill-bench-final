"""Independent trial test for task 36 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task036_output_exists():
    assert_clawbench_submission(36)
