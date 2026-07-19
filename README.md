# Freshdesk + Trello MCP Connectors for ChatGPT

This repository contains two independent FastMCP servers, grouped by their
external service. It preserves the Git history from both the original
Freshdesk (`040`) and Trello (`040.5`) repositories.

## Services

| Service | Directory | Default port | Required environment variables |
| --- | --- | --- | --- |
| Freshdesk | `freshdesk/` | 8001 | `FRESHDESK_DOMAIN`, `FRESHDESK_API_KEY` |
| Trello | `trello/` | 8000 | `TRELLO_KEY`, `TRELLO_TOKEN` |

Each service has its own `requirements.txt` because the original connectors
depend on different FastMCP version ranges. Run each server in its own virtual
environment.

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

The Freshdesk server starts on port 8001 and the Trello server starts on port
8000. Do not commit the `.env` files or generated log files.
