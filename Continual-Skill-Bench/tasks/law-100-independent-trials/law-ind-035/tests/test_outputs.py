"""Independent trial test for task 35 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task035_output_exists():
    assert_clawbench_submission(35)
