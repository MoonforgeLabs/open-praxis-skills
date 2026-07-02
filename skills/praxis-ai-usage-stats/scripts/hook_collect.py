#!/usr/bin/env python3
"""PostToolUse hook for Claude Code - 实时捕获 skill/tool/agent 调用

用法:
    在 ~/.claude/settings.json 中添加:
    {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "",
                    "hook": "python3 /path/to/hook_collect.py"
                }
            ]
        }
    }
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加父目录到 path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from db import UsageDB
except ImportError:
    # 如果 db 模块不存在，使用简单的文件日志
    UsageDB = None


# 模型费率 (per 1M tokens)
MODEL_RATES = {
    # Claude 3.5 系列
    "claude-3-5-sonnet": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
    "claude-3-5-haiku": {"input": 0.8, "output": 4.0, "cache_read": 0.08},
    # Claude 3 系列
    "claude-3-opus": {"input": 15.0, "output": 75.0, "cache_read": 1.5},
    "claude-3-haiku": {"input": 0.25, "output": 1.25, "cache_read": 0.03},
    "claude-3-sonnet": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
    # Claude 4 系列 (pa/ 前缀是代理服务)
    "claude-opus-4": {"input": 15.0, "output": 75.0, "cache_read": 1.5},
    "claude-sonnet-4": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
    "claude-haiku-4": {"input": 0.8, "output": 4.0, "cache_read": 0.08},
    # Xiaomi MiMo 系列
    "mimo-v2.5-pro": {"input": 0.435, "output": 0.87, "cache_read": 0.044},
    "mimo-v2.5": {"input": 0.105, "output": 0.28, "cache_read": 0.01},
    "mimo": {"input": 0.435, "output": 0.87, "cache_read": 0.044},
    # GPT 系列
    "gpt-5.5": {"input": 5.0, "output": 30.0, "cache_read": 0.5},
    "gpt-5": {"input": 2.5, "output": 15.0, "cache_read": 0.25},
    # ppio 代理服务（实际按 GPT-5 费率计费，非 GPT-5.5 官价）
    "ppio/": {"input": 2.5, "output": 15.0, "cache_read": 0.25},
    "gpt-4": {"input": 30.0, "output": 60.0, "cache_read": 0.0},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0, "cache_read": 0.0},
    "gpt-4o": {"input": 5.0, "output": 15.0, "cache_read": 0.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6, "cache_read": 0.0},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5, "cache_read": 0.0},
    # 本地模型 (免费)
    "ollama": {"input": 0.0, "output": 0.0, "cache_read": 0.0},
    "llama": {"input": 0.0, "output": 0.0, "cache_read": 0.0},
    "mistral": {"input": 0.0, "output": 0.0, "cache_read": 0.0},
    "qwen": {"input": 0.0, "output": 0.0, "cache_read": 0.0},
    "deepseek": {"input": 0.0, "output": 0.0, "cache_read": 0.0},
}

# 默认费率 (用于未知模型)
DEFAULT_RATE = {"input": 3.0, "output": 15.0, "cache_read": 0.3}


def classify_tool(tool_name: str, tool_input: dict = None) -> str:
    """分类工具类型"""
    if not tool_name:
        return "tool"

    # Agent 相关工具
    agent_patterns = {
        "agent", "subagent", "worker", "explorer", "planner",
        "reviewer", "debugger", "executor", "Explore", "Plan"
    }
    codex_agent_tools = {
        "spawn_agent", "send_input", "wait_agent",
        "close_agent", "resume_agent"
    }

    if tool_name in codex_agent_tools:
        return "agent"
    if any(p in tool_name for p in agent_patterns):
        return "agent"

    # Skill 工具
    if tool_name == "Skill":
        return "skill"

    # MCP 工具
    if tool_name.startswith("mcp__") or "codegraph" in tool_name.lower():
        return "tool"

    return "tool"


def get_skill_name(tool_input: dict) -> str:
    """从 tool_input 中提取 skill 名称"""
    if not tool_input:
        return "unknown"

    # Claude Code 的 Skill 工具
    if "skill" in tool_input:
        return tool_input["skill"]

    # 其他可能的字段
    for key in ["name", "command", "tool"]:
        if key in tool_input:
            return str(tool_input[key])

    return "unknown"


def match_model_rate(model: str) -> dict:
    """匹配模型费率，支持多种模型名格式

    支持的格式：
    - claude-3-5-sonnet-20241022
    - pa/claude-opus-4-6 (代理服务)
    - mimo-v2.5-pro (自定义模型)
    - ollama/llama3 (本地模型)
    """
    if not model:
        return DEFAULT_RATE

    model_lower = model.lower().strip()

    # ppio 代理服务特殊处理（实际按 GPT-5 费率，非官价）
    if 'ppio/' in model_lower:
        return MODEL_RATES.get('ppio/', DEFAULT_RATE)

    # 移除代理服务前缀 (pa/, proxy/, api/, ppio/ 等)
    prefixes_to_remove = ['ppio/', 'pa/', 'proxy/', 'api/', 'openai/', 'anthropic/']
    for prefix in prefixes_to_remove:
        while model_lower.startswith(prefix):
            model_lower = model_lower[len(prefix):]

    # 移除版本号后缀 (如 -20241022, -v1, -latest)
    import re
    model_lower = re.sub(r'-\d{8}$', '', model_lower)  # 移除日期后缀
    model_lower = re.sub(r'-v\d+$', '', model_lower)    # 移除版本号
    model_lower = re.sub(r'-latest$', '', model_lower)  # 移除 latest

    # 精确匹配优先
    if model_lower in MODEL_RATES:
        return MODEL_RATES[model_lower]

    # 模糊匹配 (子字符串匹配)
    for model_prefix, model_rate in MODEL_RATES.items():
        if model_prefix in model_lower:
            return model_rate

    # 特殊处理：检查是否包含关键词
    model_keywords = {
        'opus': MODEL_RATES.get('claude-3-opus', DEFAULT_RATE),
        'sonnet': MODEL_RATES.get('claude-3-5-sonnet', DEFAULT_RATE),
        'haiku': MODEL_RATES.get('claude-3-5-haiku', DEFAULT_RATE),
        'gpt-4o': MODEL_RATES.get('gpt-4o', DEFAULT_RATE),
        'gpt-4': MODEL_RATES.get('gpt-4', DEFAULT_RATE),
    }

    for keyword, rate in model_keywords.items():
        if keyword in model_lower:
            return rate

    return DEFAULT_RATE


def calculate_cost(tokens_in: int, tokens_out: int,
                   cache_read: int, model: str) -> float:
    """根据模型和 token 数量计算成本"""
    rate = match_model_rate(model)

    # 计算成本 (per 1M tokens)
    cost = (
        (tokens_in * rate["input"] +
         tokens_out * rate["output"] +
         cache_read * rate["cache_read"]) / 1_000_000
    )

    return round(cost, 6)


def extract_usage(data: dict) -> dict:
    """从 hook 数据中提取 token 使用信息"""
    usage = {}

    # 直接从 usage 字段
    if "usage" in data:
        usage = data["usage"]

    # 从 tool_result 中提取
    elif "tool_result" in data:
        result = data["tool_result"]
        if isinstance(result, dict) and "usage" in result:
            usage = result["usage"]

    return {
        "tokens_in": usage.get("input_tokens", 0),
        "tokens_out": usage.get("output_tokens", 0),
        "cache_read": usage.get("cache_read_input_tokens", 0),
        "cache_creation": usage.get("cache_creation_input_tokens", 0),
    }


def extract_error_count(data: dict) -> int:
    """从 hook 数据中提取错误数量"""
    error_count = 0

    # 检查 tool_result 中的错误
    if "tool_result" in data:
        result = data["tool_result"]
        if isinstance(result, dict):
            if result.get("is_error"):
                error_count += 1
            # 检查 content 中的错误
            content = result.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "error":
                        error_count += 1

    return error_count


def extract_model(data: dict) -> str:
    """从 hook 数据中提取模型信息"""
    # 直接从 model 字段
    if "model" in data:
        return data["model"]

    # 从 metadata 中提取
    if "metadata" in data:
        metadata = data["metadata"]
        if isinstance(metadata, dict) and "model" in metadata:
            return metadata["model"]

    return ""


def extract_session_id(data: dict) -> str:
    """从 hook 数据中提取会话 ID"""
    # 直接从 session_id 字段
    if "session_id" in data:
        return data["session_id"]

    # 从 metadata 中提取
    if "metadata" in data:
        metadata = data["metadata"]
        if isinstance(metadata, dict):
            for key in ["session_id", "conversation_id", "id"]:
                if key in metadata:
                    return str(metadata[key])

    return ""


def extract_project(data: dict) -> str:
    """从 hook 数据中提取项目信息"""
    # 从 cwd 中提取
    if "cwd" in data:
        return os.path.basename(data["cwd"])

    # 从 metadata 中提取
    if "metadata" in data:
        metadata = data["metadata"]
        if isinstance(metadata, dict):
            if "project" in metadata:
                return metadata["project"]
            if "cwd" in metadata:
                return os.path.basename(metadata["cwd"])

    # 从当前工作目录
    return os.path.basename(os.getcwd())


def save_to_file(event: dict):
    """当数据库不可用时，保存到文件"""
    log_dir = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "events.jsonl"

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')


def main():
    """主入口 - 从 stdin 读取 hook 数据"""
    try:
        # 从 stdin 读取 JSON 数据
        data = json.load(sys.stdin)

        # 提取基本信息
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # 确定事件类型和名称
        kind = classify_tool(tool_name, tool_input)
        name = tool_name

        if kind == "skill":
            name = get_skill_name(tool_input)
        elif kind == "agent":
            name = tool_name

        # 提取详细信息
        usage = extract_usage(data)
        model = extract_model(data)
        session_id = extract_session_id(data)
        project = extract_project(data)
        error_count = extract_error_count(data)

        # 计算成本
        cost = calculate_cost(
            usage["tokens_in"],
            usage["tokens_out"],
            usage["cache_read"],
            model
        )

        # 构建事件
        event = {
            "ts": datetime.now().isoformat(),
            "runtime": "claude",
            "kind": kind,
            "name": name,
            "project": project,
            "model": model,
            "context": "",
            "tokens_in": usage["tokens_in"],
            "tokens_out": usage["tokens_out"],
            "cache_read": usage["cache_read"],
            "cache_creation": usage["cache_creation"],
            "latency_ms": 0,  # 需要从前后事件计算
            "cost_usd": cost,
            "outcome": "unknown",
            "triggered_by": "",
            "user_followup": "",
            "interrupted": 0,
            "error_count": error_count,
            "session_id": session_id,
        }

        # 保存到数据库
        if UsageDB:
            try:
                db = UsageDB()
                db.insert_event(event)
                db.close()
            except Exception:
                # 数据库写入失败，降级到文件
                save_to_file(event)
        else:
            save_to_file(event)

    except Exception as e:
        # 永远不要让 hook 阻塞 Claude
        # 可以在这里记录错误到文件，但不要抛出异常
        pass


if __name__ == "__main__":
    main()
