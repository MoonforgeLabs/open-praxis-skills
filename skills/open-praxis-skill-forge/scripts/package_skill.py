#!/usr/bin/env python3
"""
package_skill.py — Package a skill directory for distribution.

Usage:
    python3 scripts/package_skill.py <skill-dir> [--output <dir>]

Creates a .tar.gz archive excluding evals, __pycache__, .pyc, reports, data.json,
node_modules, .git, and other non-distributable files.

Output: <skill-name>.tar.gz in current directory (or --output dir).
"""

import sys
import tarfile
from pathlib import Path

EXCLUDE_PATTERNS = {
    "__pycache__", "*.pyc", ".git", ".gitignore", ".DS_Store",
    "reports", "data.json", "node_modules", "*.db", "*.db-journal",
    "*.log", ".env", ".env.local", "evals", "tests",
}


def should_exclude(path: str) -> bool:
    """Check if a path should be excluded from the package."""
    parts = Path(path).parts
    for part in parts:
        if part in EXCLUDE_PATTERNS:
            return True
        for pattern in EXCLUDE_PATTERNS:
            if pattern.startswith("*") and part.endswith(pattern[1:]):
                return True
    return False


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """Create a distributable archive of the skill."""
    if not (skill_dir / "SKILL.md").exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    skill_name = skill_dir.name
    archive_path = output_dir / f"{skill_name}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        for item in sorted(skill_dir.rglob("*")):
            rel_path = item.relative_to(skill_dir)
            if should_exclude(str(rel_path)):
                continue
            tar.add(item, arcname=f"{skill_name}/{rel_path}")

    return archive_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 package_skill.py <skill-dir> [--output <dir>]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    output_dir = Path(".")

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_dir = Path(sys.argv[idx + 1])
            output_dir.mkdir(parents=True, exist_ok=True)

    try:
        archive = package_skill(skill_dir, output_dir)
        size_kb = archive.stat().st_size / 1024
        print(f"✅ Packaged: {archive} ({size_kb:.1f} KB)")

        # List contents
        with tarfile.open(archive, "r:gz") as tar:
            members = tar.getnames()
            print(f"   Files: {len(members)}")
            for m in members[:10]:
                print(f"   - {m}")
            if len(members) > 10:
                print(f"   ... and {len(members) - 10} more")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
