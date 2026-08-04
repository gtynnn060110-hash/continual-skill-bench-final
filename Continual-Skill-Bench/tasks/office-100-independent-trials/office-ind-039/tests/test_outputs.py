"""Independent trial test for task 39 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task039_output_exists():
    assert_clawbench_submission(39)
