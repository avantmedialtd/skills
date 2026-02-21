#!/usr/bin/env python3
"""
Package a skill directory into a .skill file for Claude Desktop.

Usage:
    python3 scripts/package_skill.py skills/typescript-react-standards [dist/]

A .skill file is a zip archive containing the skill directory contents.
"""

import os
import sys
import zipfile
from pathlib import Path


def package_skill(skill_path: str, output_dir: str = "dist") -> str:
    skill_path = Path(skill_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: {skill_path}/SKILL.md not found", file=sys.stderr)
        sys.exit(1)

    skill_name = skill_path.name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{skill_name}.skill"

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file in files:
                if file.startswith("."):
                    continue
                file_path = Path(root) / file
                arcname = str(file_path.relative_to(skill_path.parent))
                zf.write(file_path, arcname)

    print(f"Packaged: {output_file} ({output_file.stat().st_size} bytes)")
    return str(output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <skill-path> [output-dir]", file=sys.stderr)
        sys.exit(1)

    skill = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "dist"
    package_skill(skill, out)
