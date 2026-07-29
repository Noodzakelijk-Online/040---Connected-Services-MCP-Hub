"""
This module contains tools for managing Trello boards.
"""

import logging
from typing import List

from mcp.server.fastmcp import Context

from server.models import TrelloBoard, TrelloLabel, TrelloMember
from server.dtos.create_label import CreateLabelPayload
from server.dtos.create_board import CreateBoardPayload
from server.dtos.update_board import UpdateBoardPayload
from server.services.board import BoardService
from server.validators import ValidationService
from server.trello import client
from server.exceptions import TrelloMCPError
from server.active_context import active_context

logger = logging.getLogger(__name__)

service = BoardService(client)
validator = ValidationService(client)


async def get_board(ctx: Context, board_id: str | None = None) -> TrelloBoard:
    """Retrieves a specific board by its ID.

    Args:
        board_id (str): The ID of the board to retrieve.

    Returns:
        TrelloBoard: The board object containing board details.
    """
    try:
        board_id = active_context.resolve_board(ctx, board_id)
        logger.info(f"Getting board with ID: {board_id}")
        result = await service.get_board(board_id)
        logger.info(f"Successfully retrieved board: {board_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to get board: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_boards(ctx: Context) -> List[TrelloBoard]:
    """Retrieves all boards for the authenticated user.

    Returns:
        List[TrelloBoard]: A list of board objects.
    """
    try:
        logger.info("Getting all boards")
        result = await service.get_boards()
        logger.info(f"Successfully retrieved {len(result)} boards")
        return result
    except Exception as e:
        error_msg = f"Failed to get boards: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_board_labels(ctx: Context, board_id: str | None = None) -> List[TrelloLabel]:
    """Retrieves all labels for a specific board.

    Args:
        board_id (str): The ID of the board whose labels to retrieve.

    Returns:
        List[TrelloLabel]: A list of label objects for the board.
    """
    try:
        board_id = active_context.resolve_board(ctx, board_id)
        logger.info(f"Getting labels for board: {board_id}")
        result = await service.get_board_labels(board_id)
        logger.info(f"Successfully retrieved {len(result)} labels for board: {board_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to get board labels: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_board_members(ctx: Context, board_id: str | None = None) -> List[TrelloMember]:
    """Retrieves all members of a specific board.

    Args:
        board_id (str): The ID of the board whose members to retrieve.

    Returns:
        List[TrelloMember]: A list of member objects with id, fullName, and username.
    """
    try:
        board_id = active_context.resolve_board(ctx, board_id)
        logger.info(f"Getting members for board: {board_id}")
        result = await service.get_board_members(board_id)
        logger.info(f"Successfully retrieved {len(result)} members for board: {board_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to get board members: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def create_board_label(ctx: Context, payload: CreateLabelPayload, board_id: str | None = None) -> TrelloLabel:
    """Create label for a specific board.

    Args:
        board_id (str): The ID of the board whose to add label to.
        payload (CreateLabelPayload): The label creation payload.

    Returns:
        TrelloLabel: A label object for the board.
    """
    try:
        board_id = active_context.resolve_board(ctx, board_id)
        logger.info(f"Creating label {payload.name} label for board: {board_id}")
        # Validate board exists
        await validator.validate_board_exists(board_id)
        result = await service.create_board_label(board_id, **payload.model_dump(exclude_unset=True))
        logger.info(f"Successfully created label {payload.name} for board: {board_id}")
        return result
    except TrelloMCPError as e:
        error_msg = f"Failed to create board label: {e.message}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Failed to create board label: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def create_board(ctx: Context, payload: CreateBoardPayload) -> TrelloBoard:
    """Create a new Trello board.

    Args:
        payload (CreateBoardPayload): The board creation payload containing name, description,
                                     organization, and preferences.

    Returns:
        TrelloBoard: The newly created board object.
    """
    try:
        logger.info(f"Creating board: {payload.name}")

        # Validate organization exists if specified
        if payload.id_organization:
            await validator.validate_organization_exists(payload.id_organization)
            await validator.validate_organization_membership(payload.id_organization)

        result = await service.create_board(**payload.model_dump(exclude_unset=True))
        logger.info(f"Successfully created board: {result.id} - {result.name}")
        return result
    except TrelloMCPError as e:
        error_msg = f"Failed to create board: {e.message}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Failed to create board: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def update_board(ctx: Context, payload: UpdateBoardPayload, board_id: str | None = None) -> TrelloBoard:
    """Update an existing Trello board.

    Args:
        board_id (str): The ID of the board to update.
        payload (UpdateBoardPayload): The board update payload containing fields to update.

    Returns:
        TrelloBoard: The updated board object.
    """
    try:
        board_id = active_context.resolve_board(ctx, board_id)
        logger.info(f"Updating board: {board_id}")

        # Validate board exists
        await validator.validate_board_exists(board_id)

        # Validate organization exists if moving board
        if payload.id_organization:
            await validator.validate_organization_exists(payload.id_organization)
            await validator.validate_organization_membership(payload.id_organization)

        # Convert payload to API parameters
        params = payload.to_api_params()

        result = await service.update_board(board_id, **params)
        logger.info(f"Successfully updated board: {board_id}")
        return result
    except TrelloMCPError as e:
        error_msg = f"Failed to update board: {e.message}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Failed to update board: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def delete_board(ctx: Context, board_id: str | None = None) -> dict:
    """Delete a Trello board permanently.

    Args:
        board_id (str): The ID of the board to delete.

    Returns:
        dict: Confirmation of deletion.
    """
    try:
        board_id = active_context.resolve_board(ctx, board_id)
        logger.info(f"Deleting board: {board_id}")

        # Validate board exists and user has admin permission
        await validator.validate_board_exists(board_id)
        await validator.validate_board_admin_permission(board_id)

        result = await service.delete_board(board_id)
        logger.info(f"Successfully deleted board: {board_id}")
        return {"success": True, "message": f"Board {board_id} has been permanently deleted"}
    except TrelloMCPError as e:
        error_msg = f"Failed to delete board: {e.message}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Failed to delete board: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
