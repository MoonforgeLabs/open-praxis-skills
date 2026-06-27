#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
PLACEHOLDER_MARKERS = ("<diagram", "<whiteboard", "<image", "<mindnote")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Attach visual exports/screenshots to an existing document export package.")
    parser.add_argument("package", type=Path, help="Export package directory containing document.md")
    parser.add_argument("visuals", type=Path, help="Image file or directory of screenshots/visual exports")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--section-title", default="视觉资产 / 架构图补采集")
    parser.add_argument("--replace-placeholders", action="store_true", help="Insert image links after diagram/whiteboard placeholders")
    return parser.parse_args()


def iter_images(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in IMAGE_EXTS else []
    pattern = "**/*" if recursive else "*"
    return sorted(item for item in path.glob(pattern) if item.is_file() and item.suffix.lower() in IMAGE_EXTS)


def load_metadata(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def main() -> int:
    args = parse_args()
    package = args.package.expanduser().resolve()
    doc = package / "document.md"
    if not doc.exists():
        raise FileNotFoundError(doc)
    visuals = iter_images(args.visuals.expanduser().resolve(), args.recursive)
    if not visuals:
        raise SystemExit("No image visuals found")
    assets_dir = package / "assets" / "visuals"
    assets_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for index, source in enumerate(visuals, 1):
        target = assets_dir / f"visual-{index:03d}{source.suffix.lower()}"
        shutil.copy2(source, target)
        rel = target.relative_to(package).as_posix()
        copied.append({"source": str(source), "path": rel})

    text = doc.read_text(encoding="utf-8")
    if args.replace_placeholders:
        lines = text.splitlines()
        output = []
        visual_index = 0
        for line in lines:
            output.append(line)
            if visual_index < len(copied) and any(marker in line for marker in PLACEHOLDER_MARKERS):
                item = copied[visual_index]
                output.append("")
                output.append(f"![visual-{visual_index + 1:03d}]({item['path']})")
                output.append("")
                visual_index += 1
        if visual_index < len(copied):
            output.append("")
            output.append(f"## {args.section_title}")
            output.append("")
            for index, item in enumerate(copied[visual_index:], visual_index + 1):
                output.append(f"![visual-{index:03d}]({item['path']})")
                output.append("")
        text = "\n".join(output).rstrip() + "\n"
    else:
        append = ["", f"## {args.section_title}", ""]
        for index, item in enumerate(copied, 1):
            append.append(f"![visual-{index:03d}]({item['path']})")
            append.append("")
        text = text.rstrip() + "\n" + "\n".join(append).rstrip() + "\n"
    doc.write_text(text, encoding="utf-8")

    metadata_path = package / "metadata.json"
    metadata = load_metadata(metadata_path)
    metadata.setdefault("visualAssets", [])
    metadata["visualAssets"].extend(copied)
    metadata["visualAssetsAttachedAt"] = datetime.now(timezone.utc).isoformat()
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "package": str(package), "attached": len(copied)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
