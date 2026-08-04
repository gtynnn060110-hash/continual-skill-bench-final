#!/usr/bin/env python3
"""
Generate task-aligned skills for law/legal benchmark tasks.

Priority:
    1) Reuse open-source/local skills.
    2) Derive from rubric points.
    3) Rule-based fallback.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import textwrap
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
TASKS_PATH = SCRIPT_DIR / "law_tasks_selected.jsonl"
SKILL_CATALOG_PATH = SCRIPT_DIR / "law_skills_catalog.jsonl"
TASK_SKILL_MAP_PATH = SCRIPT_DIR / "law_task_skill_map.jsonl"
SKILL_CATALOG_MD_PATH = SCRIPT_DIR / "law_skills_catalog.md"

DEFAULT_EXTERNAL_SKILL_FILES = [
    SCRIPT_DIR.parent / "skillhub_skills.jsonl",
    SCRIPT_DIR.parent / "open_source_skills.jsonl",
    SCRIPT_DIR / "law_skills_catalog.jsonl",
]


def load_jsonl_if_exists(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = load_jsonl_if_exists(path)
    if not rows:
        raise FileNotFoundError(f"Missing or empty input file: {path}")
    return rows


def normalize_slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "law-skill"


def compact_text(text: str, max_len: int = 220) -> str:
    return textwrap.shorten(str(text).replace("\n", " "), width=max_len, placeholder="...")


def extract_keywords(text: str, max_n: int = 20) -> set[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\-\_]{2,}", text.lower())
    stop = {
        "the", "and", "for", "with", "from", "that", "this", "task", "using",
        "into", "your", "when", "where", "what", "which", "will", "should",
        "can", "are", "not", "all", "one", "two", "three", "than", "then",
        "json", "answer", "question", "data", "file", "result",
    }
    filtered = [t for t in tokens if t not in stop]
    return set(filtered[:max_n])


def canonicalize_skill(raw: dict[str, Any], source: str) -> dict[str, Any]:
    name = raw.get("skill_name") or raw.get("name") or raw.get("slug") or raw.get("id") or "law-skill"
    summary = raw.get("skill_summary") or raw.get("summary") or raw.get("description") or ""
    when_to_use = raw.get("when_to_use") or raw.get("use_case") or raw.get("trigger") or ""
    steps = raw.get("steps") or raw.get("procedure") or []
    inputs = raw.get("inputs") or []
    validation = raw.get("validation") or raw.get("checks") or []
    tags = raw.get("tags") or raw.get("keywords") or []

    skill = {
        "skill_name": normalize_slug(str(name)),
        "skill_summary": str(summary).strip(),
        "when_to_use": str(when_to_use).strip(),
        "inputs": [str(x).strip() for x in inputs if str(x).strip()],
        "steps": [str(x).strip() for x in steps if str(x).strip()],
        "validation": [str(x).strip() for x in validation if str(x).strip()],
        "tags": [str(x).strip().lower() for x in tags if str(x).strip()],
        "source": source,
    }
    if not skill["skill_summary"]:
        skill["skill_summary"] = "Reusable legal workflow skill."
    if not skill["when_to_use"]:
        skill["when_to_use"] = "Use this skill for legal tasks matching its domain and required tools."
    if not skill["inputs"]:
        skill["inputs"] = ["task question", "available data files", "required output format"]
    if not skill["steps"]:
        skill["steps"] = [
            "Identify legal issue and governing rule.",
            "Extract relevant facts/evidence from sources.",
            "Apply rule to facts with explicit reasoning.",
            "Return structured output in required format.",
        ]
    if not skill["validation"]:
        skill["validation"] = ["Citations and facts are consistent.", "Reasoning follows rule-to-fact logic.", "Output format is valid."]
    return skill


def task_profile(task: dict[str, Any]) -> dict[str, Any]:
    domain = str(task.get("domain") or task.get("llm_domain") or "")
    difficulty = str(task.get("difficulty") or task.get("llm_difficulty_score") or "")
    tools = task.get("tools", []) or []
    question = str(task.get("question", ""))
    answer = str(task.get("answer", ""))
    rubric_answer = str(task.get("rubric_answer", ""))
    rubrics = task.get("rubrics", []) or []
    text = " ".join(
        [
            domain,
            difficulty,
            " ".join(tools),
            question,
            answer,
            rubric_answer,
        ]
    )
    return {
        "text": text.lower(),
        "keywords": extract_keywords(text, max_n=30),
        "rubrics": rubrics,
    }


def skill_profile(skill: dict[str, Any]) -> dict[str, Any]:
    text = " ".join(
        [
            str(skill.get("skill_name", "")),
            str(skill.get("skill_summary", "")),
            str(skill.get("when_to_use", "")),
            " ".join(skill.get("inputs", []) or []),
            " ".join(skill.get("steps", []) or []),
            " ".join(skill.get("tags", []) or []),
        ]
    )
    return {
        "text": text.lower(),
        "keywords": extract_keywords(text, max_n=40),
    }


def heuristic_match_score(task: dict[str, Any], skill: dict[str, Any]) -> float:
    t = task_profile(task)
    s = skill_profile(skill)
    overlap = len(t["keywords"] & s["keywords"])

    score = float(overlap) * 0.25
    if str(task.get("domain", "")) and str(task.get("domain", "")) in s["text"]:
        score += 1.2
    for tool in task.get("tools", []) or []:
        if str(tool).lower() in s["text"]:
            score += 0.6
    if str(task.get("difficulty", "")) in s["text"]:
        score += 0.2
    return score


def llm_reuse_judge(task: dict[str, Any], candidate_skill: dict[str, Any], model: str) -> tuple[bool, str]:
    from openai import OpenAI  # type: ignore[reportMissingImports]

    client = OpenAI()
    prompt = f"""
You are checking if an existing skill is sufficient for a task.
Return strict JSON: {{"reuse": true/false, "reason": "<short>"}}

Task:
- domain: {task.get("domain")}
- difficulty: {task.get("difficulty")}
- tools: {task.get("tools")}
- question: {compact_text(task.get("question",""), 300)}
- rubric_answer: {compact_text(task.get("rubric_answer",""), 220)}

Candidate skill:
- name: {candidate_skill.get("skill_name")}
- summary: {candidate_skill.get("skill_summary")}
- when_to_use: {candidate_skill.get("when_to_use")}
- steps: {candidate_skill.get("steps")}
""".strip()

    resp = client.responses.create(
        model=model,
        input=prompt,
        temperature=0.0,
        max_output_tokens=220,
    )
    data = json.loads((resp.output_text or "").strip())
    return bool(data.get("reuse")), str(data.get("reason", "")).strip()


def pick_existing_skill(
    task: dict[str, Any],
    pool: list[dict[str, Any]],
    use_llm_judge: bool,
    llm_model: str,
) -> tuple[dict[str, Any] | None, str]:
    if not pool:
        return None, "no-pool"

    scored = sorted(
        ((heuristic_match_score(task, s), s) for s in pool),
        key=lambda x: x[0],
        reverse=True,
    )
    best_score, best_skill = scored[0]
    if best_score < 1.6:
        return None, f"low-heuristic-score:{best_score:.2f}"

    if use_llm_judge:
        try:
            ok, reason = llm_reuse_judge(task, best_skill, model=llm_model)
            if ok:
                return best_skill, f"llm-reuse:{reason}"
            return None, f"llm-reject:{reason}"
        except Exception as e:
            return best_skill, f"heuristic-fallback:{e}"
    return best_skill, f"heuristic-reuse:{best_score:.2f}"


def skill_from_rubrics(task: dict[str, Any]) -> dict[str, Any] | None:
    rubrics = task.get("rubrics", []) or []
    if not rubrics:
        return None

    rubric_points: list[str] = []
    for r in rubrics:
        if isinstance(r, dict):
            txt = str(r.get("rubric_detail", "") or r.get("rubric", "")).strip()
        else:
            txt = str(r).strip()
        if txt:
            rubric_points.append(txt)
    if not rubric_points:
        return None

    domain = str(task.get("domain") or task.get("llm_domain") or "general-law")
    difficulty = str(task.get("difficulty") or task.get("llm_difficulty_score") or "medium")
    name = normalize_slug(f"{domain}-rubric-driven-{difficulty}")
    steps = ["Extract evidence needed by each rubric item."]
    steps.extend([f"Address rubric point: {compact_text(p, 120)}" for p in rubric_points[:5]])
    steps.append("Synthesize final answer aligned with rubric scoring criteria.")

    return {
        "skill_name": name,
        "skill_summary": "Solve tasks by following explicit rubric-aligned evaluation points.",
        "when_to_use": "Use when task has explicit grading rubrics or checklist-like answer requirements.",
        "inputs": ["task question", "rubric points", "supporting files/data"],
        "steps": steps,
        "validation": [
            "Each rubric point is explicitly addressed.",
            "Claims are backed by extracted evidence.",
            "Final answer format is deterministic and complete.",
        ],
        "tags": [domain, "rubric-driven", difficulty],
        "source": "rubric-derived",
    }


def fallback_skill(task: dict[str, Any]) -> dict[str, Any]:
    domain = str(task.get("domain") or task.get("llm_domain") or "general-law")
    tools = task.get("tools", []) or []
    difficulty = str(task.get("difficulty") or task.get("llm_difficulty_score") or "medium")
    base_name = normalize_slug(f"{domain}-task-solver-{difficulty}")
    return {
        "skill_name": base_name,
        "skill_summary": "General reusable workflow for legal task solving.",
        "when_to_use": f"Use for {domain} legal tasks when no specialized reusable skill is available.",
        "inputs": ["task question", "source documents", "required output schema"],
        "steps": [
            "Identify requested legal issue and scope.",
            "Extract relevant facts/clauses from evidence.",
            "Apply legal reasoning with explicit assumptions.",
            "Return deterministic answer with concise rationale.",
        ],
        "validation": [
            "Rule and fact mapping is explicit.",
            "Conclusion is supported by extracted evidence.",
            "Output schema constraints are satisfied.",
        ],
        "tags": [domain, difficulty] + [str(t).lower() for t in tools],
        "source": "fallback-rule-based",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate law skills with open-source-first reuse strategy.")
    parser.add_argument("--tasks", default=str(TASKS_PATH), help="Path to law tasks jsonl.")
    parser.add_argument(
        "--skill-files",
        nargs="*",
        default=[str(p) for p in DEFAULT_EXTERNAL_SKILL_FILES],
        help="Candidate open-source/local skill jsonl files (searched in order).",
    )
    parser.add_argument(
        "--llm-judge",
        action="store_true",
        help="Use LLM only to decide whether to reuse an existing skill.",
    )
    parser.add_argument(
        "--llm-model",
        default="gpt-4o-mini",
        help="Model for optional LLM reuse judge.",
    )
    args = parser.parse_args()

    tasks = load_jsonl(Path(args.tasks))
    if not tasks:
        print(f"No tasks in {args.tasks}")
        return

    use_llm_judge = bool(args.llm_judge and os.environ.get("OPENAI_API_KEY"))
    if args.llm_judge and not use_llm_judge:
        print("--llm-judge requested but OPENAI_API_KEY not set; falling back to heuristic-only reuse.")

    external_pool: list[dict[str, Any]] = []
    for skill_file in args.skill_files:
        path = Path(skill_file)
        rows = load_jsonl_if_exists(path)
        if rows:
            source_name = f"external:{path.name}"
            external_pool.extend(canonicalize_skill(r, source=source_name) for r in rows)
            print(f"Loaded {len(rows)} skills from {path}")

    unique_pool: dict[str, dict[str, Any]] = {}
    for s in external_pool:
        unique_pool.setdefault(s["skill_name"], s)
    reusable_pool = list(unique_pool.values())
    print(f"Reusable skill pool size: {len(reusable_pool)}")

    task_skill_map: list[dict[str, Any]] = []
    skill_catalog_by_name: dict[str, dict[str, Any]] = {s["skill_name"]: s for s in reusable_pool}
    stats = {"reused": 0, "rubric_derived": 0, "fallback": 0}

    for task in tasks:
        picked, reason = pick_existing_skill(
            task, reusable_pool, use_llm_judge=use_llm_judge, llm_model=args.llm_model
        )
        if picked:
            skill = picked
            stats["reused"] += 1
        else:
            skill = skill_from_rubrics(task)
            if skill is not None:
                stats["rubric_derived"] += 1
            else:
                skill = fallback_skill(task)
                stats["fallback"] += 1

        skill_name = skill["skill_name"]
        skill_catalog_by_name.setdefault(skill_name, skill)

        task_skill_map.append(
            {
                "task_id": task.get("task_id"),
                "source": task.get("source"),
                "source_id": task.get("source_id"),
                "domain": task.get("domain") or task.get("llm_domain"),
                "difficulty": task.get("difficulty") or task.get("llm_difficulty_score"),
                "question": task.get("question"),
                "skill_name": skill_name,
                "match_reason": reason if picked else skill.get("source", ""),
            }
        )

    skill_catalog = sorted(skill_catalog_by_name.values(), key=lambda x: x["skill_name"])

    with SKILL_CATALOG_PATH.open("w", encoding="utf-8") as f:
        for row in skill_catalog:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with TASK_SKILL_MAP_PATH.open("w", encoding="utf-8") as f:
        for row in task_skill_map:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    md_lines = [
        "# Law Skills Catalog",
        "",
        f"Total tasks: {len(tasks)}",
        f"Unique skills: {len(skill_catalog)}",
        f"Reused existing skills: {stats['reused']}",
        f"Rubric-derived skills: {stats['rubric_derived']}",
        f"Fallback-created skills: {stats['fallback']}",
        "",
        "| Skill | Source | Summary |",
        "|---|---|---|",
    ]
    for skill in skill_catalog:
        summary = str(skill.get("skill_summary", "")).replace("|", "\\|")
        md_lines.append(f"| `{skill['skill_name']}` | {skill.get('source','')} | {summary} |")

    md_lines += [
        "",
        "## Task-to-Skill Mapping",
        "",
        "| Task ID | Domain | Difficulty | Skill | Match Reason |",
        "|---|---|---|---|---|",
    ]
    for row in task_skill_map:
        reason = str(row.get("match_reason", "")).replace("|", "\\|")
        md_lines.append(
            f"| {row.get('task_id')} | {row.get('domain')} | {row.get('difficulty')} | "
            f"`{row.get('skill_name')}` | {reason} |"
        )

    SKILL_CATALOG_MD_PATH.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Saved: {SKILL_CATALOG_PATH}")
    print(f"Saved: {TASK_SKILL_MAP_PATH}")
    print(f"Saved: {SKILL_CATALOG_MD_PATH}")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()

