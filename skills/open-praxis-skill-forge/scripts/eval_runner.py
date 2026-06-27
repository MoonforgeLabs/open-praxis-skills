#!/usr/bin/env python3
"""
eval_runner.py — Test skill description trigger accuracy.

Usage:
    python3 scripts/eval_runner.py <skill-dir> --queries <queries-file>
    python3 scripts/eval_runner.py <skill-dir> --auto          # auto-generate queries

Queries file format (one per line):
    + <query that SHOULD trigger>
    - <query that SHOULD NOT trigger>

Exit codes: 0 = pass (≥80% accuracy), 1 = fail
"""

import json
import re
import sys
import random
from pathlib import Path


def load_queries(queries_path: Path) -> tuple[list[str], list[str]]:
    """Load queries from file. Returns (should_trigger, should_not_trigger)."""
    positive, negative = [], []
    for line in queries_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("+"):
            positive.append(line[1:].strip())
        elif line.startswith("-"):
            negative.append(line[1:].strip())
    return positive, negative


def auto_generate_queries(skill_dir: Path) -> tuple[list[str], list[str]]:
    """Generate queries by extracting trigger phrases from the description itself."""
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")

    # Extract description
    desc = ""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
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
                            desc = val.strip('"').strip("'")
                            break
                else:
                    if line.startswith('  ') or line.startswith('\t'):
                        desc_lines.append(line.strip())
                    else:
                        break
            if desc_lines:
                desc = ' '.join(desc_lines)

    positive = []
    negative = []

    # Extract quoted trigger phrases: "translate", "翻译", etc.
    quoted = re.findall(r'"([^"]+)"', desc)
    for q in quoted:
        if len(q) >= 2 and not q.startswith('http'):
            positive.append(q)

    # Extract Chinese trigger phrases (2+ chars, not common words)
    common_chinese = {"的", "了", "在", "是", "我", "你", "他", "她", "它", "们",
                      "这", "那", "有", "和", "与", "或", "但", "不", "也", "就",
                      "都", "很", "会", "能", "可以", "使用", "当", "用户", "提到"}
    chinese_phrases = re.findall(r'[一-鿿]{2,}', desc)
    for phrase in chinese_phrases:
        if phrase not in common_chinese and len(phrase) >= 2:
            positive.append(phrase)

    # Extract "Use when" triggers
    use_when = re.search(r'[Uu]se when[^.。]*', desc)
    if use_when:
        trigger_text = use_when.group().replace("Use when", "").replace("use when", "").strip()
        # Extract quoted items from "use when" section
        use_quoted = re.findall(r'"([^"]+)"', trigger_text)
        for q in use_quoted:
            if q not in positive:
                positive.append(q)

    # Generate negative queries (common tasks that should NOT trigger this skill)
    negative_pool = [
        "翻译这段话", "写代码", "画个图", "压缩图片", "今天天气怎么样",
        "create a diagram", "write a function", "compress this image",
        "format markdown", "generate a logo", "make a slide deck",
    ]
    # Filter out any that overlap with positive
    positive_set = set(p.lower() for p in positive)
    for n in negative_pool:
        if n.lower() not in positive_set:
            negative.append(n)

    # Deduplicate, limit to 10 each
    positive = list(dict.fromkeys(positive))[:10]
    negative = list(dict.fromkeys(negative))[:8]

    return positive, negative


def check_trigger(description: str, query: str) -> bool:
    """Check if a query would likely trigger this skill based on description overlap."""
    desc_lower = description.lower()
    query_lower = query.lower()

    # 1. Extract tokens: English words (3+ chars) and Chinese substrings (2+ chars)
    query_tokens = set(re.findall(r'[a-z]{3,}', query_lower))
    desc_tokens = set(re.findall(r'[a-z]{3,}', desc_lower))

    # 2. Extract Chinese characters and check substring containment
    query_chinese = set(re.findall(r'[一-鿿]+', query))
    desc_chinese = set(re.findall(r'[一-鿿]+', desc_lower))

    # 3. Check Chinese substring overlap (any 2+ char Chinese substring)
    for qc in query_chinese:
        for dc in desc_chinese:
            if len(qc) >= 2 and qc in dc:
                return True
            if len(dc) >= 2 and dc in qc:
                return True
            # Check character overlap for short phrases
            if len(qc) >= 2 and len(dc) >= 2:
                common = set(qc) & set(dc)
                if len(common) >= 2:
                    return True

    # 4. English token overlap
    overlap = query_tokens & desc_tokens
    if overlap:
        return True

    # 5. English substring containment
    for qt in query_tokens:
        if qt in desc_lower:
            return True
    for dt in desc_tokens:
        if dt in query_lower and len(dt) >= 3:
            return True

    return False


def run_eval(skill_dir: Path, positive: list[str], negative: list[str]) -> dict:
    """Run evaluation and return results."""
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")

    # Extract description (no PyYAML dependency)
    desc = ""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
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
                            desc = val.strip('"').strip("'")
                            break
                else:
                    if line.startswith('  ') or line.startswith('\t'):
                        desc_lines.append(line.strip())
                    else:
                        break
            if desc_lines:
                desc = ' '.join(desc_lines)

    if not desc:
        return {"error": "Could not parse description"}

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    details = []

    for query in positive:
        triggered = check_trigger(desc, query)
        if triggered:
            true_positive += 1
            details.append(f"  ✅ TP: '{query}' → triggered (correct)")
        else:
            false_negative += 1
            details.append(f"  ❌ FN: '{query}' → not triggered (should have)")

    for query in negative:
        triggered = check_trigger(desc, query)
        if not triggered:
            true_negative += 1
            details.append(f"  ✅ TN: '{query}' → not triggered (correct)")
        else:
            false_positive += 1
            details.append(f"  ❌ FP: '{query}' → triggered (should not have)")

    total = len(positive) + len(negative)
    correct = true_positive + true_negative
    accuracy = correct / total if total > 0 else 0
    trigger_rate = true_positive / len(positive) if positive else 0

    return {
        "skill": skill_dir.name,
        "total_queries": total,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "accuracy": round(accuracy, 3),
        "trigger_rate": round(trigger_rate, 3),
        "details": details,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 eval_runner.py <skill-dir> [--queries <file>] [--auto]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    if not (skill_dir / "SKILL.md").exists():
        print(f"Error: {skill_dir}/SKILL.md not found")
        sys.exit(1)

    positive, negative = [], []

    if "--queries" in sys.argv:
        idx = sys.argv.index("--queries")
        if idx + 1 < len(sys.argv):
            positive, negative = load_queries(Path(sys.argv[idx + 1]))
    elif "--auto" in sys.argv or len(sys.argv) == 2:
        positive, negative = auto_generate_queries(skill_dir)
    else:
        print("Specify --queries <file> or --auto")
        sys.exit(1)

    if not positive and not negative:
        print("No queries found. Use --queries <file> or --auto.")
        sys.exit(1)

    print(f"=== Eval: {skill_dir.name} ===")
    print(f"Queries: {len(positive)} positive, {len(negative)} negative")
    print()

    result = run_eval(skill_dir, positive, negative)

    for d in result.get("details", []):
        print(d)

    print()
    print(f"Accuracy: {result['accuracy']*100:.1f}% ({result['true_positive']+result['true_negative']}/{result['total_queries']})")
    print(f"Trigger rate: {result['trigger_rate']*100:.1f}% ({result['true_positive']}/{len(positive)})")

    # Output JSON if requested
    if "--json" in sys.argv:
        result.pop("details", None)
        print(json.dumps(result, indent=2))

    if result["accuracy"] >= 0.8:
        print("\n✅ PASS (≥80% accuracy)")
        sys.exit(0)
    else:
        print(f"\n❌ FAIL ({result['accuracy']*100:.1f}% < 80%)")
        sys.exit(1)


if __name__ == "__main__":
    main()
