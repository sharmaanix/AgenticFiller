# AgenticFiller

Multi-user Gmail MCP server. Authenticate any number of Gmail accounts once,
then expose their inboxes and PDF attachments as
[Model Context Protocol](https://modelcontextprotocol.io/) tools that any
MCP-compatible agent (Claude Desktop, custom agents, etc.) can call.

## Layout

```
src/agenticfiller/
├── config.py            Central paths, scopes, ports
├── auth/                OAuth flow + per-user token persistence
├── gmail/               Gmail API service factory + operations
├── pdf/                 PDF text + LLM-driven structured extraction
├── mcp_server/          FastMCP server entrypoint
└── cli/                 Console scripts
```

## Setup

```bash
# 1. Configure Google OAuth + Anthropic API key
cp .env.example .env
# fill in GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ANTHROPIC_API_KEY

# 2. Install
uv sync

# 3. Authenticate one or more Gmail users
uv run agenticfiller-auth --user alice@gmail.com
uv run agenticfiller-auth --user bob@gmail.com

# 4. Run the MCP server
uv run agenticfiller-mcp
```

Tokens persist under `~/.agenticfiller/tokens/`. Downloaded PDFs go to
`~/.agenticfiller/attachments/<user>/`.
