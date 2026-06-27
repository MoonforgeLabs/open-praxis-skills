#!/usr/bin/env python3
"""
improve_description.py — Auto-improve skill description using LLM.

Usage:
    python3 scripts/improve_description.py <skill-dir>
    python3 scripts/improve_description.py <skill-dir> --iterations 3
    python3 scripts/improve_description.py <skill-dir> --dry-run  # show suggestion, don't write

Workflow: extract description → run eval → if fail, improve → re-eval → pick best.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

MAX_DESC_LEN = 1536
ITERATIONS_DEFAULT = 3


def extract_description(skill_md_path: Path) -> str:
    """Extract description from SKILL.md."""
    text = skill_md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""

    fm_lines = parts[1].splitlines()
    in_desc = False
    desc_lines = []
    for line in fm_lines:
        if not in_desc:
            m = re.match(r'^description:\s*(.*)', line)
            if m:
                val = m.group(1).strip()
                if val in ('|', '>', '|-', '>-'):
                    in_desc = True
                elif val:
                    return val.strip('"').strip("'")
        else:
            if line.startswith('  ') or line.startswith('\t'):
                desc_lines.append(line.strip())
            else:
                break
    return ' '.join(desc_lines) if desc_lines else ""


def run_eval(skill_dir: Path) -> dict:
    """Run eval_runner and return results."""
    script = Path(__file__).parent / "eval_runner.py"
    result = subprocess.run(
        [sys.executable, str(script), str(skill_dir), "--auto", "--json"],
        capture_output=True, text=True
    )
    # Parse the last line as JSON (skip stdout output)
    for line in reversed(result.stdout.strip().splitlines()):
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    return {"accuracy": 0, "trigger_rate": 0}


def improve_with_llm(description: str, eval_result: dict) -> str:
    """Use claude CLI to improve the description."""
    accuracy = eval_result.get("accuracy", 0)
    trigger_rate = eval_result.get("trigger_rate", 0)

    prompt = f"""You are optimizing a skill description for an AI agent skill discovery system.

Current description:
{description}

Current performance:
- Accuracy: {accuracy*100:.1f}% (queries correctly classified)
- Trigger rate: {trigger_rate*100:.1f}% (queries that should trigger actually trigger)

Rules for the improved description:
1. Start with action verb or "Use when..." format
2. Include specific trigger words users would actually say
3. Max {MAX_DESC_LEN} characters
4. Third person, not "I can help"
5. Do NOT describe the workflow — only describe WHEN to use it
6. Include both English and Chinese trigger phrases if applicable
7. Keep it concise — 100-200 chars is ideal

Return ONLY the improved description text, nothing else."""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=30
        )
        improved = result.stdout.strip()
        # Clean up: remove quotes if wrapped
        if improved.startswith('"') and improved.endswith('"'):
            improved = improved[1:-1]
        if improved.startswith("'") and improved.endswith("'"):
            improved = improved[1:-1]
        # Truncate if too long
        if len(improved) > MAX_DESC_LEN:
            improved = improved[:MAX_DESC_LEN]
        return improved
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def replace_description(skill_md_path: Path, new_desc: str):
    """Replace description in SKILL.md."""
    text = skill_md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return

    parts = text.split("---", 2)
    if len(parts) < 3:
        return

    fm_lines = parts[1].splitlines()
    new_fm_lines = []
    in_desc = False
    desc_replaced = False

    for line in fm_lines:
        if not in_desc and not desc_replaced:
            m = re.match(r'^description:\s*', line)
            if m:
                if new_desc and len(new_desc) <= 200:
                    new_fm_lines.append(f'description: >')
                    new_fm_lines.append(f'  {new_desc}')
                else:
                    new_fm_lines.append(f'description: >')
                    # Split long descriptions into multiple lines
                    words = new_desc.split()
                    current_line = '  '
                    for word in words:
                        if len(current_line) + len(word) + 1 > 76:
                            new_fm_lines.append(current_line.rstrip())
                            current_line = '  ' + word
                        else:
                            current_line += ' ' + word
                    if current_line.strip():
                        new_fm_lines.append(current_line.rstrip())
                in_desc = True
                continue
            else:
                new_fm_lines.append(line)
        elif in_desc:
            if line.startswith('  ') or line.startswith('\t'):
                continue  # skip old multiline description
            else:
                in_desc = False
                desc_replaced = True
                new_fm_lines.append(line)
        else:
            new_fm_lines.append(line)

    new_text = f"---\n{chr(10).join(new_fm_lines)}\n---{parts[2]}"
    skill_md_path.write_text(new_text, encoding="utf-8")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 improve_description.py <skill-dir> [--iterations N] [--dry-run]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        print(f"❌ {skill_md} not found")
        sys.exit(1)

    iterations = ITERATIONS_DEFAULT
    dry_run = False

    if "--iterations" in sys.argv:
        idx = sys.argv.index("--iterations")
        iterations = int(sys.argv[idx + 1])
    if "--dry-run" in sys.argv:
        dry_run = True

    print(f"=== Improve Description: {skill_dir.name} ===")
    print(f"Iterations: {iterations}, Dry-run: {dry_run}")
    print()

    # Step 1: Baseline eval
    print("Step 1: Baseline eval...")
    current_desc = extract_description(skill_md)
    if not current_desc:
        print("❌ Could not extract description")
        sys.exit(1)

    baseline = run_eval(skill_dir)
    baseline_acc = baseline.get("accuracy", 0)
    print(f"  Baseline accuracy: {baseline_acc*100:.1f}%")

    if baseline_acc >= 0.9:
        print("  ✅ Already ≥90% — no improvement needed")
        sys.exit(0)

    # Step 2: Iterate improvements
    best_desc = current_desc
    best_acc = baseline_acc

    for i in range(iterations):
        print(f"\nStep 2.{i+1}: Improving description...")
        improved = improve_with_llm(best_desc, baseline)
        if not improved:
            print("  ⚠️  LLM improvement failed, skipping")
            continue

        print(f"  Suggested: {improved[:100]}...")

        # Temporarily replace and eval
        if not dry_run:
            replace_description(skill_md, improved)
            result = run_eval(skill_dir)
            acc = result.get("accuracy", 0)
            print(f"  New accuracy: {acc*100:.1f}%")

            if acc > best_acc:
                best_desc = improved
                best_acc = acc
                print(f"  ✅ Improved! ({baseline_acc*100:.1f}% → {best_acc*100:.1f}%)")
            else:
                print(f"  ⚠️  No improvement, reverting")
                replace_description(skill_md, best_desc)

    # Step 3: Final result
    print(f"\n=== Result ===")
    print(f"Baseline: {baseline_acc*100:.1f}%")
    print(f"Final:    {best_acc*100:.1f}%")

    if best_acc > baseline_acc:
        print(f"✅ Improved by {(best_acc-baseline_acc)*100:.1f} percentage points")
        if dry_run:
            print(f"\nSuggested description:\n{best_desc}")
    else:
        print("⚠️  No improvement achieved")


if __name__ == "__main__":
    main()
