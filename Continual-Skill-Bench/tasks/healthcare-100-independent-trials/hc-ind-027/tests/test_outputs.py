"""Independent trial test for task 27 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task027_output_exists():
    assert_clawbench_submission(27)
