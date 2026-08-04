"""Independent trial test for task 76 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task076_output_exists():
    assert_clawbench_submission(76)
