# Security policy

Do not include Trello API keys, tokens, board exports, or customer data in
issues, pull requests, logs, or tool prompts. Report suspected vulnerabilities
privately through GitHub's security-advisory workflow for this repository.

The server limits batch reads to relative Trello API paths and labels MCP tools
as read-only or destructive so compatible clients can require confirmation for
write operations.
