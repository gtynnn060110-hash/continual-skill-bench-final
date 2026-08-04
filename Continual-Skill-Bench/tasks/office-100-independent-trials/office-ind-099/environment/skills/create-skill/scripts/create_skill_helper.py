#!/usr/bin/env python3
"""
Helper script for creating new skill files across all agent skill directories.

Usage:
  python3 create_skill_helper.py --name "skill-name" --description "..." --content-file /tmp/draft.md
  python3 create_skill_helper.py --name "skill-name" --description "..." --content "..."
"""
import argparse
import sys
from pathlib import Path

AGENT_SKILL_DIRS = [
    "/root/.claude/skills",
    "/root/.terminus/skills",
    "/root/.codex/skills",
    "/root/.opencode/skill",
    "/root/.goose/skills",
    "/root/.factory/skills",
    "/root/.agents/skills",
    "/root/.gemini/skills",
]


def validate_name(name: str) -> str:
    """Ensure skill name is valid kebab-case."""
    import re
    if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", name):
        print(f"Warning: skill name '{name}' should be kebab-case (e.g., 'bond-ytm-calculator')")
    return name


def build_skill_content(name: str, description: str, body: str) -> str:
    """Build complete SKILL.md content with frontmatter."""
    # Check if body already has frontmatter
    if body.strip().startswith("---"):
        return body

    frontmatter = f"---\nname: {name}\ndescription: {description}\n---\n\n"
    return frontmatter + body


def main():
    parser = argparse.ArgumentParser(description="Create a new skill in all agent directories")
    parser.add_argument("--name", required=True, help="Skill name (kebab-case)")
    parser.add_argument("--description", default="", help="One-line skill description")
    parser.add_argument("--content", default="", help="Skill content (SKILL.md body)")
    parser.add_argument("--content-file", default="", help="Path to file containing skill content")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite if skill already exists")
    args = parser.parse_args()

    name = validate_name(args.name)

    # Get content
    if args.content_file:
        content_path = Path(args.content_file)
        if not content_path.exists():
            print(f"Error: content file not found: {args.content_file}")
            sys.exit(1)
        body = content_path.read_text(encoding="utf-8")
    elif args.content:
        body = args.content
    else:
        print("Error: provide --content or --content-file")
        sys.exit(1)

    skill_content = build_skill_content(name, args.description, body)

    # Write to all agent skill directories
    written = 0
    skipped = 0
    for skills_dir in AGENT_SKILL_DIRS:
        skill_path = Path(skills_dir) / name
        skill_file = skill_path / "SKILL.md"

        if skill_file.exists() and not args.overwrite:
            skipped += 1
            continue

        skill_path.mkdir(parents=True, exist_ok=True)
        skill_file.write_text(skill_content, encoding="utf-8")
        written += 1

    print(f"Skill '{name}' created: {written} directories written, {skipped} skipped (use --overwrite to update)")
    if written > 0:
        print(f"  Available in next task's available_skills list.")


if __name__ == "__main__":
    main()
