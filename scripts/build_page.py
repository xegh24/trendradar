#!/usr/bin/env python3
"""Build index.html from src/page.html.

src/page.html is the body-level page (the shape the claude.ai Artifact
publisher expects). index.html wraps it into a complete HTML document for
GitHub Pages or any static host.

Usage: python3 scripts/build_page.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "page.html"
OUT = ROOT / "index.html"

HEAD = """<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font-size:14px;font-family:system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
"""


def main() -> None:
    page = SRC.read_text(encoding="utf-8")
    # Head-level tags (title, meta, link, style) go into <head>; the rest into <body>.
    cut = page.index("</style>") + len("</style>")
    head_part, body_part = page[:cut], page[cut:]
    doc = f"{HEAD}{head_part}\n</head>\n<body>\n{body_part.strip()}\n</body>\n</html>\n"
    OUT.write_text(doc, encoding="utf-8")
    print(f"index.html: {len(doc) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
