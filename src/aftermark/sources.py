"""Locations derived from saved PDF markers and subtitle timing lines."""
import re

PAGE = re.compile(r"^\[Page ([1-9]\d*)\][ \t]*\r?$", re.MULTILINE)
TIME = r"(?:\d{2,}:)?[0-5]\d:[0-5]\d[.,]\d{3}"
CUE = re.compile(rf"^(?P<start>{TIME})[ \t]+-->[ \t]+(?P<end>{TIME})(?:[ \t]+[^\r\n]*)?\r?$", re.MULTILINE)


def seconds(value: str) -> float:
    parts = value.replace(",", ".").split(":")
    return sum(float(part) * 60 ** i for i, part in enumerate(reversed(parts)))


def citation(item: dict, label: str) -> str:
    return f"{item['title']} — {label} (Aftermark {item['id']}, v{item['revision']})"


def locations(item: dict) -> list[dict]:
    text = item["content"]
    result = []
    if item["kind"] == "pdf":
        markers = list(PAGE.finditer(text))
        for i, match in enumerate(markers):
            page = int(match[1])
            result.append({"id": f"page-{i + 1}", "kind": "page", "label": f"Page {page}", "page": page,
                           "start": match.start(), "end": markers[i + 1].start() if i + 1 < len(markers) else len(text)})
    elif item["kind"] == "video":
        for match in CUE.finditer(text):
            start, end = seconds(match["start"]), seconds(match["end"])
            if end <= start:
                continue
            boundary = re.search(r"\r?\n[ \t]*\r?\n", text[match.end():])
            stop = match.end() + boundary.start() if boundary else len(text)
            result.append({"id": f"cue-{len(result) + 1}", "kind": "timestamp",
                           "label": match["start"].replace(",", ".") + " → " + match["end"].replace(",", "."),
                           "start_seconds": start, "end_seconds": end, "start": match.start(), "end": stop})
    for location in result:
        location["citation"] = citation(item, location["label"])
    return result


def read_source(item: dict, offset: int = 0, limit: int = 12000,
                anchor: str = "", expected_revision: int | None = None) -> dict:
    if offset < 0 or not 1 <= limit <= 20000:
        raise ValueError("offset must be non-negative; limit must be 1..20000.")
    if expected_revision is not None and expected_revision != item["revision"]:
        raise ValueError("This bookmark changed. Recall it again before reading or citing an old location.")
    text = item["content"]
    markers = locations(item)
    start, end = 0, len(text)
    selected = None
    if anchor:
        selected = next((m for m in markers if m["id"] == anchor), None)
        if selected is None:
            raise ValueError("Source location not found. Read or recall this bookmark to discover current locations.")
        start, end = selected["start"], selected["end"]
    begin = min(start + offset, end)
    stop = min(begin + limit, end)
    visible = [m for m in markers if m["start"] < stop and m["end"] > begin]
    label = selected["label"] if selected else f"characters {begin}:{stop}"
    return {"content": text[begin:stop], "total_chars": len(text), "source_offset": begin,
            "anchor": anchor, "next_offset": offset + limit if stop < end else None,
            "locations": visible[:50], "location_count": len(markers),
            "citation": citation(item, label)}
