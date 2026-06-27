#!/usr/bin/env python3
"""
quick_validate.py — Validate SKILL.md structure, frontmatter, and naming rules.

Usage:
    python3 scripts/quick_validate.py <skill-dir>
    python3 scripts/quick_validate.py skills/praxis-translate
    python3 scripts/quick_validate.py skills/              # validate all

Exit codes: 0 = pass, 1 = fail
"""

import re
import sys
from pathlib import Path

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility", "version"}
NAME_REGEX = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
MAX_NAME_LEN = 64
MAX_DESC_LEN = 1536
MAX_BODY_LINES = 500
MAX_BODY_BYTES = 5000 * 4  # ~5000 tokens ≈ 20KB


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Extract YAML frontmatter and body from SKILL.md (no PyYAML dependency)."""
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text

    fm = {}
    current_key = None
    for line in parts[1].splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        # Match key: value (handle multiline with >)
        m = re.match(r'^(\w[\w-]*):\s*(.*)', line)
        if m:
            current_key = m.group(1)
            value = m.group(2).strip()
            if value == '>' or value == '|':
                fm[current_key] = ''  # multiline, will accumulate
            elif value.startswith('"') and value.endswith('"'):
                fm[current_key] = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                fm[current_key] = value[1:-1]
            else:
                fm[current_key] = value
        elif current_key and line.startswith('  '):
            # Continuation of multiline value
            prev = fm.get(current_key, '')
            fm[current_key] = (prev + ' ' + line.strip()).strip() if prev else line.strip()

    return fm if fm else None, parts[2]


def validate_skill(skill_dir: Path) -> list[str]:
    """Validate a single skill directory. Returns list of errors."""
    errors = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return [f"Missing SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    # --- Frontmatter checks ---
    if fm is None:
        errors.append("No valid YAML frontmatter found")
        return errors

    # Name
    name = fm.get("name", "")
    if not name:
        errors.append("Missing 'name' in frontmatter")
    elif len(name) > MAX_NAME_LEN:
        errors.append(f"Name too long ({len(name)} > {MAX_NAME_LEN})")
    elif not NAME_REGEX.match(name):
        errors.append(f"Name '{name}' invalid: must be lowercase + digits + hyphens, no leading/trailing/double hyphens")
    elif name != skill_dir.name:
        errors.append(f"Name '{name}' doesn't match directory '{skill_dir.name}'")

    # Description
    desc = fm.get("description", "")
    if not desc:
        errors.append("Missing 'description' in frontmatter")
    elif len(desc) > MAX_DESC_LEN:
        errors.append(f"Description too long ({len(desc)} > {MAX_DESC_LEN})")
    elif "<" in desc or ">" in desc:
        errors.append("Description contains angle brackets (< >)")

    # Unknown keys
    unknown = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unknown:
        errors.append(f"Unknown frontmatter keys: {unknown}")

    # --- Body checks ---
    body_lines = body.count("\n")
    if body_lines > MAX_BODY_LINES:
        errors.append(f"Body too long ({body_lines} lines > {MAX_BODY_LINES})")

    body_bytes = len(body.encode("utf-8"))
    if body_bytes > MAX_BODY_BYTES:
        errors.append(f"Body too large (~{body_bytes // 4} tokens > 5000)")

    # --- No-op detection (basic) ---
    no_op_phrases = [
        "be thorough", "write good code", "consider edge cases",
        "make sure to check", "quality matters", "best practices",
    ]
    body_lower = body.lower()
    for phrase in no_op_phrases:
        if phrase in body_lower:
            errors.append(f"Possible no-op phrase: '{phrase}'")

    # --- Cross-platform check ---
    if "os.path" in body and "pathlib" not in body:
        errors.append("Uses os.path — prefer pathlib.Path for cross-platform")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quick_validate.py <skill-dir> [<skill-dir> ...]")
        print("       python3 quick_validate.py skills/   # validate all")
        sys.exit(1)

    targets = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.is_dir() and (p / "SKILL.md").exists():
            targets.append(p)
        elif p.is_dir():
            # Assume it's a parent dir containing skill dirs
            targets.extend(sorted(d for d in p.iterdir() if (d / "SKILL.md").exists()))
        else:
            print(f"⚠️  Skipping: {arg} (not a skill directory)")

    if not targets:
        print("No skill directories found.")
        sys.exit(1)

    total_pass = 0
    total_fail = 0

    for skill_dir in targets:
        errors = validate_skill(skill_dir)
        if errors:
            total_fail += 1
            print(f"❌ {skill_dir.name}")
            for e in errors:
                print(f"   - {e}")
        else:
            total_pass += 1
            print(f"✅ {skill_dir.name}")

    print(f"\n{'='*40}")
    print(f"Results: {total_pass} passed, {total_fail} failed, {total_pass + total_fail} total")

    if total_fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
