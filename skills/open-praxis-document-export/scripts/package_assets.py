#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import shutil
from datetime import datetime, timezone
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
TEXT_EXTS = {".txt", ".md", ".html", ".htm"}
DEFAULT_EXPORT_ROOT = Path("<WORKSPACE>/document-exports")


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



def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package authorized screenshots/images/files into an export bundle.")
    parser.add_argument("source", type=Path, help="File or directory to package")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--title", default="Document asset package")
    parser.add_argument("--recursive", action="store_true")
    return parser.parse_args()


def iter_files(source: Path, recursive: bool) -> list[Path]:
    if source.is_file():
        return [source]
    pattern = "**/*" if recursive else "*"
    return [path for path in source.glob(pattern) if path.is_file()]


def main() -> int:
    args = parse_args()
    source = args.source.expanduser().resolve()
    out = (args.out or (DEFAULT_EXPORT_ROOT / source.stem)).expanduser().resolve()
    assets = out / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    files = []
    markdown = [f"# {args.title}", ""]
    for index, path in enumerate(iter_files(source, args.recursive), 1):
        ext = path.suffix.lower()
        target_name = f"asset-{index:03d}{ext or '.bin'}"
        target = assets / target_name
        shutil.copy2(path, target)
        rel = f"assets/{target_name}"
        info = {
            "source": str(path),
            "path": rel,
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "content_type": mimetypes.guess_type(str(path))[0] or "application/octet-stream",
        }
        files.append(info)
        if ext in IMAGE_EXTS:
            markdown.append(f"## Image {index}: {path.name}")
            markdown.append("")
            markdown.append(f"![{path.name}]({rel})")
            markdown.append("")
        elif ext in TEXT_EXTS:
            markdown.append(f"## Text {index}: {path.name}")
            markdown.append("")
            try:
                markdown.append(path.read_text(encoding="utf-8", errors="replace")[:20000])
            except OSError:
                markdown.append("[Could not read text]")
            markdown.append("")
        else:
            markdown.append(f"- Packaged `{path.name}` as `{rel}`")
    metadata = {"title": args.title, "source": str(source), "exportedAt": datetime.now(timezone.utc).isoformat(), "files": files}
    (out / "document.md").write_text("\n".join(markdown).strip() + "\n", encoding="utf-8")
    (out / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readable_html(out, args.title)
    print(json.dumps({"ok": True, "out": str(out), "files": len(files), "readable": str(out / "readable.html")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
