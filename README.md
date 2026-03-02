# ChipsAI MCP Server

MCP (Model Context Protocol) server for [ChipsAI](https://ai.chipsbuilder.com) — manage chatbots, conversations, documents, and AI models from Claude Code, Claude Desktop, or any MCP client.

## Requirements

- Python 3.11+
- A ChipsAI account ([sign up](https://ai.chipsbuilder.com))

## Installation

```bash
pip install mcp httpx
```

Or with uv:

```bash
uv pip install mcp httpx
```

## Configuration

The server uses environment variables for authentication (no credentials in code):

| Variable | Description | Default |
|----------|-------------|---------|
| `CHIPSAI_API_URL` | API base URL | `https://ai.chipsbuilder.com` |
| `CHIPSAI_USERNAME` | Your ChipsAI username | — |
| `CHIPSAI_PASSWORD` | Your ChipsAI password | — |

### Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "chipsai": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/chipsai-mcp/server.py"],
      "env": {
        "CHIPSAI_API_URL": "https://ai.chipsbuilder.com",
        "CHIPSAI_USERNAME": "your-username",
        "CHIPSAI_PASSWORD": "your-password"
      }
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "chipsai": {
      "command": "python3",
      "args": ["/path/to/chipsai-mcp/server.py"],
      "env": {
        "CHIPSAI_USERNAME": "your-username",
        "CHIPSAI_PASSWORD": "your-password"
      }
    }
  }
}
```

## Available Tools

### Chatbot Management

| Tool | Description |
|------|-------------|
| `list_chatbots` | List all chatbots for the authenticated user |
| `get_chatbot` | Get full chatbot details (prompt, model, colors, etc.) |
| `create_chatbot` | Create a new chatbot (returns embed script tag) |
| `update_chatbot` | Update chatbot fields (name, prompt, model, theme, colors, etc.) |
| `delete_chatbot` | Soft-delete (deactivate) a chatbot |
| `get_chatbot_config` | Get public widget configuration |
| `get_chatbot_analytics` | Get analytics: messages, sessions, daily stats, devices, countries |

### Documents (RAG)

| Tool | Description |
|------|-------------|
| `upload_document` | Upload PDF/DOC/DOCX to a chatbot's knowledge base |

### Conversations (VIP)

| Tool | Description |
|------|-------------|
| `list_conversations` | List conversations, optionally filtered by chatbot |
| `create_conversation` | Create a new conversation |
| `get_conversation` | Get conversation details |
| `update_conversation` | Update conversation title |
| `delete_conversation` | Delete a conversation and all messages |
| `get_conversation_messages` | Get all messages from a conversation |
| `send_message` | Send a message and get AI response |

### User & Models

| Tool | Description |
|------|-------------|
| `get_user_plan` | Get current plan info (limits, usage) |
| `list_ai_models` | List available AI models by provider |

## Usage Examples

Once configured, you can use natural language in Claude:

- *"List my chatbots"*
- *"Create a chatbot called Support Bot for my company"*
- *"Upload the product catalog PDF to my chatbot"*
- *"Show analytics for the last 7 days"*
- *"Change the chatbot model to Claude Sonnet 4.6"*
- *"What AI models are available?"*

## Authentication

The server uses JWT with automatic token refresh. Tokens are obtained via username/password and refreshed transparently — no manual token management needed.

## License

MIT
