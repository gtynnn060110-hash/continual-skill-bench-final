"""Independent trial test for task 29 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task029_output_exists():
    assert_clawbench_submission(29)
