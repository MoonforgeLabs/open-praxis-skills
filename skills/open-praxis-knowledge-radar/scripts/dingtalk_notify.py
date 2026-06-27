#!/usr/bin/env python3
"""
钉钉消息通知 - 用于发送扫描结果通知

用法:
    python3 dingtalk_notify.py send --title "标题" --content "内容"
    python3 dingtalk_notify.py test                    # 测试配置
"""

import json
import sys
import hashlib
import hmac
import base64
import time
import urllib.request
import urllib.parse
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "dingtalk-config.json"


def load_config() -> dict:
    """加载钉钉配置"""
    if not CONFIG_FILE.exists():
        return {}

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: dict):
    """保存钉钉配置"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_sign(timestamp: str, secret: str) -> str:
    """生成签名"""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign


def send_message(webhook: str, title: str, content: str, secret: str = None) -> bool:
    """发送钉钉消息"""
    timestamp = str(round(time.time() * 1000))

    # 构建请求 URL
    url = webhook
    if secret:
        sign = get_sign(timestamp, secret)
        url = f"{webhook}&timestamp={timestamp}&sign={sign}"

    # 构建消息体
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": f"## {title}\n\n{content}"
        }
    }

    # 发送请求
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('errcode') == 0:
                print(f"✅ 消息发送成功: {title}")
                return True
            else:
                print(f"❌ 消息发送失败: {result.get('errmsg', 'unknown error')}")
                return False
    except Exception as e:
        print(f"❌ 消息发送异常: {e}")
        return False


def setup_config(webhook: str = None, secret: str = None):
    """配置钉钉

    Args:
        webhook: Webhook URL（可选，如果不提供则交互式输入）
        secret: Secret（可选）
    """
    print("🔧 配置钉钉机器人")
    print("=" * 50)

    # 如果未提供 webhook，尝试交互式输入
    if not webhook:
        try:
            print("请在钉钉群中添加自定义机器人，获取 Webhook URL 和 Secret")
            print()
            webhook = input("请输入 Webhook URL: ").strip()
            if not webhook:
                print("❌ Webhook URL 不能为空")
                return

            secret_input = input("请输入 Secret (可选，直接回车跳过): ").strip()
            if secret_input:
                secret = secret_input
        except EOFError:
            print("❌ 无法读取输入，请使用命令行参数方式配置：")
            print("   python3 dingtalk_notify.py setup --webhook 'URL' --secret 'SECRET'")
            return

    # 验证 webhook
    if not webhook:
        print("❌ Webhook URL 不能为空")
        return

    # 保存配置
    config = {
        "webhook": webhook,
        "secret": secret,
        "enabled": True
    }
    save_config(config)

    print(f"\n✅ 配置已保存到: {CONFIG_FILE}")
    print(f"   Webhook: {webhook[:30]}...")

    # 测试发送
    print("\n发送测试消息...")
    send_message(webhook, "测试消息", "钉钉机器人配置成功！", secret)


def test_config():
    """测试钉钉配置"""
    config = load_config()

    if not config:
        print("❌ 未找到钉钉配置，请先运行: python3 dingtalk_notify.py setup")
        return False

    if not config.get('enabled'):
        print("❌ 钉钉通知已禁用")
        return False

    webhook = config.get('webhook')
    if not webhook:
        print("❌ Webhook URL 未配置")
        return False

    print(f"📋 当前配置:")
    print(f"   Webhook: {webhook[:30]}...")
    print(f"   Secret: {'已配置' if config.get('secret') else '未配置'}")

    # 测试发送
    return send_message(
        webhook,
        "测试消息",
        "这是来自 praxis-knowledge-rader 的测试消息",
        config.get('secret')
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "setup":
        # 解析参数
        webhook = None
        secret = None

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--webhook" and i + 1 < len(sys.argv):
                webhook = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--secret" and i + 1 < len(sys.argv):
                secret = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        setup_config(webhook, secret)
    elif command == "test":
        test_config()
    elif command == "send":
        # 解析参数
        title = None
        content = None

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--title" and i + 1 < len(sys.argv):
                title = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--content" and i + 1 < len(sys.argv):
                content = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        if not title or not content:
            print("❌ 请指定 --title 和 --content")
            return

        config = load_config()
        if not config or not config.get('webhook'):
            print("❌ 未找到钉钉配置，请先运行: python3 dingtalk_notify.py setup --webhook 'URL'")
            return

        send_message(
            config['webhook'],
            title,
            content,
            config.get('secret')
        )
    else:
        print(f"❌ 未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
