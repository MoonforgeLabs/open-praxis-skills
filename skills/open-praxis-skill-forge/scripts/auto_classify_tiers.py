#!/usr/bin/env python3
"""
自动分类 skill 的 capability tiers

用法:
    python3 auto_classify_tiers.py                    # 分析当前 skill（交互式确认）
    python3 auto_classify_tiers.py --skill <name>     # 分析指定 skill
    python3 auto_classify_tiers.py --auto-confirm     # 自动确认，不提示用户
    python3 auto_classify_tiers.py -y                 # 同 --auto-confirm
    python3 auto_classify_tiers.py --json             # JSON 输出
    python3 auto_classify_tiers.py --check            # 检查分类准确性
"""

import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


# Python 标准库模块（3.8+）
STDLIB_MODULES = {
    'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio',
    'asyncore', 'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex',
    'bisect', 'builtins', 'bz2', 'calendar', 'cgi', 'cgitb', 'chunk',
    'cmath', 'cmd', 'code', 'codecs', 'codeop', 'collections', 'colorsys',
    'compileall', 'concurrent', 'configparser', 'contextlib', 'contextvars',
    'copy', 'copyreg', 'cProfile', 'crypt', 'csv', 'ctypes', 'curses',
    'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis', 'distutils',
    'doctest', 'email', 'encodings', 'enum', 'errno', 'faulthandler',
    'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fractions',
    'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob',
    'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'idlelib',
    'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress',
    'itertools', 'json', 'keyword', 'lib2to3', 'linecache', 'locale',
    'logging', 'lzma', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes',
    'mmap', 'modulefinder', 'multiprocessing', 'netrc', 'nis', 'nntplib',
    'numbers', 'operator', 'optparse', 'os', 'ossaudiodev', 'parser',
    'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform',
    'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile',
    'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue',
    'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter',
    'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex',
    'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket',
    'socketserver', 'sqlite3', 'sre_compile', 'sre_constants', 'sre_parse',
    'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess',
    'sunau', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile',
    'telnetlib', 'tempfile', 'termios', 'test', 'textwrap', 'threading',
    'time', 'timeit', 'tkinter', 'token', 'tokenize', 'trace', 'traceback',
    'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing',
    'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings',
    'wave', 'weakref', 'webbrowser', 'winreg', 'winsound', 'wsgiref',
    'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib',
    '_thread', '__future__',
}

# 常见的可选 CLI 工具
OPTIONAL_CLI_TOOLS = {
    'gh': 'GitHub CLI',
    'opencli': 'OpenCLI',
    'bili': 'Bilibili CLI',
    'yt-dlp': 'YouTube downloader',
    'ffmpeg': 'FFmpeg',
    'imagemagick': 'ImageMagick',
    'jq': 'JSON processor',
    'curl': 'HTTP client',
    'wget': 'HTTP client',
}

# 需要认证的 API 模式
AUTH_API_PATTERNS = [
    r'GITHUB_TOKEN',
    r'OPENAI_API_KEY',
    r'ANTHROPIC_API_KEY',
    r'API_KEY',
    r'ACCESS_TOKEN',
    r'AUTH_TOKEN',
    r'BEARER_TOKEN',
    r'secret',
    r'credential',
]

# 外部 skill 依赖模式
EXTERNAL_SKILL_PATTERNS = [
    r'last30days',
    r'praxis-search-hub',
    r'agent-reach',
    r'opencli',
    r'mcporter',
]


def parse_imports(file_path: Path, skill_dir: Path) -> Tuple[Set[str], Set[str]]:
    """解析 Python 文件的 imports"""
    stdlib_imports = set()
    third_party_imports = set()

    # 获取本地模块列表
    local_modules = set()
    for py_file in skill_dir.rglob("*.py"):
        if '__pycache__' not in str(py_file):
            local_modules.add(py_file.stem)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in STDLIB_MODULES:
                        stdlib_imports.add(module)
                    elif module not in local_modules:
                        third_party_imports.add(module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module in STDLIB_MODULES:
                        stdlib_imports.add(module)
                    elif module not in local_modules:
                        third_party_imports.add(module)
    except (SyntaxError, ValueError):
        pass

    return stdlib_imports, third_party_imports


def detect_cli_tools(content: str) -> Set[str]:
    """检测使用的 CLI 工具"""
    tools = set()

    # 检查 subprocess 调用
    subprocess_patterns = [
        r'subprocess\.(?:run|call|Popen|check_output)\s*\(\s*["\'](\w+)',
        r'os\.system\s*\(\s*["\'](\w+)',
        r'os\.popen\s*\(\s*["\'](\w+)',
    ]

    for pattern in subprocess_patterns:
        matches = re.findall(pattern, content)
        tools.update(matches)

    # 检查 which/where 命令
    which_patterns = [
        r'which\s+(\w+)',
        r'where\s+(\w+)',
        r'shutil\.which\s*\(\s*["\'](\w+)',
    ]

    for pattern in which_patterns:
        matches = re.findall(pattern, content)
        tools.update(matches)

    return tools


def detect_auth_apis(content: str) -> Set[str]:
    """检测使用的认证 API"""
    apis = set()

    # 排除字符串定义和注释
    lines = content.split('\n')
    for line in lines:
        # 跳过注释和字符串定义
        if line.strip().startswith('#') or line.strip().startswith("'") or line.strip().startswith('"'):
            continue
        # 跳过列表/字典定义
        if 'AUTH_API_PATTERNS' in line or 'EXTERNAL_SKILL_PATTERNS' in line:
            continue

        for pattern in AUTH_API_PATTERNS:
            # 检查是否实际使用（在 os.environ.get、os.getenv 等中）
            if re.search(rf'os\.environ\.get\s*\(\s*["\']{pattern}', line):
                apis.add(pattern)
            elif re.search(rf'os\.getenv\s*\(\s*["\']{pattern}', line):
                apis.add(pattern)
            elif re.search(rf'["\']{pattern}["\']', line) and ('=' in line or 'get' in line):
                apis.add(pattern)

    return apis


def detect_external_skills(content: str) -> Set[str]:
    """检测依赖的外部 skill"""
    skills = set()

    # 排除字符串定义和注释
    lines = content.split('\n')
    for line in lines:
        # 跳过注释和字符串定义
        if line.strip().startswith('#') or line.strip().startswith("'") or line.strip().startswith('"'):
            continue
        # 跳过列表/字典定义
        if 'EXTERNAL_SKILL_PATTERNS' in line:
            continue

        for pattern in EXTERNAL_SKILL_PATTERNS:
            # 检查是否实际导入或调用
            if re.search(rf'import\s+{pattern}', line):
                skills.add(pattern)
            elif re.search(rf'from\s+{pattern}', line):
                skills.add(pattern)
            elif re.search(rf'["\']{pattern}["\']', line) and ('=' in line or 'get' in line):
                skills.add(pattern)

    return skills


def detect_graceful_degradation(content: str) -> bool:
    """检测是否有优雅降级逻辑"""
    # 检查 try-except 模式
    graceful_patterns = [
        r'try:.*?except.*?:.*?(?:skip|pass|continue|fallback|default)',
        r'if.*?(?:not\s+exists|not\s+found|missing).*?:.*?(?:skip|pass|continue|fallback)',
        r'except.*?(?:ImportError|FileNotFoundError|OSError|PermissionError)',
        r'(?:skipped|unavailable|not\s+installed|missing)',
    ]

    for pattern in graceful_patterns:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            return True

    return False


def classify_command_tier(
    file_path: Path,
    content: str,
    command_name: str,
    skill_dir: Path
) -> Dict[str, any]:
    """分类单个命令的 tier"""
    stdlib_imports, third_party_imports = parse_imports(file_path, skill_dir)
    cli_tools = detect_cli_tools(content)
    auth_apis = detect_auth_apis(content)
    external_skills = detect_external_skills(content)
    has_degradation = detect_graceful_degradation(content)

    # 判定逻辑
    if external_skills or auth_apis:
        # 依赖外部 skill 或需要认证 API → ADVANCED
        return {
            "tier": "ADVANCED",
            "deps": list(external_skills) + list(auth_apis),
            "reason": "外部 skill 或认证 API 依赖",
        }
    elif third_party_imports or cli_tools - {'python3', 'python', 'pip'}:
        # 依赖第三方包或 CLI 工具
        if has_degradation:
            # 有优雅降级 → ENHANCED
            return {
                "tier": "ENHANCED",
                "deps": list(third_party_imports) + list(cli_tools),
                "reason": "可选依赖，有优雅降级",
            }
        else:
            # 无优雅降级 → ADVANCED
            return {
                "tier": "ADVANCED",
                "deps": list(third_party_imports) + list(cli_tools),
                "reason": "必需依赖，无优雅降级",
            }
    else:
        # 只使用标准库 → CORE
        return {
            "tier": "CORE",
            "deps": [],
            "reason": "Python 标准库，零外部依赖",
        }


def analyze_skill(skill_dir: Path) -> Dict[str, any]:
    """分析整个 skill 的 tiers"""
    results = {
        "skill_name": skill_dir.name,
        "tiers": {"CORE": [], "ENHANCED": [], "ADVANCED": []},
        "summary": {},
    }

    # 分析所有 Python 文件
    for py_file in skill_dir.rglob("*.py"):
        if '__pycache__' in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取命令名（简化：使用文件名）
            command_name = py_file.stem

            # 分类
            tier_info = classify_command_tier(py_file, content, command_name, skill_dir)
            tier_info["file"] = str(py_file.relative_to(skill_dir))
            tier_info["command"] = command_name

            results["tiers"][tier_info["tier"]].append(tier_info)
        except Exception as e:
            print(f"⚠️  分析 {py_file} 失败: {e}")

    # 统计
    for tier, commands in results["tiers"].items():
        results["summary"][tier] = len(commands)

    return results


def print_analysis(results: Dict[str, any], auto_confirm: bool = False):
    """打印分析结果"""
    print("=" * 60)
    print(f"📊 {results['skill_name']} Capability Tiers 分析")
    print("=" * 60)

    for tier in ["CORE", "ENHANCED", "ADVANCED"]:
        commands = results["tiers"][tier]
        if not commands:
            continue

        emoji = {"CORE": "🟢", "ENHANCED": "🟡", "ADVANCED": "🔴"}[tier]
        print(f"\n{emoji} {tier} ({len(commands)} 个)")

        for cmd in commands:
            deps = ", ".join(cmd["deps"]) if cmd["deps"] else "无"
            print(f"  - {cmd['command']}: {cmd['reason']}")
            if cmd["deps"]:
                print(f"    依赖: {deps}")

    # 统计
    summary = results["summary"]
    total = sum(summary.values())
    print("\n" + "=" * 60)
    print(f"总计: {total} 个命令")
    print(f"  🟢 CORE: {summary.get('CORE', 0)} ({summary.get('CORE', 0)/total*100:.0f}%)")
    print(f"  🟡 ENHANCED: {summary.get('ENHANCED', 0)} ({summary.get('ENHANCED', 0)/total*100:.0f}%)")
    print(f"  🔴 ADVANCED: {summary.get('ADVANCED', 0)} ({summary.get('ADVANCED', 0)/total*100:.0f}%)")
    print("=" * 60)

    # 开源建议
    core_count = summary.get('CORE', 0)
    enhanced_count = summary.get('ENHANCED', 0)
    advanced_count = summary.get('ADVANCED', 0)

    print("\n💡 开源建议:")
    if advanced_count == 0:
        print("  ✅ 所有命令都可以开源")
    else:
        keep_count = core_count + enhanced_count
        print(f"  ✅ 保留 CORE + ENHANCED: {keep_count}/{total}")
        print(f"  ❌ 移除 ADVANCED: {advanced_count}/{total}")

    # 用户确认
    if not auto_confirm:
        print("\n" + "=" * 60)
        print("❓ 请确认以上层级划分是否正确")
        print("=" * 60)

        # 收集用户反馈
        corrections = {}
        for tier in ["CORE", "ENHANCED", "ADVANCED"]:
            commands = results["tiers"][tier]
            if not commands:
                continue

            emoji = {"CORE": "🟢", "ENHANCED": "🟡", "ADVANCED": "🔴"}[tier]
            print(f"\n{emoji} {tier} 层级:")
            for cmd in commands:
                response = input(f"  {cmd['command']} → {tier} 正确吗？(y/n/新层级): ").strip().lower()
                if response == 'n':
                    new_tier = input(f"    应该是哪个层级？(CORE/ENHANCED/ADVANCED): ").strip().upper()
                    if new_tier in ["CORE", "ENHANCED", "ADVANCED"]:
                        corrections[cmd['command']] = new_tier
                        print(f"    ✅ 已修正: {cmd['command']} → {new_tier}")
                elif response in ["core", "enhanced", "advanced"]:
                    corrections[cmd['command']] = response.upper()
                    print(f"    ✅ 已修正: {cmd['command']} → {response.upper()}")

        # 应用修正
        if corrections:
            print("\n📝 应用修正...")
            for command, new_tier in corrections.items():
                # 在原结果中找到并移动
                for tier in ["CORE", "ENHANCED", "ADVANCED"]:
                    for cmd in results["tiers"][tier]:
                        if cmd["command"] == command:
                            results["tiers"][tier].remove(cmd)
                            cmd["tier"] = new_tier
                            cmd["reason"] = f"用户修正: {cmd['reason']}"
                            results["tiers"][new_tier].append(cmd)
                            break

            # 重新统计
            for tier in ["CORE", "ENHANCED", "ADVANCED"]:
                results["summary"][tier] = len(results["tiers"][tier])

            # 重新打印
            print_analysis(results, auto_confirm=True)

        # 确认保存
        print("\n" + "=" * 60)
        save = input("💾 是否保存层级划分？(y/n): ").strip().lower()
        if save == 'y':
            print("✅ 层级划分已确认")
            return True
        else:
            print("❌ 层级划分未保存")
            return False

    return True


def main():
    args = sys.argv[1:]

    # 确定 skill 目录
    if "--skill" in args:
        idx = args.index("--skill")
        if idx + 1 < len(args):
            skill_name = args[idx + 1]
            skill_dir = Path.home() / ".claude" / "skills" / skill_name
            if not skill_dir.exists():
                skill_dir = Path.home() / ".codex" / "skills" / skill_name
            if not skill_dir.exists():
                print(f"❌ Skill 不存在: {skill_name}")
                return
        else:
            print("❌ --skill 需要指定 skill 名称")
            return
    else:
        # 默认分析当前目录
        skill_dir = Path.cwd()
        if not (skill_dir / "SKILL.md").exists():
            # 尝试查找 skill 目录
            for parent in skill_dir.parents:
                if (parent / "SKILL.md").exists():
                    skill_dir = parent
                    break

    if not (skill_dir / "SKILL.md").exists():
        print(f"❌ 未找到 SKILL.md: {skill_dir}")
        return

    print(f"📦 分析 skill: {skill_dir.name}")
    print(f"   路径: {skill_dir}\n")

    # 分析
    results = analyze_skill(skill_dir)

    # 输出
    if "--json" in args:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        auto_confirm = "--auto-confirm" in args or "-y" in args
        confirmed = print_analysis(results, auto_confirm=auto_confirm)

        if confirmed:
            # 保存到文件
            output_file = skill_dir / "capability-tiers.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 层级划分已保存到: {output_file}")

    # 检查模式
    if "--check" in args:
        print("\n🔍 检查分类准确性...")
        # TODO: 对比人工标记的 tiers
        print("⚠️  检查功能尚未实现")


if __name__ == "__main__":
    main()
