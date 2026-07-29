"""
Service for managing Trello custom fields.
"""

from typing import List, Dict, Any
from server.utils.trello_api import TrelloClient
from server.models.custom_field import TrelloCustomField, TrelloCustomFieldItem
from server.dtos.create_custom_field import CreateCustomFieldPayload
from server.dtos.set_custom_field_value import SetCustomFieldValuePayload


class CustomFieldService:
    """Service for custom field operations."""

    def __init__(self, client: TrelloClient):
        """
        Initialize the custom field service.

        Args:
            client: Trello API client instance
        """
        self.client = client

    async def get_board_custom_fields(self, board_id: str) -> List[TrelloCustomField]:
        """
        Get all custom fields on a board.

        Args:
            board_id: The ID of the board

        Returns:
            List of TrelloCustomField objects
        """
        response = await self.client.GET(f"/boards/{board_id}/customFields")
        return [TrelloCustomField(**field) for field in response]

    async def create_custom_field(self, payload: CreateCustomFieldPayload) -> TrelloCustomField:
        """
        Create a new custom field on a board.

        Args:
            payload: Custom field creation payload

        Returns:
            Created TrelloCustomField object
        """
        params = payload.to_api_params()
        response = await self.client.POST("/customFields", data=params)
        return TrelloCustomField(**response)

    async def update_custom_field(
        self,
        field_id: str,
        name: str = None,
        pos: str = None
    ) -> TrelloCustomField:
        """
        Update a custom field.

        Args:
            field_id: The ID of the custom field
            name: New name for the field
            pos: New position for the field

        Returns:
            Updated TrelloCustomField object
        """
        params = {}
        if name is not None:
            params["name"] = name
        if pos is not None:
            params["pos"] = pos

        response = await self.client.PUT(f"/customFields/{field_id}", data=params)
        return TrelloCustomField(**response)

    async def delete_custom_field(self, field_id: str) -> None:
        """
        Delete a custom field.

        Args:
            field_id: The ID of the custom field
        """
        await self.client.DELETE(f"/customFields/{field_id}")

    async def get_card_custom_field_items(self, card_id: str) -> List[TrelloCustomFieldItem]:
        """
        Get all custom field values on a card.

        Args:
            card_id: The ID of the card

        Returns:
            List of TrelloCustomFieldItem objects
        """
        response = await self.client.GET(f"/cards/{card_id}/customFieldItems")
        return [TrelloCustomFieldItem(**item) for item in response]

    async def set_custom_field_value(
        self,
        card_id: str,
        field_id: str,
        payload: SetCustomFieldValuePayload
    ) -> TrelloCustomFieldItem:
        """
        Set a custom field value on a card.

        Args:
            card_id: The ID of the card
            field_id: The ID of the custom field
            payload: Value payload

        Returns:
            Updated TrelloCustomFieldItem object
        """
        params = payload.to_api_params()
        response = await self.client.PUT(
            f"/cards/{card_id}/customField/{field_id}/item",
            data=params,
        )
        return TrelloCustomFieldItem(**response)

    async def add_custom_field_option(
        self,
        field_id: str,
        text: str,
        color: str = "none",
        pos: str = "bottom"
    ) -> Dict[str, Any]:
        """
        Add an option to a list-type custom field.

        Args:
            field_id: The ID of the custom field
            text: The text for the option
            color: The color for the option
            pos: The position for the option

        Returns:
            Created option object
        """
        params = {
            "value": {"text": text},
            "color": color,
            "pos": pos
        }
        response = await self.client.POST(f"/customFields/{field_id}/options", data=params)
        return response

    async def update_custom_field_option(
        self,
        option_id: str,
        text: str = None,
        color: str = None,
        pos: str = None
    ) -> Dict[str, Any]:
        """
        Update a custom field option.

        Args:
            option_id: The ID of the option
            text: New text for the option
            color: New color for the option
            pos: New position for the option

        Returns:
            Updated option object
        """
        params = {}
        if text is not None:
            params["value"] = {"text": text}
        if color is not None:
            params["color"] = color
        if pos is not None:
            params["pos"] = pos

        response = await self.client.PUT(f"/customFieldOptions/{option_id}", data=params)
        return response

    async def delete_custom_field_option(self, option_id: str) -> None:
        """
        Delete a custom field option.

        Args:
            option_id: The ID of the option
        """
        await self.client.DELETE(f"/customFieldOptions/{option_id}")
