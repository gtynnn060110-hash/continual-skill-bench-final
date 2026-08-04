"""Independent trial test for task 33 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task033_output_exists():
    assert_clawbench_submission(33)
