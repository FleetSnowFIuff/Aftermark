"""Synchronize the standalone introduction and the packaged app page."""
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--check", action="store_true", help="Fail if the two pages differ; do not write files")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = root / "website" / "Aftermark-介绍页.html"
target = root / "src/aftermark/static/about.html"
if args.check:
    if target.read_bytes() != source.read_bytes():
        raise SystemExit("Introduction differs. Run: python scripts/sync_site.py")
    print("Introduction pages match.")
else:
    target.write_bytes(source.read_bytes())
    print("Synced standalone introduction to the local app.")
