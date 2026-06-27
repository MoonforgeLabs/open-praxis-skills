#!/usr/bin/env python3
"""Check consistency between SKILL.md and actual functionality.

Usage:
    python3 check_consistency.py <skill-path>

Example:
    python3 check_consistency.py /path/to/praxis-knowledge-radar
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


def check_skill_md_exists(skill_path: Path) -> tuple[bool, str]:
    """Check if SKILL.md exists."""
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        return True, "SKILL.md exists"
    return False, "SKILL.md not found"


def check_scripts_exist(skill_path: Path) -> tuple[bool, list[str]]:
    """Check which scripts exist in the scripts/ directory."""
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        return False, ["scripts/ directory not found"]

    scripts = []
    for script in scripts_dir.glob("*.py"):
        scripts.append(script.name)
    for script in scripts_dir.glob("*.sh"):
        scripts.append(script.name)

    return True, scripts


def extract_commands_from_skill_md(skill_path: Path) -> list[str]:
    """Extract script commands mentioned in SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return []

    content = skill_md.read_text(encoding="utf-8")

    # Find all script references (support hyphens in filenames)
    patterns = [
        r'scripts/([\w-]+\.py)',
        r'scripts/([\w-]+\.sh)',
        r'python3\s+scripts/([\w-]+\.py)',
        r'bash\s+scripts/([\w-]+\.sh)',
    ]

    commands = set()
    for pattern in patterns:
        matches = re.findall(pattern, content)
        commands.update(matches)

    return sorted(commands)


def extract_trigger_phrases(skill_path: Path) -> list[str]:
    """Extract trigger phrases from SKILL.md description."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return []

    content = skill_md.read_text(encoding="utf-8")

    # Find trigger phrases in description (support multiple formats)
    trigger_patterns = [
        r'触发词[：:]\s*"([^"]+)"',
        r'触发词[：:]\s*([^"\n]+)',
        r'trigger[s]?\s+(?:on|phrases?)[：:]\s*"([^"]+)"',
        r'trigger[s]?\s+(?:on|phrases?)[：:]\s*([^"\n]+)',
        r'Also triggers on[：:]\s*([^"\n]+)',
    ]

    triggers = []
    for pattern in trigger_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            # Split by comma, semicolon, or Chinese comma
            phrases = re.split(r'[,;，、]', match)
            triggers.extend([p.strip() for p in phrases if p.strip()])

    return triggers


def extract_statuses_from_skill_md(skill_path: Path) -> list[str]:
    """Extract status values mentioned in SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return []

    content = skill_md.read_text(encoding="utf-8")

    # Find status values
    status_pattern = r'-\s*`(\w+)`:\s*[^-\n]+'
    matches = re.findall(status_pattern, content)

    return sorted(set(matches))


def extract_areas_from_skill_md(skill_path: Path) -> list[str]:
    """Extract area values mentioned in SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return []

    content = skill_md.read_text(encoding="utf-8")

    # Find area values
    area_pattern = r'-\s*`(\w[\w-]+)`:\s*[^-\n]+'
    matches = re.findall(area_pattern, content)

    # Filter out non-area values
    areas = [m for m in matches if '-' in m and not m.startswith('P')]

    return sorted(set(areas))


def check_consistency(skill_path: Path) -> dict[str, Any]:
    """Run all consistency checks."""
    results = {
        "skill_path": str(skill_path),
        "checks": [],
        "passed": 0,
        "failed": 0,
        "warnings": 0,
    }

    # Check 1: SKILL.md exists
    exists, msg = check_skill_md_exists(skill_path)
    results["checks"].append({
        "name": "SKILL.md exists",
        "status": "PASS" if exists else "FAIL",
        "message": msg,
    })
    if exists:
        results["passed"] += 1
    else:
        results["failed"] += 1
        return results

    # Check 2: Scripts exist
    scripts_exist, scripts = check_scripts_exist(skill_path)
    results["checks"].append({
        "name": "Scripts directory",
        "status": "PASS" if scripts_exist else "FAIL",
        "message": f"Found {len(scripts)} scripts" if scripts_exist else "No scripts found",
        "details": scripts,
    })
    if scripts_exist:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Check 3: Commands in SKILL.md match actual scripts
    commands_in_md = extract_commands_from_skill_md(skill_path)
    actual_scripts = [s for s in scripts if s.endswith(('.py', '.sh'))]

    missing_scripts = []
    for cmd in commands_in_md:
        if cmd not in actual_scripts:
            missing_scripts.append(cmd)

    orphaned_scripts = []
    for script in actual_scripts:
        if script not in commands_in_md:
            orphaned_scripts.append(script)

    if missing_scripts:
        results["checks"].append({
            "name": "Missing scripts",
            "status": "FAIL",
            "message": f"{len(missing_scripts)} scripts referenced in SKILL.md but not found",
            "details": missing_scripts,
        })
        results["failed"] += 1
    else:
        results["checks"].append({
            "name": "Missing scripts",
            "status": "PASS",
            "message": "All referenced scripts exist",
        })
        results["passed"] += 1

    if orphaned_scripts:
        results["checks"].append({
            "name": "Orphaned scripts",
            "status": "WARN",
            "message": f"{len(orphaned_scripts)} scripts exist but not referenced in SKILL.md",
            "details": orphaned_scripts,
        })
        results["warnings"] += 1
    else:
        results["checks"].append({
            "name": "Orphaned scripts",
            "status": "PASS",
            "message": "All scripts are referenced in SKILL.md",
        })
        results["passed"] += 1

    # Check 4: Trigger phrases exist
    triggers = extract_trigger_phrases(skill_path)
    if triggers:
        results["checks"].append({
            "name": "Trigger phrases",
            "status": "PASS",
            "message": f"Found {len(triggers)} trigger phrases",
            "details": triggers,
        })
        results["passed"] += 1
    else:
        results["checks"].append({
            "name": "Trigger phrases",
            "status": "WARN",
            "message": "No trigger phrases found in description",
        })
        results["warnings"] += 1

    # Check 5: Status values
    statuses = extract_statuses_from_skill_md(skill_path)
    if statuses:
        results["checks"].append({
            "name": "Status values",
            "status": "PASS",
            "message": f"Found {len(statuses)} status values",
            "details": statuses,
        })
        results["passed"] += 1
    else:
        results["checks"].append({
            "name": "Status values",
            "status": "WARN",
            "message": "No status values found in SKILL.md",
        })
        results["warnings"] += 1

    # Check 6: Area values
    areas = extract_areas_from_skill_md(skill_path)
    if areas:
        results["checks"].append({
            "name": "Area values",
            "status": "PASS",
            "message": f"Found {len(areas)} area values",
            "details": areas,
        })
        results["passed"] += 1
    else:
        results["checks"].append({
            "name": "Area values",
            "status": "WARN",
            "message": "No area values found in SKILL.md",
        })
        results["warnings"] += 1

    return results


def print_results(results: dict[str, Any]) -> None:
    """Print consistency check results."""
    print("=" * 60)
    print(f"Consistency Check: {results['skill_path']}")
    print("=" * 60)
    print()

    for check in results["checks"]:
        status = check["status"]
        name = check["name"]
        message = check["message"]

        if status == "PASS":
            icon = "✅"
        elif status == "FAIL":
            icon = "❌"
        else:
            icon = "⚠️"

        print(f"{icon} {name}: {message}")

        if "details" in check:
            details = check["details"]
            if isinstance(details, list) and details:
                for detail in details[:5]:
                    print(f"   - {detail}")
                if len(details) > 5:
                    print(f"   ... and {len(details) - 5} more")

    print()
    print("=" * 60)
    print(f"Results: {results['passed']} passed, {results['failed']} failed, {results['warnings']} warnings")
    print("=" * 60)

    if results["failed"] > 0:
        print("\n❌ CONSISTENCY CHECK FAILED")
        sys.exit(1)
    elif results["warnings"] > 0:
        print("\n⚠️ CONSISTENCY CHECK PASSED WITH WARNINGS")
        sys.exit(0)
    else:
        print("\n✅ CONSISTENCY CHECK PASSED")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Check skill consistency")
    parser.add_argument("skill_path", help="Path to skill directory")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not skill_path.exists():
        print(f"❌ Skill path not found: {skill_path}")
        sys.exit(1)

    results = check_consistency(skill_path)
    print_results(results)


if __name__ == "__main__":
    main()