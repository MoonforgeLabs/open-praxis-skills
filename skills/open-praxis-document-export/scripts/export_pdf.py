#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def import_pdf_libs():
    try:
        import pdfplumber  # type: ignore
        return "pdfplumber", pdfplumber
    except Exception:
        try:
            import pypdf  # type: ignore
            return "pypdf", pypdf
        except Exception as exc:
            raise RuntimeError("PDF export requires pdfplumber or pypdf. Use the Codex bundled Python runtime if available.") from exc


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



def extract_with_pdfplumber(path: Path) -> tuple[list[str], list[dict[str, object]]]:
    import pdfplumber  # type: ignore

    pages: list[str] = []
    meta_pages: list[dict[str, object]] = []
    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            pages.append(text.strip())
            meta_pages.append({"page": index, "chars": len(text), "width": page.width, "height": page.height})
    return pages, meta_pages


def extract_with_pypdf(path: Path) -> tuple[list[str], list[dict[str, object]]]:
    import pypdf  # type: ignore

    reader = pypdf.PdfReader(str(path))
    pages: list[str] = []
    meta_pages: list[dict[str, object]] = []
    for index, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        pages.append(text.strip())
        meta_pages.append({"page": index, "chars": len(text)})
    return pages, meta_pages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export an authorized PDF to a Markdown package.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--copy-source", action="store_true", help="Copy source PDF into assets/source.pdf")
    parser.add_argument("--title", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    title = args.title or pdf_path.stem
    out_dir = args.out or DEFAULT_EXPORT_ROOT / slugify(title)
    out_dir.mkdir(parents=True, exist_ok=True)
    backend, _ = import_pdf_libs()
    if backend == "pdfplumber":
        pages, page_meta = extract_with_pdfplumber(pdf_path)
    else:
        pages, page_meta = extract_with_pypdf(pdf_path)
    body: list[str] = []
    for index, text in enumerate(pages, 1):
        body.append(f"## Page {index}")
        body.append("")
        body.append(text or "[No extractable text on this page]")
        body.append("")
    assets = []
    if args.copy_source:
        assets_dir = out_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        target = assets_dir / "source.pdf"
        shutil.copy2(pdf_path, target)
        assets.append({"source": str(pdf_path), "path": "assets/source.pdf", "type": "source_pdf"})
    metadata = {
        "sourcePath": str(pdf_path),
        "title": title,
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "backend": backend,
        "pages": page_meta,
        "assets": assets,
    }
    frontmatter = {k: v for k, v in metadata.items() if k not in {"pages", "assets"}}
    (out_dir / "document.md").write_text("---\n" + json.dumps(frontmatter, ensure_ascii=False, indent=2) + "\n---\n\n# " + title + "\n\n" + "\n".join(body), encoding="utf-8")
    (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readable_html(out_dir, title)
    print(json.dumps({"ok": True, "out": str(out_dir), "title": title, "pages": len(pages), "backend": backend, "readable": str(out_dir / "readable.html")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
