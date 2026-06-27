#!/usr/bin/env python3
"""配置钉钉集成 — 设置 AppKey/AppSecret 和监听群

用法:
    python3 setup_dingtalk.py                      # 交互式配置
    python3 setup_dingtalk.py --app-key xxx --app-secret yyy
    python3 setup_dingtalk.py --test               # 测试连接
    python3 setup_dingtalk.py --list-groups         # 列出可用群
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CONFIG_PATH = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "dingtalk-config.json"
DINGTALK_API = "https://api.dingtalk.com/v1.0"


def get_token(app_key: str, app_secret: str) -> str:
    url = f"{DINGTALK_API}/oauth2/accessToken"
    data = json.dumps({"appKey": app_key, "appSecret": app_secret}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read()).get("accessToken", "")


def list_groups(token: str) -> list[dict]:
    url = f"{DINGTALK_API}/im/v1.0/groups"
    req = urllib.request.Request(url, headers={"x-acs-dingtalk-access-token": token})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("groupInfos", [])
    except Exception as e:
        print(f"⚠️  获取群列表失败: {e}")
        return []


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 配置已保存到 {CONFIG_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Setup DingTalk integration")
    parser.add_argument("--app-key", help="DingTalk App Key")
    parser.add_argument("--app-secret", help="DingTalk App Secret")
    parser.add_argument("--chat-id", help="DingTalk Chat ID to monitor")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--list-groups", action="store_true", help="List available groups")
    args = parser.parse_args()

    # Load existing config
    config = {}
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    # Interactive setup if no args
    if not args.app_key and not args.test and not args.list_groups:
        print("=== 钉钉集成配置 ===\n")
        print("需要以下信息（从钉钉开放平台获取）：")
        print("  1. AppKey（应用凭证 → Client ID）")
        print("  2. AppSecret（应用凭证 → Client Secret）")
        print("  3. ChatID（要监听的群 ID，可通过 --list-groups 查看）\n")

        args.app_key = input(f"AppKey [{config.get('app_key', '未设置')}]: ").strip() or config.get("app_key", "")
        args.app_secret = input(f"AppSecret [{config.get('app_secret', '未设置')[:8]}...]: ").strip() or config.get("app_secret", "")

    # Update config
    if args.app_key:
        config["app_key"] = args.app_key
    if args.app_secret:
        config["app_secret"] = args.app_secret
    if args.chat_id:
        config["chat_id"] = args.chat_id

    # Test connection
    if args.test or args.list_groups or args.app_key:
        if not config.get("app_key") or not config.get("app_secret"):
            print("❌ 缺少 AppKey 或 AppSecret")
            return 1

        print("\n🔑 测试连接...")
        try:
            token = get_token(config["app_key"], config["app_secret"])
            print("✅ Token 获取成功")
        except Exception as e:
            print(f"❌ Token 获取失败: {e}")
            return 1

        if args.list_groups:
            print("\n📋 群列表:")
            groups = list_groups(token)
            if not groups:
                print("  （无群或权限不足）")
            for g in groups:
                print(f"  {g.get('name', '?'):30s} ChatID: {g.get('openConversationId', '?')}")

    # Save config
    save_config(config)

    print(f"\n配置文件: {CONFIG_PATH}")
    print("下一步: python3 scripts/dingtalk_fetch.py --dry-run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
