"""Independent trial test for task 43 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task043_output_exists():
    assert_clawbench_submission(43)
