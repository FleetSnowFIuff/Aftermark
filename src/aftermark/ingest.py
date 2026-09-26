"""Read source material. No generated summaries and no silent extraction fallback."""

from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader
from pypdf.errors import PdfReadError

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
        raise ValueError("This page has no readable text. Paste the content manually; JavaScript-only pages are not rendered in v0.1.")
    return str(title)[:240], text


def fetch_page(url: str, *, title: str = "", intent: str = "", project: str = "", role: str = "reference") -> ItemInput:
    # Validate the input at the network boundary; imported pages remain data.
    ItemInput(title=title or url[:240], source_url=url)
    with httpx.Client(timeout=20, follow_redirects=True, max_redirects=5) as client:
        with client.stream("GET", url, headers={"User-Agent": "Aftermark/0.1 (personal knowledge importer)"}) as response:
            response.raise_for_status()
            mime = response.headers.get("content-type", "").split(";")[0].lower()
            if mime not in {"text/html", "application/xhtml+xml", "text/plain", "text/markdown"}:
                raise ValueError(f"Unsupported web content type: {mime or 'unknown'}. Upload PDF files directly.")
            chunks = []
            size = 0
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > MAX_WEB_BYTES:
                    raise ValueError("Page exceeds the 5 MB import limit.")
                chunks.append(chunk)
            data = b"".join(chunks)
            if mime in {"text/plain", "text/markdown"}:
                page_title, content = title or urlsplit(url).hostname, data.decode(response.encoding or "utf-8")
            else:
                page_title, content = extract_html(data, str(response.url))
    return ItemInput(title=title or page_title, content=content, kind="web", source_url=url,
                     intent=intent, project=project, role=role)


def parse_file(filename: str, data: bytes, *, title: str = "", intent: str = "", project: str = "",
               role: str = "reference", source_url: str = "") -> tuple[ItemInput, tuple[str, str, bytes]]:
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
            raise ValueError("This PDF has no extractable text. OCR is not included in v0.1; paste a transcription instead.")
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
                     intent=intent, project=project, role=role, source_url=source_url)
    return item, (name, mime, data)
