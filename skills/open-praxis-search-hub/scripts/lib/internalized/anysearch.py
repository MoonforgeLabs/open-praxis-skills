"""
AnySearch 核心功能内化模块
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# AnySearch CLI 路径
ANYSEARCH_CLI = None
for path in [
    Path.home() / ".agents" / "skills" / "anysearch-skill" / "scripts" / "anysearch_cli.js",
    Path.home() / ".claude" / "skills" / "anysearch-skill" / "scripts" / "anysearch_cli.js",
]:
    if path.exists():
        ANYSEARCH_CLI = path
        break


def _run_cli(*args, timeout: int = 30) -> Dict[str, Any]:
    """运行 AnySearch CLI"""
    cmd = ["node", str(ANYSEARCH_CLI)] + [str(a) for a in args]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout}
        else:
            return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "Timeout"}
    except Exception as e:
        return {"error": str(e)}


def search(query: str, max_results: int = 10, domain: Optional[str] = None,
           sub_domain: Optional[str] = None, sdp: Optional[str] = None) -> Dict[str, Any]:
    """执行搜索"""
    args = ["search", query, "--max_results", str(max_results)]
    if domain:
        args.extend(["--domain", domain])
    if sub_domain:
        args.extend(["--sub_domain", sub_domain])
    if sdp:
        args.extend(["--sdp", sdp])
    return _run_cli(*args)


def batch_search(queries: List[str], max_results: int = 5,
                 domain: Optional[str] = None) -> Dict[str, Any]:
    """批量并行搜索"""
    args = ["batch_search"]
    for q in queries:
        args.extend(["--query", q])
    if domain:
        args.extend(["--domain", domain])
    return _run_cli(*args, timeout=60)


def extract(url: str) -> str:
    """提取网页内容为 Markdown"""
    result = _run_cli("extract", url)
    if "error" in result:
        return f"Error: {result['error']}"
    return result.get("output", result.get("content", ""))


def get_sub_domains(domain: str) -> List[Dict[str, Any]]:
    """获取垂直领域的子域名列表"""
    result = _run_cli("get_sub_domains", "--domain", domain)
    if "error" in result:
        return []
    output = result.get("output", "")
    sub_domains = []
    for line in output.split("\n"):
        if "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                sub_domains.append({"name": parts[0], "description": parts[1]})
    return sub_domains


def list_domains() -> List[str]:
    """列出所有支持的垂直领域"""
    return list(DOMAINS.keys())


DOMAINS = {
    "general": "通用搜索", "resource": "资源搜索", "social_media": "社交媒体",
    "finance": "金融", "academic": "学术", "legal": "法律", "health": "健康",
    "business": "商业", "security": "安全", "ip": "知识产权", "code": "代码",
    "energy": "能源", "environment": "环境", "agriculture": "农业",
    "travel": "旅行", "film": "电影", "gaming": "游戏",
}
