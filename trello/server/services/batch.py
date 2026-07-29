"""
Service for Trello batch operations.
"""

from typing import List, Dict, Any
from server.utils.trello_api import TrelloClient


class BatchService:
    """Service for batch operations."""

    def __init__(self, client: TrelloClient):
        """
        Initialize the batch service.

        Args:
            client: Trello API client instance
        """
        self.client = client

    async def batch_get(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Execute multiple GET requests in a single batch.

        Args:
            urls: List of relative URLs to fetch (max 10)

        Returns:
            List of response objects
        """
        if not urls or len(urls) > 10:
            raise ValueError("Maximum 10 URLs allowed per batch request")
        if any(
            not url.startswith("/")
            or url.startswith("//")
            or "://" in url
            or "\r" in url
            or "\n" in url
            for url in urls
        ):
            raise ValueError("Batch URLs must be relative Trello API paths beginning with one slash")

        # Join URLs with comma
        urls_param = ",".join(urls)

        response = await self.client.GET("/batch", params={"urls": urls_param})
        return response
