"""Independent trial test for task 17 (auto-split from math-100)."""
import json
from pathlib import Path

OUTPUT_DIR = Path('/app')

def test_task017_output_exists():
    """QA task 17: output file must exist and contain answer."""
    p = OUTPUT_DIR / 'task_017_output.json'
    assert p.exists(), f'Missing output: {p}'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert isinstance(data, dict), 'Output must be a JSON object'
    assert any(data.get(k) not in (None, '') for k in ('answer', 'final_answer', 'short_answer', 'response')), 'Output JSON missing answer field'
