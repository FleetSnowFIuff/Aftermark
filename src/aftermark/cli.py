import argparse
import json
import sys
from pathlib import Path

import httpx

from . import __version__
from .ingest import fetch_page, parse_file
from .integration import config
from .models import Bundle, CorrectionInput, ItemInput, UsageInput
from .store import Store


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="aftermark", description="Save what works. Bring your knowledge into your agent's next task.")
    root.add_argument("--version", action="version", version=__version__)
    root.add_argument("--data-dir", type=Path, help="Library directory (or AFTERMARK_HOME). All clients must use the same directory.")
    commands = root.add_subparsers(dest="command", required=True)
    serve = commands.add_parser("serve", help="Open the local library in a browser")
    serve.add_argument("--port", type=int, default=43821)
    serve.add_argument("--open", action="store_true", help="Open the browser automatically")
    commands.add_parser("mcp", help="Run the MCP server over stdio")
    commands.add_parser("config", help="Print MCP configuration and suggested host instructions")
    commands.add_parser("status", help="Show version and database location")
    commands.add_parser("examples", help="Import three small, original example bookmarks")
    add = commands.add_parser("add", help="Save a note, URL, or file")
    add.add_argument("--title", default="")
    source = add.add_mutually_exclusive_group(required=True)
    source.add_argument("--text")
    source.add_argument("--url")
    source.add_argument("--file", type=Path)
    add.add_argument("--fetch", action="store_true", help="Extract a URL's text; otherwise save the link only")
    add.add_argument("--kind", choices=["note", "web", "pdf", "video"], default="note")
    add.add_argument("--intent", default="")
    add.add_argument("--project", default="")
    add.add_argument("--role", choices=["reference", "method", "rule"], default="reference")
    add.add_argument("--tag", action="append", default=[])
    listing = commands.add_parser("list")
    listing.add_argument("--query", default="")
    listing.add_argument("--project", default=None)
    listing.add_argument("--archived", action="store_true")
    read = commands.add_parser("show")
    read.add_argument("id")
    recall = commands.add_parser("recall")
    recall.add_argument("task")
    recall.add_argument("--project", default="")
    recall.add_argument("--limit", type=int, choices=range(1, 11), default=5)
    correction = commands.add_parser("correct")
    correction.add_argument("id")
    correction.add_argument("text")
    correction.add_argument("--project", default="")
    record = commands.add_parser("record")
    record.add_argument("id")
    record.add_argument("--task", required=True)
    record.add_argument("--outcome", required=True, choices=["referenced", "applied", "verified", "skipped"])
    record.add_argument("--reason", required=True)
    record.add_argument("--evidence", default="")
    record.add_argument("--project", default="")
    archive = commands.add_parser("archive")
    archive.add_argument("id")
    archive.add_argument("--restore", action="store_true")
    export = commands.add_parser("export")
    export.add_argument("file", type=Path)
    load = commands.add_parser("import")
    load.add_argument("file", type=Path)
    return root


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parser().parse_args()
    try:
        run(args)
    except (ValueError, KeyError, OSError, httpx.HTTPError) as error:
        print(f"aftermark: {error}", file=sys.stderr)
        raise SystemExit(1) from error


def run(args):
    if args.command == "serve":
        import threading
        import webbrowser
        import uvicorn
        from .web import create_app
        if args.open:
            timer = threading.Timer(1.5, webbrowser.open, args=(f"http://127.0.0.1:{args.port}",))
            timer.daemon = True
            timer.start()
        uvicorn.run(create_app(args.data_dir), host="127.0.0.1", port=args.port)
        return
    store = Store(args.data_dir)
    if args.command == "mcp":
        from .mcp_server import create_server
        create_server(store).run()
        return
    if args.command == "config":
        result = config(store.home)
    elif args.command == "status":
        result = {"version": __version__, "data_dir": str(store.home.resolve()), "database": str(store.path.resolve())}
    elif args.command == "examples":
        result = store.import_bundle(Bundle.model_validate_json((Path(__file__).parent / "data/examples.json").read_text(encoding="utf-8")))
    elif args.command == "add":
        common = dict(title=args.title, intent=args.intent, project=args.project, role=args.role)
        if args.file:
            item, attachment = parse_file(args.file.name, args.file.read_bytes(), **common)
            item.tags = args.tag
            result = store.create(item, attachment)
        elif args.url and args.fetch:
            item = fetch_page(args.url, **common)
            item.tags = args.tag
            result = store.create(item)
        else:
            if not args.title:
                raise ValueError("Give the bookmark a --title.")
            kind = "web" if args.url and args.kind == "note" else args.kind
            result = store.create(ItemInput(**common, content=args.text or "", source_url=args.url or "", kind=kind, tags=args.tag))
    elif args.command == "list":
        result = store.list(args.query, args.project, args.archived)
    elif args.command == "show":
        result = store.get(args.id)
    elif args.command == "recall":
        result = store.recall(args.task, args.project, args.limit)
    elif args.command == "correct":
        result = store.correct(args.id, CorrectionInput(text=args.text, project=args.project))
    elif args.command == "record":
        result = store.record(args.id, UsageInput(task=args.task, outcome=args.outcome, reason=args.reason, evidence=args.evidence, project=args.project))
    elif args.command == "archive":
        result = store.archive(args.id, not args.restore)
    elif args.command == "export":
        args.file.write_text(json.dumps(store.export(), ensure_ascii=False, indent=2), encoding="utf-8")
        result = {"exported": str(args.file)}
    elif args.command == "import":
        result = store.import_bundle(Bundle.model_validate_json(args.file.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, indent=2))
