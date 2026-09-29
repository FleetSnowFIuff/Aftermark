"""Locations derived from saved PDF markers and subtitle timing lines."""
import re
from collections import Counter
from heapq import merge

PAGE = re.compile(r"^\[Page ([1-9]\d*)\][ \t]*\r?$", re.MULTILINE)
TIME = r"(?:\d{2,}:)?[0-5]\d:[0-5]\d[.,]\d{3}"
CUE = re.compile(rf"^(?P<start>{TIME})[ \t]+-->[ \t]+(?P<end>{TIME})(?:[ \t]+[^\r\n]*)?\r?$", re.MULTILINE)


def task_excerpt(text: str, query_terms: list[str], limit: int = 1200) -> dict:
    """Score keyword-anchored windows by distinct coverage, earliest on ties."""
    wanted = set(query_terms)
    lowered = text.lower()
    # Some Unicode lowercase mappings expand; returned offsets must still address the source.
    offsets = None
    if len(lowered) != len(text):
        offsets = [i for i, char in enumerate(text) for _ in char.lower()] + [len(text)]
    hits = []
    for word in re.finditer(r"[a-z0-9_]+|[\u3400-\u9fff]+", lowered):
        token = word.group()
        pieces = ((i, token[i:i + 2]) for i in range(max(1, len(token) - 1))) if "\u3400" <= token[0] <= "\u9fff" else [(0, token)]
        for relative, term in pieces:
            if term in wanted:
                begin, end = word.start() + relative, word.start() + relative + len(term)
                if offsets is not None:
                    begin, end = offsets[begin], offsets[end - 1] + 1
                hits.append((begin, end, term))
    best_start, best_terms = 0, set()
    counts = Counter()
    left = right = 0
    # Both edges move forward: repeated keywords do not increase the coverage score.
    starts = merge((max(0, position - 160) for position, _, _ in hits),
                   (position for position, _, _ in hits))
    for start in starts:
        while right < len(hits) and hits[right][1] <= start + limit:
            counts[hits[right][2]] += 1
            right += 1
        while left < right and hits[left][0] < start:
            term = hits[left][2]
            counts[term] -= 1
            if not counts[term]:
                del counts[term]
            left += 1
        if len(counts) > len(best_terms):
            best_start, best_terms = start, set(counts)
    return {"excerpt": text[best_start:best_start + limit], "excerpt_start": best_start,
            "excerpt_matched_terms": [term for term in query_terms if term in best_terms]}


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
