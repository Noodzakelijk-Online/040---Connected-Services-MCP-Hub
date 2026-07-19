"""Public Trello data models used by tools and services."""

from typing import Optional

from pydantic import BaseModel

from .action import TrelloAction
from .attachment import TrelloAttachment
from .custom_field import (
    TrelloCustomField,
    TrelloCustomFieldItem,
    TrelloCustomFieldOption,
)
from .member import TrelloMember
from .webhook import TrelloWebhook


class TrelloBoard(BaseModel):
    id: str
    name: str
    desc: str | None = None
    closed: bool = False
    idOrganization: str | None = None
    url: str


class TrelloList(BaseModel):
    id: str
    name: str
    closed: bool = False
    idBoard: str
    pos: float


class TrelloLabel(BaseModel):
    id: str
    name: str
    color: str | None = None


class TrelloCard(BaseModel):
    id: str
    name: str
    desc: str | None = None
    closed: bool = False
    idList: str
    idBoard: str
    url: str
    pos: float
    labels: list[TrelloLabel] = []
    due: str | None = None


class TrelloOrganization(BaseModel):
    id: str
    name: str
    displayName: str
    desc: Optional[str] = None
    url: str
    idEnterprise: Optional[str] = None
    prefs: Optional[dict] = None
    memberships: Optional[list[str]] = None


__all__ = [
    "TrelloAction",
    "TrelloAttachment",
    "TrelloBoard",
    "TrelloCard",
    "TrelloCustomField",
    "TrelloCustomFieldItem",
    "TrelloCustomFieldOption",
    "TrelloLabel",
    "TrelloList",
    "TrelloMember",
    "TrelloOrganization",
    "TrelloWebhook",
]
