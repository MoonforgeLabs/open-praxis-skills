#!/usr/bin/env python3
"""Check if a skill is ready for open-source publishing.

Usage:
    python3 check_open_source_readiness.py <skill-path>

Example:
    python3 check_open_source_readiness.py /path/to/praxis-knowledge-radar
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


# Blocked terms that should not appear in published skills
BLOCKED_TERMS = [
    "praxis-skill-forge",
    "intake-rubric",
    "capability-tier",
    "praxis-knowledge-radar",
    "praxis-learning-radar",
    "praxis-skill-publish",
    "auto_classify",
    "source-notes",
    "dependency-lifecycle",
    "skill-architecture",
    "curator",
    "creative brief",
    "skill creation",
    "skill development",
]

# Internal scripts that should not be published
INTERNAL_SCRIPTS = [
    "auto_classify_tiers.py",
    "quick_validate.py",
    "vendor_sync.py",
    "install_skill.sh",
    "link-skills.sh",
    "doctor.sh",
    "bump-version.sh",
    "improve_description.py",
    "eval_runner.py",
    "check_consistency.py",
]

# Internal references that should not be published
INTERNAL_REFERENCES = [
    "intake-rubric.md",
    "source-notes.md",
    "dependency-lifecycle.md",
    "capability-tiers.md",
    "skill-architecture.md",
    "skill-file-checklist.md",
]


def check_blocked_terms(skill_path: Path) -> tuple[bool, list[str]]:
    """Check for blocked terms in SKILL.md and references/."""
    found_terms = []

    # Check SKILL.md
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        for term in BLOCKED_TERMS:
            if term.lower() in content.lower():
                found_terms.append(f"SKILL.md: {term}")

    # Check references/
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        for ref_file in refs_dir.glob("*.md"):
            content = ref_file.read_text(encoding="utf-8")
            for term in BLOCKED_TERMS:
                if term.lower() in content.lower():
                    found_terms.append(f"references/{ref_file.name}: {term}")

    # Check scripts/
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for script_file in scripts_dir.glob("*"):
            if script_file.is_file():
                try:
                    content = script_file.read_text(encoding="utf-8")
                    for term in BLOCKED_TERMS:
                        if term.lower() in content.lower():
                            found_terms.append(f"scripts/{script_file.name}: {term}")
                except:
                    pass

    return len(found_terms) == 0, found_terms


def check_internal_scripts(skill_path: Path) -> tuple[bool, list[str]]:
    """Check for internal scripts that should not be published."""
    found_scripts = []

    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.glob("*"):
            if script.name in INTERNAL_SCRIPTS:
                found_scripts.append(script.name)

    return len(found_scripts) == 0, found_scripts


def check_internal_references(skill_path: Path) -> tuple[bool, list[str]]:
    """Check for internal references that should not be published."""
    found_refs = []

    refs_dir = skill_path / "references"
    if refs_dir.exists():
        for ref in refs_dir.glob("*.md"):
            if ref.name in INTERNAL_REFERENCES:
                found_refs.append(ref.name)

    return len(found_refs) == 0, found_refs


def check_license(skill_path: Path) -> tuple[bool, str]:
    """Check if LICENSE file exists."""
    license_file = skill_path / "LICENSE"
    if license_file.exists():
        return True, "LICENSE file exists"
    return False, "LICENSE file not found"


def check_readme(skill_path: Path) -> tuple[bool, str]:
    """Check if README.md exists."""
    readme_file = skill_path / "README.md"
    if readme_file.exists():
        return True, "README.md exists"
    return False, "README.md not found"


def check_install_docs(skill_path: Path) -> tuple[bool, str]:
    """Check if installation documentation exists."""
    # Check README.md for installation section
    readme_file = skill_path / "README.md"
    if readme_file.exists():
        content = readme_file.read_text(encoding="utf-8")
        if "install" in content.lower() or "setup" in content.lower() or "quick start" in content.lower():
            return True, "Installation docs found in README.md"

    # Check for INSTALL.md
    install_file = skill_path / "INSTALL.md"
    if install_file.exists():
        return True, "INSTALL.md exists"

    # Check SKILL.md for installation section
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        if "install" in content.lower() or "setup" in content.lower() or "quick start" in content.lower():
            return True, "Installation docs found in SKILL.md"

    return False, "No installation documentation found"


def check_dependencies_documented(skill_path: Path) -> tuple[bool, list[str]]:
    """Check if dependencies are documented."""
    missing_deps = []

    # Check for deps-manifest.json
    deps_manifest = skill_path / "deps-manifest.json"
    if not deps_manifest.exists():
        missing_deps.append("deps-manifest.json")

    # Check SKILL.md for dependency documentation
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        if "depend" not in content.lower() and "require" not in content.lower() and "prerequisite" not in content.lower():
            missing_deps.append("Dependency documentation in SKILL.md")

    return len(missing_deps) == 0, missing_deps


def check_cross_platform(skill_path: Path) -> tuple[bool, list[str]]:
    """Check for cross-platform compatibility issues."""
    issues = []

    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            try:
                content = script.read_text(encoding="utf-8")

                # Check for Windows-style paths
                if "os.path" in content and "pathlib" not in content:
                    issues.append(f"{script.name}: Uses os.path instead of pathlib")

                # Check for platform-specific code
                if "sys.platform" in content:
                    if "if sys.platform" not in content and "elif sys.platform" not in content:
                        issues.append(f"{script.name}: Platform-specific code without fallback")

            except:
                pass

    return len(issues) == 0, issues


def check_no_private_data(skill_path: Path) -> tuple[bool, list[str]]:
    """Check for private data that should not be published."""
    private_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'home/[^/\s]+/\.praxis-skills',
        r'/Users/[^/\s]+/',
    ]

    found_private = []

    # Check all files
    for file_path in skill_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in ['.py', '.sh', '.md', '.json', '.yaml', '.yml']:
            try:
                content = file_path.read_text(encoding="utf-8")
                for pattern in private_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        rel_path = file_path.relative_to(skill_path)
                        found_private.append(f"{rel_path}: {matches[0][:50]}...")
            except:
                pass

    return len(found_private) == 0, found_private


def classify_readiness(skill_path: Path) -> str:
    """Classify skill readiness tier."""
    # Check dependencies
    deps_manifest = skill_path / "deps-manifest.json"
    has_deps = deps_manifest.exists()

    # Check for external dependencies
    scripts_dir = skill_path / "scripts"
    has_external_deps = False

    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            try:
                content = script.read_text(encoding="utf-8")
                if "import subprocess" in content or "os.system" in content:
                    has_external_deps = True
                    break
            except:
                pass

    # Classify
    if not has_deps and not has_external_deps:
        return "A — Ship now"
    elif has_deps and not has_external_deps:
        return "B — Add prerequisites"
    else:
        return "C — Surgery needed"


def check_open_source_readiness(skill_path: Path) -> dict[str, Any]:
    """Run all open-source readiness checks."""
    results = {
        "skill_path": str(skill_path),
        "checks": [],
        "passed": 0,
        "failed": 0,
        "warnings": 0,
        "readiness_tier": "",
    }

    # Check 1: Blocked terms
    clean, found_terms = check_blocked_terms(skill_path)
    results["checks"].append({
        "name": "Blocked terms",
        "status": "PASS" if clean else "FAIL",
        "message": "No blocked terms found" if clean else f"Found {len(found_terms)} blocked terms",
        "details": found_terms[:10] if found_terms else [],
    })
    if clean:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Check 2: Internal scripts
    clean, found_scripts = check_internal_scripts(skill_path)
    results["checks"].append({
        "name": "Internal scripts",
        "status": "PASS" if clean else "FAIL",
        "message": "No internal scripts found" if clean else f"Found {len(found_scripts)} internal scripts",
        "details": found_scripts,
    })
    if clean:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Check 3: Internal references
    clean, found_refs = check_internal_references(skill_path)
    results["checks"].append({
        "name": "Internal references",
        "status": "PASS" if clean else "FAIL",
        "message": "No internal references found" if clean else f"Found {len(found_refs)} internal references",
        "details": found_refs,
    })
    if clean:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Check 4: LICENSE
    has_license, msg = check_license(skill_path)
    results["checks"].append({
        "name": "LICENSE file",
        "status": "PASS" if has_license else "WARN",
        "message": msg,
    })
    if has_license:
        results["passed"] += 1
    else:
        results["warnings"] += 1

    # Check 5: README
    has_readme, msg = check_readme(skill_path)
    results["checks"].append({
        "name": "README.md",
        "status": "PASS" if has_readme else "WARN",
        "message": msg,
    })
    if has_readme:
        results["passed"] += 1
    else:
        results["warnings"] += 1

    # Check 6: Installation docs
    has_install, msg = check_install_docs(skill_path)
    results["checks"].append({
        "name": "Installation docs",
        "status": "PASS" if has_install else "WARN",
        "message": msg,
    })
    if has_install:
        results["passed"] += 1
    else:
        results["warnings"] += 1

    # Check 7: Dependencies documented
    has_deps, missing_deps = check_dependencies_documented(skill_path)
    results["checks"].append({
        "name": "Dependencies documented",
        "status": "PASS" if has_deps else "WARN",
        "message": "Dependencies documented" if has_deps else f"Missing: {', '.join(missing_deps)}",
    })
    if has_deps:
        results["passed"] += 1
    else:
        results["warnings"] += 1

    # Check 8: Cross-platform
    is_cross_platform, issues = check_cross_platform(skill_path)
    results["checks"].append({
        "name": "Cross-platform",
        "status": "PASS" if is_cross_platform else "WARN",
        "message": "Cross-platform compatible" if is_cross_platform else f"{len(issues)} issues found",
        "details": issues,
    })
    if is_cross_platform:
        results["passed"] += 1
    else:
        results["warnings"] += 1

    # Check 9: No private data
    no_private, found_private = check_no_private_data(skill_path)
    results["checks"].append({
        "name": "No private data",
        "status": "PASS" if no_private else "FAIL",
        "message": "No private data found" if no_private else f"Found {len(found_private)} private data",
        "details": found_private[:5] if found_private else [],
    })
    if no_private:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Classify readiness tier
    results["readiness_tier"] = classify_readiness(skill_path)

    return results


def print_results(results: dict[str, Any]) -> None:
    """Print open-source readiness check results."""
    print("=" * 60)
    print(f"Open-Source Readiness Check: {results['skill_path']}")
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
    print(f"Readiness Tier: {results['readiness_tier']}")
    print("=" * 60)

    if results["failed"] > 0:
        print("\n❌ OPEN-SOURCE READINESS CHECK FAILED")
        print("   Please fix the issues above before publishing.")
        sys.exit(1)
    elif results["warnings"] > 0:
        print("\n⚠️ OPEN-SOURCE READINESS CHECK PASSED WITH WARNINGS")
        print("   Consider addressing the warnings before publishing.")
        sys.exit(0)
    else:
        print("\n✅ OPEN-SOURCE READINESS CHECK PASSED")
        print("   Ready for publishing!")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Check open-source readiness")
    parser.add_argument("skill_path", help="Path to skill directory")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not skill_path.exists():
        print(f"❌ Skill path not found: {skill_path}")
        sys.exit(1)

    results = check_open_source_readiness(skill_path)
    print_results(results)


if __name__ == "__main__":
    main()