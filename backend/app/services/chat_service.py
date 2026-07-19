"""
Chat business logic: conversation/message persistence, orchestrating the
AI provider + knowledge retrieval + prompt engineering, and follow-up
suggestion generation.
"""
import time
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.chat import Conversation, Message
from app.models.enums import MessageRole
from app.models.feedback_analytics import AnalyticsEvent
from app.services.ai_providers.base import ChatMessage
from app.services.ai_providers.manager import AIManager
from app.services.knowledge_service import search_knowledge
from app.services.prompt_engineering import build_system_prompt, detect_mode

MAX_HISTORY_MESSAGES = 12  # conversation memory window sent to the AI

_FALLBACK_SUGGESTIONS = {
    "department": [
        "What are the ND II courses?",
        "Who is the Head of Department?",
        "How do I register my courses?",
        "Show current announcements.",
    ],
    "academic": [
        "Generate a Python quiz.",
        "Explain Big O notation.",
        "Explain Database Normalization.",
        "Give me common interview questions on data structures.",
    ],
    "campus": [
        "What are the library opening hours?",
        "How do I apply for a hostel?",
        "What is SIWES?",
        "Tell me about student affairs services.",
    ],
}


async def get_conversation_or_404(db: AsyncSession, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Conversation:
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise NotFoundError("Conversation not found")
    if conversation.user_id != user_id:
        raise ForbiddenError("This conversation does not belong to you")
    return conversation


async def get_or_create_conversation(
    db: AsyncSession, user_id: uuid.UUID, conversation_id: uuid.UUID | None, first_message: str
) -> Conversation:
    if conversation_id:
        return await get_conversation_or_404(db, conversation_id, user_id)

    title = (first_message.strip()[:60] + ("…" if len(first_message.strip()) > 60 else "")) or "New Conversation"
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    await db.flush()  # get an ID without committing yet
    return conversation


async def load_history(db: AsyncSession, conversation_id: uuid.UUID) -> list[ChatMessage]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
    )
    messages = list(reversed(result.scalars().all()))
    return [ChatMessage(role=m.role, content=m.content) for m in messages]


async def prepare_ai_call(
    db: AsyncSession, conversation: Conversation, user_message: str
) -> tuple[list[ChatMessage], str, object, object]:
    """
    Shared setup for both the streaming and non-streaming chat endpoints:
    persists the user message, builds history + system prompt, resolves
    the active AI provider. Returns (chat_messages, mode, provider, config).
    """
    user_msg = Message(conversation_id=conversation.id, role=MessageRole.USER, content=user_message)
    db.add(user_msg)
    await db.flush()

    mode = detect_mode(user_message)
    knowledge_context = await search_knowledge(db, user_message)

    manager = AIManager(db)
    provider, config = await manager.resolve_provider()
    config.system_prompt = build_system_prompt(mode, knowledge_context, config.system_prompt)

    history = await load_history(db, conversation.id)
    return history, mode, provider, config


async def persist_assistant_message(
    db: AsyncSession,
    conversation: Conversation,
    content: str,
    provider_name: str,
    tokens_used: int | None,
    response_time_ms: int,
) -> Message:
    assistant_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=content,
        tokens_used=tokens_used,
        response_time_ms=response_time_ms,
    )
    conversation.ai_provider_used = provider_name
    db.add(assistant_msg)
    db.add(AnalyticsEvent(event_type="message_sent", user_id=conversation.user_id, metadata_json={"provider": provider_name}))
    await db.commit()
    await db.refresh(assistant_msg)
    return assistant_msg


def generate_suggestions(mode: str) -> list[str]:
    """
    Static, mode-aware fallback suggestions. Replaced by the admin-managed
    suggested_prompts table in ES-003, and can be made AI-generated later
    without changing the calling contract.
    """
    return _FALLBACK_SUGGESTIONS.get(mode, _FALLBACK_SUGGESTIONS["department"])


class Timer:
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.elapsed_ms = int((time.perf_counter() - self._start) * 1000)
