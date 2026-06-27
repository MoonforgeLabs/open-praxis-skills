#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

USER_AGENT = "praxis-document-export/0.1"


class MarkdownHTMLParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.lines: list[str] = []
        self.text_parts: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.skip_depth = 0
        self.heading_level = 0
        self.in_pre = False
        self.in_li = False
        self.in_table = False
        self.current_row: list[str] = []
        self.rows: list[list[str]] = []
        self.images: list[dict[str, str]] = []
        self.html_parts: list[str] = []

    def flush_text(self) -> None:
        if self.skip_depth:
            self.text_parts.clear()
            return
        text = " ".join("".join(self.text_parts).split())
        self.text_parts.clear()
        if not text:
            return
        if self.heading_level:
            self.lines.append(f"{'#' * self.heading_level} {text}")
            self.lines.append("")
        elif self.in_li:
            self.lines.append(f"- {text}")
        elif self.in_pre:
            self.lines.append(f"```\n{text}\n```")
            self.lines.append("")
        elif self.in_table:
            self.current_row.append(text.replace("|", "\\|"))
        else:
            self.lines.append(text)
            self.lines.append("")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        if tag in {"script", "style", "noscript", "iframe", "svg", "nav", "footer", "aside"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = True
            return
        elif re.fullmatch(r"h[1-6]", tag):
            self.flush_text()
            self.heading_level = int(tag[1])
        elif tag in {"p", "blockquote"}:
            self.flush_text()
        elif tag == "br":
            self.text_parts.append("\n")
        elif tag == "li":
            self.flush_text()
            self.in_li = True
        elif tag == "pre":
            self.flush_text()
            self.in_pre = True
        elif tag == "table":
            self.flush_text()
            self.in_table = True
            self.rows = []
        elif tag == "tr" and self.in_table:
            self.current_row = []
        elif tag == "img":
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "")
            if src:
                absolute = urljoin(self.base_url, src)
                self.images.append({"src": absolute, "alt": alt})
                self.lines.append(f"![{alt}]({absolute})")
                self.lines.append("")
        safe_attrs = []
        for key, value in attrs:
            if key.lower().startswith("on") or key.lower() in {"style", "class"}:
                continue
            if key.lower() in {"href", "src"} and value:
                value = urljoin(self.base_url, value)
            safe_attrs.append(f'{key}="{escape(value or "", quote=True)}"')
        self.html_parts.append("<" + tag + (" " + " ".join(safe_attrs) if safe_attrs else "") + ">")

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "title":
            self.in_title = False
            self.text_parts.clear()
        elif re.fullmatch(r"h[1-6]", tag):
            self.flush_text()
            self.heading_level = 0
        elif tag in {"p", "blockquote"}:
            self.flush_text()
        elif tag == "li":
            self.flush_text()
            self.in_li = False
        elif tag == "pre":
            self.flush_text()
            self.in_pre = False
        elif tag == "tr" and self.in_table:
            if self.current_row:
                self.rows.append(self.current_row)
            self.current_row = []
        elif tag in {"th", "td"} and self.in_table:
            self.flush_text()
        elif tag == "table":
            self.flush_text()
            self.emit_table()
            self.in_table = False
        self.html_parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_title:
            self.title_parts.append(data)
            return
        self.text_parts.append(data)
        self.html_parts.append(escape(data))

    def emit_table(self) -> None:
        if not self.rows:
            return
        width = max(len(row) for row in self.rows)
        rows = [row + [""] * (width - len(row)) for row in self.rows]
        self.lines.append("| " + " | ".join(rows[0]) + " |")
        self.lines.append("| " + " | ".join(["---"] * width) + " |")
        for row in rows[1:]:
            self.lines.append("| " + " | ".join(row) + " |")
        self.lines.append("")

    @property
    def markdown(self) -> str:
        self.flush_text()
        return "\n".join(line for line in self.lines).strip() + "\n"

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def cleaned_html(self) -> str:
        return "".join(self.html_parts)


DEFAULT_EXPORT_ROOT = Path("<WORKSPACE>/document-exports")


def slugify(value: str, fallback: str = "document") -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", value).strip("-").lower()
    return value[:80] or fallback

def write_readable_html(package_dir: Path, title: str) -> None:
    try:
        from bundle_to_doc import write_html
    except Exception:
        import importlib.util
        script = Path(__file__).with_name("bundle_to_doc.py")
        spec = importlib.util.spec_from_file_location("bundle_to_doc", script)
        if spec is None or spec.loader is None:
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        write_html = module.write_html
    write_html(package_dir, package_dir / "readable.html", title)



def fetch_text(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    if parsed.scheme in {"", "file"}:
        path = Path(urllib.request.url2pathname(parsed.path if parsed.scheme == "file" else url)).expanduser()
        return path.read_text(encoding="utf-8", errors="replace"), path.resolve().as_uri()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read()
        final_url = response.geturl()
        charset = response.headers.get_content_charset() or "utf-8"
    return data.decode(charset, errors="replace"), final_url


def fetch_bytes(url: str, referer: str) -> tuple[bytes, str]:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        path = Path(urllib.request.url2pathname(parsed.path)).expanduser()
        content = path.read_bytes()
        return content, mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Referer": referer})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(), response.headers.get_content_type()


def download_images(images: list[dict[str, str]], base_url: str, assets_dir: Path) -> list[dict[str, str]]:
    assets_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []
    for index, image in enumerate(images, 1):
        src = image["src"]
        try:
            content, content_type = fetch_bytes(src, base_url)
        except (urllib.error.URLError, TimeoutError, OSError):
            continue
        suffix = mimetypes.guess_extension(content_type) or Path(urlparse(src).path).suffix or ".bin"
        digest = hashlib.sha256(content).hexdigest()[:10]
        name = f"image-{index:03d}-{digest}{suffix}"
        path = assets_dir / name
        path.write_bytes(content)
        image["local"] = f"assets/{name}"
        downloaded.append({"source": src, "path": f"assets/{name}", "content_type": content_type, "alt": image.get("alt", "")})
    return downloaded


def rewrite_image_links(markdown: str, downloaded: list[dict[str, str]]) -> str:
    for item in downloaded:
        markdown = markdown.replace(f"]({item['source']})", f"]({item['path']})")
    return markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export an authorized URL to Markdown/HTML with optional images.")
    parser.add_argument("url")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--images", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--title", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    html, final_url = fetch_text(args.url)
    parser = MarkdownHTMLParser(final_url)
    parser.feed(html)
    title = args.title or parser.title or urlparse(final_url).netloc or "document"
    out_dir = args.out or DEFAULT_EXPORT_ROOT / slugify(title)
    out_dir.mkdir(parents=True, exist_ok=True)
    downloaded = download_images(parser.images, final_url, out_dir / "assets") if args.images else []
    markdown = rewrite_image_links(parser.markdown, downloaded)
    metadata = {
        "sourceUrl": args.url,
        "finalUrl": final_url,
        "title": title,
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "imagesDownloaded": len(downloaded),
        "images": downloaded,
    }
    (out_dir / "document.md").write_text("---\n" + json.dumps({k: v for k, v in metadata.items() if k != "images"}, ensure_ascii=False, indent=2) + "\n---\n\n" + markdown, encoding="utf-8")
    if args.html:
        (out_dir / "document.html").write_text(parser.cleaned_html, encoding="utf-8")
    (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readable_html(out_dir, title)
    print(json.dumps({"ok": True, "out": str(out_dir), "title": title, "images": len(downloaded), "readable": str(out_dir / "readable.html")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
