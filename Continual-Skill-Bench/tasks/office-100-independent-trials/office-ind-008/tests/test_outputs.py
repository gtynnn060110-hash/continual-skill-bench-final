"""Independent trial test for task 8 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task008_output_exists():
    assert_clawbench_submission(8)
