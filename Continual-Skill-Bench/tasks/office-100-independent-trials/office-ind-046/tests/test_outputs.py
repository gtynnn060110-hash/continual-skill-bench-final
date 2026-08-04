"""Independent trial test for task 46 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission


def test_task046_output_exists():
    assert_clawbench_submission(46)
