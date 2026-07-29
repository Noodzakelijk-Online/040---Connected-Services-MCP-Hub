"""
Service for Trello analytics and reporting.
"""

from typing import Dict, Any
from datetime import datetime, timezone
from collections import defaultdict
from server.utils.trello_api import TrelloClient


def _parse_trello_timestamp(value: object) -> datetime | None:
    """Parse a Trello timestamp without letting malformed source data break analytics."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class AnalyticsService:
    """Service for analytics and reporting operations."""

    def __init__(self, client: TrelloClient):
        """
        Initialize the analytics service.

        Args:
            client: Trello API client instance
        """
        self.client = client

    async def get_board_statistics(self, board_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a board.

        Args:
            board_id: The ID of the board

        Returns:
            Dictionary containing board statistics
        """
        # Get board with all data
        params = {
            "cards": "all",
            "lists": "all",
            "members": "all",
            "labels": "all",
            "actions": "all",
            "actions_limit": "1000"
        }
        board = await self.client.GET(f"/boards/{board_id}", params=params)

        # Calculate statistics
        overdue_cards = 0
        now = datetime.now(timezone.utc)
        for card in board.get("cards", []):
            due = _parse_trello_timestamp(card.get("due"))
            if due and not card.get("dueComplete") and due < now:
                overdue_cards += 1

        stats = {
            "board_name": board.get("name"),
            "board_id": board_id,
            "total_lists": len(board.get("lists", [])),
            "total_cards": len(board.get("cards", [])),
            "total_members": len(board.get("members", [])),
            "total_labels": len(board.get("labels", [])),
            "open_cards": len([c for c in board.get("cards", []) if not c.get("closed")]),
            "closed_cards": len([c for c in board.get("cards", []) if c.get("closed")]),
            "cards_with_due_dates": len([c for c in board.get("cards", []) if c.get("due")]),
            "overdue_cards": overdue_cards,
            "completed_cards": len([c for c in board.get("cards", []) if c.get("dueComplete")]),
        }

        # Cards per list
        cards_per_list = defaultdict(int)
        for card in board.get("cards", []):
            if not card.get("closed"):
                list_id = card.get("idList")
                cards_per_list[list_id] += 1

        # Find list names
        list_names = {lst["id"]: lst["name"] for lst in board.get("lists", [])}
        stats["cards_per_list"] = {
            list_names.get(lid, lid): count
            for lid, count in cards_per_list.items()
        }

        # Label usage
        label_usage = defaultdict(int)
        for card in board.get("cards", []):
            for label_id in card.get("idLabels", []):
                label_usage[label_id] += 1

        label_names = {
            label["id"]: label.get("name") or label.get("color") or label["id"]
            for label in board.get("labels", [])
            if label.get("id")
        }
        stats["label_usage"] = {
            label_names.get(lid, lid): count
            for lid, count in label_usage.items()
        }

        # Member activity
        member_actions = defaultdict(int)
        for action in board.get("actions", []):
            member_id = action.get("idMemberCreator")
            if member_id:
                member_actions[member_id] += 1

        member_names = {mbr["id"]: mbr.get("fullName", mbr.get("username")) for mbr in board.get("members", [])}
        stats["member_activity"] = {
            member_names.get(mid, mid): count
            for mid, count in member_actions.items()
        }

        return stats

    async def get_card_cycle_time(self, board_id: str) -> Dict[str, Any]:
        """
        Calculate average time cards spend in each list.

        Args:
            board_id: The ID of the board

        Returns:
            Dictionary containing cycle time statistics
        """
        # Get board actions
        params = {
            "filter": "updateCard:idList",
            "limit": "1000"
        }
        actions = await self.client.GET(f"/boards/{board_id}/actions", params=params)

        # Get lists
        lists = await self.client.GET(f"/boards/{board_id}/lists")
        list_names = {lst["id"]: lst["name"] for lst in lists}

        # Calculate time in each list
        card_times = defaultdict(lambda: defaultdict(list))
        card_current_list = {}
        card_list_enter_time = {}

        # Process actions in reverse chronological order
        for action in reversed(actions):
            card_id = action.get("data", {}).get("card", {}).get("id")
            list_after = action.get("data", {}).get("listAfter", {}).get("id")
            action_date = action.get("date")

            if card_id and list_after:
                # Card moved to new list
                if card_id in card_current_list and card_id in card_list_enter_time:
                    # Calculate time in previous list
                    prev_list = card_current_list[card_id]
                    enter_time = _parse_trello_timestamp(card_list_enter_time[card_id])
                    exit_time = _parse_trello_timestamp(action_date)
                    if enter_time and exit_time:
                        duration = (exit_time - enter_time).total_seconds() / 3600
                        if duration >= 0:
                            card_times[prev_list]["durations"].append(duration)

                card_current_list[card_id] = list_after
                card_list_enter_time[card_id] = action_date

        # Calculate averages
        cycle_times = {}
        for list_id, data in card_times.items():
            durations = data["durations"]
            if durations:
                cycle_times[list_names.get(list_id, list_id)] = {
                    "average_hours": sum(durations) / len(durations),
                    "min_hours": min(durations),
                    "max_hours": max(durations),
                    "card_count": len(durations)
                }

        return {
            "board_id": board_id,
            "cycle_times": cycle_times
        }
