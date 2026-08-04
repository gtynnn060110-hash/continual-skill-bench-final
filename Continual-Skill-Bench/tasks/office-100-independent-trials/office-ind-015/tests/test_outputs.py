"""Independent trial test for task 15 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task015_output_exists():
    assert_clawbench_submission(15)
