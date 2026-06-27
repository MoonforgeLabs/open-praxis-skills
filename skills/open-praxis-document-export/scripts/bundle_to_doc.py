#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_EXPORT_ROOT = Path("<WORKSPACE>/document-exports")


def slugify(value: str, fallback: str = "document") -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", value).strip("-").lower()
    return value[:80] or fallback


def strip_frontmatter(markdown: str) -> str:
    if not markdown.startswith("---\n"):
        return markdown
    end = markdown.find("\n---\n", 4)
    if end == -1:
        return markdown
    return markdown[end + 5 :].lstrip()


def load_title(package: Path) -> str:
    metadata = package / "metadata.json"
    if metadata.exists():
        try:
            data = json.loads(metadata.read_text(encoding="utf-8"))
            if data.get("title"):
                return str(data["title"])
        except (OSError, json.JSONDecodeError):
            pass
    return package.name


def image_to_data_uri(package: Path, link: str) -> str:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link):
        return link
    image_path = (package / link).resolve()
    try:
        image_path.relative_to(package.resolve())
    except ValueError:
        return link
    if not image_path.exists() or not image_path.is_file():
        return link
    mime = mimetypes.guess_type(str(image_path))[0] or "application/octet-stream"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def markdown_inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def markdown_to_html(markdown: str, package: Path) -> str:
    lines = strip_frontmatter(markdown).splitlines()
    output: list[str] = []
    in_code = False
    code_lines: list[str] = []
    list_open = False

    def close_list() -> None:
        nonlocal list_open
        if list_open:
            output.append("</ul>")
            list_open = False

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                close_list()
                in_code = True
            continue
        if in_code:
            code_lines.append(raw)
            continue
        if not line.strip():
            close_list()
            continue
        image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if image_match:
            close_list()
            alt, link = image_match.groups()
            src = image_to_data_uri(package, link)
            output.append(f'<figure><img src="{html.escape(src)}" alt="{html.escape(alt)}"/><figcaption>{html.escape(alt)}</figcaption></figure>')
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            close_list()
            level = len(heading.group(1))
            output.append(f"<h{level}>{markdown_inline(heading.group(2))}</h{level}>")
            continue
        bullet = re.match(r"^\s*[-*+]\s+(.+)$", line)
        if bullet:
            if not list_open:
                output.append("<ul>")
                list_open = True
            output.append(f"<li>{markdown_inline(bullet.group(1))}</li>")
            continue
        close_list()
        output.append(f"<p>{markdown_inline(line)}</p>")
    close_list()
    if in_code:
        output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    return "\n".join(output)


def write_html(package: Path, out: Path, title: str) -> None:
    markdown_path = package / "document.md"
    if not markdown_path.exists():
        raise FileNotFoundError(markdown_path)
    body = markdown_to_html(markdown_path.read_text(encoding="utf-8"), package)
    rendered = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
<meta charset=\"utf-8\"/>
<title>{html.escape(title)}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.65; margin: 48px auto; max-width: 920px; color: #1f2328; }}
img {{ max-width: 100%; height: auto; border: 1px solid #d0d7de; border-radius: 8px; }}
figure {{ margin: 24px 0; }}
figcaption {{ color: #667085; font-size: 0.9em; margin-top: 6px; }}
pre {{ background: #f6f8fa; padding: 16px; overflow-x: auto; border-radius: 8px; }}
code {{ background: #f6f8fa; padding: 0.1em 0.3em; border-radius: 4px; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""
    out.write_text(rendered, encoding="utf-8")


def convert_with_pandoc(source: Path, target: Path) -> bool:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        return False
    subprocess.run([pandoc, str(source), "-o", str(target)], check=True)
    return True


def convert_with_textutil(source: Path, target: Path) -> bool:
    textutil = shutil.which("textutil")
    if not textutil or target.suffix.lower() != ".docx":
        return False
    subprocess.run([textutil, "-convert", "docx", str(source), "-output", str(target)], check=True)
    return True


def convert_with_chrome(source: Path, target: Path) -> bool:
    if target.suffix.lower() != ".pdf":
        return False
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    browser = next((item for item in candidates if Path(item).exists()), None)
    if not browser:
        return False
    subprocess.run([
        browser,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={target}",
        source.resolve().as_uri(),
    ], check=True)
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge an praxis-document-export package into a single HTML, DOCX, or PDF file.")
    parser.add_argument("package", type=Path, help="Export package directory containing document.md")
    parser.add_argument("--format", choices=["html", "docx", "pdf", "all"], default="html")
    parser.add_argument("--out", type=Path, default=None, help="Output file or directory. Defaults to the package directory")
    parser.add_argument("--title", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package = args.package.expanduser().resolve()
    title = args.title or load_title(package)
    formats = ["html", "docx", "pdf"] if args.format == "all" else [args.format]
    out_is_file = args.out and args.out.suffix and len(formats) == 1
    out_dir = (args.out.parent if out_is_file else (args.out or package)).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    base_name = slugify(title or package.name)
    html_path = (args.out.expanduser().resolve() if out_is_file and formats == ["html"] else out_dir / "readable.html")
    write_html(package, html_path, title)
    results = {"html": str(html_path)}
    for fmt in formats:
        if fmt == "html":
            continue
        target = (args.out.expanduser().resolve() if out_is_file else out_dir / f"document.{fmt}")
        ok = False
        if fmt == "docx":
            ok = convert_with_pandoc(html_path, target) or convert_with_textutil(html_path, target)
        elif fmt == "pdf":
            ok = convert_with_pandoc(html_path, target) or convert_with_chrome(html_path, target)
        results[fmt] = str(target) if ok else "conversion tool unavailable; HTML generated"
    manifest = {
        "sourcePackage": str(package),
        "title": title,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    (out_dir / "merge.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
