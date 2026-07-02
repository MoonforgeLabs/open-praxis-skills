#!/usr/bin/env python3
"""从 Codex Usage Proxy 日志导入 token 数据到 ai-usage-stats 数据库

用法:
    python3 codex_usage_import.py           # 导入新数据（增量）
    python3 codex_usage_import.py --all     # 重新导入全部
    python3 codex_usage_import.py --show    # 只显示不写入
"""

import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 日志路径
USAGE_LOG = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "codex_usage.jsonl"
# 数据库路径
DB_PATH = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "usage.db"
# 增量标记文件
MARKER_FILE = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / ".codex_usage_marker"


def load_log() -> List[Dict[str, Any]]:
    """加载 proxy 日志"""
    if not USAGE_LOG.exists():
        return []

    records = []
    for line in USAGE_LOG.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def get_last_offset() -> int:
    """获取上次处理到的行号"""
    if MARKER_FILE.exists():
        try:
            return int(MARKER_FILE.read_text().strip())
        except ValueError:
            return 0
    return 0


def save_offset(offset: int):
    """保存处理进度"""
    MARKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    MARKER_FILE.write_text(str(offset))


def calculate_cost(tokens_in: int, tokens_out: int, cache_read: int, model: str) -> float:
    """计算费用（复用 hook_collect 的费率逻辑）"""
    # 简化版费率表
    rates = {
        "gpt-5": {"input": 10.0, "output": 30.0, "cache_read": 1.0},
        "gpt-5.5": {"input": 10.0, "output": 30.0, "cache_read": 1.0},
        "gpt-4o": {"input": 5.0, "output": 15.0, "cache_read": 0.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.6, "cache_read": 0.0},
        "gpt-4": {"input": 30.0, "output": 60.0, "cache_read": 0.0},
        "claude-opus-4": {"input": 15.0, "output": 75.0, "cache_read": 1.5},
        "claude-sonnet-4": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
        "claude-haiku-4": {"input": 0.8, "output": 4.0, "cache_read": 0.08},
    }

    model_lower = model.lower()

    # 去掉代理前缀
    for prefix in ["pa/", "ppio/", "proxy/", "api/"]:
        if model_lower.startswith(prefix):
            model_lower = model_lower[len(prefix):]

    # 匹配费率
    rate = None
    for key, r in rates.items():
        if key in model_lower:
            rate = r
            break

    if not rate:
        rate = {"input": 3.0, "output": 15.0, "cache_read": 0.3}  # 默认

    cost = (
        tokens_in * rate["input"] +
        tokens_out * rate["output"] +
        cache_read * rate["cache_read"]
    ) / 1_000_000

    return round(cost, 6)


def insert_to_db(records: List[Dict[str, Any]]):
    """写入数据库"""
    if not DB_PATH.exists():
        print(f"❌ 数据库不存在: {DB_PATH}")
        print("   先运行一次 praxis-ai-usage-stats 初始化数据库")
        return

    conn = sqlite3.connect(DB_PATH)

    for r in records:
        model = r.get("model", "")
        tokens_in = r.get("tokens_in", 0)
        tokens_out = r.get("tokens_out", 0)
        cache_read = r.get("cache_read", 0)
        cost = calculate_cost(tokens_in, tokens_out, cache_read, model)

        conn.execute("""
            INSERT INTO events (ts, runtime, kind, name, model, tokens_in, tokens_out,
                                cache_read, latency_ms, cost_usd, outcome)
            VALUES (?, 'codex', 'tool', 'api-inference', ?, ?, ?, ?, ?, ?, 'success')
        """, (
            r.get("ts", datetime.now().isoformat()),
            model,
            tokens_in,
            tokens_out,
            cache_read,
            r.get("latency_ms", 0),
            cost,
        ))

    conn.commit()
    conn.close()


def main():
    show_only = "--show" in sys.argv
    import_all = "--all" in sys.argv

    print("🔍 扫描 Codex usage 日志...")
    records = load_log()

    if not records:
        print(f"  无记录 ({USAGE_LOG})")
        print("  确保 codex_usage_proxy.py 正在运行")
        return

    # 过滤已处理的
    last_offset = 0 if import_all else get_last_offset()
    new_records = records[last_offset:]

    if not new_records:
        print(f"  无新记录 (共 {len(records)} 条，已处理到第 {last_offset} 条)")
        return

    print(f"  找到 {len(new_records)} 条新记录 (共 {len(records)} 条)")

    # 统计
    total_in = sum(r.get("tokens_in", 0) for r in new_records)
    total_out = sum(r.get("tokens_out", 0) for r in new_records)
    total_cache = sum(r.get("cache_read", 0) for r in new_records)
    total_latency = sum(r.get("latency_ms", 0) for r in new_records)

    # 按模型分组
    models = {}
    for r in new_records:
        m = r.get("model", "unknown")
        if m not in models:
            models[m] = {"count": 0, "in": 0, "out": 0, "cost": 0}
        models[m]["count"] += 1
        models[m]["in"] += r.get("tokens_in", 0)
        models[m]["out"] += r.get("tokens_out", 0)
        models[m]["cost"] += calculate_cost(
            r.get("tokens_in", 0), r.get("tokens_out", 0),
            r.get("cache_read", 0), m
        )

    print(f"\n📊 Token 用量:")
    print(f"  输入 tokens: {total_in:,}")
    print(f"  输出 tokens: {total_out:,}")
    print(f"  缓存读取:   {total_cache:,}")
    print(f"  总 tokens:   {total_in + total_out:,}")
    print(f"  总耗时:      {total_latency / 1000:.1f}s")

    print(f"\n📋 按模型:")
    for m, stats in sorted(models.items(), key=lambda x: -x[1]["cost"]):
        print(f"  {m}: {stats['count']} 次, in={stats['in']:,} out={stats['out']:,}, ${stats['cost']:.4f}")

    total_cost = sum(s["cost"] for s in models.values())
    print(f"\n💰 总费用: ${total_cost:.4f}")

    if show_only:
        print("\n(--show 模式，不写入数据库)")
        return

    # 写入数据库
    insert_to_db(new_records)
    save_offset(len(records))
    print(f"\n✅ 已写入 {len(new_records)} 条记录到 {DB_PATH}")


if __name__ == "__main__":
    main()