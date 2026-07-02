#!/usr/bin/env python3
"""增强版 JSONL 解析器 - 从各 AI Runtime 的日志中提取使用数据"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter


# 分类模式
AGENT_PATTERNS = {
    "agent", "subagent", "worker", "explorer", "planner",
    "reviewer", "debugger", "executor", "Explore", "Plan"
}
CODEX_AGENT_TOOLS = {
    "spawn_agent", "send_input", "wait_agent",
    "close_agent", "resume_agent"
}
MCP_PREFIX = "mcp__"

CONTEXT_TRUNCATE = 200


def classify_tool(name: str, source_type: str = "") -> str:
    """分类工具类型"""
    if source_type == "skill":
        return "skill"
    if source_type in ("agent", "workflow"):
        return "agent"
    if source_type == "mcp":
        return "tool"
    if name in CODEX_AGENT_TOOLS:
        return "agent"
    if any(p in name for p in AGENT_PATTERNS):
        return "agent"
    if name.startswith(MCP_PREFIX) or "codegraph" in name:
        return "tool"
    return "tool"


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """解析时间戳"""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00")).replace(tzinfo=None)
    except (ValueError, AttributeError, TypeError):
        return None


# ============================================================
# Claude Code 解析器
# ============================================================

def parse_claude_tool_log(since: datetime) -> List[Dict[str, Any]]:
    """解析 ~/.claude/tool-usage.log (TSV from hook)"""
    records = []
    log_path = Path.home() / ".claude" / "tool-usage.log"

    if not log_path.exists():
        return records

    try:
        for line in log_path.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            try:
                ts = datetime.fromisoformat(parts[0])
            except ValueError:
                continue
            if ts < since:
                continue

            source_type = parts[1]
            name = parts[2]
            project = parts[3]

            records.append({
                "ts": ts.isoformat(),
                "runtime": "claude",
                "kind": classify_tool(name, source_type),
                "name": name,
                "project": project,
                "model": "",
                "context": (parts[4][:CONTEXT_TRUNCATE] if len(parts) > 4 else ""),
                "tokens_in": 0,
                "tokens_out": 0,
                "cache_read": 0,
                "cache_creation": 0,
                "latency_ms": 0,
                "cost_usd": 0.0,
                "outcome": "unknown",
                "triggered_by": "",
                "session_id": "",
            })
    except (OSError, PermissionError):
        pass

    return records


def parse_claude_skill_log(since: datetime) -> List[Dict[str, Any]]:
    """解析 ~/.claude/skill-usage.log (legacy skill log)"""
    records = []
    log_path = Path.home() / ".claude" / "skill-usage.log"

    if not log_path.exists():
        return records

    try:
        for line in log_path.read_text().splitlines():
            parts = line.split("  ", 2)
            if len(parts) < 2:
                parts = line.split(None, 2)
                if len(parts) < 2:
                    continue
                if parts[0].isdigit():
                    ts = datetime.fromtimestamp(int(parts[0]))
                    name = parts[2] if len(parts) > 2 else parts[1]
                    context = ""
                else:
                    continue
            else:
                ts_str = parts[0].strip()
                try:
                    ts = datetime.fromisoformat(ts_str)
                except ValueError:
                    continue
                rest = parts[1].split("  ", 1)
                name = rest[0].strip()
                context = (rest[1].strip()[:CONTEXT_TRUNCATE] if len(rest) > 1 else "")

            if ts < since:
                continue

            records.append({
                "ts": ts.isoformat(),
                "runtime": "claude",
                "kind": "skill",
                "name": name,
                "project": "",
                "model": "",
                "context": context,
                "tokens_in": 0,
                "tokens_out": 0,
                "cache_read": 0,
                "cache_creation": 0,
                "latency_ms": 0,
                "cost_usd": 0.0,
                "outcome": "unknown",
                "triggered_by": "",
                "session_id": "",
            })
    except (OSError, PermissionError):
        pass

    return records


def parse_claude_jsonl(since: datetime) -> List[Dict[str, Any]]:
    """解析 ~/.claude/projects/**/*.jsonl for tool_use events"""
    records = []
    projects_dir = Path.home() / ".claude" / "projects"

    if not projects_dir.exists():
        return records

    for jsonl_file in projects_dir.rglob("*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
            if mtime < since:
                continue
        except OSError:
            continue

        project = jsonl_file.parent.name.split("-")[-1] if "-" in jsonl_file.parent.name else ""
        session_id = jsonl_file.stem
        last_user_message = ""
        current_model = ""

        try:
            for line in jsonl_file.open(encoding='utf-8'):
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = d.get("type")
                message = d.get("message", {})

                # 跟踪用户消息
                if msg_type == "human":
                    content = message.get("content", "")
                    if isinstance(content, str):
                        last_user_message = content[:CONTEXT_TRUNCATE]
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                last_user_message = block.get("text", "")[:CONTEXT_TRUNCATE]
                                break

                # 解析助手消息
                if msg_type == "assistant":
                    content = message.get("content", [])
                    if not isinstance(content, list):
                        continue

                    # 提取 token 使用
                    usage = message.get("usage", {})
                    tokens_in = usage.get("input_tokens", 0)
                    tokens_out = usage.get("output_tokens", 0)
                    cache_read = usage.get("cache_read_input_tokens", 0)
                    cache_creation = usage.get("cache_creation_input_tokens", 0)

                    # 更新模型
                    if message.get("model"):
                        current_model = message["model"]

                    # 提取时间戳
                    ts_str = message.get("created_at", d.get("timestamp", ""))
                    ts = parse_timestamp(ts_str)
                    if not ts or ts < since:
                        continue

                    # 计算成本
                    from hook_collect import calculate_cost
                    cost = calculate_cost(tokens_in, tokens_out, cache_read, current_model)

                    # 解析工具调用
                    for block in content:
                        if not isinstance(block, dict):
                            continue

                        if block.get("type") == "tool_use":
                            tool_name = block.get("name", "")
                            if not tool_name:
                                continue

                            records.append({
                                "ts": ts.isoformat(),
                                "runtime": "claude",
                                "kind": classify_tool(tool_name),
                                "name": tool_name,
                                "project": project,
                                "model": current_model,
                                "context": "",
                                "tokens_in": tokens_in,
                                "tokens_out": tokens_out,
                                "cache_read": cache_read,
                                "cache_creation": cache_creation,
                                "latency_ms": 0,
                                "cost_usd": cost,
                                "outcome": "unknown",
                                "triggered_by": last_user_message,
                                "session_id": session_id,
                            })

        except (json.JSONDecodeError, OSError, PermissionError):
            continue

    return records


# ============================================================
# Codex 解析器
# ============================================================

def parse_codex_active_logs(since: datetime) -> List[Dict[str, Any]]:
    """解析 ~/.codex/{skill,agent,tool}-usage.log"""
    records = []
    log_dir = Path.home() / ".codex"

    log_map = [
        (log_dir / "skill-usage.log", "skill"),
        (log_dir / "agent-usage.log", "agent"),
        (log_dir / "tool-usage.log", "tool"),
    ]

    for log_path, kind in log_map:
        if not log_path.exists():
            continue

        try:
            for line in log_path.read_text().splitlines():
                parts = line.split("\t")
                if len(parts) < 2:
                    continue

                ts = parse_timestamp(parts[0].replace("Z", "+00:00"))
                if not ts or ts < since:
                    continue

                records.append({
                    "ts": ts.isoformat(),
                    "runtime": "codex",
                    "kind": kind,
                    "name": parts[1],
                    "project": "",
                    "model": "",
                    "context": (parts[2][:CONTEXT_TRUNCATE] if len(parts) > 2 else ""),
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "cache_read": 0,
                    "cache_creation": 0,
                    "latency_ms": 0,
                    "cost_usd": 0.0,
                    "outcome": "unknown",
                    "triggered_by": "",
                    "session_id": "",
                })
        except (OSError, PermissionError):
            continue

    return records


def parse_codex_sessions(since: datetime) -> List[Dict[str, Any]]:
    """解析 ~/.codex/sessions and archived_sessions

    从 session JSONL 中提取：
    - function_call / mcp_tool_call_end 事件（工具调用记录）
    - event_msg 中的 payload.info.last_token_usage（token 用量）
    """
    records = []
    session_dirs = [
        Path.home() / ".codex" / "sessions",
        Path.home() / ".codex" / "archived_sessions",
    ]

    for base_dir in session_dirs:
        if not base_dir.exists():
            continue

        for jsonl_file in base_dir.rglob("*.jsonl"):
            try:
                mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
                if mtime < since:
                    continue
            except OSError:
                continue

            session_id = jsonl_file.stem
            cwd = ""
            current_model = ""
            # 跟踪上次的累计 token，用于计算增量
            prev_total_in = 0
            prev_total_out = 0

            try:
                for line in jsonl_file.open(encoding='utf-8'):
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    p = d.get("payload", {})
                    if not isinstance(p, dict):
                        continue

                    # 提取会话元数据
                    if d.get("type") == "session_meta":
                        cwd = os.path.basename(p.get("cwd", ""))

                    # 提取模型信息
                    if d.get("type") == "turn_context":
                        current_model = str(p.get("model") or current_model)

                    ts_str = d.get("timestamp", "")

                    # 提取 token 用量（event_msg 中的 payload.info）
                    if d.get("type") == "event_msg":
                        info = p.get("info", {})
                        if isinstance(info, dict):
                            usage = info.get("last_token_usage", {})
                            if isinstance(usage, dict) and usage.get("input_tokens", 0) > 0:
                                ts = parse_timestamp(ts_str)
                                if ts and ts >= since:
                                    tokens_in = usage.get("input_tokens", 0)
                                    tokens_out = usage.get("output_tokens", 0)
                                    cache_read = usage.get("cached_input_tokens", 0)
                                    # 计算费用
                                    from hook_collect import calculate_cost
                                    cost = calculate_cost(tokens_in, tokens_out, cache_read, current_model)
                                    records.append({
                                        "ts": ts.isoformat(),
                                        "runtime": "codex",
                                        "kind": "tool",
                                        "name": "api-inference",
                                        "project": cwd,
                                        "model": current_model,
                                        "context": "",
                                        "tokens_in": tokens_in,
                                        "tokens_out": tokens_out,
                                        "cache_read": cache_read,
                                        "cache_creation": 0,
                                        "latency_ms": info.get("time_to_first_token_ms", 0),
                                        "cost_usd": cost,
                                        "outcome": "success",
                                        "triggered_by": "",
                                        "session_id": session_id,
                                    })

                    # function_call events
                    if "name" in p and p.get("type") == "function_call":
                        ts = parse_timestamp(ts_str)
                        if not ts or ts < since:
                            continue

                        name = p["name"]
                        records.append({
                            "ts": ts.isoformat(),
                            "runtime": "codex",
                            "kind": classify_tool(name),
                            "name": name,
                            "project": cwd,
                            "model": current_model,
                            "context": "",
                            "tokens_in": 0,
                            "tokens_out": 0,
                            "cache_read": 0,
                            "cache_creation": 0,
                            "latency_ms": 0,
                            "cost_usd": 0.0,
                            "outcome": "unknown",
                            "triggered_by": "",
                            "session_id": session_id,
                        })

                    # mcp_tool_call_end events
                    elif p.get("type") == "mcp_tool_call_end":
                        invocation = p.get("invocation", {})
                        if isinstance(invocation, dict) and invocation.get("tool"):
                            ts = parse_timestamp(ts_str)
                            if not ts or ts < since:
                                continue

                            tool_name = str(invocation["tool"])
                            server = str(invocation.get("server", ""))
                            full_name = f"{server}.{tool_name}" if server else tool_name

                            records.append({
                                "ts": ts.isoformat(),
                                "runtime": "codex",
                                "kind": "tool",
                                "name": full_name,
                                "project": cwd,
                                "model": current_model,
                                "context": "",
                                "tokens_in": 0,
                                "tokens_out": 0,
                                "cache_read": 0,
                                "cache_creation": 0,
                                "latency_ms": 0,
                                "cost_usd": 0.0,
                                "outcome": "unknown",
                                "triggered_by": "",
                                "session_id": session_id,
                            })

            except (json.JSONDecodeError, OSError, PermissionError):
                continue

    return records


# ============================================================
# 统一解析器
# ============================================================

def parse_all_runtimes(since: datetime, runtime: str = "all") -> List[Dict[str, Any]]:
    """解析所有 Runtime 的数据"""
    all_records = []

    # Claude Code
    if runtime in ("all", "claude"):
        all_records.extend(parse_claude_tool_log(since))
        all_records.extend(parse_claude_skill_log(since))
        all_records.extend(parse_claude_jsonl(since))

    # Codex
    if runtime in ("all", "codex"):
        all_records.extend(parse_codex_active_logs(since))
        all_records.extend(parse_codex_sessions(since))

    # 去重
    all_records = dedup_records(all_records)

    # 按时间排序
    all_records.sort(key=lambda r: r["ts"])

    return all_records


def dedup_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """去重 - 按 (minute, name, runtime, kind) 去重"""
    seen = set()
    result = []

    for r in records:
        try:
            ts = datetime.fromisoformat(r["ts"])
            key = (ts.strftime("%Y-%m-%dT%H:%M"), r["name"], r["runtime"], r["kind"])
        except (ValueError, KeyError):
            continue

        if key not in seen:
            seen.add(key)
            result.append(r)

    return result


if __name__ == "__main__":
    # 测试代码
    since = datetime.now() - __import__('datetime').timedelta(days=7)
    records = parse_all_runtimes(since)
    print(f"Found {len(records)} records")

    # 统计
    kind_counter = Counter(r["kind"] for r in records)
    runtime_counter = Counter(r["runtime"] for r in records)

    print(f"\nBy kind: {dict(kind_counter)}")
    print(f"By runtime: {dict(runtime_counter)}")
