#!/usr/bin/env python3
"""
示例：Step 3 任务 skill 迁移判定脚本

当前实现：基于固定随机种子采样 pairs，并输出 YES/NO/PARTIAL。

Run (sampled, default 200 pairs):
    python example_ordering_script.py
"""

from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path

# ── LLM-based skill transfer checking ───────────────────────────────────────

def _build_transfer_prompt(task_a: dict, task_b: dict) -> str:
    return f"""You are evaluating whether two tasks share transferable skills that an AI agent could learn.

Task A: {task_a['question']}

Task B: {task_b['question']}

Analyze the skill transfer relationship between these two tasks. Consider:
1. **Prerequisite sub-skills**: Does Task A require sub-skills (e.g. reading tables, ratio calculation, parsing text) that also appear in Task B? Or vice versa?
2. **Shared skill practice**: Do both tasks exercise the same underlying skill, meaning doing either one gives useful practice for the other?
3. **Transfer direction**: Is the transfer primarily A→B (doing A first helps B), B→A (doing B first helps A), or bidirectional?

Guidance (be generous with YES):
- If there is any clear overlap in required sub-skills or reasoning steps, label YES.
- Use PARTIAL only when the overlap is weak or incidental.
- If A is broader/more complex than B, treat A→B as YES (practice on the broader task still helps), and B→A as YES when the simpler task is a prerequisite; otherwise PARTIAL.

Respond in this exact JSON format:
{{
  "a_helps_b": "YES" | "PARTIAL" | "NO",
  "b_helps_a": "YES" | "PARTIAL" | "NO",
  "shared_skills": ["skill1", "skill2"],
  "reason": "one sentence explaining the main skill relationship"
}}

Only output the JSON, nothing else."""


def llm_skill_transfer_check(task_a: dict, task_b: dict, client, model: str) -> dict:
    """问 LLM：task_a 和 task_b 之间的双向 skill 迁移关系。
    返回 {"a_helps_b": "YES"|"PARTIAL"|"NO", "b_helps_a": ..., "shared_skills": [...], "reason": "..."}
    """
    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=600,
        messages=[{"role": "user", "content": _build_transfer_prompt(task_a, task_b)}],
    )
    text = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0].strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # Truncated JSON: find last complete field by scanning for the closing brace
        last_brace = text.rfind("}")
        if last_brace > 0:
            try:
                result = json.loads(text[: last_brace + 1])
            except json.JSONDecodeError:
                result = {}
        else:
            result = {}

    if not result:
        # Last-resort fallback: scan raw text for verdict keywords
        upper = text.upper()
        verdict = "YES" if "YES" in upper else ("PARTIAL" if "PARTIAL" in upper else "NO")
        return {"a_helps_b": verdict, "b_helps_a": "NO", "shared_skills": [], "reason": text[:200]}

    for key in ("a_helps_b", "b_helps_a"):
        val = str(result.get(key, "NO")).upper()
        result[key] = val if val in ("YES", "PARTIAL", "NO") else "NO"
    if not isinstance(result.get("shared_skills"), list):
        result["shared_skills"] = []
    if not isinstance(result.get("reason"), str):
        result["reason"] = ""
    return result


# ── 主函数 ───────────────────────────────────────────────────────────────────

INPUT_FILES = [
    "/Users/gtynnn/Documents/Learning/llm_porj/Continual-Skill-Bench/scripts/finance/finance_tasks_ordered.jsonl",
    "/Users/gtynnn/Documents/Learning/llm_porj/Continual-Skill-Bench/scripts/law/law_tasks_ordered.jsonl",
    "/Users/gtynnn/Documents/Learning/llm_porj/Continual-Skill-Bench/scripts/office/office_tasks_selected.jsonl",
    "/Users/gtynnn/Documents/Learning/llm_porj/Continual-Skill-Bench/scripts/healthcare/healthcare_tasks_selected.jsonl",
    "/Users/gtynnn/Documents/Learning/llm_porj/math_tasks_ordered.jsonl"
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-pairs", type=int, default=200,
                        help="sampled 模式下采样的 pair 数量（默认 200）")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()

    from openai import OpenAI

    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-5.4")

    for input_path in INPUT_FILES:
        tasks = [
            json.loads(l)
            for l in Path(input_path).read_text().splitlines()
            if l.strip()
        ]
        print(f"INPUT\t{input_path}")
        print(f"LOADED\t{len(tasks)}")

        rng = random.Random(args.seed)
        n = len(tasks)
        all_unordered = [(i, j) for i in range(n) for j in range(n) if i < j]
        sampled = rng.sample(all_unordered, min(args.n_pairs, len(all_unordered)))

        counts = {"YES": 0, "NO": 0, "PARTIAL": 0}
        for a_idx, b_idx in sampled:
            result = llm_skill_transfer_check(tasks[a_idx], tasks[b_idx], client, model)
            counts[result["a_helps_b"]] += 1
            counts[result["b_helps_a"]] += 1

        print(f"YES\t{counts['YES']}")
        print(f"NO\t{counts['NO']}")
        print(f"PARTIAL\t{counts['PARTIAL']}")


if __name__ == "__main__":
    main()
