import json
from pathlib import Path
from urllib.parse import quote

import httpx
from pydantic import Field
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import __version__
from .ingest import MAX_FILE_BYTES, fetch_page, parse_file
from .integration import config
from .models import Bundle, CorrectionInput, InputModel, ItemInput, SearchInput, UsageInput
from .store import RevisionConflict, Store

ROOT = Path(__file__).parent


class WebImport(InputModel):
    url: str
    title: str = ""
    intent: str = ""
    project: str = ""
    role: str = "reference"
    tags: list[str] = Field(default_factory=list)


class ArchiveInput(InputModel):
    archived: bool


def create_app(home: Path | str | None = None) -> FastAPI:
    store = Store(home)
    app = FastAPI(title="Aftermark", version=__version__)
    app.state.store = store
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"])

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        # Protect the local write API from a page opened on a different origin.
        origin = request.headers.get("origin")
        if origin and origin != f"{request.url.scheme}://{request.headers.get('host')}":
            return JSONResponse({"detail": "Cross-origin access is not allowed."}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(KeyError)
    async def missing(_request, error):
        return JSONResponse({"detail": str(error.args[0])}, status_code=404)

    @app.exception_handler(RevisionConflict)
    async def revision_conflict(_request, error):
        return JSONResponse({"detail": str(error), "code": "revision_conflict"}, status_code=409)

    @app.exception_handler(ValueError)
    async def invalid(_request, error):
        return JSONResponse({"detail": str(error)}, status_code=422)

    @app.exception_handler(httpx.HTTPError)
    async def remote_error(_request, error):
        return JSONResponse({"detail": f"Source import failed: {error}. You can save the link or paste text instead."}, status_code=422)

    @app.get("/api/status")
    def status():
        return {"version": __version__, "data_dir": str(store.home.resolve()), "database": str(store.path.resolve()), "storage": "local", "model_required": False}

    @app.get("/api/items")
    def items(q: str = "", project: str | None = None, archived: bool = False):
        records = store.list(q, project, archived)
        return [{**item, "content": item["content"][:280]} for item in records]

    @app.get("/api/projects")
    def projects():
        return store.projects()

    @app.post("/api/items", status_code=201)
    def create(value: ItemInput):
        return store.create(value)

    @app.get("/api/items/{item_id}")
    def get(item_id: str):
        return store.get(item_id)

    @app.put("/api/items/{item_id}")
    def update(item_id: str, value: ItemInput):
        return store.update(item_id, value)

    @app.patch("/api/items/{item_id}/archive")
    def archive(item_id: str, value: ArchiveInput):
        return store.archive(item_id, value.archived)

    @app.post("/api/items/{item_id}/corrections", status_code=201)
    def correct(item_id: str, value: CorrectionInput):
        return store.correct(item_id, value)

    @app.post("/api/items/{item_id}/usage", status_code=201)
    def record(item_id: str, value: UsageInput):
        return store.record(item_id, value)

    @app.get("/api/items/{item_id}/original")
    def original(item_id: str):
        file = store.attachment(item_id)
        return Response(file["data"], media_type=file["media_type"], headers={
            "Content-Disposition": "attachment; filename*=UTF-8''" + quote(file["filename"], safe="")})

    @app.post("/api/import/web", status_code=201)
    def import_web(value: WebImport):
        args = value.model_dump()
        return store.create(fetch_page(**args))

    @app.post("/api/import/file", status_code=201)
    async def import_file(file: UploadFile = File(...), title: str = Form(""), intent: str = Form(""),
                          project: str = Form(""), role: str = Form("reference"), source_url: str = Form(""), tags: list[str] = Form([])):
        data = await file.read(MAX_FILE_BYTES + 1)
        item, attachment = parse_file(file.filename or "", data, title=title, intent=intent,
                                      project=project, role=role, source_url=source_url, tags=tags)
        return store.create(item, attachment)

    @app.post("/api/recall")
    def recall(value: SearchInput):
        return store.recall(value.task, value.project, value.limit)

    @app.get("/api/history")
    def history():
        return store.history()

    @app.get("/api/export")
    def export():
        return Response(json.dumps(store.export(), ensure_ascii=False, indent=2), media_type="application/json",
                        headers={"Content-Disposition": 'attachment; filename="aftermark-backup.json"'})

    @app.post("/api/import/bundle")
    def import_bundle(value: Bundle):
        return store.import_bundle(value)

    @app.post("/api/examples")
    def examples():
        bundle = Bundle.model_validate_json((ROOT / "data/examples.json").read_text(encoding="utf-8"))
        return store.import_bundle(bundle)

    @app.post("/api/diagnostics")
    async def diagnostics():
        from .diagnostics import check_connection
        return await check_connection(store)

    @app.get("/api/integration")
    def integration(project: str | None = None):
        return config(store.home, project)

    @app.get("/")
    def index():
        return FileResponse(ROOT / "static/index.html")

    @app.get("/about")
    def about():
        return FileResponse(ROOT / "static/about.html")

    app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
    return app
