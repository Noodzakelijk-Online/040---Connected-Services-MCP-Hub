"""Regression tests for Freshdesk transport, search fallback, and update handling."""

import asyncio
import os
import sys
from pathlib import Path

import requests

os.environ["FRESHDESK_DOMAIN"] = "example.freshdesk.com"
os.environ["FRESHDESK_API_KEY"] = "test_key"
sys.path.insert(0, str(Path(__file__).parent))

import main as freshdesk


class FakeResponse:
    def __init__(self, status_code, payload=None, headers=None):
        self.status_code = status_code
        self.payload = payload
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError(f"HTTP {self.status_code}")
            error.response = self
            raise error

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def test_normalize_domain_accepts_hosts_and_rejects_url_paths():
    assert freshdesk.normalize_domain("https://Example.Freshdesk.com/") == "example.freshdesk.com"
    assert freshdesk.normalize_domain("example.freshdesk.com") == "example.freshdesk.com"
    try:
        freshdesk.normalize_domain("https://example.freshdesk.com/api/v2")
    except ValueError:
        pass
    else:
        raise AssertionError("domains with paths must be rejected")


def test_safe_request_retries_rate_limits_and_handles_empty_success(monkeypatch):
    responses = [
        FakeResponse(429, headers={"Retry-After": "1"}),
        FakeResponse(204),
    ]
    calls = []
    monkeypatch.setattr(
        freshdesk.requests,
        "request",
        lambda *args, **kwargs: (calls.append((args, kwargs)) or responses.pop(0)),
    )
    monkeypatch.setattr(freshdesk.time, "sleep", lambda _seconds: None)

    assert freshdesk.safe_request("GET", "tickets") == {}
    assert len(calls) == 2


def test_search_fallback_is_paginated_but_auth_errors_do_not_trigger_it(monkeypatch):
    async def exercise():
        calls = []

        async def fallback_get(endpoint, params=None):
            calls.append((endpoint, params))
            if endpoint == "search/tickets":
                return {"error": "search unavailable", "status_code": 403}
            return [{"id": 7, "subject": "Roadmap", "description_text": "Plan work"}]

        monkeypatch.setattr(freshdesk, "fd_get", fallback_get)
        assert (await freshdesk.search("road"))["results"][0]["id"] == 7
        assert calls[1] == ("tickets", {"page": 1, "per_page": 100})

        async def auth_error_get(endpoint, params=None):
            calls.append((endpoint, params))
            return {"error": "Freshdesk request failed", "status_code": 401}

        calls.clear()
        monkeypatch.setattr(freshdesk, "fd_get", auth_error_get)
        assert (await freshdesk.search("road"))["status_code"] == 401
        assert len(calls) == 1

    asyncio.run(exercise())


def test_update_ticket_accepts_an_empty_description_and_rejects_empty_updates(monkeypatch):
    async def exercise():
        calls = []

        async def put(endpoint, data):
            calls.append((endpoint, data))
            return {"id": 7}

        monkeypatch.setattr(freshdesk, "fd_put", put)
        assert (await freshdesk.update_ticket(7))["error"]
        assert await freshdesk.update_ticket(7, description="") == {"id": 7}
        assert calls == [("tickets/7", {"description": ""})]

    asyncio.run(exercise())
