"""Audit logging and response helpers for praxis-search-hub."""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


def audit(event: dict[str, Any]) -> None:
    """Write an audit event to the log file."""
    configured_path = Path(os.getenv("PRAXIS_SEARCH_AUDIT_LOG", "~/.praxis-search-hub/audit.jsonl")).expanduser()
    path = configured_path
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        path = Path("/tmp/praxis-search-hub/audit.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
    sanitized = {k: v for k, v in event.items() if k.lower() not in {"token", "authorization", "cookie"}}
    sanitized["ts"] = int(time.time())
    try:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(sanitized, ensure_ascii=False, sort_keys=True) + "\n")
    except OSError:
        pass


def response(**kwargs: Any) -> dict[str, Any]:
    """Create a response dict and audit it."""
    data = {"ok": True, "skipped": False, "results": []}
    data.update(kwargs)
    audit({k: v for k, v in data.items() if k != "results"})
    return data


def skipped(channel: str, query: str, reason: str, **extra: Any) -> dict[str, Any]:
    """Create a skipped response."""
    return response(ok=True, skipped=True, channel=channel, query=query, reason=reason, results=[], **extra)


def run_command(command: list[str], timeout: int = 45) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    return proc.returncode, proc.stdout, proc.stderr
