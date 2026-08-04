#!/usr/bin/env python3
"""
Helper script for modifying existing skill files across all agent skill directories.

Usage:
  python3 modify_skill_helper.py --name "skill-name" --append "text to append"
  python3 modify_skill_helper.py --name "skill-name" --replace-section "## Section" --new-content "..."
  python3 modify_skill_helper.py --name "skill-name" --content-file /tmp/new.md --full-replace
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


def find_skill_file(name: str) -> Path | None:
    """Find the first existing skill file."""
    for d in AGENT_SKILL_DIRS:
        p = Path(d) / name / "SKILL.md"
        if p.exists():
            return p
    return None


def modify_all(name: str, fn) -> int:
    """Apply modification function to all copies of the skill. Returns count modified."""
    count = 0
    for d in AGENT_SKILL_DIRS:
        skill_file = Path(d) / name / "SKILL.md"
        if skill_file.exists():
            original = skill_file.read_text(encoding="utf-8")
            modified = fn(original)
            if modified != original:
                skill_file.write_text(modified, encoding="utf-8")
                count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Modify an existing skill")
    parser.add_argument("--name", required=True, help="Skill name (kebab-case)")
    parser.add_argument("--append", default="", help="Text to append to the skill")
    parser.add_argument("--replace-section", default="", help="Section header to replace (e.g. '## Notes')")
    parser.add_argument("--new-content", default="", help="New content for the replaced section")
    parser.add_argument("--content-file", default="", help="File containing new full content")
    parser.add_argument("--full-replace", action="store_true", help="Replace entire skill content")
    args = parser.parse_args()

    name = args.name

    # Check skill exists
    existing = find_skill_file(name)
    if not existing:
        print(f"Error: skill '{name}' not found in any agent directory")
        print("Use create-skill to create a new skill.")
        sys.exit(1)

    if args.full_replace:
        if args.content_file:
            new_content = Path(args.content_file).read_text(encoding="utf-8")
        elif args.new_content:
            new_content = args.new_content
        else:
            print("Error: --full-replace requires --content-file or --new-content")
            sys.exit(1)
        count = modify_all(name, lambda _: new_content)
        print(f"Full replace of '{name}': {count} files updated")

    elif args.append:
        text = args.append
        count = modify_all(name, lambda c: c + "\n" + text)
        print(f"Appended to '{name}': {count} files updated")

    elif args.replace_section:
        if not args.new_content:
            print("Error: --replace-section requires --new-content")
            sys.exit(1)
        section_header = args.replace_section.strip()
        new_section_content = args.new_content

        def replace_section(content: str) -> str:
            lines = content.splitlines(keepends=True)
            start_idx = None
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if line.strip() == section_header:
                    start_idx = i
                elif start_idx is not None and i > start_idx:
                    # Next section starts with ## or end of file
                    if line.startswith("## ") or line.startswith("# "):
                        end_idx = i
                        break
            if start_idx is None:
                # Section not found — append
                return content + f"\n\n{new_section_content}\n"
            before = "".join(lines[:start_idx])
            after = "".join(lines[end_idx:])
            return before + new_section_content + "\n\n" + after

        count = modify_all(name, replace_section)
        print(f"Replaced section '{section_header}' in '{name}': {count} files updated")

    else:
        print("Error: specify --append, --replace-section, or --full-replace")
        sys.exit(1)

    if count == 0:
        print(f"Warning: No files were updated (skill may not exist in expected directories)")


if __name__ == "__main__":
    main()
