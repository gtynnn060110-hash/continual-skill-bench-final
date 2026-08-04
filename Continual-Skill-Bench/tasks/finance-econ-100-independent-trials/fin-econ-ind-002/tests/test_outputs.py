"""Independent trial test for task 2 (programmatic/claw-bench)."""
from clawbench_eval import assert_clawbench_submission
from investorbench_eval import assert_investorbench_submission

def test_task002_output_exists():
    assert_investorbench_submission(2)
