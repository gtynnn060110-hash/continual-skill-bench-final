"""Independent trial test for task 70 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task070_output_exists():
    assert_clawbench_submission(70)
