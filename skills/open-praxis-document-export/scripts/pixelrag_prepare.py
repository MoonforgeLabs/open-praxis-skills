#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
from datetime import datetime, timezone
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
PDF_EXTS = {".pdf"}
HTML_EXTS = {".html", ".htm"}
VISUAL_DIR_HINTS = {"diagrams", "visuals", "screenshots", "images", "figures", "charts", "tables"}
DEFAULT_TILE_SIZE = 1024
DEFAULT_OVERLAP = 128


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def strip_frontmatter(markdown: str) -> str:
    if not markdown.startswith("---\n"):
        return markdown
    end = markdown.find("\n---\n", 4)
    if end == -1:
        return markdown
    return markdown[end + 5 :].lstrip()


def markdown_image_links(package: Path) -> set[str]:
    doc = package / "document.md"
    if not doc.exists():
        return set()
    text = strip_frontmatter(doc.read_text(encoding="utf-8", errors="replace"))
    return {match.group(1) for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text)}


def is_visual_candidate(path: Path, package: Path) -> bool:
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTS | PDF_EXTS | HTML_EXTS:
        return True
    parts = {part.lower() for part in path.relative_to(package).parts[:-1]}
    return bool(parts & VISUAL_DIR_HINTS)


def candidate_reason(path: Path, package: Path, linked_images: set[str]) -> list[str]:
    rel = path.relative_to(package).as_posix()
    suffix = path.suffix.lower()
    reasons: list[str] = []
    if rel in linked_images:
        reasons.append("referenced-by-document-md")
    if suffix in IMAGE_EXTS:
        reasons.append("image-asset")
    if suffix in PDF_EXTS:
        reasons.append("source-or-exported-pdf")
    if suffix in HTML_EXTS:
        reasons.append("html-rendering")
    parts = {part.lower() for part in path.relative_to(package).parts[:-1]}
    matched = sorted(parts & VISUAL_DIR_HINTS)
    if matched:
        reasons.append("visual-directory:" + ",".join(matched))
    return reasons or ["visual-candidate"]


def iter_candidates(package: Path) -> list[Path]:
    files = [path for path in package.rglob("*") if path.is_file()]
    ignored_names = {"metadata.json", "merge.json", "pixelrag-manifest.json", "document.md"}
    return [path for path in files if path.name not in ignored_names and is_visual_candidate(path, package)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a PixelRAG handoff manifest for an praxis-document-export package.")
    parser.add_argument("package", type=Path, help="Export package directory containing document.md/assets/readable.html")
    parser.add_argument("--out", type=Path, default=None, help="Manifest path. Defaults to package/pixelrag-manifest.json")
    parser.add_argument("--tile-size", type=int, default=DEFAULT_TILE_SIZE)
    parser.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP)
    parser.add_argument("--include-html", action="store_true", help="Include readable.html/document.html as render targets")
    parser.add_argument("--include-pdf", action="store_true", help="Include source/exported PDFs as render targets")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package = args.package.expanduser().resolve()
    if not package.exists() or not package.is_dir():
        raise FileNotFoundError(package)
    metadata = read_json(package / "metadata.json")
    linked_images = markdown_image_links(package)
    candidates = []
    skipped = []
    for path in iter_candidates(package):
        suffix = path.suffix.lower()
        if suffix in HTML_EXTS and not args.include_html:
            skipped.append({"path": path.relative_to(package).as_posix(), "reason": "html excluded; pass --include-html"})
            continue
        if suffix in PDF_EXTS and not args.include_pdf:
            skipped.append({"path": path.relative_to(package).as_posix(), "reason": "pdf excluded; pass --include-pdf"})
            continue
        stat = path.stat()
        candidates.append(
            {
                "path": path.relative_to(package).as_posix(),
                "absolutePath": str(path),
                "contentType": mimetypes.guess_type(str(path))[0] or "application/octet-stream",
                "size": stat.st_size,
                "sha256": sha256(path),
                "reasons": candidate_reason(path, package, linked_images),
                "recommendedProcessing": {
                    "mode": "visual-tile",
                    "tileSize": args.tile_size,
                    "overlap": args.overlap,
                },
            }
        )
    manifest = {
        "schemaVersion": 1,
        "kind": "praxis-document-export.pixelrag-handoff",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "packagePath": str(package),
        "source": {
            "title": metadata.get("title") or package.name,
            "sourceUrl": metadata.get("sourceUrl") or metadata.get("finalUrl"),
            "sourcePath": metadata.get("sourcePath"),
            "docId": metadata.get("docId"),
        },
        "canonicalFiles": {
            "markdown": "document.md" if (package / "document.md").exists() else None,
            "readableHtml": "readable.html" if (package / "readable.html").exists() else None,
            "metadata": "metadata.json" if (package / "metadata.json").exists() else None,
        },
        "indexingPolicy": {
            "defaultUse": "Only run PixelRAG when visual layout, diagrams, tables, charts, UI screenshots, scanned pages, or slides matter.",
            "tileSize": args.tile_size,
            "overlap": args.overlap,
            "preserveCanonicalPackage": True,
        },
        "candidates": candidates,
        "skipped": skipped,
        "nextSteps": [
            "Install or provide a PixelRAG-compatible visual indexer separately.",
            "Render each candidate to pages or tiles according to recommendedProcessing.",
            "Store generated tiles/index next to this manifest or in a separate visual index store.",
            "Keep references back to packagePath and candidate.path for provenance.",
        ],
    }
    out = (args.out or package / "pixelrag-manifest.json").expanduser().resolve()
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "candidates": len(candidates), "skipped": len(skipped)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
