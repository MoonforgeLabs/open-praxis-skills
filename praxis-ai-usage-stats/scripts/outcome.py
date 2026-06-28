#!/usr/bin/env python3
"""成功/失败启发式判断模块

参考 claude-skills-usage 的实现，根据用户后续消息和事件特征推断结果。
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


# 修正词列表
CORRECTION_WORDS = {
    # 中文
    "不对", "错误", "重试", "再来", "不行", "失败", "回退", "撤销",
    "不要", "停止", "取消", "算了", "没用", "无效", "有问题",
    # 英文
    "stop", "wrong", "error", "failed", "mistake", "undo", "retry",
    "cancel", "abort", "no", "not", "incorrect", "invalid", "issue",
    "problem", "bug", "fix", "broken",
}


def infer_outcome(events: List[Dict[str, Any]],
                  user_followup: str = "") -> str:
    """根据事件序列和用户后续消息推断结果

    Args:
        events: 事件列表
        user_followup: 用户后续消息

    Returns:
        "likely_solved", "likely_failed", 或 "unknown"
    """
    if not events:
        return "unknown"

    # 检查是否有中断
    if any(e.get("interrupted") for e in events):
        return "likely_failed"

    # 检查错误数量
    error_count = sum(e.get("error_count", 0) for e in events)
    if error_count >= 3:
        return "likely_failed"

    # 检查后续消息中的修正词
    if user_followup:
        followup_lower = user_followup.lower()
        if any(word in followup_lower for word in CORRECTION_WORDS):
            return "likely_failed"
        # 有后续消息且没有修正词，可能是成功的
        return "likely_solved"

    # 没有后续消息
    return "unknown"


def analyze_skill_flow(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析 skill 执行流程

    Args:
        events: 事件列表

    Returns:
        分析结果字典
    """
    if not events:
        return {
            "outcome": "unknown",
            "duration_ms": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "event_count": 0,
            "error_count": 0,
        }

    # 计算持续时间
    timestamps = []
    for e in events:
        ts_str = e.get("ts", "")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00").replace("+00:00", ""))
                timestamps.append(ts)
            except (ValueError, AttributeError):
                pass

    if len(timestamps) >= 2:
        duration = (max(timestamps) - min(timestamps)).total_seconds() * 1000
    else:
        duration = 0

    # 计算总 token
    total_tokens_in = sum(e.get("tokens_in", 0) for e in events)
    total_tokens_out = sum(e.get("tokens_out", 0) for e in events)
    total_tokens = total_tokens_in + total_tokens_out

    # 计算总成本
    total_cost = sum(e.get("cost_usd", 0.0) for e in events)

    # 计算错误数
    error_count = sum(e.get("error_count", 0) for e in events)

    # 推断结果
    outcome = infer_outcome(events)

    return {
        "outcome": outcome,
        "duration_ms": round(duration),
        "total_tokens": total_tokens,
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "total_cost": round(total_cost, 6),
        "event_count": len(events),
        "error_count": error_count,
    }


def analyze_session(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析整个会话

    Args:
        events: 会话中的所有事件

    Returns:
        会话分析结果
    """
    if not events:
        return {}

    # 按 session_id 分组
    sessions = {}
    for e in events:
        session_id = e.get("session_id", "unknown")
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append(e)

    # 分析每个会话
    session_analyses = []
    for session_id, session_events in sessions.items():
        analysis = analyze_skill_flow(session_events)
        analysis["session_id"] = session_id
        session_analyses.append(analysis)

    # 汇总
    total_events = sum(a["event_count"] for a in session_analyses)
    total_tokens = sum(a["total_tokens"] for a in session_analyses)
    total_cost = sum(a["total_cost"] for a in session_analyses)
    total_errors = sum(a["error_count"] for a in session_analyses)

    # 成功率
    success_count = sum(1 for a in session_analyses if a["outcome"] == "likely_solved")
    failed_count = sum(1 for a in session_analyses if a["outcome"] == "likely_failed")
    unknown_count = sum(1 for a in session_analyses if a["outcome"] == "unknown")

    return {
        "session_count": len(sessions),
        "total_events": total_events,
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 6),
        "total_errors": total_errors,
        "success_count": success_count,
        "failed_count": failed_count,
        "unknown_count": unknown_count,
        "success_rate": round(success_count / len(sessions) * 100, 1) if sessions else 0,
        "sessions": session_analyses,
    }


def mark_event_outcome(events: List[Dict[str, Any]],
                       event_index: int,
                       outcome: str,
                       user_followup: str = "") -> List[Dict[str, Any]]:
    """手动标记事件结果

    Args:
        events: 事件列表
        event_index: 事件索引
        outcome: 结果 ("likely_solved", "likely_failed", "unknown")
        user_followup: 用户后续消息

    Returns:
        更新后的事件列表
    """
    if 0 <= event_index < len(events):
        events[event_index]["outcome"] = outcome
        if user_followup:
            events[event_index]["user_followup"] = user_followup

    return events


def get_outcome_stats(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """获取结果统计

    Args:
        events: 事件列表

    Returns:
        统计结果
    """
    if not events:
        return {
            "total": 0,
            "likely_solved": 0,
            "likely_failed": 0,
            "unknown": 0,
            "success_rate": 0.0,
        }

    outcome_counts = {}
    for e in events:
        outcome = e.get("outcome", "unknown")
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

    total = len(events)
    likely_solved = outcome_counts.get("likely_solved", 0)
    likely_failed = outcome_counts.get("likely_failed", 0)
    unknown = outcome_counts.get("unknown", 0)

    # 成功率 = 成功 / (成功 + 失败)
    known_total = likely_solved + likely_failed
    success_rate = (likely_solved / known_total * 100) if known_total > 0 else 0.0

    return {
        "total": total,
        "likely_solved": likely_solved,
        "likely_failed": likely_failed,
        "unknown": unknown,
        "success_rate": round(success_rate, 1),
    }


if __name__ == "__main__":
    # 测试代码
    test_events = [
        {"ts": "2024-01-01T10:00:00", "tokens_in": 100, "tokens_out": 50, "error_count": 0},
        {"ts": "2024-01-01T10:01:00", "tokens_in": 200, "tokens_out": 100, "error_count": 0},
    ]

    # 测试推断
    result = infer_outcome(test_events, "好的，完成了")
    print(f"Outcome with followup: {result}")

    result = infer_outcome(test_events, "不对，重试")
    print(f"Outcome with correction: {result}")

    result = infer_outcome(test_events)
    print(f"Outcome without followup: {result}")

    # 测试分析
    analysis = analyze_skill_flow(test_events)
    print(f"\nAnalysis: {analysis}")

    # 测试统计
    stats = get_outcome_stats(test_events)
    print(f"\nStats: {stats}")
