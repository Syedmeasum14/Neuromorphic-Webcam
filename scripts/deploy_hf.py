#!/usr/bin/env python3
"""Publish the page to a Hugging Face static Space.

Rebuilds index.html from src/app.html, then pushes it plus a Space-flavoured
README (Hugging Face reads its configuration from README front matter, which
is why the Space gets its own copy rather than the repo's).

Log in first -- the token is yours to enter, not this script's to store:

    .venv/bin/hf auth login

Then:

    .venv/bin/python scripts/deploy_hf.py
"""

import sys
from pathlib import Path

from huggingface_hub import HfApi

import build

SPACE_NAME = "neuromorphic-webcam"
ROOT = Path(__file__).resolve().parent.parent

SPACE_README = """---
title: Neuromorphic Webcam
emoji: 👁️
colorFrom: gray
colorTo: yellow
sdk: static
app_file: index.html
pinned: false
short_description: See what an event camera sees, live in your browser
---

# Neuromorphic Webcam

A normal camera samples every pixel on a clock and ships the whole frame,
whether or not anything happened. An **event camera** gives each pixel its own
trigger: report only when the light it sees changes, and stay silent otherwise.

This Space runs that pixel model live. Left panel: the frame. Right panel:
everything the sensor would actually have transmitted. Turn on your camera and
hold still — you disappear.

**For camera access, open the direct Space URL** ({direct}) rather than viewing
it embedded, since embedded frames withhold camera permission.

Built with no dependencies and no build step: one HTML file, and the sensor
model runs entirely in your browser. No video is uploaded anywhere.
"""


def main() -> None:
    build.main()

    api = HfApi()
    try:
        user = api.whoami()["name"]
    except Exception as exc:                       # noqa: BLE001 - report and stop
        sys.exit(
            "Not logged in to Hugging Face (%s).\n"
            "Run:  .venv/bin/hf auth login" % type(exc).__name__
        )

    repo_id = f"{user}/{SPACE_NAME}"
    direct = f"https://{user.lower()}-{SPACE_NAME}.static.hf.space"

    api.create_repo(repo_id, repo_type="space", space_sdk="static", exist_ok=True)

    api.upload_file(
        path_or_fileobj=str(ROOT / "index.html"),
        path_in_repo="index.html",
        repo_id=repo_id,
        repo_type="space",
        commit_message="Update the event camera page",
    )
    api.upload_file(
        path_or_fileobj=SPACE_README.format(direct=direct).encode("utf-8"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="space",
        commit_message="Update Space description",
    )

    print("\nSpace:  https://huggingface.co/spaces/" + repo_id)
    print("Direct: " + direct + "   <- share this one; the camera works here")


if __name__ == "__main__":
    main()
