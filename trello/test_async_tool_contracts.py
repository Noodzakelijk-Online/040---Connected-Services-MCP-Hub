"""Regression coverage for asynchronous Trello service and tool contracts."""

import asyncio
import os

os.environ["TRELLO_API_KEY"] = "test_key"
os.environ["TRELLO_TOKEN"] = "test_token"

from server.dtos.create_custom_field import CreateCustomFieldPayload
from server.dtos.set_custom_field_value import SetCustomFieldValuePayload
from server.services.analytics import AnalyticsService
from server.services.custom_field import CustomFieldService
from server.services.export import ExportService
from server.services.search import SearchService
from server.tools import advanced_card, analytics, custom_field, export, search
from server.utils.trello_api import _redact_secrets


CUSTOM_FIELD = {
    "id": "field",
    "idModel": "board",
    "modelType": "board",
    "name": "Priority",
    "pos": 1,
    "type": "text",
}
CUSTOM_FIELD_ITEM = {
    "id": "item",
    "idCustomField": "field",
    "idModel": "card",
    "modelType": "card",
    "value": {"text": "high"},
}


class StubClient:
    def __init__(self):
        self.calls = []

    async def GET(self, endpoint, params=None):
        self.calls.append(("GET", endpoint, params))
        if endpoint == "/search":
            return {"cards": [], "boards": [], "members": [], "organizations": []}
        if endpoint == "/search/members":
            return []
        if endpoint.endswith("/customFields"):
            return [CUSTOM_FIELD]
        if endpoint.endswith("/customFieldItems"):
            return [CUSTOM_FIELD_ITEM]
        if endpoint.endswith("/actions"):
            return []
        if endpoint.endswith("/lists"):
            return []
        if endpoint.endswith("/exports"):
            return []
        return {
            "id": "board",
            "name": "Board",
            "lists": [],
            "cards": [],
            "members": [],
            "labels": [],
            "actions": [],
        }

    async def POST(self, endpoint, data=None, params=None):
        self.calls.append(("POST", endpoint, data, params))
        if endpoint == "/customFields":
            return CUSTOM_FIELD
        if endpoint.endswith("/options"):
            return {"id": "option"}
        if endpoint == "/boards":
            return {"id": "created", "name": "Template copy"}
        return {"id": "export", "status": "pending"}

    async def PUT(self, endpoint, data=None, params=None):
        self.calls.append(("PUT", endpoint, data, params))
        if "/customField/" in endpoint:
            return CUSTOM_FIELD_ITEM
        if endpoint.startswith("/customFields/"):
            return CUSTOM_FIELD
        return {}

    async def DELETE(self, endpoint, params=None):
        self.calls.append(("DELETE", endpoint, params))
        return {}


class ValidResource:
    async def validate_board_exists(self, _board_id):
        return None

    async def validate_card_exists(self, _card_id):
        return None


def test_async_services_call_the_public_trello_client_api():
    async def exercise():
        client = StubClient()
        search_service = SearchService(client)
        export_service = ExportService(client)
        analytics_service = AnalyticsService(client)
        custom_field_service = CustomFieldService(client)

        assert await search_service.search("roadmap") == {
            "cards": [],
            "boards": [],
            "members": [],
            "organizations": [],
        }
        assert await search_service.search_members("Ada") == []
        assert (await export_service.export_board("board"))["name"] == "Board"
        assert await export_service.list_organization_exports("org") == []
        assert (await export_service.create_organization_export("org"))["id"] == "export"
        assert (
            await export_service.create_board_from_template("source", "Template copy", "org")
        )["id"] == "created"
        assert (await analytics_service.get_board_statistics("board"))["total_cards"] == 0
        assert (await analytics_service.get_card_cycle_time("board"))["cycle_times"] == {}

        class InvalidAnalyticsClient(StubClient):
            async def GET(self, endpoint, params=None):
                if endpoint == "/boards/invalid":
                    return {
                        "id": "invalid",
                        "name": "Invalid dates",
                        "lists": [],
                        "cards": [{"idList": "list", "due": "not-a-date"}],
                        "members": [],
                        "labels": [{"id": "label"}],
                        "actions": [],
                    }
                return await super().GET(endpoint, params)

        invalid_stats = await AnalyticsService(InvalidAnalyticsClient()).get_board_statistics(
            "invalid"
        )
        assert invalid_stats["overdue_cards"] == 0
        assert invalid_stats["label_usage"] == {}

        assert (await custom_field_service.get_board_custom_fields("board"))[0].id == "field"
        assert (
            await custom_field_service.create_custom_field(
                CreateCustomFieldPayload(id_model="board", name="Priority", type="text")
            )
        ).id == "field"
        assert (await custom_field_service.update_custom_field("field", name="Urgency")).id == "field"
        await custom_field_service.delete_custom_field("field")
        assert (await custom_field_service.get_card_custom_field_items("card"))[0].id == "item"
        assert (
            await custom_field_service.set_custom_field_value(
                "card", "field", SetCustomFieldValuePayload(value={"text": "high"})
            )
        ).id == "item"
        assert (await custom_field_service.add_custom_field_option("field", "High"))["id"] == "option"
        assert await custom_field_service.update_custom_field_option("option", text="Low") == {}
        await custom_field_service.delete_custom_field_option("option")

        methods = [call[0] for call in client.calls]
        assert {"GET", "POST", "PUT", "DELETE"} <= set(methods)

    asyncio.run(exercise())


def test_async_tools_await_services_and_advanced_card_uses_public_client(monkeypatch):
    async def exercise():
        client = StubClient()
        validator = ValidResource()

        monkeypatch.setattr(search, "service", SearchService(client))
        monkeypatch.setattr(export, "service", ExportService(client))
        monkeypatch.setattr(export, "validator", validator)
        monkeypatch.setattr(analytics, "service", AnalyticsService(client))
        monkeypatch.setattr(analytics, "validator", validator)
        monkeypatch.setattr(custom_field, "service", CustomFieldService(client))
        monkeypatch.setattr(custom_field, "validator", validator)
        monkeypatch.setattr(advanced_card, "client", client)
        monkeypatch.setattr(advanced_card, "validator", validator)

        assert "0 cards" in await search.search_trello(object(), "roadmap")
        assert "0 member(s)" in await search.search_members(object(), "Ada")
        assert "Exported board" in await export.export_board(object(), "board")
        assert "Found 0 export(s)" in await export.list_organization_exports(object(), "org")
        assert "Created export" in await export.create_organization_export(object(), "org")
        assert "Created board" in await export.create_board_from_template(
            object(), "source", "Template copy", "org"
        )
        assert "Board Statistics" in await analytics.get_board_statistics(object(), "board")
        assert "Cycle Time" in await analytics.get_card_cycle_time(object(), "board")
        assert "Found 1 custom field(s)" in await custom_field.get_board_custom_fields(
            object(), "board"
        )
        assert "Created custom field" in await custom_field.create_custom_field(
            object(), "Priority", "text", board_id="board"
        )
        assert "Set text field" in await custom_field.set_custom_field_value_text(
            object(), "card", "field", "high"
        )
        assert "Added option" in await custom_field.add_custom_field_option(
            object(), "field", "High"
        )
        assert "Set due date" in await advanced_card.set_card_due_date(
            "card", "2027-01-01T00:00:00.000Z", object()
        )
        assert any(call[0] == "PUT" and call[1] == "/cards/card" for call in client.calls)

    asyncio.run(exercise())


def test_trello_error_redaction_covers_query_credentials():
    message = "GET https://api.trello.com/1/boards?id=board&key=secret&token=token-secret"
    redacted = _redact_secrets(message)
    assert "secret" not in redacted
    assert "token-secret" not in redacted
    assert "key=[REDACTED]" in redacted
    assert "token=[REDACTED]" in redacted
