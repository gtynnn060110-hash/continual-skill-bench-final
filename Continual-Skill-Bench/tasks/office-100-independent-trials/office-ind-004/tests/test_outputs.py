"""Independent trial test for task 4 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task004_output_exists():
    assert_clawbench_submission(4)
