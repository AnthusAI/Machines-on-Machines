"""Draw the default share picture of each language: the wordmark in white capitals with the middle word in a cream seal, on navy, 1200x630.

The picture is made from the same words and the same stylesheet as the site's wordmark (`web/strings/<tag>.json` `brand.lead` and `brand.on`,
`design/system/tokens.css` and `components/bundle.css`), so a language's lockup cannot drift from the site's. Headless Chrome draws it; the result is
`web/assets/share/mom-share-default[-<prefix>].png`, which each language's `seo.defaultImage` string names. Generated images carry no credit.

    python3 tools/build_share_images.py            write the pictures
"""

from __future__ import annotations

import html
import json
import subprocess
import tempfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SHARE_DIRECTORY = REPOSITORY_ROOT / "web" / "assets" / "share"
# language tag: (file name, wordmark size in px); the size fits the lockup across the picture
# the English picture (mom-share-default.png) is the original and is not redrawn
PICTURES = {"es-419": ("mom-share-default-es.png", 94), "zh-Hans": ("mom-share-default-zh.png", 170)}


def page_for(tag: str, size: int) -> str:
    strings = json.loads((REPOSITORY_ROOT / "web" / "strings" / f"{tag}.json").read_text(encoding="utf-8"))
    lead, middle = html.escape(strings["brand.lead"]), html.escape(strings["brand.on"])
    wide = " mom-wordmark-on-wide" if len(strings["brand.on"]) > 2 else ""
    tokens = (REPOSITORY_ROOT / "design" / "system" / "tokens.css").read_text(encoding="utf-8")
    components = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text(encoding="utf-8")
    chinese = ":root{--font-display: Anton, 'PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC', sans-serif}.mom-wordmark,.mom-wordmark>span{font-weight:900;text-transform:none;letter-spacing:0}" if tag == "zh-Hans" else ""
    return (
        f'<!doctype html><html lang="{tag}"><head><meta charset="utf-8">'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&display=block">'
        f"<style>{tokens}\n{components}\n{chinese}"
        "html,body{margin:0;width:1200px;height:630px;background:var(--brand-light, #1f2a44);}"
        "body{display:grid;place-items:center;color:var(--on-brand-light, #f6f7f9)}"
        f".mom-wordmark{{font-size:{size}px;color:#f6f7f9}}.mom-wordmark-on{{background:#e7e1d4;color:#12161c}}</style></head>"
        f'<body><div class="mom-wordmark mom-wordmark-inline"><span>{lead}</span><span class="mom-wordmark-on{wide}">{middle}</span><span>{lead}</span></div></body></html>'
    )


def main() -> None:
    SHARE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for tag, (name, size) in PICTURES.items():
        with tempfile.TemporaryDirectory() as work:
            page = Path(work) / "share.html"
            page.write_text(page_for(tag, size), encoding="utf-8")
            subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=1", "--window-size=1200,630", "--virtual-time-budget=8000",
                            f"--screenshot={SHARE_DIRECTORY / name}", page.as_uri()], check=True, capture_output=True)
        print("wrote", SHARE_DIRECTORY / name)


if __name__ == "__main__":
    main()
