"""Independent trial test for task 85 (auto-split from math-100)."""
import json
from pathlib import Path

OUTPUT_DIR = Path('/app')

def test_task085_output_exists():
    """Rubric task 85: output file for LLM judge."""
    p = OUTPUT_DIR / 'task_085_output.json'
    assert p.exists(), f'Missing output: {p}'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert isinstance(data, dict), 'Output must be a JSON object'
    assert any(data.get(k) not in (None, '') for k in ('answer', 'final_answer', 'short_answer', 'response')), 'Output JSON missing answer field'
