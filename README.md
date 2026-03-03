# ChipsAI MCP Server

MCP (Model Context Protocol) server for [ChipsAI](https://ai.chipsbuilder.com) — manage chatbots, conversations, documents, and AI models from Claude Code, Claude Desktop, or any MCP client.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A ChipsAI account ([sign up](https://ai.chipsbuilder.com))

## Quick Start

No installation needed with `uv`:

```bash
uv run --script server.py
```

Or install manually:

```bash
pip install "mcp[cli]" httpx
python server.py
```

## Configuration

The server uses environment variables for authentication:

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
      "command": "uv",
      "args": ["run", "--script", "/path/to/chipsai-mcp/server.py"],
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
      "command": "uv",
      "args": ["run", "--script", "/path/to/chipsai-mcp/server.py"],
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
| `upload_document` | Upload PDF/DOC/DOCX to a chatbot's knowledge base (LlamaParse) |

### Conversations

| Tool | Description |
|------|-------------|
| `list_conversations` | List conversations, optionally filtered by chatbot |
| `create_conversation` | Create a new conversation |
| `get_conversation` | Get conversation details |
| `update_conversation` | Update conversation title |
| `delete_conversation` | Delete a conversation and all messages |
| `get_conversation_messages` | Get all messages from a conversation |

### Chat

| Tool | Description |
|------|-------------|
| `send_message` | Send a message and get AI response (auto-creates conversation) |

### User & Models

| Tool | Description |
|------|-------------|
| `get_user_plan` | Get credit balance, unlimited status, usage stats |
| `list_ai_models` | List available AI models by provider with credit costs |

## Credit System

ChipsAI uses a credit-based pricing model:

| Tier | Credits/msg | Models |
|------|-------------|--------|
| **Free** | 0 | Llama 4 Scout, Llama 3.3 70B, Llama 3.1 8B (Groq) |
| **Economy** | 0.5 | Mistral Nemo, DeepSeek Chat |
| **Standard** | 1.0 | GPT-4o-mini, Gemini 2.5 Flash, Mistral Small, Claude Haiku 4.5 |
| **Premium** | 2.0 | GPT-4o, Mistral Large, DeepSeek Reasoner |
| **Top** | 3.0 | GPT-4.1, Claude Sonnet 4.6, Gemini 2.5 Pro |

Credit packages: **150 credits for €5** | **700 for €20** | **2000 for €50**. Credits never expire. Bring your own API key to use any model for free (no credits consumed).

## Usage Examples

Once configured, use natural language in Claude:

- *"List my chatbots"*
- *"Create a chatbot called Support Bot"*
- *"Upload the product catalog PDF to my chatbot"*
- *"Send a test message to my chatbot"*
- *"Show analytics for the last 7 days"*
- *"Change the chatbot model to Claude Sonnet 4.6"*
- *"What's my credit balance?"*
- *"What AI models are available?"*

## Authentication

The server uses JWT with automatic token refresh. Tokens are obtained via username/password and refreshed transparently — no manual token management needed.

## License

MIT
