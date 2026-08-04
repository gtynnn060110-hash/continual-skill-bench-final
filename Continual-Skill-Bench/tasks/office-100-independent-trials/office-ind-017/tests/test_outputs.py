"""Independent trial test for task 17 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task017_output_exists():
    assert_clawbench_submission(17)
