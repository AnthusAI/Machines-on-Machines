"""Preview this checkout of the site on the real production content, on your network.

    python3 tools/preview_production.py                      # render and serve on 0.0.0.0:5492
    python3 tools/preview_production.py --papyrus-src ~/Projects/Papyrus/src   # also try a Papyrus branch

What it does, in order:
  1. Reads the published stories from the production backend through your signed-in session (read only).
  2. Reads the editors' private star ratings (one read-only DynamoDB get) and keeps them in memory, so the order on the pages is the order production has.
  3. Renders every page from this checkout's `web/` (hooks, components, stylesheet, ads) into a local folder. Nothing is uploaded, saved or purged.
  4. Serves that folder, and fetches anything the render does not write (pictures, renditions, fonts) from the public site.

It never writes to production: the page writer is a local directory, the star store is memory, and the only calls to AWS are reads.
"""

from __future__ import annotations

import argparse
import http.server
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
SITE = "newsroom.machines-on-machines.anth.us"
PUBLIC_ORIGIN = "https://machines-on-machines.anth.us"
AWS_PROFILE = "papyrus-production"
SITE_BUCKET = "amplify-d260vp72hqglnc-main-bra-sitebucket397a1860-ohsbrwmezxev"
LOCK_TABLE = "papyrus-projection-locks"
STARS_KEY = "story-stars#fc970377"


def read_star_ratings() -> dict[str, int]:
    import boto3

    table = boto3.Session(profile_name=AWS_PROFILE, region_name="us-east-1").client("dynamodb")
    item = table.get_item(TableName=LOCK_TABLE, Key={"publication": {"S": STARS_KEY}}).get("Item", {})
    return {lineage: int(value["N"]) for lineage, value in item.get("stars", {}).get("M", {}).items()}


def copy_home_page_snapshot(output_directory: Path) -> None:
    """Read-only: copy the site's published `_data/home-page/` files (the References, the conversations) into the local render folder, so the preview draws Findings,
    Worth Watching and the conversation rail from the same data production does. Nothing is written to the bucket."""
    import boto3

    client = boto3.Session(profile_name=AWS_PROFILE, region_name="us-east-1").client("s3")
    prefix = "_data/home-page/"
    count = 0
    for page in client.get_paginator("list_objects_v2").paginate(Bucket=SITE_BUCKET, Prefix=prefix):
        for entry in page.get("Contents", []):
            target = output_directory / entry["Key"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(client.get_object(Bucket=SITE_BUCKET, Key=entry["Key"])["Body"].read())
            count += 1
    print(f"copied {count} home-page data files from the bucket (read only)")

def add_demo_links() -> None:
    """Preview only: link the newest published Story to the next few as `see_also` (in memory, on top of what the backend holds) so the rail, See also and Posts can be seen
    before anyone has written such links. Nothing is saved anywhere."""
    from papyrus_content.projection import source
    from papyrus_content.projection.site_relations import SiteRelations

    original = source.read_site_relations

    def with_demo(client, stories, page_slugs):
        stories = list(stories)
        found = original(client, stories, page_slugs)
        ids = [item_id for item_id, lineage, _ in stories if lineage]
        if len(ids) < 8:
            return found
        related = {key: list(value) for key, value in found.related.items()}
        for other in ids[1:8]:
            related.setdefault(ids[0], []).append(other)
            related.setdefault(other, []).append(ids[0])
        return SiteRelations(based_on=found.based_on, concepts=found.concepts, related={key: tuple(dict.fromkeys(value)) for key, value in related.items()})

    source.read_site_relations = with_demo
    print("demo links on: the newest Story is see_also-linked to the next seven (preview only, in memory)")


def add_demo_references(path: str) -> None:
    """Preview only: give the stories named in this JSON file (keyed by their address, each a list of Reference mappings) a `related_references` list, in memory, until Papyrus supplies the real one."""
    import json as _json
    from papyrus_content.projection.standard import projector as standard_projector

    demo = _json.loads(Path(path).read_text())
    original = standard_projector.StandardMarkusProjector._page

    def with_demo(self, kind, *args, **kwargs):
        page = original(self, kind, *args, **kwargs)
        entry = kwargs.get("entry")
        found = demo.get(getattr(entry, "url", None) or "") if entry is not None else None
        if found:
            object.__setattr__(page, "related_references", tuple(found))
        return page

    standard_projector.StandardMarkusProjector._page = with_demo
    print(f"demo related references on for {len(demo)} stories (preview only, in memory)")


def render(output_directory: Path) -> None:
    from papyrus_content import project_commands as commands
    from papyrus_content.projection.engine import project_all
    from papyrus_content.projection.story_stars import MemoryStarStore

    from papyrus_content import site_selection

    site_selection.install()
    os.environ["PAPYRUS_SITE"] = SITE
    os.environ.setdefault("AWS_PROFILE", AWS_PROFILE)
    stars = read_star_ratings()
    client, _claims = commands.create_authoring_client()
    context = commands._build_context(client, {"static-dir": str(REPOSITORY_ROOT / "web"), "bucket": SITE_BUCKET, "out": str(output_directory)})
    context.source.star_store = MemoryStarStore(stars)
    report = project_all(context)
    written = report.to_dict()["written"]
    print(f"rendered {written} pages from production content, with {len(stars)} star ratings; errors: {len(report.errors)}")
    for error in report.errors[:5]:
        print("error:", error)


def serve(directory: Path, port: int) -> None:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def do_GET(self):
            path = self.translate_path(self.path)
            if os.path.isdir(path):
                path = os.path.join(path, "index.html")
            if os.path.exists(path):
                return super().do_GET()
            try:
                request = urllib.request.Request(PUBLIC_ORIGIN + self.path, headers={"User-Agent": "mom-local-preview"})
                with urllib.request.urlopen(request, timeout=20) as response:
                    body = response.read()
                    self.send_response(response.status)
                    self.send_header("Content-Type", response.headers.get("Content-Type") or mimetypes.guess_type(self.path)[0] or "application/octet-stream")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
            except urllib.error.HTTPError as error:
                self.send_error(error.code)
            except Exception:
                self.send_error(502)

        def log_message(self, *args):
            pass

    print(f"serving {directory} at http://0.0.0.0:{port}/  (open it from another machine at this computer's network address)")
    http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=5492)
    parser.add_argument("--out", default="/tmp/mom-preview-out")
    parser.add_argument("--papyrus-src", help="a Papyrus checkout's src/ folder, to preview a Papyrus branch with this site")
    parser.add_argument("--demo-links", action="store_true", help="preview only: add in-memory see_also links around the newest Story so the article rail can be seen")
    parser.add_argument("--demo-references", help="preview only: a JSON file {story address: [reference mappings]} to show as related References")
    parser.add_argument("--no-render", action="store_true", help="serve the last render without rendering again")
    arguments = parser.parse_args()
    if arguments.papyrus_src:
        sys.path.insert(0, str(Path(arguments.papyrus_src).expanduser()))
    output_directory = Path(arguments.out)
    if arguments.demo_links:
        add_demo_links()
    if arguments.demo_references:
        add_demo_references(arguments.demo_references)
    if not arguments.no_render:
        output_directory.mkdir(parents=True, exist_ok=True)
        copy_home_page_snapshot(output_directory)
        render(output_directory)
    serve(output_directory, arguments.port)


if __name__ == "__main__":
    main()
