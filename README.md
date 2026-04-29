<!-- mcp-name: io.github.fgasparetto/chipsai-mcp -->

# ChipsAI MCP Server

MCP (Model Context Protocol) server for [ChipsBot](https://bot.chipsbuilder.com) — manage chatbots, conversations, documents, bot-to-bot routing, RAG configuration, and AI models from Claude Code, Claude Desktop, or any MCP client.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A ChipsBot account ([sign up](https://bot.chipsbuilder.com))

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

The server uses environment variables for authentication. **API key is the recommended method** — generate one from your [ChipsBot dashboard](https://bot.chipsbuilder.com/dashboard/settings/).

| Variable | Description | Default |
|----------|-------------|---------|
| `CHIPSAI_API_KEY` | Your ChipsAI API key (recommended) | — |
| `CHIPSAI_API_URL` | API base URL | `https://ai.chipsbuilder.com` |

<details>
<summary>Legacy: username/password authentication</summary>

If you don't have an API key, you can use username/password instead:

| Variable | Description |
|----------|-------------|
| `CHIPSAI_USERNAME` | Your ChipsAI username |
| `CHIPSAI_PASSWORD` | Your ChipsAI password |

</details>

### Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "chipsai": {
      "command": "uvx",
      "args": ["chipsai-mcp"],
      "env": {
        "CHIPSAI_API_KEY": "chipsai_your_api_key_here"
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
      "command": "uvx",
      "args": ["chipsai-mcp"],
      "env": {
        "CHIPSAI_API_KEY": "chipsai_your_api_key_here"
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

### Widget History

| Tool | Description |
|------|-------------|
| `list_conversation_history` | List widget conversation sessions (paginated, filter by chatbot) |
| `get_session_messages` | Get all messages from a widget conversation session |

### Chat

| Tool | Description |
|------|-------------|
| `send_message` | Send a message and get AI response (auto-creates conversation) |

### Bot-to-Bot Connections

| Tool | Description |
|------|-------------|
| `connect_bot` | Connect a specialist bot to an orchestrator bot (role-based routing) |
| `list_bot_connections` | List all specialist bots connected to an orchestrator |
| `update_bot_connection` | Update role, label, description, or active status of a connection |
| `disconnect_bot` | Remove a bot-to-bot connection |

### RAG Configuration

| Tool | Description |
|------|-------------|
| `get_rag_config` | Get RAG config: threshold, chunk settings, HyDE, L2, reranker, system instructions |
| `update_rag_config` | Update RAG config (threshold, chunk_size, chunk_strategy, HyDE, L2, reranker, etc.) |

### User & Models

| Tool | Description |
|------|-------------|
| `get_user_plan` | Get credit balance, unlimited status, usage stats |
| `list_ai_models` | List available AI models by provider with credit costs |

## RAG Pipeline

ChipsBot supports a full Retrieval-Augmented Generation pipeline configurable per-bot:

- **Semantic routing (L1):** pgvector + Jina Embeddings v3 — routes queries to the best specialist based on cosine similarity (HNSW index)
- **HyDE:** for sparse/short queries, generates a hypothetical answer with Haiku and re-embeds it for better retrieval
- **Chunk injection (L2):** at response time, injects only the top-K relevant KB chunks instead of the full prompt — reduces token usage, improves quality
- **Reranking:** optional Jina cross-encoder reranker (`jina-reranker-v2-base-multilingual`) applied after cosine retrieval
- **Chunking strategies:** `char` (fixed size), `paragraph` (semantic `\n\n` split), `sentence` (`.!?` split)
- **Document upload:** PDF/DOC/DOCX parsed via LlamaParse, extracted text stored as KB

Use `get_rag_config` / `update_rag_config` to tune all parameters per-bot.

## Bot-to-Bot Routing

An orchestrator bot can route questions to specialist bots based on role/description. The orchestrator detects `[ROUTE:uuid]` tags in its own response and delegates to the matching specialist, passing recent chat history as context.

Use `connect_bot` to link specialists to an orchestrator, `list_bot_connections` to inspect the routing table, and `update_bot_connection` to adjust roles or toggle connections on/off.

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
- *"Connect the billing bot as a specialist of my main orchestrator"*
- *"List all specialist bots connected to my orchestrator"*
- *"Show the RAG config for my chatbot"*
- *"Set the RAG threshold to 0.5 and enable reranking"*
- *"Enable L2 chunk injection with top_k=5"*

## Authentication

**API Key (recommended):** Set `CHIPSAI_API_KEY` with a key generated from your dashboard. The key is sent as a Bearer token — no token management needed.

**JWT (legacy):** If using username/password, tokens are obtained via JWT and refreshed transparently.

## License

MIT
