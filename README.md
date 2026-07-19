# Freshdesk + Trello MCP Connectors for ChatGPT

This repository contains two independent FastMCP servers, grouped by their
external service. It preserves the Git history from both the original
Freshdesk (`040`) and Trello (`040.5`) repositories.

## Services

| Service | Directory | Default port | Required environment variables |
| --- | --- | --- | --- |
| Freshdesk | `freshdesk/` | 8001 | `FRESHDESK_DOMAIN`, `FRESHDESK_API_KEY` |
| Trello (lightweight) | `trello/` | 8000 | `TRELLO_KEY`, `TRELLO_TOKEN` |
| Trello (enhanced) | `trello-enhanced/` | 8000 | `TRELLO_API_KEY`, `TRELLO_TOKEN` |

Each service has its own dependency definition because the original connectors
use different MCP SDKs and FastMCP version ranges. Run each server in its own
virtual environment. The enhanced Trello server also has a Docker setup and a
substantial set of board, list, card, collaboration, analytics, and automation
tools.

## Run a service

From either `freshdesk/` or `trello/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Fill in the service credentials in .env, then:
python main.py
```

The Freshdesk server starts on port 8001 and the lightweight Trello server
starts on port 8000. Do not commit the `.env` files or generated log files.

## Run the enhanced Trello server

The full server is in `trello-enhanced/`. Its `pyproject.toml` and `uv.lock`
are preserved from `trello-mcp-server`:

```powershell
cd trello-enhanced
Copy-Item .env.example .env
# Set TRELLO_API_KEY and TRELLO_TOKEN in .env, then:
uv sync --python 3.13
uv run --python 3.13 python main.py
```

Both Trello implementations default to port 8000, so run only one at a time or
set `MCP_SERVER_PORT` for the enhanced server. The enhanced server's locked
dependencies require Python 3.12 or 3.13; its pinned `pydantic-core` does not
yet build on Python 3.14.
