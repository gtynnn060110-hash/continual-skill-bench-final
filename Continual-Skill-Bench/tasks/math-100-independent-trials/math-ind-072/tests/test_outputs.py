"""Independent trial test for task 72 (auto-split from math-100)."""
import json
from pathlib import Path

OUTPUT_DIR = Path('/app')

def test_task072_output_exists():
    """MathCode task 72: execute Python code and verify result."""
    from mathcode_eval import assert_mathcode_submission
    assert_mathcode_submission(72)
