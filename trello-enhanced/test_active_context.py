from server.active_context import active_context


class FakeContext:
    client_id = "test-client"

    @property
    def session(self):
        return object()


def test_active_context_is_scoped_and_resolves_defaults():
    first = FakeContext()
    active_context.clear(first)
    active_context.set_board(first, "board-1")
    active_context.set_workspace(first, "workspace-1")

    assert active_context.resolve_board(first, None) == "board-1"
    assert active_context.resolve_workspace(first, None) == "workspace-1"
    assert active_context.resolve_board(first, "board-override") == "board-override"


def test_active_context_requires_a_selection():
    second = FakeContext()
    second.client_id = "another-client"
    active_context.clear(second)

    try:
        active_context.resolve_board(second, None)
    except ValueError as error:
        assert "set_active_board" in str(error)
    else:
        raise AssertionError("Expected an active-board selection error")
