from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def new_id() -> str:
    return str(uuid4())


Kind = Literal["note", "web", "pdf", "video"]
Role = Literal["reference", "method", "rule"]
Outcome = Literal["referenced", "applied", "verified", "skipped"]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class IntegrationInput(InputModel):
    project: str | None = Field(default=None, max_length=160)


class ItemInput(InputModel):
    title: str = Field(min_length=1, max_length=240)
    kind: Kind = "note"
    content: str = Field(default="", max_length=500_000)
    intent: str = Field(default="", max_length=4000)
    project: str = Field(default="", max_length=160)
    role: Role = "reference"
    source_url: str = Field(default="", max_length=4000)
    source_name: str = Field(default="", max_length=255)
    tags: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("source_url")
    @classmethod
    def http_url(cls, value: str) -> str:
        if value:
            from urllib.parse import urlsplit

            url = urlsplit(value)
            if url.scheme not in {"http", "https"} or not url.hostname or url.username:
                raise ValueError("Use an http(s) URL without embedded credentials.")
        return value

    @field_validator("tags")
    @classmethod
    def tidy_tags(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(tag.strip()[:60] for tag in values if tag.strip()))

    @model_validator(mode="after")
    def has_material(self):
        if not self.content and not self.source_url:
            raise ValueError("Add some text or a source URL.")
        if self.role != "reference" and not self.intent:
            raise ValueError("A method or rule needs your intent, not just a source.")
        return self


class Item(ItemInput):
    id: str
    revision: int = Field(ge=1)
    archived: bool = False
    created_at: str
    updated_at: str


class CorrectionInput(InputModel):
    text: str = Field(min_length=1, max_length=4000)
    project: str = Field(default="", max_length=160)


class Correction(CorrectionInput):
    id: str
    item_id: str
    created_at: str


class UsageFields(InputModel):
    task: str = Field(min_length=1, max_length=4000)
    project: str = Field(default="", max_length=160)
    outcome: Outcome
    reason: str = Field(min_length=1, max_length=4000)
    evidence: str = Field(default="", max_length=8000)

    @model_validator(mode="after")
    def verification_has_evidence(self):
        if self.outcome in {"applied", "verified"} and not self.evidence:
            raise ValueError("Applied/verified records need a change, file, or test reference.")
        return self


class UsageInput(UsageFields):
    expected_revision: int = Field(ge=1)


class Usage(UsageFields):
    id: str
    item_id: str
    item_revision: int = Field(ge=1)
    created_at: str


class Attachment(InputModel):
    item_id: str
    filename: str
    media_type: str
    base64: str


class Bundle(InputModel):
    format: Literal["aftermark"] = "aftermark"
    version: Literal[1] = 1
    items: list[Item]
    corrections: list[Correction] = Field(default_factory=list)
    usage: list[Usage] = Field(default_factory=list)
    attachments: list[Attachment] = Field(default_factory=list)


class SearchInput(InputModel):
    task: str = Field(min_length=1, max_length=4000)
    project: str = Field(default="", max_length=160)
    limit: int = Field(default=5, ge=1, le=10)
