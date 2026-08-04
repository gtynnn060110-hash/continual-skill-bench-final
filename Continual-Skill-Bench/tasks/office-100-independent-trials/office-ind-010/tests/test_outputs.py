"""Independent trial test for task 10 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task010_output_exists():
    assert_clawbench_submission(10)
