"""
Pydantic schemas for chat, conversations, and messages.
"""
from datetime import datetime

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    conversation_id: str | None = None  # None => create a new conversation
    message: str


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    liked: bool | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: str
    title: str
    is_pinned: bool
    is_archived: bool
    ai_provider_used: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailOut(ConversationOut):
    messages: list[MessageOut] = []


class ChatResponse(BaseModel):
    conversation_id: str
    message: MessageOut
    suggestions: list[str] = []


class ConversationRenameRequest(BaseModel):
    title: str


class MessageReactionRequest(BaseModel):
    liked: bool | None  # true=like, false=dislike, null=clear
