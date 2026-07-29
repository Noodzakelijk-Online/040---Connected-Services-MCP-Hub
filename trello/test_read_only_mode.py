"""Regression tests for the server-side read-only tool boundary."""

import os

os.environ["TRELLO_API_KEY"] = "test_key"
os.environ["TRELLO_TOKEN"] = "test_token"

from server.tools.tools import register_tools


class MockMCP:
    def __init__(self):
        self.tools = []

    def add_tool(self, tool, **_kwargs):
        self.tools.append(tool)


def test_read_only_mode_excludes_mutation_tools():
    mcp = MockMCP()
    register_tools(mcp, read_only=True)

    names = {tool.__name__ for tool in mcp.tools}
    assert len(names) == len(mcp.tools)
    assert {"get_boards", "search_cards", "overview", "fetch"} <= names
    assert not {
        "create_board",
        "update_board",
        "delete_board",
        "create_card",
        "move_card",
        "set_active_board",
    } & names


def test_full_mode_retains_mutation_tools():
    mcp = MockMCP()
    register_tools(mcp, read_only=False)

    names = {tool.__name__ for tool in mcp.tools}
    assert len(names) == len(mcp.tools)
    assert {"create_board", "create_card", "move_card", "set_active_board"} <= names
