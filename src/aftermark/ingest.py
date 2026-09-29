"""Read source material. No generated summaries and no silent extraction fallback."""

from io import BytesIO
from pathlib import Path
from urllib.parse import unquote, urlsplit

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from . import __version__
from .models import ItemInput

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_WEB_BYTES = 5 * 1024 * 1024


def extract_html(data: bytes, url: str) -> tuple[str, str]:
    soup = BeautifulSoup(data, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else urlsplit(url).hostname
    for node in soup.select("script, style, nav, footer, header, noscript, svg, form"):
        node.decompose()
    main = soup.find("article") or soup.find("main") or soup.body or soup
    text = "\n".join(line.strip() for line in main.get_text("\n").splitlines() if line.strip())
    if not text:
        raise ValueError("This page has no readable text. Paste the content manually; JavaScript-only pages are not rendered.")
    return str(title)[:240], text


def fetch_url(url: str, *, title: str = "", intent: str = "", project: str = "", role: str = "reference",
              tags: list[str] | None = None) -> tuple[ItemInput, tuple[str, str, bytes] | None]:
    """Import declared HTML/text or a text PDF; retain PDF bytes and the requested URL."""
    common = dict(title=title, intent=intent, project=project, role=role, tags=tags or [])
    ItemInput(**{**common, "title": title or url[:240]}, source_url=url)
    with httpx.Client(timeout=20, follow_redirects=True, max_redirects=5) as client:
        with client.stream("GET", url, headers={"User-Agent": f"Aftermark/{__version__} (personal knowledge importer)"}) as response:
            response.raise_for_status()
            mime = response.headers.get("content-type", "").split(";")[0].strip().lower()
            if mime not in {"text/html", "application/xhtml+xml", "text/plain", "text/markdown", "application/pdf"}:
                raise ValueError(f"Unsupported content type: {mime or 'unknown'}. Use an HTML/text page or a text PDF URL.")
            byte_limit = MAX_FILE_BYTES if mime == "application/pdf" else MAX_WEB_BYTES
            chunks = []
            size = 0
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > byte_limit:
                    raise ValueError("PDF exceeds the 20 MB import limit." if mime == "application/pdf" else "Page exceeds the 5 MB import limit.")
                chunks.append(chunk)
            data = b"".join(chunks)
            if mime == "application/pdf":
                name = Path(unquote(response.url.path).replace("\\", "/")).name or "document"
                if not name.lower().endswith(".pdf"):
                    name += ".pdf"
                return parse_file(name, data, source_url=url, **common)
            if mime in {"text/plain", "text/markdown"}:
                page_title, content = title or urlsplit(url).hostname, data.decode(response.encoding or "utf-8")
                if not content.strip():
                    raise ValueError("This URL has no readable text; no bookmark was imported.")
            else:
                page_title, content = extract_html(data, str(response.url))
    return ItemInput(**{**common, "title": title or page_title}, content=content, kind="web", source_url=url), None


def parse_file(filename: str, data: bytes, *, title: str = "", intent: str = "", project: str = "",
               role: str = "reference", source_url: str = "", tags: list[str] | None = None) -> tuple[ItemInput, tuple[str, str, bytes]]:
    name = Path(filename.replace("\\", "/")).name
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("File exceeds the 20 MB import limit.")
    suffix = Path(name).suffix.lower()
    if suffix == ".pdf":
        try:
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted:
                raise ValueError("Unlock the PDF before importing it.")
            pages = [page.extract_text() or "" for page in reader.pages]
        except PdfReadError as error:
            raise ValueError("This file could not be read as a PDF.") from error
        if not any(page.strip() for page in pages):
            raise ValueError("This PDF has no extractable text. OCR is not included; paste a transcription instead.")
        content = "\n\n".join(f"[Page {i}]\n{text}" for i, text in enumerate(pages, 1))
        kind, mime = "pdf", "application/pdf"
    elif suffix in {".txt", ".md", ".srt", ".vtt"}:
        try:
            content = data.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError("Save the text file as UTF-8 before importing.") from error
        kind = "video" if suffix in {".srt", ".vtt"} else "note"
        mime = "text/plain; charset=utf-8"
    else:
        raise ValueError("Supported files: PDF, Markdown, TXT, SRT, and VTT.")
    item = ItemInput(title=title or Path(name).stem, content=content, kind=kind, source_name=name,
                     intent=intent, project=project, role=role, source_url=source_url, tags=tags or [])
    return item, (name, mime, data)
