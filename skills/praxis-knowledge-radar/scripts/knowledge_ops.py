#!/usr/bin/env python3
"""知识运维 — 间隔重复、知识 lint、内容质量分级、dedup

用法:
    python3 knowledge_ops.py review          # 查看今日复习任务（间隔重复）
    python3 knowledge_ops.py review --do     # 标记复习完成
    python3 knowledge_ops.py lint            # 知识质量检查
    python3 knowledge_ops.py lint --fix      # 自动修复可修复的问题
    python3 knowledge_ops.py grade           # 内容质量分级
    python3 knowledge_ops.py dedup           # 检查重复条目
    python3 knowledge_ops.py progress        # 学习进度追踪
    python3 knowledge_ops.py triage          # inbox 分拣

参考:
    - FSRS-6 间隔重复算法 (open-spaced-repetition)
    - Knowledge MEMO (owenliang60-ship-it/knowledge-mgmt): lint + retain
    - advanced-memory-mcp (sandraschi): inbox triage
    - research-knowledge-super-skill: content quality tiers
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

STORE = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "tasks.jsonl"

# ── FSRS-6 间隔重复参数 ──
# 间隔天数：复习后按此序列安排下次复习
FSRS_INTERVALS = [1, 3, 7, 14, 30, 90]  # 天


def load_records() -> list[dict[str, Any]]:
    if not STORE.exists():
        return []
    records = []
    with STORE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def save_records(records: list[dict[str, Any]]) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    with STORE.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ━━━ 间隔重复 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_review(args: argparse.Namespace) -> None:
    """显示今日需要复习的知识点，或标记复习完成。"""
    records = load_records()
    now = datetime.now(timezone.utc)
    today = now.date()

    # 找出需要复习的条目（learned 状态 + 有 review_schedule）
    due = []
    for r in records:
        if r.get("status") != "learned":
            continue
        schedule = r.get("review_schedule", [])
        if not schedule:
            # 从未安排过复习，安排第一次
            r["review_schedule"] = [1, 3, 7, 14, 30, 90]
            r["next_review"] = (now + timedelta(days=1)).isoformat(timespec="seconds")
            r["review_count"] = 0
            due.append(r)
            continue

        next_review = r.get("next_review", "")
        if not next_review:
            continue
        try:
            review_date = datetime.fromisoformat(next_review).date()
            if review_date <= today:
                due.append(r)
        except ValueError:
            continue

    if not due:
        print("✅ 今天没有需要复习的知识点")
        print(f"   总共 {len([r for r in records if r.get('status') == 'learned'])} 个已学完的条目")
        return

    print(f"📖 今日复习任务: {len(due)} 个\n")
    for i, r in enumerate(due, 1):
        review_count = r.get("review_count", 0)
        area = r.get("area", "?")
        title = r.get("title", "?")[:60]
        refs = r.get("references", [])
        ref = refs[0][:60] if refs else ""

        print(f"  {i}. [{area}] {title}")
        if ref:
            print(f"     {ref}")
        print(f"     已复习 {review_count} 次 | 下次: {r.get('next_review', '?')[:10]}")

        if args.do:
            # 标记复习完成，安排下次
            new_count = review_count + 1
            if new_count < len(FSRS_INTERVALS):
                interval = FSRS_INTERVALS[new_count]
                r["next_review"] = (now + timedelta(days=interval)).isoformat(timespec="seconds")
            else:
                r["next_review"] = (now + timedelta(days=FSRS_INTERVALS[-1])).isoformat(timespec="seconds")
            r["review_count"] = new_count
            r["last_reviewed"] = now.isoformat(timespec="seconds")
            print(f"     ✅ 复习完成，下次复习: {interval} 天后")

    if args.do:
        save_records(records)
        print(f"\n✅ 已更新 {len(due)} 个条目的复习计划")
    else:
        print(f"\n💡 使用 --do 标记复习完成")


# ━━━ 知识 Lint ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_lint(args: argparse.Namespace) -> None:
    """检查知识质量：重复、过期、不完整、孤儿条目。"""
    records = load_records()
    now = datetime.now(timezone.utc)
    issues = []

    # 1. 重复检查（同 URL）
    url_map: dict[str, list[int]] = {}
    for i, r in enumerate(records):
        for ref in r.get("references", []):
            url_map.setdefault(ref, []).append(i)
    for url, indices in url_map.items():
        if len(indices) > 1:
            issues.append({
                "type": "duplicate",
                "severity": "warning",
                "message": f"URL 重复: {url[:60]}",
                "ids": [records[i].get("id") for i in indices],
                "fix": "合并或删除重复条目",
            })

    # 2. 过期检查（inbox 超过 30 天未处理）
    stale_threshold = now - timedelta(days=30)
    for r in records:
        if r.get("status") == "inbox":
            created = r.get("created_at", "")
            try:
                created_dt = datetime.fromisoformat(created)
                if created_dt < stale_threshold:
                    days = (now - created_dt).days
                    issues.append({
                        "type": "stale",
                        "severity": "info",
                        "message": f"inbox 超过 {days} 天未处理: {r.get('title', '?')[:50]}",
                        "id": r.get("id"),
                        "fix": "归类学习或归档",
                    })
            except ValueError:
                pass

    # 3. 不完整检查（learned 但没有学习笔记）
    for r in records:
        if r.get("status") == "learned" and not r.get("notes"):
            issues.append({
                "type": "incomplete",
                "severity": "warning",
                "message": f"已学完但没有笔记: {r.get('title', '?')[:50]}",
                "id": r.get("id"),
                "fix": "补充学习笔记",
            })

    # 4. 孤儿检查（learned 超过 14 天但没 applied）
    orphan_threshold = now - timedelta(days=14)
    for r in records:
        if r.get("status") == "learned":
            updated = r.get("updated_at", "")
            try:
                updated_dt = datetime.fromisoformat(updated)
                if updated_dt < orphan_threshold:
                    issues.append({
                        "type": "orphan",
                        "severity": "info",
                        "message": f"学完 14+ 天但未应用: {r.get('title', '?')[:50]}",
                        "id": r.get("id"),
                        "fix": "应用到项目或归档",
                    })
            except ValueError:
                pass

    # 5. 无 area 检查
    for r in records:
        if r.get("status") in ("inbox", "next") and not r.get("area"):
            issues.append({
                "type": "no_area",
                "severity": "warning",
                "message": f"未分类: {r.get('title', '?')[:50]}",
                "id": r.get("id"),
                "fix": "分配 area",
            })

    # 输出
    if not issues:
        print("✅ 知识库质量良好，没有发现问题")
        return

    severity_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}
    print(f"📋 发现 {len(issues)} 个问题:\n")
    for issue in issues:
        icon = severity_icon.get(issue["severity"], "⚪")
        print(f"  {icon} [{issue['type']}] {issue['message']}")
        print(f"     修复: {issue['fix']}")

    # 统计
    by_type = Counter(i["type"] for i in issues)
    print(f"\n统计: {', '.join(f'{t}={c}' for t, c in by_type.items())}")

    if args.fix:
        fix_count = 0
        # 自动修复：给无 area 的条目分配 area
        for r in records:
            if r.get("status") in ("inbox", "next") and not r.get("area"):
                r["area"] = "inbox"
                fix_count += 1
        if fix_count:
            save_records(records)
            print(f"\n✅ 自动修复了 {fix_count} 个无 area 条目")


# ━━━ 内容质量分级 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_grade(args: argparse.Namespace) -> None:
    """给内容条目分级：A(权威)/B(高质量)/C(社区)/D(低质量)"""
    records = load_records()
    for r in records:
        if r.get("status") in ("done", "archived"):
            continue

        refs = r.get("references", [])
        source = r.get("source", "")
        grade = _grade_content(refs, source, r)
        r["content_grade"] = grade

    save_records(records)

    # 输出统计
    grades = Counter(r.get("content_grade", "?") for r in records if r.get("status") not in ("done", "archived"))
    print("📊 内容质量分级:\n")
    for g in ["A", "B", "C", "D", "?"]:
        if grades[g]:
            desc = {"A": "权威来源", "B": "高质量", "C": "社区内容", "D": "低质量", "?": "未分级"}.get(g, "")
            print(f"  {g} ({desc}): {grades[g]} 条")


def _grade_content(refs: list[str], source: str, record: dict) -> str:
    """根据来源和引用分级。"""
    url = refs[0].lower() if refs else ""

    # A 级：官方文档、学术论文
    if any(d in url for d in [
        "docs.github.com", "docs.python.org", "developer.mozilla.org",
        "arxiv.org", "anthropic.com", "openai.com", "arxiv.org",
        "docs.anthropic.com", "platform.openai.com",
    ]):
        return "A"

    # B 级：高星 GitHub 仓库、知名博客
    if "github.com" in url:
        return "B"
    if source in ("dingtalk", "manual") and any(kw in url for kw in ["blog", "article", "post"]):
        return "B"

    # C 级：社区内容
    if any(d in url for d in ["reddit.com", "twitter.com", "x.com", "medium.com", "dev.to"]):
        return "C"
    if source == "dingtalk":
        return "C"

    # D 级：其他
    return "D"


# ━━━ Dedup ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_dedup(args: argparse.Namespace) -> None:
    """检查并显示重复条目。"""
    records = load_records()
    url_map: dict[str, list[dict]] = {}
    title_map: dict[str, list[dict]] = {}

    for r in records:
        for ref in r.get("references", []):
            url_map.setdefault(ref, []).append(r)
        title = r.get("title", "").lower().strip()
        if title and len(title) > 5:
            title_map.setdefault(title, []).append(r)

    dupes = []
    for url, entries in url_map.items():
        if len(entries) > 1:
            dupes.append({"type": "url", "key": url[:60], "count": len(entries),
                          "ids": [e.get("id") for e in entries]})

    for title, entries in title_map.items():
        if len(entries) > 1:
            dupes.append({"type": "title", "key": title[:60], "count": len(entries),
                          "ids": [e.get("id") for e in entries]})

    if not dupes:
        print("✅ 没有重复条目")
        return

    print(f"🔍 发现 {len(dupes)} 组重复:\n")
    for d in dupes:
        print(f"  [{d['type']}] {d['key']} ({d['count']} 条)")
        print(f"    IDs: {', '.join(d['ids'])}")


# ━━━ 学习进度 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_progress(args: argparse.Namespace) -> None:
    """按 area 显示学习进度。"""
    records = load_records()
    area_stats: dict[str, dict[str, int]] = {}

    for r in records:
        area = r.get("area", "未分类")
        status = r.get("status", "unknown")
        area_stats.setdefault(area, {"total": 0, "inbox": 0, "learning": 0, "learned": 0, "applied": 0})
        area_stats[area]["total"] += 1
        if status in area_stats[area]:
            area_stats[area][status] += 1

    if not area_stats:
        print("📭 知识库为空")
        return

    print("📊 学习进度:\n")
    for area, stats in sorted(area_stats.items(), key=lambda x: x[1]["total"], reverse=True):
        total = stats["total"]
        done = stats["learned"] + stats["applied"]
        pct = int(done / total * 100) if total > 0 else 0
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)

        print(f"  {area:25s} {bar} {pct:3d}% ({done}/{total})")
        if stats["inbox"] > 0:
            print(f"    inbox: {stats['inbox']}  learning: {stats['learning']}  learned: {stats['learned']}  applied: {stats['applied']}")

    # 总计
    total_all = sum(s["total"] for s in area_stats.values())
    done_all = sum(s["learned"] + s["applied"] for s in area_stats.values())
    print(f"\n  总计: {total_all} 条，已完成 {done_all} 条 ({int(done_all/total_all*100) if total_all else 0}%)")


# ━━━ Inbox 分拣 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_triage(args: argparse.Namespace) -> None:
    """分拣 inbox 中的条目。"""
    records = load_records()
    inbox = [r for r in records if r.get("status") == "inbox"]

    if not inbox:
        print("✅ inbox 为空，没有需要分拣的条目")
        return

    print(f"📥 inbox 中有 {len(inbox)} 条待分拣:\n")
    for i, r in enumerate(inbox, 1):
        title = r.get("title", "?")[:55]
        area = r.get("area", "未分类")
        refs = r.get("references", [])
        ref = refs[0][:50] if refs else ""
        grade = r.get("content_grade", "?")

        print(f"  {i}. [{grade}] {title}")
        print(f"     area: {area} | {ref}")

    print(f"\n💡 使用以下命令分拣:")
    print(f"  python3 scripts/radar.py update <id> --status next --area <area> --priority P1")
    print(f"  python3 scripts/radar.py update <id> --status archived  # 不需要了")


# ━━━ CLI ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(required=True)

    review_p = sub.add_parser("review", help="今日复习任务")
    review_p.add_argument("--do", action="store_true", help="标记复习完成")
    review_p.set_defaults(func=cmd_review)

    lint_p = sub.add_parser("lint", help="知识质量检查")
    lint_p.add_argument("--fix", action="store_true", help="自动修复")
    lint_p.set_defaults(func=cmd_lint)

    grade_p = sub.add_parser("grade", help="内容质量分级")
    grade_p.set_defaults(func=cmd_grade)

    dedup_p = sub.add_parser("dedup", help="检查重复")
    dedup_p.set_defaults(func=cmd_dedup)

    progress_p = sub.add_parser("progress", help="学习进度")
    progress_p.set_defaults(func=cmd_progress)

    triage_p = sub.add_parser("triage", help="inbox 分拣")
    triage_p.set_defaults(func=cmd_triage)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
