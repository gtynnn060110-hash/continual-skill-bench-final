#!/usr/bin/env python3
"""Count difficulty-order inversions in a JSONL tasks file.

An inversion is any pair i<j where rank(i) > rank(j), with ranks: hard>medium>easy.

Usage:
    python count_difficulty_inversions.py [path/to/law_tasks_ordered.jsonl] [--examples N]
"""
import argparse
import json
from collections import defaultdict
from typing import List, Dict


RANK = {"easy": 1, "medium": 2, "hard": 3}


def load_difficulties(path: str) -> List[Dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                print(f"Warning: skipping invalid JSON on line {i}")
                continue
            diff = obj.get("difficulty")
            items.append({"index": i, "difficulty": diff, "obj": obj})
    return items


def count_inversions(items: List[Dict], max_examples: int = 50):
    counts_by_rank = defaultdict(int)
    inversions = 0
    examples = []

    for idx, it in enumerate(items):
        diff = (it.get("difficulty") or "").lower()
        rank = RANK.get(diff)
        if rank is None:
            # treat unknowns as lowest priority (no inversions counted)
            rank = 0
        # any previously seen item with higher rank produces inversions
        for higher_rank in range(rank + 1, max(RANK.values()) + 1):
            cnt = counts_by_rank.get(higher_rank, 0)
            if cnt:
                inversions += cnt
                # record examples (limited)
                if len(examples) < max_examples:
                    # find and store up to one example per higher_rank seen so far
                    examples.append({
                        "current_index": it["index"],
                        "current_difficulty": diff,
                        "higher_rank": higher_rank,
                        "higher_count_seen": cnt,
                    })
        counts_by_rank[rank] += 1

    return inversions, examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="Continual-Skill-Bench/scripts/law/law_tasks_ordered.jsonl",
                        help="path to JSONL file")
    parser.add_argument("--examples", "-e", type=int, default=20,
                        help="max number of example inversion records to show")
    args = parser.parse_args()

    items = load_difficulties(args.path)
    if not items:
        print("No items loaded. Check the file path and content.")
        return

    total = len(items)
    inversions, examples = count_inversions(items, max_examples=args.examples)

    # total possible pairs
    total_pairs = total * (total - 1) // 2

    print(f"File: {args.path}")
    print(f"Total items: {total}")
    print(f"Total pairs: {total_pairs}")
    print(f"Inversion count (hard>medium>easy ordering violations): {inversions}")
    pct = (inversions / total_pairs * 100) if total_pairs else 0.0
    print(f"Inversion percentage of all pairs: {pct:.2f}%")

    if examples:
        print()
        print(f"Showing up to {len(examples)} example inversion records (summary):")
        for ex in examples:
            hr = ex["higher_rank"]
            # map rank back to name
            hr_name = next((k for k, v in RANK.items() if v == hr), str(hr))
            print(f"  Index {ex['current_index']}: {ex['current_difficulty']} (after {hr_name} entries: {ex['higher_count_seen']})")


if __name__ == "__main__":
    main()
