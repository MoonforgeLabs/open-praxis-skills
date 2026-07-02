#!/usr/bin/env python3
"""Codex Token Usage Logging Proxy

在 CC Switch 前面加一层透明代理，拦截 API 响应提取 token 用量。

架构: Codex → Proxy (15720) → CC Switch (15721) → ppio

用法:
    python3 codex_usage_proxy.py              # 前台运行
    python3 codex_usage_proxy.py --port 15720 # 指定端口
    python3 codex_usage_proxy.py --daemon     # 后台运行
"""

import json
import sys
import os
import time
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.client import HTTPConnection
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 配置（用 dict 避免 global 声明问题）
CONFIG = {
    "listen_host": "127.0.0.1",
    "listen_port": 15720,
    "upstream_host": "127.0.0.1",
    "upstream_port": 15721,
}

# 日志路径
DATA_DIR = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats"
USAGE_LOG = DATA_DIR / "codex_usage.jsonl"
PID_FILE = DATA_DIR / "codex_usage_proxy.pid"

# 北京时间
CST = timezone(timedelta(hours=8))

# 不转发的 hop-by-hop 头
HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
}


def log(msg: str):
    ts = datetime.now(CST).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def save_usage(record: dict):
    """追加写入 JSONL 日志"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(USAGE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def extract_usage_from_response(body: bytes) -> dict | None:
    """从非流式响应中提取 usage"""
    try:
        data = json.loads(body)
        usage = data.get("usage")
        if usage:
            return {
                "tokens_in": usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0),
                "tokens_out": usage.get("output_tokens", 0) or usage.get("completion_tokens", 0),
                "cache_read": usage.get("cache_read_input_tokens", 0),
                "model": data.get("model", ""),
            }
    except (json.JSONDecodeError, AttributeError):
        pass
    return None


def extract_usage_from_sse_line(line: str) -> dict | None:
    """从 SSE 行中提取 usage 数据"""
    if not line.startswith("data: "):
        return None

    payload = line[6:].strip()
    if payload == "[DONE]":
        return None

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None

    # OpenAI responses API: response.completed 事件
    if data.get("type") == "response.completed":
        response = data.get("response", {})
        usage = response.get("usage", {})
        if usage:
            return {
                "tokens_in": usage.get("input_tokens", 0),
                "tokens_out": usage.get("output_tokens", 0),
                "cache_read": usage.get("cache_read_input_tokens", 0),
                "model": response.get("model", ""),
            }

    # OpenAI chat completions API: 最后一个 chunk 带 usage
    usage = data.get("usage")
    if usage:
        return {
            "tokens_in": usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0),
            "tokens_out": usage.get("completion_tokens", 0) or usage.get("output_tokens", 0),
            "cache_read": usage.get("cache_read_input_tokens", 0),
            "model": data.get("model", ""),
        }

    return None


class ProxyHandler(BaseHTTPRequestHandler):
    """透明 HTTP 代理，拦截响应提取 usage"""

    def log_message(self, format, *args):
        pass

    def _proxy_request(self, method: str):
        """转发请求到上游 CC Switch"""
        start_time = time.time()
        path = self.path

        upstream_conn = HTTPConnection(
            CONFIG["upstream_host"], CONFIG["upstream_port"], timeout=300
        )

        # 收集请求头（去掉 hop-by-hop）
        headers = {}
        for key, val in self.headers.items():
            if key.lower() not in HOP_BY_HOP:
                headers[key] = val

        # 读取请求体
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # 检测是否为流式请求
        is_streaming = False
        if body:
            try:
                req_data = json.loads(body)
                is_streaming = req_data.get("stream", False)
            except (json.JSONDecodeError, AttributeError):
                pass

        try:
            upstream_conn.request(method, path, body=body, headers=headers)
            resp = upstream_conn.getresponse()
        except Exception as e:
            log(f"❌ 上游连接失败: {e}")
            self.send_error(502, f"Bad Gateway: {e}")
            return

        # 构建响应头
        self.send_response(resp.status)
        resp_headers = {}
        for key, val in resp.getheaders():
            if key.lower() not in HOP_BY_HOP:
                self.send_header(key, val)
                resp_headers[key.lower()] = val
        self.end_headers()

        # 转发响应体
        usage_data = None

        if is_streaming and resp_headers.get("content-type", "").startswith("text/event-stream"):
            # 流式响应：逐 chunk 转发并提取 usage
            buffer = b""
            for chunk in iter(lambda: resp.read(4096), b""):
                self.wfile.write(chunk)
                self.wfile.flush()
                buffer += chunk

                # 按行处理 SSE
                while b"\n" in buffer:
                    line_bytes, buffer = buffer.split(b"\n", 1)
                    line = line_bytes.decode("utf-8", errors="ignore").strip()
                    if line:
                        extracted = extract_usage_from_sse_line(line)
                        if extracted:
                            usage_data = extracted
        else:
            # 非流式响应：读取完整响应体
            resp_body = resp.read()
            self.wfile.write(resp_body)
            self.wfile.flush()
            usage_data = extract_usage_from_response(resp_body)

        latency_ms = int((time.time() - start_time) * 1000)

        # 记录 usage
        if usage_data and (usage_data["tokens_in"] > 0 or usage_data["tokens_out"] > 0):
            record = {
                "ts": datetime.now(CST).isoformat(),
                "model": usage_data.get("model", ""),
                "tokens_in": usage_data["tokens_in"],
                "tokens_out": usage_data["tokens_out"],
                "cache_read": usage_data.get("cache_read", 0),
                "latency_ms": latency_ms,
                "endpoint": path,
                "streaming": is_streaming,
            }
            save_usage(record)
            log(f"📊 {record['model']} | in={record['tokens_in']:,} out={record['tokens_out']:,} | {latency_ms}ms")

        upstream_conn.close()

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "proxy": "codex-usage-logger"}).encode())
            return
        self._proxy_request("GET")

    def do_POST(self):
        self._proxy_request("POST")

    def do_PUT(self):
        self._proxy_request("PUT")

    def do_DELETE(self):
        self._proxy_request("DELETE")

    def do_PATCH(self):
        self._proxy_request("PATCH")

    def do_OPTIONS(self):
        self._proxy_request("OPTIONS")


def write_pid():
    """写入 PID 文件"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))


def cleanup_pid(*args):
    """清理 PID 文件"""
    PID_FILE.unlink(missing_ok=True)
    log("🛑 Proxy 已停止")
    sys.exit(0)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Codex Token Usage Logging Proxy")
    parser.add_argument("--port", type=int, default=15720, help="监听端口")
    parser.add_argument("--upstream-port", type=int, default=15721, help="上游端口")
    parser.add_argument("--daemon", action="store_true", help="后台运行")
    args = parser.parse_args()

    CONFIG["listen_port"] = args.port
    CONFIG["upstream_port"] = args.upstream_port

    if args.daemon:
        if os.fork() > 0:
            sys.exit(0)
        os.setsid()
        if os.fork() > 0:
            sys.exit(0)
        log_file = DATA_DIR / "codex_usage_proxy.log"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        sys.stdout = open(log_file, "a")
        sys.stderr = sys.stdout

    server = HTTPServer((CONFIG["listen_host"], CONFIG["listen_port"]), ProxyHandler)

    signal.signal(signal.SIGINT, cleanup_pid)
    signal.signal(signal.SIGTERM, cleanup_pid)
    write_pid()

    log(f"🚀 Codex Usage Proxy 启动")
    log(f"   监听: {CONFIG['listen_host']}:{CONFIG['listen_port']}")
    log(f"   上游: {CONFIG['upstream_host']}:{CONFIG['upstream_port']} (CC Switch)")
    log(f"   日志: {USAGE_LOG}")
    log(f"   PID: {os.getpid()}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        cleanup_pid()


if __name__ == "__main__":
    main()
