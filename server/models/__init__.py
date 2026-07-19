"""Public Trello data models used by tools and services."""

from typing import Any, Dict, Optional

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


class TrelloComment(BaseModel):
    id: str
    author_id: str
    date: str
    text: str


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
    idMembers: list[str] = []
    dueComplete: bool = False
    cover: Dict[str, Any] | None = None
    subscribed: bool = False
    attachments: list[Dict[str, Any]] = []
    comments: list[TrelloComment] = []


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
    "TrelloComment",
    "TrelloCustomField",
    "TrelloCustomFieldItem",
    "TrelloCustomFieldOption",
    "TrelloLabel",
    "TrelloList",
    "TrelloMember",
    "TrelloOrganization",
    "TrelloWebhook",
]
