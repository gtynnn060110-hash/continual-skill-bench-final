"""Independent trial test for task 14 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task014_output_exists():
    assert_clawbench_submission(14)
