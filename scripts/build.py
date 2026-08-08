#!/usr/bin/env python3
"""Wrap src/app.html into a standalone index.html.

src/app.html is the single source of truth. It is a document fragment -- a
<title>, a <style>, the markup and a <script>, with no <html>/<head>/<body> --
because that is the form the artifact host expects. GitHub Pages wants a
complete document, so this adds the skeleton around it.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "app.html"
OUT = ROOT / "index.html"

SKELETON = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A live event-camera (DVS) pixel model running in the browser on your webcam, a video file, or a synthetic scene.">
{head}
</head>
<body>
{body}
</body>
</html>
"""


def main() -> None:
    source = SRC.read_text(encoding="utf-8")

    # Everything up to and including the </style> belongs in <head>;
    # the markup and script that follow belong in <body>.
    split = source.index("</style>") + len("</style>")
    head, body = source[:split].strip(), source[split:].strip()

    OUT.write_text(SKELETON.format(head=head, body=body), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
