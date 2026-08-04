"""Independent trial test for task 68 (auto-split from math-100)."""
import json
from pathlib import Path

OUTPUT_DIR = Path('/app')

def test_task068_output_exists():
    """MathCode task 68: execute Python code and verify result."""
    from mathcode_eval import assert_mathcode_submission
    assert_mathcode_submission(68)
