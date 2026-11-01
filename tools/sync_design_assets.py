"""Copy the design system's stylesheets into the site, where Papyrus publishes them.

Papyrus publishes only `web/css/site-theme.css` and everything under `web/assets/`, so the design system's generated
`tokens.css` and its `components/bundle.css` are copied to `web/assets/mom-tokens.css` and `web/assets/mom-components.css`.
Edit the design system, run `python3 tools/build_tokens_css.py` and then this tool; never edit the copies.

    python3 tools/sync_design_assets.py           write the copies
    python3 tools/sync_design_assets.py --check   exit 1 when a copy differs (CI)
"""

from __future__ import annotations

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
COPIES = (
    (REPOSITORY_ROOT / "design" / "system" / "tokens.css", REPOSITORY_ROOT / "web" / "assets" / "mom-tokens.css"),
    (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css", REPOSITORY_ROOT / "web" / "assets" / "mom-components.css"),
)


def stale_copies() -> list[Path]:
    return [target for source, target in COPIES if not target.is_file() or target.read_bytes() != source.read_bytes()]


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        stale = stale_copies()
        for target in stale:
            print(f"{target.relative_to(REPOSITORY_ROOT)} is out of date; run python3 tools/sync_design_assets.py")
        raise SystemExit(1 if stale else 0)
    for source, target in COPIES:
        target.write_bytes(source.read_bytes())
        print(f"wrote {target.relative_to(REPOSITORY_ROOT)}")
