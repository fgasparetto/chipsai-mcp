"""
ChipsAI MCP Server - Manage ai.chipsbuilder.com chatbots via MCP.

Tools: chatbot CRUD, conversations, chat, user plan, AI models, document upload, analytics.
Auth: JWT with auto-refresh.
"""

import os
import time
import asyncio
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# --- Config from env ---
API_URL = os.environ.get("CHIPSAI_API_URL", "https://ai.chipsbuilder.com").rstrip("/")
USERNAME = os.environ.get("CHIPSAI_USERNAME", "")
PASSWORD = os.environ.get("CHIPSAI_PASSWORD", "")


# --- Token Manager ---
class TokenManager:
    def __init__(self):
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.access_expires_at: float = 0
        self._lock = asyncio.Lock()

    async def get_token(self, client: httpx.AsyncClient) -> str:
        async with self._lock:
            if self.access_token and time.time() < self.access_expires_at:
                return self.access_token
            if self.refresh_token:
                try:
                    return await self._refresh(client)
                except Exception:
                    pass
            return await self._login(client)

    async def _login(self, client: httpx.AsyncClient) -> str:
        r = await client.post(
            f"{API_URL}/api/token/",
            json={"username": USERNAME, "password": PASSWORD},
        )
        r.raise_for_status()
        data = r.json()
        self.access_token = data["access"]
        self.refresh_token = data["refresh"]
        self.access_expires_at = time.time() + 270  # 4.5 min (token lasts 5)
        return self.access_token

    async def _refresh(self, client: httpx.AsyncClient) -> str:
        r = await client.post(
            f"{API_URL}/api/token/refresh/",
            json={"refresh": self.refresh_token},
        )
        r.raise_for_status()
        data = r.json()
        self.access_token = data["access"]
        self.access_expires_at = time.time() + 270
        return self.access_token

    def invalidate(self):
        self.access_token = None
        self.access_expires_at = 0


token_mgr = TokenManager()


# --- HTTP helper ---
async def api_request(
    method: str,
    path: str,
    *,
    json_data: dict | None = None,
    params: dict | None = None,
    files: dict | None = None,
) -> Any:
    """Make authenticated API request with auto-retry on 401."""
    async with httpx.AsyncClient(timeout=60) as client:
        token = await token_mgr.get_token(client)

        for attempt in range(2):
            headers = {"Authorization": f"Bearer {token}"}
            kwargs: dict[str, Any] = {"headers": headers}
            if params:
                kwargs["params"] = params
            if files:
                kwargs["files"] = files
            elif json_data is not None:
                kwargs["json"] = json_data

            r = await client.request(method, f"{API_URL}{path}", **kwargs)

            if r.status_code == 401 and attempt == 0:
                token_mgr.invalidate()
                token = await token_mgr.get_token(client)
                continue

            if r.status_code >= 400:
                try:
                    detail = r.json()
                except Exception:
                    detail = r.text
                return {"error": f"HTTP {r.status_code}", "detail": detail}

            if r.status_code == 204:
                return {"success": True}
            return r.json()

    return {"error": "Request failed"}


# --- FastMCP Server ---
mcp = FastMCP(
    "chipsai",
    instructions=(
        "Manage ai.chipsbuilder.com (ChipsAI) chatbots, conversations, and AI models. "
        "Use list_chatbots to see chatbots, get/create/update/delete them. "
        "VIP users can manage conversations and send chat messages."
    ),
)


# ========== Chatbot Management ==========

@mcp.tool()
async def list_chatbots() -> dict:
    """List all chatbots for the authenticated user. Returns uuid, name, brand_name, welcome, is_active, created_at."""
    return await api_request("GET", "/api/v1/chatbots/")


@mcp.tool()
async def get_chatbot(uuid: str) -> dict:
    """Get full chatbot details: name, brand_name, welcome, prompt, current_ai_model, colors, is_active."""
    return await api_request("GET", f"/api/v1/chatbots/{uuid}/")


@mcp.tool()
async def create_chatbot(
    name: str, brand_name: str = "", welcome: str = ""
) -> dict:
    """Create a new chatbot. Returns uuid, details, and the embed script tag to add to any website."""
    result = await api_request(
        "POST", "/api/v1/chatbots/", json_data={"name": name, "brand_name": brand_name, "welcome": welcome}
    )
    if "uuid" in result:
        result["embed_script"] = (
            f'<script src="{API_URL}/static/widget/chatbot-widget.js" '
            f'data-chatbot-uuid="{result["uuid"]}"></script>'
        )
    return result


@mcp.tool()
async def update_chatbot(
    uuid: str,
    name: str = "",
    brand_name: str = "",
    welcome: str = "",
    prompt: str = "",
    current_ai_model: str = "",
    chat_bg_color: str = "",
    bot_text_bg_color: str = "",
    user_text_bg_color: str = "",
    is_active: bool | None = None,
    allowed_domains: str = "",
    theme: str = "",
) -> dict:
    """Update chatbot fields. Only non-empty values are sent. Use get_chatbot first to see current values."""
    data: dict[str, Any] = {}
    for field, val in [
        ("name", name), ("brand_name", brand_name), ("welcome", welcome),
        ("prompt", prompt), ("current_ai_model", current_ai_model),
        ("chat_bg_color", chat_bg_color), ("bot_text_bg_color", bot_text_bg_color),
        ("user_text_bg_color", user_text_bg_color), ("allowed_domains", allowed_domains),
        ("theme", theme),
    ]:
        if val:
            data[field] = val
    if is_active is not None:
        data["is_active"] = is_active
    if not data:
        return {"error": "No fields to update. Provide at least one non-empty field."}
    return await api_request("PATCH", f"/api/v1/chatbots/{uuid}/", json_data=data)


@mcp.tool()
async def delete_chatbot(uuid: str) -> dict:
    """Soft-delete (deactivate) a chatbot."""
    return await api_request("DELETE", f"/api/v1/chatbots/{uuid}/")


@mcp.tool()
async def get_chatbot_config(uuid: str) -> dict:
    """Get public widget configuration for a chatbot: colors, fonts, logo, welcome message."""
    return await api_request("GET", f"/api/v1/config/{uuid}/")


@mcp.tool()
async def get_chatbot_analytics(uuid: str, days: int = 30) -> dict:
    """Get chatbot analytics: total messages, sessions, daily stats, device/country distribution."""
    return await api_request("GET", f"/api/v1/chatbots/{uuid}/analytics/", params={"days": days})


# ========== Document Upload ==========

@mcp.tool()
async def upload_document(uuid: str, file_path: str) -> dict:
    """Upload a PDF/DOC/DOCX file to a chatbot for RAG knowledge base extraction (LlamaParse). Provide absolute local file_path."""
    import os.path
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    async with httpx.AsyncClient(timeout=120) as client:
        token = await token_mgr.get_token(client)
        r = await client.post(
            f"{API_URL}/api/v1/chatbots/{uuid}/upload-document/",
            headers={"Authorization": f"Bearer {token}"},
            files={"document": (filename, file_bytes)},
        )
        if r.status_code >= 400:
            try:
                detail = r.json()
            except Exception:
                detail = r.text
            return {"error": f"HTTP {r.status_code}", "detail": detail}
        return r.json()


# ========== Conversations (VIP) ==========

@mcp.tool()
async def list_conversations(chatbot_uuid: str = "") -> dict:
    """List conversations. Optionally filter by chatbot_uuid. Requires VIP plan."""
    params = {}
    if chatbot_uuid:
        params["chatbot"] = chatbot_uuid
    return await api_request("GET", "/api/v1/conversations/", params=params)


@mcp.tool()
async def create_conversation(chatbot_id: str, title: str = "New conversation") -> dict:
    """Create a new conversation for a chatbot. Requires VIP plan."""
    return await api_request(
        "POST", "/api/v1/conversations/", json_data={"chatbot_id": chatbot_id, "title": title}
    )


@mcp.tool()
async def get_conversation(conversation_id: str) -> dict:
    """Get conversation details: title, chatbot, timestamps, message count. Requires VIP."""
    return await api_request("GET", f"/api/v1/conversations/{conversation_id}/")


@mcp.tool()
async def update_conversation(conversation_id: str, title: str) -> dict:
    """Update conversation title. Requires VIP."""
    return await api_request(
        "PATCH", f"/api/v1/conversations/{conversation_id}/", json_data={"title": title}
    )


@mcp.tool()
async def delete_conversation(conversation_id: str) -> dict:
    """Delete a conversation and all its messages. Requires VIP."""
    return await api_request("POST", f"/api/v1/conversations/{conversation_id}/delete/")


@mcp.tool()
async def get_conversation_messages(conversation_id: str) -> dict:
    """Get all messages from a conversation (role, content, timestamp). Requires VIP."""
    return await api_request("GET", f"/api/v1/conversations/{conversation_id}/messages/")


# ========== Chat ==========

@mcp.tool()
async def send_message(
    chatbot_uuid: str,
    message: str,
    conversation_id: str = "",
    chat_history: list[dict] | None = None,
) -> dict:
    """Send a message to a chatbot and get AI response. Creates new conversation if conversation_id not provided. Requires VIP."""
    data: dict[str, Any] = {"message": message}
    if conversation_id:
        data["conversation_id"] = conversation_id
    if chat_history:
        data["chat_history"] = chat_history
    return await api_request("POST", f"/api/v1/chat/{chatbot_uuid}/vip/", json_data=data)


# ========== User & Models ==========

@mcp.tool()
async def get_user_plan() -> dict:
    """Get current user plan info: plan type, is_pro, email, chatbot count/limit, messages used/limit."""
    return await api_request("GET", "/api/v1/user/plan/")


@mcp.tool()
async def list_ai_models() -> dict:
    """List available AI models grouped by provider (name, model_id, is_free)."""
    return await api_request("GET", "/api/v1/ai-models/")


# --- Entry point ---
if __name__ == "__main__":
    mcp.run()
