"""Independent trial test for task 43 (numeric)."""
import json
from pathlib import Path

OUTPUT = Path("/app/task_043_output.json")


def test_task043_output_exists():
    assert OUTPUT.exists(), f"Missing output: {OUTPUT}"
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Output must be a JSON object"
    assert data, "Output must not be empty"
